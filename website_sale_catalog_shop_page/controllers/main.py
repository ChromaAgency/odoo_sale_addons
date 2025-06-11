from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website.controllers.main import QueryURL
import logging
_logger = logging.getLogger(__name__)

class WebsiteSaleCatalog(WebsiteSale):

    def _get_product_sort_mapping (self):
        super_mapping = super()._get_product_sort_mapping()

        _logger.info(super_mapping)
        # # Remove price sorting options
        # if 'sorting_options' in values:
        #     new_vals['sorting_options'] = [
        #         opt for opt in values['sorting_options'] 
        #         if 'list_price' not in opt[0] and 'list_price' not in opt[0]
        #     ]
        return super_mapping

    def _get_additional_shop_values(self, values):
        new_vals = {
            'catalog_mode': True,
            'hide_price': True,
            'prevent_add_to_cart': True
        }
        
        # Replace 'shop' with 'catalog' in pager URLs
        if 'pager' in values:
            new_vals['pager'] = {
                'page': values['pager']['page'],
                'page_count': values['pager']['page_count'],
                'page_previous': {'url': values['pager']['page_previous']['url'].replace('/shop', '/catalog')},
                'page_next': {'url': values['pager']['page_next']['url'].replace('/shop', '/catalog')},
                'pages': [{
                    'num': page['num'],
                    'url': page['url'].replace('/shop', '/catalog')
                } for page in values['pager']['pages']]
            }
        return new_vals

    def _website_show_quick_add(self):
        return False

    @http.route([
        '/catalog',
        '/catalog/page/<int:page>',
        '/catalog/category/<model("product.public.category"):category>',
        '/catalog/category/<model("product.public.category"):category>/page/<int:page>',

    ], type='http', auth="public", website=True)
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        # Override the shop route to make it catalog-only (no add to cart)
        return super(WebsiteSaleCatalog, self).shop(
            page=page, 
            category=category,
            search=search,
            ppg=ppg,
            **post
        )

    def _prepare_product_values(self, product, category, search, **kwargs):
        # Override to modify product display values
        values = super(WebsiteSaleCatalog, self)._prepare_product_values(
            product, category, search, **kwargs
        )
        
        values.update({
            'catalog_mode': True,
            'hide_price': True,
            'prevent_add_to_cart': True
        })
        
        return values
