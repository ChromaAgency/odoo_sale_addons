from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_pickup = fields.Boolean(string="Pickup", default=False)