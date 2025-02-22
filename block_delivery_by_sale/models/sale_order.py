from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_active_validate = fields.Boolean(string="Active validate", compute="_compute_active_validate")
    is_active_validate_manual = fields.Boolean(string="Active validate")
    
    @api.depends('payment_term_id','invoice_ids','invoice_ids.state', 'invoice_ids.payment_state')
    def _compute_active_validate(self):
        for rec in self:
            if rec.is_active_validate_manual:
                rec.is_active_validate = True
                return
                
            if rec.payment_term_id.cascade_payment_term_id:
                if rec.invoice_ids and rec.payment_term_id.cascade_payment_term_id:
                    downpayment_invoices = rec.invoice_ids.filtered(
                        lambda inv: inv.is_down_payment_invoice and inv.state == 'posted'
                    )
                    if downpayment_invoices:
                        rec.is_active_validate = any(state in ['paid','in_payment'] for state in downpayment_invoices.mapped('payment_state'))
            else:
                rec.is_active_validate = False


    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        if self.payment_term_id.cascade_payment_term_id: #Prevent innecesary filter
            active_invoices = self.invoice_ids.filtered(lambda inv: inv.state != 'cancel' and inv.move_type != 'out_refund' and not inv.reversed_entry_id)
            if not active_invoices:
                res['invoice_payment_term_id'] = self.payment_term_id.cascade_payment_term_id.id
                res['is_down_payment_invoice'] = True
        return res
    
    def active_validate(self):
        self.is_active_validate_manual = True

    def block_validate(self):
        self.is_active_validate_manual = False