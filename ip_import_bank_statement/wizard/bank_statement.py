# -*- coding: utf-8 -*-
import binascii
import logging
import tempfile
import xlrd
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import UserError
from odoo import models, fields, api, _
_logger = logging.getLogger(__name__)


class ImportAccountBankStatement(models.TransientModel):
    _name = "import.account.bank.statement"

    file = fields.Binary(string='Excel File', required=True)
    import_option = fields.Selection([('sbi', 'SBI'), ('hdfc', 'HDFC')], string='Bank', default='sbi')

    @api.multi
    def create_bank_statement(self, values):
        self.env['account.bank.statement.line'].create({
            'name': values.get('memo'),
            'statement_id': self._context.get('active_id'),
            'ref': values.get('ref'),
            'amount': values.get('amount'),
            'date': values.get('date')
        })

    @api.multi
    def import_bank_statements(self):
        statement_id = self.env['account.bank.statement'].browse([self._context.get('active_id')])
        if self.import_option == 'hdfc':
            fx = tempfile.NamedTemporaryFile(suffix=".xls")
            fx.write(binascii.a2b_base64(self.file))
            fx.seek(21)
            values = {}
            try:
                workbook = xlrd.open_workbook(fx.name)
            except Exception:
                raise UserError(_("Please check file, may be not in Proper Excel Formate, Please check !"))
            sheet = workbook.sheet_by_index(0)
            for row_no in range(22, sheet.nrows - 18):
                bank_statement_line = list(map(lambda row: str(row.value), sheet.row(row_no)))
                statment_date = bank_statement_line[0].split('/')
                date = '20'+str(statment_date[2]+'-'+statment_date[1]+'-'+statment_date[0])
                string_dt = datetime.strptime(date, DEFAULT_SERVER_DATE_FORMAT)
                if bank_statement_line[4]:
                    amount = - float(bank_statement_line[4])
                else:
                    amount = float(bank_statement_line[5])
                values.update({
                        'date': string_dt,
                        'memo': bank_statement_line[1],
                        'ref': bank_statement_line[2],
                        'amount': amount,
                        })
                res = self.create_bank_statement(values)
            balance_row = list(map(lambda row: str(row.value), sheet.row(sheet.nrows - 12)))
            statement_id.balance_start = float(balance_row[0])
            statement_id.balance_end_real = float(balance_row[6])
            return res
        else:
            fx = tempfile.NamedTemporaryFile(suffix=".xls")
            fx.write(binascii.a2b_base64(self.file))
            fx.seek(21)
            values = {}
            try:
                workbook = xlrd.open_workbook(fx.name)
            except Exception:
                raise UserError(_("Please check file, may be not in Proper Excel Formate, Please check !"))
            sheet = workbook.sheet_by_index(0)
            for row_no in range(21, sheet.nrows - 2):
                bank_statement_line = list(map(lambda row: str(row.value), sheet.row(row_no)))
                statment_date = bank_statement_line[0].split('/')
                date = str(statment_date[2]+'-'+statment_date[1]+'-'+statment_date[0])
                string_dt = datetime.strptime(date, DEFAULT_SERVER_DATE_FORMAT)
                if bank_statement_line[5].strip() != '':
                    amount = - float(bank_statement_line[5])
                else:
                    amount = float(bank_statement_line[6])
                values.update({
                        'date': string_dt,
                        'memo': bank_statement_line[2],
                        'ref': bank_statement_line[3],
                        'amount': amount,
                        })
                res = self.create_bank_statement(values)
            starting_balance_row = list(map(lambda row: str(row.value), sheet.row(17)))
            statement_id.balance_start = float(starting_balance_row[1])
            ending_balance_row = list(map(lambda row: str(row.value), sheet.row(sheet.nrows - 3)))
            statement_id.balance_end_real = float(ending_balance_row[7])
            return res
