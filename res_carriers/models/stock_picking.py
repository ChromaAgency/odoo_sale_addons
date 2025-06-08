from odoo.models import Model
from odoo.fields import Many2one
from odoo.api import model  
class StockPicking(Model):
    _inherit = 'stock.picking'

    carrier_express_id = Many2one('delivery.carrier.express', string='Expreso')

    @model
    def create(self, vals):
        res = super(StockPicking, self).create(vals)
        if not res.carrier_express_id:
            res.carrier_express_id = res.partner_id.carrier_id or res.partner_id.commercial_partner_id.carrier_id
        return res