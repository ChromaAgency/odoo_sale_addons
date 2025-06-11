from odoo import models, fields, api, _

class Website(models.Model):
    _inherit = 'website'

    @staticmethod
    def _get_product_sort_mapping():
        return [
            ('website_sequence asc', _("Featured")),
            ('create_date desc', _("Newest Arrivals")), 
            ('name asc', _("Name (A-Z)")),
        ]
