# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2014 Vertel AB (<http://vertel.se>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from datetime import time, date

from openerp.osv import osv
from openerp.report import report_sxw
from openerp import api, models


class block_data(report_sxw.rml_parse,):
    _name = 'report.share_register.report_block'

    def __init__(self, cr, uid, name, context=None):
        super(block_data, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'date': date,
            'get_block': self._get_block,
            'get_beneficiary': self._get_beneficiary,
            'get_stakeholder': self._get_stakeholder,
            'get_partowner': self._get_partowner,
        })
        self.context = context

    def _get_block(self):
        if self.context.get('active_ids') and len(self.context['active_ids']) > 0:
            block_pool = self.pool.get('share.block')
            block_ids = block_pool.search(self.cr, self.uid, [('company_id', '=', self.context['active_ids'][0])],order="name asc")
            if block_ids:
                return block_pool.browse(self.cr, self.uid, block_ids)
        return ""

    def set_context(self, objects, data, ids, report_type=None):
        new_ids = ids
        return super(block_data, self).set_context(objects, data, new_ids, report_type=report_type)

    def _get_beneficiary(self):
        setting_pool = self.pool.get('company.share.setting')
        setting_ids = setting_pool.search(self.cr, self.uid, [])
        if setting_ids and len(setting_ids) > 0:
            return setting_pool.browse(self.cr, self.uid, setting_ids[0]).view_beneficiary
        else:
            return False

    def _get_stakeholder(self):
        setting_pool = self.pool.get('company.share.setting')
        setting_ids = setting_pool.search(self.cr, self.uid, [])
        if setting_ids and len(setting_ids) > 0:
            return setting_pool.browse(self.cr, self.uid, setting_ids[0]).view_stakeholder
        else:
            return False

    def _get_partowner(self):
        setting_pool = self.pool.get('company.share.setting')
        setting_ids = setting_pool.search(self.cr, self.uid, [])
        if setting_ids and len(setting_ids) > 0:
            return setting_pool.browse(self.cr, self.uid, setting_ids[0]).view_partowner
        else:
            return False

class ParticularReport(models.AbstractModel):
    _name = 'report.share_register.report_block'
    _inherit = 'report.abstract_report'
    _template = 'share_register.report_block'
    _wrapped_report_class = block_data


class partnerblock_data(report_sxw.rml_parse,):
    _name = 'report.share_register.report_partnerblock'

    def __init__(self, cr, uid, name, context=None):
        super(partnerblock_data, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'date': date,
            'get_block': self._get_block,
            'get_company': self._get_company,
            'block_available': self._block_available,
            'get_partner':self._get_partner,
        })
        self.context = context

    def _get_company(self, partner_brw):
        block_brw = partner_brw.block_ids
        if block_brw:
            company_brw = [x.company_id for x in block_brw]
            company_brw = list(set(company_brw))  # To remove duplicate company_ids from the list
            return company_brw
        return []

    def _get_block(self, company_brw, partner_brw):

        if company_brw and partner_brw:
            block_brw = [x for x in partner_brw.block_ids if x.company_id.id == company_brw.id]
            return block_brw
        return []

    def _block_available(self, partner_brw):
        block_brw = partner_brw.block_ids
        if block_brw:
            return True
        return False

    def _get_partner(self, partner_brw):
        return partner_brw


class PartnerParticularReport(models.AbstractModel):
    _name = 'report.share_register.report_partnerblock'
    _inherit = 'report.abstract_report'
    _template = 'share_register.report_partnerblock'

#     @api.multi
#     def render_html(self, data=None):
#         report_obj = self.env['report']
#         report = report_obj._get_report_from_name('share_register.report_partnerblock')
#         docargs = {
#             'doc_ids': self._ids,
#             'doc_model': report.model,
#             'docs': self,
#         }
#         return report_obj.render('share_register.report_partnerblock', docargs)

    _wrapped_report_class = partnerblock_data
