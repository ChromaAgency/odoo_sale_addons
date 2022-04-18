# -*- coding: utf-8 -*-
{
    'name': "Monto faltante en lista de precio",

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
    'version': '0.1',

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
