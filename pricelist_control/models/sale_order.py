from odoo.models import Model
from odoo.exceptions import UserError
from odoo.fields import Boolean
from odoo.api import onchange, depends
import logging
_logger = logging.getLogger(__name__)
class SaleOrderLine(Model):
    _inherit = 'sale.order.line'
        
    not_aligned_with_pricelist = Boolean(string="No coincide con lista de precios", compute="_compute_not_aligned_with_pricelist")
    
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
        if self.needs_manager_approval and not self.env.ref('sales_team.group_sale_manager').id in self.env.user.groups_id.ids:
            raise UserError('Los precios no son los mismos que la lista de precios, por favor revisarlos o pida la aprobación de un gerente.')
        return super().action_confirm()
