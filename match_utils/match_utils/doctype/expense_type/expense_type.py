# Copyright (c) 2026, match systems and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class ExpenseType(Document):
	def validate(self):
		self.validate_duplicate_company()

	def validate_duplicate_company(self):
		seen_companies = set()
		for row in self.accounts:
			if not row.company:
				continue
			if row.company in seen_companies:
				frappe.throw(
					_("Row #{0}: Company {1} is already mapped in another row. Each company can appear only once.").format(
						row.idx, row.company
					)
				)
			seen_companies.add(row.company)
