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


class DeliverySetting(models.Model):
#     _name = "delivery.setting"
    _inherit = "stock.warehouse"
    
    send_email = fields.Boolean(string="Send Delivery Email")
    send_auto_mail = fields.Boolean(string="Send Automatic Email")
    email_temp = fields.Many2one('mail.template',string="Select Email Template")
    
  
  
    
