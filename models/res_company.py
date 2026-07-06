# -*- coding: utf-8 -*-
from odoo import fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'

    lisa_wb_inactivity_threshold_days = fields.Integer(
        string='Inactivity Threshold (Days)',
        default=60,
        help="Number of days of customer purchase inactivity before starting the win-back campaign."
    )
    lisa_wb_interval_days = fields.Integer(
        string='Win-back Interval (Days)',
        default=7,
        help="Number of days between emails in the win-back campaign chain."
    )
    lisa_wb_offer_email2 = fields.Char(
        string='Win-back Offer (Email 2)',
        default='WELCOME10',
        help="Discount code or special incentive text to insert into Email 2."
    )
    lisa_wb_max_emails = fields.Integer(
        string='Max Win-back Emails',
        default=3,
        help="Maximum number of emails in the win-back campaign chain."
    )
    lisa_wb_segment_by_category = fields.Boolean(
        string='Segment by Category',
        default=False,
        help="If enabled, win-back campaigns only target customers based on previously purchased categories."
    )
    lisa_wb_auto_reply = fields.Boolean(
        string='Auto Reply',
        default=False,
        help="If enabled, campaign emails are sent automatically. Otherwise, drafts are saved to the customer's record for review."
    )
    lisa_wb_recipient_override = fields.Char(
        string='Recipient Override Email',
        default='jatoimasab@gmail.com',
        help="If set, all campaign outreach emails are redirected to this address instead of the actual customer's email (useful for auditing/testing)."
    )

