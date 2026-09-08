# ------------------------------------------------------------
# Author      : HmMam Alsukhni
# Created     : 8-09-2026 | 05:36 PM (GMT+3)
# Module      : Res Partner Extension
# File        : res_partner.py
# Purpose     : Extends the res.partner model to include a 
#               relationship with estate properties, allowing 
#               tracking of properties bought by partners.
# ------------------------------------------------------------

from odoo import fields, models

class ResPartner(models.Model):
    """
    Extends the standard res.partner model with a relationship
    to real estate properties purchased by the partner.

    This allows users to view all properties associated with a
    partner as the buyer directly from the partner record.
    """

    _inherit = "res.partner"

    # --------------------------------------------------------
    # Property Relationships
    # --------------------------------------------------------

    # List of properties purchased by this partner.
    # The inverse relationship is defined by the "buyer_id"
    # field on the estate.property model.
    property_ids = fields.One2many("estate.property", "buyer_id", string="Properties Bought")