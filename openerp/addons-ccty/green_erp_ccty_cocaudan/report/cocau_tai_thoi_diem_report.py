# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
            'get_cocau': self.get_cocau,
            'get_cell': self.get_cell,
            'get_col': self.get_col,
            'get_col_loai': self.get_col_loai,
            'get_ho_row': self.get_ho_row,
        })
        
    def get_cocau(self):
        return {}

    def get_ho_row(self):
        wizard_data = self.localcontext['data']['form']
        ten_ho_id = wizard_data['ten_ho_id']
        sql='''
            select * from co_cau where ten_ho_id = %s 
        '''%(ten_ho_id[0])
        self.cr.execute(sql)
        return self.cr.dictfetchall()
    
    def get_col(self):
        res = []
        sql = '''
            select * from chi_tiet_loai_vat where loai_id in (select id from loai_vat where name = 'Bò sữa')
        '''
        self.cr.execute(sql)
        
        for ct in self.cr.dictfetchall():
            res.append((0,0,{
                             'loaivat':'Bò Sữa','ct': ct['name']
                            }
                    ))
        res.append((0,0,{
                             'loaivat':'','ct': 'Cộng bò sữa'
                            }
                    ))    
        sql = '''
            select * from chi_tiet_loai_vat where loai_id in (select id from loai_vat where name = 'Bò ta')
        '''
        self.cr.execute(sql)
        for ct in self.cr.dictfetchall():
            res.append((0,0,{
                             'loaivat':'Bò Ta','ct': ct['name']
                            }
                    ))
        res.append((0,0,{
                             'loaivat':'','ct': 'Cộng bò ta'
                            }
                    ))   
        sql = '''
            select * from chi_tiet_loai_vat where loai_id in (select id from loai_vat where name = 'Bò lai sind')
        '''
        self.cr.execute(sql)
        for ct in self.cr.dictfetchall():
            res.append((0,0,{
                             'loaivat':'Bò lai sind','ct': ct['name']
                            }
                    ))
        res.append((0,0,{
                             'loaivat':'','ct': 'Cộng bò lai sind'
                            }
                    )) 
        sql = '''
            select * from chi_tiet_loai_vat where loai_id in (select id from loai_vat where name = 'Trâu')
        '''
        self.cr.execute(sql)
        for ct in self.cr.dictfetchall():
            res.append((0,0,{
                             'loaivat':'Trâu','ct': ct['name']
                            }
                    ))
        res.append((0,0,{
                             'loaivat':'','ct': 'Cộng trâu'
                            }
                    )) 
        return res
#         {'loaivat': 'trau',
#          'ct': 'duc',
#          }
#         return  [{'loaivat':'bo sua','ct':'bo sua duc','ct_hon':''},
#                 {'loaivat':'', 'ct':'bo sua cai','ct_hon':'< 6 thang'},
#                 {'loaivat':'', 'ct':'','ct_hon':'to'},
#                 {'loaivat':'', 'ct':'','ct_hon':'sinh san'},
#         
#                 {'loaivat':'bo ta','ct':'< 6 thang','ct_hon':''},
#                 {'loaivat':'', 'ct':'> 6 thang', 'ct_hon':''}
#                 ]
    
    def get_col_loai(self):
        
        {'loaivat': 'trau',
         'ct': 'duc',
         }
        return [{'loaivat': 'bo sua',},
                {'loaivat': 'bo ta',}
                ]
                
    
#     def get_row(self):
#         
#         return [1,2,3,4,5,6]
    
    def get_cell(self,row,col):
        soluong = 0
        sum = 0
        wizard_data = self.localcontext['data']['form']
        ten_ho_id = wizard_data['ten_ho_id']
        sql = '''
            select so_luong from chi_tiet_loai_line where name = '%s' and co_cau_id in (select id from co_cau where ten_ho_id = %s and ngay_ghi_so = %s)
        '''%(col, ten_ho_id[0], row)
        self.cr.execute(sql)
        sl = self.cr.dictfetchone()
        if sl:
            soluong = sl['so_luong']
        else:
            if col == "Cộng bò sữa":
                sql = '''
                    select sum(so_luong) as sum from chi_tiet_loai_line where
                    co_cau_id in (select id from co_cau where ten_ho_id = %s and chon_loai in (select id from loai_vat where name = 'Bò sữa'))
                '''%(row)
                self.cr.execute(sql)
                soluong = self.cr.dictfetchone()['sum']
        return soluong
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
