#################################################################################
# Author      : Inflow Industrial Solutions. (<https://inflow.co.in/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://inflow.co.in/>
#################################################################################

from odoo import api, fields, models, _

class Gstr1ToolExt(models.Model):
    _inherit = "gstr1.tool"

    account_journal_id = fields.Many2one('account.journal', string='Account Journal', required=True, widget="selection")

    def getInvoiceObjs(self, extrafilter=(), invoiceType=''):
        invoiceObjs = []
        gstObjs = self.search([])
        if extrafilter:
            gstObjs = self.search([extrafilter])
        invoiceIds = []
        for gstObj in gstObjs:
            invoiceIds.extend(gstObj.invoice_lines.ids)
        if self.period_id:
            filter = [
                ('date_invoice', '>=', self.period_id.date_start),
                ('date_invoice', '<=', self.period_id.date_stop),
                ('gst_status', '=', 'not_uploaded'),
                ('type', '=', invoiceType),
                ('state', 'in', ['open', 'paid']),
                ('journal_id', '=', self.account_journal_id.id),
            ]
            if not self.date_from:
                self.date_from = self.period_id.date_start
                self.date_to = self.period_id.date_start
            if self.date_from and self.date_to:
                if self.period_id.date_start > self.date_from or self.period_id.date_start > self.date_to or self.period_id.date_stop < self.date_to or self.period_id.date_stop < self.date_from:
                    raise UserError("Date should belong to selected period")
                if self.date_from > self.date_to:
                    raise UserError("End date should greater than or equal to starting date")
                filter.append(('date_invoice', '>=', self.date_from))
                filter.append(('date_invoice', '<=', self.date_to))
            if invoiceIds:
                filter.append(('id', 'not in', invoiceIds))
            invoiceObjs = self.env['account.invoice'].search(filter)
        # ctx = dict(self._context or {})
        # if not ctx.get('btn'):
        #     if not ctx.get('current_id'):
        #         return []
        return invoiceObjs