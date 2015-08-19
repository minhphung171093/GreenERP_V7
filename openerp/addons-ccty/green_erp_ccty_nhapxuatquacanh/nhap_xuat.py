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
base_path = os.path.dirname(modules.get_module_path('green_erp_ccty_base'))


class nhap_xuat(osv.osv):
    _name = "nhap.xuat"
    _columns = {
        'name': fields.char('Giấy kiểm dịch',size = 50, required = True),
        'chu_hang': fields.char('Họ tên chủ cơ sở',size = 50, required = True),
        'loai_hinh': fields.selection((('a','Nhập'), ('b','Xuất'), ('c','quá cảnh')),'Loại hình'),
        'loai_hang': fields.many2one('loai.hang','Loại hàng'),
        'ngay_nhap_xuat': fields.date('Ngày nhập xuất'),
        'soluong': fields.char('Số lượng',size = 50),
        'noi_xuat_phat': fields.char('Nơi xuất phát',size = 50),
        'noi_nhan': fields.char('Nơi nhận hàng',size = 50),
        'so_xe': fields.char('Số xe',size = 50),
                }
nhap_xuat()

class nhap_xuat_canh_giasuc(osv.osv):
    _name = "nhap.xuat.canh.giasuc"
    
    def _get_company(self, cr, uid, ids, context=None):
        user = self.pool.get('res.users').browse(cr,uid,uid)
        return user.company_id.id or False
    
    _columns = {
        'name': fields.char('Số Giấy kiểm dịch',size = 50, required = True, states={ 'done':[('readonly', True)]}),
        'loai_id': fields.many2one('loai.vat','Loài vật', required = True, states={ 'done':[('readonly', True)]}),
        'ngay_cap': fields.date('Ngày cấp', states={ 'done':[('readonly', True)]}),
        'ngay_kiem_tra': fields.date('Ngày', required = True, states={ 'done':[('readonly', True)]}),
        'ten_ho_id': fields.many2one('chan.nuoi','Hộ', states={ 'done':[('readonly', True)]}),
        'can_bo_id': fields.many2one('res.users','Cán bộ', states={ 'done':[('readonly', True)]}),
        'tram_id': fields.many2one('tram.thu.y','Trạm'),
        'phuong_xa_id': fields.many2one( 'phuong.xa','Phường (xã)', states={ 'done':[('readonly', True)]}),
        'khu_pho_id': fields.many2one( 'khu.pho','Khu phố (ấp)', states={ 'done':[('readonly', True)]}),
        'quan_huyen_id': fields.many2one( 'quan.huyen','Quận (huyện)', states={ 'done':[('readonly', True)]}),
        'loai':fields.selection([('nhap', 'Nhập'),('xuat', 'Xuất')],'Loại', readonly=True, states={ 'done':[('readonly', True)]}),
        'chitiet_loai_nx':fields.one2many('chi.tiet.loai.nhap.xuat','nhap_xuat_loai_id','Chi tiet', states={ 'done':[('readonly', True)]}),
        'chitiet_da_tiem_phong':fields.one2many('chi.tiet.da.tiem.phong','nhap_xuat_tiemphong_id','Chi tiet', states={ 'done':[('readonly', True)]}),
        'company_id': fields.many2one( 'res.company','Company', states={ 'done':[('readonly', True)]}),
        'state':fields.selection([('draft', 'Nháp'),('done', 'Duyệt')],'Status', readonly=True),
                }
    _defaults = {
        'company_id': _get_company,
        'state':'draft',
                 }
                
    
    def _check_so_luong(self, cr, uid, ids, context=None):
        for nhap_xuat in self.browse(cr, uid, ids, context=context):
            sql = '''
                select case when sum(so_luong)!=0 then sum(so_luong) else 0 end sl_loai from chi_tiet_loai_nhap_xuat
                where nhap_xuat_loai_id = %s
            '''%(nhap_xuat.id)
            cr.execute(sql)
            sl_loai = cr.dictfetchone()['sl_loai']
            sql = '''
                select case when sum(so_luong)!=0 then sum(so_luong) else 0 end sl_tiemphong from chi_tiet_da_tiem_phong
                where nhap_xuat_tiemphong_id = %s
            '''%(nhap_xuat.id)
            cr.execute(sql)
            sl_tiemphong = cr.dictfetchone()['sl_tiemphong']
            if sl_tiemphong>sl_loai:
                if nhap_xuat.loai == 'nhap':
                    raise osv.except_osv(_('Warning!'),_('Số lượng loài %s đã tiêm phòng không được nhiều hơn số lượng loài %s nhập vào')%(nhap_xuat.loai_id.name, nhap_xuat.loai_id.name))
                    return False
                if nhap_xuat.loai == 'xuat':
                    raise osv.except_osv(_('Warning!'),_('Số lượng loài %s đã tiêm phòng không được nhiều hơn số lượng loài %s xuất ra')%(nhap_xuat.loai_id.name, nhap_xuat.loai_id.name))
                    return False
            return True
         
    _constraints = [
        (_check_so_luong, 'Identical Data', []),
    ]   
    
    def bt_duyet(self, cr, uid, ids, context=None):
        chi_tiet_loai =[]
        co_cau_obj = self.pool.get('co.cau')
        for line in self.browse(cr, uid, ids, context=context):
            for loai in line.chitiet_loai_nx:
                chi_tiet_loai.append((0,0,{
                'name':loai.name,
                'so_luong':loai.so_luong,                           
                                           }))
            value ={
            'chon_loai':line.loai_id.id,
            'can_bo_ghi_so_id':line.can_bo_id and line.can_bo_id.id or False,
            'ngay_ghi_so':line.ngay_cap or False,
            'tang_giam':'a',
            'ly_do':'Nhập từ số giấy kiểm dịch'+' '+ line.name,
            'quan_huyen_id':line.quan_huyen_id and line.quan_huyen_id.id or False,
            'phuong_xa_id':line.phuong_xa_id and line.phuong_xa_id.id or False,
            'khu_pho_id':line.khu_pho_id and line.khu_pho_id.id or False,
            'ten_ho_id':line.ten_ho_id and line.ten_ho_id.id or False,
            'chitiet_loai':chi_tiet_loai,
            'trang_thai':'new',
            'company_id':line.company_id.id,
                    }
        co_cau_obj.create(cr,uid,value)
        return self.write(cr, uid, ids,{'state':'done'})
    def onchange_chon_loai(self, cr, uid, ids, loai_id = False, context=None):
        chi_tiet= []
        tiem_phong = []
        for nhap_xuat in self.browse(cr,uid,ids):
            sql = '''
                delete from chi_tiet_loai_nhap_xuat where nhap_xuat_loai_id = %s
            '''%(nhap_xuat.id)
            cr.execute(sql)
            sql = '''
                delete from chi_tiet_da_tiem_phong where nhap_xuat_tiemphong_id = %s
            '''%(nhap_xuat.id)
            cr.execute(sql)
        if loai_id:
            loai = self.pool.get('loai.vat').browse(cr,uid,loai_id)    
            for line_loaivat in loai.chitiet_loaivat:
                chi_tiet.append((0,0,{
                                      'name': line_loaivat.name
                                      }))
            for line_loaibenh in loai.chitiet_loaibenh:
                tiem_phong.append((0,0,{
                                      'name': line_loaibenh.name
                                      }))
        return {'value': {'chitiet_loai_nx': chi_tiet,
                          'chitiet_da_tiem_phong': tiem_phong,
                          }}
    
nhap_xuat_canh_giasuc()

class chi_tiet_loai_nhap_xuat(osv.osv):
    _name = "chi.tiet.loai.nhap.xuat"
    _columns = {
        'nhap_xuat_loai_id': fields.many2one('nhap.xuat.canh.giasuc','Nhap Xuat', ondelete = 'cascade'),
        'name': fields.char('Thông tin', readonly = True),
        'so_luong': fields.float('Số lượng'),
                }
chi_tiet_loai_nhap_xuat()

class chi_tiet_da_tiem_phong(osv.osv):
    _name = "chi.tiet.da.tiem.phong"
    _columns = {
        'nhap_xuat_tiemphong_id': fields.many2one('nhap.xuat.canh.giasuc','Nhap Xuat', ondelete = 'cascade'),
        'name': fields.char('Loại bệnh', readonly = True),
        'so_luong': fields.float('Số lượng'),
                }
chi_tiet_da_tiem_phong()



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
