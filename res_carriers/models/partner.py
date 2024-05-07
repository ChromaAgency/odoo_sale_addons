# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api    


class ResPartner(models.Model):
    _inherit = 'res.partner'

    carrier_id = fields.Many2one('delivery.carrier.express',  string="Expreso")


    @api.depends(lambda self: self._display_address_depends())
    def _compute_contact_address(self):
        for partner in self:
            if not partner.carrier_id or not partner.carrier_id.contact_address_complete:
                super(ResPartner, partner)._compute_contact_address()
            else:
                partner.contact_address = partner.carrier_id.contact_address_complete
