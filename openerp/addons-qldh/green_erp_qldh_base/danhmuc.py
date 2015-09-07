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
ds_nhan_vien_line()

class nhan_vien(osv.osv):
    _name = "nhan.vien"
    _columns = {
        'name': fields.char('Tên nhân viên', size = 100, required=True),
        'chuc_vu_id': fields.many2one('chuc.vu','Chức vụ', required=True),
                }
nhan_vien()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
