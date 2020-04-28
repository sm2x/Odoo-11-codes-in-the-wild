# -*- coding: utf-8 -*-
# Odoo, Open Source GST Indian Compliance.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).#
                                                             
{
    'name': 'GST Indian Compliance',
    'category': 'Indian Localization',
    'author': 'ITMusketeers Consultancy Services LLP',
    'website': 'www.itmusketeers.com',
    'description': """
================================================================================

================================================================================
""",
    'depends': ['account', 'contacts', 'sales_team', 'web', 'base', 'sale', 'sale_management', 'product', 'stock', 'purchase'],
    'summary': ' To Generate GST  Invoice reports ',

    'data': [
             'security/ir.model.access.csv',
             'data/tax.category.csv',
             'data/product.hsn.csv',
             'data/res.country.state.csv',
             #'report/sale_order_report.xml',
             #'report/purchase_order_report.xml',
             'report/account_invoice_report.xml',
             'report/account_invoice_report_duplicate.xml',
             'report/account_invoice_report_triplicate.xml',
             'report/paper_format_custom.xml',
             'report/account_report.xml',
             'views/product_hsn_code_view.xml',
             'views/inherit_line_view.xml',
             'views/partner_view.xml',
             ],
    'price': '49.00',
    'currency': "EUR",
    'images':['static/description/Banner.png'],
    'installable': True,

}
