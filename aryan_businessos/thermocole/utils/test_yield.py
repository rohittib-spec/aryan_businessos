from frappe.tests import IntegrationTestCase

from aryan_businessos.thermocole.utils.yield_calc import calculate_yield, estimate_bead_kg


class TestThermocoleYield(IntegrationTestCase):
    def test_calculate_yield_basic(self):
        yield_pct, bead_loss, output_kg = calculate_yield(100, 85)
        self.assertEqual(yield_pct, 85.0)
        self.assertEqual(bead_loss, 15.0)
        self.assertEqual(output_kg, 85)

    def test_calculate_yield_zero_input(self):
        yield_pct, bead_loss, output_kg = calculate_yield(0, 10)
        self.assertEqual(yield_pct, 0)
        self.assertEqual(bead_loss, -10.0)
        self.assertEqual(output_kg, 10)

    def test_estimate_bead_kg_medium_density(self):
        # 1000 x 500 x 100 mm x 2 nos => 0.1 m3 * 15 kg/m3 = 1.5 kg
        result = estimate_bead_kg(1000, 500, 100, 2, "Medium")
        self.assertEqual(result, 1.5)

    def test_estimate_bead_kg_high_density(self):
        result = estimate_bead_kg(1000, 1000, 1000, 1, "High")
        self.assertEqual(result, 20.0)
