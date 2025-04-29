from datetime import datetime
from odoo.models import TransientModel
import pandas as pd
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError
MELI_FIELD_TO_SEARCH_CART_ITEMS = "Ingresos por productos (ARS)"

def search_cart_row_in_df(df:pd.DataFrame, index, indexes):
    previous_index = index-1
    if previous_index in indexes:
        return search_cart_row_in_df(df, previous_index, indexes)
    return df.loc[previous_index]

class MeliSaleImporter(TransientModel):
    _name = 'meli.sale.importer'
    _description = 'Meli Sale Importer'
    _inherit = 'base.third.party.sale.importer'

    def modify_df_with_cart_values(self, row, indexes, df):
        if row.name in indexes:
            cart_row = search_cart_row_in_df(df, row.name, indexes)
            row[self.order_name_field] = cart_row[self.order_name_field]
            row[self.customer_name_field] = cart_row[self.customer_name_field]
            row[self.customer_vat_field] = cart_row[self.customer_vat_field]
            row[self.address_field] = cart_row[self.address_field]
            row[self.city_field] = cart_row[self.city_field]
            row[self.state_field] = cart_row[self.state_field]
            row[self.zip_field] = cart_row[self.zip_field]
            row[self.delivery_type_field] = cart_row[self.delivery_type_field]
            row[self.afip_responsability_type_field] = cart_row[self.afip_responsability_type_field]
            row[self.shipping_cost] = cart_row[self.shipping_cost]
            row[self.username_field] = cart_row[self.username_field]
            row[self.date_order_field] = cart_row[self.date_order_field]
        return row
    
    def _get_afip_responsability_type(self, row):
        if self.afip_responsability_type_field:
            # Cambiar a code para meli
            responsability_type = self.env['l10n_ar.afip.responsibility.type'].sudo().search([('code', '=',  row[self.afip_responsability_type_field] )], limit=1).id
            if responsability_type:
                return responsability_type
        return super()._get_afip_responsability_type(row)
    
    def _add_shipping_cost(self, row, items=[]):
            
        min_free_delivery = float(self.env['ir.config_parameter'].sudo().get_param('third_party_importers.min_amount_free_delivery', '0.0'))
        order_amount = sum([item[2]['price_unit'] * item[2]['product_uom_qty'] for item in items])
        is_meli_flex = row[self.delivery_type_field] == 'Mercado Envíos Flex'
        if min_free_delivery and order_amount >= min_free_delivery and is_meli_flex:
            return False

        return super()._add_shipping_cost(row, items)

    def _add_fields_to_cart_items_and_erase_cart_line(self, df:pd.DataFrame):
        df_to_add_fields = df[df[MELI_FIELD_TO_SEARCH_CART_ITEMS].isna()]
        indexes = list(df_to_add_fields.index)
        r_df = df.apply(lambda index: self.modify_df_with_cart_values(index, indexes, df), axis=1)
        return r_df[~r_df[self.product_code_field].eq(" ")]

    def _preprocess_df(self, df:pd.DataFrame):
        df = self._add_fields_to_cart_items_and_erase_cart_line(df)
        return df

    def _get_date_order(self, row):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    @property
    def header_skip(self):
        return 5

    @property
    def ref_field(self):
        return "Cobro Aprobado"
    
    @property
    def username_field(self):
        return "Usuario ML"

    @property
    def order_name_field(self):
        return "# de venta"
    
    @property
    def product_uom_qty_field(self):
        return "Unidades"
    
    @property
    def price_unit_field(self):
        return "Precio unitario de venta de la publicación (ARS)"
    
    @property
    def date_order_field(self):
        return "Fecha de venta"
    
    @property
    def customer_name_field(self):
        return "Comprador"
    
    @property
    def product_code_field(self):
        return "SKU"

    @property
    def name_prefix(self):
        return "ML"

    @property
    def status_done(self):
        return ["Procesando en la bodega", "Entregado", "En camino", "Etiqueta lista para imprimir", "Despacharemos el paquete", "Etiqueta impresa", "En punto de retiro"]
    
    @property
    def status_cancel(self):
        return ["Devolución finalizada. Te dimos el dinero.", "Reclamo cerrado con reembolso al comprador", "Cancelada por el comprador", "Venta cancelada. No despachés."]
    
    @property
    def status_field(self):
        return "Estado"

    def _get_payment_condition(self, row):
        return self.env['account.payment.condition'].sudo().search([(self.payment_condition_odoo_field, 'like',  "contraentrega")], limit=1).id

    @property
    def payment_condition_odoo_field(self):
        return "mercadolibre_conditions"
    
    def _get_payment_method(self, row):
        return self.env['res.partner.payment.method'].sudo().search([(self.payment_method_odoo_field, 'like',  "mercadopago")], limit=1).id
    @property
    def payment_method_odoo_field(self):
        return "mercadolibre_payment_method"
    
    @property
    def customer_vat_field(self):
        return "DNI"

    @property
    def customer_email_field(self):
        return False
    
    @property
    def delivery_type_field(self):
        return "Forma de entrega"
    
    @property
    def afip_responsability_type_field(self):
        return "Condición fiscal"
    
    @property
    def city_field(self):
        return "Ciudad"
    
    @property
    def state_field(self):
        return "Estado.1"
    
    @property
    def zip_field(self):
        return "Código postal"
    
    @property
    def address_field(self):
        return "Domicilio"
    
    @property
    def number_field(self):
        return False
    
    @property
    def floor_field(self):
        return False

    @property
    def market_name(self):
        return 'Mercado Libre'
    
    @property
    def shipping_cost(self):
        return "Ingresos por envío (ARS)"
    
    @property
    def discount(self):
        return False
