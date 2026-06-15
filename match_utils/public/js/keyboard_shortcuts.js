frappe.provide('match_utils');

match_utils.KeyboardShortcuts = class {
    constructor() {
        this.shortcuts = {};
        this.is_loading = false;
        this.load_shortcuts();
        this.init_listener();
    }

    load_shortcuts() {
        if (this.is_loading) return;
        this.is_loading = true;

        frappe.call({
            method: 'match_utils.api.get_active_shortcuts',
            callback: (r) => {
                this.is_loading = false;
                if (!r.message) return;

                this.shortcuts = r.message;
                this._register_with_frappe_keys();
            },
            error: () => {
                this.is_loading = false;
            }
        });
    }

    /**
     * Register shortcuts into frappe.ui.keys so they appear in the
     * native Shift+/ keyboard shortcut help dialog.
     */
    _register_with_frappe_keys() {
        // Remove previously registered match_utils shortcuts to avoid duplicates
        if (this._registered_shortcuts) {
            this._registered_shortcuts.forEach(key => {
                frappe.ui.keys.off(key, 'match_utils');
            });
        }
        this._registered_shortcuts = [];

        Object.entries(this.shortcuts).forEach(([shortcut_str, config]) => {
            if (!config.enabled) return;

            // Convert our format (CTRL+SHIFT+S) to frappe format (ctrl+shift+s)
            const frappe_key = shortcut_str.toLowerCase().replace(/\+/g, '+');

            frappe.ui.keys.add_shortcut({
                shortcut: frappe_key,
                action: () => this.execute_shortcut(config),
                description: this._get_description(config),
                ignore_inputs: false
            });

            this._registered_shortcuts.push(frappe_key);
        });
    }

    _get_description(config) {
        if (config.description) return config.description;
        if (config.target_type === 'DocType') {
            const mode = config.open_mode || 'List';
            return __('Open {0} ({1})', [config.target_doctype, mode]);
        }
        if (config.target_type === 'Report') {
            return __('Open report: {0}', [config.target_report]);
        }
        if (config.target_type === 'Page') {
            return __('Open page: {0}', [config.target_page]);
        }
        return '';
    }

    init_listener() {
        let pressedKeys = new Set();

        $(document).on('keydown.match_utils_shortcuts', (e) => {
            // Skip if user is typing in an input
            if ($(e.target).is('input, textarea, [contenteditable="true"]')) return;

            pressedKeys.add(e.key.toUpperCase());

            let parts = [];
            if (e.ctrlKey)  parts.push('CTRL');
            if (e.altKey)   parts.push('ALT');
            if (e.shiftKey) parts.push('SHIFT');
            if (e.metaKey)  parts.push('META');

            const key = e.key.toUpperCase();
            if (!['CONTROL', 'ALT', 'SHIFT', 'META'].includes(key)) {
                parts.push(key);
            }

            const shortcutStr = parts.join('+');
            const config = this.shortcuts[shortcutStr];

            if (config && config.enabled) {
                e.preventDefault();
                e.stopPropagation();
                this.execute_shortcut(config);
            }
        });

        $(document).on('keyup.match_utils_shortcuts', (e) => {
            pressedKeys.delete(e.key.toUpperCase());
        });

        $(window).on('blur.match_utils_shortcuts', () => {
            pressedKeys.clear();
        });
    }

    execute_shortcut(config) {
        switch (config.target_type) {
            case 'DocType':
                this._open_doctype(config.target_doctype, config.open_mode);
                break;
            case 'Report':
                this._open_report(config.target_report);
                break;
            case 'Page':
                this._open_page(config.target_page);
                break;
        }
    }

    _open_doctype(doctype, open_mode) {
        if (!doctype) return;

        if (open_mode === 'New Form') {
            frappe.new_doc(doctype);
            frappe.show_alert({ message: __('New {0}', [doctype]), indicator: 'green' }, 2);
        } else {
            // Default: List
            frappe.set_route('List', doctype);
            frappe.show_alert({ message: __('Opening {0}', [doctype]), indicator: 'green' }, 2);
        }
    }

    _open_report(report) {
        if (!report) return;
        frappe.set_route('query-report', report);
        frappe.show_alert({ message: __('Opening {0}', [report]), indicator: 'blue' }, 2);
    }

    _open_page(page) {
        if (!page) return;
        frappe.set_route(page);
        frappe.show_alert({ message: __('Opening {0}', [page]), indicator: 'blue' }, 2);
    }
};

// Initialize once Frappe desk is ready
$(document).ready(function () {
    frappe.after_ajax(function () {
        if (frappe.session.user !== 'Guest' && !frappe.keyboard_shortcuts) {
            frappe.keyboard_shortcuts = new match_utils.KeyboardShortcuts();
        }
    });
});

// Real-time reload when an admin saves/deletes a Shortcut Mapper record
frappe.realtime.on('shortcuts_updated', function () {
    if (frappe.keyboard_shortcuts) {
        frappe.keyboard_shortcuts.load_shortcuts();
        frappe.show_alert({ message: __('Keyboard shortcuts reloaded'), indicator: 'green' }, 3);
    }
});
