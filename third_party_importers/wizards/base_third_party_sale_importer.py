import base64
from odoo.models import TransientModel
from odoo.fields import Binary, Char, Selection, Command
from odoo.exceptions import UserError
import pandas as pd
from io import BytesIO
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)

def status_contains(status_to_check, status_list):
    status_filter = filter(lambda status_done: status_done in status_to_check , status_list)
    return any(status_filter)

def filter_status_done_recs(recs, status_done_list, status_field):
    for rec in recs:
        _logger.info(f"Filtering status done rec {rec} {status_contains(rec[status_field], status_done_list)}")
    _logger.info(f"Filtering status done list {status_done_list}")
    return filter(lambda r: status_contains(r[status_field], status_done_list), recs)

class BaseThirdPartySaleImporter(TransientModel):
    _name = 'base.third.party.sale.importer'
    _description = 'Base Third Party Sale Importer'

    file = Binary(string='File', required=True)
    filename = Char(string='Filename', required=True)
    separator = Selection([(',', ','), (';', ';')],string='Separator', default=';', required=True)
    encoding = Selection([('utf-8', 'UTF-8'), ('latin1', 'Latin1')], string='Encoding', default='latin1', required=True)

    @property
    def header_skip(self):
        return 0
    
    @property
    def order_name_field(self):
        raise NotImplementedError("You must implement property order_name_field")
    
    @property
    def product_uom_qty_field(self):
        raise NotImplementedError("You must implement property product_uom_qty_field")
    
    @property
    def price_unit_field(self):
        raise NotImplementedError("You must implement property price_unit_field")

    @property
    def ref_field(self):
        return False
    
    @property
    def username_field(self):
        return False

    @property
    def date_order_field(self):
        raise NotImplementedError("You must implement property date_order_field")

    @property
    def date_strptime_format(self):
        return "%d/%m/%Y"    
    
    @property
    def customer_name_field(self):
        raise NotImplementedError("You must implement property customer_name_field")

    @property
    def product_code_field(self):
        raise NotImplementedError("You must implement property product_code_field")
    
    @property
    def name_prefix(self):
        raise NotImplementedError("You must implement property product_code_field")

    @property
    def status_done(self):
        raise NotImplementedError("You must implement property status_done")
    
    @property
    def status_cancel(self):
        raise NotImplementedError("You must implement property status_cancel")
    
    @property
    def status_field(self):
        raise NotImplementedError("You must implement property status_field")
    
    @property
    def is_tax_included(self):
        return True

    @property
    def payment_condition_field(self):
        raise NotImplementedError("You must implement property payment_condition_field")
    
    @property
    def payment_condition_odoo_field(self):
        raise NotImplementedError("You must implement property payment_condition_odoo_field")
    
    @property
    def payment_method_field(self):
        raise NotImplementedError("You must implement property payment_method_field")

    @property
    def payment_method_odoo_field(self):
        raise NotImplementedError("You must implement property payment_method_odoo_field")
    
    @property
    def customer_vat_field(self):
        raise NotImplementedError("You must implement property customer_vat_field")

    @property
    def customer_email_field(self):
        raise NotImplementedError("You must implement property customer_email_field")
    
    @property
    def delivery_type_field(self):
        raise NotImplementedError("You must implement property delivery_type_field")
    
    @property
    def afip_responsability_type_field(self):
        raise NotImplementedError("You must implement property afip_responsability_type_field")
    
    @property
    def city_field(self):
        raise NotImplementedError("You must implement property city_field")
    
    @property
    def state_field(self):
        raise NotImplementedError("You must implement property state")
    
    @property
    def zip_field(self):
        raise NotImplementedError("You must implement property zip")
    
    @property
    def address_field(self):
        raise NotImplementedError("You must implement property address_field")
    
    @property
    def number_field(self):
        raise NotImplementedError("You must implement property number_field")
    
    @property
    def floor_field(self):
        raise NotImplementedError("You must implement property floor_field")
    
    @property
    def market_name(self):
        raise NotImplementedError("You must implement property market_name")
    @property
    def shipping_cost(self):
        raise NotImplementedError("You must implement property shipping_cost")
    
    @property
    def discount(self):
        raise NotImplementedError("You must implement property discount")
    
    def _preprocess_df(self, df):
        df = df.fillna("")
        return df
    
    def _read_csv(self):
        file = BytesIO(base64.b64decode(self.file))
        df = pd.read_csv(file, sep=self.separator, encoding=self.encoding, skiprows=self.header_skip, dtype={self.order_name_field: str,  self.customer_vat_field: str})
        df = self._preprocess_df(df)
        return df.to_dict(orient="records")
    
    def _read_excel(self):
        file = BytesIO(base64.b64decode(self.file))
        df = pd.read_excel(file , skiprows=self.header_skip, dtype={self.order_name_field: str, self.customer_vat_field: str})
        df = self._preprocess_df(df)
        return df.to_dict(orient="records")
    
    def _read_file(self):
        if self.filename.endswith('.csv'):
            return self._read_csv()
        if self.filename.endswith('.xlsx'):
            return self._read_excel()
        raise UserError("File format not supported")

    def _prepare_sale_order_create_values(self, recs):
        orders_to_create = {}
        for rec in recs:
            order = orders_to_create.get(rec[self.order_name_field])
            items = order and order['order_line'] or []
            partner = order and order['partner_id'] or None
            orders_to_create[rec[self.order_name_field]] = self._prepare_sale_order(rec, items, partner)
        return list(orders_to_create.values()) 

    def import_file(self):
        recs = self._read_file()
        values_to_create = self._prepare_sale_order_create_values(list(filter_status_done_recs(recs, self.status_done, self.status_field)))
        existing_orders = self.env['sale.order'].search([('name', 'in', [order['name'] for order in values_to_create])])
        if existing_orders:
            values_to_create = list(filter(lambda order: order['name'] not in [existing_order.name for existing_order in existing_orders], values_to_create))
            for exorder in existing_orders:
                if exorder.state not in ['draft', 'sent']:
                    continue
                try:
                    data = next(filter(lambda order: order['name'] == exorder.name, values_to_create))
                    exorder.write(data)
                except StopIteration:
                    pass

                
        values_to_cancel = list(filter_status_done_recs(recs, self.status_cancel, self.status_field))
        canceled_values_names = [ f'{self.name_prefix} {order[self.order_name_field]}'  for order in values_to_cancel ]
        canceled_orders = self.env['sale.order'].search([('name', 'in', canceled_values_names)])
        if canceled_orders:
            canceled_orders.with_context(disable_cancel_warning=True).action_cancel()
        orders = self.env['sale.order'].create(values_to_create)

        # orders.action_send_to_approval()
        return orders

    def _get_afip_responsability_type(self, row):
        if self.afip_responsability_type_field:
            responsability_type = self.env['l10n_ar.afip.responsibility.type'].sudo().search([('name', 'like',  row[self.afip_responsability_type_field] )], limit=1).id
            if responsability_type:
                return responsability_type
        return self.env['l10n_ar.afip.responsibility.type'].sudo().search([('name', 'like',  "Consumidor Final" )], limit=1).id
    
    def _get_identification_type_id(self, row):
        if isinstance(row[self.customer_vat_field], str) and len(str(row[self.customer_vat_field])) > 9:
            return self.env['l10n_latam.identification.type'].sudo().search([('name', 'like',  "CUIT" )], limit=1).id
        return self.env['l10n_latam.identification.type'].sudo().search([('name', 'like',  "DNI" )], limit=1).id
    
    def _get_customer_search_domain(self, row):
        return [('name', '=', row[self.customer_name_field]), ('vat', '=', str(row[self.customer_vat_field]))]
    
    def _prepare_customer_values(self, row, import_vat=True):
        state_id = self._search_state(str(row[self.state_field]))
        address = self._prepare_address(row)
        customer_values = {
                'name': row[self.customer_name_field], 
                'vat': row[self.customer_vat_field] if isinstance(row[self.customer_vat_field], str) and row[self.customer_vat_field] and import_vat else False,
                'street':address,
                'city': row[self.city_field],
                'state_id': state_id,
                'zip': row[self.zip_field],
                'country_id': self.env.ref('base.ar').id,
                'l10n_ar_afip_responsibility_type_id': self._get_afip_responsability_type(row),
                'l10n_latam_identification_type_id': self._get_identification_type_id(row),
                }
        if self.customer_email_field:
            customer_values['email'] = row[self.customer_email_field]
        return customer_values
    
    def _prepare_address(self, row):
        address = str(row[self.address_field])
        if self.number_field:
            floor = row[self.floor_field] if row[self.floor_field] else ""
            return f"{address} {row[self.number_field]} Piso {floor}"
        if '/' in address:
            return address.split('/')[0].strip()
        return address
    
    def _search_state(self, state):
        if len(state) > 1:
            if state == 'Gran Buenos Aires':
                state = 'Buenos Aires'
            state_id = self.env['res.country.state'].search([('name', '=', state), ('country_id', '=', self.env.ref('base.ar').id)]).id
            if not state_id:
                state_id = self.env['res.country.state'].search([('name', 'like', state), ('country_id', '=', self.env.ref('base.ar').id)]).id
            return state_id
        state_id = self.env['res.country.state'].search([('code', '=', state), ('country_id', '=', self.env.ref('base.ar').id)]).id
        return state_id
    
    def search_or_create_customer(self, row):
        customer = self.env['res.partner'].search(self._get_customer_search_domain(row), limit=1)
        if not customer:
            try:
                customer = self.env['res.partner'].create(self._prepare_customer_values(row))
            except Exception as e:
                customer = self.env['res.partner'].create(self._prepare_customer_values(row, import_vat=False))
        else:
            customer.write(self._prepare_customer_values(row))
        return customer.id

    def _get_product_domain(self, row):
        return [('default_code', 'ilike', row[self.product_code_field])]
    
    def search_product(self, row):
        product = self.env['product.product'].search(self._get_product_domain(row), limit=1)
        if not product:
            raise UserError(f"Product not found { row[self.product_code_field]}\n{row}" )
        return product

    def _get_product_name(self, product):
        return product.display_name
    
    def _get_product_price_unit(self, row):
        return row[self.price_unit_field] / 1.21 if self.is_tax_included else row[self.price_unit_field]
    
    def _prepare_sale_order_items(self, row):
        product = self.search_product(row)
        sale_order_items = {
            "product_id": product.id,
            "product_uom_qty": row[self.product_uom_qty_field],
            # TODO We should dynamically get the tax value from the product
            "price_unit": self._get_product_price_unit(row),
            "name": self._get_product_name(product),
        }
        return sale_order_items
    
    def _get_date_order(self, row):
        return datetime.strptime(str(row[self.date_order_field]), self.date_strptime_format).strftime("%Y-%m-%d %H:%M:%S")
    
    def _add_shipping_cost(self, row):
        shipping_product = self.env['product.template'].search([('default_code', 'ilike', 'Delivery')])[0]
        return {
            "name": "Envío",
            "product_id": shipping_product.id,
            "price_unit": row[self.shipping_cost] / 1.21 if self.is_tax_included else row[self.shipping_cost]
        }
    def _add_discount(self, row):
        discount_product = self.env['product.template'].search([('default_code', '=', 'DiscountLine')])
        return {
            "name": "Descuento",
            "product_id": discount_product.id,
            "price_unit": (row[self.discount] / 1.21 if self.is_tax_included else row[self.discount]) * -1
        }
    
    def _prepare_sale_order(self, row, items: list, partner):
        partner_id = self.search_or_create_customer(row) if not partner else partner
        new_item =  self._prepare_sale_order_items(row)
        items.append(Command.create(new_item))
        has_shipping_line = any(
        isinstance(item, tuple) and isinstance(item[2], dict) and item[2].get("name") == "Envío"
        for item in items
    )

        if self.shipping_cost and row[self.shipping_cost] > 0.0 and not has_shipping_line:
            shipping_line = self._add_shipping_cost(row)
            items.append(Command.create(shipping_line))
        if self.discount and row[self.discount] > 0.0:
            discount_line = self._add_discount(row)
            items.append(Command.create(discount_line))
        sale_order_values = {
            'client_order_ref': row[self.ref_field] if self.ref_field else False,
            'tp_username': row[self.username_field] if self.username_field else False,
            'partner_id': partner_id,
            'order_line': items,
            'is_third_party_imported': True,
            "date_order": self._get_date_order(row),
            # 'payment_condition_id': self._get_payment_condition(row),
            # 'payment_acquirer_id': self._get_payment_method(row) or 1,
            "name": f'{self.name_prefix} {row[self.order_name_field]}',
            # "analytic_account_id": self._get_analytic_account(),
        }
        # if self.delivery_type_field and 'full' in str(row[self.delivery_type_field]).lower():
        #     full_warehouse = self.env['ir.config_parameter'].sudo().get_param('stock.warehouse.full.meli')
        #     sale_order_values.update({
        #         'warehouse_id': full_warehouse,
        #         'meli_delivery_type': row[self.delivery_type_field],

        #     })
        return sale_order_values
    
    def _get_analytic_account(self):
        retail_analytic_account = self.env['account.analytic.account'].search([('name', 'ilike', 'Ventas Minorista')])
        if not retail_analytic_account:
            plan_id = self.env['account.analytic.plan'].search([('name', '=', 'Growtech')])
            if not plan_id:
                plan_id = self.env['account.analytic.plan'].create({'name': 'Growtech'})
            retail_analytic_account = self.env['account.analytic.account'].create({'name': 'Ventas Minorista', 'plan_id': plan_id.id})
        return retail_analytic_account.id
            

    def _get_payment_condition(self, row):
        payment_conditions = self.env['account.payment.condition'].sudo().search([(self.payment_condition_odoo_field, 'like', row[self.payment_condition_field])], limit=1)
        # Get the field, third party payment condition field and search all the payment conditions conditions which are not false and contains the keyword
        if not payment_conditions:
            raise UserError(f"Payment condition not found {row[self.payment_condition_field]}")
        return payment_conditions.id 
    
    def _get_payment_method(self, row):
        # Get the field, third party payment method field and search all the payment conditions conditions which are not false and contains the keyword
        payment_methods = self.env['res.partner.payment.method'].sudo().search([(self.payment_method_odoo_field, 'like',  row[self.payment_method_field] )], limit=1) 
        # Get the field, third party payment condition field and search all the payment conditions conditions which are not false and contains the keyword
        return payment_methods.id 
    
