from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta


class IncubationBatch(models.Model):
    _name = 'hatchery.incubation.batch'
    _description = 'Inkubatsiya'
    _inherit = ['mail.thread']

    name = fields.Char(string='Inkubatsiya #', compute='_compute_name', store=True)

    delivery_id = fields.Many2one(
        'hatchery.egg.delivery',
        string='Partiya',
        required=True,
        ondelete='restrict',
        tracking=True
    )
    incubator_id = fields.Many2one(
        'hatchery.incubator',
        string='Inkubator',
        required=True,
        tracking=True
    )
    zapravka_date = fields.Date(string='Zapravka kuni', required=True, tracking=True)
    expected_hatch_date = fields.Date(
        string='Kutilayotgan chiqish sanasi',
        compute='_compute_hatch_date', store=True)

    actual_chick_count = fields.Integer(
        string='Haqiqiy chiqgan jo\'ja soni', tracking=True)

    state = fields.Selection([
        ('draft', 'Yangi'),
        ('in_progress', 'Inkubatsiyada'),
        ('hatched', 'Chiqdi'),
        ('done', 'Tugadi'),
    ], string='Holat', default='draft', tracking=True)

    reservation_ids = fields.One2many(
        'hatchery.reservation', 'batch_id', string='Rezervlar')

    # Partiyadagi ma'lumotlar (related)
    total_eggs = fields.Integer(
        related='delivery_id.incubation_eggs',
        string='Inkubatsiyaga kirgan tuxum',
        store=True
    )
    total_expected_chick = fields.Integer(
        related='delivery_id.total_expected_chick_count',
        string='Kutilgan jo\'ja',
        store=True
    )

    @api.depends('incubator_id', 'delivery_id', 'zapravka_date')
    def _compute_name(self):
        for rec in self:
            inc = rec.incubator_id.name or '?'
            date = rec.zapravka_date or ''
            rec.name = f"{inc} / {date}"

    @api.depends('zapravka_date')
    def _compute_hatch_date(self):
        for rec in self:
            if rec.zapravka_date:
                rec.expected_hatch_date = rec.zapravka_date + timedelta(days=21)
            else:
                rec.expected_hatch_date = False

    def action_start(self):
        self.state = 'in_progress'
        self.incubator_id.state = 'loaded'

    def action_hatch(self):
        self.state = 'hatched'

    def action_done(self):
        self.state = 'done'
        self.incubator_id.state = 'empty'
