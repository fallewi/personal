odoo.define('ioud_sale_order.qr_code_scanner', function (require){
"use strict";
//
//var form_widget = require('web.form_widgets');
//var FormView = require('web.FormView');
//
//var Mobile = require('web_mobile.rpc');
//
//var Model = require('web.Model');
//var ajax = require('web.ajax');
//var core = require('web.core');
//
//var _t = core._t;
//var QWeb = core.qweb;
//
//FormView.include({
//// 	load_defaults: function () {
//// 		var self = this;
//// 		this._super();
//// 		self.session.user_has_group('ioud_sale_order.group_qr_code').then(function(has_group){
//// 			console.log(">>>>>has_group",has_group)
//// 			if (has_group){
//// 				if (self.model === 'sale.order'){
//// 					setTimeout(function(){
//// 						self.on_button_save();
//// 					}, 1200);
//// 				}
//// 			}
//// 		});
//// 	},
//	
//	load_defaults: function () {
//		var self = this;
//		var keys = _.keys(this.fields_view.fields);
//		self.session.user_has_group('ioud_sale_order.group_qr_code').then(function(has_group){
//			console.log(">>>>>has_group",has_group)
//			if (has_group){
//				if (self.model === 'sale.order'){
//					setTimeout(function(){
//						self.on_button_save();
//					}, 1200);
//				}
//			}
//		});
//		if (keys.length) {
//			return this.dataset.default_get(keys).then(function(r) {
//				self.trigger('load_record', _.clone(r));
//			});
//		}
//		return $.when().then(this.trigger.bind(this, 'load_record', {}));
//	},
//
//})
//
//form_widget.WidgetButton.include({
//	on_click: function() {
//		var self = this
//		var SaleOrder = new Model('sale.order');
//		self.session.user_has_group('ioud_sale_order.group_qr_code').then(function(has_group){
//			if (has_group){
//				if((self.node.attrs.custom === "codescanner") && (self.view.model === 'sale.order')){
//					Mobile.methods.scanBarcode().then(function(code){
//						if(code){
//							//var code = {};
//							SaleOrder.call('action_qr_scan',[[self.view.datarecord.id], code]).then(function(result) {
//								self.do_notify(result);
//								setTimeout(function(){
//									window.location.reload();
//								}, 1000);
//							});
//		 				}else{
//		 					self.do_notify('Your QR Code Wrong...Not Get Data');
//		 					//SaleOrder.call('action_qr_delete',[[self.view.datarecord.id]])
//		 					//window.location.reload();
//		 				}
//		 			});
//				}
//			}
//		});
//
//		this._super();
//		},
//	});
});

// 					ajax.jsonRpc("/ajax/scandata", 'call', {
// 						'id':self.view.datarecord.id,
// 						'code':{}
// 					}).then(function(res){});
