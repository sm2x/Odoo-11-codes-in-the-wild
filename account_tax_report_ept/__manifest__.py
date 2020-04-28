# -*- coding: utf-8 -*-
{
    
    # App information
    'name': 'Tax Report in Excel',
    'version': '11.0',
    'category': 'stock',
    'license': 'OPL-1',
    'summary' : 'Using this App, one can Print Tax Report in Excel in Odoo',
    
    'description': """This module will give tax report in two ways,
                      1. Tax wise separation
                      2. Tax Groups wise tax separation
                      
                      and also two reports are there,
                      1. Tax report
                      2. Tax summery report""",
   
    # Author
    'author': 'Emipro Technologies Pvt. Ltd.',
    'maintainer': 'Emipro Technologies Pvt. Ltd.',   
    'website': 'http://www.emiprotechnologies.com/',
    
     # Dependencies
       
    'depends': ['account_invoicing'],
    
    'data': [
       'views/account_tax_menu.xml'
        ],
    
     # Odoo Store Specific   
    
    'images': ['static/description/Tax-Report-in-Excel-cover.jpg'],
    
    # Technical        
    'external_dependencies' : {'python' : ['xlwt'], },
    'installable': True,
    'auto_install': False,
    'application' : True,
    'active': True,
    'live_test_url' :'http://www.emiprotechnologies.com/free-trial?app=account-tax-report-ept&version=11',
    'price': 49.00,
    'currency': 'EUR',  
    
    
}
