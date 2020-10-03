# -*- coding: utf-8 -*-

from odoo import models, fields, api


class RegionConfiguration(models.Model):
	_name = 'region.config'
	_description = 'Region Config'
	
	name = fields.Char('Region Name')
	cities_id = fields.One2many('region.cities','region_id','Cities')



class RegionCities(models.Model):
	_name = 'region.cities'
	_description = 'region Cities'
	
	name = fields.Char('City Name')
	region_id = fields.Many2one('region.config','Region ID')