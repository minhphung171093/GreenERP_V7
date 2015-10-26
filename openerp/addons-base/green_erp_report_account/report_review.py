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

class report_account_in_out_tax_review(osv.osv):
    _name = "report.account.in.out.tax.review"

    _columns = {
        'name': fields.char('Name', size=1024),
        'nguoi_nop_thue': fields.char('Người nộp thuế', size=1024),
        'ms_thue': fields.char('Mã số thuế', size=1024),
        'tong_no_tax_0': fields.float('Tổng'),
        'tong_tax_0': fields.float('Tổng'),
        'tong_no_tax_5': fields.float('Tổng'),
        'tong_tax_5': fields.float('Tổng'),
        'tong_no_tax_10': fields.float('Tổng'),
        'tong_tax_10': fields.float('Tổng'),
        'tong_chua_thue':fields.float('Tổng giá trị HHDV mua vào phục vụ SXKD được khấu trừ thuế GTGT (**)'),
        'tong_thue':fields.float('Tổng số thuế GTGT của HHDV mua vào đủ điều kiện được khấu trừ (***)'),
        'accout_in_out_review_khong_thue_line':fields.one2many('report.account.in.out.tax.line','accout_in_id','Review In'),
        'accout_in_out_review_0_line':fields.one2many('report.account.in.out.tax.line.0','0_accout_in_id','Review In'),
        'accout_in_out_review_5_line':fields.one2many('report.account.in.out.tax.line.5','5_accout_in_id','Review In'),
        'accout_in_out_review_10_line':fields.one2many('report.account.in.out.tax.line.10','10_accout_in_id','Review In'),

        
    }
    
    def print_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
#         datas = {'ids': context.get('active_ids', [])}
        datas = {'ids': ids}
        datas['model'] = 'report.account.in.out.tax.review'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'tax_vat_input_review_xls', 'datas': datas}

    def print_xls_out(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
#         datas = {'ids': context.get('active_ids', [])}
        datas = {'ids': ids}
        datas['model'] = 'report.account.in.out.tax.review'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'tax_vat_output_review_xls', 'datas': datas}
    
report_account_in_out_tax_review()
class report_account_in_out_tax_line(osv.osv):
    _name = "report.account.in.out.tax.line"
    _columns = {
        'accout_in_id':fields.many2one('report.account.in.out.tax.review','Report In',ondelete='cascade'),
        'reference':fields.char('STT', size=1024),
        'number':fields.char('Số hoá đơn', size=1024),
        'date_invoice':fields.date('Ngày, tháng, năm phát hành'),
        'partner_name':fields.char('Tên người bán', size=1024),
        'vat_code':fields.char('Mã số thuế người bán', size=1024),
        'price_subtotal':fields.float('Doanh số mua chưa có thuế'),
        'amount_tax':fields.float('Thuế GTGT'),
                }
report_account_in_out_tax_line()
class report_account_in_out_tax_line_0(osv.osv):
    _name = "report.account.in.out.tax.line.0"
    _columns = {
        '0_accout_in_id':fields.many2one('report.account.in.out.tax.review','Report In',ondelete='cascade'),
        'reference':fields.char('STT', size=1024),
        'number':fields.char('Số hoá đơn', size=1024),
        'date_invoice':fields.date('Ngày, tháng, năm phát hành'),
        'partner_name':fields.char('Tên người bán', size=1024),
        'vat_code':fields.char('Mã số thuế người bán', size=1024),
        'price_subtotal':fields.float('Doanh số mua chưa có thuế'),
        'amount_tax':fields.float('Thuế GTGT'),
        }
report_account_in_out_tax_line_0()

class report_account_in_out_tax_line_5(osv.osv):
    _name = "report.account.in.out.tax.line.5"
    _columns = {
        '5_accout_in_id':fields.many2one('report.account.in.out.tax.review','Report In',ondelete='cascade'),
        'reference':fields.char('STT', size=1024),
        'number':fields.char('Số hoá đơn', size=1024),
        'date_invoice':fields.date('Ngày, tháng, năm phát hành'),
        'partner_name':fields.char('Tên người bán', size=1024),
        'vat_code':fields.char('Mã số thuế người bán', size=1024),
        'price_subtotal':fields.float('Doanh số mua chưa có thuế'),
        'amount_tax':fields.float('Thuế GTGT'),
        }
report_account_in_out_tax_line_5()

class report_account_in_out_tax_line_10(osv.osv):
    _name = "report.account.in.out.tax.line.10"
    _columns = {
        '10_accout_in_id':fields.many2one('report.account.in.out.tax.review','Report In',ondelete='cascade'),
        'reference':fields.char('STT', size=1024),
        'number':fields.char('Số hoá đơn', size=1024),
        'date_invoice':fields.date('Ngày, tháng, năm phát hành'),
        'partner_name':fields.char('Tên người bán', size=1024),
        'vat_code':fields.char('Mã số thuế người bán', size=1024),
        'price_subtotal':fields.float('Doanh số mua chưa có thuế'),
        'amount_tax':fields.float('Thuế GTGT'),
        }
report_account_in_out_tax_line_10()

class general_trial_balance_review(osv.osv):
    _name = "general.trial.balance.review"
 
    _columns = {
        'name': fields.char('Name', size=1024),
        'start_date':fields.date('Từ ngày'),
        'end_date':fields.date('đến ngày'),
        'start_date_title':fields.date('Từ ngày'),
        'end_date_title':fields.date('đến ngày'),
        'nguoi_nop_thue': fields.char('Tên công ty', size=1024),
        'nguoi_nop_thue_title': fields.char('Tên công ty', size=1024),
        'dia_chi': fields.char('Địa chỉ', size=1024),       
        'dia_chi_title': fields.char('Địa chỉ', size=1024),  
        'tong_begin_dr':fields.float('Tồng Số dư đầu kỳ (nợ)'),
        'tong_begin_cr':fields.float('Tồng Số dư đầu kỳ (nợ)'),
        'tong_period_dr':fields.float('Tồng Số dư đầu kỳ (nợ)'),
        'tong_period_cr':fields.float('Tồng Số dư đầu kỳ (nợ)'),
        'tong_end_dr':fields.float('Tồng Số dư đầu kỳ (nợ)'),
        'tong_end_cr':fields.float('Tồng Số dư đầu kỳ (nợ)'),        
        'general_trial_balance_review_line':fields.one2many('general.trial.balance.review.line','general_trial_id','Review In'),
        'general_trial_balance_review_line_1':fields.one2many('general.trial.balance.review.line.1','general_trial_id_1','Review In'),
        'general_trial_balance_review_line_2':fields.one2many('general.trial.balance.review.line.2','general_trial_id_2','Review In'),
        
 
         
    }
     
    def print_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
#         datas = {'ids': context.get('active_ids', [])}
        datas = {'ids': ids}
        datas['model'] = 'general.trial.balance.review'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'general_trial_balance_xls', 'datas': datas}
     
general_trial_balance_review()

class general_trial_balance_review_line(osv.osv):
    _name = "general.trial.balance.review.line"
    _columns = {
        'general_trial_id':fields.many2one('general.trial.balance.review','Report In',ondelete='cascade'),
        'coa_code': fields.char('Số tài khoản', size=1024),
        'coa_name': fields.char('Tên tài khoản', size=1024),
        'begin_dr':fields.float('Số dư đầu kỳ (nợ)'),
        'begin_cr':fields.float('Số dư đầu kỳ (có)'),
        'period_dr':fields.float('Phát sinh trong kỳ (nợ)'),
        'period_cr':fields.float('Phát sinh trong kỳ (có)'),
        'end_dr':fields.float('Số dư cuối kỳ (nợ)'),
        'end_cr':fields.float('Số dư cuối kỳ (có)'),

        }
general_trial_balance_review_line()
class general_trial_balance_review_line_1(osv.osv):
    _name = "general.trial.balance.review.line.1"
    _columns = {
        'general_trial_id_1':fields.many2one('general.trial.balance.review','Report In',ondelete='cascade'),
        'coa_code': fields.char('Số tài khoản', size=1024),
        'coa_name': fields.char('Tên tài khoản', size=1024),
        'begin_dr':fields.float('Số dư đầu kỳ (nợ)'),
        'begin_cr':fields.float('Số dư đầu kỳ (có)'),
        'period_dr':fields.float('Phát sinh trong kỳ (nợ)'),
        'period_cr':fields.float('Phát sinh trong kỳ (có)'),
        'end_dr':fields.float('Số dư cuối kỳ (nợ)'),
        'end_cr':fields.float('Số dư cuối kỳ (có)'),
 
        }
general_trial_balance_review_line_1()
class general_trial_balance_review_line_2(osv.osv):
    _name = "general.trial.balance.review.line.2"
    _columns = {
        'general_trial_id_2':fields.many2one('general.trial.balance.review','Report In',ondelete='cascade'),
        'coa_code': fields.char('Số tài khoản', size=1024),
        'coa_name': fields.char('Tên tài khoản', size=1024),
        'begin_dr':fields.float('Số dư đầu kỳ (nợ)'),
        'begin_cr':fields.float('Số dư đầu kỳ (có)'),
        'period_dr':fields.float('Phát sinh trong kỳ (nợ)'),
        'period_cr':fields.float('Phát sinh trong kỳ (có)'),
        'end_dr':fields.float('Số dư cuối kỳ (nợ)'),
        'end_cr':fields.float('Số dư cuối kỳ (có)'),
 
        }
general_trial_balance_review_line_2()

class general_balance_sheet_review(osv.osv):
    _name = "general.balance.sheet.review"
 
    _columns = {
        'name': fields.char('Name', size=1024),
        'start_date':fields.date('Từ ngày'),
        'end_date':fields.date('đến ngày'),
        'start_date_title':fields.date('Từ ngày'),
        'end_date_title':fields.date('đến ngày'),
        'nguoi_nop_thue': fields.char('Tên công ty', size=1024),
        'nguoi_nop_thue_title': fields.char('Tên công ty', size=1024),
        'ms_thue': fields.char('Mã số thuế', size=1024),
        'ms_thue_title': fields.char('Mã số thuế', size=1024),
        'dia_chi': fields.char('Địa chỉ', size=1024),       
        'dia_chi_title': fields.char('Địa chỉ', size=1024),  
        'general_balance_sheet_review_line':fields.one2many('general.balance.sheet.review.line','general_sheet_id','Review In'),
        'general_balance_sheet_review_line_1':fields.one2many('general.balance.sheet.review.line.1','general_sheet_id_1','Review In'),
        
 
         
    }
     
    def print_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
#         datas = {'ids': context.get('active_ids', [])}
        datas = {'ids': ids}
        datas['model'] = 'general.balance.sheet.review'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'general_balance_sheet_xls', 'datas': datas}
     
general_balance_sheet_review()

class general_balance_sheet_review_line(osv.osv):
    _name = "general.balance.sheet.review.line"
    _columns = {
        'general_sheet_id':fields.many2one('general.balance.sheet.review','Report In',ondelete='cascade'),
        'line_no': fields.char('STT', size=1024),
        'description': fields.char('Diễn giải', size=1024),
        'code':fields.char('Mã số', size=1024),
        'illustrate':fields.char('Thuyết minh', size=1024),
        'current_amount':fields.float('Số cuối kỳ'),
        'prior_amount':fields.float('Số đầu kỳ'),
        'format':fields.integer('Số '),
        }
general_balance_sheet_review_line()

class general_balance_sheet_review_line_1(osv.osv):
    _name = "general.balance.sheet.review.line.1"
    _columns = {
        'general_sheet_id_1':fields.many2one('general.balance.sheet.review','Report In',ondelete='cascade'),
        'line_no': fields.char('STT', size=1024),
        'description': fields.char('Diễn giải', size=1024),
        'code':fields.char('Mã số', size=1024),
        'illustrate':fields.char('Thuyết minh', size=1024),
        'current_amount':fields.float('Số cuối kỳ'),
        'prior_amount':fields.float('Số đầu kỳ'),
        'format':fields.integer('Số '),
        }
general_balance_sheet_review_line_1()

class general_account_profit_loss_review(osv.osv):
    _name = "general.account.profit.loss.review"
 
    _columns = {
        'name': fields.char('Name', size=1024),
        'start_date':fields.date('Từ ngày'),
        'end_date':fields.date('đến ngày'),
        'start_date_title':fields.char('Từ ngày'),
        'end_date_title':fields.char('đến ngày'),
        'nguoi_nop_thue': fields.char('Tên công ty', size=1024),
        'nguoi_nop_thue_title': fields.char('Tên công ty', size=1024),
        'ms_thue': fields.char('Mã số thuế', size=1024),
        'ms_thue_title': fields.char('Mã số thuế', size=1024),
        'dia_chi': fields.char('Địa chỉ', size=1024),       
        'dia_chi_title': fields.char('Địa chỉ', size=1024),  
        'general_account_profit_loss_review_line':fields.one2many('general.account.profit.loss.review.line','general_account_id','Review In'),
        
 
         
    }
     
    def print_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
#         datas = {'ids': context.get('active_ids', [])}
        datas = {'ids': ids}
        datas['model'] = 'general.account.profit.loss.review'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'general_account_profit_loss_xls', 'datas': datas}
     
general_account_profit_loss_review()
class general_account_profit_loss_review_line(osv.osv):
    _name = "general.account.profit.loss.review.line"
    _columns = {
        'general_account_id':fields.many2one('general.account.profit.loss.review','Report In',ondelete='cascade'),
        'line_no': fields.char('STT', size=1024),
        'description': fields.char('Diễn giải', size=1024),
        'code':fields.char('Mã số', size=1024),
        'illustrate':fields.char('Thuyết minh', size=1024),
        'curr_amt':fields.float('Số cuối kỳ'),
        'prior_amt':fields.float('Số đầu kỳ'),
        }
general_account_profit_loss_review_line()

class luuchuyen_tiente_review(osv.osv):
    _name = "luuchuyen.tiente.review"
 
    _columns = {
        'name': fields.char('Name', size=1024),
        'start_date':fields.date('Từ ngày'),
        'end_date':fields.date('đến ngày'),
        'start_date_title':fields.char('Từ ngày'),
        'end_date_title':fields.char('đến ngày'),
        'nguoi_nop_thue': fields.char('Tên công ty', size=1024),
        'nguoi_nop_thue_title': fields.char('Tên công ty', size=1024),
        'ms_thue': fields.char('Mã số thuế', size=1024),
        'ms_thue_title': fields.char('Mã số thuế', size=1024),
        'dia_chi': fields.char('Địa chỉ', size=1024),       
        'dia_chi_title': fields.char('Địa chỉ', size=1024),  
        'luuchuyen_tiente_review_line':fields.one2many('luuchuyen.tiente.review.line','luuchuyen_tiente_id','Review In'),
        
 
         
    }
     
    def print_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
#         datas = {'ids': context.get('active_ids', [])}
        datas = {'ids': ids}
        datas['model'] = 'luuchuyen.tiente.review'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'luuchuyen_tiente_xls', 'datas': datas}
     
luuchuyen_tiente_review()
class luuchuyen_tiente_review_line(osv.osv):
    _name = "luuchuyen.tiente.review.line"
    _columns = {
        'luuchuyen_tiente_id':fields.many2one('luuchuyen.tiente.review','Report In',ondelete='cascade'),
        'line_no': fields.char('STT', size=1024),
        'description': fields.char('Diễn giải', size=1024),
        'code':fields.char('Mã số', size=1024),
        'illustrate':fields.char('Thuyết minh', size=1024),
        'curr_amt':fields.float('Số cuối kỳ'),
        'prior_amt':fields.float('Số đầu kỳ'),
        }
luuchuyen_tiente_review_line()

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
        'ledger_review_id': fields.many2one('account.ledger.report.review', 'Ledger',ondelete='cascade', readonly=True),
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
        'so_quy_review_id': fields.many2one('so.quy.review', 'so quy',ondelete='cascade', readonly=True),
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
