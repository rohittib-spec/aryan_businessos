function flt(value, precision = 3) {
	return frappe.utils.flt(value, precision);
}

function calculate_yield(frm) {
	let total_input = 0;
	let total_output = 0;

	(frm.doc.materials || []).forEach((row) => {
		total_input += flt(row.actual_qty);
	});

	(frm.doc.outputs || []).forEach((row) => {
		if (flt(row.weight_kg)) {
			total_output += flt(row.weight_kg);
		} else {
			total_output += flt(row.qty);
		}
	});

	const bead_loss = flt(total_input - total_output, 3);
	const yield_pct = total_input ? flt((total_output / total_input) * 100, 2) : 0;

	frm.set_value("total_input_kg", flt(total_input, 3));
	frm.set_value("total_output_kg", flt(total_output, 3));
	frm.set_value("bead_loss_kg", bead_loss);
	frm.set_value("yield_pct", yield_pct);
}

function pull_from_production_order(frm) {
	if (!frm.doc.production_order || frm.doc.materials?.length || frm.doc.outputs?.length) {
		return;
	}

	frappe.db.get_doc("Thermocole Production Order", frm.doc.production_order).then((order) => {
		(order.items || []).forEach((row) => {
			frm.add_child("outputs", {
				item_code: row.item_code,
				qty: row.qty,
				uom: row.uom || "Nos",
				length_mm: row.length_mm,
				width_mm: row.width_mm,
				height_mm: row.height_mm,
				warehouse: "",
			});

			if (row.planned_bead_kg) {
				frm.add_child("materials", {
					planned_qty: row.planned_bead_kg,
					actual_qty: row.planned_bead_kg,
					uom: "Kg",
				});
			}
		});

		if (order.items?.length) {
			const first = order.items[0];
			if (first.mould) {
				frm.set_value("mould", first.mould);
			}
			if (first.machine) {
				frm.set_value("machine", first.machine);
			}
		}

		frappe.db.get_value("Thermocole Mould", frm.doc.mould, "default_bead_item").then(({ message: bead_item }) => {
			if (bead_item) {
				(frm.doc.materials || []).forEach((row) => {
					if (!row.item_code) {
						row.item_code = bead_item;
					}
				});
			}
			frm.refresh_field("materials");
			frm.refresh_field("outputs");
			set_default_output_warehouse(frm);
			calculate_yield(frm);
		});
	});
}

function set_default_output_warehouse(frm) {
	frappe.call({
		method: "aryan_businessos.thermocole.utils.warehouse.get_finished_goods_warehouse",
		callback(r) {
			if (!r.message) {
				return;
			}
			(frm.doc.outputs || []).forEach((row) => {
				if (!row.warehouse) {
					row.warehouse = r.message;
				}
			});
			frm.refresh_field("outputs");
		},
	});
}

frappe.ui.form.on("Thermocole Production Entry", {
	refresh(frm) {
		calculate_yield(frm);
		if (frm.doc.docstatus === 0) {
			frm.add_custom_button(__("Pull from Production Order"), () => pull_from_production_order(frm));
		}
	},
	production_order(frm) {
		pull_from_production_order(frm);
	},
	mould(frm) {
		if (!frm.doc.mould) {
			return;
		}
		frappe.db.get_value("Thermocole Mould", frm.doc.mould, ["default_machine", "default_bead_item"]).then(({ message }) => {
			if (message?.default_machine && !frm.doc.machine) {
				frm.set_value("machine", message.default_machine);
			}
			if (message?.default_bead_item) {
				(frm.doc.materials || []).forEach((row) => {
					if (!row.item_code) {
						row.item_code = message.default_bead_item;
					}
				});
				frm.refresh_field("materials");
			}
		});
	},
});

frappe.ui.form.on("Thermocole Production Entry Material", {
	actual_qty(frm) {
		calculate_yield(frm);
	},
	materials_remove(frm) {
		calculate_yield(frm);
	},
});

frappe.ui.form.on("Thermocole Production Entry Output", {
	qty(frm) {
		calculate_yield(frm);
	},
	weight_kg(frm) {
		calculate_yield(frm);
	},
	outputs_remove(frm) {
		calculate_yield(frm);
	},
});
