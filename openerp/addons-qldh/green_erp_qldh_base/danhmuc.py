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

class chuc_vu(osv.osv):
    _name = "chuc.vu"
    _columns = {
        'name': fields.char("Tên chức vụ", size=1024, required=True),
    }

chuc_vu()

class phong_ban(osv.osv):
    _name = "phong.ban"
    _columns = {
        'name': fields.char('Tên phòng ban', size = 100, required=True),
        'truong_phong_id': fields.many2one('nhan.vien','Trưởng phòng', required=True),
        'ds_nhan_vien_line': fields.one2many('ds.nhan.vien.line','phong_ban_id','Các nhân viên'),
                }
    def _check_truong_phong_id(self, cr, uid, ids, context=None):
        for nhan_vien in self.browse(cr, uid, ids, context=context):
            nhan_vien_ids = self.search(cr, uid, [('id','!=',nhan_vien.id),('truong_phong_id', '=',nhan_vien.truong_phong_id.id)])
            if nhan_vien_ids:
                raise osv.except_osv(_('Warning!'),_('Trưởng phòng %s đã thuộc một phòng ban !')%(nhan_vien.truong_phong_id.name))
                return False
            return True
         
    _constraints = [
        (_check_truong_phong_id, 'Identical Data',[]),
    ]   
    
    def create(self, cr, uid, vals, context=None):
        new_id = super(phong_ban, self).create(cr, uid, vals, context)
        phong = self.browse(cr,uid,new_id)
        sql = '''
            update nhan_vien set phong_ban_id = %s where id = %s
        '''%(new_id, phong.truong_phong_id.id)
        cr.execute(sql)
        for line in phong.ds_nhan_vien_line:
            sql = '''
                update nhan_vien set phong_ban_id = %s where id = %s
            '''%(new_id, line.nhan_vien_id.id)
            cr.execute(sql)
        return new_id
    
    def write(self, cr, uid, ids, vals, context=None):
        new_write = super(phong_ban, self).write(cr, uid,ids, vals, context)
        for phong in self.browse(cr,uid,ids):
            sql = '''
                update nhan_vien set phong_ban_id = %s where id = %s
            '''%(new_id, phong.truong_phong_id.id)
            cr.execute(sql)
            for line in phong.ds_nhan_vien_line:
                sql = '''
                    update nhan_vien set phong_ban_id = %s where id = %s
                '''%(new_id, line.nhan_vien_id.id)
                cr.execute(sql)
        return new_write
phong_ban()

class ds_nhan_vien_line(osv.osv):
    _name = "ds.nhan.vien.line"
    _columns = {
        'phong_ban_id': fields.many2one('phong.ban','Phòng ban', ondelete = 'cascade'),
        'nhan_vien_id': fields.many2one('nhan.vien','Nhân viên', required=True),
        'chuc_vu_id': fields.many2one('chuc.vu','Chức vụ', required=True),
        'dia_chi': fields.char('Địa chỉ', size = 100),
        'sdt': fields.char('Số điện thoại', size = 100),
                }
    def onchange_nhan_vien_id(self, cr, uid, ids, nhan_vien_id = False):
        if nhan_vien_id:
            nhan_vien = self.pool.get('nhan.vien').browse(cr,uid,nhan_vien_id)
            return {'value': {'chuc_vu_id': nhan_vien.chuc_vu_id.id, 'dia_chi': nhan_vien.dia_chi and nhan_vien.dia_chi or '', 'sdt': nhan_vien.sdt and nhan_vien.sdt or ''}}
   
    def _check_nhan_vien_id(self, cr, uid, ids, context=None):
        for nhan_vien in self.browse(cr, uid, ids, context=context):
            nhan_vien_ids = self.search(cr, uid, [('id','!=',nhan_vien.id),('nhan_vien_id', '=',nhan_vien.nhan_vien_id.id)])
            if nhan_vien_ids:
                raise osv.except_osv(_('Warning!'),_('Nhân viên %s đã thuộc một phòng ban !')%(nhan_vien.nhan_vien_id.name))
                return False
            return True
         
    _constraints = [
        (_check_nhan_vien_id, 'Identical Data',[]),
    ]   
    

ds_nhan_vien_line()


class nhan_vien(osv.osv):
    _name = "nhan.vien"
    _columns = {
        'name': fields.char('Mã nhân viên', size = 100, required=True),
        'phong_ban_id': fields.many2one('phong.ban','Phòng ban'),
        'ten_nv': fields.char('Tên nhân viên', size = 100, required=True),
        'chuc_vu_id': fields.many2one('chuc.vu','Chức vụ', required=True),
        'dia_chi': fields.char('Địa chỉ', size = 100),
        'sdt': fields.char('Số điện thoại', size = 100),
                }
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('search_nhan_vien_id'):
            sql = '''
                select id from nhan_vien
                where phong_ban_id is null
            '''
            cr.execute(sql)
            nv_ids = [row[0] for row in cr.fetchall()]
            args += [('id','in',nv_ids)]
        return super(nhan_vien, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
       ids = self.search(cr, user, args, context=context, limit=limit)
       return self.name_get(cr, user, ids, context=context)
   
    def name_get(self, cr, uid, ids, context=None):
        res = []
        if not ids:
            return res
        reads = self.read(cr, uid, ids, ['name', 'ten_nv'], context)
 
        for record in reads:
            name = record['name'] + ' - ' + record['ten_nv']
            res.append((record['id'], name))
        return res
    
    def _check_ma_nhan_vien(self, cr, uid, ids, context=None):
        for nhan_vien in self.browse(cr, uid, ids, context=context):
            nhan_vien_ids = self.search(cr,uid,[('id', '!=', nhan_vien.id), ('name', '=', nhan_vien.name)])
            if nhan_vien_ids:
                raise osv.except_osv(_('Warning!'),_('Hệ thống không cho phép trùng mã nhân viên'))
                return False
        return True
    
    _constraints = [
        (_check_ma_nhan_vien, 'Identical Data', []),
    ]
nhan_vien()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
