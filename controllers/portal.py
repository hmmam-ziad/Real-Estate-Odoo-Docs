# estate/controllers/portal.py
from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager

class EstateCustomerPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'property_offer_count' in counters:
            partner = request.env.user.partner_id
            offer_count = request.env['estate.property.offer'].sudo().search_count([
                ('partner_id', '=', partner.id)
            ])
            values['property_offer_count'] = offer_count
        return values

    @http.route(['/my/offers', '/my/offers/page/<int:page>'], type='http', auth='user', website=True)
    def portal_my_offers(self, page=1, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        OfferEnv = request.env['estate.property.offer'].sudo()

        domain = [('partner_id', '=', partner.id)]

        offer_count = OfferEnv.search_count(domain)
        pager = portal_pager(
            url="/my/offers",
            total=offer_count,
            page=page,
            step=10 
        )

        offers = OfferEnv.search(domain, limit=10, offset=pager['offset'])

        values.update({
            'offers': offers,
            'page_name': 'property_offer',
            'pager': pager,
            'default_url': '/my/offers',
        })
        return request.render("estate.portal_my_offers_template", values)

    @http.route(['/my/offer/<int:offer_id>'], type='http', auth='user', website=True)
    def portal_my_offer_detail(self, offer_id=None, **kw):
        offer = request.env['estate.property.offer'].sudo().browse(offer_id)

        if not offer.exists() or offer.partner_id.id != request.env.user.partner_id.id:
            return request.redirect('/my')

        values = {
            'offer': offer,
            'page_name': 'property_offer_detail',
        }
        return request.render("estate.portal_offer_detail_template", values)