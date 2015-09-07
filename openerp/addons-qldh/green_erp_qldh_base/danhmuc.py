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
phong_ban()

class ds_nhan_vien_line(osv.osv):
    _name = "ds.nhan.vien.line"
    _columns = {
        'phong_ban_id': fields.many2one('phong.ban','Phòng ban', ondelete='cascade'),
        'nhan_vien_id': fields.many2one('nhan.vien','Nhân viên', required=True),
        'chuc_vu_id': fields.many2one('chuc.vu','Chức vụ', readonly = True),
                }
    
    
    def onchange_nhan_vien(self, cr, uid, ids,nhan_vien_id=False,context=None):
        if nhan_vien_id:
            nhan_vien = self.pool.get('nhan.vien').browse(cr,uid,nhan_vien_id)
        res = {'value':{
                        'chuc_vu_id':nhan_vien.chuc_vu_id.id,
                      }
               }
        return res 
    def create(self, cr, uid, vals, context=None):
        if 'nhan_vien_id' in vals and vals['nhan_vien_id']:
            nhan_vien = self.pool.get('nhan.vien').browse(cr,uid,vals['nhan_vien_id'])
            vals.update({
                        'chuc_vu_id':nhan_vien.chuc_vu_id.id,
                        })
        new_id = super(ds_nhan_vien_line, self).create(cr, uid, vals, context)
        return new_id
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'nhan_vien_id' in vals and vals['nhan_vien_id']:
            nhan_vien = self.pool.get('nhan.vien').browse(cr,uid,vals['nhan_vien_id'])
            vals.update({
                        'chuc_vu_id':nhan_vien.chuc_vu_id.id,
                        })
        new_write = super(ds_nhan_vien_line, self).write(cr, uid, ids, vals, context)
        return new_write
ds_nhan_vien_line()

class nhan_vien(osv.osv):
    _name = "nhan.vien"
    _columns = {
        'name': fields.char('Mã nhân viên', size = 100, required=True),
        'ten_nv': fields.char('Tên nhân viên', size = 100, required=True),
        'chuc_vu_id': fields.many2one('chuc.vu','Chức vụ', required=True),
        'dia_chi': fields.char('Địa chỉ', size = 100),
        'sdt': fields.char('Số điện thoại', size = 100),
                }
    
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
