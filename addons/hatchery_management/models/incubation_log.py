from odoo import models, fields, api
from datetime import date, timedelta


class IncubationLog(models.Model):
    _name = 'hatchery.incubation.log'
    _description = 'Kunlik Inkubatsiya Jurnali'
    _order = 'day_number asc, date asc'

    batch_id = fields.Many2one(
        'hatchery.incubation.batch',
        string='Inkubatsiya',
        required=True,
        ondelete='cascade'
    )

    day_number = fields.Integer(string='Kun', required=True)
    date = fields.Date(string='Sana', required=True, default=fields.Date.today)

    # Harorat
    temperature = fields.Float(string='Harorat (°C)', digits=(4, 1))

    # Nam ko\'rsatkichi
    humidity = fields.Float(string='Nam/Term ko\'rsatkichi', digits=(4, 1))

    # Zaslon holati
    damper_position = fields.Char(string='Zaslon holati')

    # Tekshiruv belgisi / izoh
    inspection_note = fields.Char(string='Tekshiruv belgisi')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'day_number' not in vals and vals.get('batch_id') and vals.get('date'):
                batch = self.env['hatchery.incubation.batch'].browse(vals['batch_id'])
                if batch.zapravka_date:
                    d = fields.Date.from_string(vals['date']) if isinstance(vals['date'], str) else vals['date']
                    vals['day_number'] = (d - batch.zapravka_date).days
        return super().create(vals_list)
