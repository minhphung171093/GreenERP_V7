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

class doanh_nghiep(osv.osv):
    _name = "doanh.nghiep"
    
    def _get_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = tools.image_get_resized_images(obj.image)
        return result
    
    def _set_image(self, cr, uid, id, name, value, args, context=None):
        return self.write(cr, uid, [id], {'image': tools.image_resize_image_big(value)}, context=context)

    def _has_image(self, cr, uid, ids, name, args, context=None):
        result = {}
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = obj.image != False
        return result
    
    _columns = {
        'name': fields.char('Tên cơ sở',size = 2048, required = True),
        'ma_coso': fields.char('Mã cơ sở',size = 2048),
        'lat':  fields.float(u'Tọa độ X', digits=(9, 6)),
        'lng': fields.float(u'Tọa độ Y', digits=(9, 6)),
        'mo_ta':fields.text('Mô tả'),
        'diachi': fields.char('Địa chỉ',size = 2048),
        'nguoilienhe': fields.char('Người liên hệ', size=1024),
        'dienthoai': fields.char('Điện thoại', size=1024),
        'email': fields.char('Email', size=1024),
        'tieuchi_id': fields.many2one('tieu.chi', 'Tiêu chí'),
        'phuong_xa_id': fields.many2one('phuong.xa', 'Phường/Xã'),
        'quan_huyen_id': fields.many2one('quan.huyen', 'Quận/Huyện'),
        'tinh_thanhpho_id': fields.many2one('tinh.tp', 'Tỉnh/Thành phố'),
        'soluoc_congty': fields.text('Sơ lược về công ty'),
        'fax': fields.char('Fax',size = 2048),
        'phan_loai_id': fields.many2one('phan.loai', 'Phân loại'),
        'coquan_quanly_id': fields.many2one('coquan.quanly', 'Cơ quan quản lý'),
        'hethong_dambao_attp_id': fields.many2one('hethong.dambao.attp', 'Hệ thống đảm bảo ATTP'),
        
        'image': fields.binary("Image"),
        'image_medium': fields.function(_get_image, fnct_inv=_set_image,
            string="Medium-sized image", type="binary", multi="_get_image",
            store={
                'doanh.nghiep': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            },),
        'image_small': fields.function(_get_image, fnct_inv=_set_image,
            string="Small-sized image", type="binary", multi="_get_image",
            store={
                'doanh.nghiep': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            },),
        'has_image': fields.function(_has_image, type="boolean"),
        
        }

    _defaults = {
    }
    
doanh_nghiep()

class baocao_doanhnghiep_map(osv.osv):
    _name = "baocao.doanhnghiep.map"
    _columns = {
        'lat': fields.float(u'Tọa độ X', digits=(9, 6)),
        'lng': fields.float(u'Tọa độ Y', digits=(9, 6)),
        'radius': fields.float(u'Bán kính', digits=(9, 6)),
        'map': fields.dummy(),
        'points': fields.text('Points'),
        'user_id': fields.many2one('res.users','Người tạo'),
        'doanhnghiep_ids': fields.many2many('doanh.nghiep', 'baocaodoanhnghiepmap_doanhnghiep_ref','baocao_id','doanhnghiep_id', 'Danh sách doanh nghiệp'),
    }
    
    _defaults = {
        'user_id': lambda self, cr, uid, context: uid,
    }
    
    def onchange_toado_bankinh(self, cr, uid, ids, lat=False, lng=False, radius=False, context=None):
        vals = {}
        partner_obj = self.pool.get('res.partner')
        if lat and lng and radius:
            points = ''
            sql = '''
                select id,lat,lng,mo_ta from doanh_nghiep where lat is not null and lat!=0 and lng is not null and lng!=0
            '''
            cr.execute(sql)
            doanhnghiep_ids = []
            for doanhnghiep in cr.dictfetchall():
                km = 0
                try:
                    km = partner_obj.haversine(lng,lat,doanhnghiep['lng'],doanhnghiep['lat'])
                except Exception, e:
                    pass
                if km and km*1000<=radius:
                    doanhnghiep_ids.append(doanhnghiep['id'])
                    points+=str(doanhnghiep['lat'])+'phung_cat_giatri'+str(doanhnghiep['lng'])+'phung_cat_giatri'+(doanhnghiep['mo_ta'] or '')+'phung_cat_diem'

            if points:
                points=points[:-14]
            vals = {'points':points,'doanhnghiep_ids':[(6,0,doanhnghiep_ids)]}
        return {'value': vals}
    
baocao_doanhnghiep_map()

class res_partner(osv.osv):
    _inherit = 'res.partner'

    def write_radius(self, cr, uid, id,active_model, vals, context=None):
        res = super(res_partner, self).write_radius(cr, uid, id,active_model, vals, context)
        if vals.get('radius',False) and active_model=='baocao.doanhnghiep.map':
            channuoi_map_obj = self.pool.get('baocao.doanhnghiep.map')
            line = channuoi_map_obj.browse(cr, uid, int(id))
            vals.update(channuoi_map_obj.onchange_toado_bankinh( cr, uid, [], line.lat, line.lng, vals['radius'],context)['value'])
            channuoi_map_obj.write(cr, uid, [int(id)], vals, context)
        return res
    
    def write_center(self, cr, uid, id,active_model, vals, context=None):
        res = super(res_partner, self).write_center(cr, uid, id,active_model, vals, context)
        if vals.get('center',False) and active_model=='baocao.doanhnghiep.map':
            channuoi_map_obj = self.pool.get('baocao.doanhnghiep.map')
            line = channuoi_map_obj.browse(cr, uid, int(id))
            vals.update(channuoi_map_obj.onchange_toado_bankinh( cr, uid, [], vals['center']['G'], vals['center']['K'], line.radius,context)['value'])
            vals.update({'lat':vals['center']['G'],'lng':vals['center']['K']})
            channuoi_map_obj.write(cr, uid, [int(id)], vals, context)
        return res
    
res_partner()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
