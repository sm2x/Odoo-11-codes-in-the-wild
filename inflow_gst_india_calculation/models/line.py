# -*- coding: utf-8 -*-
# Odoo, Open Source GST Indian Compliance.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).#
                                                             
from odoo import api, fields, models, _


class SaleOrderLIne(models.Model):
    "Add hsn code in sale order line"
    
    _inherit = "sale.order.line"
    
    product_hsn_id = fields.Many2one('product.hsn', 'HSN Code', copy=False,)
    

class PurchaseOrderLIne(models.Model):
    "Add hsn code in purchase order line"
    
    _inherit = "purchase.order.line"
    
    product_hsn_id = fields.Many2one('product.hsn', 'HSN Code')
    
class AccountInvoiceLIne(models.Model):
    "Add hsn code in account invoice line"
    
    _inherit = "account.invoice.line"
    
    product_hsn_id = fields.Many2one('product.hsn', 'HSN Code') 
    
