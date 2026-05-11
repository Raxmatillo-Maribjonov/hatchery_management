from odoo import models, fields, api


class Incubator(models.Model):
    _name = 'hatchery.incubator'
    _description = 'Inkubator'
    _order = 'name'

    name = fields.Char(string='Nomi', required=True)
    capacity = fields.Integer(string="Sig'im (tuxum soni)", required=True)
    date_added = fields.Date(string="Qo'shilgan sana", default=fields.Date.today)
    is_broken = fields.Boolean(string='Buzilgan', default=False)

    name_with_capacity = fields.Char(
        compute='_compute_name_with_capacity', store=True)

    state = fields.Selection([
        ('empty', "Bo'sh"),
        ('loaded', 'Faol'),
    ], string='Holati', compute='_compute_state', store=True)

    batch_ids = fields.Many2many(
        'hatchery.incubation.batch',
        'hatchery_batch_incubator_rel',
        'incubator_id', 'batch_id',
        string='Inkubatsiyalar'
    )

    active_batch_id = fields.Many2one(
        'hatchery.incubation.batch', string='Faol inkubatsiya',
        compute='_compute_state', store=True)

    active_delivery_name = fields.Char(
        related='active_batch_id.delivery_id.name',
        string='Partiya', store=True)
    active_entry_datetime = fields.Datetime(
        related='active_batch_id.entry_datetime',
        string='Kirish', store=True)
    active_exit_datetime = fields.Datetime(
        related='active_batch_id.exit_datetime',
        string='Chiqish', store=True)

    @api.depends('name', 'capacity')
    def _compute_name_with_capacity(self):
        for rec in self:
            rec.name_with_capacity = f"{rec.name}  —  {rec.capacity:,} ta"

    @api.depends('batch_ids.state')
    def _compute_state(self):
        for rec in self:
            batch = rec.batch_ids.filtered(lambda b: b.state == 'in_progress')
            rec.active_batch_id = batch[0] if batch else False
            rec.state = 'loaded' if rec.active_batch_id else 'empty'
