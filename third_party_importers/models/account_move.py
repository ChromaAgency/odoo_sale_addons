from odoo import models
import logging 
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        res = super(AccountMove, self).action_post()
        for move in self:
            if move.invoice_line_ids.sale_line_ids.order_id.is_third_party_imported:
                payment_register = self.env['account.payment.register'].with_context(
                    active_model='account.move',
                    active_ids=move.ids,
                ).create({
                    'amount': move.amount_residual,
                    'payment_date': move.invoice_date,
                    'journal_id': 6,
                })
                payment_register.action_create_payments()