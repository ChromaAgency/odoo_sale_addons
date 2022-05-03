from odoo.models import Model
from odoo.exceptions import UserError
from odoo.fields import Boolean
from odoo.api import onchange, depends
import logging
_logger = logging.getLogger(__name__)
class SaleOrderLine(Model):
    _inherit = 'sale.order.line'
        
    not_aligned_with_pricelist = Boolean(string="No coincide con lista de precios", compute="_compute_not_aligned_with_pricelist", store=True)
    
    @depends('price_unit','discount')
    def _compute_not_aligned_with_pricelist(self):
        for rec in self:
            rec.not_aligned_with_pricelist = rec._product_pricelist_price_differs_from_price_unit()

    def _product_pricelist_price_differs_from_price_unit(self):
        pricelist_price_unit = self.product_id._get_tax_included_unit_price(
            self.company_id,
            self.order_id.currency_id,
            self.order_id.date_order,
            'sale',
            fiscal_position=self.order_id.fiscal_position_id,
            product_price_unit=self._get_display_price(self.product_id),
            product_currency=self.order_id.currency_id
        )
        if self.order_id.pricelist_id.discount_policy == 'without_discount':
            product_context = dict(self.env.context, partner_id=self.order_id.partner_id.id, date=self.order_id.date_order, uom=self.product_uom.id)
            price, rule_id = self.order_id.pricelist_id.with_context(product_context).get_product_price_rule(self.product_id, self.product_uom_qty or 1.0, self.order_id.partner_id)
            new_list_price, currency = self.with_context(product_context)._get_real_price_currency(self.product_id, rule_id, self.product_uom_qty, self.product_uom, self.order_id.pricelist_id.id)
            if self.order_id.pricelist_id.currency_id != currency:
                # we need new_list_price in the same currency as price, which is in the SO's pricelist's currency
                new_list_price = currency._convert(
                    new_list_price, self.order_id.pricelist_id.currency_id,
                    self.order_id.company_id or self.env.company, self.order_id.date_order or fields.Date.today())
            discount = ((new_list_price - price) / (new_list_price or 1)) * 100
            if self.price_unit == pricelist_price_unit and discount == self.discount:
                return False
        if self.order_id.pricelist_id.discount_policy == 'with_discount':
            if self.price_unit == pricelist_price_unit and self.discount == 0:
                return False
        return True

class SaleOrder(Model):
    _inherit = 'sale.order'
    
    needs_manager_approval = Boolean(string="Necesita aprobación de gerente", compute="_compute_needs_manager_approval")

    @depends('show_update_pricelist', 'order_line.not_aligned_with_pricelist')
    def _compute_needs_manager_approval(self):
        for rec in self:
            rec.needs_manager_approval = any(rec.order_line.mapped('not_aligned_with_pricelist')) or rec.show_update_pricelist
            
    def action_confirm(self):
        if self.needs_manager_approval and not self.env.ref('sales_team.group_sale_manager').id in self.env.user.groups_id.ids and self.env.user.id != self.env.ref('base.user_root').id:
            raise UserError('Los precios no son los mismos que la lista de precios, por favor revisarlos o pida la aprobación de un gerente.')
        return super().action_confirm()
