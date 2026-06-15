# Copyright (c) 2026, match systems and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _

class ShortcutMapper(Document):
	def validate(self):
		if self.shortcut_key:
			self.shortcut_key = self.shortcut_key.upper().strip()
			self.validate_shortcut_format()

		self.validate_target()

	def validate_shortcut_format(self):
		"""Validate shortcut key format like CTRL+SHIFT+S"""
		valid_modifiers = ['CTRL', 'ALT', 'SHIFT', 'META']
		parts = self.shortcut_key.split('+')

		has_modifier = any(part in valid_modifiers for part in parts[:-1])

		if not has_modifier and len(parts) == 1:
			frappe.msgprint(
				_('Shortcut should include at least one modifier key (CTRL, ALT, SHIFT)'),
				indicator='orange',
				alert=True
			)

	def validate_target(self):
		"""Validate target based on type and set defaults"""
		if self.target_type == "DocType":
			if not self.target_doctype:
				frappe.throw(_("Target DocType is required when Target Type is DocType"))
			if not self.open_mode:
				self.open_mode = "List"
			self.target_report = None
			self.target_page = None

		elif self.target_type == "Report":
			if not self.target_report:
				frappe.throw(_("Target Report is required when Target Type is Report"))
			self.target_doctype = None
			self.open_mode = None
			self.target_page = None

		elif self.target_type == "Page":
			if not self.target_page:
				frappe.throw(_("Target Page is required when Target Type is Page"))
			self.target_doctype = None
			self.open_mode = None
			self.target_report = None

	def on_update(self):
		"""Notify all users to reload shortcuts"""
		frappe.publish_realtime('shortcuts_updated')

	def on_trash(self):
		"""Notify all users to reload shortcuts when deleted"""
		frappe.publish_realtime('shortcuts_updated')
