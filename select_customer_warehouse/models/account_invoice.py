# -*- coding: utf-8 -*-
from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        res = super(AccountInvoice, self)._onchange_partner_id()
        if self.partner_id and self.partner_id.invoice_journal_id and self.type == 'out_invoice':
            self.journal_id = self.partner_id.invoice_journal_id.id
        return res

    # @api.model
    # def create(self, vals):
    #     ctx = self._context
    #     if ctx.get('invoice') and ctx.get('invoice').partner_id.invoice_seq_id:
    #         vals['name'] = ctx.get('invoice').partner_id.invoice_seq_id.next_by_id()
    #     return super(AccountMove, self.with_context(check_move_validity=False, partner_id=vals.get('partner_id'))).create(vals)

class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    @api.multi
    def _create_invoice(self, order, so_line, amount):
        res = super(SaleAdvancePaymentInv, self)._create_invoice(order, so_line, amount)
        if res.partner_id and res.partner_id.invoice_journal_id and res.type == 'out_invoice':
            res.journal_id = res.partner_id.invoice_journal_id.id
        return res
