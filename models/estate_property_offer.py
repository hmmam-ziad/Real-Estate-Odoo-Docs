# ------------------------------------------------------------
# Author      : HmMam Alsukhni
# Created     : 27 August 2026 | 10:45 PM (GMT+3)
# Module      : Estate
# File        : estate_property_offer.py
# Purpose     : Defines the Estate Property Offer model and manages
#               property offer information.
# ------------------------------------------------------------

from odoo import fields, models
from odoo.exceptions import UserError

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