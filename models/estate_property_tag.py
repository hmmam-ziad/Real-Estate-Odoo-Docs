# ------------------------------------------------------------
# Author      : HmMam Alsukhni
# Created     : 27 August 2026 | 10:45 PM (GMT+3)
# Module      : Estate
# File        : estate_property_tag.py
# Purpose     : Defines the Estate Property Tag model and manages
#               property tag information.
# ------------------------------------------------------------

from odoo import fields, models


class EstatePropertyTag(models.Model):
    """
    Represents a tag used to categorize and organize real estate properties.

    Each tag has a unique name and can optionally be assigned a color
    for easier identification in the user interface.
    """

    _name = "estate.property.tag"
    _description = "Real Estate Property Tag"

    # --------------------------------------------------------
    # Tag Information
    # --------------------------------------------------------

    # Name of the property tag.
    # The field is required and must be unique across all tags.
    name = fields.Char(string="Name", required=True)

    # Numeric color index used by Odoo to display the tag with
    # a specific color in the user interface.
    color = fields.Integer(string="Color")

    # --------------------------------------------------------
    # Database Constraints
    # --------------------------------------------------------

    # Ensure that no two property tags can have the same name.
    # This prevents duplicate tags from being created.
    _check_name_uniq = models.Constraint(
        "UNIQUE(name)",
        "A property tag name must be unique!"
    )