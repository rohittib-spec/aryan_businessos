import frappe
from frappe.model.document import Document
from frappe import _


class ThermocoleMachine(Document):

    def validate(self):
        self.validate_unique_code()

    def validate_unique_code(self):
        if not self.machine_code:
            return
        existing = frappe.db.exists(
            "Thermocole Machine",
            {"machine_code": self.machine_code, "name": ["!=", self.name]},
        )
        if existing:
            frappe.throw(_("Machine Code {0} is already used by {1}.").format(self.machine_code, existing))
