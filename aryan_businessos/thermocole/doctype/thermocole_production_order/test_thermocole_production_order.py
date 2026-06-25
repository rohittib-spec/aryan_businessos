import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import flt

from aryan_businessos.thermocole.doctype.thermocole_production_order.thermocole_production_order import (
    ThermocoleProductionOrder,
)


class TestThermocoleProductionOrder(IntegrationTestCase):
    def test_calculate_totals_and_status_draft(self):
        doc = frappe.get_doc(
            {
                "doctype": "Thermocole Production Order",
                "order_date": "2026-06-25",
                "delivery_date": "2026-06-30",
                "items": [
                    {"item_code": "ITEM-A", "qty": 10, "uom": "Nos", "produced_qty": 3},
                    {"item_code": "ITEM-B", "qty": 5, "uom": "Nos", "produced_qty": 0},
                ],
            }
        )

        ThermocoleProductionOrder.calculate_totals(doc)
        ThermocoleProductionOrder.set_status(doc)

        self.assertEqual(flt(doc.total_planned_qty), 15)
        self.assertEqual(flt(doc.total_produced_qty), 3)
        self.assertEqual(flt(doc.pending_qty), 12)
        self.assertEqual(doc.status, "Draft")

    def test_set_status_in_production(self):
        doc = frappe.get_doc(
            {
                "doctype": "Thermocole Production Order",
                "docstatus": 1,
                "status": "Confirmed",
                "order_date": "2026-06-25",
                "delivery_date": "2026-06-30",
                "items": [{"item_code": "ITEM-A", "qty": 10, "uom": "Nos", "produced_qty": 4}],
            }
        )
        doc.total_planned_qty = 10
        doc.total_produced_qty = 4

        ThermocoleProductionOrder.set_status(doc)
        self.assertEqual(doc.status, "In Production")

    def test_set_status_completed(self):
        doc = frappe.get_doc(
            {
                "doctype": "Thermocole Production Order",
                "docstatus": 1,
                "status": "In Production",
                "order_date": "2026-06-25",
                "delivery_date": "2026-06-30",
                "items": [{"item_code": "ITEM-A", "qty": 10, "uom": "Nos", "produced_qty": 10}],
            }
        )
        doc.total_planned_qty = 10
        doc.total_produced_qty = 10

        ThermocoleProductionOrder.set_status(doc)
        self.assertEqual(doc.status, "Completed")

    def test_planned_bead_kg_calculation(self):
        doc = frappe.get_doc(
            {
                "doctype": "Thermocole Production Order",
                "order_date": "2026-06-25",
                "delivery_date": "2026-06-30",
                "items": [
                    {
                        "item_code": "ITEM-A",
                        "qty": 1,
                        "uom": "Nos",
                        "length_mm": 1000,
                        "width_mm": 1000,
                        "height_mm": 1000,
                        "density_grade": "High",
                    }
                ],
            }
        )

        ThermocoleProductionOrder.calculate_planned_bead_kg(doc)
        self.assertEqual(flt(doc.items[0].planned_bead_kg), 20.0)
