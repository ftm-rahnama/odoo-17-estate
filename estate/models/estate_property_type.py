from odoo import fields, models, api


class EstatePropertyType(models.Model):
	_name = "estate.property.type"
	_description = "Estate Property Type Model"
	property_ids = fields.One2many("estate.property", "property_type_id")
	_sql_constraints = [
		('property_type_uniq', 'UNIQUE (name)', 'property type must be unique.')]
	_order = "name desc"
	name = fields.Char(required=True)
	sequence = fields.Integer('Sequence', default=1, help="Used to order stages. Lower is better.")
	offer_ids = fields.One2many("estate.property.offer", 'property_type_id')
	offer_count = fields.Integer(compute="_compute_offer")

	@api.depends('offer_ids', 'offer_count')
	def _compute_offer(self):
		for record in self:
			# record.offer_count = record.offer_ids.search([(1, '=', 1)], count=True)
			record.offer_count = len(record.offer_ids)
