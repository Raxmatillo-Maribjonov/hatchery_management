from odoo import models, fields, api
from datetime import timedelta


class IncubationBatch(models.Model):
    _name = 'hatchery.incubation.batch'
    _description = 'Inkubatsiya'
    _inherit = ['mail.thread']

    name = fields.Char(
        string='Nomi',
        required=True,
        tracking=True,
        default=lambda self: f"Inkubatsiya {fields.Date.today()}"
    )

    delivery_id = fields.Many2one(
        'hatchery.egg.delivery',
        string='Partiya',
        required=True,
        ondelete='restrict',
        tracking=True
    )

    incubator_ids = fields.Many2many(
        'hatchery.incubator',
        'hatchery_batch_incubator_rel',
        'batch_id', 'incubator_id',
        string='Inkubatorlar',
        domain="[('state', '=', 'empty')]"
    )
    incubator_id = fields.Many2one(
        'hatchery.incubator',
        string='Asosiy inkubator',
        compute='_compute_main_incubator',
        store=True
    )

    # Kirish va Chiqish — DateTime (sana + vaqt)
    entry_datetime = fields.Datetime(
        string='Kirish sanasi va vaqti',
        required=True,
        tracking=True,
        default=fields.Datetime.now
    )
    exit_datetime = fields.Datetime(
        string='Chiqish sanasi va vaqti',
        tracking=True
    )

    # Eski nomlar (boshqa kodlar bilan moslik)
    zapravka_date = fields.Date(
        string='Kirish sanasi (kun)',
        compute='_compute_zapravka_date',
        store=True
    )
    expected_hatch_date = fields.Date(
        string='Chiqish sanasi (kun)',
        compute='_compute_hatch_date',
        store=True
    )

    actual_chick_count = fields.Integer(
        string="Haqiqiy chiqgan jo'ja soni", tracking=True)

    state = fields.Selection([
        ('draft', 'Yangi'),
        ('in_progress', 'Inkubatsiyada'),
        ('hatched', 'Chiqdi'),
        ('done', 'Tugadi'),
    ], string='Holat', default='draft', tracking=True)

    log_ids = fields.One2many(
        'hatchery.incubation.log', 'batch_id', string='Kunlik jurnal')

    total_eggs = fields.Integer(
        related='delivery_id.incubation_eggs',
        string='Partiya jami tuxum',
        store=True
    )
    total_expected_chick = fields.Integer(
        related='delivery_id.total_expected_chick_count',
        string="Kutilgan jo'ja",
        store=True
    )

    egg_count = fields.Integer(string='Bu inkubatsiyaga tuxum soni', default=0)

    already_assigned = fields.Integer(
        string='Boshqa inkubatsiyalarga joylangan',
        compute='_compute_remaining', store=False)
    remaining_eggs = fields.Integer(
        string='Qolgan (joylanmagan) tuxum',
        compute='_compute_remaining', store=False)

    # Tanlangan inkubatorlar jami sig'imi
    selected_capacity = fields.Integer(
        string='Tanlangan sig\'im', compute='_compute_capacity', store=False)
    capacity_diff = fields.Integer(
        string='Farq', compute='_compute_capacity', store=False)
    capacity_warning = fields.Selection([
        ('ok', 'Optimal'),
        ('over', 'Ortiqcha sig\'im'),
        ('under', 'Yetarli sig\'im yo\'q'),
    ], compute='_compute_capacity', store=False)
    capacity_message = fields.Char(
        string='Xabar', compute='_compute_capacity', store=False)

    # ─────────────────────────────────
    @api.depends('incubator_ids')
    def _compute_main_incubator(self):
        for rec in self:
            rec.incubator_id = rec.incubator_ids[:1]

    @api.depends('entry_datetime')
    def _compute_zapravka_date(self):
        for rec in self:
            rec.zapravka_date = rec.entry_datetime.date() if rec.entry_datetime else False

    @api.depends('exit_datetime')
    def _compute_hatch_date(self):
        for rec in self:
            rec.expected_hatch_date = rec.exit_datetime.date() if rec.exit_datetime else False

    @api.onchange('entry_datetime')
    def _onchange_entry_datetime(self):
        if self.entry_datetime:
            self.exit_datetime = self.entry_datetime + timedelta(days=18, hours=12)

    @api.depends('incubator_ids', 'incubator_ids.capacity', 'egg_count', 'delivery_id')
    def _compute_capacity(self):
        # Bo'sh va buzilmagan inkubatorlarning minimal sig'imi
        available = self.env['hatchery.incubator'].search([
            ('state', '=', 'empty'), ('is_broken', '=', False)
        ])
        min_cap = min(available.mapped('capacity')) if available else 0

        for rec in self:
            sel_cap = sum(rec.incubator_ids.mapped('capacity'))
            need = rec.egg_count or rec.total_eggs or 0
            diff = sel_cap - need
            rec.selected_capacity = sel_cap
            rec.capacity_diff = diff

            if not rec.incubator_ids or need == 0:
                rec.capacity_warning = 'ok'
                rec.capacity_message = ''
            elif diff < 0:
                # Sig'im yetmaydi
                rec.capacity_warning = 'under'
                rec.capacity_message = (
                    f"Sig'im yetmaydi!  Tanlangan: {sel_cap:,}  |  "
                    f"Kerak: {need:,}  |  Kamomad: {abs(diff):,} ta"
                )
            elif diff > 0 and min_cap > 0 and diff >= min_cap:
                # Ortiqcha sig'im — boshqa yashiq sig'masi qadar ortiqcha
                rec.capacity_warning = 'over'
                rec.capacity_message = (
                    f"Ortiqcha yashiq tanlangan!  Tanlangan: {sel_cap:,}  |  "
                    f"Kerak: {need:,}  |  Ortiqcha: {diff:,} ta  "
                    f"(kichik yashiq: {min_cap:,} ta)"
                )
            else:
                rec.capacity_warning = 'ok'
                rec.capacity_message = (
                    f"Optimal tanlov!  Jami sig'im: {sel_cap:,} ta"
                    if sel_cap > 0 else ''
                )

    @api.depends('delivery_id', 'delivery_id.incubation_eggs', 'egg_count')
    def _compute_remaining(self):
        for rec in self:
            if not rec.delivery_id:
                rec.already_assigned = 0
                rec.remaining_eggs = 0
                continue
            total = rec.delivery_id.incubation_eggs
            others = self.env['hatchery.incubation.batch'].search([
                ('delivery_id', '=', rec.delivery_id.id),
                ('id', '!=', rec.id or 0),
                ('state', '!=', 'done'),
            ])
            assigned = sum(others.mapped('egg_count'))
            rec.already_assigned = assigned
            rec.remaining_eggs = total - assigned - (rec.egg_count or 0)

    def action_start(self):
        self.state = 'in_progress'

    def action_hatch(self):
        self.state = 'hatched'

    def action_done(self):
        self.state = 'done'
