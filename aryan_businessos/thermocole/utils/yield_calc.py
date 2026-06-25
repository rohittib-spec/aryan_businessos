from frappe.utils import flt

DENSITY_KG_M3 = {
    "Low": 12,
    "Medium": 15,
    "High": 20,
}


def estimate_bead_kg(length_mm, width_mm, height_mm, qty, density_grade="Medium"):
    """Estimate raw bead consumption from dimensions and density grade."""
    density = DENSITY_KG_M3.get(density_grade or "Medium", 15)
    volume_m3 = flt(length_mm) * flt(width_mm) * flt(height_mm) * flt(qty) / 1e9
    return round(volume_m3 * density, 3)


def calculate_yield(input_kg, output_kg):
    """Return yield_pct, bead_loss_kg, total_output_kg."""
    input_kg = flt(input_kg)
    output_kg = flt(output_kg)
    bead_loss = round(input_kg - output_kg, 3)
    if not input_kg:
        return 0, bead_loss, output_kg
    yield_pct = round(output_kg / input_kg * 100, 2)
    return yield_pct, bead_loss, output_kg
