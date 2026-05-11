from odoo import models, fields, api
import json


class HatcheryDashboard(models.TransientModel):
    _name = 'hatchery.dashboard'
    _description = 'Hatchery Bosh Sahifa'
    _rec_name = 'name'

    name = fields.Char(default='Bosh Sahifa', readonly=True)
    date_from = fields.Date()
    date_to = fields.Date()

    # Loss chart JSON
    loss_chart_data = fields.Char(readonly=True)

    # Inkubatorlar (dinamik, JSON)
    incubators_json = fields.Char(readonly=True)

    # Hidden comparison fields (kept for compatibility)
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
    chart_data = fields.Char()
    chart_period_label = fields.Char()

    def _compute_loss_chart(self):
        """Barcha partiyalar bo'yicha yo'qotishlar."""
        deliveries = self.env['hatchery.egg.delivery'].search(
            [], order='arrival_date asc', limit=20)
        labels, transport, unloading, unusable, sorting = [], [], [], [], []
        for d in deliveries:
            label = d.arrival_label or str(d.arrival_date)
            labels.append(label[:16] if label else '')
            transport.append(d.transport_losses)
            unloading.append(d.unloading_losses)
            unusable.append(d.sorting_unusable)
            sorting.append(d.sorting_losses)
        return json.dumps({
            'labels': labels,
            'datasets': [
                {'label': "Yo'ldagi", 'color': '#3b82f6', 'data': transport},
                {'label': 'Tushirishdagi', 'color': '#f59e0b', 'data': unloading},
                {'label': 'Yaroqsiz', 'color': '#ef4444', 'data': unusable},
                {'label': 'Saralashdagi', 'color': '#8b5cf6', 'data': sorting},
            ]
        })

    def _compute_incubators(self):
        """Barcha inkubatorlar holati."""
        incubators = self.env['hatchery.incubator'].search([], order='name')
        result = []
        for inc in incubators:
            batch = inc.active_batch_id
            result.append({
                'name': inc.name,
                'capacity': inc.capacity,
                'is_broken': inc.is_broken,
                'state': inc.state,
                'state_label': 'Faol' if inc.state == 'loaded' else "Bo'sh",
                'delivery': batch.delivery_id.name if batch else '',
                'entry': fields.Datetime.to_string(batch.entry_datetime) if batch and batch.entry_datetime else '',
                'exit': fields.Datetime.to_string(batch.exit_datetime) if batch and batch.exit_datetime else '',
            })
        return json.dumps(result)

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        defaults['loss_chart_data'] = self._compute_loss_chart()
        defaults['incubators_json'] = self._compute_incubators()
        return defaults

    @api.onchange('date_from', 'date_to')
    def _onchange_dates(self):
        self.loss_chart_data = self._compute_loss_chart()
