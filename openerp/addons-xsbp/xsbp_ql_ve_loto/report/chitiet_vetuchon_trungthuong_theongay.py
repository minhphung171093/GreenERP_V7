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
            'get_date':self.get_date,
            'get_menh_gia':self.get_menh_gia,
            'get_tongve':self.get_tongve,
            'get_tongve_all':self.get_tongve_all,
            'get_so_phieu':self.get_so_phieu,
        })
    def get_date(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['date'], DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    def get_menh_gia(self):
        menhgia_obj = self.pool.get('product.product')
        menh_gia_ids = menhgia_obj.search(self.cr, self.uid, [('menh_gia','=',True)])
        return menhgia_obj.browse(self.cr, self.uid, menh_gia_ids) 
    def get_so_phieu(self):
        wizard_data = self.localcontext['data']['form']
        date = wizard_data['date']
        ve_loto_obj = self.pool.get('ve.loto')
        ve_loto_ids = ve_loto_obj.search(self.cr, self.uid, [('ngay','=',date),])
        return ve_loto_obj.browse(self.cr, self.uid, ve_loto_ids)
    def get_tongve(self,soph,menhgia):
        wizard_data = self.localcontext['data']['form']
        date = wizard_data['date']
        sql='''
            select sum(sl_2_d)+sum(sl_2_c)+sum(sl_2_dc)+sum(sl_2_18)+sum(sl_3_d)+sum(sl_3_c)+sum(sl_3_dc)+sum(sl_3_7)+sum(sl_3_17)+sum(sl_4_16) as tong 
            from 
                (
                    select ve_loto_id,
                        case when sl_2_d_trung !=0 then sl_2_d else 0 end sl_2_d,
                        case when sl_2_c_trung !=0 then sl_2_c else 0 end sl_2_c,
                        case when sl_2_dc_trung !=0 then sl_2_dc else 0 end sl_2_dc,
                        case when sl_2_18_trung !=0 then sl_2_18 else 0 end sl_2_18,
                        
                        case when sl_3_d_trung !=0 then sl_3_d else 0 end sl_3_d,
                        case when sl_3_c_trung !=0 then sl_3_c else 0 end sl_3_c,
                        case when sl_3_dc_trung !=0 then sl_3_dc else 0 end sl_3_dc,
                        case when sl_3_7_trung !=0 then sl_3_7 else 0 end sl_3_7,
                        
                        case when sl_3_17_trung !=0 then sl_3_17 else 0 end sl_3_17,
                        
                        case when sl_4_16_trung !=0 then sl_4_16 else 0 end sl_4_16
                    from ve_loto_line
                    where ve_loto_id = %s
                )foo
                inner join ve_loto vl on vl.id = foo.ve_loto_id where vl.state='done' and vl.product_id = %s
            '''%(soph.id,menhgia.id)
        self.cr.execute(sql,)             
        sluong = self.cr.dictfetchone()['tong'],
        return sluong and sluong[0] or False
    def get_tongve_all(self,menhgia):
        wizard_data = self.localcontext['data']['form']
        date = wizard_data['date']
        sql='''
            select sum(sl_2_d)+sum(sl_2_c)+sum(sl_2_dc)+sum(sl_2_18)+sum(sl_3_d)+sum(sl_3_c)+sum(sl_3_dc)+sum(sl_3_7)+sum(sl_3_17)+sum(sl_4_16) as tong 
            from 
                (
                    select ve_loto_id,
                        case when sl_2_d_trung !=0 then sl_2_d else 0 end sl_2_d,
                        case when sl_2_c_trung !=0 then sl_2_c else 0 end sl_2_c,
                        case when sl_2_dc_trung !=0 then sl_2_dc else 0 end sl_2_dc,
                        case when sl_2_18_trung !=0 then sl_2_18 else 0 end sl_2_18,
                        
                        case when sl_3_d_trung !=0 then sl_3_d else 0 end sl_3_d,
                        case when sl_3_c_trung !=0 then sl_3_c else 0 end sl_3_c,
                        case when sl_3_dc_trung !=0 then sl_3_dc else 0 end sl_3_dc,
                        case when sl_3_7_trung !=0 then sl_3_7 else 0 end sl_3_7,
                        
                        case when sl_3_17_trung !=0 then sl_3_17 else 0 end sl_3_17,
                        
                        case when sl_4_16_trung !=0 then sl_4_16 else 0 end sl_4_16
                    from ve_loto_line
                )foo
                inner join ve_loto vl on vl.id = foo.ve_loto_id where vl.state='done' and vl.product_id = %s and vl.ngay='%s'
            '''%(menhgia.id,date)
        self.cr.execute(sql,)             
        sluong = self.cr.dictfetchone()['tong'],
        return sluong and sluong[0] or False
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
