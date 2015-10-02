# -*- coding: utf-8 -*-
##############################################################################
#
#
##############################################################################

import time
from datetime import datetime
from osv import fields, osv
from tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
import decimal_precision as dp
from tools.translate import _
from openerp import SUPERUSER_ID

class report_account_in_out_tax_review(osv.osv):
    _name = "report.account.in.out.tax.review"

    _columns = {
        'name': fields.char('Name', size=1024),
        'nguoi_nop_thue': fields.char('Người nộp thuế', size=1024),
        'ms_thue': fields.char('Mã số thuế', size=1024),
    }
    
    def print_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'report.account.in.out.tax.review'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'tax_vat_input_review_xls', 'datas': datas}
    
report_account_in_out_tax_review()

class account_ledger_report_review(osv.osv):
    _name = "account.ledger.report.review"
 
    _columns = {
        'name': fields.char('Name', size=1024),
        'don_vi': fields.char('Đơn vị', size=1024),
        'dia_chi': fields.char('Địa chỉ', size=1024),
        'ms_thue': fields.char('MST', size=1024),
        'account_code': fields.char('Tài khoản', size=1024),
        'account_name': fields.char('Ten Tài khoản', size=1024),
        'date_from': fields.char('Từ ngày', size=1024),
        'date_to': fields.char('đến ngày', size=1024),
#         'dvt': fields.char('ĐVT: Đồng', size=1024),
        'ledger_review_line' : fields.one2many('account.ledger.report.review.line','ledger_review_id','Ledger Line'),        
    }
     
    def print_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
#         datas = {'ids': context.get('active_ids', [])}
        datas = {'ids': ids}
        datas['model'] = 'account.ledger.report.review'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':ids[0]})
#         datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'review_account_ledger_report', 'datas': datas}
    
    def print_detail_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': ids}
        datas['model'] = 'account.ledger.report.review'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':ids[0]})
        return {'type': 'ir.actions.report.xml', 'report_name': 'review_account_detail_ledger_report', 'datas': datas}
     
account_ledger_report_review()

class account_ledger_report_review_line(osv.osv):
    _name = "account.ledger.report.review.line"
 
    _columns = {
        'ledger_review_id': fields.many2one('account.ledger.report.review', 'Ledger', readonly=True),
        'ngay_ghso': fields.char('Ngày, tháng ghi sổ', size=1024),
        'so_hieu': fields.char('Chứng từ ghi sổ Số hiệu', size=1024),
        'ngay_thang': fields.char('Chứng từ ghi sổ Ngày tháng', size=1024),
        'dien_giai': fields.char('Diễn giải', size=1024),
        'tk_doi_ung': fields.char('Tài khoản đối ứng', size=1024),
        'so_ps_no': fields.float('Số phát sinh Nợ', readonly=True),
        'so_ps_co': fields.float('Số phát sinh Có', readonly=True),
        'ghi_chu': fields.char('Ghi chú', size=1024),
    }
     
account_ledger_report_review_line()

class so_quy_review(osv.osv):
    _name = "so.quy.review"
 
    _columns = {
        'name': fields.char('Name', size=1024),
        'don_vi': fields.char('Đơn vị', size=1024),
        'dia_chi': fields.char('Địa chỉ', size=1024),
        'account_code': fields.char('Tài khoản', size=1024),
        'account_name': fields.char('Ten Tài khoản', size=1024),
        'date_from': fields.char('Từ ngày', size=1024),
        'date_to': fields.char('đến ngày', size=1024),
        'so_quy_line' : fields.one2many('so.quy.review.line','so_quy_review_id','So Quy Line'),        
    }
     
    def print_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': ids}
        datas['model'] = 'so.quy.review'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':ids[0]})
        return {'type': 'ir.actions.report.xml', 'report_name': 'so_quy_chung_review_report', 'datas': datas}
    
    def print_detail_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': ids}
        datas['model'] = 'so.quy.review'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':ids[0]})
        return {'type': 'ir.actions.report.xml', 'report_name': 'soquy_tienmat_chitiet_review_report', 'datas': datas}
     
    def print_tienmat_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': ids}
        datas['model'] = 'so.quy.review'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':ids[0]})
        return {'type': 'ir.actions.report.xml', 'report_name': 'so_tiengui_nganhang_review_report', 'datas': datas}
so_quy_review()

class so_quy_review_line(osv.osv):
    _name = "so.quy.review.line"
 
    _columns = {
        'so_quy_review_id': fields.many2one('so.quy.review', 'so quy', readonly=True),
        'ngay_ghso': fields.char('Ngày, tháng ghi sổ', size=1024),
        'ngay_thang': fields.char('Ngày tháng chứng từ ', size=1024),
        'so_hieu_thu': fields.char('Số hiệu chứng từ Thu', size=1024),
        'so_hieu_chi': fields.char('Số hiệu chứng từ Chi', size=1024),
        'dien_giai': fields.char('Diễn giải', size=1024),
        'tk_doi_ung': fields.char('Tài khoản đối ứng', size=1024),
        'so_ps_no': fields.float('Số phát sinh Nợ', readonly=True),
        'so_ps_co': fields.float('Số phát sinh Có', readonly=True),
        'so_ps_ton': fields.float('Số phát sinh Tồn', readonly=True),
        'ghi_chu': fields.char('Ghi chú', size=1024),
    }
     
so_quy_review_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
