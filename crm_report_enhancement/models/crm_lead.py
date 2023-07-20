from odoo.models import Model
from odoo.fields import Many2one, Integer

class CrmLead(Model):
    _inherit = "crm.lead"

    commercial_partner_id = Many2one("res.partner", string="Entidad del cliente", related="partner_id.commercial_partner_id", store=True)
    customer_order_count = Integer(string="Cantidad de pedidos", related="commercial_partner_id.sale_order_count", store=True)