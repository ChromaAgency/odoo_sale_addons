# -*- coding: utf-8 -*-
{
    'name': "Recalculo de Lista de precios",

    'summary': """
    Module for recalculating on a new pricelist on the sales module
        """,

    'description': """
    """,

    'author': "Making Argentina",
    'installable': True,
    'website': "http://www.making.com.ar",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full lis
    'category': 'Sales',
    'version': '17.0.1',

    # any module necessary for this one to work correctly
    'depends': ['product','sale','sale_order_amount_due'],

    # always loaded
    'data': [
        'views/views.xml'
    
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
