# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.


from odoo import fields, models, api
from datetime import datetime

        
class sale_order(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection([
            ('draft', 'Draft Quotation'),
            ('sent', 'Quotation Sent'),
            ('sale', 'Sale Order'),
            ('to approve', 'Confirmed'),
            ('cancel', 'Cancelled'),
            ('done', 'Locked'),
            ], string='Status', readonly=True, copy=False, help="Gives the status of the quotation or sales order.\
              \nThe exception status is automatically set when a cancel operation occurs \
              in the invoice validation (Invoice Exception) or in the picking list process (Shipping Exception).\nThe 'Waiting Schedule' status is set when the invoice is confirmed\
               but waiting for the scheduler to run on the order date.", select=True)


    @api.multi
    def button_toapprove(self):
        for order in self:
            so_double_validation_amount=self.env['ir.config_parameter'].sudo().get_param('sale_approve.so_double_validation_amount')
            so_order_approval = self.env['ir.config_parameter'].sudo().get_param('sale_approve.so_order_approval')
            so_double_validation_amount = self.env['ir.config_parameter'].sudo().get_param('sale_approve.so_double_validation_amount') 


            if order.state not in ['draft', 'sent']:
                continue
            #order._add_supplier_to_product()
            # Deal with double validation process
            
            
            if so_order_approval == "True" :
                
                if order.amount_total < float(so_double_validation_amount):
            

                    
                    order.action_confirm()
                else:
                    order.write({'state': 'to approve'})
            else : 
                
                order.action_confirm()
            
            
        return True


    @api.multi
    def button_unlock(self):
        self.write({'state': 'sale'})


    @api.multi
    def _track_subtype_approve(self, init_values):
        self.ensure_one()
        if 'state' in init_values and self.state == 'to approve':
            return 'sale.mt_order_toapprove'
        if 'state' in init_values and self.state == 'sale':
            return 'sale.mt_order_confirmed'
        elif 'state' in init_values and self.state == 'sent':
            return 'sale.mt_order_sent'
        return super(SaleOrder, self)._track_subtype(init_values)


class SaleConfiguration(models.TransientModel):
    _inherit = 'res.config.settings'


    so_order_approval = fields.Boolean(string= 'SO Approval')
    so_double_validation_amount = fields.Monetary( string="Double validation amount *", currency_field='company_currency_id', default=5000)     
    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True,
        help='Utility field to express amount currency')



    def get_values(self):


        res = super(SaleConfiguration, self).get_values()
        

        res.update(
            so_order_approval = self.env['ir.config_parameter'].sudo().get_param('sale_approve.so_order_approval'),
            so_double_validation_amount=float(self.env['ir.config_parameter'].sudo().get_param('sale_approve.so_double_validation_amount'))
        )
        return res

    def set_values(self):
        super(SaleConfiguration, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('sale_approve.so_order_approval', self.so_order_approval)
        self.env['ir.config_parameter'].sudo().set_param('sale_approve.so_double_validation_amount', self.so_double_validation_amount)



   





