from odoo import models, fields,api
from odoo.tools.translate import _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    is_active_validate = fields.Boolean(string="Active Validate", compute="_compute_is_active_validate")

    def _compute_is_active_validate(self):
        for rec in self:
            if rec.picking_type_id.code == 'outgoing':
                if rec.sale_id.is_active_validate:
                    rec.is_active_validate = True
                elif not rec.sale_id.payment_term_id.cascade_payment_term_id and rec.scheduled_date:
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
                raise UserError(_("Las ordenes no pueden validarse ya que la orden %s esta bloqueada.", picking.name))
            if picking.picking_type_id.code == 'outgoing' and picking.sale_id.invoice_ids:
                picking._recompute_due_date(picking.sale_id.invoice_ids.filtered(lambda inv: inv.payment_state not in ['paid','in_payment']))
        return super(StockPicking, self)._action_done()
    
    def _recompute_due_date(self, invoices):
        for invoice in invoices:
            invoice.sudo()._compute_needed_terms()
        

