# -*- coding: utf-8 -*-
{
    'name': "Control de listas de precios",

    'summary': """
                Avoid salesman from changing pricelists.
            """,

    'description': """
        This modules adds a button for sale managers to confirm the order in case of custom prices.
        
    
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
    'depends': ['sale'],

    # always loaded
    'data': [
        'views/sale.order.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
