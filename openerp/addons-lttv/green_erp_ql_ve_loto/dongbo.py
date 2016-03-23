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
DATE_FORMAT = "%Y-%m-%d"
from openerp.addons.green_erp_base.common.oorpc import OpenObjectRPC

class res_company(osv.osv):
    _inherit = "res.company"
    _columns = {
        'web_url': fields.char('Url', size=256),
        'web_port': fields.integer('Port'),
        'web_db_name': fields.char('Database', size=64),
        'web_user': fields.char('Username', size=64),
        'web_pass': fields.char('Password', size=64),
        'db_url': fields.char('Url', size=256),
        'db_port': fields.integer('Port'),
        'db_name': fields.char('Database', size=64),
        'db_user': fields.char('Username', size=64),
        'db_pass': fields.char('Password', size=64),
    }
    def connect_web_service(self, cr, uid, company_id, context=None):
        line = self.browse(cr, uid, company_id)
        web_url = line.web_url
        web_port = line.web_port
        web_db_name = line.web_db_name
        web_user = line.web_user
        web_pass = line.web_pass
        if web_url and web_port and web_db_name and web_user and web_pass:
            try:
                oorpc = OpenObjectRPC(web_url,web_db_name,web_user,web_pass,web_port)
            except Exception:
                oorpc = False
        else:
            oorpc = False
        return oorpc
    
    def connect_database(self, cr, uid, company_id, context=None):
        line = self.browse(cr, uid, company_id)
        db_url = line.db_url
        db_port = line.db_port
        db_name = line.db_name
        db_user = line.db_user
        db_pass = line.db_pass
        if db_url and db_port and db_name and db_user and db_pass:
            try:
                db_conn_string = "host='%s' port='%s' dbname='%s' user='%s' password='%s'"%(db_url,db_port,db_name,db_user,db_pass)
            except Exception:
                db_conn_string = False
        else:
            db_conn_string = False
        return db_conn_string
    
res_company()

class lichsu_dongbo(osv.osv):
    _name = "lichsu.dongbo"
    _order = 'create_date, priority'
    _columns = {
        'create_date': fields.datetime('Ngày tạo'),
        'create_uid': fields.many2one('res.users','Người tạo'),
        
        'priority': fields.integer('Độ ưu tiên'),
        'update_fields': fields.text('Trường dữ liệu'),
        'f_table': fields.char('Bảng', size=128),
        'f_object': fields.char('Đối tượng', size=128),
        'f_id': fields.integer('ID'),
        'company_id': fields.integer('Cơ quan ID'),
        'message': fields.text('Ghi chú'),
        'type': fields.selection([('create','Tạo'),('write','Sửa'),('unlink','Xóa')], 'Sự kiện'),
        'state': fields.selection([('waiting','Waiting'),('error','Error'),('done','Done')], 'Trạng thái'),
    }
    
    def create(self, cr, uid, values, context=None):
        if values.get('type',False):
            if values['type']=='create':
                values.update({'priority':1})
            if values['type']=='write':
                values.update({'priority':2})
            if values['type']=='unlink':
                values.update({'priority':3})
        return super(lichsu_dongbo, self).create(cr, uid, values, context)
    
    def dongbo_dulieu_ve_trungtam(self, cr, uid, context=None):
        context = context or {}
        company_obj = self.pool.get('res.company')
        company = self.pool.get('res.users').browse(cr, uid, uid).company_id
        sql='''
                SELECT id,f_table,f_object,f_id,update_fields,company_id,type
                FROM lichsu_dongbo
                WHERE state in ('waiting','error')
                ORDER BY priority,f_table,f_id
            '''
        cr.execute(sql)
        res = cr.dictfetchall()
        try:
            for line in res:
                oorpc = company_obj.connect_web_service(cr, uid, line['company_id'])
                if oorpc:
                    if line['type']=='create':
                        sql = '''
                            SELECT * FROM %s WHERE id=%s
                        '''%(line['f_table'],line['f_id'])
                        cr.execute(sql)
                        create_vals = cr.dictfetchone() or False
                        if create_vals:
                            for key in ('id','create_uid','create_date','write_date','write_uid','external_id'):
                                create_vals.pop(key)
                            for val in create_vals:
                                if create_vals[val]==None:
                                    create_vals.update({val:False})
                            try:
                                create_id = oorpc.create(line['f_object'], create_vals,context)
                                if create_id:
                                    sql='''
                                        UPDATE %s SET external_id=%s WHERE id=%s 
                                    '''%(line['f_table'],create_id,line['f_id'])
                                    cr.execute(sql)
                                sql='''
                                    UPDATE lichsu_dongbo SET state='done',message='' WHERE id=%s 
                                '''%(line['id'])
                                cr.execute(sql)
                            except Exception, e:
                                sql='''
                                    UPDATE lichsu_dongbo SET state='error',message='%s' WHERE id=%s 
                                '''%(str(e).replace("'",""),line['id'])
                                cr.execute(sql)
                    if line['type']=='write':
                        sql = '''
                            SELECT %s FROM %s WHERE id=%s
                        '''%(line['update_fields'],line['f_table'],line['f_id'])
                        cr.execute(sql)
                        write_vals = cr.dictfetchone() or False
                        if write_vals:
                            try:
                                write_id = self.pool.get(line['f_object']).browse(cr, uid, line['f_id']).external_id
                                if line['f_object'] == 've.loto':
                                    for line2 in self.pool.get(line['f_object']).browse(cr, uid, line['f_id']).ve_loto_2_line:
                                        loto_line_ids = oorpc.search('ve.loto.line',[('ve_loto_id','=',write_id)])
                                        oorpc.delete('ve.loto.line',loto_line_ids)
                                        vals = {
                                            'name': line2.name,
                                            'so_dt_2_d': line2.so_dt_2_d,
                                            'sl_2_d': line2.sl_2_d,
                                            'sl_2_d_trung': line2.sl_2_d_trung,
                                            'so_dt_2_c': line2.so_dt_2_c,
                                            'sl_2_c': line2.sl_2_c,
                                            'sl_2_c_trung': line2.sl_2_c_trung,
                                            'so_dt_2_dc': line2.so_dt_2_dc,
                                            'sl_2_dc': line2.sl_2_dc,
                                            'sl_2_dc_trung': line2.sl_2_dc_trung,
                                            'so_dt_2_18': line2.so_dt_2_18,
                                            'sl_2_18': line2.sl_2_18,
                                            'sl_2_18_trung': line2.sl_2_18_trung,
                                            'so_dt_3_d': line2.so_dt_3_d,
                                            'sl_3_d': line2.sl_3_d,
                                            'sl_3_d_trung': line2.sl_3_d_trung,
                                            'so_dt_3_c': line2.so_dt_3_c,
                                            'sl_3_c': line2.sl_3_c,
                                            'sl_3_c_trung': line2.sl_3_c_trung,
                                            'so_dt_3_dc': line2.so_dt_3_dc,
                                            'sl_3_dc': line2.sl_3_dc,
                                            'sl_3_dc_trung': line2.sl_3_dc_trung,
                                            'so_dt_3_7': line2.so_dt_3_7,
                                            'sl_3_7': line2.sl_3_7,
                                            'sl_3_7_trung': line2.sl_3_7_trung,
                                            'so_dt_3_17': line2.so_dt_3_17,
                                            'sl_3_17': line2.sl_3_17,
                                            'sl_3_17_trung': line2.sl_3_17_trung,
                                            'so_dt_4_16': line2.so_dt_4_16,
                                            'sl_4_16': line2.sl_4_16,
                                            'sl_4_16_trung': line2.sl_4_16_trung,
                                            've_loto_id': write_id,
                                        }
                                        oorpc.create('ve.loto.line',vals)
                                oorpc.write(line['f_object'],[write_id], write_vals,context)
                                sql='''
                                    UPDATE lichsu_dongbo SET state='done',message='' WHERE id=%s 
                                '''%(line['id'])
                                cr.execute(sql)
                            except Exception, e:
                                sql='''
                                    UPDATE lichsu_dongbo SET state='error',message='%s' WHERE id=%s 
                                '''%(str(e).replace("'",""),line['id'])
                                cr.execute(sql)
                    if line['type']=='unlink':
                        try:
                            oorpc.delete(line['f_object'],[line['f_id']],context)
                            sql='''
                                UPDATE lichsu_dongbo SET state='done',message='' WHERE id=%s 
                            '''%(line['id'])
                            cr.execute(sql)
                        except Exception, e:
                            sql='''
                                UPDATE lichsu_dongbo SET state='error',message='%s' WHERE id=%s 
                            '''%(str(e).replace("'",""),line['id'])
                            cr.execute(sql)
        except Exception, e:
            print e
        return True
lichsu_dongbo()

class dongbo_veloto(osv.osv):
    _name = "dongbo.veloto"
    _columns = {
        'name': fields.datetime('Ngày tạo'),
        'ket_qua_id': fields.many2one('ketqua.xoso','Kết quả xổ số'),
        'state': fields.selection([('waiting','Waiting'),('error','Error'),('done','Done')], 'Trạng thái'),
    }
    
    def dongbo_veloto(self, cr, uid, ids,context=None):
        context = context or {}
        company_obj = self.pool.get('res.company')
        company = self.pool.get('res.users').browse(cr, uid, uid).company_id
        try:
#             dongbo_ids = self.search(cr, uid, [('state','in',['waiting','error'])])
            for line in self.browse(cr, uid, ids):
                oorpc = company_obj.connect_web_service(cr, uid, company.id)
                if oorpc:
                    ket_qua_id = oorpc.search('ketqua.xoso',[('name','=',line['name'])])
                    if not ket_qua_id:
                        line_vals = []
                        for ketqua_line in line.ket_qua_id.ketqua_xoso_line:
                            line_vals.append((0,0,{
                                'name': ketqua_line.name,
                                'ma': ketqua_line.ma,
                                'so': ketqua_line.so,
                                'dm_7_so': ketqua_line.dm_7_so,
                            }))
                        vals = {
                            'name': line.ket_qua_id.name,
                            'dai_duthuong_id': line.ket_qua_id.dai_duthuong_id.external_id,
                            'state': line.ket_qua_id.state,
                            'ketqua_xoso_line': line_vals,
                        }
                        ket_qua_id = oorpc.create('ketqua.xoso',vals)
                        if ket_qua_id:
                            sql='''
                                UPDATE ketqua_xoso SET external_id=%s WHERE id=%s 
                            '''%(ket_qua_id,line.ket_qua_id.id)
                            cr.execute(sql)
                    if ket_qua_id:
                        ve_loto_obj = self.pool.get('ve.loto')
                        ve_loto_ids = ve_loto_obj.search(cr, uid, [('ngay','=',line.ket_qua_id.name),('state','=','done')])
                        for ve_loto in ve_loto_obj.browse(cr, uid, ve_loto_ids):
                            line_loto_vals = []
                            for loto_line in ve_loto.ve_loto_2_line:
                                line_loto_vals.append((0,0,{
                                    'name': loto_line.name,
                                    'so_dt_2_d': loto_line.so_dt_2_d,
                                    'sl_2_d': loto_line.sl_2_d,
                                    'sl_2_d_trung': loto_line.sl_2_d_trung,
                                    'so_dt_2_c': loto_line.so_dt_2_c,
                                    'sl_2_c': loto_line.sl_2_c,
                                    'sl_2_c_trung': loto_line.sl_2_c_trung,
                                    'so_dt_2_dc': loto_line.so_dt_2_dc,
                                    'sl_2_dc': loto_line.sl_2_dc,
                                    'sl_2_dc_trung': loto_line.sl_2_dc_trung,
                                    'so_dt_2_18': loto_line.so_dt_2_18,
                                    'sl_2_18': loto_line.sl_2_18,
                                    'sl_2_18_trung': loto_line.sl_2_18_trung,
                                    'so_dt_3_d': loto_line.so_dt_3_d,
                                    'sl_3_d': loto_line.sl_3_d,
                                    'sl_3_d_trung': loto_line.sl_3_d_trung,
                                    'so_dt_3_c': loto_line.so_dt_3_c,
                                    'sl_3_c': loto_line.sl_3_c,
                                    'sl_3_c_trung': loto_line.sl_3_c_trung,
                                    'so_dt_3_dc': loto_line.so_dt_3_dc,
                                    'sl_3_dc': loto_line.sl_3_dc,
                                    'sl_3_dc_trung': loto_line.sl_3_dc_trung,
                                    'so_dt_3_7': loto_line.so_dt_3_7,
                                    'sl_3_7': loto_line.sl_3_7,
                                    'sl_3_7_trung': loto_line.sl_3_7_trung,
                                    'so_dt_3_17': loto_line.so_dt_3_17,
                                    'sl_3_17': loto_line.sl_3_17,
                                    'sl_3_17_trung': loto_line.sl_3_17_trung,
                                    'so_dt_4_16': loto_line.so_dt_4_16,
                                    'sl_4_16': loto_line.sl_4_16,
                                    'sl_4_16_trung': loto_line.sl_4_16_trung,
                                }))
                            loto_vals = {
                                'name': ve_loto.name,
                                'daily_id': ve_loto.daily_id.external_id,
                                'ngay': ve_loto.ngay,
                                'so_chungtu': ve_loto.so_chungtu,
                                'product_id': ve_loto.product_id.external_id,
                                'ky_ve_id': ve_loto.ky_ve_id.external_id,
                                'sophieu': ve_loto.sophieu,
                                'tong_cong': ve_loto.tong_cong,
                                'tong_sai_kythuat': ve_loto.tong_sai_kythuat,
                                'thanh_tien': ve_loto.thanh_tien,
                                've_loto_2_line': line_loto_vals,
                                'state': ve_loto.state,
                            }
                            loto_id = oorpc.create('ve.loto',loto_vals)
                            if loto_id:
                                sql='''
                                    UPDATE ve_loto SET external_id=%s WHERE id=%s 
                                '''%(loto_id,ve_loto.id)
                                cr.execute(sql)
                                
                        sql='''
                            UPDATE dongbo_veloto SET state='done' WHERE id=%s 
                        '''%(line.id)
                        cr.execute(sql)
                            
        except Exception, e:
            print e
        return True
    
    def dongbo(self, cr, uid, ids, context=None):
        self.dongbo_veloto(cr, uid,ids, context)
        return True
    
    def dongbo_veloto_ve_trungtam(self, cr, uid, context=None):
        context = context or {}
        company_obj = self.pool.get('res.company')
        company = self.pool.get('res.users').browse(cr, uid, uid).company_id
        try:
            dongbo_ids = self.search(cr, uid, [('state','in',['waiting','error'])])
            self.dongbo_veloto(cr, uid, dongbo_ids)
        except Exception, e:
            print e
        return True
    
dongbo_veloto()
    
class dongbo_daily_trungthuong(osv.osv):
    _name = "dongbo.daily.trungthuong"
    _columns = {
        'name': fields.datetime('Ngày tạo'),
        'ket_qua_id': fields.many2one('ketqua.xoso','Kết quả xổ số'),
        'state': fields.selection([('waiting','Waiting'),('error','Error'),('done','Done')], 'Trạng thái'),
    }
    
    def get_val_trung(self, ve_loto):
        vals = []
        for line in ve_loto.ve_loto_2_line:
            #2 so
            gt_menhgia = int(ve_loto.product_id.list_price)/10000
            if line.sl_2_d_trung:
                slan_trung = line.sl_2_d_trung
                sluong_trung = line.sl_2_d
                thanhtien = (700000*gt_menhgia)
                vals.append({
                    'name': (line.so_dt_2_d),
                    'product_id': ve_loto.product_id.id,
                    'sl_trung': sluong_trung,
                    'slan_trung': slan_trung,
                    'loai': '2_so',
                    'giai': 'dau',
                    'tong_tien': thanhtien,
                })
            if line.sl_2_c_trung:
                slan_trung = line.sl_2_c_trung
                sluong_trung = line.sl_2_c
                thanhtien = (700000*gt_menhgia)
                vals.append({
                    'name': (line.so_dt_2_c),
                    'product_id': ve_loto.product_id.id,
                    'sl_trung': sluong_trung,
                    'slan_trung': slan_trung,
                    'loai': '2_so',
                    'giai': 'cuoi',
                    'tong_tien': thanhtien,
                })
            if line.sl_2_dc_trung:
                slan_trung = line.sl_2_dc_trung
                sluong_trung = line.sl_2_dc
                thanhtien = (350000*gt_menhgia)
                vals.append({
                    'name': (line.so_dt_2_dc),
                    'product_id': ve_loto.product_id.id,
                    'sl_trung': sluong_trung,
                    'slan_trung': slan_trung,
                    'loai': '2_so',
                    'giai': 'dau_cuoi',
                    'tong_tien': thanhtien,
                })
            if line.sl_2_18_trung:
                slan_trung = line.sl_2_18_trung
                sluong_trung = line.sl_2_18
                thanhtien = (39000*gt_menhgia)
                vals.append({
                    'name': (line.so_dt_2_18),
                    'product_id': ve_loto.product_id.id,
                    'sl_trung': sluong_trung,
                    'slan_trung': slan_trung,
                    'loai': '2_so',
                    'giai': '18_lo',
                    'tong_tien': thanhtien,
                })
                
            # 3 so
            if line.sl_3_d_trung:
                slan_trung = line.sl_3_d_trung
                sluong_trung = line.sl_3_d
                thanhtien = (5000000*gt_menhgia)
                vals.append({
                    'name': (line.so_dt_3_d),
                    'product_id': ve_loto.product_id.id,
                    'sl_trung': sluong_trung,
                    'slan_trung': slan_trung,
                    'loai': '3_so',
                    'giai': 'dau',
                    'tong_tien': thanhtien,
                })
            if line.sl_3_c_trung:
                slan_trung = line.sl_3_c_trung
                sluong_trung = line.sl_3_c
                thanhtien = (5000000*gt_menhgia)
                vals.append({
                    'name': (line.so_dt_3_c),
                    'product_id': ve_loto.product_id.id,
                    'sl_trung': sluong_trung,
                    'slan_trung': slan_trung,
                    'loai': '3_so',
                    'giai': 'cuoi',
                    'tong_tien': thanhtien,
                })
            if line.sl_3_dc_trung:
                slan_trung = line.sl_3_dc_trung
                sluong_trung = line.sl_3_dc
                thanhtien = (2500000*gt_menhgia)
                vals.append({
                    'name': (line.so_dt_3_dc),
                    'product_id': ve_loto.product_id.id,
                    'sl_trung': sluong_trung,
                    'slan_trung': slan_trung,
                    'loai': '3_so',
                    'giai': 'dau_cuoi',
                    'tong_tien': thanhtien,
                })
            if line.sl_3_7_trung:
                slan_trung = line.sl_3_7_trung
                sluong_trung = line.sl_3_7
                thanhtien = (715000*gt_menhgia)
                vals.append({
                    'name': (line.so_dt_3_7),
                    'product_id': ve_loto.product_id.id,
                    'sl_trung': sluong_trung,
                    'slan_trung': slan_trung,
                    'loai': '3_so',
                    'giai': '7_lo',
                    'tong_tien': thanhtien,
                })
            if line.sl_3_17_trung:
                slan_trung = line.sl_3_17_trung
                sluong_trung = line.sl_3_17
                thanhtien = (295000*gt_menhgia)
                vals.append({
                    'name': (line.so_dt_3_17),
                    'product_id': ve_loto.product_id.id,
                    'sl_trung': sluong_trung,
                    'slan_trung': slan_trung,
                    'loai': '3_so',
                    'giai': '17_lo',
                    'tong_tien': thanhtien,
                })
            
            # 4 so
            if line.sl_4_16_trung:
                slan_trung = line.sl_4_16_trung
                sluong_trung = line.sl_4_16
                thanhtien = (2000000*gt_menhgia)
                vals.append({
                    'name': (line.so_dt_4_16),
                    'product_id': ve_loto.product_id.id,
                    'sl_trung': sluong_trung,
                    'slan_trung': slan_trung,
                    'loai': '4_so',
                    'giai': '16_lo',
                    'tong_tien': thanhtien,
                })
        return vals
        
    def dongbo_daily_trungthuong(self, cr, uid, ids,context=None):
        context = context or {}
        vals = {}
        try:
            for line in self.browse(cr, uid, ids):
                tra_thuong_obj = self.pool.get('tra.thuong')
                ve_loto_obj = self.pool.get('ve.loto')
                daily_obj = self.pool.get('res.partner')
                daily_ids = daily_obj.search(cr, 1, [('dai_ly','=',True)])
                for daily in daily_obj.browse(cr, 1, daily_ids):
                    ve_loto_ids = ve_loto_obj.search(cr, 1, [('ngay','=',line.ket_qua_id.name),('daily_id','=',daily.id),('state','=','done')])
                    linevals = []
                    for ve_loto in ve_loto_obj.browse(cr, 1, ve_loto_ids):
                        val_trung = self.get_val_trung(ve_loto)
                        for val in val_trung:
                            linevals.append((0,0,val))
                    if linevals:
                        vals = {
                            'ngay': line.ket_qua_id.name,
                            'daily_id': daily.id,
                            'tra_thuong_line': linevals,
                        }
                        tra_thuong_obj.create(cr,1,vals)
                sql='''
                    UPDATE dongbo_daily_trungthuong SET state='done' WHERE id=%s 
                '''%(line.id)
                cr.execute(sql)
        except Exception, e:
            print e
        return True
    
    def dongbo(self, cr, uid, ids, context=None):
        self.dongbo_daily_trungthuong(cr, uid,ids, context)
        return True
    
    
dongbo_daily_trungthuong()

