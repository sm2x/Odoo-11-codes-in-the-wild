# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
#    Globalteckz Software Solutions and Services                             #
#    Copyright (C) 2013-Today(www.globalteckz.com).                          #
#                                                                            #
#    This program is free software: you can redistribute it and/or modify    #
#    it under the terms of the GNU Affero General Public License as          #
#    published by the Free Software Foundation, either version 3 of the      #
#    License, or (at your option) any later version.                         #
#                                                                            #
#    This program is distributed in the hope that it will be useful,         #  
#    but WITHOUT ANY WARRANTY; without even the implied warranty of          #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           #
#    GNU Affero General Public License for more details.                     #
#                                                                            #
#                                                                            #
##############################################################################
from odoo import api, fields, models,_
from datetime import datetime
from datetime import date, timedelta
import base64, urllib
from odoo.exceptions import UserError, ValidationError
import re

    
class StockPicking(models.Model):
    _inherit = "stock.picking"
     
     
    def  ValidateEmail(self, cr, uid, ids, email):
        if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) == None:
            raise osv.except_osv('Invalid Email', 'Please enter a valid email address')
        return True
    
    @api.multi
    def multiple_email(self):
        warehouse_obj = self.env['stock.warehouse']
        picking_ids = self.env.context.get('active_ids')
        p_ids = self.env['stock.picking'].browse(picking_ids)
        for rec in p_ids:
            ware_ids = warehouse_obj.search([('code','=',rec.picking_type_id.warehouse_id.code),('send_email','=',True),('email_temp','=',rec.picking_type_id.warehouse_id.email_temp.id)])
            if ware_ids:
                try:
                 template_id = self.env.ref('gt_delivery_confirmation.delivery_order_email_template_completion')
                except ValueError:
                    template_id = False
                if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", rec.partner_id.email) == None:
                    print("===========>>>>>>>>>iffffffffffff>>>")
#                     raise UserError(_('Given Email Is Not Valid.'))
                    raise ValidationError(_("The Given Email Is Not Valid '%s' for '%s' Delivery Order") % (rec.partner_id.email,rec.name))
                else :
                    send_mail = template_id.send_mail(rec.id,force_send=True)
#                     raise UserError(_('Your Message Is Successfully Send.'))
            else:
                raise UserError(_('Please Configure Your Warehouse Setting Properly'))

               
               
    @api.multi
    def single_email(self):
        warehouse_obj = self.env['stock.warehouse']
        for rec in self:
            ware_ids = warehouse_obj.search([('code','=',rec.picking_type_id.warehouse_id.code),('send_email','=',True),('email_temp','=',rec.picking_type_id.warehouse_id.email_temp.id)])
            if ware_ids:
                try:
                    template_id = self.env.ref('gt_delivery_confirmation.delivery_order_email_template_completion')
                except ValueError:
                    template_id = False
                if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", rec.partner_id.email) == None:
                    print("===========>>>>>>>>>iffffffffffff>>>")
                    raise ValidationError(_("The Given Email '%s' Is Not Valid for '%s' Delivery Order") % (rec.partner_id.email,rec.name))
                else :
                    send_mail = template_id.send_mail(rec.id,force_send=True)
                    raise UserError(_('Your Message Is Successfully Send.'))
            else:
                raise UserError(_('Please Configure Your Warehouse Setting Properly'))


    @api.multi
    def button_validate(self):
        ware_obj = self.env['stock.warehouse']
        res = super(StockPicking, self).button_validate()
        for rec in self:
            ware_ids = ware_obj.search([('code','=',rec.picking_type_id.warehouse_id.code),('send_auto_mail','=',True),('email_temp','=',rec.picking_type_id.warehouse_id.email_temp.id)])
            if rec.picking_type_id.name == 'Delivery Orders':
                if ware_ids:
                    try:
                        template_id = self.env.ref('gt_delivery_confirmation.delivery_order_email_template_completion')
                    except ValueError:
                        template_id = False
                    if template_id:
                       send_mail = template_id.send_mail(rec.id,force_send=True)
                else:
                    raise UserError(_('Please Configure Your Warehouse Setting Properly'))
        return res
