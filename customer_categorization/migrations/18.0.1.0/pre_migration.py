from odoo import api, SUPERUSER_ID

def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    categ_model = env['customer.point.categorization']
    categ_model2 = env['customer.point.categorization.type']
    categs = categ_model.search([('name', '!=', False)])
    for categ in categs:
        categ.category_name = categ.name
    model2_categs = categ_model2.search([('name', '!=', False)])
    for categ in model2_categs:
        categ.category_name = categ.name
