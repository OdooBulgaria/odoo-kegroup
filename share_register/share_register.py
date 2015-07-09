
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

import logging
_logger = logging.getLogger(__name__)


class share_share(models.Model):
    _name = "share.share"
    _inherit = ['mail.thread']
    _description = "Share Certificate"
    _order = "name desc, id desc"

    @api.model
    def _default_currency(self):
        company = self.company_id
        return company.currency_id or False

    @api.model
    def _default_block(self):
        blocks = self.env['share.block'].search([])
        if blocks and len(blocks) > 0:
            return blocks[-1]
        else:
            return False

    @api.model
    def _default_nominal_value(self, company_id=False):
        if not company_id:
            company_id = self._default_company()
        company = self.env['res.company'].browse(company_id)
        return company.nominal_value

    @api.model
    def _default_company(self):
        return self.env['res.company']._company_default_get('share.share')

    name = fields.Char(string='Share No.', index=True, readonly=True, states={'draft': [('readonly', False)]})
    comment = fields.Text('Additional Information')
    state = fields.Selection([
            ('draft', 'Draft'),
            ('open', 'Open'),
            ('cancel', 'Cancelled'),
        ], string='Status', index=True, readonly=True, default='draft',
        track_visibility='onchange', copy=False,
        help=" * The 'Draft' status is used when a user is encoding a new and unconfirmed Invoice.\n"
             " * The 'Open' status is used when user create invoice,a invoice number is generated.Its in open status till user does not pay invoice.\n"
             " * The 'Cancelled' status is used when user cancel invoice.")
    date_issued = fields.Date(string='Date Issued',
        readonly=True, states={'draft': [('readonly', False)], }, index=True,
        help="Keep empty to use the current date", default=fields.Date.today, copy=False)

    owner_id = fields.Many2one('res.partner', string='Owner', change_default=True,
        required=True, readonly=True, states={'draft': [('readonly', False)]},
        track_visibility='always')

    seller_id = fields.Many2one('res.partner', string='Seller', change_default=True,
        required=False, readonly=True, states={'draft': [('readonly', False)]},
        track_visibility='always')

    currency_id = fields.Many2one('res.currency', string='Currency',
        required=True, readonly=True, states={'draft': [('readonly', False)]},
        default=_default_currency, track_visibility='always')

    nominal_value = fields.Float('Nominal value', digits_compute=dp.get_precision('Account'))

    purchase_price = fields.Float('Purchase price', digits_compute=dp.get_precision('Account'))

    company_id = fields.Many2one('res.company', string='Company', change_default=True,
        required=True, readonly=True, states={'draft': [('readonly', False)]},
        default=lambda self: self.env['res.company']._company_default_get('share.share'))

    share_beneficiary = fields.Many2one('res.partner', string='Beneficiary', change_default=True,
             help=" * The benficiary is the real person behind an owner.")

    share_stakeholder = fields.Many2many('res.partner', string='Stakeholder', change_default=True,
                help=" * People who shoule be informed about events around this share. ")

#    share_partowner = fields.Many2one('res.partner', string='PartOwner', change_default=True,
#             help=" * The Partowner behind the real person owner.")
#
    partowner_ids = fields.One2many('share.partowner', 'share_id', string='Partowners')

#    partowner_ids = fields.One2many('share.partowner', 'share_id', string='Partowners', change_default=True,  # Sl� upp One2many  Assetion Error
#        required=False, readonly=True, states={'draft': [('readonly', False)]},
#        track_visibility='always')
#    partowners_ids = fields.One2many('share.partowner', 'share_partowner', string='Shares',readonly=True, states={'draft': [('readonly', False)]}, copy=True)


    share_class = fields.Selection([('ordinary', 'Ordinary'), ('redemtion', 'Redemption'), ('a', 'A'), ('b', 'B'), ('c', 'C')], string='Share Class',
                                 help=" * Share classes defines the nominal value")

    share_emption = fields.Boolean('Emption',
                      help=""" * Emption is a limitation when a share is sold. \n
                             * It needs to be offered to previous owners before a new owner can be accepted.""")


    block_id = fields.Many2one('share.block', string='Certificate', change_default=True,
        required=False, readonly=True, states={'draft': [('readonly', False)]}, default=lambda self: self._default_block(),)



#    _sql_constraints = [
#        ('number_uniq', 'unique(name, company_id, )',
#            'Invoice Number must be unique per Company!'),
#    ]



    @api.multi
    def _log_event(self, factor=1.0, name='Open share certificate'):
        # TODO: implement messages system
        return True

class block_partowner(models.Model):
    _name = "block.partowner"
    _inherit = ['mail.thread']
    _description = "Partowners of shares"
    _order = "name desc, id desc"

    block_id = fields.Many2one('share.block', string='Certificate', change_default=True, required=True, readonly=False, track_visibility='always')
    name = fields.Char(string='Part Owner No.', index=True,readonly=False,)
    partowner_id = fields.Many2one('res.partner', string='Part Owner', change_default=True, required=True, readonly=False,track_visibility='always')
    partowner_percent = fields.Float('Owner percent', digits_compute=dp.get_precision('Account'))
    purchase_price = fields.Float('Purchase price', digits_compute=dp.get_precision('Account'))    
    purchase_date = fields.Date('Purchase Date',)
    block_state = fields.Selection(string='State', related='block_id.state')

class share_block(models.Model):
    _name = "share.block"
    _inherit = ['mail.thread']
    _description = "Certificate of shares"
    _order = "name desc, id desc"

    def _block(self, cr, uid, ids, name, args, context=None):
        res = {}
        for block in self.browse(cr, uid, ids, context=context):
            if block.share_ids[0].partowner_ids:
                res[block.id]['block_part_owner_ids'] = [po.id for po in block.share_ids[0].partowner_ids]
        return res

    @api.model
    def _default_company(self):
        return self.env['res.company']._company_default_get('share.block')

    @api.model
    def _nominal_value(self):
        return 0.0

    name = fields.Char(string='Cert No.', index=True, readonly=True, states={'draft': [('readonly', False)]})
    comment = fields.Text('Additional Information', track_visibility='onchange')
    state = fields.Selection([
            ('draft', 'Draft'),
            ('open', 'Open'),
            ('cancel', 'Cancelled'),
        ], string='Status', index=True, readonly=False, default='draft',
        track_visibility='onchange', copy=False,
        help=" * The 'Draft' status is used when a user is encoding a new and unconfirmed Invoice.\n"
             " * The 'Open' status is used when user create invoice,a invoice number is generated.Its in open status till user does not pay invoice.\n"
             " * The 'Cancelled' status is used when user cancel invoice.")
    date_issued = fields.Date(string='Date Issued',
        readonly=True, states={'draft': [('readonly', False)]}, index=True,
        help="Keep empty to use the current date", copy=False)
    owner_id = fields.Many2one('res.partner', string='Owner', change_default=True,
        required=True, readonly=True, states={'draft': [('readonly', False)]}, track_visibility='onchange')

    beneficiary = fields.Many2one('res.partner', string='Beneficiary', change_default=True, track_visibility='onchange')

    stakeholder = fields.Many2many('res.partner', string='Stakeholder', change_default=True, track_visibility='onchange')

    partowner_ids = fields.One2many('block.partowner', 'block_id', string='Part Owners',)
    partowner_names = fields.Char('Partowners',compute='_partowner_names',store=True,  track_visibility='always')
    #  change convert_for_display in mail_thread.py to get a better display of a One2many-change-log
    meeting_ids =  fields.Many2many('calendar.event', relation="rel_blocks_calendar",string='Board meeting')


    @api.depends('partowner_ids')
    def _partowner_names(self):
        _logger.warning("My partowner_ids %s" % self.partowner_ids)
        self.partowner_names = ','.join([p.partowner_id.name for p in self.partowner_ids]) if self.partowner_ids else ""
            

    nominal_value = fields.Float('Nominal value', digits_compute=dp.get_precision('Account'), track_visibility='onchange')

    purchase_price = fields.Float('Purchase price', digits_compute=dp.get_precision('Account'), track_visibility='onchange')



    block_share_numbers = fields.Char(string='Share No. Interval', track_visibility='onchange')
    share_ids = fields.One2many('share.share', 'block_id', string='Shares', readonly=True, track_visibility='onchange')
    certificate_issued = fields.Boolean('Certificate Issed', help=""" * Checked if there has been a physical Share Certificate Issued for the Shares in the interval.""")

#
# Anders: De h�r f�lten finns ocks� i shares.shares och ska vara samma p� alla i aktieposten. Senare vill jag endast lagra info p� ett st�lle (aktien) och sedan lyfta upp det till blocket, eftersom en aktie kan splittas och d� kanske den �ndrar aktieklass.
#
    share_class = fields.Selection([('ordinary', 'Ordinary'), ('redemtion', 'Redemption'), ('a', 'A'), ('b', 'B'), ('c', 'C')], string='Share Class',)
    emption = fields.Boolean('Emption', track_visibility='onchange')


    # block_part_owner_ids = fields.Function(_block, type="One2many", 'share.partowner',string='Part Owners',help="from first share in block.",multi='all',)  # V�nta p� dokumentation

#    block_part_owner_ids = fields.fields(_block,'res.partner', string='Part Owner', change_default=True,
#        required=True, readonly=True, states={'draft': [('readonly', False)]},
#        track_visibility='always')

# Slut nya f�lbootstrap snippet radiobuttont

    company_id = fields.Many2one('res.company', string='Company', change_default=True, required=True, readonly=True, states={'draft': [('readonly', False)]}, default=lambda self: self.env['res.company']._company_default_get('share.share'), track_visibility='onchange')
    number_of_shares = fields.Integer('No. of Shares', track_visibility='onchange')
    date_purchased = fields.Date(string='Purchased Date', readonly=True, states={'draft': [('readonly', False)]},)
#    share_ids = fields.One2many('share.share', 'block_id', string='Shares',readonly=True, states={'draft': [('readonly', False)]}, copy=True)

#    share_capital = fields.Reference(['company_id','share_capital'])
#    share_total = fields.Reference(['company_id','share_total'])
#    nominal_value = fields.Function(lambda self: self.share_capital / self.share_total, type="decimal", string='Nominal value',)
#    nominal_value = fields.Function(_nominal_value, type="decimal", string='Nominal value',)

#    share_ids = fields.One2many('share.share', 'share_block','Shares', change_default=True,required=False, readonly=True, states={'draft': [('readonly', False)]},)


#    cancelled_date  = fields
    transferred_date = fields.Date(string='Transferred Date')
    numbers_sold = fields.Integer('Numbers Sold')
    cancelled_date = fields.Date(string='Cancelled Date')

    new_shares = fields.Integer('New Shares')

    @api.one
    def _new_balance(self):
        self.new_balance = self.number_of_shares + self.new_shares - self.numbers_sold
    new_balance = fields.Integer('New Balance',compute="_new_balance")

    part_owner_purchase_date = fields.Date(string='Partowner Date')
    lastname = fields.Char()
    policy_number = fields.Char()
    new_cert_number = fields.Char('New certificate number')
    
    
    
    
class share_partowner(models.Model):
    _name = "share.partowner"
    _inherit = ['mail.thread']
    _description = "Partowners of shares"
    _order = "name desc, id desc"


    share_id = fields.Many2one('share.share', string='Share', change_default=True,
        required=True, readonly=False,
        track_visibility='always')

    name = fields.Char(string='Part Owner No.', index=True,
        readonly=False,)

    partowner_id = fields.Many2one('res.partner', string='Part Owner', change_default=True,
        required=True, readonly=False,
        track_visibility='always')

    partowner_percent = fields.Float('Owner percent', digits_compute=dp.get_precision('Account'))







class company_share_setting(models.Model):
    _name = "company.share.setting"

    view_beneficiary = fields.Boolean('Beneficiary',)
    view_stakeholder = fields.Boolean('Stakeholder',)
    view_partowner = fields.Boolean('Partowner',)
    
    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
