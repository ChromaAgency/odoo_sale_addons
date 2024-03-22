# -*- coding: utf-8 -*-
{
    'name': "Permisos de vendedores extr<",

    'summary': """
    Module with advanced salesman permissions
        """,

    'description': """
    """,

    'author': "Making Argentina",
    'installable': True,
    'application':True,
    'website': "http://www.making.com.ar",

    'category': 'Sales',
    'version': '17.0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale'],

    # always loaded
    'data': [
        'security/res.groups.xml',
        'security/ir.rule.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
