# -*- coding: utf-8 -*-
{
    'name': "ioud_sale_order",

    'summary': """
        This module is for customization of sale for iOud """,

    'description': """
        This module is for customization of sale for iOud
    """,

    'author': "SolutionFounder",
    'website': "http://www.solutionfounder.com",
    
    # for the full list
    'category': 'sale',
    'version': '13.4.23',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','delivery'],

    # always loaded
    'data': [
        # 'data/partner_sequnce.xml',
        'security/user_groups.xml',
        'security/ir.model.access.csv',
        'views/branches.xml',
        'views/account_invoice_view.xml',
        'views/sale_order_view.xml',
        'views/res_partner_view.xml',
        'views/region_config_view.xml',
        # 'views/config.xml',
        # 'views/stcok.xml',
#         
         #Backend View Load - JS
      #  'views/assets.xml'
    ],
    # only loaded in demonstration mode
}
