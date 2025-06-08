from odoo.models import Model
from odoo.fields import Many2one, Char, Integer, Many2many
from odoo.api import depends

class CustomerPointCategorization(Model):
    _inherit = "product.pricelist"

    customer_category_id = Many2one('customer.point.categorization.type', string="Tipo de cliente")
    industry_id = Many2one('res.partner.industry', string="Canal")
    
    
    