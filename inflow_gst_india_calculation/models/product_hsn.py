# -*- coding: utf-8 -*-
# Odoo, Open Source GST Indian Compliance.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).#
                                                             
from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare


class ProductHSN(models.Model):
    """ product category HSN CODE Configuration """
    _name = "product.hsn"
    
    name = fields.Char('HSN Code')
    tax_categ_id = fields.Many2one('tax.category', 'GST Chapter')
    description = fields.Char('Item Description')
    rate = fields.Char('Rate')

class TaxCategory(models.Model):
    """ Tax category HSN CODE Configuration """    
    _name = "tax.category"

    name = fields.Char('Chapter Name')
    
    
class ProductProduct(models.Model):
    """ Tax category HSN CODE Configuration in Product """    
    _inherit = "product.template"
    
    tax_category_id = fields.Many2one('tax.category', 'Tax GST Category')
    hsn_id = fields.Many2one('product.hsn', 'HSN Code')
    
    
class Invoice(models.Model):
    _inherit = "account.invoice"
    
    # reverse_charge = fields.Boolean('Reverse Charges',default=False)
    
    '''@api.onchange('reverse_charge')
    def reverse_charge_change(self):
        search_tax_id =False
        if self.reverse_charge == False:
            if self.type in ('out_invoice','out_refund'):
                if self.invoice_line_ids:
                    for line in self.invoice_line_ids:
                        if self.partner_id.state_id.gst_code == self.company_id.state_id.gst_code:
                            if line.product_id.hsn_id:
                                if line.product_id.hsn_id.rate != 'Nil':
                                    amount =  float(float(line.product_id.hsn_id.rate)/2) * 100
                                    search_tax_id = self.env['account.tax'].search([('type_tax_use','=', 'sale' ),('amount','=', amount),'|', ('sgst','=',True),('cgst','=',True)] )
                        else:
                            if line.product_id.hsn_id:
                                if line.product_id.hsn_id.rate != 'Nil':
                                    amount =  float(line.product_id.hsn_id.rate) * 100
                                    search_tax_id = self.env['account.tax'].search([('type_tax_use','=', 'sale' ),('amount','=', amount),('igst','=',True)] )
                        line.update({'invoice_line_tax_ids':search_tax_id , })
            elif self.type in ('in_invoice','in_refund'):
                if self.invoice_line_ids:
                    for line in self.invoice_line_ids:
                        line.update({'invoice_line_tax_ids': False,})
        elif self.reverse_charge == True:   
            if self.type in ('in_invoice','in_refund'):
                if self.invoice_line_ids:
                    for line in self.invoice_line_ids:
                        if self.partner_id.state_id.gst_code == self.company_id.state_id.gst_code:
                            if line.product_id.hsn_id:
                                if line.product_id.hsn_id.rate != 'Nil':
                                    amount =  float(float(line.product_id.hsn_id.rate)/2) * 100
                                    search_tax_id = self.env['account.tax'].search([('type_tax_use','=', 'purchase' ),('amount','=', amount),'|', ('sgst','=',True),('cgst','=',True)] )
                        else:
                            if line.product_id.hsn_id:
                                if line.product_id.hsn_id.rate != 'Nil':
                                    amount =  float(line.product_id.hsn_id.rate) * 100
                                    search_tax_id = self.env['account.tax'].search([('type_tax_use','=', 'purchase' ),('amount','=', amount),('igst','=',True)] )
                        line.update({'invoice_line_tax_ids':search_tax_id ,})
            elif self.type in ('out_invoice','out_refund'):
                if self.invoice_line_ids:
                    for line in self.invoice_line_ids:
                        line.update({'invoice_line_tax_ids': False,})'''
    
    @api.multi    
    def amount_to_text(self, amount, currency):
        convert_amount_in_words = currency.amount_to_text(amount) 
        convert_amount_in_words += ' Only '   
        return convert_amount_in_words
    
# for convert amount into words in sale order
class SaleOrder(models.Model):
    _inherit = "sale.order"
    
#     reverse_charge = fields.Boolean('Reverse Charge')
#     
    @api.multi    
    def amount_to_text(self, amount, currency):
        convert_amount_in_words = currency.amount_to_text(amount) 
        convert_amount_in_words += ' Only '   
        return convert_amount_in_words
    
# for convert amount into words in purchase order
class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    
    @api.multi    
    def amount_to_text(self, amount, currency):
        convert_amount_in_words = currency.amount_to_text(amount) 
        convert_amount_in_words += ' Only '   
        return convert_amount_in_words
    
    
class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    
    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return {'domain': {'product_uom': []}}
        vals = {}
        domain = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
        if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
            vals['product_uom'] = self.product_id.uom_id
            vals['product_uom_qty'] = 1.0
        
        search_tax_id = []   
        if self.product_id.hsn_id:
            hsn_id = self.product_id.hsn_id.id
            vals['product_hsn_id'] = hsn_id
            amount = 0.0
            if self.order_id.partner_id.state_id:
                if self.order_id.partner_id.state_id.gst_code == self.order_id.warehouse_id.partner_id.state_id.gst_code:
                    if self.product_id.hsn_id.rate != 'Nil':
                        amount = float(float(self.product_id.hsn_id.rate) / 2) * 100
                        search_tax_id = self.env['account.tax'].search([('amount_type', '=', 'group'), ('type_tax_use', 'in', ['sale'])])
                        sale_tax_list = [tax.id for tax in search_tax_id for child in tax.children_tax_ids if amount == child.amount ]
                        search_tax_id = self.env['account.tax'].search([('id', 'in', sale_tax_list)])
                else:
                    if self.product_id.hsn_id.rate != 'Nil':
                        amount = float(self.product_id.hsn_id.rate) * 100
                        search_tax_group_id = self.env['account.tax.group'].search([('name', '=', 'IGST')])
                        tax_list = [ tax.id for tax in search_tax_group_id if search_tax_group_id ]
                        search_tax_id = self.env['account.tax'].search([('type_tax_use', 'in', ['sale']), ('amount', '=', amount), ('tax_group_id', 'in', tax_list)])
            vals['tax_id'] = search_tax_id or False
        product = self.product_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id.id,
            quantity=vals.get('product_uom_qty') or self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id,
            
        )
        name = product.name_get()[0][1]
        if product.description_sale:
            name += '\n' + product.description_sale
        vals['name'] = name
        
        
        self._compute_tax_id()
        if self.order_id.pricelist_id and self.order_id.partner_id:
            vals['price_unit'] = self.env['account.tax']._fix_tax_included_price(self._get_display_price(product), product.taxes_id, self.tax_id)
        self.update(vals)
        
        title = False
        message = False
        warning = {}
        if not self.order_id.partner_id.state_id  and not self.order_id.company_id.state_id:
            message = "Please Set State in Customer and State in Company"
            warning['message'] = message
            return {'warning': warning}
        if not self.order_id.partner_id.state_id  and  self.order_id.company_id.state_id:
            message = "Please Set State in Customer"
            warning['message'] = message
            return {'warning': warning}
        if self.order_id.partner_id.state_id  and not self.order_id.company_id.state_id:
            message = "Please Set State in Company"
            warning['message'] = message
            return {'warning': warning}
        if product.sale_line_warn != 'no-message':
            title = _("Warning for %s") % product.name
            message = product.sale_line_warn_msg
            warning['title'] = title
            warning['message'] = message
            if product.sale_line_warn == 'block':
                self.product_id = False
            return {'warning': warning}
        
        return {'domain': domain}
    
    @api.multi
    def _prepare_invoice_line(self, qty):
        """
        Prepare the dict of values to create the new invoice line for a sales order line.

        :param qty: float quantity to invoice
        """
        self.ensure_one()
        res = {}
        account = self.product_id.property_account_income_id or self.product_id.categ_id.property_account_income_categ_id
        if not account:
            raise UserError(_('Please define income account for this product: "%s" (id:%d) - or for its category: "%s".') % 
                (self.product_id.name, self.product_id.id, self.product_id.categ_id.name))

        fpos = self.order_id.fiscal_position_id or self.order_id.partner_id.property_account_position_id
        if fpos:
            account = fpos.map_account(account)

        res = {
            'name': self.name,
            'sequence': self.sequence,
            'origin': self.order_id.name,
            'account_id': account.id,
            'price_unit': self.price_unit,
            'quantity': qty,
            'discount': self.discount,
            'uom_id': self.product_uom.id,
            'product_id': self.product_id.id or False,
            'layout_category_id': self.layout_category_id and self.layout_category_id.id or False,
            'product_id': self.product_id.id or False,
            'invoice_line_tax_ids': [(6, 0, self.tax_id.ids)],
            'account_analytic_id': self.order_id.analytic_account_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            'product_hsn_id' : self.product_hsn_id.id or False,
        }
        return res


class SaleAdvancePaymentInvCustom(models.TransientModel):
    _inherit = "sale.advance.payment.inv"
    
    @api.multi
    def _create_invoice(self, order, so_line, amount):
        inv_obj = self.env['account.invoice']
        ir_property_obj = self.env['ir.property']

        account_id = False
        if self.product_id.id:
            account_id = self.product_id.property_account_income_id.id
        if not account_id:
            inc_acc = ir_property_obj.get('property_account_income_categ_id', 'product.category')
            account_id = order.fiscal_position_id.map_account(inc_acc).id if inc_acc else False
        if not account_id:
            raise UserError(
                _('There is no income account defined for this product: "%s". You may have to install a chart of account from Accounting app, settings menu.') % 
                (self.product_id.name,))

        if self.amount <= 0.00:
            raise UserError(_('The value of the down payment amount must be positive.'))
        if self.advance_payment_method == 'percentage':
            amount = order.amount_untaxed * self.amount / 100
            name = _("Down payment of %s%%") % (self.amount,)
        else:
            amount = self.amount
            name = _('Down Payment')
        if order.fiscal_position_id and self.product_id.taxes_id:
            tax_ids = order.fiscal_position_id.map_tax(self.product_id.taxes_id).ids
        else:
            tax_ids = self.product_id.taxes_id.ids

        invoice = inv_obj.create({
            'name': order.client_order_ref or order.name,
            'origin': order.name,
            'type': 'out_invoice',
            'reference': False,
            'account_id': order.partner_id.property_account_receivable_id.id,
            'partner_id': order.partner_invoice_id.id,
            'partner_shipping_id': order.partner_shipping_id.id,
            'invoice_line_ids': [(0, 0, {
                'name': name,
                'origin': order.name,
                'account_id': account_id,
                'price_unit': amount,
                'quantity': 1.0,
                'discount': 0.0,
                'uom_id': self.product_id.uom_id.id,
                'product_hsn_id' : self.product_id.product_hsn_id.id or False,
                'product_id': self.product_id.id,
                'sale_line_ids': [(6, 0, [so_line.id])],
                'invoice_line_tax_ids': [(6, 0, tax_ids)],
                'account_analytic_id': order.project_id.id or False,
            })],
            'currency_id': order.pricelist_id.currency_id.id,
            'payment_term_id': order.payment_term_id.id,
            'fiscal_position_id': order.fiscal_position_id.id or order.partner_id.property_account_position_id.id,
            'team_id': order.team_id.id,
            'comment': order.note,
        })
        invoice.compute_taxes()
        invoice.message_post_with_view('mail.message_origin_link',
                    values={'self': invoice, 'origin': order},
                    subtype_id=self.env.ref('mail.mt_note').id)
        return invoice


    
class AccountInvoiceLines(models.Model):
    _inherit = "account.invoice.line"    
    
    
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        domain = {}
        if not self.invoice_id:
            return
        part = self.invoice_id.partner_id
        fpos = self.invoice_id.fiscal_position_id
        company = self.invoice_id.company_id
        currency = self.invoice_id.currency_id
        type = self.invoice_id.type
        hsn_id = False
        amount = 0.0
        if self.product_id.hsn_id:
            hsn_id = self.product_id.hsn_id.id
            self.product_hsn_id = hsn_id
        if not part:
            warning = {
                    'title': _('Warning!'),
                    'message': _('You must first select a partner!'),
                }
            return {'warning': warning}

        if not self.product_id:
            if type not in ('in_invoice', 'in_refund'):
                self.price_unit = 0.0
            domain['uom_id'] = []
        else:
            
            if part.lang:
                product = self.product_id.with_context(lang=part.lang)
            else:
                product = self.product_id

            self.name = product.partner_ref
            account = self.get_invoice_line_account(type, product, fpos, company)
            if account:
                self.account_id = account.id
            self._set_taxes()
            search_tax_id = []
            if type in ('in_invoice', 'in_refund'):
                if self.invoice_id.partner_id.state_id.gst_code == self.invoice_id.company_id.state_id.gst_code:
                    if self.product_id.hsn_id:
                        if self.product_id.hsn_id.rate != 'Nil':
                            amount = float(float(self.product_id.hsn_id.rate) / 2) * 100
                            search_tax_id = self.env['account.tax'].search([('amount_type', '=', 'group'), ('type_tax_use', 'in', ['purchase'])])
                            purchase_tax_list = [tax.id for tax in search_tax_id for child in tax.children_tax_ids if amount == child.amount ]
                            search_tax_id = self.env['account.tax'].search([('id', 'in', purchase_tax_list)])
                else:
                    if self.product_id.hsn_id:
                        if self.product_id.hsn_id.rate != 'Nil':
                            amount = float(self.product_id.hsn_id.rate) * 100
                            search_tax_group_id = self.env['account.tax.group'].search([('name', '=', 'IGST')])
                            tax_list = [ tax.id for tax in search_tax_group_id if search_tax_group_id ]
                            search_tax_id = self.env['account.tax'].search([('type_tax_use', 'in', ['purchase']), ('amount', '=', amount), ('tax_group_id', 'in', tax_list)])
                if product.description_purchase:
                    self.name += '\n' + product.description_purchase
                if hsn_id:
                    self.invoice_line_tax_ids = search_tax_id or False
            else:
                if self.invoice_id.partner_id.state_id.gst_code == self.invoice_id.company_id.state_id.gst_code:
                    if self.product_id.hsn_id:
                        if self.product_id.hsn_id.rate != 'Nil':
                            amount = float(float(self.product_id.hsn_id.rate) / 2) * 100
                            search_tax_id = self.env['account.tax'].search([('amount_type', '=', 'group'), ('type_tax_use', 'in', ['sale'])])
                            sale_tax_list = [tax.id for tax in search_tax_id for child in tax.children_tax_ids if amount == child.amount ]
                            search_tax_id = self.env['account.tax'].search([('id', 'in', sale_tax_list)])
                else:
                    if self.product_id.hsn_id:
                        if self.product_id.hsn_id.rate != 'Nil':
                            amount = float(self.product_id.hsn_id.rate) * 100
                            search_tax_group_id = self.env['account.tax.group'].search([('name', '=', 'IGST')])
                            tax_list = [ tax.id for tax in search_tax_group_id if search_tax_group_id ]
                            search_tax_id = self.env['account.tax'].search([('type_tax_use', 'in', ['sale']), ('amount', '=', amount), ('tax_group_id', 'in', tax_list)])
                if product.description_sale:
                    self.name += '\n' + product.description_sale
                
                if hsn_id:
                    self.invoice_line_tax_ids = search_tax_id or False
                    
            if not self.uom_id or product.uom_id.category_id.id != self.uom_id.category_id.id:
                self.uom_id = product.uom_id.id
            domain['uom_id'] = [('category_id', '=', product.uom_id.category_id.id)]
            
            if company and currency:
                if company.currency_id != currency:
                    self.price_unit = self.price_unit * currency.with_context(dict(self._context or {}, date=self.invoice_id.date_invoice)).rate

                if self.uom_id and self.uom_id.id != product.uom_id.id:
                    self.price_unit = product.uom_id._compute_price(self.price_unit, self.uom_id)
            message = False
            warning = {}
            if not self.invoice_id.partner_id.state_id  and not self.invoice_id.company_id.state_id:
                message = "Please Set State in Customer and State in Company"
                warning['message'] = message
                return {'warning': warning}
            if not self.invoice_id.partner_id.state_id  and  self.invoice_id.company_id.state_id:
                message = "Please Set State in Customer"
                warning['message'] = message
                return {'warning': warning}
            if self.invoice_id.partner_id.state_id  and not self.invoice_id.company_id.state_id:
                message = "Please Set State in Company"
                warning['message'] = message
                return {'warning': warning}
        
        return {'domain': domain}
  
    
class AccountInvoice(models.Model):
    _inherit = "account.invoice"    
    
    def _prepare_invoice_line_from_po_line(self, line):
        if line.product_id.purchase_method == 'purchase':
            qty = line.product_qty - line.qty_invoiced
        else:
            qty = line.qty_received - line.qty_invoiced
        if float_compare(qty, 0.0, precision_rounding=line.product_uom.rounding) <= 0:
            qty = 0.0
        taxes = line.taxes_id
        invoice_line_tax_ids = line.order_id.fiscal_position_id.map_tax(taxes)
        invoice_line = self.env['account.invoice.line']
        data = {
            'purchase_line_id': line.id,
            'name': line.order_id.name + ': ' + line.name,
            'origin': line.order_id.origin,
            'uom_id': line.product_uom.id,
            'product_id': line.product_id.id,
            'account_id': invoice_line.with_context({'journal_id': self.journal_id.id, 'type': 'in_invoice'})._default_account(),
            'price_unit': line.order_id.currency_id.compute(line.price_unit, self.currency_id, round=False),
            'quantity': qty,
            'discount': 0.0,
            'product_hsn_id' : line.product_hsn_id.id or False,
            'account_analytic_id': line.account_analytic_id.id,
            'analytic_tag_ids': line.analytic_tag_ids.ids,
            'invoice_line_tax_ids': invoice_line_tax_ids.ids
        }
        account = invoice_line.get_invoice_line_account('in_invoice', line.product_id, line.order_id.fiscal_position_id, self.env.user.company_id)
        if account:
            data['account_id'] = account.id
        return data

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line" 
    
    @api.onchange('product_id')
    def onchange_product_id(self):
        result = {}
        search_tax_id = []
        if not self.product_id:
            return result
        amount = 0.0
        # Reset date, price and quantity since _onchange_quantity will provide default values
        self.date_planned = datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        self.price_unit = self.product_qty = 0.0
        self.product_uom = self.product_id.uom_po_id or self.product_id.uom_id
        result['domain'] = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}

        product_lang = self.product_id.with_context({
            'lang': self.partner_id.lang,
            'partner_id': self.partner_id.id,
        })
        self.name = product_lang.display_name
        if product_lang.description_purchase:
            self.name += '\n' + product_lang.description_purchase
        fpos = self.order_id.fiscal_position_id
        if self.env.uid == SUPERUSER_ID:
            company_id = self.env.user.company_id.id
            self.taxes_id = fpos.map_tax(self.product_id.supplier_taxes_id.filtered(lambda r: r.company_id.id == company_id))
        else:
            self.taxes_id = fpos.map_tax(self.product_id.supplier_taxes_id)
        if self.product_id.hsn_id:
            if self.order_id.partner_id.state_id.gst_code == self.order_id.company_id.state_id.gst_code:
                if self.product_id.hsn_id.rate != 'Nil':
                    amount = float(float(self.product_id.hsn_id.rate) / 2) * 100
                    search_tax_id = self.env['account.tax'].search([('amount_type', '=', 'group'), ('type_tax_use', 'in', ['purchase'])])
                    purchase_tax_list = [tax.id for tax in search_tax_id for child in tax.children_tax_ids if amount == child.amount ]
                    search_tax_id = self.env['account.tax'].search([('id', 'in', purchase_tax_list)])
            else:
                if self.product_id.hsn_id.rate != 'Nil':
                    amount = float(self.product_id.hsn_id.rate) * 100
                    search_tax_group_id = self.env['account.tax.group'].search([('name', '=', 'IGST')])
                    tax_list = [ tax.id for tax in search_tax_group_id if search_tax_group_id ]
                    search_tax_id = self.env['account.tax'].search([('type_tax_use', 'in', ['purchase']), ('amount', '=', amount), ('tax_group_id', 'in', tax_list)])
            hsn_id = self.product_id.hsn_id.id
            self.product_hsn_id = hsn_id
            
            self.taxes_id = search_tax_id or False
        
        message = False
        warning = {}
        if not self.order_id.partner_id.state_id  and not self.order_id.company_id.state_id:
            message = "Please Set State in Customer and State in Company"
            warning['message'] = message
            return {'warning': warning}
        if not self.order_id.partner_id.state_id  and  self.order_id.company_id.state_id:
            message = "Please Set State in Customer"
            warning['message'] = message
            return {'warning': warning}
        if self.order_id.partner_id.state_id  and not self.order_id.company_id.state_id:
            message = "Please Set State in Company"
            warning['message'] = message
            return {'warning': warning}
        self._suggest_quantity()
        self._onchange_quantity()
        return result
