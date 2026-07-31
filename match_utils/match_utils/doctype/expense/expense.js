// Copyright (c) 2026, match systems and contributors
// For license information, please see license.txt

frappe.ui.form.on('Expense', {
	onload: function(frm) {
		if (frm.is_new() && !frm.doc.company) {
			frm.set_value('company', frappe.defaults.get_user_default('Company'));
		}
	},

	company: function(frm) {
		frm.set_value('expense_type', '');
	},

	expense_type: function(frm) {
		frm.set_value('cost_center', '');
	}
});
