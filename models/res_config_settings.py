# -*- coding: utf-8 -*-
from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    lisa_wb_inactivity_threshold_days = fields.Integer(
        related='company_id.lisa_wb_inactivity_threshold_days',
        readonly=False,
        string="Inactivity Threshold (Days)",
        help="Number of days of customer purchase inactivity before starting the win-back campaign."
    )
    lisa_wb_interval_days = fields.Integer(
        related='company_id.lisa_wb_interval_days',
        readonly=False,
        string="Win-back Interval (Days)",
        help="Number of days between emails in the win-back campaign chain."
    )
    lisa_wb_offer_email2 = fields.Char(
        related='company_id.lisa_wb_offer_email2',
        readonly=False,
        string="Win-back Offer (Email 2)",
        help="Discount code or special incentive text to insert into Email 2."
    )
    lisa_wb_max_emails = fields.Integer(
        related='company_id.lisa_wb_max_emails',
        readonly=False,
        string="Max Win-back Emails",
        help="Maximum number of emails in the win-back campaign chain."
    )
    lisa_wb_segment_by_category = fields.Boolean(
        related='company_id.lisa_wb_segment_by_category',
        readonly=False,
        string="Segment by Category",
        help="If enabled, win-back campaigns only target customers based on previously purchased categories."
    )
    lisa_wb_auto_reply = fields.Boolean(
        related='company_id.lisa_wb_auto_reply',
        readonly=False,
        string="Auto Reply",
        help="If enabled, campaign emails are sent automatically. Otherwise, drafts are saved to the customer's record for review."
    )
    lisa_wb_recipient_override = fields.Char(
        related='company_id.lisa_wb_recipient_override',
        readonly=False,
        string="Recipient Override Email",
        help="If set, all campaign outreach emails are redirected to this address instead of the actual customer's email (useful for auditing/testing)."
    )

    def action_run_winback_agent(self):
        """Runs the win-back campaign python agent script at the backend."""
        import subprocess
        import os
        from odoo import _
        from odoo.exceptions import UserError

        python_exe = r"d:\Lisa\Win-Back Agent\.venv\Scripts\python.exe"
        script_path = r"d:\Lisa\Win-Back Agent\main.py"
        cwd = r"d:\Lisa\Win-Back Agent"

        if not os.path.exists(python_exe) or not os.path.exists(script_path):
            raise UserError(_("Python agent executable or script path not found. Please verify directories."))

        try:
            # Run as a detached background subprocess so it doesn't block Odoo
            # On Windows, we use DETACHED_PROCESS creation flag so it runs independently
            creation_flags = 0x00000008  # DETACHED_PROCESS
            subprocess.Popen(
                [python_exe, script_path],
                cwd=cwd,
                creationflags=creation_flags,
                close_fds=True
            )
        except Exception as e:
            raise UserError(_("Failed to start the agent: %s") % str(e))

        # Show a friendly success notification to the user
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Win-Back Agent Started'),
                'message': _('The campaign agent has been successfully launched at the backend in the background.'),
                'sticky': False,
                'type': 'success',
            }
        }


