# Copyright (c) 2026, match systems and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import secrets
from frappe.utils import now_datetime, add_days, get_datetime
from frappe.utils.pdf import get_pdf

@frappe.whitelist()
def get_active_shortcuts():
	"""Get all active keyboard shortcuts for current user"""
	try:
		shortcuts = frappe.get_all(
			'Shortcut Mapper',
			filters={'enabled': 1},
			fields=['shortcut_key', 'target_type', 'target_doctype', 'target_report', 'target_page', 'enabled']
		)
		
		shortcut_map = {}
		for shortcut in shortcuts:
			shortcut_map[shortcut.shortcut_key] = {
				'target_type': shortcut.target_type,
				'target_doctype': shortcut.target_doctype,
				'target_report': shortcut.target_report,
				'target_page': shortcut.target_page,
				'enabled': shortcut.enabled
			}
		
		return shortcut_map
	except Exception as e:
		frappe.log_error(f"Error loading shortcuts: {str(e)}")
		return {}

@frappe.whitelist()
def reload_shortcuts():
	"""Notify all connected clients to reload shortcuts"""
	frappe.publish_realtime('shortcuts_updated')
	return {'message': _('Shortcuts reloaded successfully')}

@frappe.whitelist()
def generate_share_link(doctype, docname):
	"""Generate a public share link for any document PDF"""
	
	try:
		# Check permissions
		if not frappe.has_permission(doctype, "read", docname):
			frappe.throw(_("No permission to share this document"))
		
		# Verify document exists
		if not frappe.db.exists(doctype, docname):
			frappe.throw(_("Document {0} {1} not found").format(doctype, docname))
		
		# Generate unique token
		token = secrets.token_urlsafe(32)
		
		# Check if Document Share Key doctype exists
		if not frappe.db.exists("DocType", "Document Share Key"):
			create_document_share_key_doctype()
		
		# Calculate expiration date (set to 10 years for unlimited access)
		expiry_datetime = add_days(now_datetime(), 3650)
		
		# Create or update share record
		existing = frappe.db.get_value(
			"Document Share Key",
			{"reference_doctype": doctype, "reference_docname": docname},
			"name"
		)
		
		if existing:
			share_doc = frappe.get_doc("Document Share Key", existing)
			share_doc.key = token
			share_doc.expires_on = expiry_datetime
			share_doc.created_by = frappe.session.user
			share_doc.save(ignore_permissions=True)
		else:
			share_doc = frappe.get_doc({
				"doctype": "Document Share Key",
				"reference_doctype": doctype,
				"reference_docname": docname,
				"key": token,
				"expires_on": expiry_datetime,
				"created_by": frappe.session.user
			})
			share_doc.insert(ignore_permissions=True)
		
		# Commit the transaction immediately
		frappe.db.commit()

		# Add a small delay to ensure database replication/consistency
		# This prevents "Invalid Link" errors on first click
		import time
		time.sleep(0.1)

		frappe.logger().info(f"Share link created: {token} for {doctype} {docname}")

		return {
			"route": f"/api/method/match_utils.api.view_shared_pdf?key={token}",
			"expires_in": "Unlimited",
			"token": token,
			"share_key_name": share_doc.name
		}
		
	except Exception as e:
		frappe.log_error(f"Error generating share link: {str(e)}", "Share Link Error")
		frappe.throw(_("Error generating share link: {0}").format(str(e)))

@frappe.whitelist(allow_guest=True)
def view_shared_pdf(key):
	"""View shared document PDF via public link"""

	try:
		if not key:
			frappe.respond_as_web_page(
				_("Invalid Request"),
				_("No share key provided"),
				indicator_color='red',
				http_status_code=400
			)
			return

		# Find share record with retry mechanism for race conditions
		share = None
		max_retries = 3

		for attempt in range(max_retries):
			share = frappe.db.get_value(
				"Document Share Key",
				{"key": key},
				["name", "reference_doctype", "reference_docname", "expires_on"],
				as_dict=True
			)

			if share:
				break

			# If not found and we have retries left, wait a bit
			if attempt < max_retries - 1:
				import time
				time.sleep(0.2)  # Wait 200ms before retry

		if not share:
			frappe.logger().error(f"Share key not found: {key}")
			frappe.respond_as_web_page(
				_("Invalid Link"),
				_("This share link is invalid or has been removed."),
				indicator_color='red',
				http_status_code=404
			)
			return
		
		# Convert expires_on to datetime for comparison
		expiry_datetime = get_datetime(share.expires_on)
		current_datetime = now_datetime()
		
		# Check expiration
		if expiry_datetime < current_datetime:
			frappe.respond_as_web_page(
				_("Link Expired"),
				_("This share link has expired on {0}.").format(frappe.format(expiry_datetime, {'fieldtype': 'Datetime'})),
				indicator_color='red',
				http_status_code=410
			)
			return
		
		# Check if document still exists
		if not frappe.db.exists(share.reference_doctype, share.reference_docname):
			frappe.respond_as_web_page(
				_("Document Not Found"),
				_("The document associated with this link no longer exists."),
				indicator_color='red',
				http_status_code=404
			)
			return
		
		# Get the document
		doc = frappe.get_doc(share.reference_doctype, share.reference_docname)
		
		# Get print format - try to find the default one
		print_format = frappe.db.get_value(
			"Print Format",
			{"doc_type": share.reference_doctype, "disabled": 0},
			"name"
		) or "Standard"
		
		# Generate PDF
		html = frappe.get_print(
			share.reference_doctype,
			share.reference_docname,
			print_format=print_format,
			doc=doc,
			no_letterhead=0
		)
		
		pdf = get_pdf(html)
		
		# Log access
		frappe.logger().info(f"PDF accessed via share link: {key} for {share.reference_doctype} {share.reference_docname}")
		
		# Return PDF
		frappe.local.response.filename = f"{share.reference_docname}.pdf"
		frappe.local.response.filecontent = pdf
		frappe.local.response.type = "pdf"
		
	except Exception as e:
		frappe.log_error(f"Error viewing shared PDF: {str(e)}", "View Shared PDF Error")
		frappe.respond_as_web_page(
			_("Error"),
			_("An error occurred while generating the PDF: {0}").format(str(e)),
			indicator_color='red',
			http_status_code=500
		)

def create_document_share_key_doctype():
	"""Create Document Share Key doctype if it doesn't exist"""
	if frappe.db.exists("DocType", "Document Share Key"):
		return
	
	try:
		doc = frappe.get_doc({
			"doctype": "DocType",
			"name": "Document Share Key",
			"module": "Match Utils",
			"custom": 0,
			"is_submittable": 0,
			"track_changes": 1,
			"autoname": "hash",
			"fields": [
				{
					"fieldname": "reference_doctype",
					"fieldtype": "Link",
					"label": "Reference DocType",
					"options": "DocType",
					"reqd": 1,
					"in_list_view": 1
				},
				{
					"fieldname": "reference_docname",
					"fieldtype": "Dynamic Link",
					"label": "Reference Document",
					"options": "reference_doctype",
					"reqd": 1,
					"in_list_view": 1
				},
				{
					"fieldname": "key",
					"fieldtype": "Data",
					"label": "Share Key",
					"unique": 1,
					"reqd": 1,
					"read_only": 1,
					"in_list_view": 1
				},
				{
					"fieldname": "expires_on",
					"fieldtype": "Datetime",
					"label": "Expires On",
					"reqd": 1,
					"in_list_view": 1
				},
				{
					"fieldname": "created_by",
					"fieldtype": "Link",
					"label": "Created By",
					"options": "User",
					"in_list_view": 1
				}
			],
			"permissions": [
				{
					"role": "System Manager",
					"read": 1,
					"write": 1,
					"create": 1,
					"delete": 1
				},
				{
					"role": "All",
					"read": 1
				}
			]
		})
		doc.insert(ignore_permissions=True)
		frappe.db.commit()
		frappe.logger().info("Document Share Key doctype created successfully")
	except Exception as e:
		frappe.log_error(f"Error creating Document Share Key doctype: {str(e)}")
		raise
