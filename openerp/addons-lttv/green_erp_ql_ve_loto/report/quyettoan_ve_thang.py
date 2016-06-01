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
from green_erp_ql_ve_loto.report import amount_to_text_vn
import random
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp.addons.green_erp_ql_ve_loto.report import amount_to_text_vn

class Parser(report_sxw.rml_parse):
        
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        pool = pooler.get_pool(self.cr.dbname)
        self.localcontext.update({
            'get_vietname_date': self.get_vietname_date,
            'convert': self.convert,
            'get_gt_menhgia': self.get_gt_menhgia,
            'get_lines': self.get_lines,
            'get_date_to': self.get_date_to,
            'get_name_menhgia': self.get_name_menhgia,
            'get_line_tong': self.get_line_tong,
            'get_ddt_name': self.get_ddt_name,
        })
        
    def get_ddt_name(self, dai_duthuong_id):
        dai_duthuong = self.pool.get('dai.duthuong').browse(self.cr, self.uid, dai_duthuong_id)
        return dai_duthuong.name
        
    def get_line_tong(self):
        wizard_data = self.localcontext['data']['form']
        product = wizard_data['product_id']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        sql = '''
            select 
                    case when sum(sl_2_d_tong)!=0 then sum(sl_2_d_tong) else 0 end sl_2_d_tong,
                    case when sum(sl_2_c_tong)!=0 then sum(sl_2_c_tong) else 0 end sl_2_c_tong,
                    case when sum(sl_2_dc_tong)!=0 then sum(sl_2_dc_tong) else 0 end sl_2_dc_tong,
                    case when sum(sl_2_18_tong)!=0 then sum(sl_2_18_tong) else 0 end sl_2_18_tong,
                    
                    case when sum(sl_3_d_tong)!=0 then sum(sl_3_d_tong) else 0 end sl_3_d_tong,
                    case when sum(sl_3_c_tong)!=0 then sum(sl_3_c_tong) else 0 end sl_3_c_tong,
                    case when sum(sl_3_dc_tong)!=0 then sum(sl_3_dc_tong) else 0 end sl_3_dc_tong,
                    case when sum(sl_3_7_tong)!=0 then sum(sl_3_7_tong) else 0 end sl_3_7_tong,
                    case when sum(sl_3_17_tong)!=0 then sum(sl_3_17_tong) else 0 end sl_3_17_tong,
                    
                    case when sum(sl_4_16_tong)!=0 then sum(sl_4_16_tong) else 0 end sl_4_16_tong,
                    
                    case when sum(st_2_d_tong)!=0 then sum(st_2_d_tong) else 0 end st_2_d_tong,
                    case when sum(st_2_c_tong)!=0 then sum(st_2_c_tong) else 0 end st_2_c_tong,
                    case when sum(st_2_dc_tong)!=0 then sum(st_2_dc_tong) else 0 end st_2_dc_tong,
                    case when sum(st_2_18_tong)!=0 then sum(st_2_18_tong) else 0 end st_2_18_tong,
                    
                    case when sum(st_3_d_tong)!=0 then sum(st_3_d_tong) else 0 end st_3_d_tong,
                    case when sum(st_3_c_tong)!=0 then sum(st_3_c_tong) else 0 end st_3_c_tong,
                    case when sum(st_3_dc_tong)!=0 then sum(st_3_dc_tong) else 0 end st_3_dc_tong,
                    case when sum(st_3_7_tong)!=0 then sum(st_3_7_tong) else 0 end st_3_7_tong,
                    case when sum(st_3_17_tong)!=0 then sum(st_3_17_tong) else 0 end st_3_17_tong,
                
                    case when sum(st_4_16_tong)!=0 then sum(st_4_16_tong) else 0 end st_4_16_tong,
                    
                    case when sum(sl_tong)!=0 then sum(sl_tong) else 0 end sl_tong,
                    case when sum(st_tong)!=0 then sum(st_tong) else 0 end st_tong
            
                from quyet_toan_ve_ngay
                
                where date_to between '%s' and '%s' and product_id=%s
                
        '''%(date_from,date_to,product[0])
        self.cr.execute(sql)
        return self.cr.dictfetchall()
        
    def get_lines_old(self):
        wizard_data = self.localcontext['data']['form']
        product = wizard_data['product_id']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        sql = '''
            select dai_duthuong_id,slan_2_dc, slan_2_18, slan_3_dc, slan_3_7, slan_3_17, slan_4_16,
                    case when sum(sl_2_d)!=0 then sum(sl_2_d) else 0 end sl_2_d,
                    case when sum(sl_2_c)!=0 then sum(sl_2_c) else 0 end sl_2_c,
                    case when sum(sl_2_dc)!=0 then sum(sl_2_dc) else 0 end sl_2_dc,
                    case when sum(sl_2_18)!=0 then sum(sl_2_18) else 0 end sl_2_18,
                    
                    case when sum(sl_3_d)!=0 then sum(sl_3_d) else 0 end sl_3_d,
                    case when sum(sl_3_c)!=0 then sum(sl_3_c) else 0 end sl_3_c,
                    case when sum(sl_3_dc)!=0 then sum(sl_3_dc) else 0 end sl_3_dc,
                    case when sum(sl_3_7)!=0 then sum(sl_3_7) else 0 end sl_3_7,
                    case when sum(sl_3_17)!=0 then sum(sl_3_17) else 0 end sl_3_17,
                    
                    case when sum(sl_4_16)!=0 then sum(sl_4_16) else 0 end sl_4_16,
                    
                    case when sum(st_2_d)!=0 then sum(st_2_d) else 0 end st_2_d,
                    case when sum(st_2_c)!=0 then sum(st_2_c) else 0 end st_2_c,
                    case when sum(st_2_dc)!=0 then sum(st_2_dc) else 0 end st_2_dc,
                    case when sum(st_2_18)!=0 then sum(st_2_18) else 0 end st_2_18,
                    
                    case when sum(st_3_d)!=0 then sum(st_3_d) else 0 end st_3_d,
                    case when sum(st_3_c)!=0 then sum(st_3_c) else 0 end st_3_c,
                    case when sum(st_3_dc)!=0 then sum(st_3_dc) else 0 end st_3_dc,
                    case when sum(st_3_7)!=0 then sum(st_3_7) else 0 end st_3_7,
                    case when sum(st_3_17)!=0 then sum(st_3_17) else 0 end st_3_17,
                
                    case when sum(st_4_16)!=0 then sum(st_4_16) else 0 end st_4_16,
                    
                    case when sum(sl_tong)!=0 then sum(sl_tong) else 0 end sl_tong,
                    case when sum(st_tong)!=0 then sum(st_tong) else 0 end st_tong
            
                from quyet_toan_ve_ngay_line
                
                where quyettoan_id in (select id from quyet_toan_ve_ngay where date_to between '%s' and '%s' and product_id=%s)
                
                group by dai_duthuong_id,slan_2_dc, slan_2_18, slan_3_dc, slan_3_7, slan_3_17, slan_4_16
        '''%(date_from,date_to,product[0])
        self.cr.execute(sql)
        return self.cr.dictfetchall()
    
    def get_lines(self):
        wizard_data = self.localcontext['data']['form']
        product = wizard_data['product_id']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        res = []
        seq = -1
        sql = '''
            select qtvl.ngay_mo_thuong as ngay_mo_so, kqxs.dai_duthuong_id as dai_duthuong
                from quyet_toan_ve_ngay_line qtvl
                left join ketqua_xoso kqxs on kqxs.name = qtvl.ngay_mo_thuong
                where qtvl.quyettoan_id in (select id from quyet_toan_ve_ngay where date_to between '%s' and '%s' and product_id=%s)
                group by qtvl.ngay,kqxs.dai_duthuong_id
                order by qtvl.ngay
        '''%(date_from,date_to,product[0])
        self.cr.execute(sql)
        for seq_tt,line in enumerate(self.cr.dictfetchall()):
            seq += 1
            seq_n = seq
            res.append({
                'ngay_mo_so': line['ngay_mo_so'],
                'dai_duthuong_id': line['dai_duthuong'],
            })
            # 2 so
            sql = '''
                select case when sum(sl_2_d)!=0 then sum(sl_2_d) else 0 end sl_trung,
                        case when sum(st_2_d)!=0 then sum(st_2_d) else 0 end so_tien
                    from quyet_toan_ve_ngay_line
                    where ngay_mo_thuong='%s' and quyettoan_id in (select id from quyet_toan_ve_ngay where date_to between '%s' and '%s' and product_id=%s)
            '''%(line['ngay_mo_so'], date_from,date_to,product[0])
            self.cr.execute(sql)
            loai_2_d = self.cr.dictfetchone()
            res[seq_n]['sl_2_d'] = loai_2_d['sl_trung']
            res[seq_n]['st_2_d'] = loai_2_d['so_tien']
            
            sql = '''
                select case when sum(sl_2_c)!=0 then sum(sl_2_c) else 0 end sl_trung,
                        case when sum(st_2_c)!=0 then sum(st_2_c) else 0 end so_tien
                    from quyet_toan_ve_ngay_line
                    where ngay_mo_thuong='%s' and quyettoan_id in (select id from quyet_toan_ve_ngay where date_to between '%s' and '%s' and product_id=%s)
            '''%(line['ngay_mo_so'], date_from,date_to,product[0])
            self.cr.execute(sql)
            loai_2_c = self.cr.dictfetchone()
            res[seq_n]['sl_2_c'] = loai_2_c['sl_trung']
            res[seq_n]['st_2_c'] = loai_2_c['so_tien']
            
            sql = '''
                select slan_2_dc as slan_trung,
                        case when sum(sl_2_dc)!=0 then sum(sl_2_dc) else 0 end sl_trung,
                        case when sum(st_2_dc)!=0 then sum(st_2_dc) else 0 end end so_tien
                    
                    from quyet_toan_ve_ngay_line
                    where ngay_mo_thuong='%s' and quyettoan_id in (select id from quyet_toan_ve_ngay where date_to between '%s' and '%s' and product_id=%s)
                    
                    group by slan_2_dc 
            '''%(line['ngay_mo_so'], date_from,date_to,product[0])
            self.cr.execute(sql)
            for s_2_dc,loai_2_dc in enumerate(self.cr.dictfetchall()):
                if seq_n+s_2_dc > seq and (loai_2_dc['sl_trung']!=0 or loai_2_dc['slan_trung']!=0 or loai_2_dc['so_tien']!=0):
                    seq += 1
                    res.append({
                        'ngay_mo_so': False,
                        'dai_duthuong_id': False,
                    })
                res[seq_n+s_2_dc]['sl_2_dc'] = loai_2_dc['sl_trung']
                res[seq_n+s_2_dc]['slan_2_dc'] = loai_2_dc['slan_trung']
                res[seq_n+s_2_dc]['st_2_dc'] = loai_2_dc['so_tien']
                
            sql = '''
                select slan_2_18 as slan_trung,
                        case when sum(sl_2_18)!=0 then sum(sl_2_18) else 0 end sl_trung,
                        case when sum(st_2_18)!=0 then sum(st_2_18) else 0 end end so_tien
                    
                    from quyet_toan_ve_ngay_line
                    where ngay_mo_thuong='%s' and quyettoan_id in (select id from quyet_toan_ve_ngay where date_to between '%s' and '%s' and product_id=%s)
                    
                    group by slan_2_18  
            '''%(line['ngay_mo_so'], date_from,date_to,product[0])
            self.cr.execute(sql)
            for s_2_18,loai_2_18 in enumerate(self.cr.dictfetchall()):
                if seq_n+s_2_18 > seq and (loai_2_18['sl_trung']!=0 or loai_2_18['slan_trung']!=0 or loai_2_18['so_tien']!=0):
                    seq += 1
                    res.append({
                        'ngay_mo_so': False,
                        'dai_duthuong_id': False,
                    })
                res[seq_n+s_2_18]['sl_2_18'] = loai_2_18['sl_trung']
                res[seq_n+s_2_18]['slan_2_18'] = loai_2_18['slan_trung']
                res[seq_n+s_2_18]['st_2_18'] = loai_2_18['so_tien']
            
            # 3 so
            sql = '''
                select case when sum(sl_3_d)!=0 then sum(sl_3_d) else 0 end sl_trung,
                        case when sum(st_3_d)!=0 then sum(st_3_d) else 0 end so_tien
                    from quyet_toan_ve_ngay_line
                    where ngay_mo_thuong='%s' and quyettoan_id in (select id from quyet_toan_ve_ngay where date_to between '%s' and '%s' and product_id=%s)
            '''%(line['ngay_mo_so'], date_from,date_to,product[0])
            self.cr.execute(sql)
            loai_3_d = self.cr.dictfetchone()
            res[seq_n]['sl_3_d'] = loai_3_d['sl_trung']
            res[seq_n]['st_3_d'] = loai_3_d['so_tien']
            
            sql = '''
                select case when sum(sl_3_c)!=0 then sum(sl_3_c) else 0 end sl_trung,
                        case when sum(st_3_c)!=0 then sum(st_3_c) else 0 end so_tien
                    from quyet_toan_ve_ngay_line
                    where ngay_mo_thuong='%s' and quyettoan_id in (select id from quyet_toan_ve_ngay where date_to between '%s' and '%s' and product_id=%s)
            '''%(line['ngay_mo_so'], date_from,date_to,product[0])
            self.cr.execute(sql)
            loai_3_c = self.cr.dictfetchone()
            res[seq_n]['sl_3_c'] = loai_3_c['sl_trung']
            res[seq_n]['st_3_c'] = loai_3_c['so_tien']
            
            sql = '''
                select slan_3_dc as slan_trung,
                        case when sum(sl_3_dc)!=0 then sum(sl_3_dc) else 0 end sl_trung,
                        case when sum(st_3_dc)!=0 then sum(st_3_dc) else 0 end end so_tien
                    
                    from quyet_toan_ve_ngay_line
                    where ngay_mo_thuong='%s' and quyettoan_id in (select id from quyet_toan_ve_ngay where date_to between '%s' and '%s' and product_id=%s)
                    
                    group by slan_3_dc 
            '''%(line['ngay_mo_so'], date_from,date_to,product[0])
            self.cr.execute(sql)
            for s_3_dc,loai_3_dc in enumerate(self.cr.dictfetchall()):
                if seq_n+s_3_dc > seq and (loai_3_dc['sl_trung']!=0 or loai_3_dc['slan_trung']!=0 or loai_3_dc['so_tien']!=0):
                    seq += 1
                    res.append({
                        'ngay_mo_so': False,
                        'dai_duthuong_id': False,
                    })
                res[seq_n+s_3_dc]['sl_3_dc'] = loai_3_dc['sl_trung']
                res[seq_n+s_3_dc]['slan_3_dc'] = loai_3_dc['slan_trung']
                res[seq_n+s_3_dc]['st_3_dc'] = loai_3_dc['so_tien']
                
            sql = '''
                select slan_3_7 as slan_trung,
                        case when sum(sl_3_7)!=0 then sum(sl_3_7) else 0 end sl_trung,
                        case when sum(st_3_7)!=0 then sum(st_3_7) else 0 end end so_tien
                    
                    from quyet_toan_ve_ngay_line
                    where ngay_mo_thuong='%s' and quyettoan_id in (select id from quyet_toan_ve_ngay where date_to between '%s' and '%s' and product_id=%s)
                    
                    group by slan_3_7 
            '''%(line['ngay_mo_so'], date_from,date_to,product[0])
            self.cr.execute(sql)
            for s_3_7,loai_3_7 in enumerate(self.cr.dictfetchall()):
                if seq_n+s_3_7 > seq and (loai_3_7['sl_trung']!=0 or loai_3_7['slan_trung']!=0 or loai_3_7['so_tien']!=0):
                    seq += 1
                    res.append({
                        'ngay_mo_so': False,
                        'dai_duthuong_id': False,
                    })
                res[seq_n+s_3_7]['sl_3_7'] = loai_3_7['sl_trung']
                res[seq_n+s_3_7]['slan_3_7'] = loai_3_7['slan_trung']
                res[seq_n+s_3_7]['st_3_7'] = loai_3_7['so_tien']
                
            sql = '''
                select slan_3_17 as slan_trung,
                        case when sum(sl_3_17)!=0 then sum(sl_3_17) else 0 end sl_trung,
                        case when sum(st_3_17)!=0 then sum(st_3_17) else 0 end end so_tien
                    
                    from quyet_toan_ve_ngay_line
                    where ngay_mo_thuong='%s' and quyettoan_id in (select id from quyet_toan_ve_ngay where date_to between '%s' and '%s' and product_id=%s)
                    
                    group by slan_3_17 
            '''%(line['ngay_mo_so'], date_from,date_to,product[0])
            self.cr.execute(sql)
            for s_3_17,loai_3_17 in enumerate(self.cr.dictfetchall()):
                if seq_n+s_3_17 > seq and (loai_3_17['sl_trung']!=0 or loai_3_17['slan_trung']!=0 or loai_3_17['so_tien']!=0):
                    seq += 1
                    res.append({
                        'ngay_mo_so': False,
                        'dai_duthuong_id': False,
                    })
                res[seq_n+s_3_17]['sl_3_17'] = loai_3_17['sl_trung']
                res[seq_n+s_3_17]['slan_3_17'] = loai_3_17['slan_trung']
                res[seq_n+s_3_17]['st_3_17'] = loai_3_17['so_tien']
                
            #4 so
            sql = '''
                select slan_4_16 as slan_trung,
                        case when sum(sl_4_16)!=0 then sum(sl_4_16) else 0 end sl_trung,
                        case when sum(st_4_16)!=0 then sum(st_4_16) else 0 end end so_tien
                    
                    from quyet_toan_ve_ngay_line
                    where ngay_mo_thuong='%s' and quyettoan_id in (select id from quyet_toan_ve_ngay where date_to between '%s' and '%s' and product_id=%s)
                    
                    group by slan_4_16 
            '''%(line['ngay_mo_so'], date_from,date_to,product[0])
            self.cr.execute(sql)
            for s_4_16,loai_4_16 in enumerate(self.cr.dictfetchall()):
                if seq_n+s_4_16 > seq and (loai_4_16['sl_trung']!=0 or loai_4_16['slan_trung']!=0 or loai_4_16['so_tien']!=0):
                    seq += 1
                    res.append({
                        'ngay_mo_so': False,
                        'dai_duthuong_id': False,
                    })
                res[seq_n+s_4_16]['sl_4_16'] = loai_4_16['sl_trung']
                res[seq_n+s_4_16]['slan_4_16'] = loai_4_16['slan_trung']
                res[seq_n+s_4_16]['st_4_16'] = loai_4_16['so_tien']
                
        return res
    
    def get_vietname_date(self, date):
        if not date:
            return ''
        date = datetime.strptime(date, DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    def get_date_to(self):
        wizard_data = self.localcontext['data']['form']
        date_to = wizard_data['date_to']
        return date_to
    
    def get_name_menhgia(self):
        wizard_data = self.localcontext['data']['form']
        product = wizard_data['product_id']
        menhgia = self.pool.get('product.product').browse(self.cr, self.uid, product[0])
        return menhgia.name
    
    def convert(self, amount):
        amount_text = amount_to_text_vn.amount_to_text(amount, 'vn')
        if amount_text and len(amount_text)>1:
            amount = amount_text[1:]
            head = amount_text[:1]
            amount_text = head.upper()+amount
        return amount_text
    
    def get_gt_menhgia(self):
        wizard_data = self.localcontext['data']['form']
        product = wizard_data['product_id']
        menhgia = self.pool.get('product.product').browse(self.cr, self.uid, product[0])
        return int(menhgia.list_price)/10000
    