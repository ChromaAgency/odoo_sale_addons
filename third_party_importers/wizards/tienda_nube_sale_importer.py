from odoo.models import TransientModel
import pandas as pd
TN_FIELD_TO_SEARCH_CART_ITEMS = "Fecha"

import logging
_logger = logging.getLogger(__name__)
def search_cart_row_in_df(df:pd.DataFrame, index, indexes):
    previous_index = index-1
    if previous_index in indexes:
        return search_cart_row_in_df(df, previous_index, indexes)
    return df.loc[previous_index]

class TiendaNubeSaleImporter(TransientModel):
    _name = 'tiendanube.sale.importer'
    _description = 'Tienda nube Sale Importer'
    _inherit = 'base.third.party.sale.importer'

    def modify_df_with_cart_values(self, row, indexes, df):
        if row.name in indexes:
            cart_row = search_cart_row_in_df(df, row.name, indexes)
            row[self.date_order_field] = cart_row[self.date_order_field]
            row[self.customer_name_field] = cart_row[self.customer_name_field]
            row[self.status_field] = cart_row[self.status_field]
        return row

    def _add_fields_to_cart_items_and_erase_cart_line(self, df:pd.DataFrame):
        df_to_add_fields = df[df[TN_FIELD_TO_SEARCH_CART_ITEMS].isna()]
        indexes = list(df_to_add_fields.index)
        r_df = df.apply(lambda index: self.modify_df_with_cart_values(index, indexes, df), axis=1)
        return r_df[~r_df[self.product_code_field].isna()]

    def _preprocess_df(self, df:pd.DataFrame):
        df = self._add_fields_to_cart_items_and_erase_cart_line(df)
        return df
    
    @property
    def order_name_field(self):
        return "Número de orden"
    
    @property
    def product_uom_qty_field(self):
        return "Cantidad del producto"
    
    @property
    def price_unit_field(self):
        return "Precio del producto"
    
    @property
    def date_order_field(self):
        return "Fecha"
    
    @property
    def customer_name_field(self):
        return "Nombre del comprador"
    
    @property
    def product_code_field(self):
        return "SKU"

    @property
    def name_prefix(self):
        return "TN"
    
    @property
    def status_done(self):
        return ["Listo para enviar" ,"Archivada", "Esperando confirmación de pago", "Esperando que empaquetes la orden", "Esperando confirmación de envío", "Esperando que el cliente retire la orden", "Listas para archivar", "Enviado" ]
    
    @property
    def status_cancel(self):
        return ["Cancelada"]
   
    @property
    def status_field(self):
        return "Estado del envío"

    def _get_payment_condition(self, row):
        return self.env['account.payment.condition'].sudo().search([(self.payment_condition_odoo_field, 'like', "contraentrega" )], limit=1).id
    
    @property
    def payment_condition_odoo_field(self):
        return "tn_conditions"
    
    @property
    def payment_method_field(self):
        return "Medio de pago"

    @property
    def payment_method_odoo_field(self):
        return "tn_payment_method"
    
    @property
    def customer_vat_field(self):
        return "DNI / CUIT"

    @property
    def customer_email_field(self):
        return "Email"
    
    @property
    def afip_responsability_type_field(self):
        return False
    
    @property
    def delivery_type_field(self):
        return False
    
    @property
    def city_field(self):
        return "Localidad"
    
    @property
    def state_field(self):
        return "Provincia o estado"
    
    @property
    def zip_field(self):
        return "Código postal"
    
    @property
    def address_field(self):
        return "Dirección"
    
    @property
    def number_field(self):
        return "Número"

    @property
    def floor_field(self):
        return "Piso"
    
    @property
    def market_name(self):
        return 'Tienda Nube'
    
    @property
    def shipping_cost(self):
        return "Costo de envío"
    
    @property
    def discount(self):
        return "Descuento"
