# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResPartnerInherit(models.Model):
	_inherit = 'res.partner'

	@api.model
	def default_get(self, fields):
		result= super(ResPartnerInherit, self).default_get(fields)
		res = self.env['account.account'].search([('code','=','13111000')], limit=1)
		result['property_account_payable_id'] = res.id
		return result
	
	ext_arabic_name = fields.Char(string="Arabic Name")
	ext_classification = fields.Char(string="Classification")
	ext_vendor_no = fields.Char(string="Vendor Number")
	ext_finance_contact = fields.Char(string="Finance Person")
	ext_finance_contact_no = fields.Char(string="Finance Contact")
	ext_finance_contact_email = fields.Char(string="Finance Email")
	ext_purchase_contact = fields.Char(string="Purchase Person")
	ext_purchase_contact_no = fields.Char(string="Purchase Contact")
	ext_purchase_contact_email = fields.Char(string="Purchase Email")
	# # ext_type_of_cust = fields.Selection([('MT', 'Modern Trade'),
    #                                 ('WT', 'Traditional Trade'),
    #                                 ('CT', 'Corporate Trade'),
    #                                 ('partner', 'Partner'),
    #                                 ('POS', 'POS'),
    #                                 ('EC', 'E-Commerce'),
    #                                 ('EX', 'Exporting'),
    #                                 ('OT', 'Others'),
    #                                 ('EMP', 'Employee'),
    #                                 ], string='Customer Type')
	pos_discount = fields.Boolean(string="POS Discount (%)")
	ext_type_of_material = fields.Char(string="Type of Material Supplier")
	ext_payment_terms = fields.Char(string="Payment Terms")
	ext_iban_no = fields.Char(string="IBAN No")
	ext_bank = fields.Char(string="Bank")
	ext_location = fields.Char(string="Location")
	ext_kind = fields.Char(string="Kind")
	ext_stands = fields.Char(string="Stands")
	stand_qty = fields.Float(string="Stand Qty", compute="_compute_stand_attrs")
	stand_rent = fields.Float(string="Stand Rent", compute="_compute_stand_attrs")
	rebate_percent = fields.Float(string="Rebate %")
	rebate_from = fields.Date(string="Rebate From")
	rebate_to = fields.Date(string="Rebate To")

	salesperson_user_ids = fields.Many2many('res.users', string='Salesperson')

	# price_per_product = fields.One2many('price.per.product', 'product_price_id', string="Price Per Product", track_visibility=True)
	is_new_vendor_no = fields.Boolean("Is New Sequnce",default=True)
	is_new = fields.Boolean("Is NEW")
	
	@api.model
	def create(self, vals):
		vals['ext_vendor_no'] = self.env['ir.sequence'].next_by_code('res.partner.new') or _('New')
		vals['is_new_vendor_no'] = True
		return super(ResPartnerInherit, self).create(vals)


	@api.model 
	def _cron_generate_internal_refrence(self):
		for data in self.search([('is_new','=',False)]):	
			data.write({'is_new' : True,'is_new_vendor_no' : True,'ext_vendor_no' : self.env['ir.sequence'].next_by_code('res.partner.new')})


	@api.depends('name')
	def _compute_stand_attrs(self):
		self.stand_rent = sum(line.stand_rent for line in self.env['ioud_branches.ioud_branches'].search([('head_office','=',self.id)]))
		self.stand_qty = sum(line.stand_qty for line in self.env['ioud_branches.ioud_branches'].search([('head_office','=',self.id)]))
		return True

	@api.model
	def name_search(self, name, args=None, operator='ilike', limit=100):
		args = args or []
		recs = self.browse()
		if name:
			recs = self.search([('ext_arabic_name', '=', name)] + args, limit=limit)
		if not recs:
			recs = self.search([('name', operator, name)] + args, limit=limit)
		return recs.name_get()

	# @api.model
	# def setPricePerProduct(self, first_prod_id, first_prod_amt, second_prod_id, second_prod_amt):
	# 	count = 0
	# 	Records  = self.env['res.partner'].search([('customer','=',True),('active', '=', True)])
	# 	for rec in Records:
	# 		rec.price_per_product.unlink()
	# 		rec.price_per_product.create({
	# 			'product_id': int(first_prod_id),
	# 			'amount': float(first_prod_amt),
	# 			'product_price_id': rec.id
	# 			})
	# 		rec.price_per_product.create({
	# 			'product_id': int(second_prod_id),
	# 			'amount': float(second_prod_amt),
	# 			'product_price_id': rec.id
	# 			})
	# 		count += 1