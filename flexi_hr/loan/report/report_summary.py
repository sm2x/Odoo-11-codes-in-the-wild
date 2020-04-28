#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

from odoo import api, models, _
from openerp.exceptions import Warning


class wrapped_report_loan_summary(models.AbstractModel):
    _name = 'report.flexi_hr.report_loan_summary'

    @api.model
    def get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name('flexi_hr.report_loan_summary')
        loan_app_id = self.env['loan.application'].browse(docids)
        for loan_id in loan_app_id:
            if loan_id.amount == 0.0:
                raise Warning(_('You not allow to print the summary with zero loan amount'))
            if loan_id.state != 'paid':
                raise Warning(_("You can't print the summary before the loan is approved"))
        return {
           'doc_ids': docids,
           'doc_model': report.model,
           'docs': loan_app_id,
        }
