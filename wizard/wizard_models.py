# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.tools.misc import clean_context

AVAILABLE_PRIORITIES = [
    ('0', 'Low'),
    ('1', 'Medium'),
    ('2', 'High'),
    ('3', 'Very High'),
]


class CreateLead(models.TransientModel):
    _name = "create.crm.lead"
    _description = "Create lead"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.model
    def default_get(self, fields):
        result = super(CreateLead, self).default_get(fields)
        lead_id = self.env.context.get('active_id')
        if lead_id:
            result['lead_id'] = lead_id
        return result
    name = fields.Char('Opportunity', required=True, index=True)
    partner_id = fields.Many2one('res.partner', string='Customer', index=True)
    tag_ids = fields.Many2many('crm.lead.tag', string='Tags',
                               help="Classify and analyze your lead/opportunity categories like: Training, Service")
    lead_id = fields.Many2one('crm.lead', string='Lead',
                              required=True, ondelete='cascade', default=lambda self: self.default_get)
    user_id = fields.Many2one('res.users', string='Salesperson', default=lambda self: self.env.user)
    priority = fields.Selection(AVAILABLE_PRIORITIES, string='Priority',
                                index=True, default=AVAILABLE_PRIORITIES[0][0])

    @api.multi
    def button_create_lead(self):
        wizards = self.browse(self._ids)
        for wizard in wizards:
            lead_id = wizard.lead_id.copy()
            ctx = dict(
                clean_context(self.env.context),
                default_res_id=lead_id.id,
                default_res_model='crm.lead',
            )
            lead_id.name = wizard.name
            lead_id.user_id = wizard.user_id
            lead_id.partner_id = wizard.partner_id
            lead_id.type = 'lead'
            lead_id.tag_ids = wizard.tag_ids
            lead_id.priority = wizard.priority

        return {
            'name': _('Schedule an Activity'),
            'view_type': 'form',
            'context': ctx,
            'view_mode': 'form',
            'res_model': 'mail.activity',
            'views': [(False, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'new'}
