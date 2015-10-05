# -*- coding: utf-8 -*-
##############################################################################
#
#
##############################################################################

import time
from osv import fields, osv
from tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
import decimal_precision as dp
from tools.translate import _
from openerp import SUPERUSER_ID
from datetime import datetime
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

class general_aged_partner_balance_review(osv.osv):
    _name = "general.aged.partner.balance.review"
 
    _columns = {
        'name': fields.char('Company Name', size=1024),
        'address_company': fields.char('Address', size=1024),
        'vat_company': fields.char('MST', size=1024),
        'account_code': fields.char('Số hiệu TK', size=1024),
        'account_name': fields.char('Tên TK', size=1024),
        'start_date': fields.char('Ngày báo cáo'),
        'general_aged_partner_balance_review_line':fields.one2many('general.aged.partner.balance.review.line','review_id','Each Line'),
    }
     
    def print_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
#         datas = {'ids': context.get('active_ids', [])}
        datas = {'ids': ids}
        datas['model'] = 'general.aged.partner.balance.review'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'general_aged_partner_balance_review_xls', 'datas': datas}
    
general_aged_partner_balance_review()
class general_aged_partner_balance_review_line(osv.osv):
    _name = "general.aged.partner.balance.review.line"
    _columns = {
        'review_id':fields.many2one('general.aged.partner.balance.review','Review'),
        'seq':fields.char('STT', size=1024),
        'partner_code':fields.char('Mã', size=1024),
        'partner_name':fields.char('Tên', size=1024),
        'voucher_no':fields.char('Số CT', size=1024),
        'date_document':fields.char('Ngày CT'),
        'date_due':fields.char('Ngày t.hạn'),
        'description':fields.char('Diễn giải', size=1024),
        'origin_amount':fields.float('Doanh số mua chưa có thuế'),
        'residual_30':fields.float('<= 30 ngày'),
        'residual_90':fields.float('<= 90 ngày'),
        'residual_180':fields.float('<= 180 ngày'),
        'residual_else':fields.float('> 180 ngày'),
        'aging_day':fields.integer('Quá hạn (ngày)'),
                }
general_aged_partner_balance_review_line()

class general_report_partner_ledger_detail_review(osv.osv):
    _name = "general.report.partner.ledger.detail.review"
 
    _columns = {
        'name': fields.char('Company Name', size=1024),
        'address_company': fields.char('Address', size=1024),
        'vat_company': fields.char('MST', size=1024),
        'account_code': fields.char('Số hiệu TK', size=1024),
        'account_name': fields.char('Tên TK', size=1024),
        'start_date': fields.char('Ngày từ'),
        'end_date': fields.char('Ngày đến'),
        'general_report_partner_ledger_detail_review_line':fields.one2many('general.report.partner.ledger.detail.review.line','review_id','Each Line'),
    }
     
    def print_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
#         datas = {'ids': context.get('active_ids', [])}
        datas = {'ids': ids}
        datas['model'] = 'general.report.partner.ledger.detail.review'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'general_report_partner_ledger_detail_review_xls', 'datas': datas}
    
general_report_partner_ledger_detail_review()

class general_report_partner_ledger_detail_review_line(osv.osv):
    _name = "general.report.partner.ledger.detail.review.line"
    _columns = {
        'review_id':fields.many2one('general.report.partner.ledger.detail.review','Review'),
        'seq':fields.char('STT', size=1024),
        'partner_code':fields.char('Mã', size=1024),
        'partner_name':fields.char('Tên', size=1024),
        'begin_dr':fields.float('Nợ'),
        'begin_cr':fields.float('Có'),
        'period_dr':fields.float('Nợ'),
        'period_cr':fields.float('Có'),
        'end_dr':fields.float('Nợ'),
        'end_cr':fields.float('Có'),
                }
general_report_partner_ledger_detail_review_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
