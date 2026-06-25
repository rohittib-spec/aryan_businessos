const DENSITY_KG_M3 = {
	Low: 12,
	Medium: 15,
	High: 20,
};

function flt(value, precision = 3) {
	return frappe.utils.flt(value, precision);
}

function estimate_bead_kg(row) {
	const density = DENSITY_KG_M3[row.density_grade || "Medium"] || 15;
	const volume_m3 =
		(flt(row.length_mm) * flt(row.width_mm) * flt(row.height_mm) * flt(row.qty)) / 1e9;
	return flt(volume_m3 * density, 3);
}

function calculate_totals(frm) {
	let planned = 0;
	let produced = 0;
	(frm.doc.items || []).forEach((row) => {
		planned += flt(row.qty);
		produced += flt(row.produced_qty);
	});
	frm.set_value("total_planned_qty", flt(planned, 3));
	frm.set_value("total_produced_qty", flt(produced, 3));
	frm.set_value("pending_qty", flt(planned - produced, 3));
}

frappe.ui.form.on("Thermocole Production Order", {
	refresh(frm) {
		calculate_totals(frm);
	},
});

frappe.ui.form.on("Thermocole Production Order Item", {
	qty(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (row.length_mm && row.width_mm && row.height_mm) {
			frappe.model.set_value(cdt, cdn, "planned_bead_kg", estimate_bead_kg(row));
		}
		calculate_totals(frm);
	},
	length_mm(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (row.qty) {
			frappe.model.set_value(cdt, cdn, "planned_bead_kg", estimate_bead_kg(row));
		}
	},
	width_mm(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (row.qty) {
			frappe.model.set_value(cdt, cdn, "planned_bead_kg", estimate_bead_kg(row));
		}
	},
	height_mm(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (row.qty) {
			frappe.model.set_value(cdt, cdn, "planned_bead_kg", estimate_bead_kg(row));
		}
	},
	density_grade(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (row.qty) {
			frappe.model.set_value(cdt, cdn, "planned_bead_kg", estimate_bead_kg(row));
		}
	},
	item_code(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (!row.item_code) {
			return;
		}
		frappe.db.get_value("Item", row.item_code, [
			"custom_default_length_mm",
			"custom_default_width_mm",
			"custom_default_height_mm",
			"custom_density_grade",
			"custom_default_mould",
		]).then(({ message }) => {
			if (!message) {
				return;
			}
			if (message.custom_default_length_mm) {
				frappe.model.set_value(cdt, cdn, "length_mm", message.custom_default_length_mm);
			}
			if (message.custom_default_width_mm) {
				frappe.model.set_value(cdt, cdn, "width_mm", message.custom_default_width_mm);
			}
			if (message.custom_default_height_mm) {
				frappe.model.set_value(cdt, cdn, "height_mm", message.custom_default_height_mm);
			}
			if (message.custom_density_grade) {
				frappe.model.set_value(cdt, cdn, "density_grade", message.custom_density_grade);
			}
			if (message.custom_default_mould) {
				frappe.model.set_value(cdt, cdn, "mould", message.custom_default_mould);
			}
		});
	},
	mould(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (!row.mould) {
			return;
		}
		frappe.db.get_value("Thermocole Mould", row.mould, [
			"length_mm",
			"width_mm",
			"height_mm",
			"default_machine",
		]).then(({ message }) => {
			if (!message) {
				return;
			}
			if (!row.length_mm && message.length_mm) {
				frappe.model.set_value(cdt, cdn, "length_mm", message.length_mm);
			}
			if (!row.width_mm && message.width_mm) {
				frappe.model.set_value(cdt, cdn, "width_mm", message.width_mm);
			}
			if (!row.height_mm && message.height_mm) {
				frappe.model.set_value(cdt, cdn, "height_mm", message.height_mm);
			}
			if (message.default_machine) {
				frappe.model.set_value(cdt, cdn, "machine", message.default_machine);
			}
		});
	},
});
