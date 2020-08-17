# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, modules, _


class Users(models.Model):
    _inherit = 'res.users'

    @api.model
    def systray_get_lead(self):
        query = """SELECT count(*), act.res_model as model, act.res_id, c.id,
                            CASE
                                WHEN %(today)s::date - act.date_deadline::date = 0 Then 'today'
                                WHEN %(today)s::date - act.date_deadline::date > 0 Then 'overdue'
                                WHEN %(today)s::date - act.date_deadline::date < 0 Then 'planned'
                            END AS states
                        FROM mail_activity AS act
                        JOIN crm_lead AS c ON act.res_id = c.id
                        WHERE c.type = 'lead' 
                        GROUP BY act.res_id, states,c.id, act.res_model;
                        """

        self.env.cr.execute(query, {
            'today': fields.Date.context_today(self),
            'user_id': self.env.uid,
        })
        activity_data = self.env.cr.dictfetchall()
        user_activities = {}
        for activity in activity_data:
            if not user_activities.get(activity['model']):
                user_activities[activity['model']] = {
                    'name': 'CRM Qualifications',
                    'model': activity['model'],
                    'domain': [('type', '=', 'lead')],
                    'type': 'activity',
                    'icon': modules.module.get_module_icon(self.env[activity['model']]._original_module),
                    'total_count': 0, 'today_count': 0, 'overdue_count': 0, 'planned_count': 0,
                }
            user_activities[activity['model']]['%s_count' % activity['states']] += activity['count']
            if activity['states'] in ('today', 'overdue'):
                user_activities[activity['model']]['total_count'] += activity['count']

        return list(user_activities.values())


class Partner(models.Model):
    _inherit = "res.partner"

    lead_ids = fields.One2many('crm.lead', 'partner_id', string="Leads in progress", domain=[('type', '=', 'lead')],
                               auto_join=True, readonly=True)


class Lead(models.Model):
    _inherit = "crm.lead"

    partner_id = fields.Many2one('res.partner')
    date_next_action = fields.Date('Date next action', compute="_compute_date_next_action")
    act_ids = fields.One2many('mail.activity', 'res_id', string='Activities',
                              auto_join=True, readonly=True, domain=lambda self: [('res_model', '=', self._name)])

    @api.depends()
    def _compute_date_next_action(self):
        leads = self.search([('type', '=', 'lead'), ('user_id', '=', self._uid)])
        today = fields.Date.from_string(fields.Date.context_today(self))
        for lead in leads:
            list_date_action = []
            for activity in lead.activity_ids:
                if activity.date_deadline < today:
                    list_date_action.append(activity.date_deadline)
            if list_date_action:
                lead.date_next_action = min(list_date_action)
