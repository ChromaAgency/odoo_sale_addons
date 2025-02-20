from odoo import _
from odoo import models, fields
import logging
_logger = logging.getLogger(__name__)
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_third_party_imported = fields.Boolean(string='Is Third Party Imported', default=False)

    def action_cancel(self):
        res = super(SaleOrder, self).action_cancel()
        for order in self:
            if order.is_third_party_imported:
                order._create_credit_note()
        return res

    def _create_credit_note(self):
        invoice = self.invoice_ids.filtered(lambda x: x.state == 'posted' and x.payment_state != 'reversed' and x.move_type == 'out_invoice')
        if invoice:
            pays = invoice.matched_payment_ids
            pays.action_draft()
            pays.unlink()
            reversal_wizard = self.env['account.move.reversal'].with_context(active_ids=invoice.ids)
            wizard = reversal_wizard.create({
                'reason': _('Cancelation of the sale order %s') % self.name,
                'date': fields.Date.today(),
                'move_ids': invoice.ids,
                'journal_id': invoice.journal_id.id,
            })
            credit_note = wizard.refund_moves()
            wizard.new_move_ids.action_post()