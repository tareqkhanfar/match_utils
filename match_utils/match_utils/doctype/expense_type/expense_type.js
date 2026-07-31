// Copyright (c) 2026, match systems and contributors
// For license information, please see license.txt

frappe.ui.form.on('Expense Type', {
	refresh: function(frm) {
		set_account_filters(frm);
	}
});

frappe.ui.form.on('Expense Type Account', {
	company: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		row.expense_account = '';
		row.credit_account = '';
		frm.refresh_field('accounts');
	}
});

function set_account_filters(frm) {
	frm.set_query('expense_account', 'accounts', function(doc, cdt, cdn) {
		let row = locals[cdt][cdn];
		return {
			filters: {
				company: row.company,
				root_type: 'Expense',
				is_group: 0
			}
		};
	});

	frm.set_query('credit_account', 'accounts', function(doc, cdt, cdn) {
		let row = locals[cdt][cdn];
		return {
			filters: {
				company: row.company,
				is_group: 0
			}
		};
	});
}
