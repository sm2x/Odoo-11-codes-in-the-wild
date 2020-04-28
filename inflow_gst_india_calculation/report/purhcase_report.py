# -*- coding: utf-8 -*-
# Odoo, Open Source GST Indian Compliance.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).#
                                                             
import time
from odoo import api, models

class Purchasereport(models.AbstractModel):
    _name = 'report.purchase.report_purchaseorder'
    
    
    @api.multi
    def _get_val(self, data):
        gst_val = {}
        if data:
            for purchase in data:
                gst_val[purchase.id]={'cgst_amount':0.0 ,'sgst_amount':0.0 }
                cgst_amount = sgst_amount = 0.0
                for line in purchase.order_line:
                    if line.taxes_id:
                        for tax in line.taxes_id:
                            if tax.children_tax_ids:
                                for child in tax.children_tax_ids:
                                    if child.tax_group_id.name == 'CGST':
                                        tax_amt = (child.amount * line.price_subtotal) / 100
                                        cgst_amount += tax_amt
                                    if child.tax_group_id.name == 'SGST':
                                        tax_amt = (child.amount * line.price_subtotal) / 100
                                        sgst_amount += tax_amt
                    gst_val.update({ purchase.id: {'cgst_amount':cgst_amount, 'sgst_amount':sgst_amount  }})
        return gst_val
    
        
    @api.multi
    def _get_igst_val(self, data):
        igst_amount = {}
        if data:
            for purchase in data:
                igst_amount[purchase.id] = 0.0
                for line in purchase.order_line:
                    if line.taxes_id:
                        for tax in line.taxes_id:
                            if tax.tax_group_id.name == 'IGST':
                                igst_amount[purchase.id]= purchase.amount_tax
        return igst_amount
    
    @api.multi
    def get_report_values(self, docids, data=None):
        self.model = self.env['purchase.order']
        gst_val = {}
        igst_val = {}
        docs = self.model.browse(docids)
        if docs:
            gst_val = self._get_val(docs)
            igst_val = self._get_igst_val(docs)
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
    
class quatation(models.AbstractModel):
    _name = 'report.purchase.report_purchasequotation'
    
    
    @api.multi
    def _get_val(self, data):
        gst_val = {}
        if data:
            for purchase in data:
                cgst_amount = sgst_amount = 0.0
                for line in purchase.order_line:
                    if line.taxes_id:
                        for tax in line.taxes_id:
                            if tax.children_tax_ids:
                                for child in tax.children_tax_ids:
                                    if child.tax_group_id.name == 'CGST':
                                        tax_amt = (child.amount * line.price_subtotal) / 100
                                        cgst_amount += tax_amt
                                    if child.tax_group_id.name == 'SGST':
                                        tax_amt = (child.amount * line.price_subtotal) / 100
                                        sgst_amount += tax_amt
                    gst_val.update({ purchase.id: {'cgst_amount':cgst_amount, 'sgst_amount':sgst_amount  }})
        return gst_val
    
        
    @api.multi
    def _get_igst_val(self, data):
        igst_amount = {}
        if data:
            for purchase in data:
                igst_amount[purchase.id] = 0.0
                for line in purchase.order_line:
                    if line.taxes_id:
                        for tax in line.taxes_id:
                            if tax.tax_group_id.name == 'IGST':
                                igst_amount[purchase.id]= purchase.amount_tax
        return igst_amount
    
    @api.multi
    def get_report_values(self, docids, data=None):
        self.model = self.env['purchase.order']
        gst_val = {}
        igst_val = {}
        docs = self.model.browse(docids)
        if docs:
            gst_val = self._get_val(docs)
            igst_val = self._get_igst_val(docs)
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
