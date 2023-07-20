# -*- coding: utf-8 -*-
{
'name': "Mejoras de reporte de CRM",

    'summary': """
    Module to enhance CRM Report
        """,

    'description': """
    """,

    'author': "Chroma",
    'installable': True,
    'application':True,
    'website': "http://www.making.com.ar",

    'category': 'Sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['crm'],

    # always loaded
    'data': [
        'views/crm.lead.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
