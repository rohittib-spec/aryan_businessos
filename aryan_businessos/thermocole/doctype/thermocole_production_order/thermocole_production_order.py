import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import flt

from aryan_businessos.thermocole.utils.yield_calc import estimate_bead_kg


class ThermocoleProductionOrder(Document):

    def validate(self):
        self.validate_dates()
        self.calculate_planned_bead_kg()
        self.calculate_totals()
        self.set_status()

    def on_submit(self):
        self.status = "Confirmed"
        self.db_set("status", "Confirmed")

    def on_cancel(self):
        self.status = "Cancelled"
        self.db_set("status", "Cancelled")

    def validate_dates(self):
        if self.delivery_date and self.order_date and self.delivery_date < self.order_date:
            frappe.throw(_("Delivery Date cannot be before Order Date."))

        if not self.items:
            frappe.throw(_("Add at least one item row."))

    def calculate_planned_bead_kg(self):
        for row in self.items or []:
            if row.length_mm and row.width_mm and row.height_mm and row.qty:
                row.planned_bead_kg = estimate_bead_kg(
                    row.length_mm,
                    row.width_mm,
                    row.height_mm,
                    row.qty,
                    row.density_grade or "Medium",
                )

    def calculate_totals(self):
        planned = sum(flt(row.qty) for row in self.items or [])
        produced = sum(flt(row.produced_qty) for row in self.items or [])
        self.total_planned_qty = round(planned, 3)
        self.total_produced_qty = round(produced, 3)
        self.pending_qty = round(planned - produced, 3)

    def set_status(self):
        if self.docstatus == 0:
            self.status = "Draft"
            return

        if self.status == "Cancelled":
            return

        if flt(self.total_produced_qty) >= flt(self.total_planned_qty) and flt(self.total_planned_qty):
            if self.status not in ("QC Pending", "Completed"):
                self.status = "Completed"
        elif flt(self.total_produced_qty) > 0:
            self.status = "In Production"

    def refresh_produced_qty(self):
        """Recompute produced qty from submitted production entries."""
        produced_by_item = frappe.db.sql(
            """
            SELECT tpoi.name AS row_name, COALESCE(SUM(tpeo.qty), 0) AS produced
            FROM `tabThermocole Production Order Item` tpoi
            LEFT JOIN `tabThermocole Production Entry` tpe
                ON tpe.production_order = tpoi.parent AND tpe.docstatus = 1
            LEFT JOIN `tabThermocole Production Entry Output` tpeo
                ON tpeo.parent = tpe.name AND tpeo.item_code = tpoi.item_code
            WHERE tpoi.parent = %s
            GROUP BY tpoi.name
            """,
            self.name,
            as_dict=True,
        )

        produced_map = {row.row_name: flt(row.produced) for row in produced_by_item}
        for row in self.items or []:
            row.produced_qty = produced_map.get(row.name, 0)

        self.calculate_totals()
        self.set_status()
        self.db_update()
        for row in self.items or []:
            frappe.db.set_value(
                "Thermocole Production Order Item",
                row.name,
                "produced_qty",
                row.produced_qty,
                update_modified=False,
            )
        self.db_set("status", self.status)
        self.db_set("total_produced_qty", self.total_produced_qty)
        self.db_set("pending_qty", self.pending_qty)

    def mark_qc_pending(self):
        if self.docstatus != 1:
            return
        self.db_set("status", "QC Pending")

    def mark_completed(self):
        if self.docstatus != 1:
            return
        self.refresh_produced_qty()
        if flt(self.pending_qty) <= 0:
            self.db_set("status", "Completed")
