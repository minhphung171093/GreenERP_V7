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
    _columns = {
        'name':fields.char('Tên nhóm công việc',size=1024,required=True),
        'phong_ban_id':fields.many2one('phong.ban','Phòng ban'),
        'ho_tro':fields.selection([('co','Có'),('khong','Không')],'Hỗ trợ'),
        'quy_trinh_id':fields.many2one('quy.trinh','Quy trình'),
        'trang_thai':fields.selection([('moi','Mới nhận'),('lam','Đang làm'),('cho_duyet','Chờ phê duyệt'),('duyet','Đã duyệt')],'Trạng thái'),
        'ct_nhom_cv_line':fields.one2many('ct.nhom.cong.viec','nhom_cv_id','Chi tiết công việc'),
        'ghi_chu':fields.text('Ghi chú'),
        'cong_viec_line':fields.one2many('cong.viec','nhom_cong_viec_id','Nhóm công việc'),
                
    }
    _defaults = {
             'trang_thai':'moi',    
             'ho_tro':'co'    
                 }
    def onchange_quy_trinh_id(self, cr, uid, ids, quy_trinh_id=False):
        ct_nhom_cv_line = []
        if quy_trinh_id:
            quy_trinh = self.pool.get('quy.trinh').browse(cr,uid,quy_trinh_id)
            for line in quy_trinh.buoc_thuc_hien_line:
                ct_nhom_cv_line.append((0,0,{
                                            'name': line.name,
                                            'datas_fname': line.datas_fname,
                                            'datas': line.datas,
                                            'store_fname': line.store_fname,
                                            'db_datas': line.db_datas,
                                            'file_size': line.file_size,
                                            'yeu_cau_kq': line.yeu_cau_kq,
                                            'cach_thuc_hien': line.cach_thuc_hien,
                                             }))
        return {'value': {'ct_nhom_cv_line': ct_nhom_cv_line}}  
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

    }

ct_nhom_cong_viec()

class cong_viec(osv.osv):
    _name = "cong.viec"
    _columns = {
        'nhom_cong_viec_id':fields.many2one('nhom.cong.viec','Nhóm công việc'),
        'name':fields.char('Tên công việc',size=1024,required=True),
        'phong_ban_id':fields.many2one('phong.ban','Phòng ban'),
#         'ho_tro':fields.selection([('co','Có'),('khong','Không')],'Hỗ trợ'),
        'quy_trinh_id':fields.many2one('quy.trinh','Quy trình'),
        'trang_thai':fields.selection([('moi','Mới nhận'),('lam','Đang làm'),('cho_duyet','Chờ phê duyệt'),('duyet','Đã duyệt')],'Trạng thái'),
        'chi_tiet_cv_line':fields.one2many('chi.tiet.cong.viec','cv_id','Chi tiết công việc'),
        'ghi_chu':fields.text('Ghi chú'),
        'cong_viec_con_line':fields.one2many('cong.viec.con','cong_viec_id','Công việc'),
                
    }
    
    _defaults = {
             'trang_thai':'moi',    
                 }
    def onchange_quy_trinh_id(self, cr, uid, ids, quy_trinh_id=False):
        ct_cv_line = []
        if quy_trinh_id:
            quy_trinh = self.pool.get('quy.trinh').browse(cr,uid,quy_trinh_id)
            for line in quy_trinh.buoc_thuc_hien_line:
                ct_cv_line.append((0,0,{
                                            'name': line.name,
                                            'datas_fname': line.datas_fname,
                                            'datas': line.datas,
                                            'store_fname': line.store_fname,
                                            'db_datas': line.db_datas,
                                            'file_size': line.file_size,
                                            'yeu_cau_kq': line.yeu_cau_kq,
                                            'cach_thuc_hien': line.cach_thuc_hien,
                                             }))
        return {'value': {'chi_tiet_cv_line': ct_cv_line}}
cong_viec()

class chi_tiet_cong_viec(osv.osv):
    _name = "chi.tiet.cong.viec"
    
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
            super(chi_tiet_cong_viec, self).write(cr, SUPERUSER_ID, [id], {'store_fname': fname, 'file_size': file_size}, context=context)
        else:
            super(chi_tiet_cong_viec, self).write(cr, SUPERUSER_ID, [id], {'db_datas': value, 'file_size': file_size}, context=context)
        return True
    _columns = {
        'cv_id':fields.many2one('cong.viec','Cong viec',ondelete='cascade'),
        'name':fields.char('Tên chi tiết',size=1024, required = True),
        'datas_fname': fields.char('File Name',size=256),
        'datas': fields.function(_data_get, fnct_inv=_data_set, string='File Content', type="binary", nodrop=True),
        'store_fname': fields.char('Stored Filename', size=256),
        'db_datas': fields.binary('Database Data'),
        'file_size': fields.integer('File Size'),
        'yeu_cau_kq':fields.text('Yêu cầu kết quả'),
        'cach_thuc_hien':fields.text('Cách thức thực hiện'),

    }

chi_tiet_cong_viec()

class cong_viec_con(osv.osv):
    _name = "cong.viec.con"
    _columns = {
        'cong_viec_id':fields.many2one('cong.viec','Công việc'),
        'nhom_cv_id': fields.many2one('nhom.cong.viec','Nhóm công việc'),
        'name':fields.char('Tên công việc con',size=1024,required=True),
        'phong_ban_id':fields.many2one('phong.ban','Phòng ban'),
#         'ho_tro':fields.selection([('co','Có'),('khong','Không')],'Hỗ trợ'),
        'quy_trinh_id':fields.many2one('quy.trinh','Quy trình'),
        'trang_thai':fields.selection([('moi','Mới nhận'),('lam','Đang làm'),('cho_duyet','Chờ phê duyệt'),('duyet','Đã duyệt')],'Trạng thái'),
        'chi_tiet_cv_con_line':fields.one2many('chi.tiet.cong.viec.con','cv_con_id','Chi tiết công việc'),
        'ghi_chu':fields.text('Ghi chú'),
#         'cong_viec_line':fields.one2many('ct.nhom.cong.viec','nhom_cv_id','Chi tiết công việc'),
                
    }
    
    _defaults = {
             'trang_thai':'moi',    
                 }
    def create(self, cr, uid, vals, context=None):
        if 'cong_viec_id' in vals and vals['cong_viec_id']:
            cong_viec = self.pool.get('cong.viec').browse(cr,uid,vals['cong_viec_id'])
            vals.update({
                        'nhom_cv_id':cong_viec.nhom_cong_viec_id.id,
                        })
        new_id = super(cong_viec_con, self).create(cr, uid, vals, context)
        return new_id
    def onchange_quy_trinh_id(self, cr, uid, ids, quy_trinh_id=False):
        ct_cv_con_line = []
        if quy_trinh_id:
            quy_trinh = self.pool.get('quy.trinh').browse(cr,uid,quy_trinh_id)
            for line in quy_trinh.buoc_thuc_hien_line:
                ct_cv_con_line.append((0,0,{
                                            'name': line.name,
                                            'datas_fname': line.datas_fname,
                                            'datas': line.datas,
                                            'store_fname': line.store_fname,
                                            'db_datas': line.db_datas,
                                            'file_size': line.file_size,
                                            'yeu_cau_kq': line.yeu_cau_kq,
                                            'cach_thuc_hien': line.cach_thuc_hien,
                                             }))
        return {'value': {'chi_tiet_cv_con_line': ct_cv_con_line}}
cong_viec_con()

class chi_tiet_cong_viec_con(osv.osv):
    _name = "chi.tiet.cong.viec.con"
    
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
            super(chi_tiet_cong_viec_con, self).write(cr, SUPERUSER_ID, [id], {'store_fname': fname, 'file_size': file_size}, context=context)
        else:
            super(chi_tiet_cong_viec_con, self).write(cr, SUPERUSER_ID, [id], {'db_datas': value, 'file_size': file_size}, context=context)
        return True
    _columns = {
        'cv_con_id':fields.many2one('cong.viec.con','Cong viec',ondelete='cascade'),
        'name':fields.char('Tên chi tiết',size=1024, required = True),
        'datas_fname': fields.char('File Name',size=256),
        'datas': fields.function(_data_get, fnct_inv=_data_set, string='File Content', type="binary", nodrop=True),
        'store_fname': fields.char('Stored Filename', size=256),
        'db_datas': fields.binary('Database Data'),
        'file_size': fields.integer('File Size'),
        'yeu_cau_kq':fields.text('Yêu cầu kết quả'),
        'cach_thuc_hien':fields.text('Cách thức thực hiện'),

    }

chi_tiet_cong_viec_con()




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
