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

class congno_vacine_review(osv.osv):
    _name = "congno.vacine.review"
    _columns = {
        'name': fields.char('Name', size=1024),
        'date_from':fields.date('Từ ngày'),
        'date_to':fields.date('đến ngày'),
        'date_from_title':fields.char('Từ ngày', size=1024),
        'date_to_title':fields.char('đến ngày', size=1024),
        'congno_vacine_review_line':fields.one2many('congno.vacine.review.line','congno_vacine_id','Review In'),

        }
    def print_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
#         datas = {'ids': context.get('active_ids', [])}
        datas = {'ids': ids}
        datas['model'] = 'congno.vacine'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'congno_vacine_report', 'datas': datas}    
congno_vacine_review()

class congno_vacine_review_line(osv.osv):
    _name = "congno.vacine.review.line"
    _columns = {
        'congno_vacine_id':fields.many2one('congno.vacine.review','Report In',ondelete='cascade'),
        'stt': fields.char('STT', size=1024),
        'ngay_xuat': fields.date('NGÀY XUẤT'),
        'ma_kh':fields.char('MÃ KH'),
        'so_hd':fields.char('SỐ HĐ'),
        'khach_hang':fields.char('KHÁCH HÀNG'),
        'dia_chi':fields.char('ĐỊA CHỈ'),
        'no_dk':fields.float('NỢ ĐK'),
        'phat_sinh':fields.float('PHÁT SINH'),
        'tt_tien_mat':fields.float('THỰC THU TIỀN MẶT'),
        'tt_ck_exim':fields.float('THỰC THU CK EXIM'),
        'tt_ck_acb':fields.float('THỰC THU CK ACB'),
        'tt_ck_agr':fields.float('THỰC THU CK AGR'),
        'no_ck':fields.float('NỢ CK'),
        'ngay_thanh_toan':fields.char('NGÀY THANH TOÁN', size=1024),
        'so_ngay_no':fields.float('SỐ NGÀY NỢ'),
        'tdv':fields.char('TDV'),
        'tinh_tp':fields.char('TỈNH/THÀNH PHỐ'),
        'hang':fields.char('HÃNG'),

        }
congno_vacine_review_line()

class congno_mypham_review(osv.osv):
    _name = "congno.mypham.review"
    _columns = {
        'name': fields.char('Name', size=1024),
        'date_from':fields.date('Từ ngày'),
        'date_to':fields.date('đến ngày'),
        'date_from_title':fields.char('Từ ngày', size=1024),
        'date_to_title':fields.char('đến ngày', size=1024),
        'congno_mypham_review_line':fields.one2many('congno.mypham.review.line','congno_mypham_id','Review In'),

        }
    def print_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
#         datas = {'ids': context.get('active_ids', [])}
        datas = {'ids': ids}
        datas['model'] = 'congno.mypham'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'congno_mypham_report', 'datas': datas}    
congno_mypham_review()

class congno_mypham_review_line(osv.osv):
    _name = "congno.mypham.review.line"
    _columns = {
        'congno_mypham_id':fields.many2one('congno.mypham.review','Report In',ondelete='cascade'),
        'stt': fields.char('STT', size=1024),
        'ngay_xuat': fields.char('NGÀY XUẤT', size=1024),
        'ma_kh':fields.char('MÃ KH'),
        'so_hd':fields.char('SỐ HĐ'),
        'khach_hang':fields.char('KHÁCH HÀNG'),
        'dia_chi':fields.char('ĐỊA CHỈ'),
        'no_dk':fields.float('NỢ ĐK'),
        'phat_sinh':fields.float('PHÁT SINH'),
        'tt_tien_mat':fields.float('THỰC THU TIỀN MẶT'),
        'tt_ck_exim':fields.float('THỰC THU CK EXIM'),
        'tt_ck_acb':fields.float('THỰC THU CK ACB'),
        'tt_ck_agr':fields.float('THỰC THU CK AGR'),
        'no_ck':fields.float('NỢ CK'),
        'ngay_thanh_toan':fields.char('NGÀY THANH TOÁN', size=1024),
        'so_ngay_no':fields.float('SỐ NGÀY NỢ'),
        'tdv':fields.char('TDV'),
        'tinh_tp':fields.char('TỈNH/THÀNH PHỐ'),
        'hang':fields.char('HÃNG'),

        }
congno_mypham_review_line()

class congno_duocpham_review(osv.osv):
    _name = "congno.duocpham.review"
    _columns = {
        'name': fields.char('Name', size=1024),
        'date_from':fields.date('Từ ngày'),
        'date_to':fields.date('đến ngày'),
        'date_from_title':fields.char('Từ ngày', size=1024),
        'date_to_title':fields.char('đến ngày', size=1024),
        'congno_duocpham_review_line':fields.one2many('congno.duocpham.review.line','congno_duocpham_id','Review In'),

        }
    def print_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
#         datas = {'ids': context.get('active_ids', [])}
        datas = {'ids': ids}
        datas['model'] = 'congno.duocpham'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'congno_duocpham_report', 'datas': datas}    
congno_duocpham_review()

class congno_duocpham_review_line(osv.osv):
    _name = "congno.duocpham.review.line"
    _columns = {
        'congno_duocpham_id':fields.many2one('congno.duocpham.review','Report In',ondelete='cascade'),
        'stt': fields.char('STT', size=1024),
        'ngay_xuat': fields.char('NGÀY XUẤT', size=1024),
        'ma_kh':fields.char('MÃ KH'),
        'so_hd':fields.char('SỐ HĐ'),
        'khach_hang':fields.char('KHÁCH HÀNG'),
        'dia_chi':fields.char('ĐỊA CHỈ'),
        'no_dk':fields.float('NỢ ĐK'),
        'phat_sinh':fields.float('PHÁT SINH'),
        'tt_tien_mat':fields.float('THỰC THU TIỀN MẶT'),
        'tt_ck_exim':fields.float('THỰC THU CK EXIM'),
        'tt_ck_acb':fields.float('THỰC THU CK ACB'),
        'tt_ck_agr':fields.float('THỰC THU CK AGR'),
        'no_ck':fields.float('NỢ CK'),
        'ngay_thanh_toan':fields.char('NGÀY THANH TOÁN', size=1024),
        'so_ngay_no':fields.float('SỐ NGÀY NỢ'),
        'tdv':fields.char('TDV'),
        'tinh_tp':fields.char('TỈNH/THÀNH PHỐ'),
        'hang':fields.char('HÃNG'),

        }
congno_duocpham_review_line()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
