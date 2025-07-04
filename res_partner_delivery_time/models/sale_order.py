from odoo.models import Model
from odoo.api import onchange

import logging

_logger = logging.getLogger(__name__)
class SaleOrder(Model):
    _inherit = "sale.order"

    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        if 'partner_id' in defaults:
            partner_id = defaults.get("partner_id") 
            if partner_id:
                defaults.update({'commitment_date': self.env['res.partner'].browse([partner_id]).get_next_delivery_date()})
        return defaults

    @onchange('partner_id', 'partner_shipping_id')
    def _onchange_partner_id_delivery_date(self):
        if self.partner_id:
            self.commitment_date = self.partner_id.get_next_delivery_date()
        return {}