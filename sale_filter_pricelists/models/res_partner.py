from odoo.models import Model
from odoo.fields import Many2many 

class ResPartner(Model):
    _inherit = "res.partner"

    available_pricelist_ids = Many2many("product.pricelist", string="Listas de precio disponibles")