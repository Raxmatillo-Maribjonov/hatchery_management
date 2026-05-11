from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Reservation(models.Model):
    _name = 'hatchery.reservation'
    _description = 'Buyurtma'
    _inherit = ['mail.thread']

    name = fields.Char(string='Buyurtma #', required=True, default='Yangi buyurtma')
    delivery_id = fields.Many2one(
        'hatchery.egg.delivery',
        string='Partiya',
        required=True,
        ondelete='restrict'
    )
    client_name = fields.Char(string='Mijoz ismi', required=True)
    client_phone = fields.Char(string='Telefon')
    chick_count = fields.Integer(string="Jo'ja soni", required=True)
    state = fields.Selection([
        ('confirmed', 'Tasdiqlangan'),
        ('waiting', 'Navbatda'),
        ('delivered', 'Berildi'),
        ('cancelled', 'Bekor qilindi'),
    ], string='Holat', default='confirmed', tracking=True,
       group_expand='_group_expand_state')
    reservation_date = fields.Date(string='Sana', default=fields.Date.today)
    notes = fields.Text(string='Izoh')

    @api.model
    def _group_expand_state(self, states, domain):
        return ['confirmed', 'waiting', 'delivered', 'cancelled']

    def action_set_waiting(self):
        self.state = 'waiting'

    def action_deliver(self):
        self.state = 'delivered'

    def action_cancel(self):
        self.state = 'cancelled'
