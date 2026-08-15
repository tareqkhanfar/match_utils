// Match Systems Frappe 16 sidebar cleanup — removes the "Switch to Frappe CRM"
// promotional banner from the sidebar. Frappe 16 only: no-ops on v15 and
// earlier, where frappe.ui.sidebar's promotional-banners feature doesn't
// exist.
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

	$(document).on("app_ready page-change", function () {
		setTimeout(remove_crm_banner, 200);
	});

	// The sidebar (and its .promotional-banners container) is built
	// dynamically well after DOMContentLoaded, so observe document.body
	// broadly rather than a container that may not exist yet.
	if (window.MutationObserver) {
		const observer = new MutationObserver(remove_crm_banner);
		const start_observing = function () {
			observer.observe(document.body, { childList: true, subtree: true });
		};
		if (document.body) {
			start_observing();
		} else {
			document.addEventListener("DOMContentLoaded", start_observing);
		}
	}

	remove_crm_banner();
});
