from odoo.models import Model
from odoo.fields import Many2one

class CrmLead(Model):
    _inherit = "crm.lead"

    commercial_partner_id = Many2one("res.partner", string="Entidad del cliente", related="partner_id.commercial_partner_id", store=True)
    last_order_id = Many2one("sale.order", string="Última orden", compute="_compute_last_order_id", store=True)

    def _compute_last_order_id(self):
        for rec in self:
            orders = rec.order_ids.filtered(lambda r: r.state in ["sale", "done"])
            rec.last_order_id = orders and orders[-1] or False