import frappe
from frappe.model.document import Document
from frappe import _


class Karigar(Document):

    def validate(self):
        self.validate_loss_thresholds()

    def validate_loss_thresholds(self):
        """Ensure no duplicate metal type in loss thresholds."""
        seen = []
        for row in self.loss_thresholds or []:
            key = (row.metal_type, row.purity)
            if key in seen:
                frappe.throw(
                    _("Duplicate entry for Metal Type {0} Purity {1} in Loss Thresholds").format(
                        row.metal_type, row.purity
                    )
                )
            seen.append(key)

    def update_statistics(self):
        """Recompute running stats from all submitted challans and receipts."""
        issued = frappe.db.sql("""
            SELECT COALESCE(SUM(jwd.issued_weight), 0)
            FROM `tabJob Work Challan Detail` jwd
            JOIN `tabJob Work Challan` jwc ON jwc.name = jwd.parent
            WHERE jwc.karigar = %s AND jwc.docstatus = 1
        """, self.name)[0][0] or 0

        returned = frappe.db.sql("""
            SELECT COALESCE(SUM(jwr.received_weight), 0)
            FROM `tabJob Work Receipt` jwr
            WHERE jwr.karigar = %s AND jwr.docstatus = 1
        """, self.name)[0][0] or 0

        open_challans = frappe.db.count(
            "Job Work Challan",
            {"karigar": self.name, "docstatus": 1, "status": ["in", ["Open", "Partially Received"]]}
        )

        self.total_metal_issued_grams = issued
        self.total_metal_returned_grams = returned
        self.total_loss_grams = round(issued - returned, 3)
        self.avg_loss_pct = round((self.total_loss_grams / issued * 100), 2) if issued else 0
        self.open_challans = open_challans
        self.db_update()

    def get_acceptable_loss_pct(self, metal_type, purity=None):
        """Return acceptable loss % for a given metal type and purity."""
        for row in self.loss_thresholds or []:
            if row.metal_type == metal_type:
                if purity and row.purity and row.purity != purity:
                    continue
                return row.acceptable_loss_pct
        return 0.0
