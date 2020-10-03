# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

import logging
import pprint

_logger = logging.getLogger(__name__)

import traceback

class SaleOrderInherit(models.Model):
	_inherit = 'sale.order'
	
	@api.model
	def default_get(self, fields):
		res = super(SaleOrderInherit, self).default_get(fields)
		pricelist_id = self.env['product.pricelist'].search([('id','=',1)])
		res['pricelist_id'] = pricelist_id.id if pricelist_id else False
		res['currency_id'] = pricelist_id.currency_id.id if pricelist_id else False
		if self.env.user.has_group('ioud_sale_order.group_qr_code'):
			res['state'] = 'scan'
		else:
			res['state'] = 'draft'
		return res
	
	state = fields.Selection([
		('scan', 'Scan'),
		('confirm', 'Confirm'),
		('draft', 'Quotation'),
		('sent', 'Quotation Sent'),
		('sale', 'Sales Order'),
		('done', 'Locked'),
		('cancel', 'Cancelled'),
		], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange')
	branch_id = fields.Many2one('ioud_branches.ioud_branches',string="Branch")
	# po_reference = fields.Char(string="PO Ref")
	# customer_shipping_cost = fields.Float(string="Customer's Cost")
	company_shipping_cost = fields.Float(string="Company Cost")
	allow_unit_price = fields.Boolean(string="Allow Price Modification")
	partner_id = fields.Many2one('res.partner', string='Customer', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, required=False, change_default=True, index=True, track_visibility='always')
	partner_invoice_id = fields.Many2one('res.partner', string='Invoice Address', readonly=True, required=False, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, help="Invoice address for current sales order.")
	partner_shipping_id = fields.Many2one('res.partner', string='Delivery Address', readonly=True, required=False, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, help="Delivery address for current sales order.")
	pricelist_id = fields.Many2one('product.pricelist', string='Pricelist', required=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)],'scan': [('readonly', False)],'confirm': [('readonly', False)]}, help="Pricelist for current sales order.")
	shipping_price = fields.Float(string='Estimated Delivery Price', )
	is_invoiced = fields.Boolean('Is Invoiced')

	# function in order to hide the invoice order from sale order action
	@api.model
	def hide_invoice_orders_from_actions(self):
		if self.env.ref('sale.sale_order_line_make_invoice'):
			self.env.ref('sale.sale_order_line_make_invoice').unlink()
	
	
	def _prepare_invoice(self):
		dict_obj = super(SaleOrderInherit, self)._prepare_invoice()
		dict_obj.update({
			'branch_id': self.branch_id.id,
			# 'po_reference': self.po_reference,
			# 'customer_shipping_cost': self.customer_shipping_cost,
			'company_shipping_cost': self.company_shipping_cost,
			})
		return dict_obj
	
	def action_scan_data(self):
		return True
	
	def action_confirm(self):
		res = super(SaleOrderInherit, self).action_confirm()
		# creation of invoice on confirmation

		for order in self:
			warehouse = order.warehouse_id
			if order.picking_ids:
				for picking in self.picking_ids:
					picking.action_assign()
					picking.action_confirm()
					for mv in picking.move_ids_without_package:
						mv.quantity_done = mv.product_uom_qty
					picking.button_validate()

		# self.validate_sale_delivery()
		self.create_direct_invoice()
		self.invoice_ids.action_post()
		self.invoice_ids.write({'state':'waiting_for_delivery'})
		return res

	# @api.model
	# def create(self,vals):
	# 	res = super(SaleOrderInherit, self).create(vals)
	# 	if self.env.user.has_group('ioud_sale_order.group_qr_code') and res.order_line:
	# 		mailing_group = self._getMailingGroup('Line Manager')
	# 		for line in mailing_group.email_user_ids:
	# 			mailing_group.to_mails = line.login
	# 			mailing_group.mail_user = line.name
	# 			self.send_mail_custom(line.login, line.name, res.user_id.name, res.partner_id.name, res.amount_total, res.id)
	# 	return res
	
	def write(self, vals):
		res = super(SaleOrderInherit, self).write(vals)
		for l in self.order_line:
			l.action_check_price()
		return res
	
	def create_direct_invoice(self):
		if self.id:
			invoice = self._create_invoices()
			# mailing_group = self._getMailingGroup('Head of Sales')
			# for line in mailing_group.email_user_ids:
			# 	mailing_group.to_mails = line.login
			# 	mailing_group.mail_user = line.name
			# 	self.send_mail_ceo(line.login, line.name, self.user_id.name, self.partner_id.name, self.amount_total, invoice[0], self.name)

	# @api.onchange('partner_id')
	# def onchange_partner_id(self):
	# 	res = super(SaleOrderInherit, self).onchange_partner_id()
	# 	if self.partner_id:
	# 		warehouse = self.env['stock.warehouse'].search([('user_ids','in',self.env.user.id)])
	# 		if warehouse:
	# 			self.warehouse_id = warehouse[0].id
	# 	return res
	
	#QR-code scanner Data - JS
# 	def action_qr_scan(self, code):
# 		_logger.info('\n\n SCAN OPPP DATAAAA %s', pprint.pformat(code))
# 		for Order_id in self:
# 			#code = {u'data': u'partner_id=620,product_id=2,rack_id=292,model=ioud_branches.ioud_branches', u'success': True}
# 			raw_data =[line.split('=') for line in code['data'].split(',')]
# 			partner_id = None
# 			product_id = None
# 			rack_id = None
# 			model = None
# 			rack_record = False
# 			print (raw_data)
# 			for line in raw_data:
# 				if line[0] == 'partner_id':
# 					partner_id = line[1]
# 				elif line[0] == 'product_id':
# 					product_id = line[1]
# 				elif line[0] == 'rack_id':
# 					rack_id = line[1]
# 				elif line[0] == 'model':
# 					model = line[1]
# 			partner_id = self.env['ioud_branches.ioud_branches'].browse(int(partner_id)).head_office.id
# 			line_id = False
# 			if rack_id and partner_id:
# 				RacksID = self.env['rack_qr_inventory'].browse(int(rack_id))
# 				Order_id.write({'partner_id':partner_id,'branch_id':RacksID.ioud_branch_id.id,'state':'confirm'})
# 				Order_id.onchange_partner_id()
# 				return 'successfully add your product you can check and verify..🙌 '
# # 				try:
# # 					line_id = self.env['sale.order.line'].create({'order_id':Order_id.id,'product_id':int(product_id)})
# # 					return 200
# # 				except Exception as e:
# # 					print ("line_id",line_id)
# # 					raise UserError(
# # 						_('Sorry....' + str(e)), )
# 			else:
# 				raise UserError(
# 						_('Your QR Code Wrong...'), )
#
# 	#QR-code scanner Data - JS
# 	def action_qr_delete(self, code):
# 		self.unlink()
		
	def action_confirm_data(self):
		if self.order_line:
			# mailing_group = self._getMailingGroup('Line Manager')
			# for line in mailing_group.email_user_ids:
			# 	mailing_group.to_mails = line.login
			# 	mailing_group.mail_user = line.name
			# 	self.send_mail_custom(line.login, line.name, self.user_id.name, self.partner_id.name, self.amount_total, self.id)
			self.state = 'draft'
		else:
			raise UserError(
				_('Please Select Order Line....'), )

	# def send_mail_custom(self, email_to, receiver, sender, customer, amount, id):
	# 	mail_pool = self.env['mail.mail']
	# 	base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
	# 	values={}
	# 	html_body = """
	# 			<div summary="o_mail_template" style="padding:0px;width:600px;margin:auto;background: #FFFFFF repeat top /100%;color:#777777">
	# 					<div>
	# 					<p align="right">{receiver} عزيزي مدير المبيعات</p>
	# 					<p align="right">{sender} امر بيع تم ان شاءه بواسطه {customer} للعميل</p>
	# 					<p align="right">باجمالي قيمة {amount} كيف تريد التنفيذ ؟</p>
	# 					</div>
	#
	# 					<div>
	# 							Dear {receiver}
	# 						A Sale order has been Created by ({sender}) for Customer ({customer}) with total value of {amount} , How do you wish to proceed ?
	# 					</div>
	# 			<div>
	# 				<hr width="100%" style="background-color:rgb(204,204,204);border:medium none;clear:both;display:block;font-size:0px;min-height:1px;line-height:0;margin:15px auto;padding:0">
	# 			</div>
	# 			<table cellspacing="0" cellpadding="0" style="width:600px;background:inherit;color:inherit">
	# 			    <tbody><tr>
	# 			        <td valign="center" width="200" style="padding:10px 10px 10px 5px;font-size: 12px">
	#
	# 			        </td>
	# 			        <td valign="center" align="right" width="340" style="padding:10px 10px 10px 5px; font-size: 12px;">
	# 			            <p>
	# 			                <a href="{url}/iOud/sale/confirm?id={id}" style="padding: 5px 10px; font-size: 12px; line-height: 18px; color: #FFFFFF; border-color:#875A7B; text-decoration: none; display: inline-block; margin-bottom: 0px; font-weight: 400; text-align: center; vertical-align: middle; cursor: pointer; white-space: nowrap; background-image: none; background-color: #875A7B; border: 1px solid #875A7B; border-radius:3px">Accept</a>
	# 			                <a href="{url}/iOud/sale/declined?id={id}" style="padding: 5px 10px; font-size: 12px; line-height: 18px; color: #FFFFFF; border-color:#875A7B; text-decoration: none; display: inline-block; margin-bottom: 0px; font-weight: 400; text-align: center; vertical-align: middle; cursor: pointer; white-space: nowrap; background-image: none; background-color: #875A7B; border: 1px solid #875A7B; border-radius:3px">Decline</a>
	# 			                <a href="{url}/iOud/sale/view?id={id}" style="padding: 5px 10px; font-size: 12px; line-height: 18px; color: #FFFFFF; border-color:#875A7B; text-decoration: none; display: inline-block; margin-bottom: 0px; font-weight: 400; text-align: center; vertical-align: middle; cursor: pointer; white-space: nowrap; background-image: none; background-color: #875A7B; border: 1px solid #875A7B; border-radius:3px">View</a>
	# 			            </p>
	# 			        </td>
	# 			    </tr></tbody>
	# 			</table>
	# 			</div>
    #             """
	# 	body = html_body.format(url=base_url, id=id,receiver=receiver.encode('utf-8'),sender=sender.encode('utf-8'),customer=customer.encode('utf-8'),amount=amount)
	# 	values.update({'subject': 'Notification of Quotation'})
	# 	values.update({'email_to': email_to})
	# 	values.update({'body_html': body })
	# 	values.update({'body': body })
	# 	msg_id = mail_pool.create(values)
	# 	# And then call send function of the mail.mail,
	# 	if msg_id:
	# 		mail_pool.send([msg_id])
	#
	# def send_mail_salesman(self, email_to, receiver):
	# 	mail_pool = self.env['mail.mail']
	# 	values={}
	# 	body = """<div summary="o_mail_template" style="padding:0px;width:600px;margin:auto;background: #FFFFFF repeat top /100%;color:#777777">
    #                     <div>Dear """+ receiver + """<br>Your Quotation has been Approved, Please Create Invoice
    #                     </div>
    #                         <div>
    #                             <hr width="100%" style="background-color:rgb(204,204,204);border:medium none;clear:both;display:block;font-size:0px;min-height:1px;line-height:0;margin:15px auto;padding:0">
    #                         </div>
    #                         <table cellspacing="0" cellpadding="0" style="width:600px;background:inherit;color:inherit">
    #                             <tbody><tr>
    #                                 <td valign="center" width="200" style="padding:10px 10px 10px 5px;font-size: 12px">
	#
    #                                 </td>
    #                             </tr></tbody>
    #                         </table>
    #                     </div>"""
	# 	values.update({'subject': 'Notification of Quotation'})
	# 	values.update({'email_to': email_to})
	# 	values.update({'body_html': body })
	# 	values.update({'body': body })
	# 	msg_id = mail_pool.create(values)
	# 	# And then call send function of the mail.mail,
	# 	if msg_id:
	# 		mail_pool.send([msg_id])
	#
	# def send_mail_ceo(self, email_to, receiver, sender, customer, amount, id, SO):
	# 	base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
	# 	mail_pool = self.env['mail.mail']
	# 	values={}
	# 	html_body = """
	# 			<div summary="o_mail_template" style="padding:0px;width:600px;margin:auto;background: #FFFFFF repeat top /100%;color:#777777">
	# 					<div>
	# 					<p align="right">{receiver} عزيزي المدير العام</p>
	# 					<p align="right">{sender} موظف المبيعات {SO} انشأ فاتورة رقم {customer} للعميل</p>
	# 					<p align="right"> بقيمة اجمالية {amount} هل توافق؟</p>
	# 					</div>
	# 				<div>Dear {receiver}
	# 				A Salesperson {sender} Created an invoice for {SO}
	# 				and for customer {customer} with total value of {amount}
	# 				</div>
	# 			<div>
	# 			    <hr width="100%" style="background-color:rgb(204,204,204);border:medium none;clear:both;display:block;font-size:0px;min-height:1px;line-height:0;margin:15px auto;padding:0">
	# 			</div>
	# 			<table cellspacing="0" cellpadding="0" style="width:600px;background:inherit;color:inherit">
	# 			    <tbody><tr>
	# 			        <td valign="center" width="200" style="padding:10px 10px 10px 5px;font-size: 12px">
	# 			        <p>Do you Approve ?</>
	# 			        </td>
	# 			        <td valign="center" align="right" width="340" style="padding:10px 10px 10px 5px; font-size: 12px;">
	# 			            <p>
	# 			                <a href="{url}/iOud/invoice/confirm?id={id}" style="padding: 5px 10px; font-size: 12px; line-height: 18px; color: #FFFFFF; border-color:#875A7B; text-decoration: none; display: inline-block; margin-bottom: 0px; font-weight: 400; text-align: center; vertical-align: middle; cursor: pointer; white-space: nowrap; background-image: none; background-color: #875A7B; border: 1px solid #875A7B; border-radius:3px">Accept</a>
	# 			                <a href="{url}/iOud/invoice/declined?id={id}" style="padding: 5px 10px; font-size: 12px; line-height: 18px; color: #FFFFFF; border-color:#875A7B; text-decoration: none; display: inline-block; margin-bottom: 0px; font-weight: 400; text-align: center; vertical-align: middle; cursor: pointer; white-space: nowrap; background-image: none; background-color: #875A7B; border: 1px solid #875A7B; border-radius:3px">Decline</a>
	# 			                <a href="{url}/iOud/invoice/view?id={id}" style="padding: 5px 10px; font-size: 12px; line-height: 18px; color: #FFFFFF; border-color:#875A7B; text-decoration: none; display: inline-block; margin-bottom: 0px; font-weight: 400; text-align: center; vertical-align: middle; cursor: pointer; white-space: nowrap; background-image: none; background-color: #875A7B; border: 1px solid #875A7B; border-radius:3px">View</a>
	# 			            </p>
	# 			        </td>
	# 			    </tr></tbody>
	# 			</table>
	# 			</div>
    #         	"""
	# 	body = html_body.format(url=base_url, id=id,SO=SO.encode('utf-8'),receiver=receiver.encode('utf-8'),sender=sender.encode('utf-8'),customer=customer.encode('utf-8'),amount=amount)
	# 	values.update({'subject': 'Notification of Invoice Validation'})
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
	#
	#Delivery Order Confirm -  invoice throw 
	def validate_sale_delivery(self):
		if self.picking_ids:
			for pick in self.picking_ids:
				if pick.state == 'assigned':
					pick.min_date = self.validity_date
					pick.action_confirm()
					pick.action_done()
				elif pick.state in ['confirmed','partially_available']:
					pick.min_date = self.validity_date
					pick.force_assign()
					pick.do_transfer()

	# def shipping_set(self):
	# 	# Remove delivery products from the sale order
	# 	self._delivery_unset()
	# 	for order in self:
	# 		carrier = order.carrier_id
	# 		if carrier:
	# 			if order.state not in ('draft', 'sent'):
	# 				raise UserError(_('The order state have to be draft to add delivery lines.'))
	#
	# 			if carrier.delivery_type not in ['fixed', 'base_on_rule']:
	# 			# Shipping providers are used when delivery_type is other than 'fixed' or 'base_on_rule'
	# 				price_unit = order.carrier_id.get_shipping_price_from_so(order)[0]
	# 			else:
	# 			# Classic grid-based carriers
	# 				carrier = order.carrier_id.verify_carrier(order.partner_shipping_id)
	# 			if not carrier:
	# 				raise UserError(_('No carrier matching.'))
	# 			price_unit = carrier.get_price_available(order)
	# 			if order.company_id.currency_id.id != order.pricelist_id.currency_id.id:
	# 				price_unit = order.company_id.currency_id.with_context(date=order.date_order).compute(price_unit, order.pricelist_id.currency_id)
	# 			#final_price = price_unit * (1.0 + (float(self.carrier_id.margin) / 100.0))
	# 			final_price = self.shipping_price
	# 			order._create_delivery_line(carrier, final_price)
	# 		else:
	# 			raise UserError(_('No carrier set for this order.'))
	# 	return True
		
# class SaleOrderLine(models.Model):
# 	_inherit = 'sale.order.line'
#
# 	@api.model
# 	def create(self, vals):
# 		res = super(SaleOrderLine, self).create(vals)
# 		if not self.env.user.has_group('ioud_superuser.group_superuser'):
# 			stock_qty_obj = self.env['stock.quant']
# 			User_warehouse = self.env['stock.warehouse'].search([('user_ids','in',res._uid)])
# 			if res.product_id.type == 'product':
# 				if User_warehouse and len(User_warehouse) < 2:
# 					location_stock = stock_qty_obj.search([('location_id','=',User_warehouse.lot_stock_id.id),('product_id','=',res.product_id.id)])
# 					inhand_qty = sum(line.quantity for line in location_stock)
# 					output = round(res.product_uom_qty, 2)
# 					if inhand_qty <= 0 or output > inhand_qty:
# 						raise UserError(
# 							_('The product qty inhand is less then ordered qty or equal to 0 please update qty before proceed'),
# 						)
# 				else:
# 					raise UserError(
# 							_('You have multiple assosiated users under stock locations one 1 user is allowed.'),
# 						)
# 				customer_products = res.order_id.partner_id.price_per_product
# 				find_product = customer_products.search([('product_id', '=', res.product_id.id), ('product_price_id', '=', res.order_id.partner_id.id)])
# 				print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXx")
# 				print(find_product)
# 				if find_product and not res.order_id.allow_unit_price:
# 					output = round(res.price_unit, 2)
# 					if output != find_product.amount:
# 						raise UserError(
# 							_('You can not modify the Unit Price.'),
# 						)
# 		return res
#
# 	@api.onchange('product_id')
# 	def product_id_change(self):
# 		if not self.order_id.partner_id:
# 			raise UserError(
# 					_('Please select customer or Head of office...!'),
# 				)
# 		else:
# 			res = super(SaleOrderLine, self).product_id_change()
# 			PricePerProduct = self.env['price.per.product']
# 			find_product = PricePerProduct.search([('product_id', '=', self.product_id.id),('product_price_id', '=',self.order_id.partner_id.id)], limit=1)
# 			if find_product:
# 				self.update({'price_unit':find_product.amount})
# 			return res
#
# 	@api.onchange('product_uom', 'product_uom_qty')
# 	def product_uom_change(self):
# 		super(SaleOrderLine, self).product_uom_change()
# 		PricePerProduct = self.env['price.per.product']
# 		find_product = PricePerProduct.search([('product_id', '=', self.product_id.id),('product_price_id', '=',self.order_id.partner_id.id)], limit=1)
# 		if find_product:
# 			self.update({'price_unit':find_product.amount})
#
# 	@api.onchange('price_unit')
# 	def product_price_unit_change(self):
# 		PricePerProduct = self.env['price.per.product']
# 		find_product = PricePerProduct.search([('product_id', '=', self.product_id.id),('product_price_id', '=',self.order_id.partner_id.id)], limit=1)
# 		if find_product:
# 			self.update({'price_unit':find_product.amount})
#
# 	def action_check_price(self):
# 		for res in self:
# 			customer_products = res.order_id.partner_id.price_per_product
# 			find_product = customer_products.search([('product_id', '=', res.product_id.id), ('product_price_id', '=', res.order_id.partner_id.id)])
# 			print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXx")
# 			print(find_product.amount)
# 			print(res.price_unit)
# 			if find_product and not res.order_id.allow_unit_price:
# 				output = round(res.price_unit, 2)
# 				if output != find_product.amount:
# 					raise UserError(
# 						_('You can not modify the Unit Price. : - " %s "') % (res.name),
# 					)
