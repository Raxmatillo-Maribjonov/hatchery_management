from odoo import models, fields, api
from odoo.exceptions import ValidationError


class BatchWizardLine(models.TransientModel):
    _name = 'hatchery.batch.wizard.line'
    _description = 'Yangi Partiya - Kategoriya Qatori'

    wizard_id = fields.Many2one('hatchery.batch.wizard', ondelete='cascade')

    norm_id = fields.Many2one(
        'hatchery.norm.standard',
        string='Kategoriya / Yosh',
        required=True
    )
    egg_count = fields.Integer(string='Tuxum soni', required=True)
    hatch_rate = fields.Float(related='norm_id.hatch_rate', string='Chiqish %')
    expected_chick_count = fields.Integer(
        string='Kutilgan jo\'ja', compute='_compute_preview')

    @api.depends('egg_count', 'norm_id')
    def _compute_preview(self):
        for line in self:
            if line.egg_count and line.norm_id:
                line.expected_chick_count = int(line.egg_count * line.norm_id.hatch_rate / 100.0)
            else:
                line.expected_chick_count = 0


class BatchWizard(models.TransientModel):
    _name = 'hatchery.batch.wizard'
    _description = 'Yangi Partiya Qo\'shish'

    incubator_id = fields.Many2one('hatchery.incubator', string='Inkubator', required=True)
    zapravka_date = fields.Date(string='Zapravka kuni', required=True, default=fields.Date.today)

    line_ids = fields.One2many('hatchery.batch.wizard.line', 'wizard_id', string='Sortlar')

    total_egg_count = fields.Integer(string='Jami tuxum', compute='_compute_totals')
    total_expected_chick_count = fields.Integer(string='Jami kutilgan jo\'ja', compute='_compute_totals')

    @api.depends('line_ids.egg_count', 'line_ids.expected_chick_count')
    def _compute_totals(self):
        for rec in self:
            rec.total_egg_count = sum(rec.line_ids.mapped('egg_count'))
            rec.total_expected_chick_count = sum(rec.line_ids.mapped('expected_chick_count'))

    @api.constrains('total_egg_count', 'incubator_id')
    def _check_capacity(self):
        for rec in self:
            if rec.incubator_id and rec.total_egg_count > rec.incubator_id.capacity:
                raise ValidationError(
                    f"Jami tuxum soni ({rec.total_egg_count}) "
                    f"inkubator sig'imidan ({rec.incubator_id.capacity}) oshib ketdi!"
                )

    def action_create_batch(self):
        if not self.line_ids:
            raise ValidationError("Kamida bitta sort qatori kiriting!")

        batch = self.env['hatchery.incubation.batch'].create({
            'incubator_id': self.incubator_id.id,
            'zapravka_date': self.zapravka_date,
            'state': 'in_progress',
            'line_ids': [(0, 0, {
                'norm_id': line.norm_id.id,
                'egg_count': line.egg_count,
            }) for line in self.line_ids],
        })
        self.incubator_id.state = 'loaded'
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hatchery.incubation.batch',
            'res_id': batch.id,
            'view_mode': 'form',
        }
