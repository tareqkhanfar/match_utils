# Copyright (c) 2026, match systems and contributors
# For license information, please see license.txt

from match_utils.match_utils.report.statement_of_account import execute as _execute


def execute(filters=None):
	return _execute(filters, party_type="Supplier")
