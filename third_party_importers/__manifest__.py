# -*- coding: utf-8 -*-
{
    'name': "Third Party Importers",

    'summary': """
        Import sales from third party platforms like Mercadolibre, Tienda nube and woocommerce
    """,

    'description': """
        Import sales from third party platforms like Mercadolibre, Tienda nube and woocommerce
    """,
    'author': "Chroma",
    'website': "https://chroma.agency/",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Account',
    'version': '1.0',
    'installable': True,
    # any module necessary for this one to work correctly
    'depends': ['sale', 'l10n_ar', 'account_payment_conditions'],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/ir.actions.xml',
        'data/ir.menu.xml',
        'wizards/base_third_party_sale_importer.xml',
        'wizards/meli_sale_importer.xml',
        'wizards/tiendanube_sale_importer.xml',
        'wizards/woocommerce_sale_importer.xml',
        'views/res.config.settings_views.xml',
    ]
}
