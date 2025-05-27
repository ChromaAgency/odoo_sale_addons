from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website.controllers.main import QueryURL


class WebsiteSaleCatalog(WebsiteSale):

    @http.route([
        '''/shop''',
        '''/shop/page/<int:page>''',
        '''/shop/category/<model("product.public.category"):category>''',
        '''/shop/category/<model("product.public.category"):category>/page/<int:page>'''
    ], type='http', auth="public", website=True)
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        # Override the shop route to make it catalog-only (no add to cart)
        res = super(WebsiteSaleCatalog, self).shop(
            page=page, 
            category=category,
            search=search,
            ppg=ppg,
            **post
        )
        
        if isinstance(res, dict):
            # Set catalog mode flag
            res.update({
                'catalog_mode': True,
                'hide_price': True,
                'prevent_add_to_cart': True
            })
            
            # Remove price sorting options
            if 'sorting_options' in res:
                res['sorting_options'] = [
                    opt for opt in res['sorting_options'] 
                    if 'price' not in opt[0]
                ]

        return res

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
