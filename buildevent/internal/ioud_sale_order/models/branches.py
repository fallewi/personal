# -*- coding: utf-8 -*-

from odoo import models, fields, api

class IoudBranches(models.Model):
	_name = 'ioud_branches.ioud_branches'
	_description = 'Ioud Branches'
	_rec_name = 'record_name'
	
	image = fields.Binary(string="Image")
	name = fields.Char()
	head_office = fields.Many2one('res.partner',string="Customer")
	street = fields.Char()
	street2 = fields.Char()
	city = fields.Many2one('region.cities',"City")
	state_id = fields.Many2one('res.country.state',string='State')
	state_zip = fields.Char()
	country_id = fields.Many2one('res.country',string="Country")
	website = fields.Char()
	category_id = fields.Many2one('res.partner.category',string="Tags")
	phone = fields.Char()
	mobile = fields.Char()
	fax = fields.Char()
	email = fields.Char()
	arabic_name = fields.Char(string="Arabic Name")
	branch_no = fields.Char(string="Branch No")
	stand_qty = fields.Float(string="Stand Qty")
	stand_rent = fields.Float(string="Stand Rent")
	region = fields.Many2one('region.config',string="Region")
	user_id = fields.Many2one('res.users',string="Salesperson", default=lambda self: self.env.user)


	record_name = fields.Char(compute="_compute_name",string="Name")
	# compute and search fields, in the same order of fields declaration
	
	def _compute_name(self):
		for rec in self:	
			rec.record_name = rec.name or rec.arabic_name or 'Name not defined'

	@api.model
	def name_search(self, name, args=None, operator='ilike', limit=100):
		args = args or []
		recs = self.browse()
		if name:
			recs = self.search([('arabic_name', '=', name)] + args, limit=limit)
		if not recs:
			recs = self.search([('name', operator, name)] + args, limit=limit)
		return recs.name_get()