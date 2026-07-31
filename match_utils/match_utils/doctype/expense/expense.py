# Copyright (c) 2026, match systems and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class Expense(Document):
	def validate(self):
		self.set_accounts_from_expense_type()

		if self.amount is not None and self.amount <= 0:
			frappe.throw(_("Amount must be greater than zero"))

		if self.docstatus == 1 and self.party_type and not self.party:
			frappe.throw(_("Party is required when Party Type is set"))

	def set_accounts_from_expense_type(self):
		expense_type = frappe.get_doc("Expense Type", self.expense_type)

		account_row = None
		for row in expense_type.accounts:
			if row.company == self.company:
				account_row = row
				break

		if not account_row:
			frappe.throw(
				_("لا يوجد ربط حسابات لشركة {0} ضمن نوع المصروف {1}").format(
					self.company, self.expense_type
				)
			)

		self.expense_account = account_row.expense_account
		self.credit_account = account_row.credit_account
		self.party_type = account_row.party_type or None

		if not self.cost_center and account_row.default_cost_center:
			self.cost_center = account_row.default_cost_center

	def on_submit(self):
		je = self.create_journal_entry()
		self.db_set("journal_entry", je.name)

	def create_journal_entry(self):
		je = frappe.new_doc("Journal Entry")
		je.voucher_type = "Journal Entry"
		je.posting_date = self.posting_date
		je.company = self.company
		je.user_remark = f"Expense {self.name} - {self.expense_type}"

		debit_row = {
			"account": self.expense_account,
			"debit_in_account_currency": self.amount,
			"cost_center": self.cost_center,
			"reference_type": "Expense",
			"reference_name": self.name,
		}
		je.append("accounts", debit_row)

		credit_row = {
			"account": self.credit_account,
			"credit_in_account_currency": self.amount,
			"cost_center": self.cost_center,
			"reference_type": "Expense",
			"reference_name": self.name,
		}
		if self.party_type and self.party:
			credit_row["party_type"] = self.party_type
			credit_row["party"] = self.party
		je.append("accounts", credit_row)

		je.insert(ignore_permissions=True)
		je.submit()
		return je

	def on_cancel(self):
		if self.journal_entry:
			je = frappe.get_doc("Journal Entry", self.journal_entry)
			if je.docstatus == 1:
				je.cancel()
