from odoo.models import TransientModel
class WoocomerceSaleImporter(TransientModel):
    _name = 'woocommerce.sale.importer'
    _description = 'Woocomerce Sale Importer'
    _inherit = 'base.third.party.sale.importer'
    

    @property
    def ref_field(self):
        return "Cobro Aprobado"
    
    @property
    def username_field(self):
        return "Usuario ML"
        
    @property
    def order_name_field(self):
        return "Número de pedido"
    
    @property
    def product_uom_qty_field(self):
        return "Cantidad"
    
    @property
    def price_unit_field(self):
        return "Coste de artículo"
    
    @property
    def date_order_field(self):
        return "Fecha del pedido"
    
    @property
    def customer_name_field(self):
        return "Apellidos (facturación)"
    
    @property
    def product_code_field(self):
        return "SKU"

    @property
    def name_prefix(self):
        return "WOO"
     
    @property
    def date_strptime_format(self):
        return "%Y-%m-%d %H:%M:%S"
    
    @property
    def status_done(self):
        return ["Completado", "Procesando"]
    
    @property
    def status_cancel(self):
        return ["Cancelled", "Falló"]
    
    @property
    def status_field(self):
        return "Estado del pedido"
    
    def _get_payment_condition(self, row):
        return self.env['account.payment.condition'].sudo().search([(self.payment_condition_odoo_field, 'like',  "contraentrega" )], limit=1).id

    @property
    def payment_condition_odoo_field(self):
        return "woocomerce_conditions"
    
    @property
    def payment_method_field(self):
        return "Título del método de pago"

    @property
    def payment_method_odoo_field(self):
        return "woocomerce_payment_method"
    
    @property
    def customer_vat_field(self):
        return "Empresa (facturación)"

    @property
    def customer_email_field(self):
        return "Correo electrónico (facturación)"
    
    @property
    def afip_responsability_type_field(self):
        return False
    
    @property
    def delivery_type_field(self):
        return False
    
    @property
    def city_field(self):
        return "Ciudad (facturación)"
    
    @property
    def state_field(self):
        return "Código de provincia (facturación)"
    
    @property
    def zip_field(self):
        return "Código postal (facturación)"
    
    @property
    def address_field(self):
        return "Dirección lineas 1 y 2 (facturación)"
    
    @property
    def number_field(self):
        return False
    
    @property
    def floor_field(self):
        return False
    
    @property
    def market_name(self):
        return 'Woocommerce'
    
    @property
    def shipping_cost(self):
        return False
    
    @property
    def discount(self):
        return False
