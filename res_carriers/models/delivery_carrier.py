# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class res_Carrier(models.Model):
    _name = 'delivery.carrier.express'
    _description = "Expresos"
    _order = 'sequence, id'

    name = fields.Char('Expreso', required=True, translate=True)
    company_name = fields.Char('Razón Social')
    address = fields.Char('Dirección')
    city = fields.Char('Ciudad')
    zip = fields.Char('Código Postal')
    state_id = fields.Many2one('res.country.state', 'Provincia')
    telephone = fields.Char('Teléfono')
    cellphone = fields.Char('Móvil')
    email =fields.Char('Correo electrónico')
    active = fields.Boolean(default=True)
    sequence = fields.Integer(help="Determine the display order", default=10)

    country_ids = fields.Many2many('res.country', 'res_carrier_country_rel', 'carrier_id', 'country_id', 'Countries')
    state_ids = fields.Many2many('res.country.state', 'res_carrier_state_rel', 'carrier_id', 'state_id', 'States')
    contact_address_complete = fields.Char(compute='_compute_contact_address', string='Dirección completa')
