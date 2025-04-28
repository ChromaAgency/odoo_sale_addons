from odoo.models import Model 

class ResPartner(Model):
    _inherit = 'res.partner'

    l10n_ar_include_vat = Boolean(string="Incluir impuestos")

    def _commercial_fields(self):
        return super(ResPartner, self)._commercial_fields() + ['l10n_ar_include_vat']


class SaleOrder(Model):
    _inherit = 'sale.order'

    def _l10n_ar_include_vat(self):
        return self.partner_id.l10n_ar_include_vat
