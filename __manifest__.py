# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'test_Darbtech',
    'version': '1.0',
    'sequence': 170,
    'category': 'Extra tools',
    'summary': '',
    'description': "",
    'author': 'El Mahdi ICHOU',
    'website': '',
    'depends': ['crm'],
    'data': [
        'views/crm_lead_icon_view.xml',
    ],
'qweb': [
        'static/src/xml/lead_icon.xml',

    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
