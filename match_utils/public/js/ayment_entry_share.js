// Add Share button to Payment Entry
frappe.ui.form.on('Payment Entry', {
    refresh: function(frm) {
        if (!frm.is_new()) {
            // Add custom button in the primary button group
            frm.add_custom_button(__('Share as Link'), function() {
                share_payment_entry_pdf(frm);
            }).addClass('btn-primary');
        }
    }
});

function share_payment_entry_pdf(frm) {
    frappe.call({
        method: 'match_utils.api.generate_share_link',
        args: {
            doctype: frm.doctype,
            docname: frm.docname
        },
        freeze: true,
        freeze_message: __('Generating share link...'),
        callback: function(r) {
            if (r.message) {
                let share_url = window.location.origin + r.message.route;
                
                let d = new frappe.ui.Dialog({
                    title: __('Share Payment Entry as PDF'),
                    fields: [
                        {
                            fieldtype: 'HTML',
                            fieldname: 'share_info',
                            options: `
                                <div style="padding: 15px;">
                                    <div class="form-group">
                                        <label style="font-weight: bold; margin-bottom: 10px; display: block;">
                                            <i class="fa fa-link"></i> ${__('Public PDF Link')}
                                        </label>
                                        <div class="input-group" style="margin-bottom: 10px;">
                                            <input type="text" 
                                                   class="form-control" 
                                                   id="share-url-input" 
                                                   value="${share_url}" 
                                                   readonly 
                                                   style="font-size: 13px; font-family: monospace;">
                                            <div class="input-group-append">
                                                <button class="btn btn-default" id="copy-share-url" type="button">
                                                    <i class="fa fa-copy"></i> ${__('Copy')}
                                                </button>
                                            </div>
                                        </div>
                                        <small class="form-text text-muted">
                                            <i class="fa fa-clock-o"></i> ${__('This link will expire in {0} days', [r.message.expires_in || 30])}
                                        </small>
                                    </div>
                                    
                                    <div class="alert alert-info" style="margin-top: 15px;">
                                        <i class="fa fa-info-circle"></i> 
                                        ${__('Anyone with this link can view and download the PDF without login')}
                                    </div>
                                    
                                    <div style="margin-top: 15px;">
                                        <strong>${__('Document')}:</strong> ${frm.docname}<br>
                                        <strong>${__('Amount')}:</strong> ${format_currency(frm.doc.paid_amount, frm.doc.paid_to_account_currency)}
                                    </div>
                                </div>
                            `
                        }
                    ],
                    size: 'large',
                    primary_action_label: __('Open PDF in New Tab'),
                    primary_action: function() {
                        window.open(share_url, '_blank');
                    },
                    secondary_action_label: __('Close')
                });
                
                d.show();
                
                // Copy button functionality
                d.$wrapper.find('#copy-share-url').on('click', function() {
                    let input = document.getElementById('share-url-input');
                    input.select();
                    input.setSelectionRange(0, 99999); // For mobile devices
                    
                    // Try modern clipboard API first
                    if (navigator.clipboard) {
                        navigator.clipboard.writeText(share_url).then(function() {
                            frappe.show_alert({
                                message: __('Link copied to clipboard!'),
                                indicator: 'green'
                            }, 3);
                        });
                    } else {
                        // Fallback for older browsers
                        document.execCommand('copy');
                        frappe.show_alert({
                            message: __('Link copied to clipboard!'),
                            indicator: 'green'
                        }, 3);
                    }
                });
                
                // Auto-select on click
                d.$wrapper.find('#share-url-input').on('click', function() {
                    this.select();
                });
            }
        },
        error: function(r) {
            frappe.msgprint({
                title: __('Error'),
                message: __('Failed to generate share link. Please try again.'),
                indicator: 'red'
            });
        }
    });
}