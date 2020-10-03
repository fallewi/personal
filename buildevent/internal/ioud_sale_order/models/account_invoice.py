# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError

MAP_INVOICE_TYPE_PARTNER_TYPE = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
}

class AccountMoveInherit(models.Model):
	_inherit = 'account.move'

	branch_id = fields.Many2one('ioud_branches.ioud_branches',string="Branch")
	# po_reference = fields.Char(string="PO Ref")
	# customer_shipping_cost = fields.Float(string="Customer's Cost")
	company_shipping_cost = fields.Float(string="Company Cost")
	# ext_type_of_cust = fields.Selection(related="partner_id.ext_type_of_cust",string="Customer Type",store=True)

	@api.model
	def _default_debit_account_id(self):
		debit_account_id = self.env['ir.values'].get_default('res.config.settings', 'debit_account_id')
		return self.env['account.account'].browse(debit_account_id)

	@api.model
	def _default_credit_account_id(self):
		credit_account_id = self.env['ir.values'].get_default('res.config.settings', 'credit_account_id')
		return self.env['account.account'].browse(credit_account_id)

	@api.model
	def _default_shipping_journal_id(self):
		shipping_journal_id = self.env['ir.values'].get_default('res.config.settings', 'shipping_journal_id')
		return self.env['account.journal'].browse(shipping_journal_id)


	def genrateJournalEntries(self, journal_id, date):
		JornalEntries = self.env['account.move']
		create_journal_entry = JornalEntries.create({
				'journal_id': journal_id,
				'date':date,
				})
		return create_journal_entry
        
	def genrateJournalEntriyLines(self, move_id ,account_id, partner_id, name, amount, deb_amount):
		JornalEntries_lines = self.env['account.move.line']
		if deb_amount:
			move_id.line_ids.create({
				'account_id':account_id,
				'partner_id':partner_id,
				'name': str(name), 
				'debit':0,
				'credit':amount,
				'move_id':move_id.id
				})
		else:
			move_id.line_ids.create({
				'account_id':account_id,
				'partner_id':partner_id,
				'name': str(name), 
				'debit':amount,
				'credit':0,
				'move_id':move_id.id
				})
		# create_journal_entry.post()

	def action_invoice_open(self):
		res = super(AccountMoveInherit, self).action_invoice_open()

		DebitAccount = self._default_debit_account_id()
		CreditAccount = self._default_credit_account_id()
		JournalAccount = self._default_shipping_journal_id()
		if DebitAccount and CreditAccount and JournalAccount:
			if self.company_shipping_cost > 0:
				JournalEntry = self.genrateJournalEntries(JournalAccount.id, self.date)
				self.genrateJournalEntriyLines(JournalEntry, DebitAccount.id, False, 'Debit', self.company_shipping_cost, False)
				self.genrateJournalEntriyLines(JournalEntry, CreditAccount.id, False, 'Credit', self.company_shipping_cost, True)
# 		sale_order = self.env['sale.order'].search([('name', '=', self.origin)]);print ("sale_order",sale_order)
# 		if sale_order:
# 			sale_order[0].validate_sale_delivery()
		return res

	def confirm_invoice_controller_method(self):
		self.action_invoice_open()
		sale_order = self.env['sale.order'].search([('name','=',self.origin)])
		delivery_order = self.env['stock.picking'].search([('origin','=',self.origin)]) 
		if sale_order and delivery_order:
			#appliying done qty in stock.picking
			for line in delivery_order.pack_operation_product_ids:
				line.qty_done = line.product_qty
			# transfering new stock 
			if delivery_order.state == 'assigned':
				delivery_order.do_new_transfer()
		return True

	# def send_mail_wmg(self, email_to, receiver, SO, salesperson):
	# 	mail_pool = self.env['mail.mail']
	# 	values={}
	# 	html_body = """<div summary="o_mail_template" style="padding:0px;width:600px;margin:auto;background: #FFFFFF repeat top /100%;color:#777777">
	# 					<div>
	# 					Dear {receiver}
	# 					An Invoice has been approved against the SO {SO} for the salesman {salesperson}, please validate the Delivery order.
	# 					</div>
	# 						<div>
	# 							<hr width="100%" style="background-color:rgb(204,204,204);border:medium none;clear:both;display:block;font-size:0px;min-height:1px;line-height:0;margin:15px auto;padding:0">
	# 						</div>
	# 						<table cellspacing="0" cellpadding="0" style="width:600px;background:inherit;color:inherit">
	# 							<tbody><tr>
	# 								<td valign="center" width="200" style="padding:10px 10px 10px 5px;font-size: 12px">
	#
	# 								</td>
	# 							</tr></tbody>
	# 						</table>
	# 					</div>"""
	# 	body = html_body.format(receiver=receiver.encode('utf-8'),SO=SO.encode('utf-8'),salesperson=salesperson.encode('utf-8'))
	# 	values.update({'subject': 'Notification of Quotation'})
	# 	values.update({'email_to': email_to})
	# 	values.update({'body_html': body })
	# 	values.update({'body': body })
	# 	msg_id = mail_pool.create(values)
	# 	# And then call send function of the mail.mail,
	# 	if msg_id:
	# 		mail_pool.send([msg_id])


	# def _getMailingGroup(self, domain):
	# 	mailing_group = self.env['ioud_email_alerts.ioud_email_alerts'].search([('name','=',domain)])
	# 	return mailing_group


class AccountPaymentInherit(models.Model):
	_inherit = 'account.payment'
	
	# @api.model
	# def default_get(self, fields):
	# 	rec = super(AccountPaymentInherit, self).default_get(fields)
	# 	invoice_defaults = self.resolve_2many_commands('invoice_ids', rec.get('invoice_ids'))
	# 	invoice = invoice_defaults[0]
	# 	rec['currency_id'] = invoice['currency_id'][0]
	# 	rec['payment_type'] = invoice['type'][0] in ('out_invoice', 'in_refund') and 'inbound' or 'outbound'
	# 	rec['partner_type'] = MAP_INVOICE_TYPE_PARTNER_TYPE[invoice['type']]
	# 	rec['partner_id'] = invoice['partner_id'][0]
	# 	rec['amount'] = sum(line['residual'] for line in invoice_defaults)
	# 	return rec
