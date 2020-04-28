from odoo import fields, models

class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    invoice_journal_id = fields.Many2one('account.journal', string='Account Journal')
