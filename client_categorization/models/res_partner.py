from odoo.models import Model
from odoo.fields import Many2one, Char, Integer, Many2many
from odoo.api import depends

class ResPartners(Model):
    _inherit = "res.partner"

    customer_score = Integer(string="Score total", compute="_compute_customer_score", store=True, readonly=True)
    customer_point_ids = Many2many('customer.point.categorization', 'partner_id', string="Categorización")
    customer_point_type_id = Many2one('customer.point.categorization.type', string="Tipo de cliente")

    @depends('customer_point_ids.weighted_score')
    def _compute_customer_score(self):
        for rec in self:
            rec.customer_score = sum(rec.customer_point_ids.mapped('weighted_score'))

    @depends('customer_point_ids.weighted_score', 'customer_score')
    def _compute_customer_point_type_id(self):
        for rec in self:
            rec.customer_point_type_id = rec.customer_point_type_id.get_customer_point_categorization_type(rec.customer_score)