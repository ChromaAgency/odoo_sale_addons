from odoo import _
from odoo.models import Model 
from odoo.fields import Many2one, Monetary, Date
from odoo.api import depends_context

class ResPartner(Model):
    _inherit = 'res.partner'

    credit_limit_currency_id = Many2one('res.currency', string="Moneda del limite de credito", default=lambda s: s.env.company.currency_id)
    credit_with_confirmed_orders = Monetary(currency_field='credit_limit_currency_id')

    def _get_confirmed_order_lines(self):
        domain = [
                    ('order_id.partner_id.commercial_partner_id', '=', self.commercial_partner_id.id),
                    # buscamos las que estan a facturar o las no ya que nos interesa
                    # la cantidad total y no solo la facturada. Esta busqueda ayuda
                    # a que no busquemos en todo lo que ya fue facturado al dope
                    ('invoice_status', 'in', ['to invoice', 'no']),
                    ('order_id.state', 'in', ['sale', 'done']),
                ]
        return self.env['sale.order.line'].search(domain)
    def _get_to_invoice_amount(self):
            order_lines = self._get_confirmed_order_lines()
            to_invoice_amount = 0.0
            credit_limit_currency_id = self.commercial_partner_id.credit_limit_currency_id

            # We sum from all the sale orders that are aproved, the sale order
            # lines that are not yet invoiced
            for line in order_lines:
                # not_invoiced is different from native qty_to_invoice because
                # the last one only consider to_invoice lines the ones
                # that has been delivered or are ready to invoice regarding
                # the invoicing policy. Not_invoiced consider all
                not_invoiced = line.product_uom_qty - line.qty_invoiced
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                taxes = line.tax_id.compute_all(
                    price, line.order_id.currency_id,
                    not_invoiced,
                    product=line.product_id, partner=line.order_id.partner_id)
                total = taxes['total_included']
                if line.order_id.currency_id != credit_limit_currency_id:
                    total = line.order_id.currency_id._convert(
                        taxes['total_included'], credit_limit_currency_id, line.company_id, Date.today())
                to_invoice_amount += total
            return to_invoice_amount
    
    def _get_draft_invoice_lines(self):            
        domain = [
                    ('move_id.partner_id.commercial_partner_id', '=', self.commercial_partner_id.id),
                    ('move_id.move_type', 'in', ['out_invoice', 'out_refund']),
                    ('move_id.state', '=', 'draft'),
                    '|',('sale_line_ids', '=', False),
                    ('sale_line_ids.order_id.invoice_status', '=', 'invoiced')]
        return self.env['account.move.line'].search(domain)
    
    def _get_draft_invoice_lines_amount(self):
        draft_invoice_lines = self._get_draft_invoice_lines()
        draft_invoice_lines_amount = 0.0
        credit_limit_currency_id = self.commercial_partner_id.credit_limit_currency_id
        for line in draft_invoice_lines:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_ids.compute_all(
                price, line.move_id.currency_id,
                line.quantity,
                product=line.product_id, partner=line.move_id.partner_id)
            total = taxes['total_included']
            if line.move_id.currency_id != credit_limit_currency_id:
                total = line.move_id.currency_id._convert(
                    taxes['total_included'], credit_limit_currency_id, line.company_id, Date.today())
            draft_invoice_lines_amount += total
        return draft_invoice_lines_amount
    
    @depends_context('company')
    def _compute_credit_with_confirmed_orders(self):
        # Sets 0 when use_partner_credit_limit is not set avoiding unnecessary overloads
        credit_with_confirmed_orders = 0
        if self.use_partner_credit_limit:
            to_invoice_amount = self._get_to_invoice_amount()
            draft_invoice_lines_amount = self._get_draft_invoice_lines_amount()
            credit_with_confirmed_orders = to_invoice_amount + draft_invoice_lines_amount + self.credit
        self.credit_with_confirmed_orders = credit_with_confirmed_orders
