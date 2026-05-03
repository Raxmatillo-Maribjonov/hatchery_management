from odoo import models, fields, api


class NormStandard(models.Model):
    _name = 'hatchery.norm.standard'
    _description = 'Normativ Standartlar'
    _order = 'category, age_weeks'

    name = fields.Char(string='Nomi', compute='_compute_name', store=True)
    category = fields.Char(string='Kategoriya', required=True)
    age_weeks = fields.Integer(string='Tuxum yoshi (hafta)', required=True)
    hatch_rate = fields.Float(string='Chiqish foizi (%)', required=True)

    @api.depends('category', 'age_weeks')
    def _compute_name(self):
        for rec in self:
            cat = rec.category or ''
            age = rec.age_weeks or ''
            rec.name = f"{cat} {age}-haftalik" if cat and age else cat or ''

    _sql_constraints = [
        ('unique_category_age', 'UNIQUE(category, age_weeks)',
         'Bu kategoriya va yosh kombinatsiyasi allaqachon mavjud!'),
    ]
