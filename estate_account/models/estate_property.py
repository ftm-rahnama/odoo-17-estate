from odoo import fields, models, Command

class EstateProperty(models.Model):
	_inherit = "estate.property"

	def action_sold(self):
		journal = self.env["account.journal"].search([("type", "=", "sale")], limit=1)
		for rec in self:
			self.env["account.move"].create(
				{
					"partner_id": rec.buyer.id,
					"move_type": "out_invoice",
					"journal_id": journal.id,
					"invoice_line_ids": [
						Command.create({
							"name": rec.name,
							"quantity": 1.0,
							"price_unit": rec.selling_price * 0.06,
						}),
						Command.create({
							"name": "administrative fees",
							"quantity": 1.0,
							"price_unit": 100.0,
						}),
					],
				}
			)
		return super().action_sold()
