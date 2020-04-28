# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.tools.float_utils import float_round


class ProductStockBalance(models.Model):
    _name = 'product.stock.balance'

    product_template_id = fields.Many2one('product.template', string="Product")
    product_name = fields.Char()
    location_id = fields.Many2one('stock.location', string="Location Name")
    onhand = fields.Float(string="On Hand")
    forecast = fields.Float()
    incoming = fields.Float()
    outgoing = fields.Float()


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_stock_location = fields.One2many(
        'product.stock.balance', 'product_template_id', compute='display_data')

    @api.multi
    def display_data(self):
        product_ids = self.env['product.product'].search(
            [('product_tmpl_id', '=', self.id)])
        for product_id in product_ids:
            stock_quant_ids = self.env['stock.quant'].search(
                [('product_id', '=', product_id.id)])
            location_ids = stock_quant_ids.mapped('location_id')
            location_id_list = location_ids.filtered(
                lambda s: s.usage == "internal").ids
            stock_location_records = {}
            for location_id in location_id_list:
                res = self.sudo().get_product_stock_location(location_id, product_id)
                stock_location_records.update(res)
            for location_id_id in stock_location_records:
                location_id = self.env['stock.location'].browse(
                    [location_id_id])
                parent_location_id = location_id.location_id.id
                if parent_location_id in stock_location_records.keys():
                    stock_location_records[
                        parent_location_id]['qty_available'] -= \
                        stock_location_records[location_id_id]['qty_available']
                    stock_location_records[
                        parent_location_id]['incoming_qty'] -= \
                        stock_location_records[location_id_id]['incoming_qty']
                    stock_location_records[
                        parent_location_id]['outgoing_qty'] -= \
                        stock_location_records[location_id_id]['outgoing_qty']
                    stock_location_records[
                        parent_location_id]['virtual_available'] -= \
                        stock_location_records[
                        location_id_id]['virtual_available']
            for data in stock_location_records:
                values = {'product_template_id': self.id,
                          'product_name': product_id.display_name,
                          'location_id': data,
                          'onhand':
                          stock_location_records[data]['qty_available'],
                          'forecast':
                          stock_location_records[data]['virtual_available'],
                          'incoming':
                          stock_location_records[data]['incoming_qty'],
                          'outgoing':
                          stock_location_records[data]['outgoing_qty'],
                          }
                self.product_stock_location |= self.env[
                    'product.stock.balance'].sudo().create(
                    values)

    @api.multi
    def get_data(self):
        val = []
        product_ids = self.env['product.product'].search(
            [('product_tmpl_id', 'in', self.ids)])
        for product_id in product_ids:
            stock_quant_ids = self.env['stock.quant'].search(
                [('product_id', '=', product_id.id)])
            location_ids = stock_quant_ids.mapped('location_id')
            location_id_list = location_ids.filtered(
                lambda s: s.usage == "internal").ids
            stock_location_records = {}
            for location_id in location_id_list:
                res = self.sudo().get_product_stock_location(location_id, product_id)
                stock_location_records.update(res)
            for location_id_id in stock_location_records:
                location_id = self.env['stock.location'].browse(
                    [location_id_id])
                parent_location_id = location_id.location_id.id
                if parent_location_id in stock_location_records.keys():
                    stock_location_records[
                        parent_location_id]['qty_available'] -= \
                        stock_location_records[location_id_id]['qty_available']
                    stock_location_records[
                        parent_location_id]['incoming_qty'] -= \
                        stock_location_records[location_id_id]['incoming_qty']
                    stock_location_records[
                        parent_location_id]['outgoing_qty'] -= \
                        stock_location_records[location_id_id]['outgoing_qty']
                    stock_location_records[
                        parent_location_id]['virtual_available'] -= \
                        stock_location_records[
                        location_id_id]['virtual_available']
                values = {'product_template_id': self.id,
                          'product_name': product_id.display_name,
                          'location_id': location_id.id,
                          'onhand':
                          stock_location_records[
                              location_id_id]['qty_available'],
                          'forecast':
                          stock_location_records[
                              location_id_id]['virtual_available'],
                          'incoming':
                          stock_location_records[
                              location_id_id]['incoming_qty'],
                          'outgoing':
                          stock_location_records[
                              location_id_id]['outgoing_qty'],
                          }
                val.append(self.env['product.stock.balance'].sudo().create(values))
        return val

    def get_product_stock_location(self, location_id, product_id):
        domain_quant_loc, domain_move_in_loc, domain_move_out_loc = self.env[
            'product.product']._get_domain_locations_new(
                location_id, company_id=False, compute_child=True)
        domain_quant = [('product_id', 'in', product_id.ids)
                        ] + domain_quant_loc
        domain_move_in = [
            ('product_id', 'in', product_id.ids)] + domain_move_in_loc
        domain_move_out = [
            ('product_id', 'in', product_id.ids)] + domain_move_out_loc
        Move = self.env['stock.move']
        Quant = self.env['stock.quant']
        domain_move_in_todo = [
            ('state', 'not in', ('done', 'cancel', 'draft'))] + domain_move_in
        domain_move_out_todo = [
            ('state', 'not in', ('done', 'cancel', 'draft'))] + domain_move_out
        moves_in_res = dict((item['product_id'][0], item[
            'product_qty']) for item in Move.read_group(
            domain_move_in_todo, ['product_id', 'product_qty'], [
                'product_id']))
        moves_out_res = dict((item['product_id'][0], item[
            'product_qty']) for item in Move.read_group(
            domain_move_out_todo, ['product_id', 'product_qty'], [
                'product_id']))
        quants_res = dict((item['product_id'][0], item[
            'quantity']) for item in Quant.read_group(
            domain_quant, ['product_id', 'quantity'], ['product_id']))
        res = dict()
        for product in product_id:
            res[location_id] = {}
            qty_available = quants_res.get(product.id, 0.0)
            res[location_id]['qty_available'] = float_round(
                qty_available, precision_rounding=product.uom_id.rounding)
            res[location_id]['incoming_qty'] = float_round(moves_in_res.get(
                product.id, 0.0), precision_rounding=product.uom_id.rounding)
            res[location_id]['outgoing_qty'] = float_round(moves_out_res.get(
                product.id, 0.0), precision_rounding=product.uom_id.rounding)
            res[location_id]['virtual_available'] = float_round(
                qty_available +
                res[location_id]['incoming_qty'] -
                res[location_id]['outgoing_qty'],
                precision_rounding=product.uom_id.rounding)
        return res
