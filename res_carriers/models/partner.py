# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api    


class ResPartner(models.Model):
    _inherit = 'res.partner'

    carrier_id = fields.Many2one('delivery.carrier.express',  string="Expreso")
