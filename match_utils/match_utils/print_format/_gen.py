"""Generator for the Statement of Account print formats.
Run with: python3 _gen.py   (writes the two JSON fixtures)
Kept in-repo so the formats are reproducible.
"""

import json
import os

CSS = r"""@import url("https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;600&display=swap");

:root {
  --ink:       #0d1117;
  --ink-soft:  #4a5568;
  --rule:      #d0d7de;
  --rule-dark: #0d1117;
  --accent:    #0550ae;
  --accent-bg: #dbeafe;
  --row-alt:   #f6f8fa;
  --white:     #ffffff;
  --red:       #b91c1c;
  --green:     #15803d;
  --debit-bg:  #fff7ed;
  --credit-bg: #f0fdf4;
  --sans:      "Cairo", sans-serif;
  --mono:      "IBM Plex Mono", monospace;
}

.soa-wrap { font-family: var(--sans); font-size: 9pt; color: var(--ink); direction: rtl; text-align: right; }

/* HEADER */
.soa-header {
  display: grid; grid-template-columns: auto 1fr auto; align-items: center;
  border-bottom: 2.5px solid var(--rule-dark); padding-bottom: 10px; margin-bottom: 12px; gap: 12px;
}
.soa-logo { max-height: 64px; max-width: 160px; object-fit: contain; }
.soa-report-name { font-size: 14pt; font-weight: 700; color: var(--accent); letter-spacing: .3px; }
.soa-period      { font-size: 8pt; color: var(--ink-soft); margin-top: 3px; }
.soa-printed-by  { font-size: 7pt; color: var(--ink-soft); font-family: var(--mono); margin-top: 2px; direction: ltr; text-align: left; }
.soa-title-block { text-align: left; direction: ltr; }
.soa-company-name { font-size: 15pt; font-weight: 700; color: var(--ink); }
.soa-company-meta { font-size: 7.5pt; color: var(--ink-soft); margin-top: 3px; }
.soa-currency-badge {
  display: inline-block; background: var(--accent-bg); color: var(--accent);
  font-family: var(--mono); font-size: 7pt; font-weight: 600;
  padding: 1px 6px; border-radius: 3px; margin-right: 5px; direction: ltr;
}

/* ITEM SUB-TABLE (Show Details) */
.soa-items-row td { padding: 0 !important; background: #fbfdff !important; border-left: none !important; }
.soa-subtable-wrap { padding: 4px 26px 8px 26px; }
.soa-subtable-title { font-size: 7.5pt; font-weight: 700; color: var(--accent); margin-bottom: 3px; }
.soa-subtable { width: 100%; border-collapse: collapse; font-size: 7.8pt; border: 1px solid #cfe0f5; }
.soa-subtable thead tr { background: #eaf2fd; }
.soa-subtable th { padding: 3px 6px; text-align: center; font-weight: 700; color: #1e3a5f; border: 1px solid #cfe0f5; white-space: nowrap; }
.soa-subtable td { padding: 3px 6px; text-align: center; border: 1px solid #e3edf9; }
.soa-subtable td.txt { text-align: right; }
.soa-subtable td.num { text-align: left; font-family: var(--mono); direction: ltr; }
.soa-subtable tfoot td { font-weight: 700; background: #f3f8ff; }

/* FILTERS STRIP */
.soa-filters {
  display: flex; flex-wrap: wrap; gap: 6px 16px;
  background: var(--row-alt); border: 1px solid var(--rule);
  border-radius: 5px; padding: 7px 12px; margin-bottom: 16px; font-size: 8pt;
}
.soa-filter-lbl { color: var(--ink-soft); font-weight: 600; font-size: 7pt; margin-left: 4px; }
.soa-filter-val { color: var(--ink); font-weight: 600; }

/* TABLE */
.soa-table { width: 100%; border-collapse: collapse; border: 1px solid var(--rule); font-size: 8.5pt; }
.soa-table thead tr { background: #1e293b; color: var(--white); }
.soa-table thead th {
  padding: 6px 7px; text-align: center; font-size: 7.5pt; font-weight: 600;
  letter-spacing: .3px; white-space: nowrap; border-left: 1px solid rgba(255,255,255,.12);
}
.soa-table thead th:last-child { border-left: none; }
.soa-table tbody tr:nth-child(even) { background: var(--row-alt); }
.soa-table tbody td {
  padding: 4px 7px; border-bottom: 1px solid var(--rule);
  border-left: 1px solid var(--rule); vertical-align: middle; text-align: center;
}
.soa-table tbody td:last-child { border-left: none; }
.soa-table .txt { text-align: right; }
.soa-table .num { text-align: left; font-family: var(--mono); font-size: 8pt; white-space: nowrap; direction: ltr; }
.soa-table .dt  { font-family: var(--mono); font-size: 7.5pt; color: var(--ink-soft); white-space: nowrap; direction: ltr; }
.soa-table .vc  { font-family: var(--mono); font-size: 7.5pt; color: var(--accent); font-weight: 600; direction: ltr; }
.soa-table .dr-cell { background: var(--debit-bg); color: var(--red); }
.soa-table .cr-cell { background: var(--credit-bg); color: var(--green); }

/* Opening / Total / Detail rows */
.soa-row-open td  { background: #eff6ff !important; font-weight: 700; color: #1e40af; border-top: 1.5px solid #bfdbfe !important; border-bottom: 1.5px solid #bfdbfe !important; }
.soa-row-total td { background: #1e293b !important; color: var(--white) !important; font-weight: 700; font-size: 9pt; border-top: 2px solid var(--ink) !important; }
.soa-row-detail td { background: #fcfcfc !important; color: var(--ink-soft); font-size: 7.5pt; font-style: italic; }
.soa-detail-label { padding-right: 14px !important; }

/* GRAND TOTALS */
.soa-grand { margin-top: 22px; display: flex; justify-content: space-between; align-items: flex-end; flex-direction: row-reverse; }
.soa-totals-box { border: 1.5px solid var(--rule-dark); border-radius: 5px; overflow: hidden; min-width: 340px; }
.soa-totals-head { background: var(--ink); color: var(--white); padding: 5px 12px; font-size: 8pt; font-weight: 700; text-align: center; }
.soa-totals-grid { display: flex; }
.soa-tc { flex: 1; padding: 8px 12px; border-right: 1px solid var(--rule); text-align: center; }
.soa-tc:last-child { border-right: none; }
.soa-tc-lbl { font-size: 7pt; color: var(--ink-soft); font-weight: 600; margin-bottom: 3px; }
.soa-tc-val { font-family: var(--mono); font-size: 10pt; font-weight: 700; color: var(--ink); direction: ltr; }
.soa-tc-val.dr { color: var(--red); }
.soa-tc-val.cr { color: var(--green); }

/* SIGNATURES */
.soa-sigs { display: flex; gap: 28px; }
.soa-sig  { text-align: center; min-width: 110px; }
.soa-sig-line { border-top: 1px solid var(--ink); padding-top: 4px; font-size: 7.5pt; color: var(--ink-soft); margin-top: 32px; }

/* FOOTER */
.soa-footer { margin-top: 18px; border-top: 1px solid var(--rule); padding-top: 6px; display: flex; justify-content: space-between; align-items: center; font-size: 7pt; color: var(--ink-soft); }
.soa-footer-brand { font-weight: 700; color: var(--accent); }

@media print {
  .soa-table thead { display: table-header-group; }
  tr { page-break-inside: avoid; }
}
"""

# HTML microtemplate. __TITLE__, __PARTY_LABEL__, __PARTY_FIELD__ are substituted.
HTML = r"""{%
  function fmtMoney(v) {
    if (v === "" || v === null || v === undefined) return "";
    return format_currency(v, filters.company_currency || "");
  }
  function fmtDate(d) {
    if (!d) return "";
    return frappe.datetime.str_to_user(d);
  }
  function vtype(v) {
    if (v === "Sales Invoice") return "فاتورة مبيعات";
    if (v === "Purchase Invoice") return "فاتورة مشتريات";
    if (v === "Payment Entry") return "سند دفع";
    if (v === "Journal Entry") return "قيد يومية";
    if (v === "Sales Order") return "أمر مبيعات";
    if (v === "Purchase Order") return "أمر مشتريات";
    if (v === "Delivery Note") return "إشعار تسليم";
    if (v === "Purchase Receipt") return "إشعار استلام";
    return v || "";
  }

  var totalDebit = 0, totalCredit = 0, closingBalance = 0;
  for (var i = 0; i < data.length; i++) {
    var r = data[i];
    if (r.is_total) {
      totalDebit = parseFloat(r.debit || 0);
      totalCredit = parseFloat(r.credit || 0);
      closingBalance = parseFloat(r.balance || 0);
    }
  }
  var cur = filters.company_currency || "";
  var now = frappe.datetime.now_datetime ? frappe.datetime.now_datetime() : "";
%}

<div class="soa-wrap">

  <div class="soa-header">
    {% if (filters.company_logo) { %}
      <img class="soa-logo" src="{%= filters.company_logo %}">
    {% } else { %}
      <div></div>
    {% } %}
    <div>
      <div class="soa-report-name">
        __TITLE__
        <span class="soa-currency-badge">{%= cur %}</span>
      </div>
      <div class="soa-period">
        الفترة: <strong>{%= fmtDate(filters.from_date) %}</strong>
        — <strong>{%= fmtDate(filters.to_date) %}</strong>
      </div>
    </div>
    <div class="soa-title-block">
      <div class="soa-company-name">{%= filters.company || "" %}</div>
      <div class="soa-printed-by">Printed: {%= now %}</div>
    </div>
  </div>

  <div class="soa-filters">
    <span>
      <span class="soa-filter-lbl">__PARTY_LABEL__</span>
      <span class="soa-filter-val">{%= filters.__PARTY_FIELD__ || "" %}</span>
    </span>
    <span>
      <span class="soa-filter-lbl">الشركة</span>
      <span class="soa-filter-val">{%= filters.company || "" %}</span>
    </span>
    <span>
      <span class="soa-filter-lbl">من تاريخ</span>
      <span class="soa-filter-val">{%= fmtDate(filters.from_date) %}</span>
    </span>
    <span>
      <span class="soa-filter-lbl">إلى تاريخ</span>
      <span class="soa-filter-val">{%= fmtDate(filters.to_date) %}</span>
    </span>
  </div>

  <table class="soa-table">
    <thead>
      <tr>
        <th style="width: 11%;">التاريخ</th>
        <th style="width: 13%;">نوع المستند</th>
        <th style="width: 14%;">رقم المستند</th>
        <th style="width: 24%;">البيان</th>
        <th style="width: 12%;">مدين ({%= cur %})</th>
        <th style="width: 12%;">دائن ({%= cur %})</th>
        <th style="width: 14%;">الرصيد</th>
      </tr>
    </thead>
    <tbody>
      {% for (var i = 0; i < data.length; i++) { %}
        {% var row = data[i]; %}
        {% if (row.is_detail) { continue; } %}
        {% var cls = ""; %}
        {% if (row.is_opening) { cls = "soa-row-open"; } %}
        {% if (row.is_total) { cls = "soa-row-total"; } %}
        <tr class="{%= cls %}">
          <td class="dt">{%= fmtDate(row.posting_date) %}</td>
          <td>{%= vtype(row.voucher_type) %}</td>
          <td class="vc">{%= row.voucher_no || "" %}</td>
          <td class="txt">{%= row.remarks || "" %}</td>
          <td class="num {%= (row.debit && !row.is_total && !row.is_opening) ? "dr-cell" : "" %}">{%= row.debit ? fmtMoney(row.debit) : "" %}</td>
          <td class="num {%= (row.credit && !row.is_total && !row.is_opening) ? "cr-cell" : "" %}">{%= row.credit ? fmtMoney(row.credit) : "" %}</td>
          <td class="num">{%= (row.balance === "" || row.balance === undefined) ? "" : fmtMoney(row.balance) %}</td>
        </tr>
        {% if (row._items && row._items.length) { %}
          <tr class="soa-items-row">
            <td colspan="7">
              <div class="soa-subtable-wrap">
                <div class="soa-subtable-title">تفاصيل أصناف الفاتورة {%= row.voucher_no || "" %}</div>
                <table class="soa-subtable">
                  <thead>
                    <tr>
                      <th style="width: 6%;">م</th>
                      <th style="width: 40%;">الصنف</th>
                      <th style="width: 14%;">الكمية</th>
                      <th style="width: 10%;">الوحدة</th>
                      <th style="width: 15%;">السعر</th>
                      <th style="width: 15%;">المجموع</th>
                    </tr>
                  </thead>
                  <tbody>
                    {% for (var j = 0; j < row._items.length; j++) { %}
                      {% var it = row._items[j]; %}
                      <tr>
                        <td>{%= j + 1 %}</td>
                        <td class="txt">{%= it.item_name || "" %}</td>
                        <td class="num">{%= it.qty %}</td>
                        <td>{%= it.uom || "" %}</td>
                        <td class="num">{%= fmtMoney(it.rate) %}</td>
                        <td class="num">{%= fmtMoney(it.amount) %}</td>
                      </tr>
                    {% } %}
                  </tbody>
                </table>
              </div>
            </td>
          </tr>
        {% } %}
      {% } %}
    </tbody>
  </table>

  <div class="soa-grand">
    <div class="soa-totals-box">
      <div class="soa-totals-head">ملخص الحساب</div>
      <div class="soa-totals-grid">
        <div class="soa-tc">
          <div class="soa-tc-lbl">إجمالي المدين</div>
          <div class="soa-tc-val dr">{%= fmtMoney(totalDebit) %}</div>
        </div>
        <div class="soa-tc">
          <div class="soa-tc-lbl">إجمالي الدائن</div>
          <div class="soa-tc-val cr">{%= fmtMoney(totalCredit) %}</div>
        </div>
        <div class="soa-tc">
          <div class="soa-tc-lbl">الرصيد النهائي</div>
          <div class="soa-tc-val">{%= fmtMoney(closingBalance) %}</div>
        </div>
      </div>
    </div>
    <div class="soa-sigs">
      <div class="soa-sig"><div class="soa-sig-line">المحاسب</div></div>
      <div class="soa-sig"><div class="soa-sig-line">المدير المالي</div></div>
    </div>
  </div>

  <div class="soa-footer">
    <span>{%= filters.company || "" %} — كشف حساب سري</span>
    <span class="soa-footer-brand">Powered by Match Systems — شركة ماتش سيستمز لحلول الأنظمة التكنولوجية</span>
    <span>Printed: {%= now %}</span>
  </div>

</div>
"""


def html_for(party_label, party_field, title_ar):
	return (
		HTML.replace("__TITLE__", title_ar)
		.replace("__PARTY_LABEL__", party_label)
		.replace("__PARTY_FIELD__", party_field)
	)


FORMATS = {
	"Customer Statement of Account": ("العميل", "customer", "كشف حساب العميل"),
	"Supplier Statement of Account": ("المورد", "supplier", "كشف حساب المورد"),
}


def main():
	base = os.path.dirname(os.path.abspath(__file__))
	for report_name, (party_label, party_field, title_ar) in FORMATS.items():
		folder = os.path.join(base, report_name.lower().replace(" ", "_").replace("-", "_"))
		os.makedirs(folder, exist_ok=True)
		doc = {
			"absolute_value": 0,
			"align_labels_right": 0,
			"creation": "2026-06-22 12:00:00.000000",
			"css": CSS,
			"custom_format": 1,
			"default_print_language": "ar",
			"disabled": 0,
			"doc_type": None,
			"docstatus": 0,
			"doctype": "Print Format",
			"font_size": 0,
			"html": html_for(party_label, party_field, title_ar),
			"idx": 0,
			"line_breaks": 0,
			"margin_bottom": 0.0,
			"margin_left": 0.0,
			"margin_right": 0.0,
			"margin_top": 0.0,
			"modified": "2026-06-22 12:00:00.000000",
			"modified_by": "Administrator",
			"module": "Match Utils",
			"name": report_name,
			"owner": "Administrator",
			"pdf_generator": "chrome",
			"print_format_builder": 0,
			"print_format_type": "JS",
			"raw_printing": 0,
			"report": report_name,
			"show_section_headings": 0,
			"standard": "Yes",
		}
		path = os.path.join(folder, os.path.basename(folder) + ".json")
		with open(path, "w", encoding="utf-8") as f:
			json.dump(doc, f, ensure_ascii=False, indent=1)
		print("wrote:", path)


if __name__ == "__main__":
	main()
