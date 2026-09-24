// "التحكم بالديسك" tab on User: show/hide modules and workspaces on the desk.
// Visibility only — rows are stored in desk_hidden_modules / desk_hidden_workspaces
// and applied server-side in match_utils.desk_control.boot_session.
frappe.ui.form.on("User", {
	refresh(frm) {
		const field = frm.fields_dict.desk_control_html;
		if (!field || frm.is_new() || !frappe.user.has_role("System Manager")) return;

		const load = frm.__desk_tree
			? Promise.resolve(frm.__desk_tree)
			: frappe.xcall("match_utils.desk_control.get_desk_tree").then((tree) => (frm.__desk_tree = tree));

		load.then((tree) => render_desk_control(frm, field.$wrapper, tree));
	},
});

function render_desk_control(frm, $wrapper, tree) {
	const esc = frappe.utils.escape_html;
	const hidden_modules = new Set((frm.doc.desk_hidden_modules || []).map((r) => r.module));
	const hidden_ws = new Set((frm.doc.desk_hidden_workspaces || []).map((r) => r.workspace));
	const read_only = !frm.perm[1] || !frm.perm[1].write;

	const ws_html = (ws, module_hidden) => `
		<label class="mdc-ws" data-search="${esc((ws.title + " " + __(ws.title)).toLowerCase())}">
			<input type="checkbox" data-ws="${esc(ws.name)}"
				${!hidden_ws.has(ws.name) && !module_hidden ? "checked" : ""}
				${module_hidden || read_only ? "disabled" : ""}>
			<span>${esc(__(ws.title))}</span>
		</label>`;

	const module_html = (module) => {
		const module_hidden = module.name && hidden_modules.has(module.name);
		const search = [module.name, __(module.name), ...module.workspaces.map((w) => w.title + " " + __(w.title))]
			.join(" ")
			.toLowerCase();
		return `
			<div class="mdc-module" data-search="${esc(search)}">
				${
					module.name
						? `<label class="mdc-module-head">
							<input type="checkbox" data-module="${esc(module.name)}"
								${module_hidden ? "" : "checked"} ${read_only ? "disabled" : ""}>
							<b>${esc(__(module.name))}</b>
							${module.workspaces.length ? "" : `<span class="text-muted small">(${__("بدون مساحات عمل")})</span>`}
						</label>`
						: ""
				}
				<div class="mdc-ws-list">${module.workspaces.map((w) => ws_html(w, module_hidden)).join("")}</div>
			</div>`;
	};

	$wrapper.html(`
		<style>
			.mdc-intro { color: var(--text-muted); margin-bottom: var(--margin-md); }
			.mdc-toolbar { display: flex; gap: var(--margin-sm); margin-bottom: var(--margin-md); flex-wrap: wrap; }
			.mdc-toolbar input { max-width: 320px; }
			.mdc-app { border: 1px solid var(--border-color); border-radius: var(--border-radius-md); margin-bottom: var(--margin-md); }
			.mdc-app > summary { padding: var(--padding-sm) var(--padding-md); cursor: pointer; font-weight: 600; background: var(--subtle-fg); border-radius: var(--border-radius-md); }
			.mdc-app-body { padding: var(--padding-sm) var(--padding-md); display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: var(--margin-sm) var(--margin-lg); }
			.mdc-module-head, .mdc-ws { display: flex; align-items: center; gap: 6px; margin: 0; cursor: pointer; font-weight: normal; }
			.mdc-ws-list { margin-inline-start: 22px; }
			.mdc-ws input:disabled + span { color: var(--text-light); text-decoration: line-through; }
		</style>
		<p class="mdc-intro">${__(
			"إظهار أو إخفاء الموديولات ومساحات العمل من الديسك لهذا المستخدم فقط. لا يغيّر الصلاحيات. تظهر التغييرات عند المستخدم بعد الحفظ وتحديث الصفحة."
		)}</p>
		<div class="mdc-toolbar">
			<input type="search" class="form-control input-sm mdc-search" placeholder="${__("بحث...")}">
			${read_only ? "" : `<button class="btn btn-default btn-xs mdc-show-all">${__("إظهار الكل")}</button>`}
		</div>
		${tree
			.map(
				(app) => `
			<details class="mdc-app" open>
				<summary>${esc(__(app.title))}</summary>
				<div class="mdc-app-body">${app.modules.map(module_html).join("")}</div>
			</details>`
			)
			.join("")}
	`);

	const sync = () => {
		frm.clear_table("desk_hidden_modules");
		hidden_modules.forEach((module) => frm.add_child("desk_hidden_modules", { module }));
		frm.clear_table("desk_hidden_workspaces");
		hidden_ws.forEach((workspace) => frm.add_child("desk_hidden_workspaces", { workspace }));
		frm.dirty();
	};

	$wrapper.find("input[data-module]").on("change", function () {
		const module = $(this).attr("data-module");
		this.checked ? hidden_modules.delete(module) : hidden_modules.add(module);
		$(this)
			.closest(".mdc-module")
			.find("input[data-ws]")
			.each(function () {
				$(this).prop("disabled", !!hidden_modules.has(module));
				$(this).prop("checked", !hidden_modules.has(module) && !hidden_ws.has($(this).attr("data-ws")));
			});
		sync();
	});

	$wrapper.find("input[data-ws]").on("change", function () {
		const ws = $(this).attr("data-ws");
		this.checked ? hidden_ws.delete(ws) : hidden_ws.add(ws);
		sync();
	});

	$wrapper.find(".mdc-show-all").on("click", () => {
		hidden_modules.clear();
		hidden_ws.clear();
		sync();
		render_desk_control(frm, $wrapper, tree);
	});

	$wrapper.find(".mdc-search").on("input", function () {
		const q = this.value.trim().toLowerCase();
		$wrapper.find(".mdc-module").each(function () {
			$(this).toggle(!q || $(this).attr("data-search").includes(q));
		});
		$wrapper.find(".mdc-app").each(function () {
			const shown = $(this)
				.find(".mdc-module")
				.filter(function () {
					return this.style.display !== "none";
				}).length;
			$(this).toggle(shown > 0);
		});
	});
}
