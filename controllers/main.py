# estate/controllers/main.py
from odoo import http
from odoo.http import request

class EstateController(http.Controller):
    @http.route('/estate/properties', type='http', auth='public', website=True)
    def list_properties(self, **kw):
        properties = request.env['estate.property'].sudo().search([
            ('state', 'in', ['new', 'offer_received'])
        ])
        return request.render('estate.property_list_template', {
            'properties': properties,
        })

    @http.route('/estate/property/<model("estate.property"):property_obj>', type='http', auth='public', website=True)
    def property_detail(self, property_obj, **kw):
        return request.render('estate.property_detail_template', {
            'property': property_obj,
        })

    @http.route('/api/v1/properties', type='json', auth='public', methods=['GET'], csrf=False)
    def api_get_properties(self, **kw):
        properties = request.env['estate.property'].sudo().search_read(
            domain=[('state', 'in', ['new', 'offer_received'])],
            fields=['id', 'name', 'expected_price', 'bedrooms', 'living_area', 'state']
        )
        return {
            'status': 'success',
            'count': len(properties),
            'data': properties,
        }

    @http.route('/api/v1/property/offer', type='json', auth='user', methods=['POST'], csrf=False)
    def api_create_offer(self, property_id, price, **kw):
        prop = request.env['estate.property'].browse(property_id)
        if not prop.exists():
            return {'status': 'error', 'message': 'Property not found'}

        offer = request.env['estate.property.offer'].create({
            'property_id': property_id,
            'price': price,
            'partner_id': request.env.user.partner_id.id,
        })

        return {
            'status': 'success',
            'offer_id': offer.id,
            'message': 'Offer created successfully',
        }