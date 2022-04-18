from odoo.models import Model
from odoo.api import onchange

class SaleOrder(Model):
    _inherit = 'sale.order'
    
    @onchange('order_line', 'order_line.price_unit', 'order_line.discount')
    def _onchange_orderline_prices(self):
        for rec in self.order_line:
            if rec.price_unit == rec._origin.price_unit and rec.discount == rec._origin.discount:
                continue
            self.show_update_pricelist = True
            break