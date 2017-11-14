# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2012 OpenERP SA (<http://openerp.com>).
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

import base64
import re
import threading
from openerp.tools.safe_eval import safe_eval as eval
from openerp import tools
import openerp.modules
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import SUPERUSER_ID
from openerp import netsvc


class muc_tran(osv.osv):
    _name = "muc.tran"
    _columns = {
        'mt_2_d': fields.float('Đầu', digits=(16,0)),
        'mt_2_c': fields.float('Cuối', digits=(16,0)),
        'mt_2_dc': fields.float('Đầu/Cuối', digits=(16,0)),
        'mt_2_18': fields.float('18 lô', digits=(16,0)),
        'mt_3_d': fields.float('Đầu', digits=(16,0)),
        'mt_3_c': fields.float('Cuối', digits=(16,0)),
        'mt_3_dc': fields.float('Đầu/Cuối', digits=(16,0)),
        'mt_3_7': fields.float('7 lô', digits=(16,0)),
        'mt_3_17': fields.float('17 lô', digits=(16,0)),
        'mt_4_16': fields.float('16 lô', digits=(16,0))
    }
    
muc_tran()

class vuot_tran(osv.osv):
    _name = "vuot.tran"
    _order = "ngay_xs desc"
    
    _columns = {
        'ngay_xs': fields.date('Ngày xổ số',required=True),
        'vuot_tran_line': fields.one2many('vuot.tran.line','vuot_tran_id')
    }

    def update(self, cr, uid, ids, context=None):
        for record in self.browse(cr,uid,ids):
            sql = '''
                delete from vuot_tran_line where vuot_tran_id=%s
            '''%(record.id)
            cr.execute(sql)
            product_obj = self.pool.get('product.product')
            
            sql='''
                select v.daily_id as daily, v.product_id, vl.*
                from ve_loto_line vl 
                left join ve_loto v on vl.ve_loto_id = v.id
                where v.ngay = '%s'
            '''%(record.ngay_xs)
            data_dict = {}
            data_muctran_dict = {}
            cr.execute(sql)
            for line in cr.dictfetchall():
                
                product = product_obj.browse(cr, uid, line['product_id'])
                if line['so_dt_2_d'] and line['sl_2_d']:
                    loai_2  = '2_so'
                    giai_2_d = 'dau'
                    so_dt_2_d = line['so_dt_2_d']
                    st_2_d = line['sl_2_d']*int(product.list_price)
                    if data_dict.get(line['daily'], False):
                        if data_dict[line['daily']].get(loai_2, False):
                            if data_dict[line['daily']][loai_2].get(giai_2_d, False):
                                if data_dict[line['daily']][loai_2][giai_2_d].get(so_dt_2_d, False):
                                    data_dict[line['daily']][loai_2][giai_2_d][so_dt_2_d] += st_2_d
                                else:
                                    data_dict[line['daily']][loai_2][giai_2_d][so_dt_2_d] = st_2_d
                            else:
                                data_dict[line['daily']][loai_2][giai_2_d] = {so_dt_2_d: st_2_d}
                        else:
                            data_dict[line['daily']][loai_2] = {giai_2_d: {so_dt_2_d: st_2_d}}
                    else:
                        data_dict[line['daily']] = {loai_2: {giai_2_d: {so_dt_2_d: st_2_d}}}

                if line['so_dt_2_c'] and line['sl_2_c']:
                    loai_2  = '2_so'
                    giai_2_c = 'cuoi'
                    so_dt_2_c = line['so_dt_2_c']
                    st_2_c = line['sl_2_c']*int(product.list_price)
                    if data_dict.get(line['daily'], False):
                        if data_dict[line['daily']].get(loai_2, False):
                            if data_dict[line['daily']][loai_2].get(giai_2_c, False):
                                if data_dict[line['daily']][loai_2][giai_2_c].get(so_dt_2_c, False):
                                    data_dict[line['daily']][loai_2][giai_2_c][so_dt_2_c] += st_2_c
                                else:
                                    data_dict[line['daily']][loai_2][giai_2_c][so_dt_2_c] = st_2_c
                            else:
                                data_dict[line['daily']][loai_2][giai_2_c] = {so_dt_2_c: st_2_c}
                        else:
                            data_dict[line['daily']][loai_2] = {giai_2_c: {so_dt_2_c: st_2_c}}
                    else:
                        data_dict[line['daily']] = {loai_2: {giai_2_c: {so_dt_2_c: st_2_c}}}
                         
                if line['so_dt_2_dc'] and line['sl_2_dc']:
                    loai_2  = '2_so'
                    giai_2_dc = 'dau_cuoi'
                    so_dt_2_dc = line['so_dt_2_dc']
                    st_2_dc = line['sl_2_dc']*int(product.list_price)
                    if data_dict.get(line['daily'], False):
                        if data_dict[line['daily']].get(loai_2, False):
                            if data_dict[line['daily']][loai_2].get(giai_2_dc, False):
                                if data_dict[line['daily']][loai_2][giai_2_dc].get(so_dt_2_dc, False):
                                    data_dict[line['daily']][loai_2][giai_2_dc][so_dt_2_dc] += st_2_dc
                                else:
                                    data_dict[line['daily']][loai_2][giai_2_dc][so_dt_2_dc] = st_2_dc
                            else:
                                data_dict[line['daily']][loai_2][giai_2_dc] = {so_dt_2_dc: st_2_dc}
                        else:
                            data_dict[line['daily']][loai_2] = {giai_2_dc: {so_dt_2_dc: st_2_dc}}
                    else:
                        data_dict[line['daily']] = {loai_2: {giai_2_dc: {so_dt_2_dc: st_2_dc}}}
                         
                if line['so_dt_2_18'] and line['sl_2_18']:
                    loai_2  = '2_so'
                    giai_2_18 = '18_lo'
                    so_dt_2_18 = line['so_dt_2_18']
                    st_2_18 = line['sl_2_18']*int(product.list_price)
                    if data_dict.get(line['daily'], False):
                        if data_dict[line['daily']].get(loai_2, False):
                            if data_dict[line['daily']][loai_2].get(giai_2_18, False):
                                if data_dict[line['daily']][loai_2][giai_2_18].get(so_dt_2_18, False):
                                    data_dict[line['daily']][loai_2][giai_2_18][so_dt_2_18] += st_2_18
                                else:
                                    data_dict[line['daily']][loai_2][giai_2_18][so_dt_2_18] = st_2_18
                            else:
                                data_dict[line['daily']][loai_2][giai_2_18] = {so_dt_2_18: st_2_18}
                        else:
                            data_dict[line['daily']][loai_2] = {giai_2_18: {so_dt_2_18: st_2_18}}
                    else:
                        data_dict[line['daily']] = {loai_2: {giai_2_18: {so_dt_2_18: st_2_18}}}   
                            
                if line['so_dt_3_d'] and line['sl_3_d']:
                    loai_3  = '3_so'
                    giai_3_d = 'dau'
                    so_dt_3_d = line['so_dt_3_d']
                    st_3_d = line['sl_3_d']*int(product.list_price)
                    if data_dict.get(line['daily'], False):
                        if data_dict[line['daily']].get(loai_3, False):
                            if data_dict[line['daily']][loai_3].get(giai_3_d, False):
                                if data_dict[line['daily']][loai_3][giai_3_d].get(so_dt_3_d, False):
                                    data_dict[line['daily']][loai_3][giai_3_d][so_dt_3_d] += st_3_d
                                else:
                                    data_dict[line['daily']][loai_3][giai_3_d][so_dt_3_d] = st_3_d
                            else:
                                data_dict[line['daily']][loai_3][giai_3_d] = {so_dt_3_d: st_3_d}
                        else:
                            data_dict[line['daily']][loai_3] = {giai_3_d: {so_dt_3_d: st_3_d}}
                    else:
                        data_dict[line['daily']] = {loai_3: {giai_3_d: {so_dt_3_d: st_3_d}}}  
                if line['so_dt_3_c'] and line['sl_3_c']:
                    loai_3  = '3_so'
                    giai_3_c = 'cuoi'
                    so_dt_3_c = line['so_dt_3_c']
                    st_3_c = line['sl_3_c']*int(product.list_price)
                    if data_dict.get(line['daily'], False):
                        if data_dict[line['daily']].get(loai_3, False):
                            if data_dict[line['daily']][loai_3].get(giai_3_c, False):
                                if data_dict[line['daily']][loai_3][giai_3_c].get(so_dt_3_c, False):
                                    data_dict[line['daily']][loai_3][giai_3_c][so_dt_3_c] += st_3_c
                                else:
                                    data_dict[line['daily']][loai_3][giai_3_c][so_dt_3_c] = st_3_c
                            else:
                                data_dict[line['daily']][loai_3][giai_3_c] = {so_dt_3_c: st_3_c}
                        else:
                            data_dict[line['daily']][loai_3] = {giai_3_c: {so_dt_3_c: st_3_c}}
                    else:
                        data_dict[line['daily']] = {loai_3: {giai_3_c: {so_dt_3_c: st_3_c}}}
                if line['so_dt_3_dc'] and line['sl_3_dc']:
                    loai_3  = '3_so'
                    giai_3_dc = 'dau_cuoi'
                    so_dt_3_dc = line['so_dt_3_dc']
                    st_3_dc = line['sl_3_dc']*int(product.list_price)
                    if data_dict.get(line['daily'], False):
                        if data_dict[line['daily']].get(loai_3, False):
                            if data_dict[line['daily']][loai_3].get(giai_3_dc, False):
                                if data_dict[line['daily']][loai_3][giai_3_dc].get(so_dt_3_dc, False):
                                    data_dict[line['daily']][loai_3][giai_3_dc][so_dt_3_dc] += st_3_dc
                                else:
                                    data_dict[line['daily']][loai_3][giai_3_dc][so_dt_3_dc] = st_3_dc
                            else:
                                data_dict[line['daily']][loai_3][giai_3_dc] = {so_dt_3_dc: st_3_dc}
                        else:
                            data_dict[line['daily']][loai_3] = {giai_3_dc: {so_dt_3_dc: st_3_dc}}
                    else:
                        data_dict[line['daily']] = {loai_3: {giai_3_dc: {so_dt_3_dc: st_3_dc}}}
                         
                if line['so_dt_3_7'] and line['sl_3_7']:
                    loai_3  = '3_so'
                    giai_3_7 = '7_lo'
                    so_dt_3_7 = line['so_dt_3_7']
                    st_3_7 = line['sl_3_7']*int(product.list_price)
                    if data_dict.get(line['daily'], False):
                        if data_dict[line['daily']].get(loai_3, False):
                            if data_dict[line['daily']][loai_3].get(giai_3_7, False):
                                if data_dict[line['daily']][loai_3][giai_3_7].get(so_dt_3_7, False):
                                    data_dict[line['daily']][loai_3][giai_3_7][so_dt_3_7] += st_3_7
                                else:
                                    data_dict[line['daily']][loai_3][giai_3_7][so_dt_3_7] = st_3_7
                            else:
                                data_dict[line['daily']][loai_3][giai_3_7] = {so_dt_3_7: st_3_7}
                        else:
                            data_dict[line['daily']][loai_3] = {giai_3_7: {so_dt_3_7: st_3_7}}
                    else:
                        data_dict[line['daily']] = {loai_3: {giai_3_7: {so_dt_3_7: st_3_7}}}
                if line['so_dt_3_17'] and line['sl_3_17']:
                    loai_3  = '3_so'
                    giai_3_17 = '17_lo'
                    so_dt_3_17 = line['so_dt_3_17']
                    st_3_17 = line['sl_3_17']*int(product.list_price)
                    if data_dict.get(line['daily'], False):
                        if data_dict[line['daily']].get(loai_3, False):
                            if data_dict[line['daily']][loai_3].get(giai_3_17, False):
                                if data_dict[line['daily']][loai_3][giai_3_17].get(so_dt_3_17, False):
                                    data_dict[line['daily']][loai_3][giai_3_17][so_dt_3_17] += st_3_17
                                else:
                                    data_dict[line['daily']][loai_3][giai_3_17][so_dt_3_17] = st_3_17
                            else:
                                data_dict[line['daily']][loai_3][giai_3_17] = {so_dt_3_17: st_3_17}
                        else:
                            data_dict[line['daily']][loai_3] = {giai_3_17: {so_dt_3_17: st_3_17}}
                    else:
                        data_dict[line['daily']] = {loai_3: {giai_3_17: {so_dt_3_17: st_3_17}}}
                    
                if line['so_dt_4_16'] and line['sl_4_16']:
                    loai_4  = '4_so'
                    giai_4_16 = '16_lo'
                    so_dt_4_16 = line['so_dt_4_16']
                    st_4_16 = line['sl_4_16']*int(product.list_price)
                    if data_dict.get(line['daily'], False):
                        if data_dict[line['daily']].get(loai_4, False):
                            if data_dict[line['daily']][loai_4].get(giai_4_16, False):
                                if data_dict[line['daily']][loai_4][giai_4_16].get(so_dt_4_16, False):
                                    data_dict[line['daily']][loai_4][giai_4_16][so_dt_4_16] += st_4_16
                                else:
                                    data_dict[line['daily']][loai_4][giai_4_16][so_dt_4_16] = st_4_16
                            else:
                                data_dict[line['daily']][loai_4][giai_4_16] = {so_dt_4_16: st_4_16}
                        else:
                            data_dict[line['daily']][loai_4] = {giai_4_16: {so_dt_4_16: st_4_16}}
                    else:
                        data_dict[line['daily']] = {loai_4: {giai_4_16: {so_dt_4_16: st_4_16}}}
            muctran_obj = self.pool.get('muc.tran')
            muctran_ids = muctran_obj.search(cr, uid, [])
            mt = muctran_obj.browse(cr, uid, muctran_ids)
            for line in mt:
                data_muctran_dict = {'mt_2_d': line.mt_2_d,
                                    'mt_2_c': line.mt_2_c,
                                    'mt_2_dc': line.mt_2_dc,
                                    'mt_2_18': line.mt_2_18,
                                    'mt_3_d': line.mt_3_d,
                                    'mt_3_c': line.mt_3_c,
                                    'mt_3_dc': line.mt_3_dc,
                                    'mt_3_7': line.mt_3_7,
                                    'mt_3_17': line.mt_3_17,
                                    'mt_4_16': line.mt_4_16
                                    }
            if data_dict:
                for daily, daily_vals in data_dict.iteritems():
                    for loai, loai_vals in daily_vals.iteritems():
                        for giai, giai_vals in loai_vals.iteritems():
                            for so_dt, sotien  in giai_vals.iteritems():
                                vuot_tran_vals = {
                                    'dai_ly_id': daily,
                                    'loai': loai,
                                    'lo_du_thuong': giai,
                                    'so_du_thuong': so_dt,
                                    'thanh_tien': sotien,
                                    'vuot_tran_id': record.id,
                                    'data_muctran':json.dumps(data_muctran_dict)
                                }
                                self.pool.get('vuot.tran.line').create(cr,uid,vuot_tran_vals)
    
    
    def _check_ngay_xs(self, cr, uid, ids, context=None):
        for action in self.browse(cr, uid, ids, context=context):
            sql = '''
                select vt.ngay_xs
                from vuot_tran vt
            '''
            cr.execute(sql)
            res = cr.fetchone()
            ngay = res and res[0] or 0 
            if action.ngay_xs in ngay:
                return False
        return True

    _constraints = [
        (_check_ngay_xs, ('Ngày xổ số đã được tạo trước đó!'), ['ngay_xs'])]
    
vuot_tran()

class vuot_tran_line(osv.osv):
    _name = "vuot.tran.line"
    _order = 'kt_vt desc, thanh_tien desc'
    
    def _kt_vt(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        kt_vt = False
        for record in self.browse(cr, uid, ids, context=context):
            res[record.id] =False
            muctran = json.loads(record.data_muctran)
            if record.data_muctran and record.data_muctran != '{}':
                if record.loai == '2_so' and record.lo_du_thuong == 'dau' and record.thanh_tien > muctran['mt_2_d']:
                    res[record.id] = True
                if record.loai == '2_so' and record.lo_du_thuong == 'cuoi'and record.thanh_tien > muctran['mt_2_c']:
                    res[record.id] = True
                if record.loai == '2_so' and record.lo_du_thuong == 'dau_cuoi' and record.thanh_tien > muctran['mt_2_dc']:
                    res[record.id] = True
                if record.loai == '2_so' and record.lo_du_thuong == 'cuoi' and record.thanh_tien > muctran['mt_2_dc']:
                    res[record.id] = True
                if record.loai == '2_so' and record.lo_du_thuong == '18_lo' and record.thanh_tien > muctran['mt_2_18']:
                    res[record.id] = True
                if record.loai == '3_so' and record.lo_du_thuong == 'dau' and record.thanh_tien > muctran['mt_3_d']:
                    res[record.id] = True
                if record.loai == '3_so' and record.lo_du_thuong == 'cuoi' and record.thanh_tien > muctran['mt_3_c']:
                    res[record.id] = True
                if record.loai == '3_so' and record.lo_du_thuong == 'dau_cuoi' and record.thanh_tien > muctran['mt_3_dc']:
                    res[record.id] = True
                if record.loai == '3_so' and record.lo_du_thuong == '7_lo' and record.thanh_tien > muctran['mt_3_7']:
                    res[record.id] = True
                if record.loai == '3_so' and record.lo_du_thuong == '17_lo' and record.thanh_tien > muctran['mt_3_17']:
                    res[record.id] = True
                if record.loai == '4_so' and record.lo_du_thuong == '16_lo' and record.thanh_tien > muctran['mt_4_16']:
                    res[record.id] = True
        return res
#             data_muctran_dict = []
#             data_muctran_vals ={}
#             if record.data_muctran and record.data_muctran != '{}':
#                 for key, value in json.loads(record.data_muctran).iteritems():
#                     data_muctran_vals[key] = value['value']
#                 data_muctran_dict.append(data_muctran_vals)
    _columns = {
        'vuot_tran_id': fields.many2one('vuot.tran','Vượt trần', ondelete='cascade'),
        'dai_ly_id': fields.many2one('res.partner', 'Đại lý'),
        'loai':fields.selection([('2_so','2 số'),('3_so','3 số'),('4_so','4 số')],'Loại'),
        'lo_du_thuong': fields.selection([('dau','Đầu'),
                                          ('cuoi','Cuối'),
                                          ('dau_cuoi','Đầu Cuối'),
                                          ('18_lo','18 Lô'),
                                          ('7_lo','7 Lô'),
                                          ('17_lo','17 Lô'),
                                          ('16_lo','16 Lô')],'Lô dự thưởng'),
        'so_du_thuong': fields.char('Số dự thưởng'),
        'thanh_tien': fields.float('Thành tiền',digits=(16,0)),
        'kt_vt':fields.function(_kt_vt, string='Vượt trần', type='boolean', store=True),
        'data_muctran': fields.text('Data cấu hình mức trần')
        }

vuot_tran_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: