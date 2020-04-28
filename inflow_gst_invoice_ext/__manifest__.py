#################################################################################
# Author      : Inflow Industrial Solutions. (<https://inflow.co.in/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://inflow.co.in/>
#################################################################################

{
    'name': 'GST - Returns and Invoices Extension for Sale Journal',
    'version': '1.0.2',
    'category': 'Accounting',
    'sequence': 1,
    "author": "Inflow Industrial Solutions",
    'website': 'https://inflow.co.in',
    'summary': 'GST Invoice Reports extension with Sale Journal',
    'description': """

GST - Returns and Invoices
==========================
Extension of Webkul module with the added functionality of Journal Invoices
--------------------------------------------------------------
    """,
    'depends': [
        'l10n_in',
        'account_tax_python',
        'gst_invoice',
    ],
    'data': [
        'views/gstr_view_ext.xml',

    ],
    'sequence': 1,
    'application': False,
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
