{
    'name': 'Pricelist with IVA',
    'version': '18.0.1.0.0',
    'category': 'Sales/Sales',
    'summary': 'Adds taxes (IVA) to the Product Pricelist Report',
    'description': """
This module modifies the standard product pricelist report (report.product.report_pricelist)
to display the price including applicable taxes.
    """,
    'author': 'Your Name', # Replace with your name or company
    'website': 'Your Website', # Optional: Replace with your website
    'depends': [
        'product',
        'account', # Dependency needed for tax calculation
    ],
    'data': [
        'report/report_pricelist_templates.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3', # Or your preferred license
}