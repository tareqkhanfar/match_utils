// Patch desktop.js setup_avatar to remove hardcoded About and Frappe Support items
frappe.after_ajax(function () {
	const LABELS_TO_REMOVE = ["About", "Frappe Support"];

	$(document).on("app_ready", function () {
		patch_avatar_menu();
	});

	// Also patch on page change in case desktop re-renders
	$(document).on("page-change", function () {
		patch_avatar_menu();
	});

	function patch_avatar_menu() {
		const desktop = frappe.pages?.desktop;
		if (!desktop || !desktop.page) return;

		const app = desktop.page?.desktop_page;
		if (!app || typeof app.setup_avatar !== "function") return;

		const original = app.setup_avatar.bind(app);
		app.setup_avatar = function () {
			original();
			// Remove unwanted items from the rendered menu
			remove_items_from_dom();
		};
	}

	function remove_items_from_dom() {
		$(".desktop-avatar")
			.closest(".frappe-menu-wrapper, .dropdown")
			.find(".dropdown-menu-item, .menu-item-title")
			.filter(function () {
				return LABELS_TO_REMOVE.includes($(this).text().trim());
			})
			.closest(".dropdown-menu-item")
			.remove();
	}

	// Patch frappe.ui.create_menu to strip unwanted items before rendering
	const _original_create_menu = frappe.ui.create_menu;
	frappe.ui.create_menu = function (opts) {
		if (opts && opts.menu_items) {
			opts.menu_items = opts.menu_items.filter(function (item) {
				return !LABELS_TO_REMOVE.includes(item.label);
			});
		}
		return _original_create_menu.call(this, opts);
	};
});
