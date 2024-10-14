# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models
from odoo.api import depends

_logger = logging.getLogger(__name__)


class res_Carrier(models.Model):
    _name = 'delivery.carrier.express'
    _description = "Expresos"
    _order = 'sequence, id'

    name = fields.Char('Expreso', required=True, translate=True)
    company_name = fields.Char('Razón Social')
    street = fields.Char('Dirección')
    city = fields.Char('Ciudad')
    zip = fields.Char('Código Postal')
    state_id = fields.Many2one('res.country.state', 'Provincia')
    phone = fields.Char('Teléfono')
    mobile = fields.Char('Móvil')
    email =fields.Char('Correo electrónico')
    active = fields.Boolean(default=True)
    sequence = fields.Integer(help="Determine the display order", default=10)
    complete_address = fields.Char(string="Dirección Completa", compute="_compute_complete_address", store=True)
    country_id = fields.Many2one('res.country', string="País")

    @depends('street', 'city', 'state_id', 'zip', 'country_id')
    def _compute_complete_address(self):
        for carrier in self:
            carrier.complete_address = ', '.join([carrier.street, carrier.city, carrier.state_id.name if carrier.state_id else '', carrier.zip, carrier.country_id.name if carrier.country_id else ''])

    country_ids = fields.Many2many('res.country', 'res_carrier_country_rel', 'carrier_id', 'country_id', 'Countries') # is this a nonesense?
    state_ids = fields.Many2many('res.country.state', 'res_carrier_state_rel', 'carrier_id', 'state_id', 'States')
