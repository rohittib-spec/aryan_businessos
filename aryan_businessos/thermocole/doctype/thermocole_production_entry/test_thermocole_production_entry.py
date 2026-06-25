import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import flt
from unittest.mock import patch

from aryan_businessos.thermocole.doctype.thermocole_production_entry.thermocole_production_entry import (
    ThermocoleProductionEntry,
)


class TestThermocoleProductionEntry(IntegrationTestCase):
    def test_calculate_yield_from_materials_and_outputs(self):
        doc = frappe.get_doc(
            {
                "doctype": "Thermocole Production Entry",
                "entry_date": "2026-06-25",
                "materials": [
                    {"item_code": "BEADS", "actual_qty": 50, "uom": "Kg"},
                    {"item_code": "BEADS", "actual_qty": 30, "uom": "Kg"},
                ],
                "outputs": [
                    {"item_code": "BLOCK", "qty": 10, "weight_kg": 25, "uom": "Nos"},
                    {"item_code": "BLOCK", "qty": 10, "weight_kg": 48, "uom": "Nos"},
                ],
            }
        )

        ThermocoleProductionEntry.calculate_yield(doc)

        self.assertEqual(flt(doc.total_input_kg), 80)
        self.assertEqual(flt(doc.total_output_kg), 73)
        self.assertEqual(flt(doc.bead_loss_kg), 7)
        self.assertEqual(flt(doc.yield_pct), 91.25)

    def test_calculate_yield_uses_qty_when_weight_missing(self):
        doc = frappe.get_doc(
            {
                "doctype": "Thermocole Production Entry",
                "entry_date": "2026-06-25",
                "materials": [{"item_code": "BEADS", "actual_qty": 20, "uom": "Kg"}],
                "outputs": [{"item_code": "BLOCK", "qty": 15, "uom": "Nos"}],
            }
        )

        ThermocoleProductionEntry.calculate_yield(doc)

        self.assertEqual(flt(doc.total_input_kg), 20)
        self.assertEqual(flt(doc.total_output_kg), 15)
        self.assertEqual(flt(doc.yield_pct), 75.0)

    @patch(
        "aryan_businessos.thermocole.doctype.thermocole_production_entry.thermocole_production_entry.create_production_stock_entry"
    )
    def test_on_submit_creates_stock_entry(self, mock_create_se):
        mock_create_se.return_value = frappe._dict(name="SE-TEST-001")

        doc = frappe.get_doc(
            {
                "doctype": "Thermocole Production Entry",
                "name": "TPE-TEST-001",
                "entry_date": "2026-06-25",
                "materials": [{"item_code": "BEADS", "actual_qty": 10, "uom": "Kg", "warehouse": "Stores"}],
                "outputs": [{"item_code": "BLOCK", "qty": 1, "weight_kg": 8, "uom": "Nos", "warehouse": "FG"}],
            }
        )
        ThermocoleProductionEntry.calculate_yield(doc)

        with patch.object(ThermocoleProductionEntry, "update_production_order"):
            with patch.object(ThermocoleProductionEntry, "update_mould_statistics"):
                ThermocoleProductionEntry.on_submit(doc)

        mock_create_se.assert_called_once_with(doc)
