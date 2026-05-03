from odoo import models, fields, api
from datetime import date, timedelta
import calendar
import json


class HatcheryDashboard(models.TransientModel):
    _name = 'hatchery.dashboard'
    _description = 'Hatchery Bosh Sahifa'
    _rec_name = 'name'

    name = fields.Char(default='Bosh Sahifa', readonly=True)
    date_from = fields.Date()
    date_to = fields.Date()

    # === Asosiy KPI ===
    total_partiya = fields.Integer()
    total_eggs_received = fields.Integer()
    total_incubation_eggs = fields.Integer()
    active_incubation = fields.Integer()
    eggs_in_incubation = fields.Integer()
    expected_chicks = fields.Integer()
    hatching_this_week = fields.Integer()
    hatching_today = fields.Integer()
    confirmed_reservations = fields.Integer()
    waiting_reservations = fields.Integer()
    total_reserved_chicks = fields.Integer()

    # === Comparison (o'tgan davr bilan) ===
    prev_total_partiya = fields.Integer()
    prev_eggs_in_incubation = fields.Integer()
    prev_expected_chicks = fields.Integer()
    prev_confirmed_reservations = fields.Integer()

    change_partiya_pct = fields.Float(digits=(6, 1))
    change_eggs_pct = fields.Float(digits=(6, 1))
    change_chicks_pct = fields.Float(digits=(6, 1))
    change_reservations_pct = fields.Float(digits=(6, 1))

    change_partiya_up = fields.Boolean()
    change_eggs_up = fields.Boolean()
    change_chicks_up = fields.Boolean()
    change_reservations_up = fields.Boolean()

    # === Inkubatorlar ===
    incubator_1_name = fields.Char()
    incubator_1_state = fields.Char()
    incubator_1_capacity = fields.Integer()
    incubator_1_eggs = fields.Integer()
    incubator_1_free = fields.Integer()
    incubator_1_utilization = fields.Float()
    incubator_1_hatch_date = fields.Date()

    incubator_2_name = fields.Char()
    incubator_2_state = fields.Char()
    incubator_2_capacity = fields.Integer()
    incubator_2_eggs = fields.Integer()
    incubator_2_free = fields.Integer()
    incubator_2_utilization = fields.Float()
    incubator_2_hatch_date = fields.Date()

    incubator_3_name = fields.Char()
    incubator_3_state = fields.Char()
    incubator_3_capacity = fields.Integer()
    incubator_3_eggs = fields.Integer()
    incubator_3_free = fields.Integer()
    incubator_3_utilization = fields.Float()
    incubator_3_hatch_date = fields.Date()

    incubator_4_name = fields.Char()
    incubator_4_state = fields.Char()
    incubator_4_capacity = fields.Integer()
    incubator_4_eggs = fields.Integer()
    incubator_4_free = fields.Integer()
    incubator_4_utilization = fields.Float()
    incubator_4_hatch_date = fields.Date()

    # === Chart data ===
    chart_data = fields.Char()
    chart_period_label = fields.Char()

    # ─────────────────────────────────────────
    def _pct(self, cur, prev):
        if not prev:
            return (100.0 if cur else 0.0), (cur > 0)
        p = round((cur - prev) / prev * 100, 1)
        return abs(p), (p >= 0)

    def _dom(self, df, dt, field='arrival_date'):
        d = []
        if df:
            d.append((field, '>=', df.strftime('%Y-%m-%d')))
        if dt:
            d.append((field, '<=', dt.strftime('%Y-%m-%d')))
        return d

    def _prev_period(self, df, dt):
        if not df or not dt:
            return None, None
        delta = (dt - df).days + 1
        prev_dt = df - timedelta(days=1)
        prev_df = prev_dt - timedelta(days=delta - 1)
        return prev_df, prev_dt

    def _compute_stats(self, df=None, dt=None):
        today = date.today()
        week_later = today + timedelta(days=7)

        deliveries = self.env['hatchery.egg.delivery'].search(self._dom(df, dt))
        batches    = self.env['hatchery.incubation.batch'].search(self._dom(df, dt, 'zapravka_date'))
        active     = batches.filtered(lambda b: b.state == 'in_progress')
        reservations = self.env['hatchery.reservation'].search([])
        confirmed  = reservations.filtered(lambda r: r.state == 'confirmed')
        waiting    = reservations.filtered(lambda r: r.state == 'waiting')

        cur_partiya = len(deliveries)
        cur_eggs    = sum(active.mapped('total_eggs'))
        cur_chicks  = sum(active.mapped('total_expected_chick'))
        cur_res     = len(confirmed)

        # Previous period
        prev_df, prev_dt = self._prev_period(df, dt)
        prev_deliveries = self.env['hatchery.egg.delivery'].search(self._dom(prev_df, prev_dt))
        prev_batches    = self.env['hatchery.incubation.batch'].search(
            self._dom(prev_df, prev_dt, 'zapravka_date'))
        prev_active     = prev_batches.filtered(lambda b: b.state == 'in_progress')
        prev_reservations = self.env['hatchery.reservation'].search([])
        prev_confirmed  = prev_reservations.filtered(lambda r: r.state == 'confirmed')

        prev_partiya = len(prev_deliveries)
        prev_eggs    = sum(prev_active.mapped('total_eggs'))
        prev_chicks  = sum(prev_active.mapped('total_expected_chick'))
        prev_res     = len(prev_confirmed)

        p_pct, p_up   = self._pct(cur_partiya, prev_partiya)
        e_pct, e_up   = self._pct(cur_eggs, prev_eggs)
        ch_pct, ch_up = self._pct(cur_chicks, prev_chicks)
        r_pct, r_up   = self._pct(cur_res, prev_res)

        vals = {
            'total_partiya':          cur_partiya,
            'total_eggs_received':    sum(deliveries.mapped('total_eggs_received')),
            'total_incubation_eggs':  sum(deliveries.mapped('incubation_eggs')),
            'active_incubation':      len(active),
            'eggs_in_incubation':     cur_eggs,
            'expected_chicks':        cur_chicks,
            'hatching_today':         len(active.filtered(lambda b: b.expected_hatch_date == today)),
            'hatching_this_week':     len(active.filtered(
                lambda b: b.expected_hatch_date and today <= b.expected_hatch_date <= week_later)),
            'confirmed_reservations': cur_res,
            'waiting_reservations':   len(waiting),
            'total_reserved_chicks':  sum((confirmed + waiting).mapped('chick_count')),
            # Comparison
            'prev_total_partiya':          prev_partiya,
            'prev_eggs_in_incubation':     prev_eggs,
            'prev_expected_chicks':        prev_chicks,
            'prev_confirmed_reservations': prev_res,
            'change_partiya_pct':     p_pct,
            'change_eggs_pct':        e_pct,
            'change_chicks_pct':      ch_pct,
            'change_reservations_pct': r_pct,
            'change_partiya_up':      p_up,
            'change_eggs_up':         e_up,
            'change_chicks_up':       ch_up,
            'change_reservations_up': r_up,
        }

        # Inkubatorlar
        incubators = self.env['hatchery.incubator'].search([], limit=4)
        for i, inc in enumerate(incubators, 1):
            batch = inc.active_batch_id
            eggs  = batch.total_eggs if batch else 0
            cap   = inc.capacity or 1
            vals[f'incubator_{i}_name']        = inc.name
            vals[f'incubator_{i}_state']       = inc.state
            vals[f'incubator_{i}_capacity']    = inc.capacity
            vals[f'incubator_{i}_eggs']        = eggs
            vals[f'incubator_{i}_free']        = max(0, inc.capacity - eggs)
            vals[f'incubator_{i}_utilization'] = round(eggs / cap * 100, 1)
            vals[f'incubator_{i}_hatch_date']  = batch.expected_hatch_date if batch else False

        # Monthly chart (joriy yil)
        vals['chart_data']         = self._monthly_chart_data()
        vals['chart_period_label'] = self._prev_label(prev_df, prev_dt)

        return vals

    def _prev_label(self, prev_df, prev_dt):
        if not prev_df or not prev_dt:
            return ''
        months = ['Yan','Fev','Mar','Apr','May','Iyn','Iyl','Avg','Sen','Okt','Noy','Dek']
        if prev_df.month == prev_dt.month:
            return f"{months[prev_df.month-1]} {prev_df.year}"
        return f"{months[prev_df.month-1]} {prev_df.day} – {months[prev_dt.month-1]} {prev_dt.day}"

    def _monthly_chart_data(self):
        today = date.today()
        year  = today.year
        months_uz = ['Yan','Fev','Mar','Apr','May','Iyn','Iyl','Avg','Sen','Okt','Noy','Dek']
        labels, eggs_data, chicks_data, partiya_data = [], [], [], []

        for m in range(1, today.month + 1):
            first = date(year, m, 1)
            last  = date(year, m, calendar.monthrange(year, m)[1])
            fmt_first = first.strftime('%Y-%m-%d')
            fmt_last  = last.strftime('%Y-%m-%d')

            deliveries = self.env['hatchery.egg.delivery'].search([
                ('arrival_date', '>=', fmt_first), ('arrival_date', '<=', fmt_last)])
            batches = self.env['hatchery.incubation.batch'].search([
                ('zapravka_date', '>=', fmt_first), ('zapravka_date', '<=', fmt_last)])

            labels.append(months_uz[m-1])
            eggs_data.append(sum(deliveries.mapped('incubation_eggs')))
            chicks_data.append(sum(batches.mapped('total_expected_chick')))
            partiya_data.append(len(deliveries))

        return json.dumps({
            'labels':  labels,
            'eggs':    eggs_data,
            'chicks':  chicks_data,
            'partiya': partiya_data,
            'year':    year,
        })

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        today = date.today()
        df = today.replace(day=1)
        dt = today.replace(day=calendar.monthrange(today.year, today.month)[1])
        defaults['date_from'] = df
        defaults['date_to']   = dt
        defaults.update(self._compute_stats(df, dt))
        return defaults

    @api.onchange('date_from', 'date_to')
    def _onchange_dates(self):
        vals = self._compute_stats(self.date_from, self.date_to)
        for k, v in vals.items():
            setattr(self, k, v)
