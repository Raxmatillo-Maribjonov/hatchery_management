from odoo import models, fields


class Incubator(models.Model):
    _name = 'hatchery.incubator'
    _description = 'Inkubator'

    name = fields.Char(string='Nomi', required=True)
    capacity = fields.Integer(string='Sig\'im (tuxum soni)', required=True)
    date_added = fields.Date(string='Qo\'shilgan sana', default=fields.Date.today)
    state = fields.Selection([
        ('empty', 'Bo\'sh'),
        ('loaded', 'Zapravka qilingan'),
    ], string='Holati', default='empty')
    batch_ids = fields.One2many('hatchery.incubation.batch', 'incubator_id', string='Partiyalar')
    active_batch_id = fields.Many2one(
        'hatchery.incubation.batch', string='Faol partiya', compute='_compute_active_batch')

    def _compute_active_batch(self):
        for rec in self:
            batch = rec.batch_ids.filtered(lambda b: b.state == 'in_progress')
            rec.active_batch_id = batch[0] if batch else False
