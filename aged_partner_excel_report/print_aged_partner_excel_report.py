# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import base64
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
from odoo import api, fields, models
from io import StringIO
import io





try:
    import xlwt
except ImportError:
    xlwt = None

class account_aged_trial_balance(models.TransientModel):
    _inherit = 'account.aged.trial.balance'

    @api.multi
    def _get_partner_move_lines(self):
        periods = {}
        start = datetime.strptime(self.date_from, "%Y-%m-%d")
        for i in range(5)[::-1]:
            stop = start - relativedelta(days=self.period_length)
            periods[str(i)] = {
                'name': (i!=0 and (str((5-(i+1)) * self.period_length) + '-' + str((5-i) * self.period_length)) or ('+'+str(4 * self.period_length))),
                'stop': start.strftime('%Y-%m-%d'),
                'start': (i!=0 and stop.strftime('%Y-%m-%d') or False),
            }
            start = stop - relativedelta(days=1)

        res = []
        total = []
        cr = self._cr
        user_company = self.env['res.users'].browse(self._uid).company_id.id
        if self.result_selection == 'customer':
            account_type = ['receivable']
        elif self.result_selection == 'supplier':
            account_type = ['payable']
        else:
            account_type = ['payable','receivable']

        move_state = ['draft', 'posted']
        if self.target_move == 'posted':
            move_state = ['posted']
        arg_list = (tuple(move_state), tuple(account_type))
        #build the reconciliation clause to see what partner needs to be printed
        reconciliation_clause = '(l.reconciled IS FALSE)'
        cr.execute('SELECT debit_move_id, credit_move_id FROM account_partial_reconcile where create_date > %s', (self.date_from,))
        reconciled_after_date = []
        for row in cr.fetchall():
            reconciled_after_date += [row[0], row[1]]
        if reconciled_after_date:
            reconciliation_clause = '(l.reconciled IS FALSE OR l.id IN %s)'
            arg_list += (tuple(reconciled_after_date),)
        arg_list += (self.date_from, user_company)
        query = '''
            SELECT DISTINCT l.partner_id, UPPER(res_partner.name)
            FROM account_move_line AS l left join res_partner on l.partner_id = res_partner.id, account_account, account_move am
            WHERE (l.account_id = account_account.id)
                AND (l.move_id = am.id)
                AND (am.state IN %s)
                AND (account_account.internal_type IN %s)
                AND ''' + reconciliation_clause + '''
                AND (l.date <= %s)
                AND l.company_id = %s
            ORDER BY UPPER(res_partner.name)'''
        cr.execute(query, arg_list)

        partners = cr.dictfetchall()
        # put a total of 0
        for i in range(7):
            total.append(0)

        # Build a string like (1,2,3) for easy use in SQL query
        partner_ids = [partner['partner_id'] for partner in partners if partner['partner_id']]
        lines = dict((partner['partner_id'] or False, []) for partner in partners)
        if not partner_ids:
            return [], [], []

        # This dictionary will store the not due amount of all partners
        undue_amounts = {}
        query = '''SELECT l.id
                FROM account_move_line AS l, account_account, account_move am
                WHERE (l.account_id = account_account.id) AND (l.move_id = am.id)
                    AND (am.state IN %s)
                    AND (account_account.internal_type IN %s)
                    AND (COALESCE(l.date_maturity,l.date) > %s)\
                    AND ((l.partner_id IN %s) OR (l.partner_id IS NULL))
                AND (l.date <= %s)
                AND l.company_id = %s'''
        cr.execute(query, (tuple(move_state), tuple(account_type), self.date_from, tuple(partner_ids), self.date_from, user_company))
        aml_ids = cr.fetchall()
        aml_ids = aml_ids and [x[0] for x in aml_ids] or []
        for line in self.env['account.move.line'].browse(aml_ids):
            partner_id = line.partner_id.id or False
            if partner_id not in undue_amounts:
                undue_amounts[partner_id] = 0.0
            line_amount = line.balance
            if line.balance == 0:
                continue
            for partial_line in line.matched_debit_ids:
                if partial_line.create_date[:10] <= self.date_from:
                    line_amount += partial_line.amount
            for partial_line in line.matched_credit_ids:
                if partial_line.create_date[:10] <= self.date_from:
                    line_amount -= partial_line.amount
            if not self.env.user.company_id.currency_id.is_zero(line_amount):
                undue_amounts[partner_id] += line_amount
                lines[partner_id].append({
                    'line': line,
                    'amount': line_amount,
                    'period': 6,
                })

        # Use one query per period and store results in history (a list variable)
        # Each history will contain: history[1] = {'<partner_id>': <partner_debit-credit>}
        history = []
        for i in range(5):
            args_list = (tuple(move_state), tuple(account_type), tuple(partner_ids),)
            dates_query = '(COALESCE(l.date_maturity,l.date)'

            if periods[str(i)]['start'] and periods[str(i)]['stop']:
                dates_query += ' BETWEEN %s AND %s)'
                args_list += (periods[str(i)]['start'], periods[str(i)]['stop'])
            elif periods[str(i)]['start']:
                dates_query += ' >= %s)'
                args_list += (periods[str(i)]['start'],)
            else:
                dates_query += ' <= %s)'
                args_list += (periods[str(i)]['stop'],)
            args_list += (self.date_from, user_company)

            query = '''SELECT l.id
                    FROM account_move_line AS l, account_account, account_move am
                    WHERE (l.account_id = account_account.id) AND (l.move_id = am.id)
                        AND (am.state IN %s)
                        AND (account_account.internal_type IN %s)
                        AND ((l.partner_id IN %s) OR (l.partner_id IS NULL))
                        AND ''' + dates_query + '''
                    AND (l.date <= %s)
                    AND l.company_id = %s'''
            cr.execute(query, args_list)
            partners_amount = {}
            aml_ids = cr.fetchall()
            aml_ids = aml_ids and [x[0] for x in aml_ids] or []
            for line in self.env['account.move.line'].browse(aml_ids):
                partner_id = line.partner_id.id or False
                if partner_id not in partners_amount:
                    partners_amount[partner_id] = 0.0
                line_amount = line.balance
                if line.balance == 0:
                    continue
                for partial_line in line.matched_debit_ids:
                    if partial_line.create_date[:10] <= self.date_from:
                        line_amount += partial_line.amount
                for partial_line in line.matched_credit_ids:
                    if partial_line.create_date[:10] <= self.date_from:
                        line_amount -= partial_line.amount

                if not self.env.user.company_id.currency_id.is_zero(line_amount):
                    partners_amount[partner_id] += line_amount
                    lines[partner_id].append({
                        'line': line,
                        'amount': line_amount,
                        'period': i + 1,
                        })
            history.append(partners_amount)

        for partner in partners:
            at_least_one_amount = False
            values = {}
            undue_amt = 0.0
            if partner['partner_id'] in undue_amounts:  # Making sure this partner actually was found by the query
                undue_amt = undue_amounts[partner['partner_id']]

            total[6] = total[6] + undue_amt
            values['direction'] = undue_amt
            if not float_is_zero(values['direction'], precision_rounding=self.env.user.company_id.currency_id.rounding):
                at_least_one_amount = True

            for i in range(5):
                during = False
                if partner['partner_id'] in history[i]:
                    during = [history[i][partner['partner_id']]]
                # Adding counter
                total[(i)] = total[(i)] + (during and during[0] or 0)
                values[str(i)] = during and during[0] or 0.0
                if not float_is_zero(values[str(i)], precision_rounding=self.env.user.company_id.currency_id.rounding):
                    at_least_one_amount = True
            values['total'] = sum([values['direction']] + [values[str(i)] for i in range(5)])
            ## Add for total
            total[(i + 1)] += values['total']
            values['partner_id'] = partner['partner_id']
            if partner['partner_id']:
                browsed_partner = self.env['res.partner'].browse(partner['partner_id'])
                values['name'] = browsed_partner.name and len(browsed_partner.name) >= 45 and browsed_partner.name[0:40] + '...' or browsed_partner.name
                values['trust'] = browsed_partner.trust
            else:
                values['name'] = _('Unknown Partner')
                values['trust'] = False

            if at_least_one_amount:
                res.append(values)

        return res, total, lines



    @api.multi
    def print_excel_report(self):
        res = {}

        start = datetime.strptime(self.date_from, "%Y-%m-%d")

        for i in range(5)[::-1]:
            stop = start - relativedelta(days=self.period_length - 1)
            res[str(i)] = {
                'name': (i!=0 and (str((5-(i+1)) * self.period_length) + '-' + str((5-i) * self.period_length)) or ('+'+str(4 * self.period_length))),
                'stop': start.strftime('%Y-%m-%d'),
                'start': (i!=0 and stop.strftime('%Y-%m-%d') or False),
            }
            start = stop - relativedelta(days=1)

        period_length = self.period_length
        if period_length<=0:
            raise UserError(_("You must set a period length greater than 0."))
        if not self.date_from:
            raise UserError(_("You must set a start date."))
#
        movelines, total, dummy = self._get_partner_move_lines()
        filename = 'Aged Partner Balance Report.xls'
        workbook = xlwt.Workbook()
        style = xlwt.XFStyle()
        tall_style = xlwt.easyxf('font:height 720;')  # 36pt
        # Create a font to use with the style
        font = xlwt.Font()
        font.name = ''
        font.bold = True
        font.height = 200
        style.font = font
        index = 1
        worksheet = workbook.add_sheet('Sheet 1')
        worksheet.write(1, 3, 'Aged Trial Balance', style)
        worksheet.write(3, 1, 'Start Date:', style)
        worksheet.write(4, 1, self.date_from)
        worksheet.write(3, 3, 'Period Length (days)', style)
        worksheet.write(4, 3, period_length)
        worksheet.write(6, 1, "Partner's:" , style)
        worksheet.write(7, 1,self.result_selection)
        worksheet.write(6, 3, "Target Moves:" , style)
        worksheet.write(7, 3, self.target_move)
        worksheet.write(9, 0, 'Partners' , style)
        worksheet.write(9, 1, "Not Due", style )
        worksheet.write(9, 2, res['4']['name'] , style)
        worksheet.write(9, 3, res['3']['name'] , style)
        worksheet.write(9, 4, res['2']['name'] , style)
        worksheet.write(9, 5, res['1']['name'] , style)
        worksheet.write(9, 6, res['0']['name'] , style)
        worksheet.write(9, 7, 'Total' , style)
        if total:
            zero_columan = total[6]
            first_col = total[4]
            sec_col = total[3]
            third_col = total[2]
            forth_col = total[1]
            fifth_col = total[0]
            sixth_col = total[5]
        if movelines:
            worksheet.write(11, 0, 'Total' , style)
            worksheet.write(11, 1, zero_columan  , style)
            worksheet.write(11, 2,  first_col, style)
            worksheet.write(11, 3,  sec_col, style)
            worksheet.write(11, 4,  third_col, style)
            worksheet.write(11, 5,  forth_col, style)
            worksheet.write(11, 6, fifth_col, style)
            worksheet.write(11, 7,  sixth_col, style)
        row = 12

        for vals in movelines:
            row = row + 1
            worksheet.write(row, 0, vals['name'])
            worksheet.write(row, 1, vals['direction'])
            worksheet.write(row, 2, vals['4'])
            worksheet.write(row, 3, vals['3'])
            worksheet.write(row, 4, vals['2'])
            worksheet.write(row, 5, vals['1'])
            worksheet.write(row, 6, vals['0'])
            worksheet.write(row, 7, vals['total'])
        row= row+ 1    
        fp = io.BytesIO()
        workbook.save(fp)
        export_id = self.env['aged.partner.balance.report.excel'].create({'excel_file': base64.encodestring(fp.getvalue()), 'file_name': filename})
        fp.close()
        res = {
                        'view_mode': 'form',
                        'res_id': export_id.id,
                        'res_model': 'aged.partner.balance.report.excel',
                        'view_type': 'form',
                        'type': 'ir.actions.act_window',
                        'target':'new'
                }
        return res

class aged_partner_balance_report_excel(models.TransientModel):
    _name = "aged.partner.balance.report.excel"
    
    
    excel_file = fields.Binary('Excel Report for aged partner balance ')
    file_name = fields.Char('Excel File', size=64)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
