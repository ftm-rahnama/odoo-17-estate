from odoo import fields, models


class EstatePropertyTag(models.Model):
	_name = "estate.property.tag"
	_description = "Estate Property Tag Model"
	_sql_constraints = [
		('name_uniq', 'UNIQUE (name)', 'tag name must be unique.')]
	_order = "name desc"
	name = fields.Char(required=True)
	color = fields.Integer()


