from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class OverdueLead(http.Controller):

    @http.route('/crm/leads/', website=True, auth='user')
    def lead_overdue(self, **kw):
        leads = request.env['crm.lead'].sudo().search([('type', '=', 'lead')])
        return request.render("test_p.overdue_leads_page", {
            'leads': leads
        })
