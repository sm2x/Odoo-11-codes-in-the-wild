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

{
    'name': 'Odoo Email Notification for Delivery Order Completion',
    'version': '11.0',
    'category': 'Generic Modules',
    'sequence': 1,
	"license" : "Other proprietary",
    'images': ['static/description/Banner.png'],
    "category": "Sale",
    "price": "49.00",
    "currency": "EUR",
    'author': 'Globalteckz',
    'website': 'http://www.globalteckz.com',
    'summary': 'email notification to customers once delivery order confirmed',
    'description': """
email notification
email to customer 
customer email
delivery order email 
email notification for delivery order completetion
email notification for delivery order complete
complete order email 
complete order email notification
complete order email to customer
bulk email 
bulk email to customer
automatic email to customer
automatic email
delivery order email manually to customer
notification
email to customer
manual email to customer

    """,
    'depends': ['sale','stock','base','delivery'],
    'data': [
            'views/delivery_email_view.xml',
            'views/delivery_setting_view.xml',
            'data/delivery_email_data.xml',
            ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
