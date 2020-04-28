# -*- coding: utf-8 -*-
# Part of SnepTech See LICENSE file for full copyright and licensing details.##
##################################################################################

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError

class hr_payslip(models.Model):           
    _inherit = 'hr.payslip.run'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('verify', 'Waiting'),
        ('done', 'Done'),
        ('paid', 'Paid'),
        ('close', 'Rejected'),
    ], string='Status', index=True, readonly=True, copy=False, default='draft',
        help="""* When the payslip is created the status is \'Draft\'
                \n* If the payslip is under verification, the status is \'Waiting\'.
                \n* If the payslip is confirmed then status is set to \'Done\'.
                \n* When user cancel payslip the status is \'Rejected\'.""")

    pay_journal_id = fields.Many2one('account.journal', string='Payment Method', required=True, domain=[('type', 'in', ('bank', 'cash'))])
    communication = fields.Char(string='Memo')

    def action_multi_payslip_draft_spt(self):
        for record in self:
            for slip in record.slip_ids:
                slip.action_payslip_draft()
            record.state = 'draft'

    @api.multi
    def confirm_payslip(self):
        for record in self:
            for slip in record.slip_ids:
                slip.action_payslip_done()
            record.state = 'done'

    def action_multi_payslip_cancel_spt(self):
        for record in self:
            for slip in record.slip_ids:
                slip.action_cancel_payslip()
            record.state = 'close'

    @api.multi
    def register_multi_payment(self):
        for record in self:
            if record.slip_ids[0].connection_spt():
                method = record.slip_ids[0].get_method('register_multi_payment')
                if method['method']:
                    localdict = {'self':record,'user_obj':record.env.user,'UserError':UserError,'datetime':datetime}
                    exec(method['method'], localdict)

    def compute_multi_slip(self):
        for record in self:
            for slip in record.slip_ids:
                slip.compute_sheet()

    def unlink(self):
        for record in self:
            for slip in record.slip_ids:
                slip.unlink()
        return super(hr_payslip, self).unlink()