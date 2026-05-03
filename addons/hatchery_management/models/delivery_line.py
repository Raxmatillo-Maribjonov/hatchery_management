from odoo import models, fields, api


class EggDeliveryLine(models.Model):
    _name = 'hatchery.egg.delivery.line'
    _description = 'Partiya - Sort bo\'yicha taqsimot'

    delivery_id = fields.Many2one(
        'hatchery.egg.delivery',
        string='Partiya',
        required=True,
        ondelete='cascade'
    )
    norm_id = fields.Many2one(
        'hatchery.norm.standard',
        string='Kategoriya / Yosh',
        required=True,
        ondelete='restrict'
    )
    egg_count = fields.Integer(string='Tuxum soni', required=True)
    hatch_rate = fields.Float(
        related='norm_id.hatch_rate',
        string='Chiqish (%)',
        store=True
    )
    expected_chick_count = fields.Integer(
        string='Kutilgan jo\'ja',
        compute='_compute_expected',
        store=True
    )

    @api.depends('egg_count', 'hatch_rate')
    def _compute_expected(self):
        for line in self:
            if line.egg_count and line.hatch_rate:
                line.expected_chick_count = int(line.egg_count * line.hatch_rate / 100.0)
            else:
                line.expected_chick_count = 0
