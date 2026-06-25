function populate_readings_from_entry(frm) {
	if (!frm.doc.production_entry || frm.doc.readings?.length) {
		return;
	}

	frappe.db.get_doc("Thermocole Production Entry", frm.doc.production_entry).then((entry) => {
		let total_qty = 0;
		(entry.outputs || []).forEach((row) => {
			total_qty += frappe.utils.flt(row.qty);
			frm.add_child("readings", {
				parameter: "Dimension",
				spec_value: [row.length_mm, row.width_mm, row.height_mm]
					.filter(Boolean)
					.join(" x "),
				actual_value: "",
				result: "Pass",
			});
		});

		frm.add_child("readings", {
			parameter: "Weight",
			spec_value: String(frappe.utils.flt(entry.total_output_kg)),
			actual_value: String(frappe.utils.flt(entry.total_output_kg)),
			result: "Pass",
		});

		frm.add_child("readings", {
			parameter: "Visual",
			spec_value: "No visible defects",
			actual_value: "",
			result: "Pass",
		});

		if (!frm.doc.accepted_qty && total_qty) {
			frm.set_value("accepted_qty", total_qty);
		}

		frm.refresh_field("readings");
	});
}

frappe.ui.form.on("Thermocole Quality Inspection", {
	refresh(frm) {
		if (frm.doc.docstatus === 0) {
			frm.add_custom_button(__("Populate Readings"), () => populate_readings_from_entry(frm));
		}
	},
	production_entry(frm) {
		populate_readings_from_entry(frm);
	},
});

frappe.ui.form.on("Thermocole Quality Inspection Reading", {
	result(frm) {
		const readings = frm.doc.readings || [];
		if (!readings.length) {
			return;
		}
		if (readings.some((row) => row.result === "Fail")) {
			frm.set_value("overall_result", "Fail");
		} else if (readings.every((row) => row.result === "Pass")) {
			frm.set_value("overall_result", "Pass");
		} else {
			frm.set_value("overall_result", "Conditional");
		}
	},
});
