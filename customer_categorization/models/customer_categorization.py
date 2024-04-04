from odoo.models import Model
from odoo.fields import Many2one, Char, Integer
from odoo.api import depends

class CustomerPointCategorization(Model):
    _name = "customer.point.categorization"
    _description = "Puntos para definición de tipo"
    _rec_name= "category_name"
    
    category_name = Many2one('customer.point.categorization.category', string="Concepto", required=True)
    score = Integer(string="Puntaje", required=True)
    weight = Integer(string="Peso", related="category_name.weight")
    weighted_score = Integer(string="weighted_score", compute="_compute_weighted_score", store=True)
    partner_id = Many2one('res.partner', string="Cliente")
    
    @depends('score', 'weight', 'category_name.weight')
    def _compute_weighted_score(self):
        for rec in self:
            rec.weighted_score = rec.score * rec.weight


class CustomerPointCategorizationCategory(Model):
    _name = "customer.point.categorization.category"
    _description = "Categorias para puntaje de cliente"
    _rec_name= "category_name"

    category_name = Char(string="Nombre", required=True)
    weight = Integer(string="Peso", required=True)