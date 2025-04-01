from odoo.models import Model
from odoo.fields import Many2one, Char, Integer
from odoo.api import depends
import logging 
_logger = logging.getLogger(__name__)
class CustomerPointCategorizationType(Model):
    _name = "customer.point.categorization.type"
    _description = "Tipo de cliente"
    _order = "min_points desc"

    name = Char(string="Nombre", required=True)
    min_points = Integer(string="Puntos minimos", required=True)

    def _get_type_with_highest_min_points(self):
        points = self.mapped('min_points')
        points.append(0)
        highest_min_point = max(points)
        highest_min_points_rec = self.filtered(lambda r: r.min_points == highest_min_point)
        return highest_min_points_rec[:1]


    def get_customer_point_categorization_type(self, points):
        possible_candidates = self.search([('min_points','<=',points)])
        final_candidate = possible_candidates._get_type_with_highest_min_points()
        return final_candidate