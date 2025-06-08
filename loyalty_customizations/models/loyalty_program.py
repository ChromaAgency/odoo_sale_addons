from odoo import models, fields, api


class LoyaltyProgram(models.Model):
    _inherit = "loyalty.program"

    partner_ids = fields.Many2many('res.partner', string="Clientes")
    partner_domain = fields.Char(default="[]")
