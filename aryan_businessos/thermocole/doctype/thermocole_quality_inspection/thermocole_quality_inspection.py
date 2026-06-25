import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import flt

from aryan_businessos.thermocole.utils.stock_entry import create_rejection_stock_entry


class ThermocoleQualityInspection(Document):

    def validate(self):
        self.validate_production_entry()
        self.validate_readings()
        self.set_overall_result()

    def validate_production_entry(self):
        if not self.production_entry:
            return

        entry = frappe.get_doc("Thermocole Production Entry", self.production_entry)
        if entry.docstatus != 1:
            frappe.throw(_("Production Entry {0} is not submitted.").format(self.production_entry))

    def validate_readings(self):
        if not self.readings:
            frappe.throw(_("Add at least one inspection reading."))

    def set_overall_result(self):
        if self.overall_result:
            return
        if any(row.result == "Fail" for row in self.readings or []):
            self.overall_result = "Fail"
        elif all(row.result == "Pass" for row in self.readings or []):
            self.overall_result = "Pass"
        else:
            self.overall_result = "Conditional"

    def on_submit(self):
        entry = frappe.get_doc("Thermocole Production Entry", self.production_entry)
        qc_status = "Passed" if self.overall_result == "Pass" else "Failed"
        entry.set_qc_status(qc_status, self.name)

        if flt(self.rejected_qty) > 0:
            self.create_rejection_movement(entry)

    def on_cancel(self):
        entry = frappe.get_doc("Thermocole Production Entry", self.production_entry)
        entry.set_qc_status("Pending")

    def create_rejection_movement(self, production_entry):
        output = (production_entry.outputs or [None])[0]
        if not output:
            return

        create_rejection_stock_entry(
            production_entry,
            self.rejected_qty,
            output.item_code,
            output.warehouse,
        )
