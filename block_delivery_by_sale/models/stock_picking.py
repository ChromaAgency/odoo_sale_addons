from odoo import models, fields,api
from odoo.tools.translate import _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    is_active_validate = fields.Boolean(string="Active Validate", compute="_compute_is_active_validate", store=True)

    @api.depends('sale_id.is_active_validate', 'sale_id.payment_term_id', 'scheduled_date')
    def _compute_is_active_validate(self):
        for rec in self:
            if rec.picking_type_id.code == 'outgoing':
                if not rec.sale_id.payment_term_id.cascade_payment_term_id and rec.scheduled_date:
                    rec.is_active_validate = rec.scheduled_date.date() <= fields.Date.today()
                elif rec.sale_id.payment_term_id.cascade_payment_term_id and rec.sale_id.is_active_validate:
                    rec.is_active_validate = True
                else:
                    rec.is_active_validate = False
            else:
                rec.is_active_validate = True

    def _action_done(self):
        for picking in self:
            if picking.picking_type_id.code == 'outgoing' and not picking.is_active_validate:
                raise UserError(_("The orders cannot be validated because the delivery %s is blocked.", picking.name))
        return super(StockPicking, self)._action_done()
