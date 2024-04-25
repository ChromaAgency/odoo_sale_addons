# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api    


class ResPartner(models.Model):
    _inherit = 'res.partner'



    section = fields.Char(string="Barrio")
    net_captor = fields.Selection([
        ('facebook','Facebook'),
        ('instagram', 'Instagram'),
        ('twiter', 'Twiter'),
        ('otra', 'Otra')],"Red social"
    )
    net_name = fields.Char('Nombre de Usuario', help="Nombre del usuario en la red social")
    discharge_date = fields.Date(string="Fecha de alta")
    responsable_discharge = fields.Selection([('csottile', 'csottile'),('cveron', 'cveron'),('fcaviglione', 'fcaviglione'),('yortiz', 'yortiz'), ('eortigoza','eortigoza'), ('lregulez','lregulez')], string="Responsable Alta de Cliente")
    responsable_payments = fields.Selection([('yortiz', 'yortiz'),('cfunes', 'cfunes'),('jrolon', 'jrolon'),('apijuan', 'apijuan'), ('fcaviglione','fcaviglione')], string="Responsable Cobranzas Cliente")

    carrier_id = fields.Many2one('delivery.carrier.express',  string="Expreso")
    qm_hour_from_eve = fields.Selection([
        ('00:00', '00:00'),
        ('01:00', '01:00'),
        ('02:00', '02:00'),
        ('03:00', '03:00'),
        ('04:00', '04:00'),
        ('05:00', '05:00'),
        ('06:00', '06:00'),
        ('07:00', '07:00'),
        ('08:00', '08:00'),
        ('09:00', '09:00'),
        ('10:00', '10:00'),
        ('11:00', '11:00'),
        ('12:00', '12:00'),
        ('13:00', '13:00'),
        ('14:00', '14:00'),
        ('15:00', '15:00'),
        ('16:00', '16:00'),
        ('17:00', '17:00'),
        ('18:00', '18:00'),
        ('19:00', '19:00'),
        ('20:00', '20:00'),
        ('21:00', '21:00'),
        ('22:00', '22:00'),
        ('23:00', '23:00'),
        ('00:30', '00:30'),
        ('01:30', '01:30'),
        ('02:30', '02:30'),
        ('03:30', '03:30'),
        ('04:30', '04:30'),
        ('05:30', '05:30'),
        ('06:30', '06:30'),
        ('07:30', '07:30'),
        ('08:30', '08:30'),
        ('09:30', '09:30'),
        ('10:30', '10:30'),
        ('11:30', '11:30'),
        ('12:30', '12:30'),
        ('13:30', '13:30'),
        ('14:30', '14:30'),
        ('15:30', '15:30'),
        ('16:30', '16:30'),
        ('17:30', '17:30'),
        ('18:30', '18:30'),
        ('19:30', '19:30'),
        ('20:30', '20:30'),
        ('21:30', '21:30'),
        ('22:30', '22:30'),
        ('23:30', '23:30'),


    ], 'Hour From eve')
    qm_hour_to_eve = fields.Selection([
        ('00:00', '00:00'),
        ('01:00', '01:00'),
        ('02:00', '02:00'),
        ('03:00', '03:00'),
        ('04:00', '04:00'),
        ('05:00', '05:00'),
        ('06:00', '06:00'),
        ('07:00', '07:00'),
        ('08:00', '08:00'),
        ('09:00', '09:00'),
        ('10:00', '10:00'),
        ('11:00', '11:00'),
        ('12:00', '12:00'),
        ('13:00', '13:00'),
        ('14:00', '14:00'),
        ('15:00', '15:00'),
        ('16:00', '16:00'),
        ('17:00', '17:00'),
        ('18:00', '18:00'),
        ('19:00', '19:00'),
        ('20:00', '20:00'),
        ('21:00', '21:00'),
        ('22:00', '22:00'),
        ('23:00', '23:00'),
        ('00:30', '00:30'),
        ('01:30', '01:30'),
        ('02:30', '02:30'),
        ('03:30', '03:30'),
        ('04:30', '04:30'),
        ('05:30', '05:30'),
        ('06:30', '06:30'),
        ('07:30', '07:30'),
        ('08:30', '08:30'),
        ('09:30', '09:30'),
        ('10:30', '10:30'),
        ('11:30', '11:30'),
        ('12:30', '12:30'),
        ('13:30', '13:30'),
        ('14:30', '14:30'),
        ('15:30', '15:30'),
        ('16:30', '16:30'),
        ('17:30', '17:30'),
        ('18:30', '18:30'),
        ('19:30', '19:30'),
        ('20:30', '20:30'),
        ('21:30', '21:30'),
        ('22:30', '22:30'),
        ('23:30', '23:30'),
    ], 'Hour To eve')


    @api.depends(lambda self: self._display_address_depends())
    def _compute_contact_address(self):
        for partner in self:
            if not partner.carrier_id or not partner.carrier_id.contact_address_complete:
                super(ResPartner, partner)._compute_contact_address()
            else:
                partner.contact_address = partner.carrier_id.contact_address_complete
