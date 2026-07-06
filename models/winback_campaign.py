# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class WinbackCampaign(models.Model):
    _name = 'winback.campaign'
    _description = 'Win-back Campaign'

    partner_id = fields.Many2one(
        'res.partner', 
        string='Partner', 
        required=True, 
        ondelete='cascade'
    )
    stage = fields.Selection([
        ('none', 'No Email Sent'),
        ('email_1_sent', 'Email 1 Sent'),
        ('email_2_sent', 'Email 2 Sent'),
        ('email_3_sent', 'Email 3 Sent'),
        ('replied', 'Replied'),
        ('reactivated', 'Reactivated'),
        ('cold', 'Cold'),
        ('opt_out', 'Opt Out')
    ], string='Stage', default='none', required=True)

    status = fields.Selection([
        ('not_enrolled', 'Not Enrolled'),
        ('draft', 'Draft (Review Pending)'),
        ('active', 'Running'),
        ('completed', 'Replied / Completed'),
        ('suppressed', 'Suppressed (Skipped)'),
        ('failed', 'Failed'),
        ('reactivated', 'Reactivated (Success)'),
        ('cold', 'Cold (No Response)'),
        ('opt_out', 'Opt Out (Unsubscribed)')
    ], string='Status', default='not_enrolled', required=True)

    suppression_reason = fields.Char(string='Suppression Reason')

    email_1_sent_date = fields.Datetime(string='Email 1 Sent Date')
    email_2_sent_date = fields.Datetime(string='Email 2 Sent Date')
    email_3_sent_date = fields.Datetime(string='Email 3 Sent Date')

    _sql_constraints = [
        ('partner_uniq', 'unique(partner_id)', 'A campaign record already exists for this partner!')
    ]

    @api.model
    def process_winback_campaigns(self):
        """
        Daily cron method to process win-back campaign stage transitions.
        """
        now = fields.Datetime.now()
        company = self.env.company
        interval_days = company.lisa_wb_interval_days or 7

        # Fetch active campaigns (stage NOT IN replied, reactivated, cold, opt_out and status = active)
        campaigns = self.search([
            ('stage', 'not in', ['replied', 'reactivated', 'cold', 'opt_out']),
            ('status', '=', 'active')
        ])

        for campaign in campaigns:
            # 1. Guard check: if partner has a confirmed sale.order with date_order after email_1_sent_date
            if campaign.email_1_sent_date:
                confirmed_orders = self.env['sale.order'].search([
                    ('partner_id', '=', campaign.partner_id.id),
                    ('state', 'in', ['sale', 'done']),
                    ('date_order', '>', campaign.email_1_sent_date)
                ], limit=1)
                if confirmed_orders:
                    campaign.write({'stage': 'reactivated'})
                    continue

            # 2. Stage transitions based on datetime comparisons
            if campaign.stage == 'email_1_sent' and campaign.email_1_sent_date:
                dt_sent = fields.Datetime.to_datetime(campaign.email_1_sent_date)
                if (now - dt_sent).days >= interval_days:
                    campaign.write({
                        'stage': 'email_2_sent',
                        'email_2_sent_date': now
                    })
            elif campaign.stage == 'email_2_sent' and campaign.email_2_sent_date:
                dt_sent = fields.Datetime.to_datetime(campaign.email_2_sent_date)
                if (now - dt_sent).days >= interval_days:
                    campaign.write({
                        'stage': 'email_3_sent',
                        'email_3_sent_date': now
                    })
            elif campaign.stage == 'email_3_sent' and campaign.email_3_sent_date:
                dt_sent = fields.Datetime.to_datetime(campaign.email_3_sent_date)
                if (now - dt_sent).days >= interval_days:
                    campaign.write({
                        'stage': 'cold'
                    })
                    if campaign.partner_id.user_id:
                        self.env['mail.activity'].create({
                            'res_model_id': self.env['ir.model']._get('res.partner').id,
                            'res_id': campaign.partner_id.id,
                            'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                            'summary': 'Win-Back Campaign Finished - Cold Customer',
                            'note': 'Customer completed all 3 drip re-engagement email outreach cycles without reacting or replying.',
                            'user_id': campaign.partner_id.user_id.id,
                            'date_deadline': fields.Date.context_today(self)
                        })

    def action_run_winback_agent(self):
        """Runs the win-back campaign python agent script at the backend."""
        import subprocess
        import os

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

