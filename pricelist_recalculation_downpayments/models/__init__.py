# -*- coding: utf-8 -*-
import time
from odoo import _
from odoo.models import TransientModel,Model
from odoo.fields import Many2one, Float, Selection, Integer
from odoo.api import model
from odoo.exceptions import UserError


class SaleOrder(Model):
    _inherit = 'sale.order'

    def recalculate_sale_order(self):
        action = self.env.ref('pricelist_recalculation_downpayments.action_view_sale_recalculator').read()[0]
        action_context = action['context']
        new_action_context = {}
        # if action_context and len(action_context.keys())>0:
            # new_action_context.update(action_context)
        new_action_context.update({ 'default_pricelist_id':self.pricelist_id.id})
        action['context'] = new_action_context
        return action
        
class SaleOrderRecalculator(TransientModel):
    """ 
    This model creates a recalculation for sale order.
    If using recalculate all, or recalculate due pricelist can be used to recalculate those lines.
    Then you can select to use a pricelist, but if you use the same pricelist, percentage_overcharge will be used to calculate the overcharge over either the sale order amount total, or the sale order amount_due.
    If you use a pricelist and only recalculate over the due amount, it will generate a calculation where the it will get the porcentual difference of the total recalculation with the original, and then calculate that with the due amount.
    Else you can use a fixed amount to recalculate only based on the percen
    """
    _name = "sale.order.recalculator"

    def _prepare_deposit_product(self):
        return {
            'name': 'Interest',
            'type': 'service',
            'invoice_policy': 'order',
            'company_id': False,
        }

    @model
    def _default_product_id(self):
        product_id = self.env['ir.config_parameter'].sudo(
        ).get_param('sale.default_pricelist_recalculation_product_id')
        return self.env['product.product'].browse(int(product_id)).exists()

    pricelist_id = Many2one('product.pricelist', string="Tarifa")
    recalculation_method = Selection([
        ('recalculate_due', 'Recalcular todo lo adeudado'),
        ('recalculate_all', 'Recalcular toda la orden'),
        ('fixed', 'Monto fijo')
    ], string='Create Invoice', default='recalculate_due', required=True)
    percentage_overcharge = Integer(string="Porcentaje de recargo")
    amount = Float(string="Monto")
    product_id = Many2one('product.product', string='Recalculation payment product', domain=[('type', '=', 'service')], default=_default_product_id)

    def _prepare_so_line(self, order, analytic_tag_ids, tax_ids, amount):
        so_values = {
            'name': _('Interes por cambio de tarifa: %s') % (time.strftime('%m %Y'),),
            'price_unit': amount,
            'product_uom_qty': 1.0,
            'order_id': order.id,
            'discount': 0.0,
            'product_uom': self.product_id.uom_id.id,
            'product_id': self.product_id.id,
            'analytic_tag_ids': analytic_tag_ids,
            'tax_id': [(6, 0, tax_ids)],
        }
        return so_values


    def _no_recalculation_found(self):
        raise UserError("No hay un calculo de monto para validar")
        return 0
    def _get_amount_to_recalculate(self,order):
        recaluation_amounts = {
            'recalculate_all':order.amount_total,
            'recalculate_due':order.amount_due,
            'fixed':self.amount
        }
        amount = recaluation_amounts.get(self.recalculation_method,False)
        if amount:
            return amount
        else:
            self._no_recalculation_found()

    def _recalculated_product_total(self,order, pricelist_id):
        new_product_total_amount = 0
        interest_product_id = self.product_id
        for line in order.order_line:
            if line.product_id != interest_product_id:
                new_product_total_amount += pricelist_id.with_context(uom=line.product_id.uom_id.id).get_product_price(line.product_id, 1, False) * line.product_uom_qty
        return new_product_total_amount
    def _get_percentage_difference(self,order):
        new_product_total = self._recalculated_product_total(order,self.pricelist_id)
        old_total = self._recalculated_product_total(order,order.pricelist_id)
        total_difference = new_product_total - old_total 
        return total_difference/old_total

    def _get_advance_details(self, order):
        amount = 0
        order_tax_rate = 0
        if order.amount_untaxed > 0 :
            order_tax_rate = (order.amount_tax/order.amount_untaxed) 
        amount_to_recalculate = self._get_amount_to_recalculate(order) / (1 + order_tax_rate)
        overcharge = self.percentage_overcharge/100
        if self.recalculation_method == 'recalculate_due' or self.recalculation_method == 'recalculate_all':
            if order.pricelist_id == self.pricelist_id:
                amount = amount_to_recalculate * overcharge
            else:
                percentage_difference = self._get_percentage_difference(order)
                amount = (amount_to_recalculate * (1 + percentage_difference)) - amount_to_recalculate
        else:
            amount = amount_to_recalculate * overcharge
        name = _("Interes de  %s%%") % (amount)
        return amount, name

    def create_interest_sale_order_lines(self):
        sale_orders = self.env['sale.order'].browse(
            self._context.get('active_ids', []))
        if not self.product_id:
            vals = self._prepare_deposit_product()
            self.product_id = self.env['product.product'].create(vals)
            self.env['ir.config_parameter'].sudo().set_param(
                'sale.default_pricelist_recalculation_product_id', self.product_id.id)
        sale_line_obj = self.env['sale.order.line']
        for order in sale_orders:
            amount, name = self._get_advance_details(order)
            if self.product_id.invoice_policy != 'order':
                raise UserError(
                    _('The product used to invoice a down payment should have an invoice policy set to "Ordered quantities". Please update your deposit product to be able to create a deposit invoice.'))
            if self.product_id.type != 'service':
                raise UserError(
                    _("The product used to invoice a down payment should be of type 'Service'. Please use another product or update this product."))
            taxes = self.product_id.taxes_id.filtered(
                lambda r: not order.company_id or r.company_id == order.company_id)
            if order.fiscal_position_id and taxes:
                tax_ids = order.fiscal_position_id.map_tax(
                    taxes, self.product_id, order.partner_shipping_id).ids
            else:
                tax_ids = taxes.ids
            context = {'lang': order.partner_id.lang}
            analytic_tag_ids = []
            for line in order.order_line:
                analytic_tag_ids = [(4, analytic_tag.id, None)
                                    for analytic_tag in line.analytic_tag_ids]
            so_line_values = self._prepare_so_line(
                order, analytic_tag_ids, tax_ids, amount)
            so_line = sale_line_obj.create(so_line_values)
            order.pricelist_id = self.pricelist_id
            del context
        return {'type': 'ir.actions.act_window_close'}
