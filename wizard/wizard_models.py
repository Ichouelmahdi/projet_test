# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _


class CreateLead(models.TransientModel):
    _name = "create.crm.lead"
    _description = "Create lead"

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
                              domain=[('type', '=', 'lead')], required=True, ondelete='cascade')
    user_id = fields.Many2one('res.users', string='Salesperson', default=lambda self: self.env.user)

    @api.multi
    def action_copy_lead(self):
        wizards = self.browse(self._ids)
        for wizard in wizards:
            lead_id = wizard.lead_id.copy()
            lead_id.name = wizard.name
            lead_id.user_id = wizard.user_id
            lead_id.partner_id = wizard.partner_id
            lead_id.type = 'lead'
            lead_id.tag_ids = wizard.tag_ids

        return {
           'name': _('New lead'),
           'view_type': 'form',
           'view_mode': 'form,tree',
           'res_model': 'create.crm.lead',
           'view_id': False,
           'res_id': lead_id.id,
           'type': 'ir.actions.act_window'}


class DefineAction(models.TransientModel):
    _name = "define.action"

    activity_ids = fields.Many2one('mail.activity', string='Activity')
    activity_type_id = fields.Many2one('mail.activity.type', 'Activity')
    summary = fields.Char('Summary')
    note = fields.Html('Note', sanitize_style=True)
    date_deadline = fields.Date('Due Date', index=True, required=True, default=fields.Date.context_today)
    user_id = fields.Many2one('res.users', 'Assigned to', default=lambda self: self.env.user, index=True, required=True)
    type = fields.Selection([('lead', 'Lead'), ('opportunity', 'Opportunity')], index=True,
                            required=True,
                            default=lambda self: 'lead' if self.env['res.users'].has_group('crm.group_use_lead')
                            else 'opportunity',  help="Type is used to separate Leads and Opportunities")

    @api.multi
    def action_copy_activity(self):
        wizards = self.browse(self._ids)
        for wizard in wizards:
            if wizard.activity_ids:
                activity_ids = wizard.activity_ids.copy()
                activity_ids.activity_type_id = wizard.activity_type_id
                activity_ids.summary = wizard.summary
                activity_ids.type = wizard.type
                activity_ids.date_deadline = wizard.date_deadline
                activity_ids.user_id = wizard.user_id
                activity_ids.note = wizard.note
