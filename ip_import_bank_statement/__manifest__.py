# -*- coding: utf-8 -*-
{
    'name': 'Import Bank Statements',
    'summary': "Import SBI/HDFC Bank Statements from Excel",
    'description': "Import SBI/HDFC Bank Statements from Excel",

    'author': 'iPredict IT Solutions Pvt. Ltd.',
    'website': 'http://ipredictitsolutions.com',
    'support': 'ipredictitsolutions@gmail.com',

    'category': 'Accounting',
    'version': '11.0.0.1.0',
    'depends': ['account_invoicing'],

    'data': [
        'wizard/bank_statement_view.xml',
        'views/bank_statement_import_view.xml',
    ],

    'license': "OPL-1",

    'auto_install': False,
    'installable': True,

    'images': ['static/description/main.png'],
}
