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
        self.sl_2_d_tong = 0,
        self.st_2_d_tong = 0,
        self.sl_2_c_tong = 0,
        self.st_2_c_tong = 0,
        self.sl_2_dc_tong = 0,
        self.st_2_dc_tong = 0,
        self.sl_2_18_tong = 0,
        self.st_2_18_tong = 0,
        
        self.sl_3_d_tong = 0,
        self.st_3_d_tong = 0,
        self.sl_3_c_tong = 0,
        self.st_3_c_tong = 0,
        self.sl_3_dc_tong = 0,
        self.st_3_dc_tong = 0,
        self.sl_3_7_tong = 0,
        self.st_3_7_tong = 0,
        self.sl_3_17_tong = 0,
        self.st_3_17_tong = 0,
        
        self.sl_4_16_tong = 0,
        self.st_4_16_tong = 0,
        
        self.sl_tong = 0,
        self.st_tong = 0,
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
        vals = {
            'sl_2_d_tong' :self.sl_2_d_tong,
            'st_2_d_tong' :self.st_2_d_tong,
            'sl_2_c_tong' :self.sl_2_c_tong,
            'st_2_c_tong' :self.st_2_c_tong,
            'sl_2_dc_tong' :self.sl_2_dc_tong,
            'st_2_dc_tong' :self.st_2_dc_tong,
            'sl_2_18_tong' :self.sl_2_18_tong,
            'st_2_18_tong' :self.st_2_18_tong,
            
            'sl_3_d_tong' :self.sl_3_d_tong,
            'st_3_d_tong' :self.st_3_d_tong,
            'sl_3_c_tong' :self.sl_3_c_tong,
            'st_3_c_tong' :self.st_3_c_tong,
            'sl_3_dc_tong' :self.sl_3_dc_tong,
            'st_3_dc_tong' :self.st_3_dc_tong,
            'sl_3_7_tong' :self.sl_3_7_tong,
            'st_3_7_tong' :self.st_3_7_tong,
            'sl_3_17_tong' :self.sl_3_17_tong,
            'st_3_17_tong' :self.st_3_17_tong,
            
            'sl_4_16_tong' :self.sl_4_16_tong,
            'st_4_16_tong' :self.st_4_16_tong,
            
            'sl_tong' :self.sl_tong,
            'st_tong' :self.st_tong,
        }
        self.sl_2_d_tong = 0,
        self.st_2_d_tong = 0,
        self.sl_2_c_tong = 0,
        self.st_2_c_tong = 0,
        self.sl_2_dc_tong = 0,
        self.st_2_dc_tong = 0,
        self.sl_2_18_tong = 0,
        self.st_2_18_tong = 0,
        
        self.sl_3_d_tong = 0,
        self.st_3_d_tong = 0,
        self.sl_3_c_tong = 0,
        self.st_3_c_tong = 0,
        self.sl_3_dc_tong = 0,
        self.st_3_dc_tong = 0,
        self.sl_3_7_tong = 0,
        self.st_3_7_tong = 0,
        self.sl_3_17_tong = 0,
        self.st_3_17_tong = 0,
        
        self.sl_4_16_tong = 0,
        self.st_4_16_tong = 0,
        
        self.sl_tong = 0,
        self.st_tong = 0,
        return [vals]
        
    def get_lines(self):
        wizard_data = self.localcontext['data']['form']
        product = wizard_data['product_id']
        date = wizard_data['date']
        res = self.get_lines_theongay(self.cr, product[0], date)
        return res
    
    def get_vietname_date(self, date):
        if not date:
            return ''
        date = datetime.strptime(date, DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    def get_date_to(self):
        wizard_data = self.localcontext['data']['form']
        date_to = wizard_data['date']
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
    
    def get_lines_theongay(self, cr, product_id, date):
        res = []
        seq = -1
        sql = '''
            select tttt.ngay as ngay_mo_so, kqxs.dai_duthuong_id as dai_duthuong
                from tra_thuong_thucte tttt
                left join ketqua_xoso kqxs on kqxs.name = tttt.ngay
                where tttt.state='done' and tttt.ngay_tra_thuong = '%s' and tttt.id in (select trathuong_id from tra_thuong_thucte_line where product_id=%s)
                group by tttt.ngay,kqxs.dai_duthuong_id
                order by tttt.ngay
        '''%(date,product_id)
        cr.execute(sql)
        for seq_tt,line in enumerate(cr.dictfetchall()):
            seq += 1
            seq_n = seq
            res.append({
                'ngay_mo_so': line['ngay_mo_so'],
                'ngay_mo_thuong': line['ngay_mo_so'],
                'dai_duthuong_id': line['dai_duthuong'],
                
                'sl_2_d': 0,
                'st_2_d': 0,
                'sl_2_c': 0,
                'st_2_c': 0,
                'sl_2_dc': 0,
                'slan_2_dc': 0,
                'st_2_dc': 0,
                'sl_2_18': 0,
                'slan_2_18': 0,
                'st_2_18': 0,
                
                'sl_3_d': 0,
                'st_3_d': 0,
                'sl_3_c': 0,
                'st_3_c': 0,
                'sl_3_dc': 0,
                'slan_3_dc': 0,
                'st_3_dc': 0,
                'sl_3_7': 0,
                'slan_3_7': 0,
                'st_3_7': 0,
                'sl_3_17': 0,
                'slan_3_17': 0,
                'st_3_17': 0,
                
                'sl_4_16': 0,
                'slan_4_16': 0,
                'st_4_16': 0,
                
                'sl_tong': 0,
                'st_tong': 0,
            })
            # 2 so
            sql = '''
                select case when sum(sl_trung)!=0 then sum(sl_trung) else 0 end sl_trung,
                    case when sum(sl_trung * slan_trung * tong_tien)!=0 then sum(sl_trung * slan_trung * tong_tien) else 0 end so_tien
                    
                    from tra_thuong_thucte_line where loai='2_so' and giai='dau' and product_id=%s
                        and trathuong_id in (select id from tra_thuong_thucte where ngay='%s' and ngay_tra_thuong = '%s' and state='done') 
            '''%(product_id, line['ngay_mo_so'], date)
            cr.execute(sql)
            loai_2_d = cr.dictfetchone()
            res[seq_n]['sl_2_d'] = loai_2_d['sl_trung']
            res[seq_n]['st_2_d'] = loai_2_d['so_tien']
            res[seq_n]['sl_tong'] += loai_2_d['sl_trung']
            res[seq_n]['st_tong'] += loai_2_d['so_tien']
            self.sl_2_d_tong += loai_2_d['sl_trung']
            self.st_2_d_tong += loai_2_d['so_tien']
            self.sl_tong += loai_2_d['sl_trung']
            self.st_tong += loai_2_d['so_tien']
            
            sql = '''
                select case when sum(sl_trung)!=0 then sum(sl_trung) else 0 end sl_trung,
                    case when sum(sl_trung * slan_trung * tong_tien)!=0 then sum(sl_trung * slan_trung * tong_tien) else 0 end so_tien
                    
                    from tra_thuong_thucte_line where loai='2_so' and giai='cuoi' and product_id=%s
                        and trathuong_id in (select id from tra_thuong_thucte where ngay='%s' and ngay_tra_thuong = '%s' and state='done') 
            '''%(product_id, line['ngay_mo_so'], date)
            cr.execute(sql)
            loai_2_c = cr.dictfetchone()
            res[seq_n]['sl_2_c'] = loai_2_c['sl_trung']
            res[seq_n]['st_2_c'] = loai_2_c['so_tien']
            res[seq_n]['sl_tong'] += loai_2_c['sl_trung']
            res[seq_n]['st_tong'] += loai_2_c['so_tien']
            self.sl_2_c_tong += loai_2_c['sl_trung']
            self.st_2_c_tong += loai_2_c['so_tien']
            self.sl_tong += loai_2_c['sl_trung']
            self.st_tong += loai_2_c['so_tien']
            
            sql = '''
                select slan_trung,case when sum(sl_trung)!=0 then sum(sl_trung) else 0 end sl_trung,
                    case when sum(sl_trung * slan_trung * tong_tien)!=0 then sum(sl_trung * slan_trung * tong_tien) else 0 end so_tien
                    
                    from tra_thuong_thucte_line where loai='2_so' and giai='dau_cuoi' and product_id=%s
                        and trathuong_id in (select id from tra_thuong_thucte where ngay='%s' and ngay_tra_thuong = '%s' and state='done') 
            '''%(product_id, line['ngay_mo_so'], date)
            cr.execute(sql)
            for s_2_dc,loai_2_dc in enumerate(cr.dictfetchall()):
                if seq_n+s_2_dc > seq and (loai_2_dc['sl_trung']!=0 or loai_2_dc['slan_trung']!=0 or loai_2_dc['so_tien']!=0):
                    seq += 1
                    res.append({
                        'ngay_mo_so': '',
                        'ngay_mo_thuong': line['ngay_mo_so'],
                        'dai_duthuong_id': '',
                        
                        'sl_2_d': 0,
                        'st_2_d': 0,
                        'sl_2_c': 0,
                        'st_2_c': 0,
                        'sl_2_dc': 0,
                        'slan_2_dc': 0,
                        'st_2_dc': 0,
                        'sl_2_18': 0,
                        'slan_2_18': 0,
                        'st_2_18': 0,
                        
                        'sl_3_d': 0,
                        'st_3_d': 0,
                        'sl_3_c': 0,
                        'st_3_c': 0,
                        'sl_3_dc': 0,
                        'slan_3_dc': 0,
                        'st_3_dc': 0,
                        'sl_3_7': 0,
                        'slan_3_7': 0,
                        'st_3_7': 0,
                        'sl_3_17': 0,
                        'slan_3_17': 0,
                        'st_3_17': 0,
                        
                        'sl_4_16': 0,
                        'slan_4_16': 0,
                        'st_4_16': 0,
                        
                        'sl_tong': 0,
                        'st_tong': 0,
                    })
                res[seq_n+s_2_dc]['sl_2_dc'] = loai_2_dc['sl_trung']
                res[seq_n+s_2_dc]['slan_2_dc'] = loai_2_dc['slan_trung']
                res[seq_n+s_2_dc]['st_2_dc'] = loai_2_dc['so_tien']
                res[seq_n+s_2_dc]['sl_tong'] += loai_2_dc['sl_trung']
                res[seq_n+s_2_dc]['st_tong'] += loai_2_dc['so_tien']
                self.sl_2_dc_tong += loai_2_dc['sl_trung']
                self.st_2_dc_tong += loai_2_dc['so_tien']
                self.sl_tong += loai_2_dc['sl_trung']
                self.st_tong += loai_2_dc['so_tien']
                
            sql = '''
                select slan_trung,case when sum(sl_trung)!=0 then sum(sl_trung) else 0 end sl_trung,
                    case when sum(sl_trung * slan_trung * tong_tien)!=0 then sum(sl_trung * slan_trung * tong_tien) else 0 end so_tien
                    
                    from tra_thuong_thucte_line where loai='2_so' and giai='18_lo' and product_id=%s
                        and trathuong_id in (select id from tra_thuong_thucte where ngay='%s' and ngay_tra_thuong = '%s' and state='done')
                        
                    group by slan_trung 
            '''%(product_id, line['ngay_mo_so'], date)
            cr.execute(sql)
            for s_2_18,loai_2_18 in enumerate(cr.dictfetchall()):
                if seq_n+s_2_18 > seq and (loai_2_18['sl_trung']!=0 or loai_2_18['slan_trung']!=0 or loai_2_18['so_tien']!=0):
                    seq += 1
                    res.append({
                        'ngay_mo_so': '',
                        'ngay_mo_thuong': line['ngay_mo_so'],
                        'dai_duthuong_id': '',
                        
                        'sl_2_d': 0,
                        'st_2_d': 0,
                        'sl_2_c': 0,
                        'st_2_c': 0,
                        'sl_2_dc': 0,
                        'slan_2_dc': 0,
                        'st_2_dc': 0,
                        'sl_2_18': 0,
                        'slan_2_18': 0,
                        'st_2_18': 0,
                        
                        'sl_3_d': 0,
                        'st_3_d': 0,
                        'sl_3_c': 0,
                        'st_3_c': 0,
                        'sl_3_dc': 0,
                        'slan_3_dc': 0,
                        'st_3_dc': 0,
                        'sl_3_7': 0,
                        'slan_3_7': 0,
                        'st_3_7': 0,
                        'sl_3_17': 0,
                        'slan_3_17': 0,
                        'st_3_17': 0,
                        
                        'sl_4_16': 0,
                        'slan_4_16': 0,
                        'st_4_16': 0,
                        
                        'sl_tong': 0,
                        'st_tong': 0,
                    })
                res[seq_n+s_2_18]['sl_2_18'] = loai_2_18['sl_trung']
                res[seq_n+s_2_18]['slan_2_18'] = loai_2_18['slan_trung']
                res[seq_n+s_2_18]['st_2_18'] = loai_2_18['so_tien']
                res[seq_n+s_2_18]['sl_tong'] += loai_2_18['sl_trung']
                res[seq_n+s_2_18]['st_tong'] += loai_2_18['so_tien']
                self.sl_2_18_tong += loai_2_18['sl_trung']
                self.st_2_18_tong += loai_2_18['so_tien']
                self.sl_tong += loai_2_18['sl_trung']
                self.st_tong += loai_2_18['so_tien']
            
            # 3 so
            sql = '''
                select case when sum(sl_trung)!=0 then sum(sl_trung) else 0 end sl_trung,
                    case when sum(sl_trung * slan_trung * tong_tien)!=0 then sum(sl_trung * slan_trung * tong_tien) else 0 end so_tien
                    
                    from tra_thuong_thucte_line where loai='3_so' and giai='dau' and product_id=%s
                        and trathuong_id in (select id from tra_thuong_thucte where ngay='%s' and ngay_tra_thuong = '%s' and state='done') 
            '''%(product_id, line['ngay_mo_so'], date)
            cr.execute(sql)
            loai_3_d = cr.dictfetchone()
            res[seq_n]['sl_3_d'] = loai_3_d['sl_trung']
            res[seq_n]['st_3_d'] = loai_3_d['so_tien']
            res[seq_n]['sl_tong'] += loai_3_d['sl_trung']
            res[seq_n]['st_tong'] += loai_3_d['so_tien']
            self.sl_3_d_tong += loai_3_d['sl_trung']
            self.st_3_d_tong += loai_3_d['so_tien']
            self.sl_tong += loai_3_d['sl_trung']
            self.st_tong += loai_3_d['so_tien']
            
            sql = '''
                select case when sum(sl_trung)!=0 then sum(sl_trung) else 0 end sl_trung,
                    case when sum(sl_trung * slan_trung * tong_tien)!=0 then sum(sl_trung * slan_trung * tong_tien) else 0 end so_tien
                    
                    from tra_thuong_thucte_line where loai='3_so' and giai='cuoi' and product_id=%s
                        and trathuong_id in (select id from tra_thuong_thucte where ngay='%s' and ngay_tra_thuong = '%s' and state='done') 
            '''%(product_id, line['ngay_mo_so'], date)
            cr.execute(sql)
            loai_3_c = cr.dictfetchone()
            res[seq_n]['sl_3_c'] = loai_3_c['sl_trung']
            res[seq_n]['st_3_c'] = loai_3_c['so_tien']
            res[seq_n]['sl_tong'] += loai_3_c['sl_trung']
            res[seq_n]['st_tong'] += loai_3_c['so_tien']
            self.sl_3_c_tong += loai_3_c['sl_trung']
            self.st_3_c_tong += loai_3_c['so_tien']
            self.sl_tong += loai_3_c['sl_trung']
            self.st_tong += loai_3_c['so_tien']
            
            sql = '''
                select slan_trung,case when sum(sl_trung)!=0 then sum(sl_trung) else 0 end sl_trung,
                    case when sum(sl_trung * slan_trung * tong_tien)!=0 then sum(sl_trung * slan_trung * tong_tien) else 0 end so_tien
                    
                    from tra_thuong_thucte_line where loai='3_so' and giai='dau_cuoi' and product_id=%s
                        and trathuong_id in (select id from tra_thuong_thucte where ngay='%s' and ngay_tra_thuong = '%s' and state='done')
                    
                    group by slan_trung 
            '''%(product_id, line['ngay_mo_so'], date)
            cr.execute(sql)
            for s_3_dc,loai_3_dc in enumerate(cr.dictfetchall()):
                if seq_n+s_3_dc > seq and (loai_3_dc['sl_trung']!=0 or loai_3_dc['slan_trung']!=0 or loai_3_dc['so_tien']!=0):
                    seq += 1
                    res.append({
                        'ngay_mo_so': '',
                        'ngay_mo_thuong': line['ngay_mo_so'],
                        'dai_duthuong_id': '',
                        
                        'sl_2_d': 0,
                        'st_2_d': 0,
                        'sl_2_c': 0,
                        'st_2_c': 0,
                        'sl_2_dc': 0,
                        'slan_2_dc': 0,
                        'st_2_dc': 0,
                        'sl_2_18': 0,
                        'slan_2_18': 0,
                        'st_2_18': 0,
                        
                        'sl_3_d': 0,
                        'st_3_d': 0,
                        'sl_3_c': 0,
                        'st_3_c': 0,
                        'sl_3_dc': 0,
                        'slan_3_dc': 0,
                        'st_3_dc': 0,
                        'sl_3_7': 0,
                        'slan_3_7': 0,
                        'st_3_7': 0,
                        'sl_3_17': 0,
                        'slan_3_17': 0,
                        'st_3_17': 0,
                        
                        'sl_4_16': 0,
                        'slan_4_16': 0,
                        'st_4_16': 0,
                        
                        'sl_tong': 0,
                        'st_tong': 0,
                    })
                res[seq_n+s_3_dc]['sl_3_dc'] = loai_3_dc['sl_trung']
                res[seq_n+s_3_dc]['slan_3_dc'] = loai_3_dc['slan_trung']
                res[seq_n+s_3_dc]['st_3_dc'] = loai_3_dc['so_tien']
                res[seq_n+s_3_dc]['sl_tong'] += loai_3_dc['sl_trung']
                res[seq_n+s_3_dc]['st_tong'] += loai_3_dc['so_tien']
                self.sl_3_dc_tong += loai_3_dc['sl_trung']
                self.st_3_dc_tong += loai_3_dc['so_tien']
                self.sl_tong += loai_3_dc['sl_trung']
                self.st_tong += loai_3_dc['so_tien']
                
            sql = '''
                select slan_trung,case when sum(sl_trung)!=0 then sum(sl_trung) else 0 end sl_trung,
                    case when sum(sl_trung * slan_trung * tong_tien)!=0 then sum(sl_trung * slan_trung * tong_tien) else 0 end so_tien
                    
                    from tra_thuong_thucte_line where loai='3_so' and giai='7_lo' and product_id=%s
                        and trathuong_id in (select id from tra_thuong_thucte where ngay='%s' and ngay_tra_thuong = '%s' and state='done')
                        
                    group by slan_trung  
            '''%(product_id, line['ngay_mo_so'], date)
            cr.execute(sql)
            for s_3_7,loai_3_7 in enumerate(cr.dictfetchall()):
                if seq_n+s_3_7 > seq and (loai_3_7['sl_trung']!=0 or loai_3_7['slan_trung']!=0 or loai_3_7['so_tien']!=0):
                    seq += 1
                    res.append({
                        'ngay_mo_so': '',
                        'ngay_mo_thuong': line['ngay_mo_so'],
                        'dai_duthuong_id': '',
                        
                        'sl_2_d': 0,
                        'st_2_d': 0,
                        'sl_2_c': 0,
                        'st_2_c': 0,
                        'sl_2_dc': 0,
                        'slan_2_dc': 0,
                        'st_2_dc': 0,
                        'sl_2_18': 0,
                        'slan_2_18': 0,
                        'st_2_18': 0,
                        
                        'sl_3_d': 0,
                        'st_3_d': 0,
                        'sl_3_c': 0,
                        'st_3_c': 0,
                        'sl_3_dc': 0,
                        'slan_3_dc': 0,
                        'st_3_dc': 0,
                        'sl_3_7': 0,
                        'slan_3_7': 0,
                        'st_3_7': 0,
                        'sl_3_17': 0,
                        'slan_3_17': 0,
                        'st_3_17': 0,
                        
                        'sl_4_16': 0,
                        'slan_4_16': 0,
                        'st_4_16': 0,
                        
                        'sl_tong': 0,
                        'st_tong': 0,
                    })
                res[seq_n+s_3_7]['sl_3_7'] = loai_3_7['sl_trung']
                res[seq_n+s_3_7]['slan_3_7'] = loai_3_7['slan_trung']
                res[seq_n+s_3_7]['st_3_7'] = loai_3_7['so_tien']
                res[seq_n+s_3_7]['sl_tong'] += loai_3_7['sl_trung']
                res[seq_n+s_3_7]['st_tong'] += loai_3_7['so_tien']
                self.sl_3_7_tong += loai_3_7['sl_trung']
                self.st_3_7_tong += loai_3_7['so_tien']
                self.sl_tong += loai_3_7['sl_trung']
                self.st_tong += loai_3_7['so_tien']
                
            sql = '''
                select slan_trung,case when sum(sl_trung)!=0 then sum(sl_trung) else 0 end sl_trung,
                    case when sum(sl_trung * slan_trung * tong_tien)!=0 then sum(sl_trung * slan_trung * tong_tien) else 0 end so_tien
                    
                    from tra_thuong_thucte_line where loai='3_so' and giai='17_lo' and product_id=%s
                        and trathuong_id in (select id from tra_thuong_thucte where ngay='%s' and ngay_tra_thuong = '%s' and state='done')
                        
                     group by slan_trung
            '''%(product_id, line['ngay_mo_so'], date)
            cr.execute(sql)
            for s_3_17,loai_3_17 in enumerate(cr.dictfetchall()):
                if seq_n+s_3_17 > seq and (loai_3_17['sl_trung']!=0 or loai_3_17['slan_trung']!=0 or loai_3_17['so_tien']!=0):
                    seq += 1
                    res.append({
                        'ngay_mo_so': '',
                        'ngay_mo_thuong': line['ngay_mo_so'],
                        'dai_duthuong_id': '',
                        
                        'sl_2_d': 0,
                        'st_2_d': 0,
                        'sl_2_c': 0,
                        'st_2_c': 0,
                        'sl_2_dc': 0,
                        'slan_2_dc': 0,
                        'st_2_dc': 0,
                        'sl_2_18': 0,
                        'slan_2_18': 0,
                        'st_2_18': 0,
                        
                        'sl_3_d': 0,
                        'st_3_d': 0,
                        'sl_3_c': 0,
                        'st_3_c': 0,
                        'sl_3_dc': 0,
                        'slan_3_dc': 0,
                        'st_3_dc': 0,
                        'sl_3_7': 0,
                        'slan_3_7': 0,
                        'st_3_7': 0,
                        'sl_3_17': 0,
                        'slan_3_17': 0,
                        'st_3_17': 0,
                        
                        'sl_4_16': 0,
                        'slan_4_16': 0,
                        'st_4_16': 0,
                        
                        'sl_tong': 0,
                        'st_tong': 0,
                    })
                res[seq_n+s_3_17]['sl_3_17'] = loai_3_17['sl_trung']
                res[seq_n+s_3_17]['slan_3_17'] = loai_3_17['slan_trung']
                res[seq_n+s_3_17]['st_3_17'] = loai_3_17['so_tien']
                res[seq_n+s_3_17]['sl_tong'] += loai_3_17['sl_trung']
                res[seq_n+s_3_17]['st_tong'] += loai_3_17['so_tien']
                self.sl_3_17_tong += loai_3_17['sl_trung']
                self.st_3_17_tong += loai_3_17['so_tien']
                self.sl_tong += loai_3_17['sl_trung']
                self.st_tong += loai_3_17['so_tien']
                
            #4 so
            sql = '''
                select slan_trung,case when sum(sl_trung)!=0 then sum(sl_trung) else 0 end sl_trung,
                    case when sum(sl_trung * slan_trung * tong_tien)!=0 then sum(sl_trung * slan_trung * tong_tien) else 0 end so_tien
                    
                    from tra_thuong_thucte_line where loai='4_so' and giai='16_lo' and product_id=%s
                        and trathuong_id in (select id from tra_thuong_thucte where ngay='%s' and ngay_tra_thuong = '%s' and state='done')
                        
                    group by slan_trung 
            '''%(product_id, line['ngay_mo_so'], date)
            cr.execute(sql)
            for s_4_16,loai_4_16 in enumerate(cr.dictfetchall()):
                if seq_n+s_4_16 > seq and (loai_4_16['sl_trung']!=0 or loai_4_16['slan_trung']!=0 or loai_4_16['so_tien']!=0):
                    seq += 1
                    res.append({
                        'ngay_mo_so': '',
                        'ngay_mo_thuong': line['ngay_mo_so'],
                        'dai_duthuong_id': '',
                        
                        'sl_2_d': 0,
                        'st_2_d': 0,
                        'sl_2_c': 0,
                        'st_2_c': 0,
                        'sl_2_dc': 0,
                        'slan_2_dc': 0,
                        'st_2_dc': 0,
                        'sl_2_18': 0,
                        'slan_2_18': 0,
                        'st_2_18': 0,
                        
                        'sl_3_d': 0,
                        'st_3_d': 0,
                        'sl_3_c': 0,
                        'st_3_c': 0,
                        'sl_3_dc': 0,
                        'slan_3_dc': 0,
                        'st_3_dc': 0,
                        'sl_3_7': 0,
                        'slan_3_7': 0,
                        'st_3_7': 0,
                        'sl_3_17': 0,
                        'slan_3_17': 0,
                        'st_3_17': 0,
                        
                        'sl_4_16': 0,
                        'slan_4_16': 0,
                        'st_4_16': 0,
                        
                        'sl_tong': 0,
                        'st_tong': 0,
                    })
                res[seq_n+s_4_16]['sl_4_16'] = loai_4_16['sl_trung']
                res[seq_n+s_4_16]['slan_4_16'] = loai_4_16['slan_trung']
                res[seq_n+s_4_16]['st_4_16'] = loai_4_16['so_tien']
                res[seq_n+s_4_16]['sl_tong'] += loai_4_16['sl_trung']
                res[seq_n+s_4_16]['st_tong'] += loai_4_16['so_tien']
                self.sl_4_16_tong += loai_4_16['sl_trung']
                self.st_4_16_tong += loai_4_16['so_tien']
                self.sl_tong += loai_4_16['sl_trung']
                self.st_tong += loai_4_16['so_tien']
                
        return res
    