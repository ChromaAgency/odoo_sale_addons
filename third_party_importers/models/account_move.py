from odoo import models
from odoo.exceptions import UserError
import logging 
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        res = super(AccountMove, self).action_post()
        for move in self:
            if move.invoice_line_ids.sale_line_ids.order_id.is_third_party_imported and move.move_type == 'out_invoice':
                journal_id =  self.env['ir.config_parameter'].sudo().get_param('third_party_importers.third_party_account_journal_id') or False
                if not journal_id:
                    raise UserError(_('Please configure the journal for third party importers in settings'))
                payment_register = self.env['account.payment.register'].with_context(
                    active_model='account.move',
                    active_ids=move.ids,
                ).create({
                    'amount': move.amount_residual,
                    'payment_date': move.invoice_date,
                    'journal_id': int(journal_id),
                })
                payment_register.action_create_payments()