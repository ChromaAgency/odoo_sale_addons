from odoo.models import Model
from odoo.tools import (
    formatLang,)
from odoo import _

class AccountMove(Model):
    _inherit = 'account.move'

    def _build_credit_multicurrency_warning_message(self, record, updated_credit, currency_id):
        ''' Build the warning message that will be displayed in a yellow banner on top of the current record
            if the partner exceeds a credit limit (set on the company or the partner itself).
            :param record:                  The record where the warning will appear (Invoice, Sales Order...).
            :param updated_credit (float):  The partner's updated credit limit including the current record.
            :return (str):                  The warning message to be showed.
        '''
        partner_id = record.partner_id.commercial_partner_id
        if not partner_id.credit_limit or updated_credit <= partner_id.credit_limit:
            return ''
        msg = _('%s has reached its Credit Limit of : %s\nTotal amount due ',
                partner_id.name,
                formatLang(self.env, partner_id.credit_limit, currency_obj=currency_id))
        if updated_credit > partner_id.credit:
            msg += _('(including this document) ')
        msg += ': %s' % formatLang(self.env, updated_credit, currency_obj=currency_id)
        return msg
