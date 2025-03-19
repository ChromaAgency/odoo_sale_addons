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
    'website': "https://chroma.agency",

    'category': 'Sales',
    'version': '18.0.1.1',

    # any module necessary for this one to work correctly
    'depends': ['crm','sale_crm'],

    # always loaded
    'data': [
        'views/crm.lead.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
