import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import flt


class ThermocoleMould(Document):

    def validate(self):
        self.validate_unique_code()

    def validate_unique_code(self):
        if not self.mould_code:
            return
        existing = frappe.db.exists(
            "Thermocole Mould",
            {"mould_code": self.mould_code, "name": ["!=", self.name]},
        )
        if existing:
            frappe.throw(_("Mould Code {0} is already used by {1}.").format(self.mould_code, existing))

    def update_statistics(self):
        """Recompute mould stats from submitted production entries."""
        stats = frappe.db.sql(
            """
            SELECT COUNT(*) AS total_runs,
                   COALESCE(AVG(yield_pct), 0) AS avg_yield,
                   MAX(entry_date) AS last_used
            FROM `tabThermocole Production Entry`
            WHERE mould = %s AND docstatus = 1
            """,
            self.name,
            as_dict=True,
        )[0]

        self.total_runs = stats.total_runs or 0
        self.avg_yield_pct = round(flt(stats.avg_yield), 2)
        self.last_used_date = stats.last_used
        self.db_update()
