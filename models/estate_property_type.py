# ------------------------------------------------------------
# Author      : HmMam Alsukhni
# Created     : 27 August 2026 | 10:45 PM (GMT+3)
# Module      : Estate
# File        : estate_property_type.py
# Purpose     : Defines the Estate Property Type model and manages
#               property type information and their related 
#               real estate properties.
# ------------------------------------------------------------

from odoo import api, fields, models

class EstatePropertyType(models.Model):
    """
    Represents a type or category of real estate property.

    Each property type has a unique name and can be associated with
    multiple real estate properties. The model also provides a computed
    count of the properties assigned to each type.
    """
    _name = "estate.property.type"
    _description = "Real Estate Property Type"


    # --------------------------------------------------------
    # Property Type Information
    # --------------------------------------------------------

    # Name of the property type.
    # The field is required and must be unique across all property types.
    name = fields.Char(string="Property Type", required=True)

    # --------------------------------------------------------
    # Property Relationships
    # --------------------------------------------------------
   
    # One property type can be associated with multiple properties.
    # The inverse field "property_type_id" is defined on estate.property.
    property_ids = fields.One2many("estate.property", "property_type_id", string="Properties")

    # Number of properties currently assigned to this property type.
    # The value is calculated automatically from property_ids.
    property_count = fields.Integer(string="Properties Count", compute="_compute_property_count")

    # --------------------------------------------------------
    # Computed Fields
    # --------------------------------------------------------


    @api.depends("property_ids")
    def _compute_property_count(self):
        """
        Calculate the number of properties assigned to each property type.

        The count is automatically recomputed whenever the related
        property records are modified.
        """
        for record in self:
            # Count all properties linked to the current property type.
            record.property_count = len(record.property_ids)

    # --------------------------------------------------------
    # Database Constraints
    # --------------------------------------------------------

    # Prevent duplicate property type names from being created.
    _check_name_uniq = models.Constraint(
        "UNIQUE(name)",
        "A property type name must be unique!"
    )