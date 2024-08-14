# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'res.carriers',
    'version': '1.3',
    'category': 'Operations/Inventory/Delivery',
    'description': """
Allows you to vinculate delivery methods to partners.
==============================================================

""",
    'depends': ["base", 'sale_stock', 'sale_management'],
    'data': [
        'security/ir.model.access.csv',
        'views/delivery_view.xml',
        'views/res.partner.xml'
        'views/stock.picking.xml'
    ],
    'demo': [],
    'installable': True,
}
