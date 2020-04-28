# -*- coding: utf-8 -*-
# Part of SnepTech See LICENSE file for full copyright and licensing details.##
##################################################################################


{
    'name': 'Payslip Payment Register',
    'version': '11.0.0.1',
    'summary': 'Customization related to payslip',
    'sequence': 1,
    'author': 'SnepTech',
    'license': 'AGPL-3',
    'website': 'https://www.sneptech.com/',
    "price": '49.99',
    "currency": 'USD',
    "images":['static/description/Banner.png'],  
    'description':""" 
        Odoo payslip payment register (Community). This module is aim to register the payslip payments for payrolls.
    """,
    'depends':['hr_payroll','account','hr_payroll_account','account_cancel'],
    'data':[
        'views/hr_payslip_view.xml',
        'views/hr_payslip_run_view.xml',
        'views/account_payment_view.xml',
        'wizard/register_payment_spt.xml',
        ],
        
    'application': False,
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
