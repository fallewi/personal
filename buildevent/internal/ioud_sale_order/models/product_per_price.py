# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PricePerProduct(models.Model):
    _name = 'price.per.product'
    _description = 'price Per product'
    _inherit = ['mail.thread']

    product_id = fields.Many2one('product.product', string="Product", track_visibility=True)
    amount = fields.Float('Amount', track_visibility=True)
    product_price_id = fields.Many2one('res.partner', string="Product Price ID")