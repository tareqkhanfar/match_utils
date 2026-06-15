// Copyright (c) 2026, match systems and contributors
// For license information, please see license.txt

frappe.ui.form.on("Shortcut Mapper", {
	refresh(frm) {
		set_form_intro(frm);

		if (!frm.is_new()) {
			frm.add_custom_button(__('Test Shortcut'), () => show_test_dialog(frm));

			frm.add_custom_button(__('Reload for All Users'), () => {
				frappe.call({
					method: 'match_utils.api.reload_shortcuts',
					callback: () => {
						frappe.show_alert({ message: __('Shortcuts reloaded for all users'), indicator: 'green' }, 3);
					}
				});
			});
		}

		update_open_mode_visibility(frm);
		render_shortcut_badge(frm);
	},

	shortcut_key(frm) {
		if (frm.doc.shortcut_key) {
			frm.set_value('shortcut_key', frm.doc.shortcut_key.toUpperCase());
		}
		render_shortcut_badge(frm);
	},

	target_type(frm) {
		frm.set_value('target_doctype', '');
		frm.set_value('target_report', '');
		frm.set_value('target_page', '');
		frm.set_value('open_mode', 'List');
		update_open_mode_visibility(frm);
		render_shortcut_badge(frm);
	},

	target_doctype(frm) {
		render_shortcut_badge(frm);
	},

	target_report(frm) {
		render_shortcut_badge(frm);
	},

	target_page(frm) {
		render_shortcut_badge(frm);
	},

	open_mode(frm) {
		render_shortcut_badge(frm);
	}
});

function update_open_mode_visibility(frm) {
	frm.toggle_display('open_mode', frm.doc.target_type === 'DocType');
}

function render_shortcut_badge(frm) {
	// Show a live preview below the shortcut_key field
	const key = frm.doc.shortcut_key;
	if (!key) return;

	const parts = key.split('+');
	const badges = parts.map(p => `<kbd style="
		display:inline-block;
		padding:2px 8px;
		margin:2px;
		background:#f5f5f5;
		border:1px solid #ccc;
		border-bottom:3px solid #999;
		border-radius:4px;
		font-family:monospace;
		font-size:13px;
	">${p}</kbd>`).join(' <span style="opacity:.5">+</span> ');

	let destination = '';
	if (frm.doc.target_type === 'DocType' && frm.doc.target_doctype) {
		const mode = frm.doc.open_mode || 'List';
		destination = `<strong>${frm.doc.target_doctype}</strong> &rarr; ${mode}`;
	} else if (frm.doc.target_type === 'Report' && frm.doc.target_report) {
		destination = `Report: <strong>${frm.doc.target_report}</strong>`;
	} else if (frm.doc.target_type === 'Page' && frm.doc.target_page) {
		destination = `Page: <strong>${frm.doc.target_page}</strong>`;
	}

	const html = `<div style="margin-top:6px">
		${badges}
		${destination ? `<span style="margin-left:12px;color:#555">&rarr; ${destination}</span>` : ''}
	</div>`;

	frm.fields_dict.shortcut_key.set_description(html);
}

function show_test_dialog(frm) {
	const key = frm.doc.shortcut_key || '';
	const parts = key.split('+');
	const kbd_html = parts.map(p => `<kbd style="
		padding:4px 10px;margin:2px;
		background:#f5f5f5;border:1px solid #ccc;
		border-bottom:3px solid #999;border-radius:4px;
		font-size:15px;font-family:monospace;
	">${p}</kbd>`).join(' <span style="opacity:.5;font-size:18px">+</span> ');

	let target_html = '';
	if (frm.doc.target_type === 'DocType' && frm.doc.target_doctype) {
		const mode = frm.doc.open_mode || 'List';
		target_html = `Opens <strong>${frm.doc.target_doctype}</strong> in <strong>${mode}</strong> view`;
	} else if (frm.doc.target_type === 'Report' && frm.doc.target_report) {
		target_html = `Opens report <strong>${frm.doc.target_report}</strong>`;
	} else if (frm.doc.target_type === 'Page' && frm.doc.target_page) {
		target_html = `Opens page <strong>${frm.doc.target_page}</strong>`;
	}

	const status_badge = frm.doc.enabled
		? `<span style="color:green;font-weight:600">&#10003; Enabled</span>`
		: `<span style="color:red;font-weight:600">&#10007; Disabled</span>`;

	frappe.msgprint({
		title: __('Shortcut Preview'),
		message: `
			<div style="text-align:center;padding:16px 0">
				<div style="margin-bottom:12px">${kbd_html}</div>
				<div style="margin-bottom:8px;font-size:14px">${target_html}</div>
				<div>${status_badge}</div>
				${frm.doc.description ? `<div style="margin-top:10px;color:#666;font-size:12px">${frm.doc.description}</div>` : ''}
			</div>
		`,
		indicator: frm.doc.enabled ? 'green' : 'orange'
	});
}
