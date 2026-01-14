// Copyright (c) 2026, match systems and contributors
// For license information, please see license.txt

frappe.ui.form.on("Shortcut Mapper", {
	refresh(frm) {
		// Add custom button to test shortcut
		if (!frm.is_new()) {
			frm.add_custom_button(__('Test Shortcut'), function() {
				test_shortcut(frm);
			});
			
			// Add button to reload all shortcuts
			frm.add_custom_button(__('Reload Shortcuts'), function() {
				frappe.call({
					method: 'match_utils.api.reload_shortcuts',
					callback: function(r) {
						frappe.show_alert({
							message: __('Shortcuts reloaded for all users'),
							indicator: 'green'
						}, 3);
					}
				});
			});
		}
		
		// Show helper text
		if (frm.is_new()) {
			frm.set_intro(__('Create keyboard shortcuts to quickly access doctypes, reports, or pages. Example: CTRL+SHIFT+S'));
		}
	},
	
	shortcut_key(frm) {
		// Auto-format shortcut key
		if (frm.doc.shortcut_key) {
			frm.set_value('shortcut_key', frm.doc.shortcut_key.toUpperCase());
		}
	},
	
	target_type(frm) {
		// Clear dependent fields when target type changes
		frm.set_value('target_doctype', '');
		frm.set_value('target_report', '');
		frm.set_value('target_page', '');
	}
});

function test_shortcut(frm) {
	let message = __('Press the keyboard shortcut: <strong>{0}</strong>', [frm.doc.shortcut_key]);
	message += '<br><br>' + __('The system will navigate to: ');
	
	if (frm.doc.target_type === 'DocType') {
		message += __('DocType List - <strong>{0}</strong>', [frm.doc.target_doctype]);
	} else if (frm.doc.target_type === 'Report') {
		message += __('Report - <strong>{0}</strong>', [frm.doc.target_report]);
	} else if (frm.doc.target_type === 'Page') {
		message += __('Page - <strong>{0}</strong>', [frm.doc.target_page]);
	}
	
	frappe.msgprint({
		title: __('Shortcut Test'),
		message: message,
		indicator: 'blue'
	});
}