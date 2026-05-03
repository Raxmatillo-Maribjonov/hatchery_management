from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Reservation(models.Model):
    _name = 'hatchery.reservation'
    _description = 'Rezerv'
    _inherit = ['mail.thread']

    name = fields.Char(string='Rezerv #', required=True, default='Yangi rezerv')
    batch_id = fields.Many2one('hatchery.incubation.batch', string='Partiya', required=True)
    client_name = fields.Char(string='Mijoz ismi', required=True)
    client_phone = fields.Char(string='Telefon')
    chick_count = fields.Integer(string='Jo\'ja soni', required=True)
    state = fields.Selection([
        ('confirmed', 'Tasdiqlangan'),
        ('waiting', 'Navbatda'),
        ('delivered', 'Berildi'),
        ('cancelled', 'Bekor qilindi'),
    ], string='Holat', default='confirmed', tracking=True)
    reservation_date = fields.Date(string='Rezerv sanasi', default=fields.Date.today)
    notes = fields.Text(string='Izoh')

    @api.constrains('chick_count', 'batch_id', 'state')
    def _check_availability(self):
        for rec in self:
            if rec.state == 'confirmed':
                batch = rec.batch_id
                reserved = sum(batch.reservation_ids.filtered(
                    lambda r: r.state == 'confirmed' and r.id != rec.id
                ).mapped('chick_count'))
                total = batch.actual_chick_count or batch.expected_chick_count
                available = total - reserved
                if rec.chick_count > available:
                    raise ValidationError(
                        f"Yetarli jo'ja yo'q! Mavjud: {available}, So'ralgan: {rec.chick_count}. "
                        f"Navbatga qo'yishni xohlaysizmi?"
                    )

    def action_set_waiting(self):
        self.state = 'waiting'

    def action_deliver(self):
        self.state = 'delivered'

    def action_cancel(self):
        self.state = 'cancelled'
