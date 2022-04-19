from odoo.models import Model
from odoo.fields import Many2one, Char, Integer
from odoo.api import depends

class CustomerPointCategorization(Model):
    _name = "customer.point.categorization"
    
    name = Many2one('customer.point.categorization.category', string="Concepto", required=True)
    score = Integer(string="Puntaje", required=True)
    weight = Integer(string="Peso", related="name.weight")
    weighted_score = Integer(string="weighted_score", compute="_compute_weighted_score", store=True)
    partner_id = Many2one('res.partner', string="Cliente")
    
    @depends('score', 'weight', 'name.weight')
    def _compute_weighted_score(self):
        for rec in self:
            rec.weighted_score = rec.score * rec.weight


class CustomerPointCategorizationCategory(Model):
    _name = "customer.point.categorization.category"

    name = Char(string="Nombre", required=True)
    weight = Integer(string="Peso", required=True)