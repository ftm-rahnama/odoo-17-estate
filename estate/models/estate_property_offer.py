from datetime import timedelta
from odoo import fields, models, api
from odoo.exceptions import UserError
from odoo.tools import float_compare

class EstatePropertyOffer(models.Model):
	_name = "estate.property.offer"
	_description = "Estate Property offer Model"

	price = fields.Float()
	status = fields.Selection(selection=[('Accepted', 'Accepted'), ('Refused', 'Refused')], copy=False)
	partner_id = fields.Many2one("res.partner", required=True)
	property_id = fields.Many2one("estate.property", required=True)
	property_type_id = fields.Many2one("estate.property.type", related="property_id.property_type_id", store=True)
	validity = fields.Integer(default=7)
	date_deadline = fields.Date(compute="_compute_deadlines", inverse="_inverse_deadlines")

	_sql_constraints = [
		('check_price', 'CHECK(price > 0)', 'The offer price must be strictly positive'),
	]
	_order = "price desc"
	@api.depends("create_date", "validity", "date_deadline")
	def _compute_deadlines(self):
		for record in self:
			date = record.create_date.date() if record.create_date else fields.Date.today()
			record.date_deadline = timedelta(days=record.validity) + date

	def _inverse_deadlines(self):
		for record in self:
			date = record.create_date.date() if record.create_date else fields.Date.today()
			record.validity = (record.date_deadline - date).days

	def action_confirm(self):
		if "Accepted" in self.mapped("status"):
			raise UserError("An offer as already been accepted.")
		self.write({"status": "Accepted"})
		return self.mapped("property_id").write(
			{
				"state": "Offer Accepted",
				"selling_price": self.price,
				"buyer": self.partner_id,
			}
		)

	def action_refuse(self):
		return self.write({"status": "Refused"})

	@api.model
	def create(self, vals):
		if vals.get("property_id") and vals.get("price"):
			rec = self.env["estate.property"].browse(vals["property_id"])
			if rec.offer_ids:
				max_offer = max(rec.mapped("offer_ids.price"))
				if float_compare(vals["price"], max_offer, precision_rounding=0.01) <= 0:
					raise UserError("The offer must be higher than %.2f" % max_offer)
			rec.state = "Offer Received"
		return super().create(vals)
