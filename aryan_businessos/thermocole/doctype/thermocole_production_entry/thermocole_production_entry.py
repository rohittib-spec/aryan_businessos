import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import flt

from aryan_businessos.thermocole.utils.stock_entry import create_production_stock_entry
from aryan_businessos.thermocole.utils.warehouse import get_finished_goods_warehouse
from aryan_businessos.thermocole.utils.yield_calc import calculate_yield


class ThermocoleProductionEntry(Document):

    def validate(self):
        self.validate_production_order()
        self.calculate_yield()
        if not self.materials:
            frappe.throw(_("Add at least one material row."))
        if not self.outputs:
            frappe.throw(_("Add at least one output row."))

    def before_submit(self):
        for row in self.materials or []:
            if not flt(row.actual_qty):
                frappe.throw(
                    _("Row {0}: Actual Qty is required in Materials.").format(row.idx)
                )
        for row in self.outputs or []:
            if not flt(row.qty):
                frappe.throw(_("Row {0}: Qty is required in Outputs.").format(row.idx))

    def on_submit(self):
        se = create_production_stock_entry(self)
        self.db_set("stock_entry", se.name)
        self.update_production_order()
        self.update_mould_statistics()

    def on_cancel(self):
        self.cancel_stock_entry()
        self.update_production_order()
        self.update_mould_statistics()

    def validate_production_order(self):
        if not self.production_order:
            return

        order = frappe.get_doc("Thermocole Production Order", self.production_order)
        if order.docstatus != 1:
            frappe.throw(_("Production Order {0} is not submitted.").format(self.production_order))

        if order.status == "Cancelled":
            frappe.throw(_("Production Order {0} is cancelled.").format(self.production_order))

    def calculate_yield(self):
        total_input = sum(flt(row.actual_qty) for row in self.materials or [])
        total_output = sum(flt(row.weight_kg) for row in self.outputs or [])
        if not total_output:
            total_output = sum(flt(row.qty) for row in self.outputs or [])

        yield_pct, bead_loss, output_kg = calculate_yield(total_input, total_output)
        self.total_input_kg = round(total_input, 3)
        self.total_output_kg = round(output_kg, 3)
        self.bead_loss_kg = bead_loss
        self.yield_pct = yield_pct

    def cancel_stock_entry(self):
        if self.stock_entry:
            se = frappe.get_doc("Stock Entry", self.stock_entry)
            if se.docstatus == 1:
                se.cancel()

    def update_production_order(self):
        if not self.production_order:
            return

        order = frappe.get_doc("Thermocole Production Order", self.production_order)
        order.refresh_produced_qty()
        if order.status != "Completed":
            order.db_set("status", "In Production")

    def update_mould_statistics(self):
        if not self.mould:
            return
        mould = frappe.get_doc("Thermocole Mould", self.mould)
        mould.update_statistics()

    def set_qc_status(self, status, qc_reference=None):
        self.db_set("qc_status", status)
        if qc_reference:
            self.db_set("qc_reference", qc_reference)

        if self.production_order:
            order = frappe.get_doc("Thermocole Production Order", self.production_order)
            if status == "Passed":
                order.mark_completed()
            elif status == "Failed":
                order.mark_qc_pending()
