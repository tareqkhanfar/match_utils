// Match Systems branding overrides — runs on every page load
frappe.after_ajax(function () {

	/* ── 1. Remove About & Frappe Support from user avatar menu ──────── */
	const LABELS_TO_REMOVE = ["About", "Frappe Support"];

	const _original_create_menu = frappe.ui.create_menu;
	frappe.ui.create_menu = function (opts) {
		if (opts && opts.menu_items) {
			opts.menu_items = opts.menu_items.filter(function (item) {
				return !LABELS_TO_REMOVE.includes(item.label);
			});
		}
		return _original_create_menu.call(this, opts);
	};

	/* ── 2. Replace "ERPNext" with "Match ERP" everywhere in the DOM ── */
	const BRAND_MAP = {
		"ERPNext": "Match ERP",
		"Erpnext": "Match ERP",
		"erpnext": "match_erp",         // keep lowercase slug untouched in URLs
	};

	function replace_text_nodes(root) {
		const walker = document.createTreeWalker(
			root || document.body,
			NodeFilter.SHOW_TEXT,
			null,
			false
		);
		let node;
		while ((node = walker.nextNode())) {
			const original = node.nodeValue;
			let replaced = original
				.replace(/ERPNext/g, "Match ERP")
				.replace(/Erpnext/g, "Match ERP");
			if (replaced !== original) node.nodeValue = replaced;
		}
		// Also fix title/placeholder/alt attributes
		root = root || document;
		root.querySelectorAll("[title],[placeholder],[alt]").forEach(function (el) {
			["title", "placeholder", "alt"].forEach(function (attr) {
				const v = el.getAttribute(attr);
				if (v && v.includes("ERPNext")) {
					el.setAttribute(attr, v.replace(/ERPNext/g, "Match ERP"));
				}
			});
		});
	}

	// Run on initial load
	$(document).on("app_ready page-change", function () {
		setTimeout(replace_text_nodes, 100);
	});

	// Also patch frappe.get_versions / About dialog
	const _show_about = frappe.ui.toolbar.show_about;
	if (_show_about) {
		frappe.ui.toolbar.show_about = function () {
			_show_about.apply(this, arguments);
			setTimeout(function () {
				$(".modal-body, #about-app-versions").each(function () {
					replace_text_nodes(this);
				});
			}, 300);
		};
	}

	// Patch app switcher card title
	$(document).on("app_ready", function () {
		setTimeout(function () {
			$(".app-card-title, .app-title, .app-name").each(function () {
				const $el = $(this);
				if ($el.text().trim() === "ERPNext") {
					$el.text("Match ERP");
				}
			});
			replace_text_nodes();
		}, 200);
	});

	// Observe DOM mutations to catch dynamically rendered text
	if (window.MutationObserver) {
		const observer = new MutationObserver(function (mutations) {
			mutations.forEach(function (m) {
				m.addedNodes.forEach(function (node) {
					if (node.nodeType === 1) replace_text_nodes(node);
					else if (node.nodeType === 3) {
						const v = node.nodeValue;
						if (v && v.includes("ERPNext")) {
							node.nodeValue = v.replace(/ERPNext/g, "Match ERP");
						}
					}
				});
			});
		});
		document.addEventListener("DOMContentLoaded", function () {
			observer.observe(document.body, { childList: true, subtree: true });
		});
		// If already loaded
		if (document.body) {
			observer.observe(document.body, { childList: true, subtree: true });
		}
	}

	/* ── 3. Replace document <title> tag ────────────────────────────── */
	const _original_title = Object.getOwnPropertyDescriptor(Document.prototype, "title");
	if (_original_title && _original_title.set) {
		Object.defineProperty(document, "title", {
			get: function () {
				return _original_title.get.call(this);
			},
			set: function (val) {
				_original_title.set.call(
					this,
					val ? val.replace(/ERPNext/g, "Match ERP") : val
				);
			},
			configurable: true,
		});
		// Fix current title
		if (document.title.includes("ERPNext")) {
			document.title = document.title.replace(/ERPNext/g, "Match ERP");
		}
	}
	/* ── 4. Unwrap links that point to Frappe / ERPNext sites ─────────── */
	// e.g. the "Submitted Record cannot be deleted... Cancel it first" message
	// (frappe/model/delete_doc.py) links to docs.frappe.io. The link text is
	// kept; only the anchor is removed so users never get sent off-site.
	const EXTERNAL_BRAND_LINK = /^https?:\/\/([^/]*\.)?(frappe\.io|frappecloud\.com|frappe\.school|erpnext\.com|github\.com\/frappe)(\/|$)/i;

	function unwrap_brand_links(root) {
		(root || document).querySelectorAll("a[href]").forEach(function (a) {
			if (EXTERNAL_BRAND_LINK.test(a.getAttribute("href") || "")) {
				a.replaceWith(document.createTextNode(a.textContent));
			}
		});
	}

	if (window.MutationObserver) {
		const link_observer = new MutationObserver(function (mutations) {
			mutations.forEach(function (m) {
				m.addedNodes.forEach(function (node) {
					if (node.nodeType === 1) {
						if (node.tagName === "A") unwrap_brand_links(node.parentNode);
						else unwrap_brand_links(node);
					}
				});
			});
		});
		const start_link_observer = function () {
			link_observer.observe(document.body, { childList: true, subtree: true });
		};
		if (document.body) start_link_observer();
		else document.addEventListener("DOMContentLoaded", start_link_observer);
	}
	$(document).on("app_ready page-change", function () {
		setTimeout(unwrap_brand_links, 200);
	});
});
