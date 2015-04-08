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

import itertools
from lxml import etree

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning

import openerp.addons.decimal_precision as dp


class res_partner(models.Model):
    _name = 'res.partner'
    _inherit = ['res.partner']

    def _get_ids(self, cr, uid, ids, flds, args, context=None):
        return {i: i for i in ids}

    #_columns = {
        ## hack to allow using plain browse record in qweb views
        #'self': fields.function(_get_ids, type='many2one', relation=_name),
    #}

    def _display_address(self, cr, uid, address, without_company=False, context=None):

        '''
        The purpose of this function is to build and return an address formatted accordingly to the
        client.

        :param address: browse record of the res.partner to format
        :returns: the address formatted in a display that fit its country habits (or the default ones
            if not country is specified)
        :rtype: string
        '''

        # get the information that will be injected into the display format
        # get the address format
        address_format = "%(street)s\n%(street2)s\n %(zip)s %(city)s \n %(state_code)s %(country_name)s"
        args = {
            'state_code': address.state_id.code or '',
            'state_name': address.state_id.name or '',
            'country_code': address.country_id.code or '',
            'country_name': address.country_id.name or '',
            'company_name': address.parent_name or '',
        }
        for field in self._address_fields(cr, uid, context=context):
            args[field] = getattr(address, field) or ''
        if without_company:
            args['company_name'] = ''
        elif address.parent_id:
            address_format = '%(company_name)s\n' + address_format
        return address_format % args
        

    def _share(self, cr, uid, ids, name, args, context=None):
        res = {}
        for partner in self.browse(cr, uid, ids, context=context):
#            for invoice in self.pool.get('account.invoice').browse(cr, uid, self.pool.get('account.invoice').search(cr,uid,[company_id,'=',company.id],context=context), context=context):
#                res[company.id]['smart_cach'] =+ invoice.smart_cach,
            res[partner.id]['share_amount'] = 0
            res[partner.id]['share_blocks_amount'] = 0
        return res

    # share_blocks_amount = fields.function(_share, type="integer", string='Number of registered shares',help="Number of real shares in the system.",multi='all',)
    # share_amount = fields.function(_share, type="integer", string='Number of registered shares',help="Number of real shares in the system.",multi='all',)

#     def _get_ids(self, cr, uid, ids, flds, args, context=None):
#         return {i: i for i in ids}
#

    share_ids     = fields.One2many('share.share', 'owner_id', string='Shares', readonly=True)
    block_ids     = fields.One2many('share.block', 'owner_id', string='Blocks', readonly=True)
    partowner_ids   = fields.One2many('block.partowner', 'partowner_id', string='Part owner', )
    #beneficiary_ids = fields.One2many('share.share', 'owner_id', string='Shares', readonly=True)
    beneficiary_ids = fields.One2many('share.block', 'beneficiary',string='Beneficiary', )
    stakeholder_ids = fields.One2many('share.block', 'stakeholder',string='Stakeholders', )
    #stakeholder_ids = fields.One2many('share.share', 'owner_id', string='Shares', readonly=True)
    birth_date    = fields.Date(string='Birth Date')
    name_last     = fields.Char('Last name')
    
    
     # hack to allow using plain browse record in qweb views
#     self = fields.Many2one('self', compute='_get_ids', relation=_name)

#     DONOT delete the above partner_id field, otherwise reports will stop working

#    partowner_ids = fields.One2many('share.partworner', 'owner_id', string='Part owners',
#        readonly=True)

# birth_date
# commercial_partner_id
