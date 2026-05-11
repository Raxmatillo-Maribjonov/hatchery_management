from odoo import models, fields, tools


class EggDeliveryLossReport(models.Model):
    _name = 'hatchery.loss.report'
    _description = "Yo'qotishlar statistikasi"
    _auto = False
    _order = 'arrival_date asc'

    delivery_id = fields.Many2one('hatchery.egg.delivery', string='Partiya', readonly=True)
    arrival_date = fields.Date(string='Sana', readonly=True)
    arrival_label = fields.Char(string='Partiya (sana+vaqt)', readonly=True)
    loss_type = fields.Selection([
        ('transport', "Yo'ldagi yo'qotish"),
        ('unloading', 'Tushirishdagi yo\'qotish'),
        ('unusable', 'Yaroqsiz (saralashda)'),
        ('sorting', 'Saralashdagi yo\'qotish'),
    ], string="Yo'qotish turi", readonly=True)
    loss_value = fields.Integer(string="Yo'qotish soni", readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'hatchery_loss_report')
        self.env.cr.execute("""
            CREATE VIEW hatchery_loss_report AS
            SELECT
                row_number() OVER () AS id,
                id AS delivery_id,
                arrival_date,
                arrival_label,
                'transport' AS loss_type,
                transport_losses AS loss_value
            FROM hatchery_egg_delivery
            WHERE transport_losses > 0

            UNION ALL

            SELECT
                row_number() OVER () + 100000 AS id,
                id AS delivery_id,
                arrival_date,
                arrival_label,
                'unloading' AS loss_type,
                unloading_losses AS loss_value
            FROM hatchery_egg_delivery
            WHERE unloading_losses > 0

            UNION ALL

            SELECT
                row_number() OVER () + 200000 AS id,
                id AS delivery_id,
                arrival_date,
                arrival_label,
                'unusable' AS loss_type,
                sorting_unusable AS loss_value
            FROM hatchery_egg_delivery
            WHERE sorting_unusable > 0

            UNION ALL

            SELECT
                row_number() OVER () + 300000 AS id,
                id AS delivery_id,
                arrival_date,
                arrival_label,
                'sorting' AS loss_type,
                sorting_losses AS loss_value
            FROM hatchery_egg_delivery
            WHERE sorting_losses > 0
        """)
