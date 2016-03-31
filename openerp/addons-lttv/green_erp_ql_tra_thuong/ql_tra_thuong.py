# -*- coding: utf-8 -*-
import datetime
import time
from itertools import groupby
from operator import itemgetter
import openerp.addons.decimal_precision as dp
import math
from openerp import netsvc
from openerp import tools
from openerp.osv import fields, osv
from openerp.tools.translate import _
import base64
import xlrd
from xlrd import open_workbook,xldate_as_tuple
DATE_FORMAT = "%Y-%m-%d"

class res_partner(osv.osv):
    _inherit = "res.partner"
     
    _columns = {
        'account_tra_thuong_id': fields.many2one('account.account', 'Tài khoản trả thưởng'),
    }
     
res_partner()

class tra_thuong(osv.osv):
    _name = "tra.thuong"
    
    def _amount_tong(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        if context is None:
            context = {}
        for trathuong in self.browse(cr, uid, ids, context=context):
            sum = 0
            for line in trathuong.tra_thuong_line:
                sum += line.sl_trung * line.slan_trung * line.tong_tien
            res[trathuong.id] = sum
        return res
    
    def _get_line(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('tra.thuong.line').browse(cr, uid, ids, context=context):
            result[line.trathuong_id.id] = True
        return result.keys()
    
    _columns = {
        'daily_id': fields.many2one('res.partner','Đại lý',domain="[('dai_ly','=',True)]",required=True,states={'done':[('readonly',True)]}),
#         'journal_id': fields.many2one('account.journal','Phương thức thanh toán',states={'done':[('readonly',True)]}),
        'ngay': fields.date('Ngày xổ số', readonly=True),
        'tra_thuong_line': fields.one2many('tra.thuong.line','trathuong_id','Line',states={'done':[('readonly',True)]}),
        'tong_cong': fields.function(_amount_tong, string='Tổng cộng',
            store={
                'tra.thuong': (lambda self, cr, uid, ids, c={}: ids, ['tra_thuong_line'], 20),
                'tra.thuong.line': (_get_line, ['giai','loai','product_id','sl_trung', 'slan_trung','tong_trung', 'tong_tien'], 20),
            },
            ),
        'state': fields.selection([('new','Mới tạo'),('done','Hết hạn')],'Trạng thái'),
        'parent_id': fields.many2one('tra.thuong','Parent',ondelete='cascade'),
        'lichsu_line': fields.one2many('tra.thuong','parent_id','Lịch sử', readonly=False),
        'so_vanban': fields.char('Biên bản số',readonly=True),
        'date': fields.date('Ngày',readonly=True),
    }
    
    _defaults = {
        'state': 'new',
    }
    
#     def write(self, cr, uid, ids, vals, context=None):
#         context = context or {}
#         return super(tra_thuong, self).write(cr, uid, ids, vals, context=context)
    
    def save(self, cr, uid, ids, vals, context=None):
        res = {
               'type': 'ir.actions.client',
               'tag': 'reload',
               'context' : context,
               }
        a = {'type': 'ir.actions.act_window_close'}
        return res
        
    def chinhsua(self, cr, uid, ids, vals, context=None):
        mod_obj = self.pool.get('ir.model.data')
        model_data_ids = mod_obj.search(cr, uid, [('model', '=', 'ir.ui.view'),('name', '=', 'view_chinhsua_trathuong')], context=context)
        resource_id = mod_obj.read(cr, uid, model_data_ids, fields=['res_id'], context=context)[0]['res_id']
        return {
            'name': _('Chỉnh Sửa Trả Thưởng'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'chinhsua.trathuong',
            'views': [(resource_id,'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
            }
    
tra_thuong()

class tra_thuong_line(osv.osv):
    _name = "tra.thuong.line"
    
    def _get_gia_moilantrung(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            gt_menhgia = int(line.product_id.list_price)/10000
            if line.loai=='2_so' and line.giai=='dau':
                res[line.id] = 700000*gt_menhgia
            if line.loai=='2_so' and line.giai=='cuoi':
                res[line.id] = 700000*gt_menhgia
            if line.loai=='2_so' and line.giai=='dau_cuoi':
                res[line.id] = 350000*gt_menhgia
            if line.loai=='2_so' and line.giai=='18_lo':
                res[line.id] = 39000*gt_menhgia
            if line.loai=='3_so' and line.giai=='dau':
                res[line.id] = 5000000*gt_menhgia
            if line.loai=='3_so' and line.giai=='cuoi':
                res[line.id] = 5000000*gt_menhgia
            if line.loai=='3_so' and line.giai=='dau_cuoi':
                res[line.id] = 2500000*gt_menhgia
            if line.loai=='3_so' and line.giai=='7_lo':
                res[line.id] = 715000*gt_menhgia
            if line.loai=='3_so' and line.giai=='17_lo':
                res[line.id] = 295000*gt_menhgia
            if line.loai=='4_so' and line.giai=='16_lo':
                res[line.id] = 2000000*gt_menhgia
        return res
    
    def _get_tong(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = line.sl_trung * line.slan_trung * line.tong_tien
        return res
    
    _columns = {
        'name': fields.char('Số trúng thưởng',size=1024,required=True),
        'product_id': fields.many2one('product.product','Mệnh giá',domain="[('menh_gia','=',True)]",required=True),
        'trathuong_id': fields.many2one('tra.thuong','Trả thưởng',ondelete='cascade'),
        'loai': fields.selection([('2_so','2 số'),('3_so','3 số'),('4_so','4 số')],'Loại',required=True),
        'giai': fields.selection([('dau','Đầu'),('cuoi','Cuối'),('dau_cuoi','Đầu/Cuối'),('18_lo','18 Lô'),('7_lo','7 Lô'),('17_lo','17 Lô'),('16_lo','16 Lô')], 'Giải',required=True),
        'sl_trung': fields.integer('Số lượng',required=True),
        'slan_trung': fields.integer('Số lần',required=True),
        'tong_tien': fields.function(_get_gia_moilantrung,string='Số tiền',type='float',store=True),
        'tong': fields.function(_get_tong, string='Tổng', type='float'),
    }
    
    _defaults = {
        'sl_trung': 1,
        'slan_trung': 1,
    }
    
tra_thuong_line()

class tra_thuong_thucte(osv.osv):
    _name = "tra.thuong.thucte"
    
    def tao_phieu_chi(self, cr, uid, ids, context=None):
        voucher = self.pool.get('account.voucher')
        voucher_batch_obj = self.pool.get('account.voucher.batch')
        fields_list = ['comment', 'line_cr_ids', 'is_multi_currency', 'reference', 'line_dr_ids', 'company_id', 'currency_id', 
                         'narration', 'partner_id', 'payment_rate_currency_id', 'paid_amount_in_company_currency', 
                         'writeoff_acc_id', 'state', 'pre_line', 'type', 'payment_option', 'account_id', 'period_id', 'date', 
                         'reference_number', 'payment_rate', 'name', 'writeoff_amount', 'analytic_id', 'journal_id', 'amount']
        res ={}
        user = self.pool.get('res.users').browse(cr, uid, uid)
        date_now = time.strftime('%Y-%m-%d')
        for trathuong in self.browse(cr, uid, ids):
            
            diff_day = self._get_number_of_days(trathuong.ngay,trathuong.ngay_tra_thuong)
            if not trathuong.is_manager_check and diff_day>30:
                sql = '''
                    update tra_thuong_thucte set show_manager_check='t' where id = %s;
                    commit;
                '''%(trathuong.id)
                cr.execute(sql)
                raise osv.except_osv(_('Cảnh báo!'),_('''Đã quá 30 ngày kể từ ngày xổ số'''))
            
            if not trathuong.tong_cong:
                raise osv.except_osv(_('Cảnh báo!'),_('Không thể tạo phiếu chi với tổng tiền bằng "0"!'))
            ngay = trathuong.ngay
            sql = '''
                select product_id,name, loai, giai,sum(sl_trung) as sl_trung
                    from tra_thuong_thucte_line
                    where trathuong_id=%s
                    group by product_id,name, loai, giai
            '''%(trathuong.id)
            cr.execute(sql)
            trathuong_line = cr.dictfetchall()
            for trath in trathuong_line:
                sql = '''
                    select slan_trung,case when sum(sl_trung)!=0 then sum(sl_trung) else 0 end sl_trung from tra_thuong_line where product_id = %s and name='%s' and loai='%s' and giai='%s' and
                        trathuong_id in (select id from tra_thuong where ngay = '%s' and parent_id is null) group by slan_trung
                '''%(trath['product_id'], trath['name'], trath['loai'], trath['giai'], ngay)
                cr.execute(sql)
                test = cr.dictfetchone()
                if not test:
                    raise osv.except_osv(_('Cảnh báo!'),_('Không tìm thấy số trúng thưởng "%s" trong danh sách cần trả thưởng ngày "%s"!')%(trath['name'],ngay[8:10]+'-'+ngay[5:7]+'-'+ngay[:4]))
                sl_phaitra = test['sl_trung']
                slan_trung = test['slan_trung']
                if sl_phaitra==0:
                    raise osv.except_osv(_('Cảnh báo!'),_('Không tìm thấy số trúng thưởng "%s" trong danh sách cần trả thưởng ngày "%s"!')%(trath['name'],ngay[8:10]+'-'+ngay[5:7]+'-'+ngay[:4]))
                
                sql = '''
                    select case when sum(sl_trung)!=0 then sum(sl_trung) else 0 end sl_datra from tra_thuong_thucte_line where product_id = %s and name='%s' and loai='%s' and giai='%s' and
                        trathuong_id in (select id from tra_thuong_thucte where ngay = '%s' and state='done')
                '''%(trath['product_id'], trath['name'], trath['loai'], trath['giai'], ngay)
                cr.execute(sql)
                sl_datra = cr.dictfetchone()['sl_datra']
                if sl_phaitra - sl_datra < trath['sl_trung']:
                    raise osv.except_osv(_('Cảnh báo!'),_('''Số lượng nhập lớn hơn số lượng cần trả thưởng còn lại ngày "%s"!\n
                                        Số lượng còn lại: %s''')%(ngay[8:10]+'-'+ngay[5:7]+'-'+ngay[:4],sl_phaitra - sl_datra))
            
#             line_vals = []
#             for line in trathuong.tra_thuong_line:
#                 voucher_context = {
#                     'payment_expected_currency': user.company_id.currency_id.id,
#                     'default_partner_id': self.pool.get('res.partner')._find_accounting_partner(trathuong.daily_id).id,
#                     'default_amount': line.tong,
# #                     'default_reference': inv.name,
#                     'close_after_process': True,
# #                     'invoice_type': inv.type,
# #                     'invoice_id': inv.id,
#                     'default_type': 'payment',
#                     'type': 'payment',
#                 }
#                 vals = voucher.default_get(cr, uid, fields_list, context=voucher_context)
#                 res = voucher.onchange_journal(cr, uid, [], trathuong.journal_id.id, 
#                                                False, False, trathuong.daily_id.id, 
#                                                date_now, 
#                                                line.tong, 
#                                                vals['type'], vals['company_id'], context=voucher_context)
#                 vals = dict(vals.items() + res['value'].items())
# #                 line_cr_ids = []
# #                 line_dr_ids = []
# #                 for line_cr in vals['line_cr_ids']:
# #                     line_cr_ids.append((0,0,line_cr))
# #                 for line_dr in vals['line_dr_ids']:
# #                     line_dr_ids.append((0,0,line_dr))
# #                 vals['line_cr_ids'] = line_cr_ids
# #                 vals['line_dr_ids'] = line_dr_ids
#                 
#                 vals['line_dr_ids'] = [(0,0,{
#                                              'account_id':trathuong.daily_id.account_tra_thuong_id.id,
#                                              'name': 'Chi trả thưởng vé LTTC '+line.name,
#                                              'amount': line.tong,
#                                      })]
#                 vals.update({'journal_id':trathuong.journal_id.id,
#                              'assign_user': trathuong.nguoi_nhan_thuong,})
#                 
#                 line_vals.append((0,0,vals))
#             account_id = voucher_batch_obj.onchange_journal(cr, uid, [], trathuong.journal_id.id)['value']['account_id']
#             voucher_batch_obj.create(cr, uid, {
#                 'journal_id': trathuong.journal_id.id,
#                 'account_id': account_id,
#                 'date': date_now,
#                 'assign_user': trathuong.nguoi_nhan_thuong,
#                 'voucher_lines': line_vals,
#                 'description': 'Chi trả thưởng vé LTTC',
#                 'trathuong_thucte_id': trathuong.id,
#             })
        return self.write(cr, uid, ids, {'state':'done'})
    
    def _amount_tong(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        if context is None:
            context = {}
        for trathuong in self.browse(cr, uid, ids, context=context):
            sum = 0
            for line in trathuong.tra_thuong_line:
                sum += line.sl_trung * line.slan_trung * line.tong_tien
            res[trathuong.id] = sum
        return res
    
    def _get_line(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('tra.thuong.thucte.line').browse(cr, uid, ids, context=context):
            result[line.trathuong_id.id] = True
        return result.keys()
    
    _columns = {
        'daily_id': fields.many2one('res.partner','Đại lý',domain="[('dai_ly','=',True)]",required=False,states={'done':[('readonly',True)]}),
        'nguoi_nhan_thuong': fields.char('Người nhận thưởng', size=1024, required=True,states={'done':[('readonly',True)]}),
        'journal_id': fields.many2one('account.journal','Phương thức thanh toán', required=False,states={'done':[('readonly',True)]}),
        'ngay': fields.date('Ngày xổ số', required=True,states={'done':[('readonly',True)]}),
        'ngay_tra_thuong': fields.date('Ngày trả thưởng', required=True,states={'done':[('readonly',True)]}),
        'tra_thuong_line': fields.one2many('tra.thuong.thucte.line','trathuong_id','Line',states={'done':[('readonly',True)]}),
        'is_manager_check': fields.boolean('Is Manager Check'),
        'show_manager_check': fields.boolean('Show Manager Check'),
        'tong_cong': fields.function(_amount_tong, string='Tổng cộng',
            store={
                'tra.thuong.thucte': (lambda self, cr, uid, ids, c={}: ids, ['tra_thuong_line'], 20),
                'tra.thuong.thucte.line': (_get_line, ['giai','loai','product_id','sl_trung', 'slan_trung','tong_trung', 'tong_tien'], 20),
            },
            ),
        'state': fields.selection([('new','Mới tạo'),('done','Đã trả')],'Trạng thái'),
    }
    
    _defaults = {
        'state': 'new',
        'ngay_tra_thuong': lambda *a: time.strftime('%Y-%m-%d'),
    }
    
    def _get_number_of_days(self, date_from, date_to):
        """Returns a float equals to the timedelta between two dates given as string."""
  
        DATETIME_FORMAT = "%Y-%m-%d"
        from_dt = datetime.datetime.strptime(date_from, DATETIME_FORMAT)
        to_dt = datetime.datetime.strptime(date_to, DATETIME_FORMAT)
        timedelta = to_dt - from_dt
        diff_day = timedelta.days
        return diff_day
    
    def quan_ly_duyet(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'is_manager_check':True,'show_manager_check':False}, context)
    
    def create(self, cr, uid, vals, context=None):
        new_id = super(tra_thuong_thucte, self).create(cr, uid, vals, context)
        tra_truong = self.browse(cr,uid,new_id)
        ngay = tra_truong.ngay
        sql = '''
            select product_id,name, loai, giai,sum(sl_trung) as sl_trung
                from tra_thuong_thucte_line
                where trathuong_id=%s
                group by product_id,name, loai, giai
        '''%(new_id)
        cr.execute(sql)
        trathuong_line = cr.dictfetchall()
        for trathuong in trathuong_line:
            sql = '''
                select slan_trung,case when sum(sl_trung)!=0 then sum(sl_trung) else 0 end sl_trung from tra_thuong_line where product_id = %s and name='%s' and loai='%s' and giai='%s' and
                    trathuong_id in (select id from tra_thuong where ngay = '%s' and parent_id is null) group by slan_trung
            '''%(trathuong['product_id'], trathuong['name'], trathuong['loai'], trathuong['giai'], ngay)
            cr.execute(sql)
            test = cr.dictfetchone()
            if not test:
                raise osv.except_osv(_('Cảnh báo!'),_('Không tìm thấy số trúng thưởng "%s" trong danh sách cần trả thưởng ngày "%s"!')%(trathuong['name'],ngay[8:10]+'-'+ngay[5:7]+'-'+ngay[:4]))
            sl_phaitra = test['sl_trung']
            slan_trung = test['slan_trung']
            if sl_phaitra==0:
                raise osv.except_osv(_('Cảnh báo!'),_('Không tìm thấy số trúng thưởng "%s" trong danh sách cần trả thưởng ngày "%s"!')%(trathuong['name'],ngay[8:10]+'-'+ngay[5:7]+'-'+ngay[:4]))
            
            sql = '''
                select case when sum(sl_trung)!=0 then sum(sl_trung) else 0 end sl_datra from tra_thuong_thucte_line where product_id = %s and name='%s' and loai='%s' and giai='%s' and
                    trathuong_id in (select id from tra_thuong_thucte where ngay = '%s' and state='done')
            '''%(trathuong['product_id'], trathuong['name'], trathuong['loai'], trathuong['giai'], ngay)
            cr.execute(sql)
            sl_datra = cr.dictfetchone()['sl_datra']
            if sl_phaitra - sl_datra < trathuong['sl_trung']:
                raise osv.except_osv(_('Cảnh báo!'),_('''Số lượng nhập lớn hơn số lượng cần trả thưởng còn lại ngày "%s"!\n
                                    Số lượng còn lại: %s''')%(ngay[8:10]+'-'+ngay[5:7]+'-'+ngay[:4],sl_phaitra - sl_datra))
        return new_id
    
    def write(self, cr, uid, ids, vals, context=None):
        res = super(tra_thuong_thucte, self).write(cr, uid, ids, vals, context=context)
        for tra_truong in self.browse(cr, uid, ids, context):
            ngay = tra_truong.ngay
            sql = '''
                select product_id,name, loai, giai,sum(sl_trung) as sl_trung
                    from tra_thuong_thucte_line
                    where trathuong_id=%s
                    group by product_id,name, loai, giai
            '''%(tra_truong.id)
            cr.execute(sql)
            trathuong_line = cr.dictfetchall()
            for trathuong in trathuong_line:
                sql = '''
                    select slan_trung,case when sum(sl_trung)!=0 then sum(sl_trung) else 0 end sl_trung from tra_thuong_line where product_id = %s and name='%s' and loai='%s' and giai='%s' and
                        trathuong_id in (select id from tra_thuong where ngay = '%s' and parent_id is null) group by slan_trung
                '''%(trathuong['product_id'], trathuong['name'], trathuong['loai'], trathuong['giai'], ngay)
                cr.execute(sql)
                test = cr.dictfetchone()
                if not test:
                    raise osv.except_osv(_('Cảnh báo!'),_('Không tìm thấy số trúng thưởng "%s" trong danh sách cần trả thưởng ngày "%s"!')%(trathuong['name'],ngay[8:10]+'-'+ngay[5:7]+'-'+ngay[:4]))
                sl_phaitra = test['sl_trung']
                slan_trung = test['slan_trung']
                if sl_phaitra==0:
                    raise osv.except_osv(_('Cảnh báo!'),_('Không tìm thấy số trúng thưởng "%s" trong danh sách cần trả thưởng ngày "%s"!')%(trathuong['name'],ngay[8:10]+'-'+ngay[5:7]+'-'+ngay[:4]))
                
                sql = '''
                    select case when sum(sl_trung)!=0 then sum(sl_trung) else 0 end sl_datra from tra_thuong_thucte_line where product_id = %s and name='%s' and loai='%s' and giai='%s' and
                        trathuong_id in (select id from tra_thuong_thucte where ngay = '%s' and state='done' and id!=%s)
                '''%(trathuong['product_id'], trathuong['name'], trathuong['loai'], trathuong['giai'], ngay,tra_truong.id)
                cr.execute(sql)
                sl_datra = cr.dictfetchone()['sl_datra']
                if sl_phaitra - sl_datra < trathuong['sl_trung']:
                    raise osv.except_osv(_('Cảnh báo!'),_('''Số lượng nhập lớn hơn số lượng cần trả thưởng còn lại ngày "%s"!\n
                                        Số lượng còn lại: %s''')%(ngay[8:10]+'-'+ngay[5:7]+'-'+ngay[:4],sl_phaitra - sl_datra))
        return res
    
tra_thuong_thucte()

class tra_thuong_thucte_line(osv.osv):
    _name = "tra.thuong.thucte.line"
    
    def _get_gia_moilantrung(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            gt_menhgia = int(line.product_id.list_price)/10000
            if line.loai=='2_so' and line.giai=='dau':
                res[line.id] = 700000*gt_menhgia
            if line.loai=='2_so' and line.giai=='cuoi':
                res[line.id] = 700000*gt_menhgia
            if line.loai=='2_so' and line.giai=='dau_cuoi':
                res[line.id] = 350000*gt_menhgia
            if line.loai=='2_so' and line.giai=='18_lo':
                res[line.id] = 39000*gt_menhgia
            if line.loai=='3_so' and line.giai=='dau':
                res[line.id] = 5000000*gt_menhgia
            if line.loai=='3_so' and line.giai=='cuoi':
                res[line.id] = 5000000*gt_menhgia
            if line.loai=='3_so' and line.giai=='dau_cuoi':
                res[line.id] = 2500000*gt_menhgia
            if line.loai=='3_so' and line.giai=='7_lo':
                res[line.id] = 715000*gt_menhgia
            if line.loai=='3_so' and line.giai=='17_lo':
                res[line.id] = 295000*gt_menhgia
            if line.loai=='4_so' and line.giai=='16_lo':
                res[line.id] = 2000000*gt_menhgia
        return res
    
    def _get_tong(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = line.sl_trung * line.slan_trung * line.tong_tien
        return res
    
    def onchange_product(self, cr, uid, ids, product_id=False,name=False,loai=False,giai=False,ngay=False,sl_trung=False,daily_id=False, context=None):
        res = {}
        warning = {}
        sl_chuatra = 0
        tra_thuong_line_obj = self.pool.get('tra.thuong.line')
        if product_id and name and loai and giai and ngay:
            sql = '''
                select slan_trung,case when sum(sl_trung)!=0 then sum(sl_trung) else 0 end sl_trung from tra_thuong_line where product_id = %s and name='%s' and loai='%s' and giai='%s' and
                    trathuong_id in (select id from tra_thuong where ngay = '%s' and parent_id is null) group by slan_trung
            '''%(product_id, name, loai, giai, ngay)
            cr.execute(sql)
            test = cr.dictfetchone()
            if not test:
                res = {'name':''}
                warning = {  
                        'title': _('Cảnh báo!'),  
                        'message': _('''Không tìm thấy số trúng thưởng "%s" trong danh sách cần trả thưởng ngày "%s"!''')%(name,ngay[8:10]+'-'+ngay[5:7]+'-'+ngay[:4]), 
                        }
                return {'value': res,'warning':warning}
#                 raise osv.except_osv(_('Cảnh báo!'),_('Không tìm thấy số trúng thưởng "%s" trong danh sách cần trả thưởng ngày "%s"!')%(name,ngay[8:10]+'-'+ngay[5:7]+'-'+ngay[:4]))
            sl_phaitra = test['sl_trung']
            slan_trung = test['slan_trung']
            if sl_phaitra==0:
                raise osv.except_osv(_('Cảnh báo!'),_('Không tìm thấy số trúng thưởng "%s" trong danh sách cần trả thưởng ngày "%s"!')%(name,ngay[8:10]+'-'+ngay[5:7]+'-'+ngay[:4]))
            
            sql = '''
                select case when sum(sl_trung)!=0 then sum(sl_trung) else 0 end sl_datra from tra_thuong_thucte_line where product_id = %s and name='%s' and loai='%s' and giai='%s' and
                    trathuong_id in (select id from tra_thuong_thucte where ngay = '%s' and state='done')
            '''%(product_id, name, loai, giai, ngay)
            cr.execute(sql)
            sl_datra = cr.dictfetchone()['sl_datra']
            res = {'sl_trung':sl_phaitra - sl_datra,'slan_trung':slan_trung}
            if sl_trung:
                res.update({'sl_trung':sl_trung})
                if sl_phaitra - sl_datra < sl_trung:
                    res.update({'sl_trung':sl_phaitra - sl_datra})
                    warning = {  
                        'title': _('Cảnh báo!'),  
                        'message': _('''Số lượng nhập lớn hơn số lượng cần trả thưởng còn lại ngày "%s"!\n
                                        Số lượng còn lại: %s''')%(ngay[8:10]+'-'+ngay[5:7]+'-'+ngay[:4],sl_phaitra - sl_datra),  
                        }
        return {'value': res,'warning':warning}
    _columns = {
        'name': fields.char('Số trúng thưởng',size=1024,required=True),
        'product_id': fields.many2one('product.product','Mệnh giá',domain="[('menh_gia','=',True)]",required=True),
        'trathuong_id': fields.many2one('tra.thuong.thucte','Trả thưởng',ondelete='cascade'),
        'loai': fields.selection([('2_so','2 số'),('3_so','3 số'),('4_so','4 số')],'Loại',required=True),
        'giai': fields.selection([('dau','Đầu'),('cuoi','Cuối'),('dau_cuoi','Đầu/Cuối'),('18_lo','18 Lô'),('7_lo','7 Lô'),('17_lo','17 Lô'),('16_lo','16 Lô')], 'Giải',required=True),
        'sl_trung': fields.integer('Số lượng',required=True),
        'slan_trung': fields.integer('Số lần',required=True,readonly=False),
        'tong_tien': fields.function(_get_gia_moilantrung,string='Số tiền',type='float',store=True),
        'tong': fields.function(_get_tong, string='Tổng', type='float'),
    }
    
    _defaults = {
        'sl_trung': 1,
        'slan_trung': 1,
    }
    
tra_thuong_thucte_line()
