# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd. (<http://devintellecs.com>).
#
##############################################################################
from datetime import timedelta
from openerp import models, fields, api, _
from odoo.exceptions import Warning


class customer_wirkflow(models.Model):
    """ Add Customer Workflow """
    _inherit = 'res.partner'
    _description = 'Add workflow'

    state = fields.Selection(
        [('draft', 'Draft'), ('confirm', 'Confirm'), ('approve', 'Approved'), ],
        string='State', default='draft')
    #sequence = fields.Char('Sequence', readonly=True, default="RP/")

    @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})
        return True

    @api.multi
    def action_approve(self):
        self.write({'state': 'approve'})
        return True

    @api.multi
    def action_confirm(self):
        self.write({'state': 'confirm'})
        return True

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    partner_state = fields.Selection(related='partner_id.state')


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    partner_state = fields.Selection(related='partner_id.state')
