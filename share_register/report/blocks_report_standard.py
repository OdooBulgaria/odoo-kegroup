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

    
class blocks_report_standard(models.AbstractModel):
    _name = 'report.share_register.blocks_report_standard'

    @api.multi
    def render_html(self, data=None):
        _logger.info("Reporting Block")
        report = self.env['report']._get_report_from_name('share_register.blocks_report_standard')
        for company in self.env['res.company'].browse(self._ids):
            blocks = self.env['share.block'].search([('company_id','=',company.id)])

        return self.env['report'].render('share_register.blocks_report_standard', {
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


class res_company(models.Model):
    _inherit = "res.company"

    block_ids = fields.One2many(comodel_name='share.block',inverse_name="company_id")
    
    @api.one
    @api.depends('block_ids')
    def _get_partner(self):
#        self.shareholders_block = [b.partner_id for b in self.block_ids].sorted(key=lambda self: self.name)
        self.shareholders_block = [b.partner_id for b in self.block_ids]
    
    shareholders_block = fields.One2many('res.partner',compute="_get_partner")
     

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
