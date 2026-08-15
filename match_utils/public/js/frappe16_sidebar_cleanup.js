// Match Systems Frappe 16 sidebar cleanup — removes the "Switch to Frappe CRM"
// promotional banner and the "about" (i) button from the bottom of the
// workspace sidebar. Frappe 16 only: no-ops on v15 and earlier, where
// neither element exists.
frappe.after_ajax(function () {
	const frappe_version = frappe.boot && frappe.boot.versions && frappe.boot.versions.frappe
		? frappe.boot.versions.frappe.version
		: null;
	const major_version = frappe_version ? parseInt(frappe_version.split(".")[0], 10) : null;

	if (major_version !== 16) return;

	// Rendered by frappe.ui.Sidebar.render_promotional_banners() as
	// <a class="promotional-banner"> inside <div class="promotional-banners">
	// (see frappe/public/js/frappe/ui/sidebar/sidebar.js get_crm_banner()).
	function remove_crm_banner() {
		$(".promotional-banners .promotional-banner").filter(function () {
			return $(this).text().trim() === __("Switch to Frappe CRM");
		}).remove();
	}

	// <button class="about-sidebar-link btn btn-ghost btn-xs"> in
	// .sidebar-bottom-actions, next to the collapse-sidebar-link button.
	// Opens the "Frappe Framework" About dialog.
	function remove_about_button() {
		$(".about-sidebar-link").remove();
	}

	function cleanup() {
		remove_crm_banner();
		remove_about_button();
	}

	$(document).on("app_ready page-change", function () {
		setTimeout(cleanup, 200);
	});

	// The sidebar (and these elements) is built dynamically well after
	// DOMContentLoaded, so observe document.body broadly rather than a
	// container that may not exist yet.
	if (window.MutationObserver) {
		const observer = new MutationObserver(cleanup);
		const start_observing = function () {
			observer.observe(document.body, { childList: true, subtree: true });
		};
		if (document.body) {
			start_observing();
		} else {
			document.addEventListener("DOMContentLoaded", start_observing);
		}
	}

	cleanup();
});
