from odoo.models import Model
from odoo.fields import Many2one, Char, Integer, One2many
from odoo.api import depends
import logging 
_logger = logging.getLogger(__name__)
class ResPartners(Model):
    _inherit = "res.partner"

    customer_score = Integer(string="Score total", compute="_compute_customer_score", store=True, readonly=True)
    customer_point_ids = One2many('customer.point.categorization', 'partner_id', string="Categorización")
    customer_point_type_id = Many2one('customer.point.categorization.type', string="Tipo de cliente", _compute="_compute_customer_score", store=True, readonly=True)

    @depends('customer_point_ids.weighted_score', 'customer_point_ids.weight')
    def _compute_customer_score(self):
        for rec in self:
            customer_score = sum(rec.customer_point_ids.mapped('weighted_score'))
            rec.customer_point_type_id = rec.customer_point_type_id.get_customer_point_categorization_type(customer_score)
            rec.customer_score = customer_score

