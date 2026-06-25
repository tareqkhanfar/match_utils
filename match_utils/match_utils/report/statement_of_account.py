# Copyright (c) 2026, match systems and contributors
# For license information, please see license.txt

"""Shared logic for Customer / Supplier Statement of Account reports.

Both reports are thin wrappers around `execute(filters, party_type)`.
Works on Frappe v15 and v16 (only standard GL Entry fields are used).
"""

import frappe
from frappe import _
from frappe.utils import flt, getdate


def execute(filters, party_type):
	filters = frappe._dict(filters or {})
	_validate_filters(filters, party_type)

	columns = _get_columns(party_type)
	data = _get_data(filters, party_type)
	return columns, data


def _validate_filters(filters, party_type):
	party_field = party_type.lower()  # "customer" / "supplier"
	if not filters.get("company"):
		frappe.throw(_("Please select a Company"))
	if not filters.get(party_field):
		frappe.throw(_("Please select a {0}").format(_(party_type)))
	if not filters.get("from_date") or not filters.get("to_date"):
		frappe.throw(_("Please select From Date and To Date"))
	if getdate(filters.from_date) > getdate(filters.to_date):
		frappe.throw(_("From Date cannot be after To Date"))


def _get_columns(party_type):
	currency_options = "Company:company:default_currency"
	return [
		{"label": _("Posting Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 110},
		{"label": _("Voucher Type"), "fieldname": "voucher_type", "fieldtype": "Data", "width": 130},
		{
			"label": _("Voucher No"),
			"fieldname": "voucher_no",
			"fieldtype": "Dynamic Link",
			"options": "voucher_type",
			"width": 160,
		},
		{"label": _("Remarks"), "fieldname": "remarks", "fieldtype": "Data", "width": 250},
		{
			"label": _("Debit"),
			"fieldname": "debit",
			"fieldtype": "Currency",
			"options": currency_options,
			"width": 120,
		},
		{
			"label": _("Credit"),
			"fieldname": "credit",
			"fieldtype": "Currency",
			"options": currency_options,
			"width": 120,
		},
		{
			"label": _("Amount"),
			"fieldname": "amount",
			"fieldtype": "Currency",
			"options": currency_options,
			"width": 120,
		},
		{
			"label": _("Running Balance"),
			"fieldname": "balance",
			"fieldtype": "Currency",
			"options": currency_options,
			"width": 140,
		},
	]


def _get_party_conditions(filters, party_type):
	conditions = {
		"party_type": party_type,
		"party": filters.get(party_type.lower()),
		"company": filters.company,
		"is_cancelled": 0,
	}
	return conditions


def _get_opening_balance(filters, party_type):
	"""Sum of (debit - credit) for the party before From Date."""
	rows = frappe.get_all(
		"GL Entry",
		filters={
			**_get_party_conditions(filters, party_type),
			"posting_date": ["<", filters.from_date],
		},
		fields=["sum(debit) as debit", "sum(credit) as credit"],
	)
	if rows and rows[0]:
		return flt(rows[0].debit) - flt(rows[0].credit)
	return 0.0


def _get_gl_entries(filters, party_type):
	return frappe.get_all(
		"GL Entry",
		filters={
			**_get_party_conditions(filters, party_type),
			"posting_date": ["between", [filters.from_date, filters.to_date]],
		},
		fields=[
			"posting_date",
			"voucher_type",
			"voucher_no",
			"remarks",
			"debit",
			"credit",
			"against_voucher_type",
			"against_voucher",
		],
		order_by="posting_date asc, creation asc",
	)


def _get_data(filters, party_type):
	data = []
	balance = _get_opening_balance(filters, party_type)

	# Opening balance row (always first)
	data.append(
		{
			"posting_date": filters.from_date,
			"voucher_type": "",
			"voucher_no": "",
			"remarks": _("Opening Balance"),
			"debit": 0.0,
			"credit": 0.0,
			"amount": balance,
			"balance": balance,
			"is_opening": 1,
		}
	)

	total_debit = 0.0
	total_credit = 0.0
	show_details = int(filters.get("show_details") or 0)

	for gle in _get_gl_entries(filters, party_type):
		debit = flt(gle.debit)
		credit = flt(gle.credit)
		amount = debit - credit
		balance += amount
		total_debit += debit
		total_credit += credit

		data.append(
			{
				"posting_date": gle.posting_date,
				"voucher_type": gle.voucher_type,
				"voucher_no": gle.voucher_no,
				"remarks": gle.remarks,
				"debit": debit,
				"credit": credit,
				"amount": amount,
				"balance": balance,
			}
		)

		if show_details:
			data.extend(_get_detail_rows(gle, party_type))

	# Total row
	data.append(
		{
			"posting_date": "",
			"voucher_type": "",
			"voucher_no": "",
			"remarks": _("Total"),
			"debit": total_debit,
			"credit": total_credit,
			"amount": total_debit - total_credit,
			"balance": balance,
			"is_total": 1,
		}
	)

	return data


# Voucher type -> (child doctype, parent fieldname) for detail expansion
_DETAIL_SOURCES = {
	"Sales Invoice": "Sales Invoice Item",
	"Purchase Invoice": "Purchase Invoice Item",
}


def _get_detail_rows(gle, party_type):
	"""Return indented item rows for invoice vouchers when Show Details is on."""
	child_doctype = _DETAIL_SOURCES.get(gle.voucher_type)
	if not child_doctype:
		return []

	items = frappe.get_all(
		child_doctype,
		filters={"parent": gle.voucher_no, "parenttype": gle.voucher_type},
		fields=["item_code", "item_name", "qty", "uom", "rate", "amount"],
		order_by="idx asc",
	)

	rows = []
	for item in items:
		label = item.item_name or item.item_code or ""
		detail = "{0} — {1} {2} × {3}".format(
			label, flt(item.qty), item.uom or "", flt(item.rate)
		)
		rows.append(
			{
				"posting_date": "",
				"voucher_type": "",
				"voucher_no": "",
				"remarks": detail,
				"debit": 0.0,
				"credit": 0.0,
				"amount": flt(item.amount),
				"balance": "",
				"indent": 1,
				"is_detail": 1,
			}
		)
	return rows
