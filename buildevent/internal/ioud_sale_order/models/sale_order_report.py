# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

class SaleReport(models.Model):
    _inherit = "sale.report"

    branch_id = fields.Many2one('ioud_branches.ioud_branches',string='Branch')

    def _select(self):
        return super(SaleReport, self)._select() + ", s.branch_id"

    def _group_by(self):
        return super(SaleReport, self)._group_by() + ", s.branch_id"

