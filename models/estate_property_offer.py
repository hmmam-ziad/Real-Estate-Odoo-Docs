# ------------------------------------------------------------
# Author      : HmMam Alsukhni
# Created     : 27 August 2026 | 10:45 PM (GMT+3)
# Module      : Estate
# File        : estate_property_offer.py
# Purpose     : Defines the Estate Property Offer model and manages
#               property offer information.
# ------------------------------------------------------------

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

class EstatePropertyOffer(models.Model):
    """ 
    Represents an offer submitted by a customer for a real estate property. 

    An offer is associated with both a property and a customer. It can be either accepted or refused. 
    When an offer is accepted, the related property's selling price, buyer, and status are automatically updated. 
    """
    _name = "estate.property.offer"
    _description = "Real Estate Property Offer"

    # -------------------------------------------------------- 
    # Offer Information 
    # --------------------------------------------------------

    # Amount offered by the customer for the property.
    price = fields.Float(string="Price")

    # Current status of the offer.
    # The status is intentionally not copied when duplicating an offer.
    status = fields.Selection(
        selection=[
            ('accepted', 'Accepted'),
            ('refused', 'Refused'),
        ],
        string="Status",
        copy=False,
    )

    # -------------------------------------------------------- 
    # Relationships 
    # --------------------------------------------------------

    # Customer who submitted the offer.
    # The partner must be specified before an offer can be created.
    partner_id = fields.Many2one("res.partner", string="Partner", required=True)
    # Property for which the offer was submitted.
    # Deleting the property automatically removes its related offers.
    property_id = fields.Many2one("estate.property", string="Property", required=True, ondelete="cascade")

    # --------------------------------------------------------
    # Database Constraints
    # --------------------------------------------------------

    # Prevent an offer amount of zero or less from ever being stored.
    _check_price_positive = models.Constraint(
        "CHECK(price > 0)",
        "The offer price must be strictly positive."
    )

    # --------------------------------------------------------
    # CRUD Overrides
    # --------------------------------------------------------

    @api.model_create_multi
    def create(self, vals_list):
        """
        Create new offers and keep the related property's status and
        offers in sync.

        When a property receives its first offer it moves to the
        "Offer Received" state. A new offer is also rejected if it is
        lower than the current best offer already submitted for the
        same property, matching normal negotiation behaviour.
        """
        for vals in vals_list:
            if vals.get("property_id"):
                prop = self.env["estate.property"].browse(vals["property_id"])
                if prop.state in ("sold", "canceled"):
                    raise UserError("You cannot make an offer on a property that is sold or canceled.")
                if prop.offer_ids and vals.get("price", 0) <= prop.best_price:
                    raise ValidationError(
                        f"The offer must be higher than the current best offer ({prop.best_price})."
                    )
        offers = super().create(vals_list)
        offers.mapped("property_id").filtered(
            lambda p: p.state == "new"
        ).write({"state": "offer_received"})
        return offers

    # -------------------------------------------------------- 
    # Offer Actions 
    # --------------------------------------------------------

    def action_accept(self):
        """ 
        Accept the offer and update the related property.

        Only one offer can be accepted for a property. When the offer
        is accepted, the property's selling price, buyer, and status
        are updated accordingly.
        """

        for record in self:
            # Prevent accepting more than one offer for the same property.
            if "accepted" in record.property_id.offer_ids.mapped("status"):
                raise UserError("An offer for this property is already accepted.")
            # Mark the current offer as accepted.
            record.status = "accepted"

            # Automatically refuse every other pending offer on the
            # same property, since only one offer can win.
            other_offers = record.property_id.offer_ids - record
            other_offers.filtered(lambda o: o.status != "refused").write({"status": "refused"})

            # Update the property's selling price with the accepted offer.
            record.property_id.selling_price = record.price

            # Set the customer who submitted the accepted offer as the buyer.
            record.property_id.buyer_id = record.partner_id

            # Move the property to the "Offer Accepted" state.
            record.property_id.state = "offer_accepted"
        return True

    def action_refuse(self):
        """
        Refuse the selected offer.

        The offer status is changed to "refused" without modifying
        the related property's information.
        """
        for record in self:
            # Mark the current offer as refused.
            record.status = "refused"
        return True