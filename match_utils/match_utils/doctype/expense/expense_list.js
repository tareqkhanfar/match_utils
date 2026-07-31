// Copyright (c) 2026, match systems and contributors
// For license information, please see license.txt

frappe.listview_settings['Expense'] = {
	add_fields: ['expense_type', 'posting_date', 'amount', 'company', 'docstatus'],
	filters: [],
	get_indicator: function(doc) {
		if (doc.docstatus === 0) {
			return [__('Draft'), 'red', 'docstatus,=,0'];
		} else if (doc.docstatus === 1) {
			return [__('Submitted'), 'green', 'docstatus,=,1'];
		} else if (doc.docstatus === 2) {
			return [__('Cancelled'), 'grey', 'docstatus,=,2'];
		}
	}
};
