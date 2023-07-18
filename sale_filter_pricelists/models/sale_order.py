from odoo.models import Model 
from odoo.fields import Many2many

class SaleOrder(Model):
    _inherit = "sale.order"

    partner_available_pricelist_ids = Many2many("product.pricelist", string="Listas de precio disponibles", related="partner_id.available_pricelist_ids")