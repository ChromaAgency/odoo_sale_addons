from odoo import api, SUPERUSER_ID

def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    categ_model = env['customer.categorization']
    categs = categ_model.search([('name', '!=', False)])
    for categ in categs:
        categ.category_name = categ.name
