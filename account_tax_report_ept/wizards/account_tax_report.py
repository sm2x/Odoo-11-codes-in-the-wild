from odoo import models, fields, api
import base64
from io import StringIO, BytesIO
from datetime import datetime, time
from odoo.osv import osv
import math
import xlsxwriter
from docutils.nodes import row
import os

try:
    import xlwt
    from xlwt import Borders
except ImportError:
    xlwt = None


class import_bank_statement(models.TransientModel):
    _name = 'account.tax.report'

    from_date = fields.Date("From Date", required=True)
    to_date = fields.Date("To Date", required=True)
    company_id = fields.Many2one("res.company", string="Company", required=True)
    datas = fields.Binary('File')
    tax_ids = fields.Many2many("account.tax", string="Taxes",help="If you select taxes from here then it will generate only that tax related report otherwise it will generate the report that include all taxes.")
    tax_or_group = fields.Selection([('tax', 'Taxes'), ('group', 'Tax Groups')], string='Tax or Tax Group',default='tax')
    tax_group_ids = fields.Many2many("account.tax.group", string="Tax Group")
    zero_amount_tax = fields.Boolean('Is Consider Zero Amount Tax', help = "If user want to consider Zero amount tax in report than click on this", default = False)

    @api.model
    def default_get(self, fields):
        result = super(import_bank_statement, self).default_get(fields)
        result['from_date']=datetime.today().replace(day=1)
        result['to_date']=datetime.now()
        result['company_id']=self.env.user.company_id.id
        return result

    def create_worksheet(self, workbook):
        worksheet = workbook.add_worksheet()
        merge_format = workbook.add_format({'bold': 1, 'align': 'center'})
        merge_vat_company = workbook.add_format({'bold': 1, 'align': 'left'})
        fromdate = datetime.strptime(self.from_date, '%Y-%m-%d').strftime('%m-%d-%Y')
        todate = datetime.strptime(self.to_date, '%Y-%m-%d').strftime('%m-%d-%Y')
        title = "Tax Report From %s To %s" % (fromdate, todate)
        if self._context.get('multi_currency',False):
            worksheet.merge_range('A1:K1', title, merge_format)
            company_name = "Company : " + self.company_id.name
            worksheet.merge_range('A2:K2', company_name, merge_vat_company)
            if self.company_id.vat:
                company_vat = "Vat : " + self.company_id.vat
                worksheet.merge_range('A3:K3', company_vat, merge_vat_company)
        else:
            worksheet.merge_range('A1:H1', title, merge_format)
            company_name = "Company : " + self.company_id.name
            worksheet.merge_range('A2:H2', company_name, merge_vat_company)
            if self.company_id.vat:
                company_vat = "Vat : " + self.company_id.vat
                worksheet.merge_range('A3:H3', company_vat, merge_vat_company)
        return worksheet

    def print_header(self, qry_dict, header, worksheet, row, col, tax_type_name, merge_header_format, headerforname,
                     headerforother):
        row += 1
        if self._context.get('multi_currency', False):
            worksheet.merge_range('A%s:K%s' % (row, row), tax_type_name, merge_header_format)
        else:
            worksheet.merge_range('A%s:H%s' % (row, row), tax_type_name, merge_header_format)
        #         row+=1
        for t in header:
            if t in ['Amount', 'Tax Amount']:
                worksheet.write(row, col, t, headerforname)
            else:
                worksheet.write(row, col, t, headerforother)
            col += 1
        if qry_dict == []:
            row += 2
        return row, worksheet

    @api.multi
    def get_account_tax_report(self):
        created_file_path = '/tmp/Account Tax Report from %s to %s.xlsx' % (self.from_date, self.to_date)
        workbook = xlsxwriter.Workbook(created_file_path)
        # borders = Borders()
        multi_currency = self.env['res.config.settings'].sudo().default_get('').get('group_multi_currency')
        worksheet = self.with_context(multi_currency=multi_currency).create_worksheet(workbook)
        #         worksheet = workbook.add_sheet("Account Tax Report")
        merge_header_format = workbook.add_format({'bold': 1, 'align': 'center'})
        headerforname = workbook.add_format({'bold': 1, 'align': 'right'})
        headerforother = workbook.add_format({'bold': 1, 'align': 'left'})
        total_format = workbook.add_format({'bold': 1, 'align': 'right', 'pattern': 1, 'font_color': 'white'})
        total_label_format = workbook.add_format({'bold': 1, 'align': 'left', 'pattern': 1, 'font_color': 'white'})
        tax_or_group = self.tax_or_group

        def get_tax(aml):
            credit = aml.get('credit')
            debit = aml.get('debit')
            taxamount = debit - credit
            return taxamount

        def get_amount(aml):
            a_credit = 0
            a_debit = 0
            balance = 0
            if aml.get('id',False):
                move_amount = self.env['account.move.line'].browse(aml.get('id'))
                for line in move_amount.move_id.line_ids:
                    if move_amount.tax_line_id in line.tax_ids:
                        if not line.tax_line_id:
                            a_credit = a_credit + line.credit
                            a_debit = a_debit + line.debit
                    elif not move_amount.tax_line_id in line.tax_ids:
                        account_taxes = self.env['account.tax'].search(
                            [('children_tax_ids', 'in', move_amount.tax_line_id.id)])
                        for account_tax in account_taxes:
                            if account_tax in line.tax_ids:
                                if not line.tax_line_id:
                                    a_credit = a_credit + line.credit
                                    a_debit = a_debit + line.debit
                #                                 parent_tax_name=account_tax.name

                balance = a_debit - a_credit
            else:
                if self.zero_amount_tax:
                    if aml.get('move_id', False):
                        balance = 0
                        move_obj = self.env['account.move'].browse(aml.get('move_id'))
                        tax_ids = move_obj.line_ids[0].invoice_id.tax_line_ids.filtered(
                            lambda x:x.amount_total == 0)
                        for tax in tax_ids:
                            if tax_ids and tax_ids[0].invoice_id.type in ('out_invoice', 'in_refund'):
                                to_currency = self.env.user.company_id.currency_id
                                from_currency = tax.currency_id
                                compute_currency = from_currency.compute(abs(tax.base), to_currency)
                                balance += (compute_currency) * -1
                            else:
                                to_currency = self.env.user.company_id.currency_id
                                from_currency = tax.currency_id
                                compute_currency = from_currency.compute(abs(tax.base), to_currency)
                                balance += compute_currency

                    # move_id = self.env['account.move'].browse(aml.get('move_id'))
                    # amounts = move_id.line_ids[0].invoice_id.tax_line_ids.filtered(lambda x : x.amount_total == 0) #aml.get('debit') - aml.get('credit')
                    # for amount in amounts:
                    #     if amount.invoice_id.type in ('out_invoice','in_refund'):
                    #         balance += (amount.base) * -1
                    #     else:
                    #         balance += amount.base

            return balance

        def get_name(aml):
            o_name = ''
            if aml.get('id',False):
                move_name = self.env['account.move.line'].browse(aml.get('id'))
                for line in move_name.move_id.line_ids:
                    if move_name.tax_line_id in line.tax_ids:
                        if not line.tax_line_id:
                            o_name = line.name
            else:
                if self.zero_amount_tax:
                    move_obj = self.env['account.move'].browse(aml.get('move_id'))
                    o_name = move_obj.name

            return o_name

        def get_partner(aml):
            if aml.get('id',False):
                move_partner = self.env['account.move.line'].browse(aml.get('id'))
                partner_name = move_partner.partner_id.name
                if partner_name:
                    return partner_name
                else:
                    partner_name = ''
                    return partner_name
            else:
                if aml.get('move_id',False) and self.zero_amount_tax:
                    move_obj = self.env['account.move'].browse(aml.get('move_id'))
                    partner_name = move_obj.partner_id.name
                    if partner_name:
                        return partner_name
                    else:
                        partner_name = ''
                        return partner_name
                else:
                    partner_name = ''
                    return partner_name

        def get_ref(aml):
            if aml.get('id', False):
                move_ref = self.env['account.move.line'].browse(aml.get('id'))
                ref_name = move_ref.move_id.name
            else:
                if aml.get('move_id',False) and self.zero_amount_tax:
                    move_ref = self.env['account.move'].browse(aml.get('move_id'))
                    ref_name = move_ref.name
            return ref_name


        def get_amount_tax_currency(aml,amt):
            if aml.get('id',False):
                move_ref = self.env['account.move.line'].browse(aml.get('id'))
                amount_currency = move_ref.amount_currency
                if amount_currency==0:
                    return amt
                else:
                    return amount_currency
            else:
                if self.zero_amount_tax:
                    return aml.get('amount_currency')

        def get_amount_currency(aml,amount):
            amt_cur = 0
            if aml.get('id',False):
                move_amount = self.env['account.move.line'].browse(aml.get('id'))
                balance=amount
                if not move_amount.amount_currency==0:
                    for line in move_amount.move_id.line_ids:
                        if move_amount.tax_line_id in line.tax_ids:
                            if not line.tax_line_id:
                                amt_cur=amt_cur+line.amount_currency
                        elif not move_amount.tax_line_id in line.tax_ids:
                            account_taxes = self.env['account.tax'].search(
                                [('children_tax_ids', 'in', move_amount.tax_line_id.id)])
                            for account_tax in account_taxes:
                                if account_tax in line.tax_ids:
                                    if not line.tax_line_id:
                                        amt_cur = amt_cur + line.amount_currency

                    balance = amt_cur
            else:
                if self.zero_amount_tax:
                    balance = 0
                    move_id = self.env['account.move'].browse(aml.get('move_id'))
                    amounts = move_id.line_ids[0].invoice_id.tax_line_ids.filtered(lambda x:x.amount_total == 0)  # aml.get('debit') - aml.get('credit')
                    for amount in amounts:
                        if amount.invoice_id.type in ('out_invoice', 'in_refund'):
                            balance += (amount.base) * -1
                        else:
                            balance += amount.base

                    # if aml.get('move_id',False):
                    #     balance = 0
                    #     move_obj = self.env['account.move'].browse(aml.get('move_id'))
                    #     tax_ids = move_obj.line_ids[0].invoice_id.tax_line_ids.filtered(lambda x : x.amount_total == 0)
                    #     if tax_ids and tax_ids[0].invoice_id.type in ('out_invoice', 'in_refund'):
                    #         from_currency = self.env.user.company_id.currency_id
                    #         to_currency = tax_ids.currency_id
                    #         compute_currency = from_currency.compute(abs(amount), to_currency)
                    #         balance += (compute_currency) * -1
                    #     else:
                    #         from_currency = self.env.user.company_id.currency_id
                    #         to_currency = tax_ids.currency_id
                    #         compute_currency = from_currency.compute(abs(amount), to_currency)
                    #         balance += compute_currency

                    # balance = aml.get('amount_currency')

            return balance

        def get_currency(aml):
            if aml.get('id', False):
                move_amount = self.env['account.move.line'].browse(aml.get('id'))
                if move_amount.currency_id:
                    return move_amount.currency_id.name
                else:
                    if move_amount.move_id.currency_id:
                        return move_amount.move_id.currency_id.name
                    else:
                        return ''
            else:
                if aml.get('move_id',False) and self.zero_amount_tax:
                    move_obj = self.env['account.move'].browse(aml.get('move_id'))
                    if move_obj:
                        currency = move_obj.line_ids[0].invoice_id and move_obj.line_ids[0].invoice_id.currency_id and move_obj.line_ids[0].invoice_id.currency_id.name or move_obj.currency_id and move_obj.currency_id.name
                        return currency
                    else:
                        return ''

        row = 5
        if self.zero_amount_tax:
            at_qry = """select distinct tax_line_id from (select distinct tax_line_id from account_move_line where date BETWEEN '%s' AND '%s' AND company_id=%s and tax_line_id is not null
            union all 
            select distinct ait.tax_id as tax_line_id from account_invoice ai 
            join account_invoice_tax ait on ait.invoice_id = ai.id
            join account_move am on am.id = ai.move_id 
            where (COALESCE(ait.amount) + COALESCE(ait.amount_rounding,0)) = 0 and am.date BETWEEN '%s' AND '%s' AND ait.company_id =%s)tmp""" % (
                self.from_date, self.to_date, self.company_id.id,self.from_date, self.to_date, self.company_id.id)
            self._cr.execute(at_qry)
            at_query = self._cr.dictfetchall()
        else:
            at_qry = """select distinct tax_line_id from account_move_line where date BETWEEN '%s' AND '%s' AND company_id=%s and tax_line_id is not null""" %(self.from_date, self.to_date, self.company_id.id)
            self._cr.execute(at_qry)
            at_query = self._cr.dictfetchall()

        if tax_or_group == 'tax':
            if self.tax_ids:
                for tax in self.tax_ids:
                    qry = """select aml.id,aml.date,aml.account_id,aml.credit,aml.debit,a.amount,aml.amount_currency from account_move_line  aml join account_tax a on a.id=aml.tax_line_id 
        where aml.tax_line_id=%s AND aml.date BETWEEN '%s' AND '%s' AND aml.company_id=%s""" % (
                    tax.id, self.from_date, self.to_date, self.company_id.id)
                    self._cr.execute(qry)
                    qry_dict = self._cr.dictfetchall()
                    if self.zero_amount_tax:
                        qry1 = """select null :: integer as id,am.id as move_id,am.date,ait.account_id,at.amount as amount,(COALESCE(ait.amount) + COALESCE(ait.amount_rounding,0)) as credit, 
                                            (COALESCE(ait.amount) + COALESCE(ait.amount_rounding,0)) as debit,0.0::numeric as amount_currency 
                                            from account_invoice ai 
                                            join account_invoice_tax ait on ait.invoice_id = ai.id  
                                            join account_move am on am.id = ai.move_id  
                                            join account_tax at on at.id = ait.tax_id 
                                            where (COALESCE(ait.amount) + COALESCE(ait.amount_rounding,0)) = 0 and ait.tax_id = %s and am.date BETWEEN '%s' 
                                            AND '%s' AND ait.company_id=%s""" % (tax.id, self.from_date, self.to_date, self.company_id.id)
                        self._cr.execute(qry1)
                        qry1_dict = self._cr.dictfetchall()
                        for x in qry1_dict:
                            qry_dict.append(x)
                    tax_type_name = tax.name
                    header = ['Date', 'Partner', 'Reference', 'Name', 'Account Name', 'Tax Rate', 'Amount',
                              'Tax Amount']
                    col = 0
                    if multi_currency:
                        header = ['Date', 'Partner', 'Reference', 'Name', 'Account Name', 'Tax Rate', 'Amount',
                                  'Tax Amount', 'Amount in Currency', 'Tax in Currency', 'Currency']
                    row, worksheet = self.with_context(multi_currency=multi_currency).print_header(qry_dict, header, worksheet, row, col, tax_type_name,
                                                       merge_header_format, headerforname, headerforother)

                    amt_tax = 0.0
                    amount_total = 0.0

                    if qry_dict == []:
                        # row += 1
                        worksheet.write(row, col, "Total", total_label_format)
                        worksheet.write(row, col + 1, "", total_format)
                        worksheet.write(row, col + 2, "", total_format)
                        worksheet.write(row, col + 3, "", total_format)
                        worksheet.write(row, col + 4, "", total_format)
                        worksheet.write(row, col + 5, "", total_format)
                        worksheet.write(row, col + 6, "", total_format)
                        worksheet.write(row, col + 7, "", total_format)
                        if multi_currency:
                            worksheet.write(row, col + 8, "", total_format)
                            worksheet.write(row, col + 9, "", total_format)
                            worksheet.write(row, col + 10, "", total_format)
                        row += 2
                        continue
                    for aml in qry_dict:
                        row += 1
                        col = 0
                        o_name = get_name(aml)
                        date = aml.get('date')
                        feeddate = datetime.strptime(date, '%Y-%m-%d').strftime('%m-%d-%Y')
                        worksheet.write(row, col, feeddate)
                        worksheet.set_column('A:A', 10)
                        worksheet.set_column('B:B', 13)
                        worksheet.set_column('C:C', 15)
                        worksheet.set_column('D:D', 35)
                        worksheet.set_column('E:E', 20)
                        worksheet.set_column('F:F', 10)
                        worksheet.set_column('G:G', 15)
                        worksheet.set_column('H:H', 15)
                        if multi_currency:
                            worksheet.set_column('I:I', 20)
                            worksheet.set_column('J:J', 15)
                            worksheet.set_column('K:K', 10)
                        p_name = get_partner(aml)
                        r_name = get_ref(aml)
                        account_name = self.env['account.account'].browse(aml.get('account_id')).name
                        amount = get_amount(aml)
                        balance = get_tax(aml)
                        worksheet.write(row, col + 1, p_name)
                        worksheet.write(row, col + 2, r_name)
                        worksheet.write(row, col + 3, o_name)
                        worksheet.write(row, col + 4, account_name)
                        worksheet.write(row, col + 5, str(aml.get('amount')) + '%')
                        worksheet.write(row, col + 6, round(amount, 2))
                        worksheet.write(row, col + 7, round(balance, 2))
                        if multi_currency:
                            amt_cur = get_amount_currency(aml, round(amount, 2))
                            amt_tax_cur = get_amount_tax_currency(aml, round(balance, 2))
                            worksheet.write(row, col + 8, amt_cur)
                            worksheet.write(row, col + 9, amt_tax_cur)
                            worksheet.write(row, col + 10, get_currency(aml))
                        amt_tax += balance
                        amount_total += amount
                    row += 1
                    worksheet.write(row, col, "Total", total_label_format)
                    worksheet.write(row, col + 1, "", total_format)
                    worksheet.write(row, col + 2, "", total_format)
                    worksheet.write(row, col + 3, "", total_format)
                    worksheet.write(row, col + 4, "", total_format)
                    worksheet.write(row, col + 5, "", total_format)
                    worksheet.write(row, col + 6, round(amount_total, 2), total_format)
                    worksheet.write(row, col + 7, round(amt_tax, 2), total_format)
                    if multi_currency:
                        worksheet.write(row, col + 8, "", total_format)
                        worksheet.write(row, col + 9, "", total_format)
                        worksheet.write(row, col + 10, "", total_format)
                    row += 2

            else:
                for tax in at_query:
                    tax_type_name = self.env['account.tax'].browse(tax.get('tax_line_id')).name

                    qry = """select aml.id,aml.date,aml.account_id,aml.credit,aml.debit,a.amount,aml.amount_currency from account_move_line  aml join account_tax a on a.id=aml.tax_line_id 
        where aml.tax_line_id=%s AND aml.date BETWEEN '%s' AND '%s' AND aml.company_id=%s""" % (
                    tax.get('tax_line_id'), self.from_date, self.to_date, self.company_id.id)
                    self._cr.execute(qry)
                    qry_dict = self._cr.dictfetchall()
                    if self.zero_amount_tax:
                        qry1 = """select null :: integer as id,am.id as move_id,am.date,ait.account_id,at.amount as amount,(COALESCE(ait.amount) + COALESCE(ait.amount_rounding,0)) as credit, 
                        (COALESCE(ait.amount) + COALESCE(ait.amount_rounding,0)) as debit,0.0::numeric as amount_currency 
                        from account_invoice ai
                        join account_invoice_tax ait on ait.invoice_id = ai.id
                        join account_move am on am.id = ai.move_id
                        join account_tax at on at.id = ait.tax_id
                        where (COALESCE(ait.amount) + COALESCE(ait.amount_rounding,0)) = 0 and ait.tax_id = %s and am.date BETWEEN '%s'
                        AND '%s' AND ait.company_id=%s"""% (tax.get('tax_line_id'),self.from_date, self.to_date, self.company_id.id)
                        self._cr.execute(qry1)
                        qry1_dict = self._cr.dictfetchall()
                        for x in qry1_dict:
                            qry_dict.append(x)
                    header = ['Date', 'Partner', 'Reference', 'Name', 'Account Name', 'Tax Rate', 'Amount',
                              'Tax Amount']
                    col = 0
                    if multi_currency:
                        header = ['Date', 'Partner', 'Reference', 'Name', 'Account Name', 'Tax Rate', 'Amount',
                                  'Tax Amount', 'Amount in Currency', 'Tax in Currency', 'Currency']
                    row, worksheet = self.with_context(multi_currency=multi_currency).print_header(qry_dict, header,
                                                                                                   worksheet, row, col,
                                                                                                   tax_type_name,
                                                                                                   merge_header_format,
                                                                                                   headerforname,
                                                                                                   headerforother)
                    amt_tax = 0.0
                    amount_total = 0.0

                    for aml in qry_dict:
                        row += 1
                        col = 0
                        o_name = get_name(aml)
                        date = aml.get('date')
                        feeddate = datetime.strptime(date, '%Y-%m-%d').strftime('%m-%d-%Y')
                        worksheet.write(row, col, feeddate)
                        worksheet.set_column('A:A', 10)
                        worksheet.set_column('B:B', 13)
                        worksheet.set_column('C:C', 15)
                        worksheet.set_column('D:D', 35)
                        worksheet.set_column('E:E', 20)
                        worksheet.set_column('F:F', 10)
                        worksheet.set_column('G:G', 15)
                        worksheet.set_column('H:H', 15)
                        if multi_currency:
                            worksheet.set_column('I:I', 20)
                            worksheet.set_column('J:J', 15)
                            worksheet.set_column('K:K', 10)
                        p_name = get_partner(aml)
                        worksheet.write(row, col + 1, p_name)
                        r_name = get_ref(aml)
                        worksheet.write(row, col + 2, r_name)
                        worksheet.write(row, col + 3, o_name)
                        account_name = self.env['account.account'].browse(aml.get('account_id')).name
                        worksheet.write(row, col + 4, account_name)
                        worksheet.write(row, col + 5, str(aml.get('amount')) + '%')
                        amount = get_amount(aml)
                        balance = get_tax(aml)
                        #                     final_amount=amount-balance
                        worksheet.write(row, col + 6, round(amount, 2))
                        #                     balance=aml.get('balance')
                        worksheet.write(row, col + 7, round(balance, 2))
                        if multi_currency:
                            amt_cur = get_amount_currency(aml, round(amount, 2))
                            amt_tax_cur = get_amount_tax_currency(aml, round(balance, 2))
                            worksheet.write(row, col + 8, amt_cur)
                            worksheet.write(row, col + 9, amt_tax_cur)
                            worksheet.write(row, col + 10, get_currency(aml))
                        amt_tax += balance
                        amount_total += amount
                    row += 1
                    worksheet.write(row, col, "Total", total_label_format)
                    worksheet.write(row, col + 1, "", total_format)
                    worksheet.write(row, col + 2, "", total_format)
                    worksheet.write(row, col + 3, "", total_format)
                    worksheet.write(row, col + 4, "", total_format)
                    worksheet.write(row, col + 5, "", total_format)
                    worksheet.write(row, col + 6, round(amount_total, 2), total_format)
                    worksheet.write(row, col + 7, round(amt_tax, 2), total_format)
                    if multi_currency:
                        worksheet.write(row, col + 8, "", total_format)
                        worksheet.write(row, col + 9, "", total_format)
                        worksheet.write(row, col + 10, "", total_format)
                    row += 2
        elif tax_or_group == 'group':
            if self.tax_group_ids:
                taxes = self.env['account.tax'].search([('tax_group_id', 'in', self.tax_group_ids.ids)])
                if taxes:
                    for tax in taxes:
                        qry = """select aml.id,aml.date,aml.account_id,aml.credit,aml.debit,a.amount,aml.amount_currency from account_move_line  aml join account_tax a on a.id=aml.tax_line_id 
            where aml.tax_line_id=%s AND aml.date BETWEEN '%s' AND '%s' AND aml.company_id=%s""" % (
                        tax.id, self.from_date, self.to_date, self.company_id.id)
                        self._cr.execute(qry)
                        qry_dict = self._cr.dictfetchall()
                        if self.zero_amount_tax:
                            qry1 = """select null :: integer as id,am.id as move_id,am.date,ait.account_id,at.amount as amount,(COALESCE(ait.amount) + COALESCE(ait.amount_rounding,0)) as credit, 
                                                                    (COALESCE(ait.amount) + COALESCE(ait.amount_rounding,0)) as debit,0.0::numeric as amount_currency 
                                                                    from account_invoice ai 
                                                                    join account_invoice_tax ait on ait.invoice_id = ai.id  
                                                                    join account_move am on am.id = ai.move_id  
                                                                    join account_tax at on at.id = ait.tax_id 
                                                                    where (COALESCE(ait.amount) + COALESCE(ait.amount_rounding,0)) = 0 and ait.tax_id = %s and am.date BETWEEN '%s' 
                                                                    AND '%s' AND ait.company_id=%s""" % (tax.id, self.from_date, self.to_date, self.company_id.id)
                            self._cr.execute(qry1)
                            qry1_dict = self._cr.dictfetchall()
                            for x in qry1_dict:
                                qry_dict.append(x)
                        tax_type_name = tax.name
                        if qry_dict == []:
                            continue

                        header = ['Date', 'Partner', 'Reference', 'Name', 'Account Name', 'Tax Rate', 'Amount',
                                  'Tax Amount']
                        col = 0
                        if multi_currency:
                            header = ['Date', 'Partner', 'Reference', 'Name', 'Account Name', 'Tax Rate', 'Amount',
                                      'Tax Amount', 'Amount in Currency', 'Tax in Currency', 'Currency']
                        row, worksheet = self.with_context(multi_currency=multi_currency).print_header(qry_dict, header,
                                                                                                       worksheet, row,
                                                                                                       col,
                                                                                                       tax_type_name,
                                                                                                       merge_header_format,
                                                                                                       headerforname,
                                                                                                       headerforother)

                        amt_tax = 0.0
                        amount_total = 0.0

                        for aml in qry_dict:
                            row += 1
                            col = 0
                            o_name = get_name(aml)
                            date = aml.get('date')
                            feeddate = datetime.strptime(date, '%Y-%m-%d').strftime('%m-%d-%Y')
                            worksheet.write(row, col, feeddate)
                            worksheet.set_column('A:A', 10)
                            worksheet.set_column('B:B', 13)
                            worksheet.set_column('C:C', 15)
                            worksheet.set_column('D:D', 35)
                            worksheet.set_column('E:E', 20)
                            worksheet.set_column('F:F', 10)
                            worksheet.set_column('G:G', 15)
                            worksheet.set_column('H:H', 15)
                            if multi_currency:
                                worksheet.set_column('I:I', 20)
                                worksheet.set_column('J:J', 15)
                                worksheet.set_column('K:K', 10)
                            p_name = get_partner(aml)
                            r_name = get_ref(aml)
                            account_name = self.env['account.account'].browse(aml.get('account_id')).name
                            amount = get_amount(aml)
                            balance = get_tax(aml)
                            worksheet.write(row, col + 1, p_name)
                            worksheet.write(row, col + 2, r_name)
                            worksheet.write(row, col + 3, o_name)
                            worksheet.write(row, col + 4, account_name)
                            worksheet.write(row, col + 5, str(aml.get('amount')) + '%')
                            worksheet.write(row, col + 6, round(amount, 2))
                            worksheet.write(row, col + 7, round(balance, 2))
                            if multi_currency:
                                amt_cur = get_amount_currency(aml, round(amount, 2))
                                amt_tax_cur = get_amount_tax_currency(aml, round(balance, 2))
                                worksheet.write(row, col + 8, amt_cur)
                                worksheet.write(row, col + 9, amt_tax_cur)
                                worksheet.write(row, col + 10, get_currency(aml))
                            amt_tax += balance
                            amount_total += amount
                        row += 1
                        worksheet.write(row, col, "Total", total_label_format)
                        worksheet.write(row, col + 1, "", total_format)
                        worksheet.write(row, col + 2, "", total_format)
                        worksheet.write(row, col + 3, "", total_format)
                        worksheet.write(row, col + 4, "", total_format)
                        worksheet.write(row, col + 5, "", total_format)
                        worksheet.write(row, col + 6, round(amount_total, 2), total_format)
                        worksheet.write(row, col + 7, round(amt_tax, 2), total_format)
                        if multi_currency:
                            worksheet.write(row, col + 8, "", total_format)
                            worksheet.write(row, col + 9, "", total_format)
                            worksheet.write(row, col + 10, "", total_format)

                        row += 2
            else:
                self._cr.execute("""select distinct tax_line_id as id from account_move_line 
        where tax_line_id in (select id from account_tax where tax_group_id in (select id from account_tax_group))
        and date BETWEEN '%s' AND '%s' AND company_id=%s and tax_line_id is not null""" % (
                self.from_date, self.to_date, self.company_id.id))
                grp_taxes = self._cr.fetchall()
                if self.zero_amount_tax:
                    self._cr.execute("""select distinct ait.tax_id as id from account_invoice ai join account_invoice_tax ait on ait.invoice_id = ai.id
                    join account_move am on am.id = ai.move_id
                    where (COALESCE(ait.amount) + COALESCE(ait.amount_rounding,0)) = 0 and ait.tax_id in (select id from account_tax where tax_group_id in (select id from account_tax_group))
                    and am.date BETWEEN '%s' AND '%s' and ait.company_id=%s"""%(self.from_date, self.to_date, self.company_id.id))
                    grp1_taxes = self._cr.fetchall()
                    for grp1 in grp1_taxes:
                        grp_taxes.append(grp1)
                for tax in grp_taxes:
                    tax_type_name = self.env['account.tax'].browse(tax[0]).name
                    #                 worksheet.write_merge(row,row,0,6,tax_type_name,header_bold)
                    #                 row+=1
                    #                 header=['Date','Partner','Reference','Name','Account Name','Amount','Tax Amount']
                    #                 col=0
                    #                 row,worksheet=self.print_header(header,worksheet,row,col,tax_type_name,merge_header_format,headerforname,headerforother)

                    qry = """select aml.id,aml.date,aml.account_id,aml.credit,aml.debit,a.amount,aml.amount_currency from account_move_line  aml join account_tax a on a.id=aml.tax_line_id 
        where aml.tax_line_id=%s AND aml.date BETWEEN '%s' AND '%s' AND aml.company_id=%s""" % (
                        tax[0], self.from_date, self.to_date, self.company_id.id)
                    self._cr.execute(qry)
                    qry_dict = self._cr.dictfetchall()
                    if self.zero_amount_tax:
                        qry1 = """select null :: integer as am.id,am.date,ait.account_id,at.amount as amount,(COALESCE(ait.amount) + COALESCE(ait.amount_rounding,0)) as credit, 
                                            (COALESCE(ait.amount) + COALESCE(ait.amount_rounding,0)) as debit, 0.0 :: numeric  as amount_currency 
                                            from account_invoice ai 
                                            join account_invoice_tax ait on ait.invoice_id = ai.id  
                                            join account_move am on am.id = ai.move_id  
                                            join account_tax at on at.id = ait.tax_id 
                                            where (COALESCE(ait.amount) + COALESCE(ait.amount_rounding,0)) = 0 and ait.tax_id = %s and am.date BETWEEN '%s' 
                                            AND '%s' AND ait.company_id=%s and """ % (tax[0],self.from_date, self.to_date, self.company_id.id)
                        self._cr.execute(qry1)
                        qry1_dict = self._cr.dictfetchall()
                        for x in qry1_dict:
                            qry_dict.append(x)
                    if qry_dict == []:
                        continue

                    header = ['Date', 'Partner', 'Reference', 'Name', 'Account Name', 'Tax Rate', 'Amount',
                              'Tax Amount']
                    col = 0
                    if multi_currency:
                        header = ['Date', 'Partner', 'Reference', 'Name', 'Account Name', 'Tax Rate', 'Amount',
                                  'Tax Amount', 'Amount in Currency', 'Tax in Currency', 'Currency']
                    row, worksheet = self.with_context(multi_currency=multi_currency).print_header(qry_dict, header,
                                                                                                   worksheet, row, col,
                                                                                                   tax_type_name,
                                                                                                   merge_header_format,
                                                                                                   headerforname,
                                                                                                   headerforother)

                    amt_tax = 0.0
                    amount_total = 0.0

                    for aml in qry_dict:
                        row += 1
                        col = 0
                        o_name = get_name(aml)
                        date = aml.get('date')
                        feeddate = datetime.strptime(date, '%Y-%m-%d').strftime('%m-%d-%Y')
                        worksheet.write(row, col, feeddate)
                        worksheet.set_column('A:A', 10)
                        worksheet.set_column('B:B', 13)
                        worksheet.set_column('C:C', 15)
                        worksheet.set_column('D:D', 35)
                        worksheet.set_column('E:E', 20)
                        worksheet.set_column('F:F', 10)
                        worksheet.set_column('G:G', 15)
                        worksheet.set_column('H:H', 15)
                        if multi_currency:
                            worksheet.set_column('I:I', 20)
                            worksheet.set_column('J:J', 15)
                            worksheet.set_column('K:K', 10)
                        p_name = get_partner(aml)
                        worksheet.write(row, col + 1, p_name)
                        r_name = get_ref(aml)
                        worksheet.write(row, col + 2, r_name)
                        worksheet.write(row, col + 3, o_name)
                        account_name = self.env['account.account'].browse(aml.get('account_id')).name
                        worksheet.write(row, col + 4, account_name)
                        worksheet.write(row, col + 5, str(aml.get('amount')) + '%')
                        amount = get_amount(aml)
                        balance = get_tax(aml)
                        #                     final_amount=amount-balance
                        worksheet.write(row, col + 6, round(amount, 2))
                        #                     balance=aml.get('balance')
                        worksheet.write(row, col + 7, round(balance, 2))
                        if multi_currency:
                            amt_cur = get_amount_currency(aml, round(amount, 2))
                            amt_tax_cur = get_amount_tax_currency(aml, round(balance, 2))
                            worksheet.write(row, col + 8, amt_cur)
                            worksheet.write(row, col + 9, amt_tax_cur)
                            worksheet.write(row, col + 10, get_currency(aml))
                        amt_tax += balance
                        amount_total += amount
                    row += 1
                    worksheet.write(row, col, "Total", total_label_format)
                    worksheet.write(row, col + 1, "", total_format)
                    worksheet.write(row, col + 2, "", total_format)
                    worksheet.write(row, col + 3, "", total_format)
                    worksheet.write(row, col + 4, "", total_format)
                    worksheet.write(row, col + 5, "", total_format)
                    worksheet.write(row, col + 6, round(amount_total, 2), total_format)
                    worksheet.write(row, col + 7, round(amt_tax, 2), total_format)
                    if multi_currency:
                        worksheet.write(row, col + 8, "", total_format)
                        worksheet.write(row, col + 9, "", total_format)
                        worksheet.write(row, col + 10, "", total_format)
                    row += 2
        workbook.close()
        file = open(created_file_path, 'rb')
        report_data_file = base64.encodestring(file.read())
        file.close()
        self.write({'datas': report_data_file})
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/binary/download_document?model=account.tax.report&field=datas&id=%s&filename=Account Tax Report from %s to %s.xlsx' % (
                self.id, self.from_date, self.to_date),
            'target': 'self',
            #              'type': 'ir.actions.act_window_close'
        }

    @api.multi
    def get_account_tax_report_summary(self):

        workbook = xlwt.Workbook()
        borders = Borders()
        worksheet = workbook.add_sheet("Account Tax Report")
        header_bold = xlwt.easyxf("font: bold on, height 220;alignment:horizontal center")
        headerforname = xlwt.easyxf("font: bold on, height 210; alignment:horizontal right")
        headerforother = xlwt.easyxf("font: bold on, height 210;alignment:horizontal left")
        Total_bold = xlwt.easyxf("font: bold on, height 200; pattern: pattern solid; alignment:horizontal right")
        Total_pos = xlwt.easyxf("font: bold on, height 200; pattern: pattern solid; alignment:horizontal left")
        fromdate = datetime.strptime(self.from_date, '%Y-%m-%d').strftime('%m-%d-%Y')
        todate = datetime.strptime(self.to_date, '%Y-%m-%d').strftime('%m-%d-%Y')
        title = "Tax Summary From %s To %s" % (fromdate, todate)
        worksheet.write_merge(0, 1, 0, 2, title, header_bold)
        company_name = "Company : " + self.company_id.name
        worksheet.write_merge(2, 2, 0, 2, company_name, headerforother)
        if self.company_id.vat:
            company_vat = "Vat : " + self.company_id.vat
            worksheet.write_merge(3, 3, 0, 2, company_vat, headerforother)
        tax_or_group = self.tax_or_group

        def get_summary_taxamount(qry_dict):
            credit = 0
            debit = 0
            taxamount = 0
            for aml in qry_dict:
                credit = aml.get('credit')
                debit = aml.get('debit')
                taxamount += (debit - credit)

            return taxamount

        def get_amount(qry_dict):
            credit = 0
            debit = 0
            amount = 0
            for aml in qry_dict:
                if aml.get('id',False):
                    id = aml.get('id')
                    t_credit = 0
                    t_debit = 0
                    move_amount = self.env['account.move.line'].browse(id)
                    line_amount = 0.0
                    for line in move_amount.move_id.line_ids:
                        if move_amount.tax_line_id in line.tax_ids:
                            if not line.tax_line_id:
                                t_credit = t_credit + line.credit
                                t_debit = t_debit + line.debit

                        elif not move_amount.tax_line_id in line.tax_ids:
                            account_taxes = self.env['account.tax'].search(
                                [('children_tax_ids', 'in', move_amount.tax_line_id.id)])
                            for account_tax in account_taxes:
                                if account_tax in line.tax_ids:
                                    if not line.tax_line_id:
                                        t_credit = t_credit + line.credit
                                        t_debit = t_debit + line.debit
                        line_amount = t_debit - t_credit
                    amount += line_amount
                else:
                    if self.zero_amount_tax:
                        if aml.get('move_id'):
                            move_id = self.env['account.move'].browse(aml.get('move_id'))
                            tax_lines = move_id.line_ids[0].invoice_id.tax_line_ids.filtered(lambda x : x.amount_total == 0)
                            for tax_line in tax_lines:
                                if tax_lines and tax_lines[0].invoice_id.type in ('out_invoice', 'in_refund'):
                                    to_currency = self.env.user.company_id.currency_id
                                    from_currency = tax_line.currency_id
                                    compute_currency = from_currency.compute(abs(tax_line.base), to_currency)
                                    amount += (compute_currency) * -1
                                else:
                                    to_currency = self.env.user.company_id.currency_id
                                    from_currency = tax_line.currency_id
                                    compute_currency = from_currency.compute(abs(tax_line.base), to_currency)
                                    amount += compute_currency


                                # if tax_line.invoice_id.type in ('out_invoice', 'in_refund'):
                                #     amount += (tax_line.base) * -1
                                # else:
                                #     amount += tax_line.base
                                # amount = aml.get('debit') - aml.get('credit')
            return amount

        row = 5
        col = 0

        tax_type_qry = """select distinct type_tax_use from account_tax"""
        self._cr.execute(tax_type_qry)
        tax_query = self._cr.dictfetchall()
        # Tax wise separation
        for tax_type in tax_query:

            set_tax = tax_type.get('type_tax_use')
            capital_sale = 'Sale Tax'
            capital_purchase = 'Purchase Tax'

            if set_tax == 'sale':
                worksheet.write_merge(row, row, 0, 2, capital_sale, header_bold)
            elif set_tax == 'purchase':
                worksheet.write_merge(row, row, 0, 2, capital_purchase, header_bold)
            else:
                worksheet.write_merge(row, row, 0, 2, 'None Type Tax', header_bold)

            header = ['Tax', 'Amount', 'Tax Amount']
            row += 1
            col = 0
            for t in header:
                if t in ['Amount', 'Tax Amount']:
                    worksheet.write(row, col, t, headerforname)
                else:
                    worksheet.write(row, col, t, headerforother)
                col += 1
            row += 1
            am = 0
            tax_am = 0
            if tax_or_group == 'tax':
                # if set_tax=='sale':
                #     worksheet.write_merge(row, row, 0, 2, capital_sale, header_bold)
                #     header = ['Tax', 'Amount', 'Tax Amount']
                #     row += 1
                #     col = 0
                #     for t in header:
                #         if t in ['Amount', 'Tax Amount']:
                #             worksheet.write(row, col, t, headerforname)
                #         else:
                #             worksheet.write(row, col, t, headerforother)
                #         col += 1
                #     row += 1
            # process if condition if user select particular tax in wizard otherwise generate the report that includes all taxes
                if self.tax_ids:
                    taxes = self.env['account.tax'].search(
                        [('id', 'in', self.tax_ids.ids), ('type_tax_use', '=', set_tax)])
                    for tax in taxes:
                        if tax.type_tax_use == set_tax:

                            qry = """select id,credit,debit from account_move_line where tax_line_id=%s AND date BETWEEN '%s' AND '%s' AND company_id=%s""" % (
                            tax.id, self.from_date, self.to_date, self.company_id.id)
                            self._cr.execute(qry)
                            qry_dict = self._cr.dictfetchall()
                            if self.zero_amount_tax:
                                self._cr.execute("""select null::integer as id, am.id as move_id,(COALESCE(ait.amount) + COALESCE(ait.amount_rounding,0)) as credit, (COALESCE(ait.amount) + COALESCE(ait.amount_rounding,0)) as debit from account_invoice ai 
                                join account_invoice_tax ait on ait.invoice_id = ai.id
                                join account_move am on am.id = ai.move_id
                                where (COALESCE(ait.amount) + COALESCE(ait.amount_rounding,0)) = 0  and ait.tax_id = %s and am.date BETWEEN '%s' AND '%s' and ait.company_id = %s"""
                                % (tax.id, self.from_date, self.to_date, self.company_id.id))
                                qry1_dict = self._cr.dictfetchall()
                                for x in qry1_dict:
                                    qry_dict.append(x)
                            tax_type_name = tax.name
                            col = 0
                            worksheet.write(row, col, tax_type_name)
                            worksheet.col(0).width = 7500
                            worksheet.col(1).width = 3500
                            worksheet.col(2).width = 3500
                            # call method for getting total sum of balance
                            amount = get_amount(qry_dict)
                            worksheet.write(row, col + 1, round(amount, 2))
                            am = am + amount
                            # call method for getting total sum of taxes
                            taxamount = get_summary_taxamount(qry_dict)
                            worksheet.write(row, col + 2, round(taxamount, 2))
                            tax_am = tax_am + taxamount

                            row += 1
                        else:
                            continue
                    else:
                        col = 0
                        worksheet.write(row, col, "Total", Total_pos)
                        worksheet.write(row, col + 1, round(am, 2), Total_bold)
                        worksheet.write(row, col + 2, round(tax_am, 2), Total_bold)
                        row += 2

                else:
                    if self.zero_amount_tax:
                        at_qry = """select distinct tax_line_id from (select distinct tax_line_id from account_move_line  aml join account_tax at on at.id=aml.tax_line_id
                                    where aml.date BETWEEN '%s' AND '%s' AND aml.company_id=%s and aml.tax_line_id is not null
                                    and at.type_tax_use='%s'
                                    union all 
                                    select distinct ait.tax_id as tax_line_id from account_invoice ai join account_invoice_tax ait on ait.invoice_id = ai.id
                                    join account_move am on am.id = ai.move_id
                                    join account_tax at on at.id = ait.tax_id 
                                    where (COALESCE(ait.amount) + COALESCE(ait.amount_rounding,0)) = 0 and am.date BETWEEN '%s' AND '%s' AND ait.company_id=%s
                                    and at.type_tax_use='%s')tmp""" % (self.from_date, self.to_date, self.company_id.id, set_tax,self.from_date, self.to_date, self.company_id.id, set_tax)
                    else:
                        at_qry = """select distinct tax_line_id from account_move_line  aml join account_tax at on at.id=aml.tax_line_id
                                    where aml.date BETWEEN '%s' AND '%s' AND aml.company_id=%s and aml.tax_line_id is not null
                                    and at.type_tax_use='%s'"""%(self.from_date, self.to_date, self.company_id.id, set_tax)
                    self._cr.execute(at_qry)
                    at_query = self._cr.dictfetchall()

                    for tax in at_query:
                        tax_type_use = self.env['account.tax'].browse(tax.get('tax_line_id')).type_tax_use
                        if tax_type_use == set_tax:

                            tax_type_name = self.env['account.tax'].browse(tax.get('tax_line_id')).name
                            col = 0
                            worksheet.write(row, col, tax_type_name)

                            qry = """select id,credit,debit from account_move_line where tax_line_id=%s AND date BETWEEN '%s' AND '%s' AND company_id=%s""" % (
                            tax.get('tax_line_id'), self.from_date, self.to_date, self.company_id.id)
                            self._cr.execute(qry)
                            qry_dict = self._cr.dictfetchall()
                            if self.zero_amount_tax:
                                self._cr.execute("""select null::integer as id, am.id as move_id,(COALESCE(ait.amount) + COALESCE(ait.amount_rounding,0)) as debit,(COALESCE(ait.amount) + COALESCE(ait.amount_rounding,0)) as credit
                                from account_invoice ai join account_invoice_tax ait on ait.invoice_id = ai.id
                                join account_move am on am.id = ai.move_id 
                                where (COALESCE(ait.amount) + COALESCE(ait.amount_rounding,0)) = 0 and 
                                ait.tax_id=%s AND am.date BETWEEN '%s' AND '%s' AND ait.company_id=%s"""% (tax.get('tax_line_id'), self.from_date, self.to_date, self.company_id.id))
                                qry1_dict = self._cr.dictfetchall()
                                for x in qry1_dict:
                                    qry_dict.append(x)
                            worksheet.col(0).width = 7500
                            worksheet.col(1).width = 3500
                            worksheet.col(2).width = 3500
                            # call method for getting total sum of balance
                            amount = get_amount(qry_dict)
                            worksheet.write(row, col + 1, round(amount, 2))
                            am = am + amount
                            # call method for getting total sum of taxes
                            taxamount = get_summary_taxamount(qry_dict)
                            worksheet.write(row, col + 2, round(taxamount, 2))
                            tax_am = tax_am + taxamount
                            row += 1
                        else:
                            continue
                    else:
                        col = 0
                        worksheet.write(row, col, "Total", Total_pos)
                        worksheet.write(row, col + 1, round(am, 2), Total_bold)
                        worksheet.write(row, col + 2, round(tax_am, 2), Total_bold)
                        row += 2

            elif tax_or_group == 'group':
                if self.tax_group_ids:
                    taxes = self.env['account.tax'].search([('tax_group_id', 'in', self.tax_group_ids.ids), ('type_tax_use', '=', set_tax)])
                    for tax in taxes:
                        if tax.type_tax_use == set_tax:
                            qry = """select id,credit,debit from account_move_line where tax_line_id=%s AND date BETWEEN '%s' AND '%s' AND company_id=%s""" % (tax.id, self.from_date, self.to_date, self.company_id.id)
                            self._cr.execute(qry)
                            qry_dict = self._cr.dictfetchall()
                            if self.zero_amount_tax:
                                self._cr.execute("""select null::integer as id,(COALESCE(ait.amount) + COALESCE(ait.amount_rounding,0)) as credit, (COALESCE(ait.amount) + COALESCE(ait.amount_rounding,0)) as debit from account_invoice ai 
                                join account_invoice_tax ait on ait.invoice_id = ai.id 
                                join account_move am on am.id = ai.move_id
                                where (COALESCE(ait.amount) + COALESCE(ait.amount_rounding,0)) = 0 and
                                ait.tax_id=%s AND am.date BETWEEN '%s' AND '%s' AND ait.company_id=%s"""% (tax.id, self.from_date, self.to_date, self.company_id.id))
                                qry1_dict = self._cr.dictfetchall()
                                for x in qry1_dict:
                                    qry_dict.append(x)
                            tax_type_name = tax.name
                            col = 0
                            worksheet.write(row, col, tax_type_name)
                            worksheet.col(0).width = 7500
                            worksheet.col(1).width = 3500
                            worksheet.col(2).width = 3500
                            # call method for getting total sum of balance
                            amount = get_amount(qry_dict)
                            worksheet.write(row, col + 1, round(amount, 2))
                            am = am + amount
                            # call method for getting total sum of taxes
                            taxamount = get_summary_taxamount(qry_dict)
                            worksheet.write(row, col + 2, round(taxamount, 2))
                            tax_am = tax_am + taxamount

                            row += 1
                        else:
                            continue
                    else:
                        col = 0
                        worksheet.write(row, col, "Total", Total_pos)
                        worksheet.write(row, col + 1, round(am, 2), Total_bold)
                        worksheet.write(row, col + 2, round(tax_am, 2), Total_bold)
                        row += 2
                else:
                    self._cr.execute(
                        """select id from account_tax where tax_group_id in (select id from account_tax_group) and type_tax_use='%s'""" % (
                            set_tax))
                    grp_taxes = self._cr.fetchall()
                    for tax in grp_taxes:
                        tax_type_use = self.env['account.tax'].browse(tax[0]).type_tax_use
                        if tax_type_use == set_tax:

                            tax_type_name = self.env['account.tax'].browse(tax[0]).name
                            col = 0
                            worksheet.write(row, col, tax_type_name)

                            qry = """select id,credit,debit from account_move_line where tax_line_id=%s AND date BETWEEN '%s' AND '%s' AND company_id=%s""" % (
                                tax[0], self.from_date, self.to_date, self.company_id.id)
                            self._cr.execute(qry)
                            qry_dict = self._cr.dictfetchall()
                            if self.zero_amount_tax:
                                self._cr.execute("""select null::integer as id,(COALESCE(ait.amount) + COALESCE(ait.amount_rounding,0)) as credit,(COALESCE(ait.amount) + COALESCE(ait.amount_rounding,0)) as debit from account_invoice ai 
                                join account_invoice_tax ait on ait.invoice_id = ai.id
                                join account_move am on am.id = ai.move_id 
                                where (COALESCE(ait.amount) + COALESCE(ait.amount_rounding,0)) = 0 and
                                ait.tax_id=%s AND am.date BETWEEN '%s' AND '%s' AND ait.company_id=%s"""%(tax[0], self.from_date, self.to_date, self.company_id.id))
                                qry1_dict = self._cr.dictfetchall()
                                for x in qry1_dict:
                                    qry_dict.append(x)
                            worksheet.col(0).width = 7500
                            worksheet.col(1).width = 3500
                            worksheet.col(2).width = 3500
                            # call method for getting total sum of balance
                            amount = get_amount(qry_dict)
                            worksheet.write(row, col + 1, round(amount, 2))
                            am = am + amount
                            # call method for getting total sum of taxes
                            taxamount = get_summary_taxamount(qry_dict)
                            worksheet.write(row, col + 2, round(taxamount, 2))
                            tax_am = tax_am + taxamount
                            row += 1
                        else:
                            continue
                    else:
                        col = 0
                        worksheet.write(row, col, "Total", Total_pos)
                        worksheet.write(row, col + 1, round(am, 2), Total_bold)
                        worksheet.write(row, col + 2, round(tax_am, 2), Total_bold)
                        row += 2
        fp = BytesIO()
        workbook.save(fp)
        fp.seek(0)
        report_data_file = base64.encodestring(fp.read())
        fp.close()
        self.write({'datas': report_data_file})
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/binary/download_document?model=account.tax.report&field=datas&id=%s&filename=Account Summary Report from %s to %s.xls' % (
            self.id, self.from_date, self.to_date),
            'target': 'self',
        }
