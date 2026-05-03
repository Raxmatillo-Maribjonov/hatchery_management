from odoo import models, fields, api


class IncubationBatchLine(models.Model):
    _name = 'hatchery.incubation.batch.line'
    _description = 'Partiya Kategoriya Qatori'

    batch_id = fields.Many2one(
        'hatchery.incubation.batch',
        string='Partiya',
        required=True,
        ondelete='cascade'
    )

    # Asosiy tanlov: "1-sort 24-haftalik" kabi
    norm_id = fields.Many2one(
        'hatchery.norm.standard',
        string='Kategoriya / Yosh',
        required=True,
        ondelete='restrict'
    )

    # Normativdan olinadigan ma'lumotlar
    category = fields.Char(
        related='norm_id.category',
        string='Kategoriya',
        store=True
    )
    age_weeks = fields.Integer(
        related='norm_id.age_weeks',
        string='Tuxum yoshi (hafta)',
        store=True
    )
    hatch_rate = fields.Float(
        related='norm_id.hatch_rate',
        string='Chiqish foizi (%)',
        store=True
    )
    egg_count = fields.Integer(string='Tuxum soni', required=True)

    expected_chick_count = fields.Integer(
        string='Kutilgan jo\'ja',
        compute='_compute_expected',
        store=True
    )
    actual_chick_count = fields.Integer(string='Haqiqiy jo\'ja')

    @api.depends('egg_count', 'hatch_rate')
    def _compute_expected(self):
        for line in self:
            if line.egg_count and line.hatch_rate:
                line.expected_chick_count = int(line.egg_count * line.hatch_rate / 100.0)
            else:
                line.expected_chick_count = 0
