from datetime import date, timedelta
from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round

class EstateProperty(models.Model):
	_name = "estate.property"
	_description = "Estate Property Model"
	_sql_constraints = [
		('check_expected_price', 'CHECK(expected_price > 0)', 'The expected price must be strictly positive'),
		('check_selling_price', 'CHECK(selling_price >= 0)', 'The selling price selling price must be positive'),
	]
	_order = "id desc"
	name = fields.Char(required=True)
	description = fields.Char()
	postcode = fields.Char()
	date_availability = fields.Datetime(copy=False, default=lambda self: (date.today() + timedelta(days=90)).strftime('%Y-%m-%d'))
	expected_price = fields.Float(required=True)
	selling_price = fields.Float(readonly=True, copy=False)
	bedrooms = fields.Integer(default=2)
	living_area = fields.Integer()
	facades = fields.Integer()
	garage = fields.Boolean()
	garden = fields.Boolean()
	garden_area = fields.Integer()
	garden_orientation = fields.Selection(selection=[('North', 'North'), ('South', 'South'), ('East', 'East'), ('West', 'West')])
	state = fields.Selection(selection=[('New', 'New'), ('Offer Received', 'Offer Received'), ('Offer Accepted', 'Offer Accepted'), ('Sold', 'Sold'), ('Canceled', 'Canceled')], required=True, copy=False, default='New')
	active = fields.Boolean(default=True)
	property_type_id = fields.Many2one("estate.property.type", string="Property Type")
	buyer = fields.Many2one("res.partner", copy=False)
	salesman = fields.Many2one('res.users', string='salesman', default=lambda self: self.env.user)
	tag_ids = fields.Many2many("estate.property.tag", string="Property Tags")
	offer_ids = fields.One2many("estate.property.offer", 'property_id', string="Property Offer")
	total_area = fields.Float(compute="_compute_total_area")
	best_price = fields.Float(compute="_compute_best_price")




	@api.depends('living_area', 'garden_area')
	def _compute_total_area(self):
		for record in self:
			record.total_area = record.garden_area + record.living_area

	@api.depends("offer_ids.price")
	def _compute_best_price(self):
		for rec in self:
			rec.best_price = max(rec.offer_ids.mapped('price')) if rec.offer_ids else 0.0

	@api.onchange("garden")
	def _onchange_garden(self):
		if self.garden:
			self.garden_area = 10
			self.garden_orientation = "North"
		else:
			self.garden_area = 0
			self.garden_orientation = False

	def action_sold(self):
		if "canceled" in self.mapped("state"):
			raise UserError("Canceled properties cannot be sold.")
		return self.write({"state": "Sold"})

	def action_cancel(self):
		if "sold" in self.mapped("state"):
			raise UserError("Sold properties cannot be canceled.")
		return self.write({"state": "Canceled"})

	@api.constrains("expected_price", "selling_price")
	def _check_price(self):
		for rec in self:
			if (not float_is_zero(rec.selling_price, precision_rounding=0.01) and float_compare(rec.selling_price, rec.expected_price * .9, precision_rounding=0.01) < 0):
				raise ValidationError("The selling price must be at least 90% of the expected price! You must reduce the expected price if you want to accept this offer.")

	@api.ondelete(at_uninstall=False)
	def unlink_if_not_cancel_new(self):
		if(self.state not in ['New', 'Canceled']):
			raise UserError("Can't delete new or canceled state")

