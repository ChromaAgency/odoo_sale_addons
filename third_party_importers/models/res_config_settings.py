from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    third_party_account_journal_id = fields.Many2one(
        'account.journal', 
        string='Account Journal', 
        help='Select the journal for this configuration.',
        domain="[('type', 'in', ['bank', 'cash', 'credit'])]",
        config_parameter='third_party_importers.third_party_account_journal_id',
    )

    full_warehouse = fields.Many2one('stock.warehouse', string='Almacen de Full de Meli', config_parameter='stock.warehouse.full.meli')
    
    min_amount_free_delivery = fields.Float(
        string='Minimum Amount for Free Delivery',
        help='Orders above this amount will not be charged for delivery',
        config_parameter='third_party_importers.min_amount_free_delivery'
    )