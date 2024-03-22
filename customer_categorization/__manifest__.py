# -*- coding: utf-8 -*-
{
    'name': "Categorización de clientes",

    'summary': """
                Categorize clients based on certain parameters.
            """,

    'description': """
        This module creates models to categorize your clients and give them according importance to certain parameters.
        
    
    """,

    'author': "Making Argentina",
    'installable': True,
    'application':True,
    'website': "http://www.making.com.ar",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full lis
    'category': 'Sales',
    'version': '17.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','contacts','sale'],

    # always loaded
    'data': [
        'views/res.partner.xml',
        'views/customer.categorization.xml',
        'views/product.pricelist.xml',
        'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
