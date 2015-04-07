# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution, third party extension
#    Copyright (C) 2004-2015 Vertel AB (<http://vertel.se>).
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

import itertools
from lxml import etree

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning

import openerp.addons.decimal_precision as dp

import logging
_logger = logging.getLogger(__name__)

    
class blocks_report_extended(models.AbstractModel):
    _name = 'report.share_register.blocks_report_extended'

    @api.multi
    def render_html(self, data=None):
        _logger.info("Blocks report extened")
        report = self.env['report']._get_report_from_name('share_register.blocks_report_extended')
        for company in self.env['res.company'].browse(self._ids):
            blocks = self.env['share.block'].search([('company_id','=',company.id)])

        return self.env['report'].render('share_register.blocks_report_extended', {
                    'report': report,
                    'doc_ids': self._ids,
                    'doc_model': report.model,
                    'docs': self.env['res.company'].browse(self._ids),
                })
    
    @api.one
    def get_block(self, company, partner):
        if company and partner:
            return [x for x in partner.block_ids if x.company_id.id == company.id]
        return []


     

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
