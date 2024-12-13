# -*- coding: utf-8 -*-
{
    'name': "Permisos de vendedores extra",

    'summary': """
    Module with advanced salesman permissions
        """,

    'description': """
    """,

    'author': "Chroma",
    'installable': True,
    'application':True,
    'website': "https://chroma.agency",

    'category': 'Sales',
    'version': '18.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['sale','crm','sale_management'],

    # always loaded
    'data': [
        'security/res.groups.xml',
        'security/ir.rule.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
