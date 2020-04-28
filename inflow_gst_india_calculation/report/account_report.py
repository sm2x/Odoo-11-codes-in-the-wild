# -*- coding: utf-8 -*-
# Odoo, Open Source GST Indian Compliance.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).#
                                                             
import time
from odoo import api, models


#  reports for stock
class ReportAccountreport(models.AbstractModel):
    _name = 'report.account.report_invoice'
    
    
    @api.multi
    def _get_val(self, data):
        gst_val = {}
        if data:
            for inv in data:
                gst_val[inv.id]={'cgst_amount':0.0 ,'sgst_amount':0.0 }
                cgst_amount = sgst_amount = 0.0
                for line in inv.invoice_line_ids:
                    if line.invoice_line_tax_ids:
                        for tax in line.invoice_line_tax_ids:
                            if tax.children_tax_ids:
                                for child in tax.children_tax_ids:
                                    if child.tax_group_id.name == 'CGST':
                                        tax_amt = (child.amount * line.price_subtotal) / 100
                                        cgst_amount += tax_amt
                                    if child.tax_group_id.name == 'SGST':
                                        tax_amt = (child.amount * line.price_subtotal) / 100
                                        sgst_amount += tax_amt
                    gst_val.update({ inv.id: {'cgst_amount':cgst_amount, 'sgst_amount':sgst_amount  }})
        return gst_val
    
    @api.multi
    def _get_igst_val(self, data):
        igst_amount = {}
        if data:
            for inv in data:
                igst_amount[inv.id] = 0.0
                for line in inv.invoice_line_ids:
                    if line.invoice_line_tax_ids:
                        for tax in line.invoice_line_tax_ids:
                            if tax.tax_group_id.name == 'IGST':
                                igst_amount[inv.id]= inv.amount_tax
        return igst_amount
    
    @api.multi
    def get_report_values(self, docids, data=None):
        self.model = self.env['account.invoice']
        gst_val = {}
        igst_val = {}
        docs = self.model.browse(docids)
        if docs:
            gst_val = self._get_val(docs)
            igst_val=self._get_igst_val(docs)
        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'docs': docs,
            'time': time,
            'data': data,
            'gst_val':gst_val,
            'igst_val': igst_val,
        }
        return docargs
    
class ReportkAccountduplicatereport(models.AbstractModel):
    _name = 'report.account.account_invoice_report_duplicate_main'
    
    
    @api.multi
    def _get_val(self, data):
        gst_val = {}
        cgst_amount = sgst_amount = 0.0  
        if data:
            for inv in data:
                gst_val[inv.id]={'cgst_amount':0.0 ,'sgst_amount':0.0 }
                for line in inv.invoice_line_ids:
                    if line.invoice_line_tax_ids:
                        for tax in line.invoice_line_tax_ids:
                            if tax.children_tax_ids:
                                for child in tax.children_tax_ids:
                                    if child.tax_group_id.name == 'CGST':
                                        tax_amt = (child.amount * line.price_subtotal) / 100
                                        cgst_amount += tax_amt
                                    if child.tax_group_id.name == 'SGST':
                                        tax_amt = (child.amount * line.price_subtotal) / 100
                                        sgst_amount += tax_amt
                    gst_val.update({ inv.id: {'cgst_amount':cgst_amount, 'sgst_amount':sgst_amount  }})
        return gst_val
        
    @api.multi
    def _get_igst_val(self, data):
        igst_amount = {}
        if data:
            for inv in data:
                igst_amount[inv.id] = 0.0
                for line in inv.invoice_line_ids:
                    if line.invoice_line_tax_ids:
                        for tax in line.invoice_line_tax_ids:
                            if tax.tax_group_id.name == 'IGST':
                                igst_amount[inv.id]= inv.amount_tax
        return igst_amount
    
    @api.multi
    def get_report_values(self, docids, data=None):
        self.model = self.env['account.invoice']
        gst_val = {}
        igst_val = {}
        docs = self.model.browse(docids)
        for sale in docs:
            gst_val = self._get_val(sale)
            igst_val = self._get_igst_val(sale)
            total = self._get_TOTAL(sale)
        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'docs': docs,
            'time': time,
            'data': data,
            'gst_val':gst_val,
            'igst_val': igst_val,
        }
        return docargs
