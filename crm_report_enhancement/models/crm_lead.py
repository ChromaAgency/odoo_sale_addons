from odoo.models import Model
from odoo.fields import Many2one, Integer
from odoo.api import depends

class CrmLead(Model):
    _inherit = "crm.lead"

    commercial_partner_id = Many2one("res.partner", string="Entidad del cliente", related="partner_id.commercial_partner_id", store=True)
    confirmed_sale_order_count = Integer(string="Cantidad de pedidos confirmados", compute="_compute_confirmed_sale_order_count", store=True)

    @depends('order_ids', 'order_ids.state')
    def _compute_confirmed_sale_order_count(self):
        for rec in self:
            rec.confirmed_sale_order_count = len(rec.order_ids.filtered(lambda r: r.state in ["sale",'done']))