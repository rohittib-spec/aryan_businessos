import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import flt


class JobWorkReceipt(Document):

    def validate(self):
        self.validate_challan()
        self.calculate_loss()
        self.check_excess_loss()

    def on_submit(self):
        self.create_stock_entry()
        self.update_challan()
        self.update_karigar_stats()

    def on_cancel(self):
        self.cancel_stock_entry()
        self.reverse_challan_update()
        self.update_karigar_stats()

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate_challan(self):
        challan = frappe.get_doc("Job Work Challan", self.job_work_challan)

        if challan.docstatus != 1:
            frappe.throw(_("Job Work Challan {0} is not submitted.").format(self.job_work_challan))

        if challan.status == "Closed":
            frappe.throw(
                _("Job Work Challan {0} is already Closed.").format(self.job_work_challan)
            )

        if challan.status == "Cancelled":
            frappe.throw(
                _("Job Work Challan {0} is Cancelled.").format(self.job_work_challan)
            )

        # Cannot receive more than issued
        already_received = flt(challan.total_received_weight)
        total_if_added = already_received + flt(self.received_weight)
        if total_if_added > flt(challan.total_issued_weight):
            frappe.throw(
                _("Cannot receive {0}g. Only {1}g outstanding against Challan {2}.").format(
                    self.received_weight,
                    flt(challan.total_issued_weight) - already_received,
                    self.job_work_challan
                )
            )

    def calculate_loss(self):
        """Compute loss weight, loss %, and acceptable loss for this receipt."""
        challan = frappe.get_doc("Job Work Challan", self.job_work_challan)

        self.issued_weight = challan.total_issued_weight
        self.loss_weight = round(flt(self.issued_weight) - flt(self.received_weight), 3)

        if flt(self.issued_weight):
            self.loss_pct = round(flt(self.loss_weight) / flt(self.issued_weight) * 100, 2)
        else:
            self.loss_pct = 0

        # Fetch acceptable loss from karigar master
        if challan.items:
            first_item = challan.items[0]
            karigar = frappe.get_doc("Karigar", self.karigar)
            self.acceptable_loss_pct = karigar.get_acceptable_loss_pct(
                first_item.metal_type, first_item.purity
            )

    def check_excess_loss(self):
        """Warn (not block) if loss exceeds acceptable threshold."""
        if flt(self.loss_pct) > flt(self.acceptable_loss_pct):
            self.loss_status = "Excess Loss"
            frappe.msgprint(
                _("⚠️ Loss of {0}% exceeds acceptable limit of {1}% for Karigar {2}.").format(
                    self.loss_pct, self.acceptable_loss_pct, self.karigar
                ),
                title=_("Excess Metal Loss"),
                indicator="orange"
            )
        else:
            self.loss_status = "Within Limit"

    # ------------------------------------------------------------------
    # Stock Entry — move from karigar WIP back to finished goods warehouse
    # ------------------------------------------------------------------

    def create_stock_entry(self):
        challan = frappe.get_doc("Job Work Challan", self.job_work_challan)
        company = frappe.defaults.get_user_default("Company")
        abbr = frappe.db.get_value("Company", company, "abbr")
        karigar_warehouse = f"{self.karigar} - WIP - {abbr}"

        se = frappe.new_doc("Stock Entry")
        se.stock_entry_type = "Material Transfer"
        se.purpose = "Material Transfer"
        se.posting_date = self.receipt_date
        se.custom_job_work_receipt = self.name

        for row in self.items:
            se.append("items", {
                "item_code": row.item_code,
                "qty": row.received_weight,
                "uom": row.uom or "Gram",
                "s_warehouse": karigar_warehouse,
                "t_warehouse": row.warehouse or self.target_warehouse,
                "batch_no": row.batch_no,
            })

        se.insert(ignore_permissions=True)
        se.submit()
        self.db_set("stock_entry", se.name)

    def cancel_stock_entry(self):
        se_name = frappe.db.get_value("Job Work Receipt", self.name, "stock_entry")
        if se_name:
            se = frappe.get_doc("Stock Entry", se_name)
            if se.docstatus == 1:
                se.cancel()

    # ------------------------------------------------------------------
    # Update parent challan
    # ------------------------------------------------------------------

    def update_challan(self):
        challan = frappe.get_doc("Job Work Challan", self.job_work_challan)
        challan.update_on_receipt(self.received_weight)

        if self.is_final_receipt:
            challan.db_set("status", "Closed")

    def reverse_challan_update(self):
        """On cancel, reduce received weight on challan and reopen it."""
        challan = frappe.get_doc("Job Work Challan", self.job_work_challan)
        new_received = max(0, flt(challan.total_received_weight) - flt(self.received_weight))
        challan.total_received_weight = new_received
        challan.net_loss_weight = round(
            flt(challan.total_issued_weight) - new_received, 3
        )
        if flt(challan.total_issued_weight):
            challan.loss_pct = round(
                challan.net_loss_weight / flt(challan.total_issued_weight) * 100, 2
            )
        if new_received == 0:
            challan.status = "Open"
        else:
            challan.status = "Partially Received"
        challan.db_update()

    # ------------------------------------------------------------------
    # Karigar stats
    # ------------------------------------------------------------------

    def update_karigar_stats(self):
        if self.karigar:
            karigar = frappe.get_doc("Karigar", self.karigar)
            karigar.update_statistics()


def has_permission(doc, ptype, user):
    return True
