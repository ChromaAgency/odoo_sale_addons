# -*- coding: utf-8 -*-

from odoo.models import Model
from odoo.fields import Many2one, Float
from odoo.api import depends
class SaleOrder(Model):
    _inherit = "sale.order"

    
    amount_due = Float(string="Monto adeudado", compute="_compute_amount_due")

    @depends('order_line','invoice_ids')
    def _compute_amount_due(self):
        for rec in self:
            invoices = rec.invoice_ids
            invoices_due = sum(invoices.mapped('amount_residual'))
            invoices_total = sum(invoices.mapped('amount_total'))
            sale_due = rec.amount_total - (invoices_total - invoices_due)
            if sale_due:
                rec.amount_due = sale_due
            else: 
                rec.amount_due = 0