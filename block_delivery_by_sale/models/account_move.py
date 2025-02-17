from odoo import models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    is_down_payment_invoice = fields.Boolean(string="Is Downpayment Invoice")