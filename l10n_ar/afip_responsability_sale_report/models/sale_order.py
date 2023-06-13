from odoo.models import Model 


class SaleOrder(Model):

    def _l10n_ar_include_vat(self):
        return self.partner_id.l10n_ar_afip_responsibility_type_id.name in ['Consumidor Final', 'IVA Sujeto Exento', 'Responsable Monotributo']
