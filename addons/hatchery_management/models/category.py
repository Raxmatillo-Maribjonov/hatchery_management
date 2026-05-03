from odoo import models, fields


class HatcheryCategory(models.Model):
    _name = 'hatchery.category'
    _description = 'Tuxum Kategoriyasi'
    _order = 'name'

    name = fields.Char(string='Kategoriya nomi', required=True)

    _sql_constraints = [
        ('unique_name', 'UNIQUE(name)', 'Bu kategoriya nomi allaqachon mavjud!'),
    ]
