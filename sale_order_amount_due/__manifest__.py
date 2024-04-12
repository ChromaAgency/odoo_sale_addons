# -*- coding: utf-8 -*-
{
    'name': "Monto faltante en lista de precio",

    'summary': """
    Module for telling salesman how much is due in a sales order based on downpayments
        """,

    'description': """
    """,

    'author': "Making Argentina",
    'installable': True,
    'application':True,
    'website': "http://www.making.com.ar",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full lis
    'category': 'Sales',
    'version': '17.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['sale','account','sale_management'],

    # always loaded
    'data': [
        'views/sale.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
