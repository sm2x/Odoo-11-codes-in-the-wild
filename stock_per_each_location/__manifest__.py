# -*- coding: utf-8 -*-
# Part of AktivSoftware See LICENSE file for full copyright and licensing details.
{
    'name': "Stock Per Each Location",
    'category': 'Warehouse',
    'version': '11.0.1.0.0',
    'summary': """
        Details of stock will be managed here for all products.
        """,
    'website': "http://www.aktivsoftware.com",
    'author': "Aktiv Software",
    'description': """
        This module gives you information about how many units of
        particular product are there at particular location and can alo get the
        information about the forecasting, incoming , outgoing of products.
    """,
    'depends': ['stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_template_views.xml',
        'views/product_stock_balance_views.xml',
        'views/table_css.xml',
        'report/report_product_stock_location.xml',
        'report/report_stock_location_template.xml',
    ],
    'images': ['static/description/banner.jpeg'],
    'auto_install': False,
    'installable': True,
    'application': False,
}
