# -*- coding: utf-8 -*-
{
    'name': 'Block Delivery By Sale',
    'summary': 'Bloquea el pedido de entrega dependiendo de la venta y la facturación',
    'version': '1.0.1',
    'author': 'Chroma',
    'website': 'https://www.chroma.agency',
    "category": "Stock",
    "depends": ['base', 'sale', 'stock','sale_stock'],
    'data': [
        'views/sale.order.xml',
        'views/stock.picking.xml',
        'views/account.payment.term.xml',
    ],
    'installable': True,
    'license': 'GPL-3',
}