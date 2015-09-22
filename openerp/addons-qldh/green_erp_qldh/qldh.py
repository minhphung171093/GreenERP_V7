# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
from openerp import SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from datetime import datetime
import time
from datetime import date
from datetime import timedelta
from datetime import datetime
import calendar
import openerp.addons.decimal_precision as dp
import codecs
import os
# from xlrd import open_workbook,xldate_as_tuple
from openerp import modules
base_path = os.path.dirname(modules.get_module_path('green_erp_qldh_base'))

class nhom_cong_viec(osv.osv):
    _name = "nhom.cong.viec"
    _order = 'loai desc'
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(nhom_cong_viec, self).default_get(cr, uid, fields, context)
        cong_viec_con_id = context.get('default_cong_viec_con_id',False)
        if cong_viec_con_id:
            cong_viec_con = self.browse(cr, uid, cong_viec_con_id)
            if cong_viec_con.cong_viec_id:
                res.update({'nhom_cv_id':cong_viec_con.cong_viec_id and cong_viec_con.cong_viec_id.id or False})
            if cong_viec_con.nhom_cv_pc_id:
                res.update({'nhom_cv_id':cong_viec_con.nhom_cv_pc_id and cong_viec_con.nhom_cv_pc_id.id or False,
                            'cv_tg_id': cong_viec_con.cong_viec_pc_id and cong_viec_con.cong_viec_pc_id.id or False,})
        
        cong_viec_pc_id = context.get('default_cong_viec_pc_id',False)
        if cong_viec_pc_id:
            cong_viec_pc = self.browse(cr, uid, cong_viec_pc_id)
            res.update({'nhom_cv_pc_id':cong_viec_pc.phan_cong_phong_ban_id and cong_viec_pc.phan_cong_phong_ban_id.id or False})
        return res
    
    def _data_get(self, cr, uid, ids, name, arg, context=None):
        if context is None:
            context = {}
        result = {}
        location = self.pool.get('ir.config_parameter').get_param(cr, SUPERUSER_ID, 'ir_attachment.location')
        bin_size = context.get('bin_size')
        for attach in self.browse(cr, uid, ids, context=context):
            if location and attach.store_fname:
                result[attach.id] = self._file_read(cr, uid, location, attach.store_fname, bin_size)
            else:
                result[attach.id] = attach.db_datas
                if bin_size:
                    result[attach.id] = int(result[attach.id])

        return result

    def _data_set(self, cr, uid, id, name, value, arg, context=None):
        # We dont handle setting data to null
        if not value:
            return True
        if context is None:
            context = {}
        location = self.pool.get('ir.config_parameter').get_param(cr, SUPERUSER_ID, 'ir_attachment.location')
        file_size = len(value.decode('base64'))
        if location:
            attach = self.browse(cr, uid, id, context=context)
            if attach.store_fname:
                self._file_delete(cr, uid, location, attach.store_fname)
            fname = self._file_write(cr, uid, location, value)
            # SUPERUSER_ID as probably don't have write access, trigger during create
            super(ct_nhom_cong_viec, self).write(cr, SUPERUSER_ID, [id], {'store_fname': fname, 'file_size': file_size}, context=context)
        else:
            super(ct_nhom_cong_viec, self).write(cr, SUPERUSER_ID, [id], {'db_datas': value, 'file_size': file_size}, context=context)
        return True
    
    _columns = {
        'name':fields.char('Tên nhóm công việc',size=1024,required=True),
        'phong_ban_id':fields.many2one('phong.ban','Phòng ban'),
        'ho_tro':fields.selection([('co','Có'),('khong','Không')],'Hỗ trợ'),
        'phong_ban_ids': fields.many2many('phong.ban','phong_ban_nhom_cv_ref','nhom_cv_id','phong_ban_id','Phòng ban hỗ trợ' ),
        'quy_trinh_id':fields.many2one('quy.trinh','Quy trình'),
        'state':fields.selection([('nhap','Nháp'),
                                  ('da_giao','Đã giao'),
                                  ('da_nhan','Đã nhận'),
                                  ('dang_lam','Đang làm'),
                                  ('cho_duyet','Chờ phê duyệt'),
                                  ('duyet','Đã duyệt')],'Trạng thái'),
        'loai':fields.selection([('1_nhom_cv','Nhóm công việc'),
                                 ('3_cv','Công việc'),
                                 ('4_cv_con','Công việc con'),
                                 ('2_nhom_cv_tg','Nhóm công việc TG'),
                                 ('5_ct_th','Chi tiết thực hiện')],'Loại'),
        'ct_nhom_cv_line':fields.one2many('ct.nhom.cong.viec','nhom_cv_id','Chi tiết công việc'),
        'cong_viec_id':fields.many2one('nhom.cong.viec','Nhóm công việc'),
        'nhom_cv_id': fields.many2one('nhom.cong.viec','Nhóm công việc'),
        'cv_tg_id': fields.many2one('nhom.cong.viec','Công việc phân công PBHT'),
        'cong_viec_pc_line':fields.one2many('nhom.cong.viec','cong_viec_pc_id','Công việc'),
        'cong_viec_pc_id': fields.many2one('nhom.cong.viec','Công việc phân công'),
        'nhom_cv_pc_id': fields.many2one('nhom.cong.viec','Nhóm công việc'),
        'cong_viec_line':fields.one2many('nhom.cong.viec','cong_viec_id','Công việc'),
        'cong_viec_con_id':fields.many2one('nhom.cong.viec','Công việc'),
        'cong_viec_con_line':fields.one2many('nhom.cong.viec','cong_viec_con_id','Công việc con'),
        'phan_cong_phong_ban_id':fields.many2one('nhom.cong.viec','Nhóm công việc'),
        'phan_cong_phong_ban_line':fields.one2many('nhom.cong.viec','phan_cong_phong_ban_id','Phân công phòng ban'),
        'ghi_chu':fields.text('Ghi chú'),
        'nhan_vien_id':fields.many2one('nhan.vien','Nhân viên'),
        'nhan_vien_ids':fields.many2many('nhan.vien','nhan_vien_cong_viec_ids', 'cong_viec_id', 'nhan_vien_id', 'Nhân viên'),
        'trangthai_ncv': fields.selection([('xong','Xong'),
                                 ('chua_xong','Chưa Xong')],'TT_NCV'),
        'trangthai_cv': fields.selection([('xong','Xong'),
                                 ('chua_xong','Chưa Xong')],'TT_CV'),
        'trangthai_cvc': fields.selection([('xong','Xong'),
                                 ('chua_xong','Chưa Xong')],'TT_CVC'),
        'trangthai_cv_tg': fields.selection([('xong','Xong'),
                                 ('chua_xong','Chưa Xong')],'TT_CVTG'),
                
        'ct_th_nhom_cv_line':fields.one2many('nhom.cong.viec','ct_th_nhom_cv_id','CTTH Nhom Cong Viec'),
        'ct_th_cv_tg_line':fields.one2many('nhom.cong.viec','ct_th_cv_tg_id','CTTH Cong Viec Trung Gian'),
        'ct_th_cv_line':fields.one2many('nhom.cong.viec','ct_th_cv_id','CTTH Cong Viec'), 
        'ct_th_cv_con_line':fields.one2many('nhom.cong.viec','ct_th_cv_con_id','CTTH Cong Viec Con'), 
        'ct_th_nhom_cv_id':fields.many2one('nhom.cong.viec','nhom cong viec'),
        'ct_th_cv_tg_id':fields.many2one('nhom.cong.viec','cong viec trung gian'),
        'ct_th_cv_id':fields.many2one('nhom.cong.viec','cong viec'),
        'ct_th_cv_con_id':fields.many2one('nhom.cong.viec','cong viec con'),
        
        'datas_fname': fields.char('File Name',size=256),
        'datas': fields.function(_data_get, fnct_inv=_data_set, string='File Content', type="binary", nodrop=True),
        'store_fname': fields.char('Stored Filename', size=256),
        'db_datas': fields.binary('Database Data'),
        'file_size': fields.integer('File Size'),
        'yeu_cau_kq':fields.text('Yêu cầu kết quả'),
        'cach_thuc_hien':fields.text('Cách thức thực hiện'),
    }
    _defaults = {
            'ho_tro':'khong',   
            'trangthai_ncv': 'chua_xong', 
            'trangthai_cv': 'chua_xong', 
            'trangthai_cvc': 'chua_xong', 
            'trangthai_cv_tg': 'chua_xong',
                 }
    
    
    
    def _check_nhan_vien(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids, context=context):
            for nv in line.ct_nhom_cv_line:
                if not nv.nhan_vien_id and line.state in ['moi_nhan','cho_duyet','duyet'] :
                    raise osv.except_osv(_('Cảnh Báo!'),_('Cần chọn nhân viên cho công việc'))
                    return False
        return True
    _constraints = [
        (_check_nhan_vien, 'Identical Data', []),
    ]   
    def write(self, cr, uid, ids, vals, context=None):
        new_write = super(nhom_cong_viec, self).write(cr, uid,ids, vals, context)
        dem_line = 0
        dem_ht = 0
        for nhom_cv in self.browse(cr,uid,ids):
            if nhom_cv.loai=='5_ct_th':
                if vals and nhom_cv.state == 'da_nhan' :
                    if 'state' not in vals:
                        sql = '''
                            update nhom_cong_viec set state = 'dang_lam' where id = %s
                        '''%(nhom_cv.id)
                        cr.execute(sql)
                        
                        
                        if nhom_cv.ct_th_nhom_cv_id:
                            sql = '''
                                update nhom_cong_viec set state = 'dang_lam' where id = %s
                            '''%(nhom_cv.ct_th_nhom_cv_id.id)
                            cr.execute(sql)
                            
                        if nhom_cv.ct_th_cv_tg_id:
                            sql = '''
                                update nhom_cong_viec set state = 'dang_lam' where id = %s
                            '''%(nhom_cv.ct_th_cv_tg_id.id)
                            cr.execute(sql)
                            if nhom_cv.ct_th_cv_tg_id.phan_cong_phong_ban_id:
                                sql = '''
                                    update nhom_cong_viec set state = 'dang_lam' where id = %s
                                '''%(nhom_cv.ct_th_cv_tg_id.phan_cong_phong_ban_id.id)
                                cr.execute(sql)
                        
                        if nhom_cv.ct_th_cv_id:
                            sql = '''
                                update nhom_cong_viec set state = 'dang_lam' where id = %s
                            '''%(nhom_cv.ct_th_cv_id.id)
                            cr.execute(sql)
                            if nhom_cv.ct_th_cv_id.cong_viec_id:
                                sql = '''
                                    update nhom_cong_viec set state = 'dang_lam' where id = %s
                                '''%(nhom_cv.ct_th_cv_id.cong_viec_id.id)
                                cr.execute(sql)
                                
                        if nhom_cv.ct_th_cv_con_id:
                            sql = '''
                                update nhom_cong_viec set state = 'dang_lam' where id = %s
                            '''%(nhom_cv.ct_th_cv_con_id.id)
                            cr.execute(sql)
                            if nhom_cv.ct_th_cv_con_id.cong_viec_con_id:
                                sql = '''
                                    update nhom_cong_viec set state = 'dang_lam' where id = %s
                                '''%(nhom_cv.ct_th_cv_con_id.cong_viec_con_id.id)
                                cr.execute(sql)
                            if nhom_cv.ct_th_cv_con_id.nhom_cv_id:
                                sql = '''
                                    update nhom_cong_viec set state = 'dang_lam' where id = %s
                                '''%(nhom_cv.ct_th_cv_con_id.nhom_cv_id.id)
                                cr.execute(sql)
                            if nhom_cv.ct_th_cv_con_id.cv_tg_id:
                                sql = '''
                                    update nhom_cong_viec set state = 'dang_lam' where id = %s
                                '''%(nhom_cv.ct_th_cv_con_id.cv_tg_id.id)
                                cr.execute(sql)
                                
        return new_write    
    
    def bt_hoan_thanh_ctth(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids,{'state':'cho_duyet'})
    
    def bt_duyet_ctth(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids,{'state':'duyet'})
        dem_duyet = 0
        for nhom_cv in self.browse(cr,uid,ids):
            if nhom_cv.loai == '5_ct_th':
                if nhom_cv.ct_th_nhom_cv_id:
                    sql = '''
                        select state from nhom_cong_viec where ct_th_nhom_cv_id = %s and loai = '5_ct_th'
                    '''%(nhom_cv.ct_th_nhom_cv_id.id)
                    cr.execute(sql)
                    state_ids = cr.dictfetchall()
                    for state in state_ids:
                        if state['state']=='duyet':
                            dem_duyet += 1
                    if len(state_ids) != 0 and len(state_ids) == dem_duyet:
                        sql = '''
                            update nhom_cong_viec set trangthai_ncv = 'xong' where id = %s and loai = '1_nhom_cv'
                        '''%(nhom_cv.ct_th_nhom_cv_id.id)
                        cr.execute(sql)  
                        
                if nhom_cv.ct_th_cv_tg_id:
                    sql = '''
                        select state from nhom_cong_viec where ct_th_cv_tg_id = %s and loai = '5_ct_th'
                    '''%(nhom_cv.ct_th_cv_tg_id.id)
                    cr.execute(sql)
                    state_ids = cr.dictfetchall()
                    for state in state_ids:
                        if state['state']=='duyet':
                            dem_duyet += 1
                    if len(state_ids) != 0 and len(state_ids) == dem_duyet:
                        sql = '''
                            update nhom_cong_viec set trangthai_cv_tg = 'xong' where id = %s and loai = '2_nhom_cv_tg'
                        '''%(nhom_cv.ct_th_cv_tg_id.id)
                        cr.execute(sql)  
                        
                if nhom_cv.ct_th_cv_id:
                    sql = '''
                        select state from nhom_cong_viec where ct_th_cv_id = %s and loai = '5_ct_th'
                    '''%(nhom_cv.ct_th_cv_id.id)
                    cr.execute(sql)
                    state_ids = cr.dictfetchall()
                    for state in state_ids:
                        if state['state']=='duyet':
                            dem_duyet += 1
                    if len(state_ids) != 0 and len(state_ids) == dem_duyet:
                        sql = '''
                            update nhom_cong_viec set trangthai_cv = 'xong' where id = %s and loai = '3_cv'
                        '''%(nhom_cv.ct_th_cv_id.id)
                        cr.execute(sql)   
                
                if nhom_cv.ct_th_cv_con_id:
                    sql = '''
                        select state from nhom_cong_viec where ct_th_cv_con_id = %s and loai = '5_ct_th'
                    '''%(nhom_cv.ct_th_cv_con_id.id)
                    cr.execute(sql)
                    state_ids = cr.dictfetchall()
                    for state in state_ids:
                        if state['state']=='duyet':
                            dem_duyet += 1
                    if len(state_ids) != 0 and len(state_ids) == dem_duyet:
                        sql = '''
                            update nhom_cong_viec set trangthai_cvc = 'xong' where id = %s and loai = '4_cv_con'
                        '''%(nhom_cv.ct_th_cv_con_id.id)
                        cr.execute(sql)  
        return True
    
    def bt_hoan_thanh_ncv(self, cr, uid, ids, context=None):
        dem_cho_duyet = 0
        self.write(cr, uid, ids,{'state':'cho_duyet'})
        return True
    
    def bt_hoan_thanh_cv(self, cr, uid, ids, context=None):
        dem_cho_duyet = 0
        self.write(cr, uid, ids,{'state':'cho_duyet'})
        return True
    
    def bt_duyet_cv(self, cr, uid, ids, context=None):
        dem_cho_duyet = 0
        self.write(cr, uid, ids,{'state':'duyet'})
        for cv in self.browse(cr,uid,ids):
            if cv.loai == '3_cv':
                if cv.cong_viec_id:
                    sql = '''
                        select state from nhom_cong_viec where cong_viec_id = %s and loai = '3_cv'
                    '''%(cv.cong_viec_id.id)
                    cr.execute(sql)
                    state_ids = cr.dictfetchall()
                    for state in state_ids:
                        if state['state']=='duyet':
                            dem_cho_duyet += 1
                    if len(state_ids) != 0 and len(state_ids) == dem_cho_duyet:
                        sql = '''
                            update nhom_cong_viec set trangthai_ncv = 'xong' where id = %s and loai = '1_nhom_cv'
                        '''%(cv.cong_viec_id.id)
                        cr.execute(sql)   
                if cv.cong_viec_pc_id:
                    sql = '''
                        select state from nhom_cong_viec where cong_viec_pc_id = %s and loai = '3_cv'
                    '''%(cv.cong_viec_pc_id.id)
                    cr.execute(sql)
                    state_ids = cr.dictfetchall()
                    for state in state_ids:
                        if state['state']=='duyet':
                            dem_cho_duyet += 1
                    if len(state_ids) != 0 and len(state_ids) == dem_cho_duyet:
                        sql = '''
                            update nhom_cong_viec set trangthai_cv_tg = 'xong' where id = %s and loai = '2_nhom_cv_tg'
                        '''%(cv.cong_viec_pc_id.id)
                        cr.execute(sql)   
        return True
    
    def bt_hoan_thanh_cvc(self, cr, uid, ids, context=None):
        dem_cho_duyet = 0
        self.write(cr, uid, ids,{'state':'cho_duyet'})
        return True
    
    def bt_duyet_cvc(self, cr, uid, ids, context=None):
        dem_cho_duyet = 0
        self.write(cr, uid, ids,{'state':'duyet'})
        for cvc in self.browse(cr,uid,ids):
            if cvc.loai == '4_cv_con':
                sql = '''
                    select state from nhom_cong_viec where cong_viec_con_id = %s and loai = '4_cv_con'
                '''%(cvc.cong_viec_con_id.id)
                cr.execute(sql)
                state_ids = cr.dictfetchall()
                for state in state_ids:
                    if state['state']=='duyet':
                        dem_cho_duyet += 1
                if len(state_ids) != 0 and len(state_ids) == dem_cho_duyet:
                    sql = '''
                        update nhom_cong_viec set trangthai_cv = 'xong' where id = %s and loai = '3_cv'
                    '''%(cvc.cong_viec_con_id.id)
                    cr.execute(sql)   
        return True
    
    def bt_hoan_thanh_cv_tg(self, cr, uid, ids, context=None):
        dem_cho_duyet = 0
        self.write(cr, uid, ids,{'state':'cho_duyet'})
        return True
    
    def bt_duyet_cv_tg(self, cr, uid, ids, context=None):
        dem_cho_duyet = 0
        self.write(cr, uid, ids,{'state':'duyet'})
        for cv_tg in self.browse(cr,uid,ids):
            if cv_tg.loai == '2_nhom_cv_tg':
                sql = '''
                    select state from nhom_cong_viec where phan_cong_phong_ban_id = %s and loai = '2_nhom_cv_tg'
                '''%(cv_tg.phan_cong_phong_ban_id.id)
                cr.execute(sql)
                state_ids = cr.dictfetchall()
                for state in state_ids:
                    if state['state']=='duyet':
                        dem_cho_duyet += 1
                if len(state_ids) != 0 and len(state_ids) == dem_cho_duyet:
                    sql = '''
                        update nhom_cong_viec set trangthai_ncv = 'xong' where id = %s and loai = '1_nhom_cv'
                    '''%(cv_tg.phan_cong_phong_ban_id.id)
                    cr.execute(sql) 
        return True
    
    
    
    def bt_duyet_trinh_cv_con(self, cr, uid, ids, context=None):
        return True
    
    def bt_tao_ncv(self, cr, uid, ids, context=None):
        for ncv in self.browse(cr,uid,ids):
            if ncv.quy_trinh_id and ncv.loai == '1_nhom_cv':
                for ctth in ncv.ct_th_nhom_cv_line:
                    self.write(cr, uid, [ctth.id],{'state':'da_giao'})
                for phan_cong in ncv.phan_cong_phong_ban_line:
                    self.write(cr, uid, [ctth.id],{'state':'da_giao'})
        return self.write(cr, uid, ids,{'state':'da_giao'})
    
    def bt_nhan_ncv(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids,{'state':'da_nhan'})
    
    def bt_nhan_cv_pc(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids,{'state':'da_nhan'})
    
    def bt_nhan_cv(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids,{'state':'da_nhan'})
    
    def bt_nhan_cv_con(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids,{'state':'da_nhan'})
    
    def bt_nhan_cttth(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids,{'state':'da_nhan'})
    
    def bt_cho_duyet(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids,{'state':'duyet'})
    
    
    def bt_tao_cong_viec(self, cr, uid, ids, context=None):
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_qldh', 'cong_viec_tree')
        return {
                    'name': 'Công việc',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'view_id': res[1],
                    'res_model': 'nhom.cong.viec',
                    'domain': ['loai','=','3_cv'],
                    'context': {'default_loai': '3_cv', 'default_cong_viec_id':ids[0], 'default_state':'da_giao'},
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                }

    
    def onchange_quy_trinh_id(self, cr, uid, ids, quy_trinh_id=False, loai=False):
        ct_nhom_cv_line = []
        for cv in self.browse(cr,uid,ids):
            if loai == "1_nhom_cv":
                sql = '''
                    delete from nhom_cong_viec where ct_th_nhom_cv_id = %s and ct_th_nhom_cv_id is not null
                '''%(cv.id)
                cr.execute(sql)
            if loai == "3_cv":
                sql = '''
                    delete from nhom_cong_viec where ct_th_cv_id = %s and ct_th_cv_id is not null
                '''%(cv.id)
                cr.execute(sql)
            if loai == "4_cv_con":
                sql = '''
                    delete from nhom_cong_viec where ct_th_cv_con_id = %s and ct_th_cv_con_id is not null
                '''%(cv.id)
                cr.execute(sql)
            if loai == "2_nhom_cv_tg":
                sql = '''
                    delete from nhom_cong_viec where ct_th_cv_tg_id = %s and ct_th_cv_tg_id is not null
                '''%(cv.id)
                cr.execute(sql)
        if quy_trinh_id:
            quy_trinh = self.pool.get('quy.trinh').browse(cr,uid,quy_trinh_id)
            for line in quy_trinh.buoc_thuc_hien_line:
                if loai == "1_nhom_cv":
                    ct_nhom_cv_line.append((0,0,{
                                                'name': line.name,
                                                'datas_fname': line.datas_fname,
                                                'datas': line.datas,
                                                'store_fname': line.store_fname,
                                                'db_datas': line.db_datas,
                                                'file_size': line.file_size,
                                                'yeu_cau_kq': line.yeu_cau_kq,
                                                'cach_thuc_hien': line.cach_thuc_hien,
                                                'state': 'da_giao',
                                                'loai': '5_ct_th',
                                                 }))
                    return {'value': {'ct_th_nhom_cv_line': ct_nhom_cv_line}}
                if loai == "2_nhom_cv_tg":
                    ct_nhom_cv_line.append((0,0,{
                                                'name': line.name,
                                                'datas_fname': line.datas_fname,
                                                'datas': line.datas,
                                                'store_fname': line.store_fname,
                                                'db_datas': line.db_datas,
                                                'file_size': line.file_size,
                                                'yeu_cau_kq': line.yeu_cau_kq,
                                                'cach_thuc_hien': line.cach_thuc_hien,
                                                'state': 'da_giao',
                                                'loai': '5_ct_th',
                                                 }))
                    return {'value': {'ct_th_cv_tg_line': ct_nhom_cv_line}}
                if loai == "3_cv":
                    ct_nhom_cv_line.append((0,0,{
                                                'name': line.name,
                                                'datas_fname': line.datas_fname,
                                                'datas': line.datas,
                                                'store_fname': line.store_fname,
                                                'db_datas': line.db_datas,
                                                'file_size': line.file_size,
                                                'yeu_cau_kq': line.yeu_cau_kq,
                                                'cach_thuc_hien': line.cach_thuc_hien,
                                                'state': 'da_giao',
                                                'loai': '5_ct_th',
                                                 }))
                    return {'value': {'ct_th_cv_line': ct_nhom_cv_line}}
                if loai == "4_cv_con":
                    ct_nhom_cv_line.append((0,0,{
                                                'name': line.name,
                                                'datas_fname': line.datas_fname,
                                                'datas': line.datas,
                                                'store_fname': line.store_fname,
                                                'db_datas': line.db_datas,
                                                'file_size': line.file_size,
                                                'yeu_cau_kq': line.yeu_cau_kq,
                                                'cach_thuc_hien': line.cach_thuc_hien,
                                                'state': 'da_giao',
                                                'loai': '5_ct_th',
                                                 }))
                    return {'value': {'ct_th_cv_con_line': ct_nhom_cv_line}}
    
    def onchange_phong_ban_ids(self, cr, uid, ids, phong_ban_ids = False):
        if phong_ban_ids and phong_ban_ids[0] and phong_ban_ids[0][2]:
            ho_tro = 'co'
        else:
            ho_tro = 'khong'
        return {'value': {'ho_tro': ho_tro}}
        
nhom_cong_viec()

class ct_nhom_cong_viec(osv.osv):
    _name = "ct.nhom.cong.viec"
    
    def _data_get(self, cr, uid, ids, name, arg, context=None):
        if context is None:
            context = {}
        result = {}
        location = self.pool.get('ir.config_parameter').get_param(cr, SUPERUSER_ID, 'ir_attachment.location')
        bin_size = context.get('bin_size')
        for attach in self.browse(cr, uid, ids, context=context):
            if location and attach.store_fname:
                result[attach.id] = self._file_read(cr, uid, location, attach.store_fname, bin_size)
            else:
                result[attach.id] = attach.db_datas
                if bin_size:
                    result[attach.id] = int(result[attach.id])

        return result

    def _data_set(self, cr, uid, id, name, value, arg, context=None):
        # We dont handle setting data to null
        if not value:
            return True
        if context is None:
            context = {}
        location = self.pool.get('ir.config_parameter').get_param(cr, SUPERUSER_ID, 'ir_attachment.location')
        file_size = len(value.decode('base64'))
        if location:
            attach = self.browse(cr, uid, id, context=context)
            if attach.store_fname:
                self._file_delete(cr, uid, location, attach.store_fname)
            fname = self._file_write(cr, uid, location, value)
            # SUPERUSER_ID as probably don't have write access, trigger during create
            super(ct_nhom_cong_viec, self).write(cr, SUPERUSER_ID, [id], {'store_fname': fname, 'file_size': file_size}, context=context)
        else:
            super(ct_nhom_cong_viec, self).write(cr, SUPERUSER_ID, [id], {'db_datas': value, 'file_size': file_size}, context=context)
        return True
    _columns = {
        'nhom_cv_id':fields.many2one('nhom.cong.viec','nhom cong viec',ondelete='cascade'),
        'name':fields.char('Tên chi tiết',size=1024, required = True),
        'datas_fname': fields.char('File Name',size=256),
        'datas': fields.function(_data_get, fnct_inv=_data_set, string='File Content', type="binary", nodrop=True),
        'store_fname': fields.char('Stored Filename', size=256),
        'db_datas': fields.binary('Database Data'),
        'file_size': fields.integer('File Size'),
        'yeu_cau_kq':fields.text('Yêu cầu kết quả'),
        'cach_thuc_hien':fields.text('Cách thức thực hiện'),
        'nhan_vien_id':fields.many2one('nhan.vien','Nhân viên'),
        'hoan_thanh': fields.boolean('Hoàn thành'),
    }
    _defaults = {
         'hoan_thanh': False,
         }
#     def _check_nhan_vien(self, cr, uid, ids, context=None):
#         for line in self.browse(cr, uid, ids, context=context):
#             if not line.nhan_vien_id and line.nhom_cv_id.state != 'nhap' and line.nhom_cv_id.state != 'moi_tao':
#                 raise osv.except_osv(_('Cảnh Báo!'),_('Cần chọn nhân viên cho công việc'))
#                 return False
#         return True
#     _constraints = [
#         (_check_nhan_vien, 'Identical Data', []),
#     ]
   

    
ct_nhom_cong_viec()

class quy_trinh(osv.osv):
    _name = "quy.trinh"
    _columns = {
        'name': fields.char('Tên quy trình', size = 100, required=True),
        'phong_ban_id':fields.many2one('phong.ban','Phòng Ban',required = True),
        'chuc_vu_id':fields.many2one('chuc.vu','Chức vụ'),
        'buoc_thuc_hien_line':fields.one2many('buoc.thuc.hien.line','quy_trinh_id','Các bước thực hiện'),
                }
    
quy_trinh()

class buoc_thuc_hien_line(osv.osv):
    _name = "buoc.thuc.hien.line"
    
    def _data_get(self, cr, uid, ids, name, arg, context=None):
        if context is None:
            context = {}
        result = {}
        location = self.pool.get('ir.config_parameter').get_param(cr, SUPERUSER_ID, 'ir_attachment.location')
        bin_size = context.get('bin_size')
        for attach in self.browse(cr, uid, ids, context=context):
            if location and attach.store_fname:
                result[attach.id] = self._file_read(cr, uid, location, attach.store_fname, bin_size)
            else:
                result[attach.id] = attach.db_datas
                if bin_size:
                    result[attach.id] = int(result[attach.id])

        return result

    def _data_set(self, cr, uid, id, name, value, arg, context=None):
        # We dont handle setting data to null
        if not value:
            return True
        if context is None:
            context = {}
        location = self.pool.get('ir.config_parameter').get_param(cr, SUPERUSER_ID, 'ir_attachment.location')
        file_size = len(value.decode('base64'))
        if location:
            attach = self.browse(cr, uid, id, context=context)
            if attach.store_fname:
                self._file_delete(cr, uid, location, attach.store_fname)
            fname = self._file_write(cr, uid, location, value)
            # SUPERUSER_ID as probably don't have write access, trigger during create
            super(buoc_thuc_hien_line, self).write(cr, SUPERUSER_ID, [id], {'store_fname': fname, 'file_size': file_size}, context=context)
        else:
            super(buoc_thuc_hien_line, self).write(cr, SUPERUSER_ID, [id], {'db_datas': value, 'file_size': file_size}, context=context)
        return True
    
    _columns = {
        'quy_trinh_id':fields.many2one('quy.trinh','Quy trình', ondelete = 'cascade'),
        'name': fields.char('Tên chi tiết', size = 100, required=True),
        'yeu_cau_kq':fields.text('Yêu cầu kết quả đạt được'),
        'cach_thuc_hien': fields.text('Cách thức thực hiện'),
        'datas_fname': fields.char('File Name',size=256),
        'datas': fields.function(_data_get, fnct_inv=_data_set, string='File Content', type="binary", nodrop=True),
        'store_fname': fields.char('Stored Filename', size=256),
        'db_datas': fields.binary('Database Data'),
        'file_size': fields.integer('File Size'),
                }
    

    
buoc_thuc_hien_line()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
