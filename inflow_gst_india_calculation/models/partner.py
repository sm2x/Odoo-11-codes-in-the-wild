# -*- coding: utf-8 -*-
# Odoo, Open Source GST Indian Compliance.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).#
                                                             
from odoo import api, fields, models, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError
import re


class Partner(models.Model):
    """Partner"""
    _inherit = "res.partner"
    
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict', required=True)
    
    @api.model
    def create(self, vals):
        if vals.get('vat'):
            pattern = "[0-9]{2}[a-zA-Z]{5}[0-9]{4}[a-zA-Z]{1}[1-9A-Za-z]{1}[Z]{1}[0-9a-zA-Z]{1}"
            if re.match(pattern , vals.get('vat')) == None:
                raise ValidationError("Not Valid GSTIN Number.")
        res = super(Partner, self).create(vals)
        return res
    
    @api.multi
    def write(self, vals):
        if vals.get('vat'):
            pattern = "[0-9]{2}[a-zA-Z]{5}[0-9]{4}[a-zA-Z]{1}[1-9A-Za-z]{1}[Z]{1}[0-9a-zA-Z]{1}"
            if re.match(pattern , vals.get('vat')) == None:
                raise ValidationError("Not Valid GSTIN Number.")
        res = super(Partner, self).write(vals)
        return res


class Company(models.Model):
    """Company"""
    _inherit = "res.company"
    
    
    def _inverse_state(self):
        return super(Company, self)._inverse_state()
    
    def _compute_address(self):
        return super(Company, self)._compute_address()
    
    vat = fields.Char(related='partner_id.vat', string="TIN", required=True)
    state_id = fields.Many2one('res.country.state', compute='_compute_address', inverse='_inverse_state', string="Fed. State", required=True)
    
    @api.model
    def create(self, vals):
        if vals.get('vat'):
            pattern = "[0-9]{2}[a-zA-Z]{5}[0-9]{4}[a-zA-Z]{1}[1-9A-Za-z]{1}[Z]{1}[0-9a-zA-Z]{1}"
            if re.match(pattern , vals.get('vat')) == None:
                raise ValidationError("Not Valid GSTIN Number.")
        res = super(Company, self).create(vals)
        return res
    
    @api.multi
    def write(self, vals):
        if vals.get('vat'):
            pattern = "[0-9]{2}[a-zA-Z]{5}[0-9]{4}[a-zA-Z]{1}[1-9A-Za-z]{1}[Z]{1}[0-9a-zA-Z]{1}"
            if re.match(pattern , vals.get('vat')) == None:
                raise ValidationError("Not Valid GSTIN Number.")
        res = super(Company, self).write(vals)
        return res
    
class ResState(models.Model):
    """Company"""
    _inherit = "res.country.state"
    
    gst_code = fields.Char('GST Code')
