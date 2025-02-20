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