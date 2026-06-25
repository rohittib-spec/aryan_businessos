import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import flt, today


class JobWorkChallan(Document):

    def validate(self):
        self.validate_dates()
        self.fetch_loss_thresholds()
        self.calculate_totals()
        self.set_status()

    def on_submit(self):
        self.status = "Open"
        self.db_set("status", "Open")
        self.create_stock_entry()
        self.update_karigar_stats()

    def on_cancel(self):
        self.status = "Cancelled"
        self.db_set("status", "Cancelled")
        self.cancel_stock_entry()
        self.update_karigar_stats()

    # ------------------------------------------------------------------
    # Validation helpers
    # ------------------------------------------------------------------

    def validate_dates(self):
        if self.expected_return_date < self.challan_date:
            frappe.throw(_("Expected Return Date cannot be before Challan Date."))

    def fetch_loss_thresholds(self):
        """Auto-populate acceptable loss % from karigar master per line."""
        if not self.karigar:
            return
        karigar = frappe.get_doc("Karigar", self.karigar)
        for row in self.items:
            if not row.acceptable_loss_pct:
                row.acceptable_loss_pct = karigar.get_acceptable_loss_pct(
                    row.metal_type, row.purity
                )

    def calculate_totals(self):
        total = sum(flt(row.issued_weight) for row in self.items)
        self.total_issued_weight = round(total, 3)

    def set_status(self):
        if self.docstatus == 0:
            self.status = "Draft"

    # ------------------------------------------------------------------
    # Stock Entry — debit Karigar WIP account, credit store warehouse
    # ------------------------------------------------------------------

    def create_stock_entry(self):
        """Create a Stock Entry (Material Transfer) when challan is submitted."""
        se = frappe.new_doc("Stock Entry")
        se.stock_entry_type = "Material Transfer"
        se.purpose = "Material Transfer"
        se.posting_date = self.challan_date
        se.custom_job_work_challan = self.name

        for row in self.items:
            se.append("items", {
                "item_code": row.item_code,
                "qty": row.issued_weight,
                "uom": row.uom,
                "s_warehouse": row.warehouse,
                # Karigar WIP warehouse — must exist as a virtual warehouse per karigar
                "t_warehouse": self.get_karigar_warehouse(),
                "batch_no": row.batch_no,
            })

        se.insert(ignore_permissions=True)
        se.submit()
        self.db_set("stock_entry", se.name)

    def cancel_stock_entry(self):
        se_name = frappe.db.get_value("Job Work Challan", self.name, "stock_entry")
        if se_name:
            se = frappe.get_doc("Stock Entry", se_name)
            if se.docstatus == 1:
                se.cancel()

    def get_karigar_warehouse(self):
        """
        Each karigar should have a dedicated WIP warehouse named:
        '<Karigar Name> - WIP - <Company Abbr>'
        Create it if it doesn't exist.
        """
        company = frappe.defaults.get_user_default("Company")
        abbr = frappe.db.get_value("Company", company, "abbr")
        warehouse_name = f"{self.karigar} - WIP - {abbr}"

        if not frappe.db.exists("Warehouse", warehouse_name):
            wh = frappe.get_doc({
                "doctype": "Warehouse",
                "warehouse_name": f"{self.karigar} - WIP",
                "warehouse_type": "Transit",
                "company": company,
                "parent_warehouse": "All Warehouses",
            })
            wh.insert(ignore_permissions=True)

        return warehouse_name

    # ------------------------------------------------------------------
    # Update karigar running stats
    # ------------------------------------------------------------------

    def update_karigar_stats(self):
        if self.karigar:
            karigar = frappe.get_doc("Karigar", self.karigar)
            karigar.update_statistics()

    # ------------------------------------------------------------------
    # Called from Job Work Receipt to update challan status & loss
    # ------------------------------------------------------------------

    def update_on_receipt(self, received_weight):
        """Update totals and loss status when a receipt is submitted."""
        self.total_received_weight = flt(self.total_received_weight) + flt(received_weight)
        self.net_loss_weight = round(
            flt(self.total_issued_weight) - flt(self.total_received_weight), 3
        )
        if self.total_issued_weight:
            self.loss_pct = round(
                self.net_loss_weight / self.total_issued_weight * 100, 2
            )

        # Determine loss status
        # Use first line's acceptable loss % as proxy (can be extended per metal)
        acceptable = flt(self.items[0].acceptable_loss_pct) if self.items else 0
        if self.loss_pct <= acceptable:
            self.loss_status = "Within Limit"
        else:
            self.loss_status = "Excess Loss"

        # Update challan status
        if flt(self.total_received_weight) >= flt(self.total_issued_weight):
            self.status = "Closed"
        else:
            self.status = "Partially Received"

        self.db_update()


def has_permission(doc, ptype, user):
    return True  # Extend with custom permission logic if needed
