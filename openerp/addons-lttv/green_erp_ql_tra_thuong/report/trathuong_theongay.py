# -*- coding: utf-8 -*-
##############################################################################
#
#    HLVSolution, Open Source Management Solution
#
##############################################################################
import time
from openerp.report import report_sxw
from openerp import pooler
from openerp.osv import osv
from openerp.tools.translate import _
import random
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class Parser(report_sxw.rml_parse):
        
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        pool = pooler.get_pool(self.cr.dbname)
        self.localcontext.update({
            'get_menh_gia': self.get_menh_gia,
            'get_date_from': self.get_date_from,
            'get_daiduthuong': self.get_daiduthuong,
            'get_chuatra_dauky': self.get_chuatra_dauky,
            'get_phaitratrongky': self.get_phaitratrongky,
            'get_datratrongky': self.get_datratrongky,
            'get_conlaicuoiky': self.get_conlaicuoiky,
            'get_congchuatradauky': self.get_congchuatradauky,
            'get_congphaitratrongky': self.get_congphaitratrongky,
            'get_congdatratrongky': self.get_congdatratrongky,
            'get_congconlaicuoiky': self.get_congconlaicuoiky,
            'get_tongcongchuatradauky': self.get_tongcongchuatradauky,
            'get_tongcongphaitratrongky': self.get_tongcongphaitratrongky,
            'get_tongcongdatratrongky': self.get_tongcongdatratrongky,
            'get_tongcongconlaicuoiky': self.get_tongcongconlaicuoiky,
        })
    
    def get_date_from(self):
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        return date_from[8:10]+'/'+date_from[5:7]+'/'+date_from[:4]
    
    def get_daiduthuong(self):
        wizard_data = self.localcontext['data']['form']
        date = wizard_data['date_from']
        ketqua_obj = self.pool.get('ketqua.xoso')
        ketqua_ids = ketqua_obj.search(self.cr ,self.uid, [('name','=',date),('state','=','validate')])
        if not ketqua_ids:
            raise osv.except_osv(_('Cảnh báo!'),_('Chưa có kết quả xổ số ngày %s!')%(date))
        return ketqua_obj.browse(self.cr, self.uid, ketqua_ids[0]).dai_duthuong_id.name
    
    def get_menh_gia(self):
        menhgia_obj = self.pool.get('product.product')
        menh_gia_ids = menhgia_obj.search(self.cr, self.uid, [('menh_gia','=',True)])
        return menhgia_obj.browse(self.cr, self.uid, menh_gia_ids)
    
    def get_chuatra_dauky(self,menhgia_id,loai):
        thucte = 0
        quydoi = 0
        giatri = 0
        tt_obj = self.pool.get('tra.thuong.line')
        tt_tt_obj = self.pool.get('tra.thuong.thucte.line')
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        if loai=='2_d':
            sql = '''
                select id from tra_thuong_line where loai='2_so' and giai='dau' and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong where ngay<'%(date_from)s')
            '''%{
                 'product_id': menhgia_id,
                 'date_from': date_from,
            }
        if loai=='2_c':
            sql = '''
                select id from tra_thuong_line where loai='2_so' and giai='cuoi' and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong where ngay<'%(date_from)s')
            '''%{
                 'product_id': menhgia_id,
                 'date_from': date_from,
            }
        if loai=='2_dc':
            sql = '''
                select id from tra_thuong_line where loai='2_so' and giai='dau_cuoi' and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong where ngay<'%(date_from)s')
            '''%{
                 'product_id': menhgia_id,
                 'date_from': date_from,
            }
        if loai=='2_18':
            sql = '''
                select id from tra_thuong_line where loai='2_so' and giai='18_lo' and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong where ngay<'%(date_from)s')
            '''%{
                 'product_id': menhgia_id,
                 'date_from': date_from,
            }
        if loai=='3_d':
            sql = '''
                select id from tra_thuong_line where loai='3_so' and giai='dau' and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong where ngay<'%(date_from)s')
            '''%{
                 'product_id': menhgia_id,
                 'date_from': date_from,
            }
        if loai=='3_c':
            sql = '''
                select id from tra_thuong_line where loai='3_so' and giai='cuoi' and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong where ngay<'%(date_from)s')
            '''%{
                 'product_id': menhgia_id,
                 'date_from': date_from,
            }
        if loai=='3_dc':
            sql = '''
                select id from tra_thuong_line where loai='3_so' and giai='dau_cuoi' and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong where ngay<'%(date_from)s')
            '''%{
                 'product_id': menhgia_id,
                 'date_from': date_from,
            }
        if loai=='3_7':
            sql = '''
                select id from tra_thuong_line where loai='3_so' and giai='7_lo' and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong where ngay<'%(date_from)s')
            '''%{
                 'product_id': menhgia_id,
                 'date_from': date_from,
            }
        if loai=='3_17':
            sql = '''
                select id from tra_thuong_line where loai='3_so' and giai='17_lo' and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong where ngay<'%(date_from)s')
            '''%{
                 'product_id': menhgia_id,
                 'date_from': date_from,
            }
        if loai=='4_16':
            sql = '''
                select id from tra_thuong_line where loai='4_so' and giai='16_lo' and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong where ngay<'%(date_from)s')
            '''%{
                 'product_id': menhgia_id,
                 'date_from': date_from,
            }
        self.cr.execute(sql)
        tt_ids = [r[0] for r in self.cr.fetchall()]
        for tt in tt_obj.browse(self.cr, self.uid, tt_ids):
            thucte += tt.sl_trung
            quydoi += (tt.slan_trung*tt.sl_trung)
            giatri += tt.tong
            
        if loai=='2_d':
            sql = '''
                select id from tra_thuong_thucte_line where loai='2_so' and giai='dau' and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong_thucte where state='done' and ngay_tra_thuong<'%(date_from)s')
            '''%{
                 'product_id': menhgia_id,
                 'date_from': date_from,
            }
        if loai=='2_c':
            sql = '''
                select id from tra_thuong_thucte_line where loai='2_so' and giai='cuoi' and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong_thucte where ngay_tra_thuong<'%(date_from)s')
            '''%{
                 'product_id': menhgia_id,
                 'date_from': date_from,
            }
        if loai=='2_dc':
            sql = '''
                select id from tra_thuong_thucte_line where loai='2_so' and giai='dau_cuoi' and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong_thucte where ngay_tra_thuong<'%(date_from)s')
            '''%{
                 'product_id': menhgia_id,
                 'date_from': date_from,
            }
        if loai=='2_18':
            sql = '''
                select id from tra_thuong_thucte_line where loai='2_so' and giai='18_lo' and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong_thucte where ngay_tra_thuong<'%(date_from)s')
            '''%{
                 'product_id': menhgia_id,
                 'date_from': date_from,
            }
        if loai=='3_d':
            sql = '''
                select id from tra_thuong_thucte_line where loai='3_so' and giai='dau' and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong_thucte where ngay_tra_thuong<'%(date_from)s')
            '''%{
                 'product_id': menhgia_id,
                 'date_from': date_from,
            }
        if loai=='3_c':
            sql = '''
                select id from tra_thuong_thucte_line where loai='3_so' and giai='cuoi' and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong_thucte where ngay_tra_thuong<'%(date_from)s')
            '''%{
                 'product_id': menhgia_id,
                 'date_from': date_from,
            }
        if loai=='3_dc':
            sql = '''
                select id from tra_thuong_thucte_line where loai='3_so' and giai='dau_cuoi' and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong_thucte where ngay_tra_thuong<'%(date_from)s')
            '''%{
                 'product_id': menhgia_id,
                 'date_from': date_from,
            }
        if loai=='3_7':
            sql = '''
                select id from tra_thuong_thucte_line where loai='3_so' and giai='7_lo' and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong_thucte where ngay_tra_thuong<'%(date_from)s')
            '''%{
                 'product_id': menhgia_id,
                 'date_from': date_from,
            }
        if loai=='3_17':
            sql = '''
                select id from tra_thuong_thucte_line where loai='3_so' and giai='17_lo' and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong_thucte where ngay_tra_thuong<'%(date_from)s')
            '''%{
                 'product_id': menhgia_id,
                 'date_from': date_from,
            }
        if loai=='4_16':
            sql = '''
                select id from tra_thuong_thucte_line where loai='4_so' and giai='16_lo' and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong_thucte where ngay_tra_thuong<'%(date_from)s')
            '''%{
                 'product_id': menhgia_id,
                 'date_from': date_from,
            }
        self.cr.execute(sql)
        tt_tt_ids = [r[0] for r in self.cr.fetchall()]
        for tttt in tt_tt_obj.browse(self.cr, self.uid, tt_tt_ids):
            thucte += -tttt.sl_trung
            quydoi += -(tttt.slan_trung*tttt.sl_trung)
            giatri += -tttt.tong
            
        return {'thucte': thucte,'quydoi':quydoi,'giatri':giatri}
    
    def get_phaitratrongky(self,menhgia_id,loai):
        thucte = 0
        quydoi = 0
        giatri = 0
        tt_obj = self.pool.get('tra.thuong.line')
        tt_tt_obj = self.pool.get('tra.thuong.thucte.line')
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        if loai=='2_d':
            sql = '''
                select id from tra_thuong_line where loai='2_so' and giai='dau' and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong where ngay = '%(date_from)s')
            '''%{
                 'product_id': menhgia_id,
                 'date_from': date_from,
            }
        if loai=='2_c':
            sql = '''
                select id from tra_thuong_line where loai='2_so' and giai='cuoi' and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong where ngay = '%(date_from)s')
            '''%{
                 'product_id': menhgia_id,
                 'date_from': date_from,
            }
        if loai=='2_dc':
            sql = '''
                select id from tra_thuong_line where loai='2_so' and giai='dau_cuoi' and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong where ngay = '%(date_from)s')
            '''%{
                 'product_id': menhgia_id,
                 'date_from': date_from,
            }
        if loai=='2_18':
            sql = '''
                select id from tra_thuong_line where loai='2_so' and giai='18_lo' and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong where ngay = '%(date_from)s')
            '''%{
                 'product_id': menhgia_id,
                 'date_from': date_from,
            }
        if loai=='3_d':
            sql = '''
                select id from tra_thuong_line where loai='3_so' and giai='dau' and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong where ngay = '%(date_from)s')
            '''%{
                 'product_id': menhgia_id,
                 'date_from': date_from,
            }
        if loai=='3_c':
            sql = '''
                select id from tra_thuong_line where loai='3_so' and giai='cuoi' and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong where ngay = '%(date_from)s')
            '''%{
                 'product_id': menhgia_id,
                 'date_from': date_from,
            }
        if loai=='3_dc':
            sql = '''
                select id from tra_thuong_line where loai='3_so' and giai='dau_cuoi' and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong where ngay = '%(date_from)s')
            '''%{
                 'product_id': menhgia_id,
                 'date_from': date_from,
            }
        if loai=='3_7':
            sql = '''
                select id from tra_thuong_line where loai='3_so' and giai='7_lo' and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong where ngay = '%(date_from)s')
            '''%{
                 'product_id': menhgia_id,
                 'date_from': date_from,
            }
        if loai=='3_17':
            sql = '''
                select id from tra_thuong_line where loai='3_so' and giai='17_lo' and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong where ngay = '%(date_from)s')
            '''%{
                 'product_id': menhgia_id,
                 'date_from': date_from,
            }
        if loai=='4_16':
            sql = '''
                select id from tra_thuong_line where loai='4_so' and giai='16_lo' and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong where ngay = '%(date_from)s')
            '''%{
                 'product_id': menhgia_id,
                 'date_from': date_from,
            }
        self.cr.execute(sql)
        tt_ids = [r[0] for r in self.cr.fetchall()]
        for tt in tt_obj.browse(self.cr, self.uid, tt_ids):
            thucte += tt.sl_trung
            quydoi += (tt.slan_trung*tt.sl_trung)
            giatri += tt.tong
        return {'thucte': thucte,'quydoi':quydoi,'giatri':giatri}
    
    def get_datratrongky(self,menhgia_id,loai):
        thucte = 0
        quydoi = 0
        giatri = 0
        tt_obj = self.pool.get('tra.thuong.line')
        tt_tt_obj = self.pool.get('tra.thuong.thucte.line')
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        if loai=='2_d':
            sql = '''
                select id from tra_thuong_thucte_line where loai='2_so' and giai='dau' and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong_thucte where state='done' and ngay_tra_thuong = '%(date_from)s')
            '''%{
                 'product_id': menhgia_id,
                 'date_from': date_from,
            }
        if loai=='2_c':
            sql = '''
                select id from tra_thuong_thucte_line where loai='2_so' and giai='cuoi' and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong_thucte where ngay_tra_thuong = '%(date_from)s')
            '''%{
                 'product_id': menhgia_id,
                 'date_from': date_from,
            }
        if loai=='2_dc':
            sql = '''
                select id from tra_thuong_thucte_line where loai='2_so' and giai='dau_cuoi' and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong_thucte where ngay_tra_thuong = '%(date_from)s')
            '''%{
                 'product_id': menhgia_id,
                 'date_from': date_from,
            }
        if loai=='2_18':
            sql = '''
                select id from tra_thuong_thucte_line where loai='2_so' and giai='18_lo' and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong_thucte where ngay_tra_thuong = '%(date_from)s')
            '''%{
                 'product_id': menhgia_id,
                 'date_from': date_from,
            }
        if loai=='3_d':
            sql = '''
                select id from tra_thuong_thucte_line where loai='3_so' and giai='dau' and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong_thucte where ngay_tra_thuong = '%(date_from)s')
            '''%{
                 'product_id': menhgia_id,
                 'date_from': date_from,
            }
        if loai=='3_c':
            sql = '''
                select id from tra_thuong_thucte_line where loai='3_so' and giai='cuoi' and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong_thucte where ngay_tra_thuong = '%(date_from)s')
            '''%{
                 'product_id': menhgia_id,
                 'date_from': date_from,
            }
        if loai=='3_dc':
            sql = '''
                select id from tra_thuong_thucte_line where loai='3_so' and giai='dau_cuoi' and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong_thucte where ngay_tra_thuong = '%(date_from)s')
            '''%{
                 'product_id': menhgia_id,
                 'date_from': date_from,
            }
        if loai=='3_7':
            sql = '''
                select id from tra_thuong_thucte_line where loai='3_so' and giai='7_lo' and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong_thucte where ngay_tra_thuong = '%(date_from)s')
            '''%{
                 'product_id': menhgia_id,
                 'date_from': date_from,
            }
        if loai=='3_17':
            sql = '''
                select id from tra_thuong_thucte_line where loai='3_so' and giai='17_lo' and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong_thucte where ngay_tra_thuong = '%(date_from)s')
            '''%{
                 'product_id': menhgia_id,
                 'date_from': date_from,
            }
        if loai=='4_16':
            sql = '''
                select id from tra_thuong_thucte_line where loai='4_so' and giai='16_lo' and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong_thucte where ngay_tra_thuong = '%(date_from)s')
            '''%{
                 'product_id': menhgia_id,
                 'date_from': date_from,
            }
        self.cr.execute(sql)
        tt_tt_ids = [r[0] for r in self.cr.fetchall()]
        for tttt in tt_tt_obj.browse(self.cr, self.uid, tt_tt_ids):
            thucte += tttt.sl_trung
            quydoi += (tttt.slan_trung*tttt.sl_trung)
            giatri += tttt.tong
            
        return {'thucte': thucte,'quydoi':quydoi,'giatri':giatri}
    
    def get_conlaicuoiky(self,menhgia_id,loai):
        thucte = 0
        quydoi = 0
        giatri = 0
        tt_obj = self.pool.get('tra.thuong.line')
        tt_tt_obj = self.pool.get('tra.thuong.thucte.line')
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        if loai=='2_d':
            sql = '''
                select id from tra_thuong_line where loai='2_so' and giai='dau' and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong where ngay<='%(date_from)s')
            '''%{
                 'product_id': menhgia_id,
                 'date_from': date_from,
            }
        if loai=='2_c':
            sql = '''
                select id from tra_thuong_line where loai='2_so' and giai='cuoi' and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong where ngay<='%(date_from)s')
            '''%{
                 'product_id': menhgia_id,
                 'date_from': date_from,
            }
        if loai=='2_dc':
            sql = '''
                select id from tra_thuong_line where loai='2_so' and giai='dau_cuoi' and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong where ngay<='%(date_from)s')
            '''%{
                 'product_id': menhgia_id,
                 'date_from': date_from,
            }
        if loai=='2_18':
            sql = '''
                select id from tra_thuong_line where loai='2_so' and giai='18_lo' and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong where ngay<='%(date_from)s')
            '''%{
                 'product_id': menhgia_id,
                 'date_from': date_from,
            }
        if loai=='3_d':
            sql = '''
                select id from tra_thuong_line where loai='3_so' and giai='dau' and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong where ngay<='%(date_from)s')
            '''%{
                 'product_id': menhgia_id,
                 'date_from': date_from,
            }
        if loai=='3_c':
            sql = '''
                select id from tra_thuong_line where loai='3_so' and giai='cuoi' and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong where ngay<='%(date_from)s')
            '''%{
                 'product_id': menhgia_id,
                 'date_from': date_from,
            }
        if loai=='3_dc':
            sql = '''
                select id from tra_thuong_line where loai='3_so' and giai='dau_cuoi' and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong where ngay<='%(date_from)s')
            '''%{
                 'product_id': menhgia_id,
                 'date_from': date_from,
            }
        if loai=='3_7':
            sql = '''
                select id from tra_thuong_line where loai='3_so' and giai='7_lo' and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong where ngay<='%(date_from)s')
            '''%{
                 'product_id': menhgia_id,
                 'date_from': date_from,
            }
        if loai=='3_17':
            sql = '''
                select id from tra_thuong_line where loai='3_so' and giai='17_lo' and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong where ngay<='%(date_from)s')
            '''%{
                 'product_id': menhgia_id,
                 'date_from': date_from,
            }
        if loai=='4_16':
            sql = '''
                select id from tra_thuong_line where loai='4_so' and giai='16_lo' and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong where ngay<='%(date_from)s')
            '''%{
                 'product_id': menhgia_id,
                 'date_from': date_from,
            }
        self.cr.execute(sql)
        tt_ids = [r[0] for r in self.cr.fetchall()]
        for tt in tt_obj.browse(self.cr, self.uid, tt_ids):
            thucte += tt.sl_trung
            quydoi += (tt.slan_trung*tt.sl_trung)
            giatri += tt.tong
            
        if loai=='2_d':
            sql = '''
                select id from tra_thuong_thucte_line where loai='2_so' and giai='dau' and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong_thucte where state='done' and ngay_tra_thuong<='%(date_from)s')
            '''%{
                 'product_id': menhgia_id,
                 'date_from': date_from,
            }
        if loai=='2_c':
            sql = '''
                select id from tra_thuong_thucte_line where loai='2_so' and giai='cuoi' and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong_thucte where ngay_tra_thuong<='%(date_from)s')
            '''%{
                 'product_id': menhgia_id,
                 'date_from': date_from,
            }
        if loai=='2_dc':
            sql = '''
                select id from tra_thuong_thucte_line where loai='2_so' and giai='dau_cuoi' and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong_thucte where ngay_tra_thuong<='%(date_from)s')
            '''%{
                 'product_id': menhgia_id,
                 'date_from': date_from,
            }
        if loai=='2_18':
            sql = '''
                select id from tra_thuong_thucte_line where loai='2_so' and giai='18_lo' and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong_thucte where ngay_tra_thuong<='%(date_from)s')
            '''%{
                 'product_id': menhgia_id,
                 'date_from': date_from,
            }
        if loai=='3_d':
            sql = '''
                select id from tra_thuong_thucte_line where loai='3_so' and giai='dau' and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong_thucte where ngay_tra_thuong<='%(date_from)s')
            '''%{
                 'product_id': menhgia_id,
                 'date_from': date_from,
            }
        if loai=='3_c':
            sql = '''
                select id from tra_thuong_thucte_line where loai='3_so' and giai='cuoi' and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong_thucte where ngay_tra_thuong<='%(date_from)s')
            '''%{
                 'product_id': menhgia_id,
                 'date_from': date_from,
            }
        if loai=='3_dc':
            sql = '''
                select id from tra_thuong_thucte_line where loai='3_so' and giai='dau_cuoi' and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong_thucte where ngay_tra_thuong<='%(date_from)s')
            '''%{
                 'product_id': menhgia_id,
                 'date_from': date_from,
            }
        if loai=='3_7':
            sql = '''
                select id from tra_thuong_thucte_line where loai='3_so' and giai='7_lo' and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong_thucte where ngay_tra_thuong<='%(date_from)s')
            '''%{
                 'product_id': menhgia_id,
                 'date_from': date_from,
            }
        if loai=='3_17':
            sql = '''
                select id from tra_thuong_thucte_line where loai='3_so' and giai='17_lo' and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong_thucte where ngay_tra_thuong<='%(date_from)s')
            '''%{
                 'product_id': menhgia_id,
                 'date_from': date_from,
            }
        if loai=='4_16':
            sql = '''
                select id from tra_thuong_thucte_line where loai='4_so' and giai='16_lo' and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong_thucte where ngay_tra_thuong<='%(date_from)s')
            '''%{
                 'product_id': menhgia_id,
                 'date_from': date_from,
            }
        self.cr.execute(sql)
        tt_tt_ids = [r[0] for r in self.cr.fetchall()]
        for tttt in tt_tt_obj.browse(self.cr, self.uid, tt_tt_ids):
            thucte += -tttt.sl_trung
            quydoi += -(tttt.slan_trung*tttt.sl_trung)
            giatri += -tttt.tong
            
        return {'thucte': thucte,'quydoi':quydoi,'giatri':giatri}
    
    def get_congchuatradauky(self,menhgia_id):
        thucte = 0
        quydoi = 0
        giatri = 0
        tt_obj = self.pool.get('tra.thuong.line')
        tt_tt_obj = self.pool.get('tra.thuong.thucte.line')
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        sql = '''
            select id from tra_thuong_line where
                loai in ('2_so','3_so','4_so')
                and giai in ('dau','cuoi','dau_cuoi','18_lo','7_lo','17_lo','16_lo')
                and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong where ngay<'%(date_from)s')
        '''%{
             'product_id': menhgia_id,
             'date_from': date_from,
        }
        self.cr.execute(sql)
        tt_ids = [r[0] for r in self.cr.fetchall()]
        for tt in tt_obj.browse(self.cr, self.uid, tt_ids):
            thucte += tt.sl_trung
            quydoi += (tt.slan_trung*tt.sl_trung)
            giatri += tt.tong
            
        sql = '''
            select id from tra_thuong_thucte_line where
                loai in ('2_so','3_so','4_so')
                and giai in ('dau','cuoi','dau_cuoi','18_lo','7_lo','17_lo','16_lo')
                and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong_thucte where state='done' and ngay_tra_thuong<'%(date_from)s')
        '''%{
             'product_id': menhgia_id,
             'date_from': date_from,
        }
        self.cr.execute(sql)
        tt_tt_ids = [r[0] for r in self.cr.fetchall()]
        for tttt in tt_tt_obj.browse(self.cr, self.uid, tt_tt_ids):
            thucte += -tttt.sl_trung
            quydoi += -(tttt.slan_trung*tttt.sl_trung)
            giatri += -tttt.tong
            
        return {'thucte': thucte,'quydoi':quydoi,'giatri':giatri}
    
    def get_congphaitratrongky(self,menhgia_id):
        thucte = 0
        quydoi = 0
        giatri = 0
        tt_obj = self.pool.get('tra.thuong.line')
        tt_tt_obj = self.pool.get('tra.thuong.thucte.line')
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        sql = '''
            select id from tra_thuong_line where
                loai in ('2_so','3_so','4_so')
                and giai in ('dau','cuoi','dau_cuoi','18_lo','7_lo','17_lo','16_lo')
                and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong where ngay = '%(date_from)s')
        '''%{
             'product_id': menhgia_id,
             'date_from': date_from,
        }
        self.cr.execute(sql)
        tt_ids = [r[0] for r in self.cr.fetchall()]
        for tt in tt_obj.browse(self.cr, self.uid, tt_ids):
            thucte += tt.sl_trung
            quydoi += (tt.slan_trung*tt.sl_trung)
            giatri += tt.tong
        return {'thucte': thucte,'quydoi':quydoi,'giatri':giatri}
    
    def get_congdatratrongky(self,menhgia_id):
        thucte = 0
        quydoi = 0
        giatri = 0
        tt_obj = self.pool.get('tra.thuong.line')
        tt_tt_obj = self.pool.get('tra.thuong.thucte.line')
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        sql = '''
            select id from tra_thuong_thucte_line where
                loai in ('2_so','3_so','4_so')
                and giai in ('dau','cuoi','dau_cuoi','18_lo','7_lo','17_lo','16_lo')
                and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong_thucte where state='done' and ngay_tra_thuong = '%(date_from)s')
        '''%{
             'product_id': menhgia_id,
             'date_from': date_from,
        }
        self.cr.execute(sql)
        tt_tt_ids = [r[0] for r in self.cr.fetchall()]
        for tttt in tt_tt_obj.browse(self.cr, self.uid, tt_tt_ids):
            thucte += tttt.sl_trung
            quydoi += (tttt.slan_trung*tttt.sl_trung)
            giatri += tttt.tong
            
        return {'thucte': thucte,'quydoi':quydoi,'giatri':giatri}
    
    def get_congconlaicuoiky(self,menhgia_id):
        thucte = 0
        quydoi = 0
        giatri = 0
        tt_obj = self.pool.get('tra.thuong.line')
        tt_tt_obj = self.pool.get('tra.thuong.thucte.line')
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        sql = '''
            select id from tra_thuong_line where
                loai in ('2_so','3_so','4_so')
                and giai in ('dau','cuoi','dau_cuoi','18_lo','7_lo','17_lo','16_lo')
                and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong where ngay<='%(date_from)s')
        '''%{
             'product_id': menhgia_id,
             'date_from': date_from,
        }
        self.cr.execute(sql)
        tt_ids = [r[0] for r in self.cr.fetchall()]
        for tt in tt_obj.browse(self.cr, self.uid, tt_ids):
            thucte += tt.sl_trung
            quydoi += (tt.slan_trung*tt.sl_trung)
            giatri += tt.tong
            
        sql = '''
            select id from tra_thuong_thucte_line where
                loai in ('2_so','3_so','4_so')
                and giai in ('dau','cuoi','dau_cuoi','18_lo','7_lo','17_lo','16_lo')
                and product_id=%(product_id)s and trathuong_id in (select id from tra_thuong_thucte where state='done' and ngay_tra_thuong<='%(date_from)s')
        '''%{
             'product_id': menhgia_id,
             'date_from': date_from,
        }
        self.cr.execute(sql)
        tt_tt_ids = [r[0] for r in self.cr.fetchall()]
        for tttt in tt_tt_obj.browse(self.cr, self.uid, tt_tt_ids):
            thucte += -tttt.sl_trung
            quydoi += -(tttt.slan_trung*tttt.sl_trung)
            giatri += -tttt.tong
            
        return {'thucte': thucte,'quydoi':quydoi,'giatri':giatri}
    
    def get_tongcongchuatradauky(self):
        thucte = 0
        quydoi = 0
        giatri = 0
        tt_obj = self.pool.get('tra.thuong.line')
        tt_tt_obj = self.pool.get('tra.thuong.thucte.line')
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        sql = '''
            select id from tra_thuong_line where trathuong_id in (select id from tra_thuong where ngay<'%(date_from)s')
        '''%{
             'date_from': date_from,
        }
        self.cr.execute(sql)
        tt_ids = [r[0] for r in self.cr.fetchall()]
        for tt in tt_obj.browse(self.cr, self.uid, tt_ids):
            thucte += tt.sl_trung
            quydoi += (tt.slan_trung*tt.sl_trung)
            giatri += tt.tong
            
        sql = '''
            select id from tra_thuong_thucte_line where trathuong_id in (select id from tra_thuong_thucte where state='done' and ngay_tra_thuong<'%(date_from)s')
        '''%{
             'date_from': date_from,
        }
        self.cr.execute(sql)
        tt_tt_ids = [r[0] for r in self.cr.fetchall()]
        for tttt in tt_tt_obj.browse(self.cr, self.uid, tt_tt_ids):
            thucte += -tttt.sl_trung
            quydoi += -(tttt.slan_trung*tttt.sl_trung)
            giatri += -tttt.tong
            
        return {'thucte': thucte,'quydoi':quydoi,'giatri':giatri}
    
    def get_tongcongphaitratrongky(self):
        thucte = 0
        quydoi = 0
        giatri = 0
        tt_obj = self.pool.get('tra.thuong.line')
        tt_tt_obj = self.pool.get('tra.thuong.thucte.line')
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        sql = '''
            select id from tra_thuong_line where trathuong_id in (select id from tra_thuong where ngay = '%(date_from)s')
        '''%{
             'date_from': date_from,
        }
        self.cr.execute(sql)
        tt_ids = [r[0] for r in self.cr.fetchall()]
        for tt in tt_obj.browse(self.cr, self.uid, tt_ids):
            thucte += tt.sl_trung
            quydoi += (tt.slan_trung*tt.sl_trung)
            giatri += tt.tong
        return {'thucte': thucte,'quydoi':quydoi,'giatri':giatri}
    
    def get_tongcongdatratrongky(self):
        thucte = 0
        quydoi = 0
        giatri = 0
        tt_obj = self.pool.get('tra.thuong.line')
        tt_tt_obj = self.pool.get('tra.thuong.thucte.line')
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        sql = '''
            select id from tra_thuong_thucte_line where trathuong_id in (select id from tra_thuong_thucte where state='done' and ngay_tra_thuong = '%(date_from)s')
        '''%{
             'date_from': date_from,
        }
        self.cr.execute(sql)
        tt_tt_ids = [r[0] for r in self.cr.fetchall()]
        for tttt in tt_tt_obj.browse(self.cr, self.uid, tt_tt_ids):
            thucte += tttt.sl_trung
            quydoi += (tttt.slan_trung*tttt.sl_trung)
            giatri += tttt.tong
            
        return {'thucte': thucte,'quydoi':quydoi,'giatri':giatri}
    
    def get_tongcongconlaicuoiky(self):
        thucte = 0
        quydoi = 0
        giatri = 0
        tt_obj = self.pool.get('tra.thuong.line')
        tt_tt_obj = self.pool.get('tra.thuong.thucte.line')
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        sql = '''
            select id from tra_thuong_line where trathuong_id in (select id from tra_thuong where ngay<='%(date_from)s')
        '''%{
             'date_from': date_from,
        }
        self.cr.execute(sql)
        tt_ids = [r[0] for r in self.cr.fetchall()]
        for tt in tt_obj.browse(self.cr, self.uid, tt_ids):
            thucte += tt.sl_trung
            quydoi += (tt.slan_trung*tt.sl_trung)
            giatri += tt.tong
            
        sql = '''
            select id from tra_thuong_thucte_line where trathuong_id in (select id from tra_thuong_thucte where state='done' and ngay_tra_thuong<='%(date_from)s')
        '''%{
             'date_from': date_from,
        }
        self.cr.execute(sql)
        tt_tt_ids = [r[0] for r in self.cr.fetchall()]
        for tttt in tt_tt_obj.browse(self.cr, self.uid, tt_tt_ids):
            thucte += -tttt.sl_trung
            quydoi += -(tttt.slan_trung*tttt.sl_trung)
            giatri += -tttt.tong
            
        return {'thucte': thucte,'quydoi':quydoi,'giatri':giatri}
    