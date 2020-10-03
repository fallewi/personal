# -*- coding: utf-8 -*-
import odoo.http as http

from odoo.http import request

import logging
import pprint

_logger = logging.getLogger(__name__)

class IoudSaleOrder(http.Controller):
    
    @http.route('/ajax/scandata', type='json', auth='user')
    def ajax_update_json(self, id=None, code=None):
        _logger.info('\n\n SCAN OPPP DATAAAA %s %s', code, id)
        if code and id:
            Order_id = request.env['sale.order'].browse(int(id))
            raw_data =[line.split('=') for line in code['data'].split(',')]
            partner_id = None
            product_id = None
            rack_id = None
            model = None
            rack_record = False
            print (raw_data)
            for line in raw_data:
                if line[0] == 'partner_id':
                    partner_id = line[1]
                elif line[0] == 'product_id':
                    product_id = line[1]
                elif line[0] == 'rack_id':
                    rack_id = line[1]
                elif line[0] == 'model':
                    model = line[1]
            if rack_id and partner_id:
                RacksID = request.env['rack_qr_inventory'].browse(int(rack_id)) 
                Order_id.write({'partner_id':partner_id,'branch_id':RacksID.ioud_branch_id.id,'state':'draft'})
                Order_id.onchange_partner_id()
                try:
                    request.env['sale.order.line'].create({'order_id':Order_id.id,'product_id':int(product_id)})
                    return 'sucess'
                except Exception as e:
                    return e
