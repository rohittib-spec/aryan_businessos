frappe.listview_settings["Thermocole Production Order"] = {
	has_indicator_for_draft: 1,

	get_indicator(doc) {
		const colour = frappe.utils.guess_colour(doc.status || "Draft");
		return [__(doc.status || "Draft"), colour];
	},
};
