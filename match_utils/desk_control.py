# Copyright (c) 2026, match systems and contributors
# For license information, please see license.txt

"""Per-user desk visibility ("التحكم بالديسك" tab on User).

Hides modules / workspaces from what the desk *shows* (desktop icons, sidebar,
workspace list, app switcher) by filtering bootinfo. Permissions are untouched:
a hidden workspace or doctype still opens by URL if the user's roles allow it.
"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.utils import slug

HIDDEN_MODULE_DOCTYPE = "Desk Hidden Module"
HIDDEN_WORKSPACE_DOCTYPE = "Desk Hidden Workspace"
ALWAYS_VISIBLE_SIDEBARS = {"my workspaces"}


def setup_custom_fields():
	create_custom_fields({"User": _user_fields()}, update=True)


def _user_fields():
	standard = [df.fieldname for df in frappe.get_meta("User").fields if not df.get("is_custom_field")]
	# Place the tab just before "Connections" so it sits with the other settings tabs.
	insert_after = standard[-1]
	if "connections_tab" in standard and standard.index("connections_tab") > 0:
		insert_after = standard[standard.index("connections_tab") - 1]

	return [
		{
			"fieldname": "desk_control_tab",
			"fieldtype": "Tab Break",
			"label": "التحكم بالديسك",
			"insert_after": insert_after,
			"permlevel": 1,
		},
		{
			"fieldname": "desk_control_html",
			"fieldtype": "HTML",
			"label": "التحكم بالديسك",
			"insert_after": "desk_control_tab",
			"permlevel": 1,
		},
		{
			"fieldname": "desk_hidden_modules",
			"fieldtype": "Table",
			"label": "الموديولات المخفية",
			"options": HIDDEN_MODULE_DOCTYPE,
			"insert_after": "desk_control_html",
			"permlevel": 1,
			"hidden": 1,
		},
		{
			"fieldname": "desk_hidden_workspaces",
			"fieldtype": "Table",
			"label": "مساحات العمل المخفية",
			"options": HIDDEN_WORKSPACE_DOCTYPE,
			"insert_after": "desk_hidden_modules",
			"permlevel": 1,
			"hidden": 1,
		},
	]


def clear_user_desk_cache(doc, method=None):
	frappe.cache.hdel("bootinfo", doc.name)
	frappe.cache.hdel("desktop_icons", doc.name)


@frappe.whitelist()
def get_desk_tree():
	"""Apps → modules → public workspaces, for the checkbox picker on the User form."""
	frappe.only_for("System Manager")

	workspaces_by_module = {}
	for ws in frappe.get_all(
		"Workspace",
		filters={"public": 1, "for_user": ("in", ("", None))},
		fields=["name", "title", "module"],
		order_by="sequence_id asc, name asc",
	):
		workspaces_by_module.setdefault(ws.module or "", []).append(
			{"name": ws.name, "title": ws.title or ws.name}
		)

	apps = {}
	for module in frappe.get_all("Module Def", fields=["name", "app_name"], order_by="name asc"):
		app = apps.setdefault(module.app_name, {"app": module.app_name, "title": _app_title(module.app_name), "modules": []})
		app["modules"].append({"name": module.name, "workspaces": workspaces_by_module.pop(module.name, [])})

	orphans = [w for ws in workspaces_by_module.values() for w in ws]
	if orphans:
		apps["__other__"] = {"app": "__other__", "title": "أخرى", "modules": [{"name": "", "workspaces": orphans}]}

	installed = frappe.get_installed_apps()
	return sorted(
		apps.values(),
		key=lambda a: installed.index(a["app"]) if a["app"] in installed else len(installed),
	)


def _app_title(app_name):
	try:
		return frappe.get_hooks("app_title", app_name=app_name)[0]
	except Exception:
		return app_name


def boot_session(bootinfo):
	user = frappe.session.user
	if not user or user == "Guest":
		return
	if not frappe.db.table_exists(HIDDEN_MODULE_DOCTYPE) or not frappe.db.table_exists(HIDDEN_WORKSPACE_DOCTYPE):
		return

	hidden_modules = set(
		frappe.get_all(
			HIDDEN_MODULE_DOCTYPE,
			filters={"parenttype": "User", "parent": user, "parentfield": "desk_hidden_modules"},
			pluck="module",
		)
	)
	hidden_workspaces = set(
		frappe.get_all(
			HIDDEN_WORKSPACE_DOCTYPE,
			filters={"parenttype": "User", "parent": user, "parentfield": "desk_hidden_workspaces"},
			pluck="workspace",
		)
	)
	if not hidden_modules and not hidden_workspaces:
		return

	workspace_module = {w.name: w.module for w in frappe.get_all("Workspace", fields=["name", "module"])}
	filter_bootinfo(bootinfo, hidden_modules, hidden_workspaces, workspace_module)


def filter_bootinfo(bootinfo, hidden_modules, hidden_workspaces, workspace_module):
	"""Drop hidden modules/workspaces from every bootinfo key the v15/v16 desk renders from."""
	hidden_ws = set(hidden_workspaces) | {w for w, m in workspace_module.items() if m and m in hidden_modules}

	def page_visible(page):
		return page.get("name") not in hidden_ws and page.get("module") not in hidden_modules

	# v15 sidebar
	if isinstance(bootinfo.get("allowed_workspaces"), list):
		bootinfo["allowed_workspaces"] = [p for p in bootinfo["allowed_workspaces"] if page_visible(p)]

	# v16 workspace list
	workspaces = bootinfo.get("workspaces")
	if isinstance(workspaces, dict) and isinstance(workspaces.get("pages"), list):
		workspaces["pages"] = [p for p in workspaces["pages"] if page_visible(p)]

	# v16 sidebars, keyed by lowercased sidebar title (usually the workspace name)
	removed_sidebars = set()
	sidebars = bootinfo.get("workspace_sidebar_item")
	if isinstance(sidebars, dict):
		for key in list(sidebars):
			if key in ALWAYS_VISIBLE_SIDEBARS:
				continue
			sidebar = sidebars[key]
			if sidebar.get("label") in hidden_ws or sidebar.get("module") in hidden_modules:
				removed_sidebars.add(key)
				del sidebars[key]
				continue
			sidebar["items"] = [
				item
				for item in sidebar.get("items") or []
				if not (item.get("link_type") == "Workspace" and item.get("link_to") in hidden_ws)
			]

	# v16 desktop icons
	icons = bootinfo.get("desktop_icons")
	if isinstance(icons, list):
		bootinfo["desktop_icons"] = _filter_icons(icons, hidden_ws, hidden_modules, removed_sidebars, workspace_module)

	# v16 app switcher / module map
	if isinstance(bootinfo.get("app_data"), list):
		bootinfo["app_data"] = _filter_app_data(bootinfo["app_data"], hidden_ws)

	module_wise = bootinfo.get("module_wise_workspaces")
	if isinstance(module_wise, dict):
		for module in list(module_wise):
			if module in hidden_modules:
				del module_wise[module]
			else:
				module_wise[module] = [w for w in module_wise[module] if w not in hidden_ws]

	return bootinfo


def _filter_icons(icons, hidden_ws, hidden_modules, removed_sidebars, workspace_module):
	def link_hidden(icon):
		for target in (icon.get("link_to"), icon.get("label")):
			if not target:
				continue
			if target in hidden_ws or target.lower() in removed_sidebars:
				return True
			if workspace_module.get(target) in hidden_modules:
				return True
		return False

	kept = [i for i in icons if not (i.get("icon_type") == "Link" and link_hidden(i))]

	# Folders/apps whose every child got hidden would show up empty; drop them too.
	children_before = {}
	for icon in icons:
		if icon.get("parent_icon"):
			children_before.setdefault(icon["parent_icon"], 0)
			children_before[icon["parent_icon"]] += 1

	while True:
		labels = {i.get("label") for i in kept}
		children_now = {}
		for icon in kept:
			if icon.get("parent_icon"):
				children_now[icon["parent_icon"]] = children_now.get(icon["parent_icon"], 0) + 1

		next_kept = [
			i
			for i in kept
			if not (i.get("parent_icon") and i["parent_icon"] not in labels)
			and not (children_before.get(i.get("label")) and not children_now.get(i.get("label")))
		]
		if len(next_kept) == len(kept):
			return next_kept
		kept = next_kept


def _filter_app_data(app_data, hidden_ws):
	result = []
	for app in app_data:
		original = list(app.get("workspaces") or [])
		visible = [w for w in original if w not in hidden_ws]
		if len(visible) == len(original):
			result.append(app)
			continue

		if not visible:
			continue

		route = app.get("app_route") or ""
		route_from_workspace = route in {f"/desk/{slug(original[0])}", f"/app/{slug(original[0])}"}

		app = dict(app, workspaces=visible)
		if route_from_workspace:
			app["app_route"] = route.rsplit("/", 1)[0] + "/" + slug(visible[0])
		result.append(app)
	return result
