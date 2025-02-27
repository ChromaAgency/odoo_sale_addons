from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class AccountPaymentTerm(models.Model):
    _inherit = 'account.payment.term'

    cascade_payment_term_id = fields.Many2one('account.payment.term', string='Cascade payment term')
