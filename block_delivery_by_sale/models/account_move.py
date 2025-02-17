from odoo import models, fields, api
from odoo.tools import frozendict
import logging

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    is_down_payment_invoice = fields.Boolean(string="Is Downpayment Invoice")

    def _obtain_recent_picking_date(self, invoice, date_reference):
        order_ids = invoice.invoice_line_ids.filtered(lambda l: l.sale_line_ids).sale_line_ids.mapped('order_id')            
        if order_ids:
            valid_orders = order_ids.filtered(lambda o: o.is_active_validate and o.state in ['done', 'sale'])
            
            if valid_orders:
                latest_order = max(valid_orders, key=lambda o: o.date_order)

                if latest_order.picking_ids:
                    completed_pickings = latest_order.picking_ids.filtered(lambda p: p.date_done)
                    
                    if completed_pickings:
                        latest_picking = max(completed_pickings, key=lambda p: p.date_done)
                        return latest_picking.date_done
        return date_reference
    

    @api.depends('invoice_payment_term_id', 'invoice_date', 'currency_id', 'amount_total_in_currency_signed', 'invoice_date_due')
    def _compute_needed_terms(self):
        for invoice in self:
            date_reference = invoice.invoice_date or invoice.date or fields.Date.context_today(invoice)
            if invoice.invoice_payment_term_id.cascade_payment_term_id:
                date_reference = invoice._obtain_recent_picking_date(invoice, date_reference)
            is_draft = invoice.id != invoice._origin.id
            invoice.needed_terms = {}
            invoice.needed_terms_dirty = True
            sign = 1 if invoice.is_inbound(include_receipts=True) else -1
            if invoice.is_invoice(True) and invoice.invoice_line_ids:
                if invoice.invoice_payment_term_id:
                    if is_draft:
                        tax_amount_currency = 0.0
                        untaxed_amount_currency = 0.0
                        for line in invoice.invoice_line_ids:
                            untaxed_amount_currency += line.price_subtotal
                            for tax_result in (line.compute_all_tax or {}).values():
                                tax_amount_currency += -sign * tax_result.get('amount_currency', 0.0)
                        untaxed_amount = untaxed_amount_currency
                        tax_amount = tax_amount_currency
                    else:
                        tax_amount_currency = invoice.amount_tax * sign
                        tax_amount = invoice.amount_tax_signed
                        untaxed_amount_currency = invoice.amount_untaxed * sign
                        untaxed_amount = invoice.amount_untaxed_signed
                    invoice_payment_terms = invoice.invoice_payment_term_id._compute_terms(
                        date_ref=date_reference,
                        currency=invoice.currency_id,
                        tax_amount_currency=tax_amount_currency,
                        tax_amount=tax_amount,
                        untaxed_amount_currency=untaxed_amount_currency,
                        untaxed_amount=untaxed_amount,
                        company=invoice.company_id,
                        cash_rounding=invoice.invoice_cash_rounding_id,
                        sign=sign
                    )
                    for term in invoice_payment_terms:
                        key = frozendict({
                            'move_id': invoice.id,
                            'date_maturity': fields.Date.to_date(term.get('date')),
                            'discount_date': term.get('discount_date'),
                            'discount_percentage': term.get('discount_percentage'),
                        })
                        values = {
                            'balance': term['company_amount'],
                            'amount_currency': term['foreign_amount'],
                            'discount_amount_currency': term['discount_amount_currency'] or 0.0,
                            'discount_balance': term['discount_balance'] or 0.0,
                            'discount_date': term['discount_date'],
                            'discount_percentage': term['discount_percentage'],
                        }
                        if key not in invoice.needed_terms:
                            invoice.needed_terms[key] = values
                        else:
                            invoice.needed_terms[key]['balance'] += values['balance']
                            invoice.needed_terms[key]['amount_currency'] += values['amount_currency']
                else:
                    invoice.needed_terms[frozendict({
                        'move_id': invoice.id,
                        'date_maturity': fields.Date.to_date(invoice.invoice_date_due),
                        'discount_date': False,
                        'discount_percentage': 0
                    })] = {
                        'balance': invoice.amount_total_signed,
                        'amount_currency': invoice.amount_total_in_currency_signed,
                    }