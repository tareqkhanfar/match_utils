# Copyright (c) 2026, match systems and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _

class ShortcutMapper(Document):
	def validate(self):
		# Validate and normalize shortcut key format
		
		if self.shortcut_key:
			self.shortcut_key = self.shortcut_key.upper().strip()
			self.validate_shortcut_format()
			
		# Validate target based on type
		self.validate_target()
		
	def validate_shortcut_format(self):
		"""Validate shortcut key format"""
		valid_modifiers = ['CTRL', 'ALT', 'SHIFT', 'META']
		parts = self.shortcut_key.split('+')
		
		# Check if shortcut has at least one modifier
		has_modifier = any(part in valid_modifiers for part in parts[:-1])
		
		if not has_modifier and len(parts) == 1:
			frappe.msgprint(
				_('Shortcut should include at least one modifier key (CTRL, ALT, SHIFT)'),
				indicator='orange',
				alert=True
			)
			
	def validate_target(self):
		"""Validate target based on type"""
		if self.target_type == "DocType":
			if not self.target_doctype:
				frappe.throw(_("Target DocType is required when Target Type is DocType"))
			# Clear other fields
			self.target_report = None
			self.target_page = None
			
		elif self.target_type == "Report":
			if not self.target_report:
				frappe.throw(_("Target Report is required when Target Type is Report"))
			# Clear other fields
			self.target_doctype = None
			self.target_page = None
			
		elif self.target_type == "Page":
			if not self.target_page:
				frappe.throw(_("Target Page is required when Target Type is Page"))
			# Clear other fields
			self.target_doctype = None
			self.target_report = None
			
	def on_update(self):
		"""Notify all users to reload shortcuts"""
		frappe.publish_realtime('shortcuts_updated')
		
	def on_trash(self):
		"""Notify all users to reload shortcuts when deleted"""
		frappe.publish_realtime('shortcuts_updated')