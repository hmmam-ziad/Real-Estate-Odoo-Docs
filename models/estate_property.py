# ------------------------------------------------------------
# Author      : HmMam Alsukhni
# Created     : 27 August 2026 | 10:45 PM (GMT+3)
# Module      : Estate
# File        : estate_property.py
# Purpose     : Defines the Estate Property model and manages
#               property information, features, status,
#               property types, tags, and offers.
# ------------------------------------------------------------

from odoo import Command, api, fields, models
from odoo.exceptions import UserError,ValidationError
from odoo.tools import float_is_zero, float_compare

class EstateProperty(models.Model):
    """
    Represents a real estate property managed by the estate module.

    The model stores general property information, pricing details,
    property features, related offers, property type, tags, buyer
    information, and the property's current status.
    """

    _name = "estate.property"
    _description = "Real Estate Property"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # --------------------------------------------------------
    # Basic Property Information
    # --------------------------------------------------------

    # Title or name of the property.
    name = fields.Char(string="Title", required=True, tracking=True)

    # Detailed description of the property.
    description = fields.Text(string="Description")

    # Postal code associated with the property's location.
    postcode = fields.Char(string="Postcode")

    # Date from which the property becomes available.
    date_availability = fields.Date(string="Available From")

    # Price initially expected by the seller.
    # This value must be greater than zero.
    expected_price = fields.Float(string="Expected Price", required=True, tracking=True)

    # Final selling price of the property.
    selling_price = fields.Float(string="Selling Price", tracking=True)

    # Number of bedrooms available in the property.
    bedrooms = fields.Integer(string="Bedrooms")

    # Total living area measured in square meters.
    living_area = fields.Integer(string="Living Area (sqm)")

    # Number of exterior facades of the property.
    facades = fields.Integer(string="Facades")

    # Indicates whether the property has a garage.
    garage = fields.Boolean(string="Garage")

    # Indicates whether the property has a garden.
    garden = fields.Boolean(string="Garden")

    # Size of the garden measured in square meters.
    garden_area = fields.Integer(string="Garden Area (sqm)")

    # --------------------------------------------------------
    # Computed Fields
    # --------------------------------------------------------

    # Total property area calculated from the living area
    # and garden area.
    total_area = fields.Integer(string="Total Area (sqm)", compute="_compute_total_area")

    # Highest offer currently submitted for the property.
    best_price = fields.Float(string="Best Offer Price", compute="_compute_best_price")

    # Number of offers submitted for the property.
    offer_count = fields.Integer(string="Offers Count", compute="_compute_offer_count")

    # --------------------------------------------------------
    # Relationships
    # --------------------------------------------------------

    # Property type associated with the property.
    property_type_id = fields.Many2one("estate.property.type", string="Property Type")

    # Property type associated with the property.
    tag_ids = fields.Many2many("estate.property.tag", string="Tags")

    # Offers submitted by potential buyers for this property.
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")

    # Partner who becomes the buyer after an offer is accepted.
    buyer_id = fields.Many2one("res.partner", string="Buyer")

    # --------------------------------------------------------
    # Property Status
    # --------------------------------------------------------

    # Current lifecycle status of the property.
    state = fields.Selection(
        selection=[
            ('new', 'New'),
            ('offer_received', 'Offer Received'),
            ('offer_accepted', 'Offer Accepted'),
            ('sold', 'Sold'),
            ('canceled', 'Canceled'),
        ],
        string="Status",
        required=True,
        copy=False,
        default='new',
        tracking=True
    )

    # --------------------------------------------------------
    # Garden Information
    # --------------------------------------------------------

    # Direction in which the property's garden is oriented.
    garden_orientation = fields.Selection(
        selection=[
            ('north', 'North'),
            ('south', 'South'),
            ('east', 'East'),
            ('west', 'West'),
        ],
        string="Garden Orientation",
    )

    # --------------------------------------------------------
    # Computed Methods
    # --------------------------------------------------------
    
    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        """
        Calculate the total area of each property.

        The total area is calculated by adding the living area 
        and garden area together.
        """
        for record in self:
            record.total_area = (record.living_area or 0) + (record.garden_area or 0)

    @api.depends('offer_ids.price')
    def _compute_best_price(self):
        """
        Calculate the highest offer price for each property. 
        
        If the property has no offers, the best price is set to zero.
        """
        for record in self:
            if record.offer_ids:
                record.best_price = max(record.offer_ids.mapped('price'))
            else:
                record.best_price = 0.0

    @api.depends("offer_ids")
    def _compute_offer_count(self):
        """
        Calculate the total number of offers submitted for each property.
        """
        for record in self:
            record.offer_count = len(record.offer_ids)

            
    # --------------------------------------------------------
    # Onchange Methods
    # --------------------------------------------------------
    @api.onchange("garden")
    def _onchange_garden(self):
        """
        Update garden-related fields when the garden option changes.

        When a garden is enabled, a default garden area and orientation
        are assigned. When the garden is disabled, the related fields
        are cleared.
        """
        if self.garden:
            # Set default values when the property has a garden.
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            # Clear garden information when no garden is available.
            self.garden_orientation = False
            self.garden_area = 0

    # --------------------------------------------------------
    # Property Actions
    # --------------------------------------------------------

    def action_post_cancel(self):
        """
        Cancel the selected property.

        A property that has already been sold cannot be canceled.
        """
        for record in self:
            # Prevent a sold property from being canceled.
            if record.state == 'sold':
                raise UserError("Sold properties cannot be canceled.")
            # Change the property status to canceled.
            record.state = 'canceled'
        return True

    def action_post_sold(self):
        """
        Mark the property as sold and create a customer invoice.

        The invoice contains the estate commission and administrative
        fees. Canceled properties cannot be marked as sold.
        """
        for record in self:
            # Prevent canceled properties from being sold.
            if record.state == 'canceled':
                raise UserError("Canceled properties cannot be marked as sold.")
            
            # Find an available sales journal for the customer invoice.
            journal = self.env["account.journal"].search([("type", "=", "sale")], limit=1)

            # Prepare the invoice values for the sold property.
            invoice_vals = {
                "partner_id": record.buyer_id.id,
                "move_type": "out_invoice",
                "journal_id": journal.id if journal else False,
                "line_ids": [
                    # Estate commission calculated at 6% of the selling price.
                    Command.create({
                        "name": f"Commission (6%) - {record.name}",
                        "quantity": 1,
                        "price_unit": record.selling_price * 0.06,
                    }),
                    # Fixed administrative fee charged on the transaction.
                    Command.create({
                        "name": "Administrative Fees",
                        "quantity": 1,
                        "price_unit": 100.00,
                    }),
                ],
            }
            # Create the customer invoice.
            self.env["account.move"].create(invoice_vals)

            # Update the property status after the invoice is created.
            record.state = 'sold'
        return True

    def action_view_offers(self):
        """
        Open the offers related to the current property.

        The action displays only offers belonging to the selected
        property and provides the property as the default value
        when creating a new offer.
        """

        self.ensure_one()
        return {
            'name': 'Offers',
            'type': 'ir.actions.act_window',
            'res_model': 'estate.property.offer',
            'view_mode': 'tree,form',
            'domain': [('property_id', '=', self.id)],
            'context': {'default_property_id': self.id},
        }

    # --------------------------------------------------------
    # Database Constraints
    # --------------------------------------------------------
    
    # Ensure that the expected price is always greater than zero.
    _check_expected_price = models.Constraint(
        "CHECK(expected_price > 0)",
        "The expected price must be greater than zero."
    )

    # Prevent negative selling prices at the database level.
    _check_selling_price_positive = models.Constraint(
        "CHECK(selling_price >= 0)",
        "The selling price must be positive!"
    )

    # --------------------------------------------------------
    # Business Validation
    # --------------------------------------------------------

    @api.constrains("selling_price", "expected_price")
    def _check_selling_price(self):
        """
        Validate the selling price against the expected price.

        Unless the selling price is zero, it cannot be lower than
        90% of the expected price.
        """
        for record in self:
            if not float_is_zero(record.selling_price, precision_digits=2):
                min_price = record.expected_price * 0.9
                if float_compare(record.selling_price, min_price, precision_digits=2) < 0:
                    raise ValidationError(
                        "The selling price cannot be lower than 90% of the expected price! "
                        "You must reduce the expected price if you want to accept this offer."
                    )
