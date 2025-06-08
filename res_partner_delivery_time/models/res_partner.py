from calendar import FRIDAY, MONDAY, SATURDAY, SUNDAY, THURSDAY, TUESDAY, WEDNESDAY
from datetime import date, datetime, timedelta
from odoo import fields, models  
days_by_int_weekday = {
    str(MONDAY):'Lunes', 
    str(TUESDAY):'Martes',
    str(WEDNESDAY):'Miercoles',
    str(THURSDAY): 'Jueves',
    str(FRIDAY): 'Viernes', 
    str(SATURDAY): 'Sabado',
    str(SUNDAY):'Domingo',
}
DELIVERY_DAYS_OPTIONS = [tup for tup in days_by_int_weekday.items()]
HOURS_OPTIONS = [(str(minute),str(minute)) for minute in range(0,24)]
MINUTES_OPTIONS = [(str(minute),str(minute)) for minute in range(0,60)]
NUMBER_OF_DAYS_IN_A_WEEK = 7
def _filter_future_days_and_monday(r, weekday):
    # TODO Change this to accept date range
    return int(r.day_from) > weekday

class ResPartnerTime(models.AbstractModel):
    _name = "res.partner.time"
    _order = "day_from asc"

    name = fields.Char(string="Dia hora y minutos", compute="_compute_name")
    partner_id = fields.Many2one("res.partner")
    day_from = fields.Selection(DELIVERY_DAYS_OPTIONS, string = "Dia de entrega inicial", required=True)
    day_to = fields.Selection(DELIVERY_DAYS_OPTIONS, string = "Dia de entrega final", required=True)
    #TODO Add a widger that makes it easier to see this and adapts it to TZ in frontend
    hour_from = fields.Selection(HOURS_OPTIONS, string="Hora", required=True)
    minute_from = fields.Selection(MINUTES_OPTIONS, string="Minutos", required=True)
    hour_to = fields.Selection(HOURS_OPTIONS, string="Hora", required=True)
    minute_to = fields.Selection(MINUTES_OPTIONS, string="Minutos", required=True)

    def _compute_name(self):
        for rec in self:
            # TODO Change this to accept the date range
            weekday = days_by_int_weekday.get(rec.day_from)
            rec.name = f"{weekday} {rec.hour_from:0>2}:{rec.minute_from:0>2} - {rec.hour_to:0>2}:{rec.minute_to:0>2}"

    @property
    def most_recent_next_day(self):
        self.ensure_one()
        now = datetime.now()
        weekday = now.isoweekday() - 1
        #TODO Take into account date range
        difference_to_target_weekday = int(self.day_from) - weekday 
        if difference_to_target_weekday < 0:
            difference_to_target_weekday += NUMBER_OF_DAYS_IN_A_WEEK
        # ? When implementing this on frontend take this out
        return now.replace(hour=int(self.hour_to), minute=int(self.minute_to)) + timedelta(days=difference_to_target_weekday)

    def get_most_recent_next_date(self):
        now = date.today()
        weekday = now.isoweekday() - 1 
        if not self:
            return False
        future_days_of_this_week = self.filtered(lambda r: _filter_future_days_and_monday(r, weekday) )
        if not future_days_of_this_week:
            return self[0].most_recent_next_day
        return future_days_of_this_week[0].most_recent_next_day

class DeliveryTime(models.Model):
    _name = "res.partner.delivery_time"
    _inherit = "res.partner.time"

class ReceptionTime(models.Model):
    _name = "res.partner.reception_time"
    _inherit = "res.partner.time"

class ResPartners(models.Model):
    _inherit = "res.partner"

    delivery_time_ids = fields.One2many('res.partner.delivery_time', 'partner_id', string="Dias de entrega")
    reception_time_ids = fields.One2many('res.partner.reception_time', 'partner_id', string="Dias de recepción")

    def get_next_delivery_date(self):
        self.ensure_one()
        return self.delivery_time_ids.get_most_recent_next_date()

    def get_next_reception_date(self):
        self.ensure_one()
        return self.reception_time_ids.get_most_recent_next_date()