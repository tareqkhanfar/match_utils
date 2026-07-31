# Copyright (c) 2026, match systems and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

TEST_COMPANY = "_TC"
TEST_EXPENSE_ACCOUNT = "_Test Account Cost for Goods Sold - _TC"
TEST_CREDIT_ACCOUNT = "_Test Cash - _TC"
TEST_COST_CENTER = "Main - _TC"


class TestExpense(FrappeTestCase):
	def setUp(self):
		self.expense_type = make_expense_type()

	def tearDown(self):
		frappe.db.rollback()

	def test_submit_creates_journal_entry(self):
		expense = make_expense(self.expense_type.name, amount=250)
		expense.submit()

		self.assertTrue(expense.journal_entry)

		je = frappe.get_doc("Journal Entry", expense.journal_entry)
		self.assertEqual(je.docstatus, 1)

		debit_row = next(r for r in je.accounts if r.account == TEST_EXPENSE_ACCOUNT)
		credit_row = next(r for r in je.accounts if r.account == TEST_CREDIT_ACCOUNT)

		self.assertEqual(debit_row.debit_in_account_currency, 250)
		self.assertEqual(credit_row.credit_in_account_currency, 250)
		self.assertEqual(debit_row.reference_type, "Expense")
		self.assertEqual(debit_row.reference_name, expense.name)

		expense.cancel()
		je.reload()
		self.assertEqual(je.docstatus, 2)

	def test_missing_company_mapping_throws(self):
		expense_type = make_expense_type(company=TEST_COMPANY)
		expense = frappe.get_doc({
			"doctype": "Expense",
			"expense_type": expense_type.name,
			"company": "_Test Company 1" if frappe.db.exists("Company", "_Test Company 1") else TEST_COMPANY,
			"posting_date": frappe.utils.today(),
			"amount": 100,
		})

		if expense.company == TEST_COMPANY:
			self.skipTest("No second company available to test missing mapping")

		self.assertRaises(frappe.ValidationError, expense.insert)


def make_expense_type(company=TEST_COMPANY):
	name = frappe.generate_hash(length=8)
	expense_type = frappe.get_doc({
		"doctype": "Expense Type",
		"expense_type_name": f"Test Expense Type {name}",
		"accounts": [
			{
				"company": company,
				"expense_account": TEST_EXPENSE_ACCOUNT,
				"credit_account": TEST_CREDIT_ACCOUNT,
				"default_cost_center": TEST_COST_CENTER,
			}
		],
	})
	expense_type.insert(ignore_permissions=True)
	return expense_type


def make_expense(expense_type, amount=100):
	expense = frappe.get_doc({
		"doctype": "Expense",
		"expense_type": expense_type,
		"company": TEST_COMPANY,
		"posting_date": frappe.utils.today(),
		"amount": amount,
	})
	expense.insert(ignore_permissions=True)
	return expense
