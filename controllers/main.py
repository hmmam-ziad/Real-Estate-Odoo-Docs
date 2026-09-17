# estate/controllers/main.py
from odoo import http
from odoo.http import request
from odoo.exceptions import ValidationError, UserError

# States a property must be in to be visible / open for offers on the
# public website. Sold, canceled or offer-accepted properties are kept
# out of the public listing entirely.
OPEN_STATES = ["new", "offer_received"]


class EstateController(http.Controller):

    @http.route('/estate/properties', type='http', auth='public', website=True, sitemap=True)
    def list_properties(self, property_type=None, min_price=None, max_price=None,
                         bedrooms=None, search=None, **kw):
        """
        Display the public list of available properties, with basic
        search and filtering support (type, price range, bedrooms,
        free-text search on the title).
        """
        Property = request.env['estate.property'].sudo()
        PropertyType = request.env['estate.property.type'].sudo()

        domain = [('state', 'in', OPEN_STATES)]

        if search:
            domain.append(('name', 'ilike', search))
        if property_type:
            domain.append(('property_type_id', '=', int(property_type)))
        if bedrooms:
            domain.append(('bedrooms', '>=', int(bedrooms)))
        if min_price:
            domain.append(('expected_price', '>=', float(min_price)))
        if max_price:
            domain.append(('expected_price', '<=', float(max_price)))

        properties = Property.search(domain, order='id desc')
        property_types = PropertyType.search([])

        return request.render('estate.property_list_template', {
            'properties': properties,
            'property_types': property_types,
            'filters': {
                'property_type': property_type,
                'min_price': min_price,
                'max_price': max_price,
                'bedrooms': bedrooms,
                'search': search,
            },
        })

    @http.route('/estate/property/<model("estate.property"):property_obj>', type='http', auth='public', website=True)
    def property_detail(self, property_obj, **kw):
        """
        Show the public detail page for a single property.

        Access is always resolved with sudo() since anonymous website
        visitors have no direct read access to estate.property. The
        page still enforces its own visibility rule instead of relying
        on the base ACL: sold, canceled or otherwise non-public
        properties simply 404 rather than leaking their data.
        """
        record = property_obj.sudo()
        if not record.exists() or record.state not in OPEN_STATES:
            return request.not_found()

        return request.render('estate.property_detail_template', {
            'property': record,
            'can_offer': record.website_can_receive_offers(),
        })

    @http.route('/api/v1/properties', type='jsonrpc', auth='public', methods=['GET'], csrf=False)
    def api_get_properties(self, **kw):
        properties = request.env['estate.property'].sudo().search_read(
            domain=[('state', 'in', OPEN_STATES)],
            fields=['id', 'name', 'expected_price', 'bedrooms', 'living_area', 'state']
        )
        return {
            'status': 'success',
            'count': len(properties),
            'data': properties,
        }

    @http.route('/api/v1/property/offer', type='jsonrpc', auth='public', methods=['POST'], csrf=False)
    def api_create_offer(self, property_id, price, partner_name=None, partner_email=None, **kw):
        """
        Create an offer from the public website.

        Runs entirely with sudo() since anonymous/portal visitors have
        no direct model access, but every value coming from the client
        is validated server-side before anything is written:
        - the property must exist and still be open for offers
        - the price must be a positive number
        - a partner is resolved (the logged-in user, or a contact
          found/created from the submitted name + email for anonymous
          visitors)
        """
        Property = request.env['estate.property'].sudo()
        prop = Property.browse(int(property_id))
        if not prop.exists():
            return {'status': 'error', 'message': 'Property not found.'}
        if prop.state not in OPEN_STATES:
            return {'status': 'error', 'message': 'This property is no longer open for offers.'}

        try:
            price = float(price)
        except (TypeError, ValueError):
            return {'status': 'error', 'message': 'Please enter a valid price.'}
        if price <= 0:
            return {'status': 'error', 'message': 'The offer price must be greater than zero.'}

        # Resolve the partner submitting the offer.
        if not request.env.user._is_public():
            partner = request.env.user.partner_id
        else:
            if not partner_name or not partner_email:
                return {'status': 'error', 'message': 'Please provide your name and email.'}
            partner = request.env['res.partner'].sudo().find_or_create(
                f"{partner_name} <{partner_email}>"
            )

        try:
            offer = request.env['estate.property.offer'].sudo().create({
                'property_id': prop.id,
                'price': price,
                'partner_id': partner.id,
            })
        except (ValidationError, UserError) as exc:
            return {'status': 'error', 'message': exc.args[0] if exc.args else str(exc)}

        return {
            'status': 'success',
            'offer_id': offer.id,
            'message': 'Your offer was submitted successfully!',
        }