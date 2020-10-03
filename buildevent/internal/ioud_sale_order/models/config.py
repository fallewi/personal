# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ShippingConfiguration(models.TransientModel):
	_inherit = 'res.config.settings'

	debit_account_id = fields.Many2one('account.account',string="Debit Account")
	credit_account_id = fields.Many2one('account.account',string="Credit Account")
	shipping_journal_id = fields.Many2one('account.journal', string="Journal")

	def set_import_balance_debit_account_id(self):
		return self.env['ir.values'].sudo().set_default(
			'res.config.settings', 'debit_account_id', self.debit_account_id.id)

	def set_import_balance_credit_account_id(self):
		return self.env['ir.values'].sudo().set_default(
			'res.config.settings', 'credit_account_id', self.credit_account_id.id)

	def set_import_balance_journal_id(self):
		return self.env['ir.values'].sudo().set_default(
			'res.config.settings', 'shipping_journal_id', self.shipping_journal_id.id)