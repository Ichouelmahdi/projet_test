# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import datetime

from odoo import api, fields, models, modules, _
from pytz import timezone, UTC


class Users(models.Model):
    _inherit = 'res.users'

    @api.model
    def systray_get_lead(self):
        query = """SELECT m.id, count(*), act.res_model as model,
                            CASE
                                WHEN %(today)s::date - act.date_deadline::date = 0 Then 'today'
                                WHEN %(today)s::date - act.date_deadline::date > 0 Then 'overdue'
                                WHEN %(today)s::date - act.date_deadline::date < 0 Then 'planned'
                            END AS states
                        FROM mail_activity AS act 
                        JOIN ir_model AS m ON act.res_model_id = m.id
                        WHERE user_id = %(user_id)s AND NOT EXISTS (SELECT * FROM res_users WHERE type = 'opportunity')
                        GROUP BY m.id, states, act.res_model;
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
                    'type': 'activity',
                    'icon': modules.module.get_module_icon(self.env[activity['model']]._original_module),
                    'total_count': 0, 'today_count': 0, 'overdue_count': 0, 'planned_count': 0,
                }
            user_activities[activity['model']]['%s_count' % activity['states']] += activity['count']
            if activity['states'] in ('today', 'overdue'):
                user_activities[activity['model']]['total_count'] += activity['count']

        return list(user_activities.values())



class MailActivity(models.Model):
    _inherit = 'mail.activity'
    _description = 'Activity'

    type = fields.Selection([('lead', 'Lead'), ('opportunity', 'Opportunity')], index=True, required=True,
        default=lambda self: 'lead' if self.env['res.users'].has_group('crm.group_use_lead') else 'opportunity',
        help="Type is used to separate Leads and Opportunities")