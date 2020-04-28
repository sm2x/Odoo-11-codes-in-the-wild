# -*- coding: utf-8 -*-
from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model
    def create(self, vals):
        ctx = self._context
        if ctx.get('invoice') and ctx.get('invoice').partner_id.invoice_seq_id:
            vals['name'] = ctx.get('invoice').partner_id.invoice_seq_id.next_by_id()
        return super(AccountMove, self.with_context(check_move_validity=False, partner_id=vals.get('partner_id'))).create(vals)
