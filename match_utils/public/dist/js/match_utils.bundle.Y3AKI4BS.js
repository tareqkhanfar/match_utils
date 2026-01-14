(() => {
  // ../match_utils/match_utils/public/js/keyboard_shortcuts.js
  frappe.provide("match_utils");
  match_utils.KeyboardShortcuts = class {
    constructor() {
      this.shortcuts = {};
      this.is_loading = false;
      this.load_shortcuts();
      this.init_listener();
    }
    load_shortcuts() {
      if (this.is_loading)
        return;
      this.is_loading = true;
      frappe.call({
        method: "match_utils.api.get_active_shortcuts",
        callback: (r) => {
          if (r.message) {
            this.shortcuts = r.message;
            console.log("\u2713 Keyboard shortcuts loaded:", this.shortcuts);
          }
          this.is_loading = false;
        },
        error: () => {
          this.is_loading = false;
        }
      });
    }
    init_listener() {
      const self = this;
      let pressedKeys = /* @__PURE__ */ new Set();
      $(document).on("keydown", function(e) {
        if ($(e.target).is('input, textarea, [contenteditable="true"]')) {
          return;
        }
        pressedKeys.add(e.key.toUpperCase());
        let shortcut = [];
        if (e.ctrlKey || pressedKeys.has("CONTROL"))
          shortcut.push("CTRL");
        if (e.altKey || pressedKeys.has("ALT"))
          shortcut.push("ALT");
        if (e.shiftKey || pressedKeys.has("SHIFT"))
          shortcut.push("SHIFT");
        let key = e.key.toUpperCase();
        if (key !== "CONTROL" && key !== "ALT" && key !== "SHIFT" && key !== "META") {
          shortcut.push(key);
        }
        let shortcutStr = shortcut.join("+");
        console.log("Key pressed:", shortcutStr);
        if (self.shortcuts[shortcutStr]) {
          e.preventDefault();
          e.stopPropagation();
          self.execute_shortcut(self.shortcuts[shortcutStr]);
        }
      });
      $(document).on("keyup", function(e) {
        pressedKeys.delete(e.key.toUpperCase());
      });
      $(window).on("blur", function() {
        pressedKeys.clear();
      });
    }
    execute_shortcut(config) {
      if (!config.enabled)
        return;
      console.log("Executing shortcut:", config);
      switch (config.target_type) {
        case "DocType":
          this.open_doctype(config.target_doctype);
          break;
        case "Report":
          this.open_report(config.target_report);
          break;
        case "Page":
          this.open_page(config.target_page);
          break;
      }
    }
    open_doctype(doctype) {
      frappe.set_route("List", doctype);
      frappe.show_alert({
        message: __("Opening {0}", [doctype]),
        indicator: "green"
      }, 2);
    }
    open_report(report) {
      frappe.set_route("query-report", report);
      frappe.show_alert({
        message: __("Opening Report: {0}", [report]),
        indicator: "blue"
      }, 2);
    }
    open_page(page) {
      frappe.set_route(page);
      frappe.show_alert({
        message: __("Opening Page: {0}", [page]),
        indicator: "blue"
      }, 2);
    }
  };
  $(document).ready(function() {
    frappe.after_ajax(function() {
      if (frappe.session.user !== "Guest" && !frappe.keyboard_shortcuts) {
        console.log("Initializing keyboard shortcuts...");
        frappe.keyboard_shortcuts = new match_utils.KeyboardShortcuts();
      }
    });
  });
  frappe.realtime.on("shortcuts_updated", function() {
    console.log("Shortcuts updated event received");
    if (frappe.keyboard_shortcuts) {
      frappe.keyboard_shortcuts.load_shortcuts();
      frappe.show_alert({
        message: __("Keyboard shortcuts reloaded"),
        indicator: "green"
      }, 3);
    }
  });
})();
//# sourceMappingURL=match_utils.bundle.Y3AKI4BS.js.map
