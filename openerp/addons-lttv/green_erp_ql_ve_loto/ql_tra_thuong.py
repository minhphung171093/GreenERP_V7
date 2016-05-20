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

class quyet_toan_ve_ngay(osv.osv):
    _name = "quyet.toan.ve.ngay"
    
    def _get_tongcong(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids):
            sql = '''
                select case when sum(sl_2_d)!=0 then sum(sl_2_d) else 0 end sl_2_d,
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
                
                    from quyet_toan_ve_ngay_line where quyettoan_id=%s
            '''%(line.id)
            cr.execute(sql)
            tongcong = cr.dictfetchone()
            res[line.id] = {
                'sl_2_d_tong': tongcong['sl_2_d'],
                'st_2_d_tong': tongcong['st_2_d'],
                'sl_2_c_tong': tongcong['sl_2_c'],
                'st_2_c_tong': tongcong['st_2_c'],
                'sl_2_dc_tong': tongcong['sl_2_dc'],
                'st_2_dc_tong': tongcong['st_2_dc'],
                'sl_2_18_tong': tongcong['sl_2_18'],
                'st_2_18_tong': tongcong['st_2_18'],
                
                'sl_3_d_tong': tongcong['sl_3_d'],
                'st_3_d_tong': tongcong['st_3_d'],
                'sl_3_c_tong': tongcong['sl_3_c'],
                'st_3_c_tong': tongcong['st_3_c'],
                'sl_3_dc_tong': tongcong['sl_3_dc'],
                'st_3_dc_tong': tongcong['st_3_dc'],
                'sl_3_7_tong': tongcong['sl_3_7'],
                'st_3_7_tong': tongcong['st_3_7'],
                'sl_3_17_tong': tongcong['sl_3_17'],
                'st_3_17_tong': tongcong['st_3_17'],
                
                'sl_4_16_tong': tongcong['sl_4_16'],
                'st_4_16_tong': tongcong['st_4_16'],
                
                'sl_tong': tongcong['sl_tong'],
                'st_tong': tongcong['st_tong'],
            }
        return res
    
    def _get_chitiet(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('quyet.toan.ve.ngay.line').browse(cr, uid, ids, context=context):
            result[line.quyettoan_id.id] = True
        return result.keys()
    
    _columns = {
        'name': fields.char('Tên',size=1024),
        'product_id': fields.many2one('product.product','Mệnh giá',domain="[('menh_gia','=',True)]",required=True),
        'date_from': fields.date('Từ ngày',required=True),
        'date_to': fields.date('Đến ngày',required=True),
        'co_chi': fields.boolean('Có chi?'),
        'quyettoan_line': fields.one2many('quyet.toan.ve.ngay.line', 'quyettoan_id','Chi tiết quyết toán vé ngày'),
        
        'sl_2_d_tong': fields.function(_get_tongcong, type='float', digits=(16,0), string='Tổng số lượng', multi='tongcong',
            store={
                'quyet.toan.ve.ngay': (lambda self, cr, uid, ids, c={}: ids, ['quyettoan_line','product_id','date_from','date_to'], 10),
                'quyet.toan.ve.ngay.line': (_get_chitiet, ['sl_2_d', 'st_2_d', 'sl_2_c', 'st_2_c', 'sl_2_dc', 'st_2_dc', 'sl_2_18', 'st_2_18',
                                                         'sl_3_d', 'st_3_d', 'sl_3_c', 'st_3_c', 'sl_3_dc', 'st_3_dc', 'sl_3_7', 'st_3_7', 'sl_3_17', 'st_3_17',
                                                         'sl_4_16', 'st_4_16'], 10),
            }),
        'st_2_d_tong': fields.function(_get_tongcong, type='float', digits=(16,0), string='Tổng số lượng', multi='tongcong',
            store={
                'quyet.toan.ve.ngay': (lambda self, cr, uid, ids, c={}: ids, ['quyettoan_line','product_id','date_from','date_to'], 10),
                'quyet.toan.ve.ngay.line': (_get_chitiet, ['sl_2_d', 'st_2_d', 'sl_2_c', 'st_2_c', 'sl_2_dc', 'st_2_dc', 'sl_2_18', 'st_2_18',
                                                         'sl_3_d', 'st_3_d', 'sl_3_c', 'st_3_c', 'sl_3_dc', 'st_3_dc', 'sl_3_7', 'st_3_7', 'sl_3_17', 'st_3_17',
                                                         'sl_4_16', 'st_4_16'], 10),
            }),
        'sl_2_c_tong': fields.function(_get_tongcong, type='float', digits=(16,0), string='Tổng số lượng', multi='tongcong',
            store={
                'quyet.toan.ve.ngay': (lambda self, cr, uid, ids, c={}: ids, ['quyettoan_line','product_id','date_from','date_to'], 10),
                'quyet.toan.ve.ngay.line': (_get_chitiet, ['sl_2_d', 'st_2_d', 'sl_2_c', 'st_2_c', 'sl_2_dc', 'st_2_dc', 'sl_2_18', 'st_2_18',
                                                         'sl_3_d', 'st_3_d', 'sl_3_c', 'st_3_c', 'sl_3_dc', 'st_3_dc', 'sl_3_7', 'st_3_7', 'sl_3_17', 'st_3_17',
                                                         'sl_4_16', 'st_4_16'], 10),
            }),
        'st_2_c_tong': fields.function(_get_tongcong, type='float', digits=(16,0), string='Tổng số lượng', multi='tongcong',
            store={
                'quyet.toan.ve.ngay': (lambda self, cr, uid, ids, c={}: ids, ['quyettoan_line','product_id','date_from','date_to'], 10),
                'quyet.toan.ve.ngay.line': (_get_chitiet, ['sl_2_d', 'st_2_d', 'sl_2_c', 'st_2_c', 'sl_2_dc', 'st_2_dc', 'sl_2_18', 'st_2_18',
                                                         'sl_3_d', 'st_3_d', 'sl_3_c', 'st_3_c', 'sl_3_dc', 'st_3_dc', 'sl_3_7', 'st_3_7', 'sl_3_17', 'st_3_17',
                                                         'sl_4_16', 'st_4_16'], 10),
            }),
        'sl_2_dc_tong': fields.function(_get_tongcong, type='float', digits=(16,0), string='Tổng số lượng', multi='tongcong',
            store={
                'quyet.toan.ve.ngay': (lambda self, cr, uid, ids, c={}: ids, ['quyettoan_line','product_id','date_from','date_to'], 10),
                'quyet.toan.ve.ngay.line': (_get_chitiet, ['sl_2_d', 'st_2_d', 'sl_2_c', 'st_2_c', 'sl_2_dc', 'st_2_dc', 'sl_2_18', 'st_2_18',
                                                         'sl_3_d', 'st_3_d', 'sl_3_c', 'st_3_c', 'sl_3_dc', 'st_3_dc', 'sl_3_7', 'st_3_7', 'sl_3_17', 'st_3_17',
                                                         'sl_4_16', 'st_4_16'], 10),
            }),
        'st_2_dc_tong': fields.function(_get_tongcong, type='float', digits=(16,0), string='Tổng số lượng', multi='tongcong',
            store={
                'quyet.toan.ve.ngay': (lambda self, cr, uid, ids, c={}: ids, ['quyettoan_line','product_id','date_from','date_to'], 10),
                'quyet.toan.ve.ngay.line': (_get_chitiet, ['sl_2_d', 'st_2_d', 'sl_2_c', 'st_2_c', 'sl_2_dc', 'st_2_dc', 'sl_2_18', 'st_2_18',
                                                         'sl_3_d', 'st_3_d', 'sl_3_c', 'st_3_c', 'sl_3_dc', 'st_3_dc', 'sl_3_7', 'st_3_7', 'sl_3_17', 'st_3_17',
                                                         'sl_4_16', 'st_4_16'], 10),
            }),
        'sl_2_18_tong': fields.function(_get_tongcong, type='float', digits=(16,0), string='Tổng số lượng', multi='tongcong',
            store={
                'quyet.toan.ve.ngay': (lambda self, cr, uid, ids, c={}: ids, ['quyettoan_line','product_id','date_from','date_to'], 10),
                'quyet.toan.ve.ngay.line': (_get_chitiet, ['sl_2_d', 'st_2_d', 'sl_2_c', 'st_2_c', 'sl_2_dc', 'st_2_dc', 'sl_2_18', 'st_2_18',
                                                         'sl_3_d', 'st_3_d', 'sl_3_c', 'st_3_c', 'sl_3_dc', 'st_3_dc', 'sl_3_7', 'st_3_7', 'sl_3_17', 'st_3_17',
                                                         'sl_4_16', 'st_4_16'], 10),
            }),
        'st_2_18_tong': fields.function(_get_tongcong, type='float', digits=(16,0), string='Tổng số lượng', multi='tongcong',
            store={
                'quyet.toan.ve.ngay': (lambda self, cr, uid, ids, c={}: ids, ['quyettoan_line','product_id','date_from','date_to'], 10),
                'quyet.toan.ve.ngay.line': (_get_chitiet, ['sl_2_d', 'st_2_d', 'sl_2_c', 'st_2_c', 'sl_2_dc', 'st_2_dc', 'sl_2_18', 'st_2_18',
                                                         'sl_3_d', 'st_3_d', 'sl_3_c', 'st_3_c', 'sl_3_dc', 'st_3_dc', 'sl_3_7', 'st_3_7', 'sl_3_17', 'st_3_17',
                                                         'sl_4_16', 'st_4_16'], 10),
            }),
        
        'sl_3_d_tong': fields.function(_get_tongcong, type='float', digits=(16,0), string='Tổng số lượng', multi='tongcong',
            store={
                'quyet.toan.ve.ngay': (lambda self, cr, uid, ids, c={}: ids, ['quyettoan_line','product_id','date_from','date_to'], 10),
                'quyet.toan.ve.ngay.line': (_get_chitiet, ['sl_2_d', 'st_2_d', 'sl_2_c', 'st_2_c', 'sl_2_dc', 'st_2_dc', 'sl_2_18', 'st_2_18',
                                                         'sl_3_d', 'st_3_d', 'sl_3_c', 'st_3_c', 'sl_3_dc', 'st_3_dc', 'sl_3_7', 'st_3_7', 'sl_3_17', 'st_3_17',
                                                         'sl_4_16', 'st_4_16'], 10),
            }),
        'st_3_d_tong': fields.function(_get_tongcong, type='float', digits=(16,0), string='Tổng số lượng', multi='tongcong',
            store={
                'quyet.toan.ve.ngay': (lambda self, cr, uid, ids, c={}: ids, ['quyettoan_line','product_id','date_from','date_to'], 10),
                'quyet.toan.ve.ngay.line': (_get_chitiet, ['sl_2_d', 'st_2_d', 'sl_2_c', 'st_2_c', 'sl_2_dc', 'st_2_dc', 'sl_2_18', 'st_2_18',
                                                         'sl_3_d', 'st_3_d', 'sl_3_c', 'st_3_c', 'sl_3_dc', 'st_3_dc', 'sl_3_7', 'st_3_7', 'sl_3_17', 'st_3_17',
                                                         'sl_4_16', 'st_4_16'], 10),
            }),
        'sl_3_c_tong': fields.function(_get_tongcong, type='float', digits=(16,0), string='Tổng số lượng', multi='tongcong',
            store={
                'quyet.toan.ve.ngay': (lambda self, cr, uid, ids, c={}: ids, ['quyettoan_line','product_id','date_from','date_to'], 10),
                'quyet.toan.ve.ngay.line': (_get_chitiet, ['sl_2_d', 'st_2_d', 'sl_2_c', 'st_2_c', 'sl_2_dc', 'st_2_dc', 'sl_2_18', 'st_2_18',
                                                         'sl_3_d', 'st_3_d', 'sl_3_c', 'st_3_c', 'sl_3_dc', 'st_3_dc', 'sl_3_7', 'st_3_7', 'sl_3_17', 'st_3_17',
                                                         'sl_4_16', 'st_4_16'], 10),
            }),
        'st_3_c_tong': fields.function(_get_tongcong, type='float', digits=(16,0), string='Tổng số lượng', multi='tongcong',
            store={
                'quyet.toan.ve.ngay': (lambda self, cr, uid, ids, c={}: ids, ['quyettoan_line','product_id','date_from','date_to'], 10),
                'quyet.toan.ve.ngay.line': (_get_chitiet, ['sl_2_d', 'st_2_d', 'sl_2_c', 'st_2_c', 'sl_2_dc', 'st_2_dc', 'sl_2_18', 'st_2_18',
                                                         'sl_3_d', 'st_3_d', 'sl_3_c', 'st_3_c', 'sl_3_dc', 'st_3_dc', 'sl_3_7', 'st_3_7', 'sl_3_17', 'st_3_17',
                                                         'sl_4_16', 'st_4_16'], 10),
            }),
        'sl_3_dc_tong': fields.function(_get_tongcong, type='float', digits=(16,0), string='Tổng số lượng', multi='tongcong',
            store={
                'quyet.toan.ve.ngay': (lambda self, cr, uid, ids, c={}: ids, ['quyettoan_line','product_id','date_from','date_to'], 10),
                'quyet.toan.ve.ngay.line': (_get_chitiet, ['sl_2_d', 'st_2_d', 'sl_2_c', 'st_2_c', 'sl_2_dc', 'st_2_dc', 'sl_2_18', 'st_2_18',
                                                         'sl_3_d', 'st_3_d', 'sl_3_c', 'st_3_c', 'sl_3_dc', 'st_3_dc', 'sl_3_7', 'st_3_7', 'sl_3_17', 'st_3_17',
                                                         'sl_4_16', 'st_4_16'], 10),
            }),
        'st_3_dc_tong': fields.function(_get_tongcong, type='float', digits=(16,0), string='Tổng số lượng', multi='tongcong',
            store={
                'quyet.toan.ve.ngay': (lambda self, cr, uid, ids, c={}: ids, ['quyettoan_line','product_id','date_from','date_to'], 10),
                'quyet.toan.ve.ngay.line': (_get_chitiet, ['sl_2_d', 'st_2_d', 'sl_2_c', 'st_2_c', 'sl_2_dc', 'st_2_dc', 'sl_2_18', 'st_2_18',
                                                         'sl_3_d', 'st_3_d', 'sl_3_c', 'st_3_c', 'sl_3_dc', 'st_3_dc', 'sl_3_7', 'st_3_7', 'sl_3_17', 'st_3_17',
                                                         'sl_4_16', 'st_4_16'], 10),
            }),
        'sl_3_7_tong': fields.function(_get_tongcong, type='float', digits=(16,0), string='Tổng số lượng', multi='tongcong',
            store={
                'quyet.toan.ve.ngay': (lambda self, cr, uid, ids, c={}: ids, ['quyettoan_line','product_id','date_from','date_to'], 10),
                'quyet.toan.ve.ngay.line': (_get_chitiet, ['sl_2_d', 'st_2_d', 'sl_2_c', 'st_2_c', 'sl_2_dc', 'st_2_dc', 'sl_2_18', 'st_2_18',
                                                         'sl_3_d', 'st_3_d', 'sl_3_c', 'st_3_c', 'sl_3_dc', 'st_3_dc', 'sl_3_7', 'st_3_7', 'sl_3_17', 'st_3_17',
                                                         'sl_4_16', 'st_4_16'], 10),
            }),
        'st_3_7_tong': fields.function(_get_tongcong, type='float', digits=(16,0), string='Tổng số lượng', multi='tongcong',
            store={
                'quyet.toan.ve.ngay': (lambda self, cr, uid, ids, c={}: ids, ['quyettoan_line','product_id','date_from','date_to'], 10),
                'quyet.toan.ve.ngay.line': (_get_chitiet, ['sl_2_d', 'st_2_d', 'sl_2_c', 'st_2_c', 'sl_2_dc', 'st_2_dc', 'sl_2_18', 'st_2_18',
                                                         'sl_3_d', 'st_3_d', 'sl_3_c', 'st_3_c', 'sl_3_dc', 'st_3_dc', 'sl_3_7', 'st_3_7', 'sl_3_17', 'st_3_17',
                                                         'sl_4_16', 'st_4_16'], 10),
            }),
        'sl_3_17_tong': fields.function(_get_tongcong, type='float', digits=(16,0), string='Tổng số lượng', multi='tongcong',
            store={
                'quyet.toan.ve.ngay': (lambda self, cr, uid, ids, c={}: ids, ['quyettoan_line','product_id','date_from','date_to'], 10),
                'quyet.toan.ve.ngay.line': (_get_chitiet, ['sl_2_d', 'st_2_d', 'sl_2_c', 'st_2_c', 'sl_2_dc', 'st_2_dc', 'sl_2_18', 'st_2_18',
                                                         'sl_3_d', 'st_3_d', 'sl_3_c', 'st_3_c', 'sl_3_dc', 'st_3_dc', 'sl_3_7', 'st_3_7', 'sl_3_17', 'st_3_17',
                                                         'sl_4_16', 'st_4_16'], 10),
            }),
        'st_3_17_tong': fields.function(_get_tongcong, type='float', digits=(16,0), string='Tổng số lượng', multi='tongcong',
            store={
                'quyet.toan.ve.ngay': (lambda self, cr, uid, ids, c={}: ids, ['quyettoan_line','product_id','date_from','date_to'], 10),
                'quyet.toan.ve.ngay.line': (_get_chitiet, ['sl_2_d', 'st_2_d', 'sl_2_c', 'st_2_c', 'sl_2_dc', 'st_2_dc', 'sl_2_18', 'st_2_18',
                                                         'sl_3_d', 'st_3_d', 'sl_3_c', 'st_3_c', 'sl_3_dc', 'st_3_dc', 'sl_3_7', 'st_3_7', 'sl_3_17', 'st_3_17',
                                                         'sl_4_16', 'st_4_16'], 10),
            }),
        
        'sl_4_16_tong': fields.function(_get_tongcong, type='float', digits=(16,0), string='Tổng số lượng', multi='tongcong',
            store={
                'quyet.toan.ve.ngay': (lambda self, cr, uid, ids, c={}: ids, ['quyettoan_line','product_id','date_from','date_to'], 10),
                'quyet.toan.ve.ngay.line': (_get_chitiet, ['sl_2_d', 'st_2_d', 'sl_2_c', 'st_2_c', 'sl_2_dc', 'st_2_dc', 'sl_2_18', 'st_2_18',
                                                         'sl_3_d', 'st_3_d', 'sl_3_c', 'st_3_c', 'sl_3_dc', 'st_3_dc', 'sl_3_7', 'st_3_7', 'sl_3_17', 'st_3_17',
                                                         'sl_4_16', 'st_4_16'], 10),
            }),
        'st_4_16_tong': fields.function(_get_tongcong, type='float', digits=(16,0), string='Tổng số lượng', multi='tongcong',
            store={
                'quyet.toan.ve.ngay': (lambda self, cr, uid, ids, c={}: ids, ['quyettoan_line','product_id','date_from','date_to'], 10),
                'quyet.toan.ve.ngay.line': (_get_chitiet, ['sl_2_d', 'st_2_d', 'sl_2_c', 'st_2_c', 'sl_2_dc', 'st_2_dc', 'sl_2_18', 'st_2_18',
                                                         'sl_3_d', 'st_3_d', 'sl_3_c', 'st_3_c', 'sl_3_dc', 'st_3_dc', 'sl_3_7', 'st_3_7', 'sl_3_17', 'st_3_17',
                                                         'sl_4_16', 'st_4_16'], 10),
            }),
        'sl_tong': fields.function(_get_tongcong, type='float', digits=(16,0), string='Tổng số lượng', multi='tongcong',
            store={
                'quyet.toan.ve.ngay': (lambda self, cr, uid, ids, c={}: ids, ['quyettoan_line','product_id','date_from','date_to'], 20),
                'quyet.toan.ve.ngay.line': (_get_chitiet, ['sl_2_d', 'st_2_d', 'sl_2_c', 'st_2_c', 'sl_2_dc', 'st_2_dc', 'sl_2_18', 'st_2_18',
                                                         'sl_3_d', 'st_3_d', 'sl_3_c', 'st_3_c', 'sl_3_dc', 'st_3_dc', 'sl_3_7', 'st_3_7', 'sl_3_17', 'st_3_17',
                                                         'sl_4_16', 'st_4_16'], 20),
            }),
        'st_tong': fields.function(_get_tongcong, type='float', digits=(16,0), string='Tổng số lượng', multi='tongcong',
            store={
                'quyet.toan.ve.ngay': (lambda self, cr, uid, ids, c={}: ids, ['quyettoan_line','product_id','date_from','date_to'], 20),
                'quyet.toan.ve.ngay.line': (_get_chitiet, ['sl_2_d', 'st_2_d', 'sl_2_c', 'st_2_c', 'sl_2_dc', 'st_2_dc', 'sl_2_18', 'st_2_18',
                                                         'sl_3_d', 'st_3_d', 'sl_3_c', 'st_3_c', 'sl_3_dc', 'st_3_dc', 'sl_3_7', 'st_3_7', 'sl_3_17', 'st_3_17',
                                                         'sl_4_16', 'st_4_16'], 20),
            }),
#         'state': fields.selection([('new','Mới tạo'),('done','Đã xuất báo cáo')],'Trạng thái'),
    }
    
    _defaults = {
        'name':'Quyết toán vé ngày',
    }
    
    
    def get_lines(self, cr, product_id, date_from, date_to, co_chi):
        res = []
        seq = -1
        if co_chi:
            sql = '''
                select tttt.ngay as ngay_mo_so, kqxs.dai_duthuong_id as dai_duthuong
                    from tra_thuong_thucte tttt
                    left join ketqua_xoso kqxs on kqxs.name = tttt.ngay
                    where tttt.daily_id is not null and tttt.state='done' and tttt.ngay_tra_thuong between '%s' and '%s' and tttt.id in (select trathuong_id from tra_thuong_thucte_line where product_id=%s)
                    group by tttt.ngay,kqxs.dai_duthuong_id
                    order by tttt.ngay
            '''%(date_from, date_to,product_id)
        else:
            sql = '''
                select tttt.ngay as ngay_mo_so, kqxs.dai_duthuong_id as dai_duthuong
                    from tra_thuong_thucte tttt
                    left join ketqua_xoso kqxs on kqxs.name = tttt.ngay
                    where tttt.daily_id is null and tttt.state='done' and tttt.ngay_tra_thuong between '%s' and '%s' and tttt.id in (select trathuong_id from tra_thuong_thucte_line where product_id=%s)
                    group by tttt.ngay,kqxs.dai_duthuong_id
                    order by tttt.ngay
            '''%(date_from, date_to,product_id)
        cr.execute(sql)
        for seq_tt,line in enumerate(cr.dictfetchall()):
            seq += 1
            seq_n = seq
            res.append({
                'ngay_mo_so': line['ngay_mo_so'],
                'ngay_mo_thuong': line['ngay_mo_so'],
                'dai_duthuong_id': line['dai_duthuong'],
            })
            # 2 so
            sql = '''
                select case when sum(sl_trung)!=0 then sum(sl_trung) else 0 end sl_trung,
                    case when sum(sl_trung * slan_trung * tong_tien)!=0 then sum(sl_trung * slan_trung * tong_tien) else 0 end so_tien
                    
                    from tra_thuong_thucte_line where loai='2_so' and giai='dau' and product_id=%s
                        and trathuong_id in (select id from tra_thuong_thucte where ngay='%s' and ngay_tra_thuong between '%s' and '%s' and state='done' 
            '''%(product_id, line['ngay_mo_so'], date_from, date_to)
            if co_chi:
                sql += '''
                    and daily_id is not null 
                    )
                '''
            else:
                sql += '''
                    and daily_id is null 
                    )
                '''
            cr.execute(sql)
            loai_2_d = cr.dictfetchone()
            res[seq_n]['sl_2_d'] = loai_2_d['sl_trung']
            res[seq_n]['st_2_d'] = loai_2_d['so_tien']
            
            sql = '''
                select case when sum(sl_trung)!=0 then sum(sl_trung) else 0 end sl_trung,
                    case when sum(sl_trung * slan_trung * tong_tien)!=0 then sum(sl_trung * slan_trung * tong_tien) else 0 end so_tien
                    
                    from tra_thuong_thucte_line where loai='2_so' and giai='cuoi' and product_id=%s
                        and trathuong_id in (select id from tra_thuong_thucte where ngay='%s' and ngay_tra_thuong between '%s' and '%s' and state='done' 
            '''%(product_id, line['ngay_mo_so'], date_from, date_to)
            if co_chi:
                sql += '''
                    and daily_id is not null 
                    )
                '''
            else:
                sql += '''
                    and daily_id is null 
                    )
                '''
            cr.execute(sql)
            loai_2_c = cr.dictfetchone()
            res[seq_n]['sl_2_c'] = loai_2_c['sl_trung']
            res[seq_n]['st_2_c'] = loai_2_c['so_tien']
            
            sql = '''
                select slan_trung,case when sum(sl_trung)!=0 then sum(sl_trung) else 0 end sl_trung,
                    case when sum(sl_trung * slan_trung * tong_tien)!=0 then sum(sl_trung * slan_trung * tong_tien) else 0 end so_tien
                    
                    from tra_thuong_thucte_line where loai='2_so' and giai='dau_cuoi' and product_id=%s
                        and trathuong_id in (select id from tra_thuong_thucte where ngay='%s' and ngay_tra_thuong between '%s' and '%s' and state='done' 
            '''%(product_id, line['ngay_mo_so'], date_from, date_to)
            if co_chi:
                sql += '''
                    and daily_id is not null 
                    ) group by slan_trung
                '''
            else:
                sql += '''
                    and daily_id is null 
                    ) group by slan_trung
                '''
            cr.execute(sql)
            for s_2_dc,loai_2_dc in enumerate(cr.dictfetchall()):
                if seq_n+s_2_dc > seq and (loai_2_dc['sl_trung']!=0 or loai_2_dc['slan_trung']!=0 or loai_2_dc['so_tien']!=0):
                    seq += 1
                    res.append({'ngay_mo_thuong': line['ngay_mo_so']})
                res[seq_n+s_2_dc]['sl_2_dc'] = loai_2_dc['sl_trung']
                res[seq_n+s_2_dc]['slan_2_dc'] = loai_2_dc['slan_trung']
                res[seq_n+s_2_dc]['st_2_dc'] = loai_2_dc['so_tien']
                
            sql = '''
                select slan_trung,case when sum(sl_trung)!=0 then sum(sl_trung) else 0 end sl_trung,
                    case when sum(sl_trung * slan_trung * tong_tien)!=0 then sum(sl_trung * slan_trung * tong_tien) else 0 end so_tien
                    
                    from tra_thuong_thucte_line where loai='2_so' and giai='18_lo' and product_id=%s
                        and trathuong_id in (select id from tra_thuong_thucte where ngay='%s' and ngay_tra_thuong between '%s' and '%s' and state='done' 
            '''%(product_id, line['ngay_mo_so'], date_from, date_to)
            if co_chi:
                sql += '''
                    and daily_id is not null 
                    ) group by slan_trung
                '''
            else:
                sql += '''
                    and daily_id is null 
                    ) group by slan_trung
                '''
            cr.execute(sql)
            for s_2_18,loai_2_18 in enumerate(cr.dictfetchall()):
                if seq_n+s_2_18 > seq and (loai_2_18['sl_trung']!=0 or loai_2_18['slan_trung']!=0 or loai_2_18['so_tien']!=0):
                    seq += 1
                    res.append({'ngay_mo_thuong': line['ngay_mo_so']})
                res[seq_n+s_2_18]['sl_2_18'] = loai_2_18['sl_trung']
                res[seq_n+s_2_18]['slan_2_18'] = loai_2_18['slan_trung']
                res[seq_n+s_2_18]['st_2_18'] = loai_2_18['so_tien']
            
            # 3 so
            sql = '''
                select case when sum(sl_trung)!=0 then sum(sl_trung) else 0 end sl_trung,
                    case when sum(sl_trung * slan_trung * tong_tien)!=0 then sum(sl_trung * slan_trung * tong_tien) else 0 end so_tien
                    
                    from tra_thuong_thucte_line where loai='3_so' and giai='dau' and product_id=%s
                        and trathuong_id in (select id from tra_thuong_thucte where ngay='%s' and ngay_tra_thuong between '%s' and '%s' and state='done' 
            '''%(product_id, line['ngay_mo_so'], date_from, date_to)
            if co_chi:
                sql += '''
                    and daily_id is not null 
                    )
                '''
            else:
                sql += '''
                    and daily_id is null 
                    )
                '''
            cr.execute(sql)
            loai_3_d = cr.dictfetchone()
            res[seq_n]['sl_3_d'] = loai_3_d['sl_trung']
            res[seq_n]['st_3_d'] = loai_3_d['so_tien']
            
            sql = '''
                select case when sum(sl_trung)!=0 then sum(sl_trung) else 0 end sl_trung,
                    case when sum(sl_trung * slan_trung * tong_tien)!=0 then sum(sl_trung * slan_trung * tong_tien) else 0 end so_tien
                    
                    from tra_thuong_thucte_line where loai='3_so' and giai='cuoi' and product_id=%s
                        and trathuong_id in (select id from tra_thuong_thucte where ngay='%s' and ngay_tra_thuong between '%s' and '%s' and state='done' 
            '''%(product_id, line['ngay_mo_so'], date_from, date_to)
            if co_chi:
                sql += '''
                    and daily_id is not null 
                    )
                '''
            else:
                sql += '''
                    and daily_id is null 
                    )
                '''
            cr.execute(sql)
            loai_3_c = cr.dictfetchone()
            res[seq_n]['sl_3_c'] = loai_3_c['sl_trung']
            res[seq_n]['st_3_c'] = loai_3_c['so_tien']
            
            sql = '''
                select slan_trung,case when sum(sl_trung)!=0 then sum(sl_trung) else 0 end sl_trung,
                    case when sum(sl_trung * slan_trung * tong_tien)!=0 then sum(sl_trung * slan_trung * tong_tien) else 0 end so_tien
                    
                    from tra_thuong_thucte_line where loai='3_so' and giai='dau_cuoi' and product_id=%s
                        and trathuong_id in (select id from tra_thuong_thucte where ngay='%s' and ngay_tra_thuong between '%s' and '%s' and state='done' 
            '''%(product_id, line['ngay_mo_so'], date_from, date_to)
            if co_chi:
                sql += '''
                    and daily_id is not null 
                    ) group by slan_trung
                '''
            else:
                sql += '''
                    and daily_id is null 
                    ) group by slan_trung
                '''
            cr.execute(sql)
            for s_3_dc,loai_3_dc in enumerate(cr.dictfetchall()):
                if seq_n+s_3_dc > seq and (loai_3_dc['sl_trung']!=0 or loai_3_dc['slan_trung']!=0 or loai_3_dc['so_tien']!=0):
                    seq += 1
                    res.append({'ngay_mo_thuong': line['ngay_mo_so']})
                res[seq_n+s_3_dc]['sl_3_dc'] = loai_3_dc['sl_trung']
                res[seq_n+s_3_dc]['slan_3_dc'] = loai_3_dc['slan_trung']
                res[seq_n+s_3_dc]['st_3_dc'] = loai_3_dc['so_tien']
                
            sql = '''
                select slan_trung,case when sum(sl_trung)!=0 then sum(sl_trung) else 0 end sl_trung,
                    case when sum(sl_trung * slan_trung * tong_tien)!=0 then sum(sl_trung * slan_trung * tong_tien) else 0 end so_tien
                    
                    from tra_thuong_thucte_line where loai='3_so' and giai='7_lo' and product_id=%s
                        and trathuong_id in (select id from tra_thuong_thucte where ngay='%s' and ngay_tra_thuong between '%s' and '%s' and state='done' 
            '''%(product_id, line['ngay_mo_so'], date_from, date_to)
            if co_chi:
                sql += '''
                    and daily_id is not null 
                    ) group by slan_trung 
                '''
            else:
                sql += '''
                    and daily_id is null 
                    ) group by slan_trung 
                '''
            cr.execute(sql)
            for s_3_7,loai_3_7 in enumerate(cr.dictfetchall()):
                if seq_n+s_3_7 > seq and (loai_3_7['sl_trung']!=0 or loai_3_7['slan_trung']!=0 or loai_3_7['so_tien']!=0):
                    seq += 1
                    res.append({'ngay_mo_thuong': line['ngay_mo_so']})
                res[seq_n+s_3_7]['sl_3_7'] = loai_3_7['sl_trung']
                res[seq_n+s_3_7]['slan_3_7'] = loai_3_7['slan_trung']
                res[seq_n+s_3_7]['st_3_7'] = loai_3_7['so_tien']
                
            sql = '''
                select slan_trung,case when sum(sl_trung)!=0 then sum(sl_trung) else 0 end sl_trung,
                    case when sum(sl_trung * slan_trung * tong_tien)!=0 then sum(sl_trung * slan_trung * tong_tien) else 0 end so_tien
                    
                    from tra_thuong_thucte_line where loai='3_so' and giai='17_lo' and product_id=%s
                        and trathuong_id in (select id from tra_thuong_thucte where ngay='%s' and ngay_tra_thuong between '%s' and '%s' and state='done' 
            '''%(product_id, line['ngay_mo_so'], date_from, date_to)
            if co_chi:
                sql += '''
                    and daily_id is not null 
                    ) group by slan_trung
                '''
            else:
                sql += '''
                    and daily_id is null 
                    ) group by slan_trung
                '''
            cr.execute(sql)
            for s_3_17,loai_3_17 in enumerate(cr.dictfetchall()):
                if seq_n+s_3_17 > seq and (loai_3_17['sl_trung']!=0 or loai_3_17['slan_trung']!=0 or loai_3_17['so_tien']!=0):
                    seq += 1
                    res.append({'ngay_mo_thuong': line['ngay_mo_so']})
                res[seq_n+s_3_17]['sl_3_17'] = loai_3_17['sl_trung']
                res[seq_n+s_3_17]['slan_3_17'] = loai_3_17['slan_trung']
                res[seq_n+s_3_17]['st_3_17'] = loai_3_17['so_tien']
                
            #4 so
            sql = '''
                select slan_trung,case when sum(sl_trung)!=0 then sum(sl_trung) else 0 end sl_trung,
                    case when sum(sl_trung * slan_trung * tong_tien)!=0 then sum(sl_trung * slan_trung * tong_tien) else 0 end so_tien
                    
                    from tra_thuong_thucte_line where loai='4_so' and giai='16_lo' and product_id=%s
                        and trathuong_id in (select id from tra_thuong_thucte where ngay='%s' and ngay_tra_thuong between '%s' and '%s' and state='done' 
            '''%(product_id, line['ngay_mo_so'], date_from, date_to)
            if co_chi:
                sql += '''
                    and daily_id is not null 
                    ) group by slan_trung
                '''
            else:
                sql += '''
                    and daily_id is null 
                    ) group by slan_trung
                '''
            cr.execute(sql)
            for s_4_16,loai_4_16 in enumerate(cr.dictfetchall()):
                if seq_n+s_4_16 > seq and (loai_4_16['sl_trung']!=0 or loai_4_16['slan_trung']!=0 or loai_4_16['so_tien']!=0):
                    seq += 1
                    res.append({'ngay_mo_thuong': line['ngay_mo_so']})
                res[seq_n+s_4_16]['sl_4_16'] = loai_4_16['sl_trung']
                res[seq_n+s_4_16]['slan_4_16'] = loai_4_16['slan_trung']
                res[seq_n+s_4_16]['st_4_16'] = loai_4_16['so_tien']
                
        return res

    def create(self, cr, uid, vals, context=None):
        value = self.get_lines(cr, vals['product_id'], vals['date_from'], vals['date_to'], vals['co_chi'])
        quyettoan_line = []
        for line in value:
            if line:
                quyettoan_line.append((0,0,line))
        vals['quyettoan_line'] = quyettoan_line
        return super(quyet_toan_ve_ngay, self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        new_write = super(quyet_toan_ve_ngay, self).write(cr, uid, ids, vals, context)
        for quyettoan in self.browse(cr, uid, ids):
            sql = '''
                delete from quyet_toan_ve_ngay_line where quyettoan_id=%s
            '''%(quyettoan.id)
            cr.execute(sql)
            value = self.get_lines(cr, quyettoan.product_id.id, quyettoan.date_from, quyettoan.date_to, quyettoan.co_chi)
            quyettoan_line = []
            for line in value:
                if line:
                    line['quyettoan_id'] = quyettoan.id
                    self.pool.get('quyet.toan.ve.ngay.line').create(cr, uid, line)
        return new_write

quyet_toan_ve_ngay()

class quyet_toan_ve_ngay_line(osv.osv):
    _name = "quyet.toan.ve.ngay.line"
    
    def _get_tongcong(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids):
            res[line.id] = {
                'sl_tong': 0,
                'st_tong': 0,
            }
            sl_tong = line.sl_2_d + line.sl_2_c + line.sl_2_dc + line.sl_2_18 + line.sl_3_d + line.sl_3_c + line.sl_3_dc + line.sl_3_7 + line.sl_3_17 + line.sl_4_16
            st_tong = line.st_2_d + line.st_2_c + line.st_2_dc + line.st_2_18 + line.st_3_d + line.st_3_c + line.st_3_dc + line.st_3_7 + line.st_3_17 + line.st_4_16 
            res[line.id]['sl_tong'] = sl_tong
            res[line.id]['st_tong'] = st_tong
        return res
    _columns = {
        'quyettoan_id': fields.many2one('quyet.toan.ve.ngay','Quyết toán vé ngày',ondelete='cascade'),
        'ngay_mo_so': fields.date('Ngày mở số'),
        'ngay_mo_thuong': fields.date('Ngày mở thưởng'),#luon co du lieu
        'dai_duthuong_id': fields.many2one('dai.duthuong', 'Đài dự thưởng'),
        'sl_2_d': fields.float('SL', digits=(16,0)),
        'st_2_d': fields.float('SL', digits=(16,0)),
        'sl_2_c': fields.float('SL', digits=(16,0)),
        'st_2_c': fields.float('SL', digits=(16,0)),
        'sl_2_dc': fields.float('SL', digits=(16,0)),
        'slan_2_dc': fields.float('SL', digits=(16,0)),
        'st_2_dc': fields.float('SL', digits=(16,0)),
        'sl_2_18': fields.float('SL', digits=(16,0)),
        'slan_2_18': fields.float('SL', digits=(16,0)),
        'st_2_18': fields.float('SL', digits=(16,0)),
        
        'sl_3_d': fields.float('SL', digits=(16,0)),
        'st_3_d': fields.float('SL', digits=(16,0)),
        'sl_3_c': fields.float('SL', digits=(16,0)),
        'st_3_c': fields.float('SL', digits=(16,0)),
        'sl_3_dc': fields.float('SL', digits=(16,0)),
        'slan_3_dc': fields.float('SL', digits=(16,0)),
        'st_3_dc': fields.float('SL', digits=(16,0)),
        'sl_3_7': fields.float('SL', digits=(16,0)),
        'slan_3_7': fields.float('SL', digits=(16,0)),
        'st_3_7': fields.float('SL', digits=(16,0)),
        'sl_3_17': fields.float('SL', digits=(16,0)),
        'slan_3_17': fields.float('SL', digits=(16,0)),
        'st_3_17': fields.float('SL', digits=(16,0)),
        
        'sl_4_16': fields.float('SL', digits=(16,0)),
        'slan_4_16': fields.float('SL', digits=(16,0)),
        'st_4_16': fields.float('SL', digits=(16,0)),
        
        'sl_tong': fields.function(_get_tongcong, type='float', digits=(16,0), string='Tổng số lượng', multi='tong', store=True),
        'st_tong': fields.function(_get_tongcong, type='float', digits=(16,0), string='Tổng số lượng', multi='tong', store=True),
        
    }
    
quyet_toan_ve_ngay_line()
