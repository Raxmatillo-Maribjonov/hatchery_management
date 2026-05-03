from odoo import models, fields, api
from datetime import datetime
import pytz


def _default_arrival_time(self):
    tz_name = self.env.context.get('tz') or self.env.user.tz or 'UTC'
    tz = pytz.timezone(tz_name)
    now = datetime.now(pytz.utc).astimezone(tz)
    return now.hour + now.minute / 60.0


class EggDelivery(models.Model):
    _name = 'hatchery.egg.delivery'
    _description = 'Partiya'
    _inherit = ['mail.thread']
    _order = 'arrival_date desc, arrival_time desc'

    name = fields.Char(
        string='Nomi',
        required=True,
        tracking=True,
        default=lambda self: f"Partiya {fields.Date.today()}"
    )

    # Vaqt
    arrival_date = fields.Date(
        string='Tuxumlar yetib kelgan kun',
        required=True, default=fields.Date.today, tracking=True)
    arrival_time = fields.Float(
        string='Tuxumlar yetib kelgan soat',
        required=True,
        default=_default_arrival_time,
        help='Masalan: 14.5 = 14:30')

    # Harorat
    outside_temp = fields.Float(string='Tashqaridagi harorat (°C)', tracking=True)
    vehicle_temp = fields.Float(string='Tuxum yetkazuvchi moshina harorati (°C)', tracking=True)
    egg_temp = fields.Float(string='Tuxumning harorati (°C)', tracking=True)
    room_temp = fields.Float(string='Xonaning harorati (°C)', tracking=True)
    storage_temp = fields.Float(string='Tuxum omborining harorati (°C)', tracking=True)

    # Transport
    vehicle_number = fields.Char(string='Tuxum yetkazuvchi moshina davlat raqami', tracking=True)
    driver_name = fields.Char(string='Tuxum yetkazuvchi moshina haydovchisi', tracking=True)
    receiver_id = fields.Many2one(
        'res.users',
        string='Tuxumlarni qabul qiluvchi mas\'ul',
        tracking=True,
        default=lambda self: self.env.user
    )

    # Miqdorlar
    total_eggs_received = fields.Integer(
        string='Olib kelingan jami tuxumlar soni', required=True, tracking=True)
    transport_losses = fields.Integer(
        string='Yo\'ldagi yo\'qotishlar soni', default=0, tracking=True)
    unloading_losses = fields.Integer(
        string='Tushirishdagi yo\'qotishlar soni', default=0, tracking=True)
    sorting_unusable = fields.Integer(
        string='Saralashda aniqlangan yaroqsiz tuxumlar soni', default=0, tracking=True)
    sorting_losses = fields.Integer(
        string='Saralashda yo\'qotilgan tuxumlar soni', default=0, tracking=True)

    incubation_eggs = fields.Integer(
        string='Inkubatsiyaga kirgan tuxumlar soni',
        compute='_compute_incubation_eggs', store=True)

    line_ids = fields.One2many(
        'hatchery.egg.delivery.line', 'delivery_id',
        string='Sort bo\'yicha taqsimot')

    total_expected_chick_count = fields.Integer(
        string='Jami kutilgan jo\'ja',
        compute='_compute_totals', store=True)

    notes = fields.Text(string='Izoh')

    @api.depends('total_eggs_received', 'transport_losses',
                 'unloading_losses', 'sorting_unusable', 'sorting_losses')
    def _compute_incubation_eggs(self):
        for rec in self:
            rec.incubation_eggs = (
                rec.total_eggs_received
                - rec.transport_losses
                - rec.unloading_losses
                - rec.sorting_unusable
                - rec.sorting_losses
            )

    @api.depends('line_ids.expected_chick_count')
    def _compute_totals(self):
        for rec in self:
            rec.total_expected_chick_count = sum(rec.line_ids.mapped('expected_chick_count'))
