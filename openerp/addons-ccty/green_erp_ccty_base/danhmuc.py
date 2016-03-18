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

class can_bo(osv.osv):
    _name = "can.bo"
    _columns = {
        'name': fields.char('Họ tên', size=30,required = True),
        'tram_id': fields.many2one('res.company','Trạm'),
        'email': fields.char( 'Email',size = 50),
        'dien_thoai': fields.char( 'Điện thoại',size = 50),
        'user_id': fields.many2one( 'res.users','Người dùng',required = True),
                }
can_bo()

class trang_thai(osv.osv):
    _name = "trang.thai"
    _order = "stt"
    _columns = {
        'name': fields.char('Trạng thái', size=100,required = True),
        'stt': fields.integer('STT',required = True),
        'chinh_sua': fields.selection([('nhap', 'Nháp'),('in', 'Đang xử lý'), ('ch_duyet', 'Cấp Huyện Duyệt'), ('cc_duyet', 'Chi Cục Duyệt'), ('huy', 'Hủy bỏ')],'Chinh Sua'),
                }
trang_thai()

class res_users(osv.osv):
    _inherit = "res.users"
    _columns = {
        'dien_thoai': fields.char( 'Điện thoại',size = 50),
        'ngon_ngu':fields.selection([('en_US', 'English'),('vi_VN', 'Vietnamese/Tiếng Việt')],'Ngôn ngữ')
                }
    _defaults={
        'ngon_ngu':'vi_VN',
               }
    
    def onchange_ngon_ngu(self, cr, uid, ids,ngon_ngu = False, context=None):
        vals = {}
        if ngon_ngu and ngon_ngu=='vi_VN':
            vals = {'lang':'vi_VN'}
        elif ngon_ngu and ngon_ngu=='en_US':
            vals = {'lang':'en_US'}
        else:
            vals = {'lang':''}
        return {'value': vals}
res_users()

class res_company(osv.osv):
    _inherit = "res.company"
    _columns = {
        'cap': fields.selection([('xa', 'Xã'),('huyen', 'Huyện'), ('chi_cuc', 'Chi Cục')],'Cấp'),
                }
    
    def init(self,cr):
        cr.execute(''' update ir_model_data set noupdate='f' where model='ir.rule' and module='base' and name='res_company_rule' ''')
res_company()

class tram_thu_y(osv.osv):
    _name = "tram.thu.y"
    _columns = {
        'name': fields.char('Tên trạm', size=30,required = True),
        'thanh_pho_id': fields.many2one( 'tinh.tp','Tỉnh'),
        'dia_chi': fields.char('Địa chỉ', size=200),
        'email': fields.char( 'Email',size = 50),
        'dien_thoai': fields.char( 'Điện thoại',size = 50),
        'tram_truong_id': fields.many2one( 'can.bo','Trạm trưởng'),
        'toa_do_x': fields.char( 'Tọa độ X',size = 10),
        'toa_do_y': fields.char( 'Tọa độ Y',size = 10),
        'ds_canbo_line':fields.one2many('can.bo','tram_id','Chi tiet'),
                }
tram_thu_y()

class tinh_tp(osv.osv):
    _name = "tinh.tp"
    _columns = {
        'name': fields.char('Tỉnh/Thành Phố',size = 50, required = True),
                }
tinh_tp()
class loai_vat(osv.osv):
    _name = "loai.vat"
    _columns = {
        'ma_loai': fields.char('Mã loài',size = 50),
        'name': fields.char('Tên loài',size = 50, required = True),
        'thuoc_loai': fields.selection((('dv_thuong','Động vật thường'), ('dv_hoangda','Động vật hoang dã'), ('thuy_san','Thủy sản')),'Thuộc'),
        'thoi_gian': fields.float('thời gian nuôi (tháng)'),
        'chitiet_loaivat':fields.one2many('chi.tiet.loai.vat','loai_id','Chi tiet'),
#         'chitiet_loaibenh':fields.one2many('chi.tiet.loai.benh','loai_id','Chi tiet'),
        'chitiet_loai_vaccine':fields.one2many('chi.tiet.loai.vacxin','loai_id','Chi tiet'),
                }
    
    def _check_ten_loai(self, cr, uid, ids, context=None):
        for loai in self.browse(cr, uid, ids, context=context):
            loai_ids = self.search(cr,uid,[('id', '!=', loai.id), ('name', '=', loai.name)])
            if loai_ids:
                raise osv.except_osv(_('Warning!'),_('Tên loài vật không được trùng nhau'))
                return False
        return True
    _constraints = [
        (_check_ten_loai, 'Identical Data', []),
    ]   
    
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('search_loai_id'):
            bosua_model, bosua_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'green_erp_ccty_base', 'loaivat_bosua')
            self.pool.get('loai.vat').check_access_rule(cr, uid, [bosua_id], 'read', context = context)
            sql = '''
                select id from loai_vat
                where id != %s
            '''%(bosua_id)
            cr.execute(sql)
            loaivat_ids = [row[0] for row in cr.fetchall()]
            args += [('id','in',loaivat_ids)]
        return super(loai_vat, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
       ids = self.search(cr, user, args, context=context, limit=limit)
       return self.name_get(cr, user, ids, context=context)
loai_vat()

class chi_tiet_loai_vat(osv.osv):
    _name = "chi.tiet.loai.vat"
    _columns = {
        'loai_id': fields.many2one('loai.vat','Loai vat',ondelete = 'cascade'),
        'name': fields.char('Thông tin',size = 50),
        'tiem_phong':fields.boolean('Có được phép tiêm phòng ?'),
                }
    _defaults = {
        'tiem_phong':False,
        
                 }
chi_tiet_loai_vat()

class chi_tiet_loai_vacxin(osv.osv):
    _name = "chi.tiet.loai.vacxin"
    _columns = {
        'loai_id': fields.many2one('loai.vat','Loai vat',ondelete = 'cascade'),
        'vacxin_id': fields.many2one('loai.vacxin','Loại Vaccine', required = True),
        'yes_no': fields.boolean('Có'),
                }
    _defaults = {
                 'yes_no': True,
                 }    
chi_tiet_loai_vacxin()

class chi_tiet_loai_benh(osv.osv):
    _name = "chi.tiet.loai.benh"
    _columns = {
        'loai_id': fields.many2one('loai.vat','Loai vat',ondelete = 'cascade'),
        'name': fields.char('Loại bệnh',size = 50),
                }
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('search_loai_benh'):
            sql = '''
                select id from chi_tiet_loai_benh
                where loai_id = %s
            '''%(context.get('loai_id'))
            cr.execute(sql)
            loai_benh_ids = [row[0] for row in cr.fetchall()]
            args += [('id','in',loai_benh_ids)]
        return super(chi_tiet_loai_benh, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
       ids = self.search(cr, user, args, context=context, limit=limit)
       return self.name_get(cr, user, ids, context=context)
    
chi_tiet_loai_benh()

class chan_nuoi(osv.osv):
    _name = "chan.nuoi"
    def get_trangthai_nhap(self, cr, uid, ids, context=None):
        sql = '''
            select id from trang_thai where stt = 1
        '''
        cr.execute(sql)
        trang = cr.dictfetchone()
        return trang and trang['id'] or False
    
    def _get_hien_an(self, cr, uid, ids, name, arg, context=None):        
        result = {}
        
        user = self.pool.get('res.users').browse(cr,uid,uid)
        for nhap_xuat in self.browse(cr,uid,ids):
            result[nhap_xuat.id] = False  
            if nhap_xuat.trang_thai_id.stt == 1 and user.company_id.cap in ['huyen', 'chi_cuc']:
                result[nhap_xuat.id] = True
            elif nhap_xuat.trang_thai_id.stt == 2 and user.company_id.cap in ['chi_cuc']:
                result[nhap_xuat.id] = True    
        return result
    _columns = {
        'ma_ho': fields.char('Mã hộ',size = 50, required = True),
        'name': fields.char('Tên hộ',size = 50, required = True),
        'dien_thoai': fields.char('Điện thoại',size = 50),
        'so_nha': fields.char('Số nhà',size = 50),
        'ngay_cap': fields.date('Thời gian cấp', required = False),
        'phuong_xa_id': fields.many2one( 'phuong.xa','Phường (xã)', required = True),
        'khu_pho_id': fields.many2one('khu.pho','Khu phố (ấp)', required = True),
        'quan_huyen_id': fields.many2one('quan.huyen','Quận (huyện)', required = True),
        'company_id': fields.many2one('res.company','Trạm', required = True),
#         'an_toan_dich':fields.boolean('Được cấp An toàn dịch', readonly = True),
        'dien_tich': fields.char('Diện tích đất'),
        'lat':  fields.float(u'Tọa độ X', digits=(9, 6)),
        'lng': fields.float(u'Tọa độ Y', digits=(9, 6)),
        'loai_ho_id': fields.many2one('loai.ho','Loại hộ', required = True),
        'trang_thai_id': fields.many2one('trang.thai','Trạng thái', readonly=True),
        'hien_an': fields.function(_get_hien_an, type='boolean', string='Hien/An'),
        'chinh_sua_rel': fields.related('trang_thai_id', 'chinh_sua', type="selection",
                selection=[('nhap', 'Nháp'),('in', 'Đang xử lý'), ('ch_duyet', 'Cấp Huyện Duyệt'), ('cc_duyet', 'Chi Cục Duyệt'), ('huy', 'Hủy bỏ')], 
                string="Chinh Sua", readonly=True, select=True),
        'loai_hinh_so_huu_id':fields.many2one('loai.hinh.so.huu','Loại hình sở hữu', required = True),
        'cty_gia_cong_ids': fields.many2many('cty.gia.cong', 'chan_nuoi_cong_ty_ref', 'chan_nuoi_id', 'cong_ty_id', 'Cty được gia công'),
#         'cty_gia_cong_id':fields.many2one('cty.gia.cong','Cty được gia công'),
        'quy_cach': fields.selection([('ho', 'Trại hở'),('lanh', 'Trại lạnh')],'Quy cách chuồng trại'),
        'xu_ly_moi_truong_ids': fields.many2many('xu.ly.moi.truong','chan_nuoi_xu_ly_ref','chan_nuoi_id','xu_ly_id','Xử lý môi trường',required=True),
        'bao_ve_moi_truong':fields.selection([('co', 'Có'),('khong', 'Không')],'Cam kết bảo vệ MT'),
        'danh_gia_moi_truong':fields.selection([('co', 'Có'),('khong', 'Không')],'Đánh giá tác động MT'),
        'san_xuat_giong_id':fields.many2one('san.xuat.giong','Cơ sở sản xuất giống'),
        'tieu_chuan_viet':fields.boolean('VietGAHP'),
        'tieu_chuan_global':fields.boolean('Tiêu chuẩn Global GAP'),
        'an_toan_dich':fields.boolean('Cơ sở An toàn dịch'),
        'du_dk_thu_y':fields.boolean('Đủ điều kiện vệ sinh thú y'),
        'tieu_chuan_khac':fields.boolean('Tiêu chuẩn khác'),
        'active':fields.boolean('Active'),
        'dien_tich_chuong':fields.char('Diện tích chuồng trại'),
        'mo_ta':fields.text('Mô tả'),
                }

    _defaults = {
        'trang_thai_id': get_trangthai_nhap,
        'an_toan_dich':False,
        'tieu_chuan_viet':False,
        'tieu_chuan_global':False,
        'tieu_chuan_khac':False,
        'du_dk_thu_y':False,
        'active':True,
        
                 }
    
    def _check_ma_ho(self, cr, uid, ids, context=None):
        for ho in self.browse(cr, uid, ids, context=context):
            ho_ids = self.search(cr,uid,[('id', '!=', ho.id), ('ma_ho', '=', ho.ma_ho)])
            if ho_ids:
                raise osv.except_osv(_('Warning!'),_('Mã hộ không được trùng nhau'))
                return False
        return True
         
    _constraints = [
        (_check_ma_ho, 'Identical Data', []),
    ]   

    def bt_active(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'active':False})  

    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('search_ten_ho_id'):
            sql = '''
                select id from chan_nuoi
                where trang_thai_id in (select id from trang_thai where stt = 3)
            '''
            cr.execute(sql)
            chan_nuoi_ids = [row[0] for row in cr.fetchall()]
            args += [('id','in',chan_nuoi_ids)]
        
        if context.get('search_ten_ho_id_wizard'):
            if context.get('quan_huyen_id') and not context.get('phuong_xa_id') and not context.get('khu_pho_id'):
                sql = '''
                    select id from chan_nuoi
                    where trang_thai_id in (select id from trang_thai where stt = 3) and quan_huyen_id = %s
                '''%(context.get('quan_huyen_id'))
                cr.execute(sql)
                chan_nuoi_ids = [row[0] for row in cr.fetchall()]
              
            elif context.get('quan_huyen_id') and context.get('phuong_xa_id') and not context.get('khu_pho_id'):
                sql = '''
                    select id from chan_nuoi
                    where trang_thai_id in (select id from trang_thai where stt = 3) and quan_huyen_id = %s and phuong_xa_id = %s
                '''%(context.get('quan_huyen_id'), context.get('phuong_xa_id'))
                cr.execute(sql)
                chan_nuoi_ids = [row[0] for row in cr.fetchall()]
                  
            elif context.get('quan_huyen_id') and context.get('phuong_xa_id') and context.get('khu_pho_id'):
                sql = '''
                    select id from chan_nuoi
                    where trang_thai_id in (select id from trang_thai where stt = 3) and quan_huyen_id = %s and phuong_xa_id = %s and khu_pho_id = %s
                '''%(context.get('quan_huyen_id'), context.get('phuong_xa_id'), context.get('khu_pho_id'))
                cr.execute(sql)
                chan_nuoi_ids = [row[0] for row in cr.fetchall()]
             
            elif not context.get('quan_huyen_id') and not context.get('phuong_xa_id') and not context.get('khu_pho_id'):
                sql = '''
                    select id from chan_nuoi
                    where trang_thai_id in (select id from trang_thai where stt = 3)
                '''
                cr.execute(sql)
                chan_nuoi_ids = [row[0] for row in cr.fetchall()]
            
            args += [('id','in',chan_nuoi_ids)]
            
            
        return super(chan_nuoi, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
       ids = self.search(cr, user, args, context=context, limit=limit)
       return self.name_get(cr, user, ids, context=context)

#     def bt_an_toan_dich(self, cr, uid, ids, context=None):
#         user = self.pool.get('res.users').browse(cr,uid,uid)
#         for line in self.browse(cr, uid, ids, context=context):
#            if line.an_toan_dich == False:
#                self.write(cr,uid,ids,{
#                                        'an_toan_dich': True,
#                                        })
#         return True
    
    def bt_duyet(self, cr, uid, ids, context=None):
        user = self.pool.get('res.users').browse(cr,uid,uid)
        for line in self.browse(cr, uid, ids, context=context):
            if line.trang_thai_id.stt == 1 and user.company_id.cap == 'huyen':
                sql = '''
                    select id from trang_thai where stt = 2
                '''
                cr.execute(sql)
                self.write(cr,uid,ids,{
                                       'trang_thai_id': cr.dictfetchone()['id'] or False
                                       })
                for nhap in line.nhap_dongvat_line:
                    self.pool.get('nhap.xuat.canh.giasuc').bt_duyet(cr,uid,[nhap.id])
            elif line.trang_thai_id.stt == 1 and user.company_id.cap == 'chi_cuc':
                sql = '''
                    select id from trang_thai where stt = 3
                '''
                cr.execute(sql)
                self.write(cr,uid,ids,{
                                       'trang_thai_id': cr.dictfetchone()['id'] or False
                                       })
                for nhap in line.nhap_dongvat_line:
                    self.pool.get('nhap.xuat.canh.giasuc').bt_duyet(cr,uid,[nhap.id])
            elif line.trang_thai_id.stt == 2 and user.company_id.cap == 'chi_cuc':
                sql = '''
                    select id from trang_thai where stt = 3
                '''
                cr.execute(sql)
                self.write(cr,uid,ids,{
                                       'trang_thai_id': cr.dictfetchone()['id'] or False
                                       })
                for nhap in line.nhap_dongvat_line:
                    self.pool.get('nhap.xuat.canh.giasuc').bt_duyet(cr,uid,[nhap.id])
        return True
chan_nuoi()

class phuong_xa(osv.osv):
    _name = "phuong.xa"
    _columns = {
        'name': fields.char('Phường (xã)',size = 50, required = True),
         'quan_huyen_id': fields.many2one( 'quan.huyen','Quận (huyện)', required = True),
                }
phuong_xa()
class quan_huyen(osv.osv):
    _name = "quan.huyen"
    _columns = {
        'name': fields.char('Quận (huyện)',size = 50, required = True),
        'tinh_thanh_id':fields.many2one('tinh.tp','Thuộc Tỉnh/Thành phố', required = True),
                }
quan_huyen()
class khu_pho(osv.osv):
    _name = "khu.pho"
    _columns = {
        'name': fields.char('Khu phố (ấp)',size = 50, required = True),
        'quan_huyen_id': fields.many2one( 'quan.huyen','Quận (huyện)', required = True),
        'phuong_xa_id': fields.many2one( 'phuong.xa','Phường (xã)', required = True),
                }
khu_pho()
class loai_hang(osv.osv):
    _name = "loai.hang"
    _columns = {
        'name': fields.char('Loại hàng',size = 50, required = True),
        'don_vi': fields.char('Đơn vị tính',size = 50),
                }
loai_hang()

class loai_vacxin(osv.osv):
    _name = "loai.vacxin"
    _columns = {
        'name': fields.char('Tên loại vacxin',size = 50, required = True),
                }
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        loai_vacxin_ids =[]
        if context is None:
            context = {}
        if context.get('search_vacxin_id'):
            if context.get('loai_id'):
                sql = '''
                    select vacxin_id from chi_tiet_loai_vacxin
                    where loai_id = %s and yes_no = True
                '''%(context.get('loai_id'))
                cr.execute(sql)
                loai_vacxin_ids = [row[0] for row in cr.fetchall()]
                args += [('id','in',loai_vacxin_ids)]
        return super(loai_vacxin, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
       ids = self.search(cr, user, args, context=context, limit=limit)
       return self.name_get(cr, user, ids, context=context)
loai_vacxin()

class loai_ho(osv.osv):
    _name = "loai.ho"
    _columns = {
        'name': fields.char('Loại hộ',size = 50, required = True),
                }
loai_ho()

class xu_ly_moi_truong(osv.osv):
    _name = "xu.ly.moi.truong"
    _columns = {
        'name': fields.char('Tên loại xử lý',size = 50, required = True),
                }
xu_ly_moi_truong()

class san_xuat_giong(osv.osv):
    _name = "san.xuat.giong"
    _columns = {
        'name': fields.char('Tên hướng sản xuất',size = 50, required = True),
                }
san_xuat_giong()


class loai_giay_tiem_phong(osv.osv):
    _name = "loai.giay.tiem.phong"
    _columns = {
        'name': fields.char('Loại giấy tiêm phòng',size = 50, required = True),
                }
loai_giay_tiem_phong()

class don_vi_tinh(osv.osv):
    _name = "don.vi.tinh"
    _columns = {
        'name': fields.char('Đơn vị tính',size = 50, required = True),
                }
    def create(self, cr, uid, vals, context=None):
        if 'name' in vals:
            name = vals['name'].replace(" ","")
            vals['name'] = name
        return super(don_vi_tinh, self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'name' in vals:
            name = vals['name'].replace(" ","")
            vals['name'] = name
        return super(don_vi_tinh, self).write(cr, uid,ids, vals, context)    

    def _check_dvt(self, cr, uid, ids, context=None):
        for dvt in self.browse(cr, uid, ids, context=context):
            dvt_ids = self.search(cr,uid,[('id', '!=', dvt.id), ('name', '=', dvt.name)])
            sql = '''
                select id from don_vi_tinh where id != %s and lower(name) = lower('%s')
            '''%(dvt.id,dvt.name)
            cr.execute(sql)
            lower_ids = [row[0] for row in cr.fetchall()]
            if dvt_ids or lower_ids:
                raise osv.except_osv(_('Warning!'),_('Tên ĐVT không được trùng nhau'))
                return False
        return True
    _constraints = [
        (_check_dvt, 'Identical Data', []),
    ]   
    
    
don_vi_tinh()

class loai_hoa_chat(osv.osv):
    _name = "loai.hoa.chat"
    _columns = {
        'name': fields.char('Tên hoá chất',size = 50, required = True),
                }
loai_hoa_chat()

class loai_hinh_so_huu(osv.osv):
    _name = "loai.hinh.so.huu"
    _columns = {
        'name': fields.char('Tên loại hình sở hữu',size = 50, required = True),
                }
loai_hinh_so_huu()

class cty_gia_cong(osv.osv):
    _name = "cty.gia.cong"
    _columns = {
        'name': fields.char('Tên Công Ty',size = 50, required = True),
                }
cty_gia_cong()

class baocao_coso_channuoi_map(osv.osv):
    _name = "baocao.coso.channuoi.map"
    _columns = {
        'lat': fields.float(u'Tọa độ X', digits=(9, 6)),
        'lng': fields.float(u'Tọa độ Y', digits=(9, 6)),
        'radius': fields.float(u'Bán kính', digits=(9, 6)),
        'map': fields.dummy(),
        'points': fields.text('Points'),
        'user_id': fields.many2one('res.users','Người tạo'),
    }
    
    _defaults = {
        'user_id': lambda self, cr, uid, context: uid,
    }
    
    def onchange_toado_bankinh(self, cr, uid, ids, lat=False, lng=False, radius=False, context=None):
        vals = {}
        if lat and lng and radius:
            sql = '''
                select lat,lng,mo_ta from chan_nuoi where lat is not null and lat!=0 and lng is not null and lng!=0 and ((lat-%s)^2+(lng-%s)^2<=%s)
            '''%(lat,lng,radius**2/1000000)
            cr.execute(sql)
            points = ''
            for channuoi in cr.dictfetchall():
                points+=str(channuoi['lat'])+'phung_cat_giatri'+str(channuoi['lng'])+'phung_cat_giatri'+(channuoi['mo_ta'] or '')+'phung_cat_diem'
            if points:
                points=points[:-14]
            vals = {'points':points}
        return {'value': vals}
    
baocao_coso_channuoi_map()

class res_partner(osv.osv):
    _inherit = 'res.partner'

    def write_radius(self, cr, uid, id,active_model, vals, context=None):
        res = super(res_partner, self).write_radius(cr, uid, id,active_model, vals, context)
        if vals.get('radius',False) and active_model=='baocao.coso.channuoi.map':
            channuoi_map_obj = self.pool.get('baocao.coso.channuoi.map')
            line = channuoi_map_obj.browse(cr, uid, int(id))
            vals.update(channuoi_map_obj.onchange_toado_bankinh( cr, uid, [], line.lat, line.lng, vals['radius'],context)['value'])
            channuoi_map_obj.write(cr, uid, [int(id)], vals, context)
        return res
    
    def write_center(self, cr, uid, id,active_model, vals, context=None):
        res = super(res_partner, self).write_center(cr, uid, id,active_model, vals, context)
        if vals.get('center',False) and active_model=='baocao.coso.channuoi.map':
            channuoi_map_obj = self.pool.get('baocao.coso.channuoi.map')
            line = channuoi_map_obj.browse(cr, uid, int(id))
            vals.update(channuoi_map_obj.onchange_toado_bankinh( cr, uid, [], vals['center']['G'], vals['center']['K'], line.radius,context)['value'])
            vals.update({'lat':vals['center']['G'],'lng':vals['center']['K']})
            channuoi_map_obj.write(cr, uid, [int(id)], vals, context)
        return res
    
res_partner()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
