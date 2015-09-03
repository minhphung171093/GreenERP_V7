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
from xlrd import open_workbook,xldate_as_tuple
from openerp import modules
base_path = os.path.dirname(modules.get_module_path('green_erp_viruco_base'))


class res_country_state(osv.osv):
    _inherit = "res.country.state"
    _columns = {
    }
    def init(self, cr):
        country_obj = self.pool.get('res.country')
        wb = open_workbook(base_path + '/green_erp_viruco_base/data/TinhTP.xls')
        for s in wb.sheets():
            if (s.name =='Sheet1'):
                for row in range(1,s.nrows):
                    val0 = s.cell(row,0).value
                    val1 = s.cell(row,1).value
                    val2 = s.cell(row,2).value
                    country_ids = country_obj.search(cr, 1, [('code','=',val2)])
                    if country_ids:
                        state_ids = self.search(cr, 1, [('name','=',val1),('code','=',val0),('country_id','in',country_ids)])
                        if not state_ids:
                            self.create(cr, 1, {'name': val1,'code':val0,'country_id':country_ids[0]})
          
res_country_state()

class sale_arbitration(osv.osv):
    _name = 'sale.arbitration'
    _columns = {
        'name':fields.char('Name',size=1024,required=True),
        'description': fields.text('Description'),
    }
    
sale_arbitration()
class chatluong_sanpham(osv.osv):
    _name = 'chatluong.sanpham'
    _columns = {
        'name':fields.char('Tên',size=1024,required=True),
        'description': fields.text('Ghi chú'),
    }
    
chatluong_sanpham()
class quycach_donggoi(osv.osv):
    _name = 'quycach.donggoi'
    _columns = {
        'name':fields.char('Tên',size=1024,required=True),
        'description': fields.text('Ghi chú'),
    }
    
quycach_donggoi()
class quycach_baobi(osv.osv):
    _name = 'quycach.baobi'
    _columns = {
        'name':fields.char('Tên',size=1024,required=True),
        'description': fields.text('Ghi chú'),
    }
    
quycach_baobi()
class nha_sanxuat(osv.osv):
    _name = 'nha.sanxuat'
    _columns = {
        'name':fields.char('Tên nhà sản xuất',size=1024,required=True),
        'description': fields.text('Ghi chú'),
    }
    
nha_sanxuat()

class noi_giaohang(osv.osv):
    _name = 'noi.giaohang'
    _columns = {
        'name':fields.char('Địa điểm',size=1024,required=True),
        'description': fields.text('Ghi chú'),
    }
    
noi_giaohang()

class dieukien_giaohang(osv.osv):
    _name = 'dieukien.giaohang'
    _columns = {
        'name':fields.char('Điều kiện',size=1024,required=True),
        'description': fields.text('Ghi chú'),
    }
    
dieukien_giaohang()


class hinhthuc_giaohang(osv.osv):
    _name = 'hinhthuc.giaohang'
    _columns = {
        'name':fields.char('Tên',size=1024,required=True),
        'description': fields.text('Ghi chú'),
    }
    
hinhthuc_giaohang()

class lo_trinh(osv.osv):
    _name = 'lo.trinh'
    _columns = {
        'name':fields.char('Name',size=1024,required=True),
        'diadiem_tu':fields.char('Từ',size=1024,required=True),
        'diadiem_den':fields.char('Đến',size=1024,required=True),
        'description': fields.text('Description'),
    }
    
lo_trinh()
class cang_donghang(osv.osv):
    _name = 'cang.donghang'
    _columns = {
        'name':fields.char('Name',size=1024,required=True),
        'description': fields.text('Description'),
    }
    
cang_donghang()

class bang_gia(osv.osv):
    _name = 'bang.gia'
    _columns = {
        'date_start':fields.date('Từ ngày',required=True,readonly=True, states={'moi_tao': [('readonly', False)]}),
        'date_end':fields.date('Đến ngày',required=True,readonly=True, states={'moi_tao': [('readonly', False)]}),
        'currency_id': fields.many2one('res.currency', 'Đơn vị tiền tệ', required=True,readonly=True, states={'moi_tao': [('readonly', False)]}),
        'banggia_line': fields.one2many('bang.gia.line', 'banggia_id', 'Chi tiết bảng giá',readonly=True, states={'moi_tao': [('readonly', False)]}),
        'type': fields.selection([('mua','Mua'),('ban','Bán')],'Loại bảng giá'),
        'state': fields.selection([
            ('moi_tao', 'Mới tạo'),
            ('da_duyet', 'Đã duyệt'),
            ('huy_bo', 'Hủy bỏ'),
            ], 'Trạng thái',readonly=True, states={'moi_tao': [('readonly', False)]}),
    }
    
    _defaults = {
        'date_start': time.strftime('%Y-%m-%d'),
        'date_end': time.strftime('%Y-%m-%d'),
        'state': 'moi_tao',
    }
    
    def _check_bg(self,cr,uid,ids):
        bg = self.browse(cr,uid,ids[0])
        sql = '''
            select id from bang_gia where id!=%s and currency_id=%s and (date_start between '%s' and '%s' or date_end between '%s' and '%s')
        '''%(bg.id,bg.currency_id.id,bg.date_start,bg.date_end,bg.date_start,bg.date_end)
        cr.execute(sql)
        bg_ids = [r[0] for r in cr.fetchall()]
        if bg_ids:
            if bg.type=='ban':
                raise osv.except_osv(_('Cảnh báo!'),_('Không thể tạo bảng giá bán cho cùng đơn vị tiền tệ có khoảng ngày trùng nhau!'))
            if bg.type=='mua':
                raise osv.except_osv(_('Cảnh báo!'),_('Không thể tạo bảng giá mua cho cùng đơn vị tiền tệ có khoảng ngày trùng nhau!'))
        return True
    _constraints = [
        (_check_bg, _(''), ['']),
    ]
    
    def onchange_name(self, cr, uid, ids, date_start=False, date_end=False, currency_id=False, context=None):
        vals = {}
        if date_start and currency_id:
            if ids:
                cr.execute('delete from bang_gia_line where banggia_id in %s',(tuple(ids),))
            old_banggia_ids = self.search(cr, uid, [('date_end','<',date_start),('currency_id','=',currency_id),('state','=','da_duyet')], order='date_end desc', limit=1)
            if old_banggia_ids:
                banggia = self.browse(cr, uid, old_banggia_ids[0])
                banggia_line = []
                for line in banggia.banggia_line:
                    banggia_line.append((0,0,{
                        'product_id': line.product_id.id,
                        'gia': line.gia,
                    }))
                vals = {'banggia_line': banggia_line} 
        return {'value': vals}

    def duyet(self, cr, uid, ids, context=None):
        product_pricelist_version_obj = self.pool.get('product.pricelist.version')
        product_pricelist_obj = self.pool.get('product.pricelist')
        for bg in self.browse(cr, uid, ids):
            if bg.type=='ban':
                product_pricelist_ids = product_pricelist_obj.search(cr, uid, [('currency_id','=',bg.currency_id.id),('type','=','sale')])
                if not product_pricelist_ids:
                    product_pricelist_id = product_pricelist_obj.create(cr, uid, {'name': 'Public Pricelist',
                                                                                  'type':'sale',
                                                                                  'currency_id':bg.currency_id.id})
                else:
                    product_pricelist_id = product_pricelist_ids[0]
                
                items = []
                for line in bg.banggia_line:
                    items.append((0,0,{
                        'name': line.product_id.name,
                        'product_id': line.product_id.id,
                        'base': 1,
                        'price_surcharge': line.gia,
                    }))
                    
                product_pricelist_version_obj.create(cr, uid, {
                    'pricelist_id':product_pricelist_id,
                    'name': 'Bảng giá ngày '+bg.name[8:10]+'/'+bg.name[5:7]+'/'+bg.name[:4],
                    'date_start': bg.name,
                    'date_end': bg.name,
                    'items_id': items,
                })
            if bg.type=='mua':
                product_pricelist_ids = product_pricelist_obj.search(cr, uid, [('currency_id','=',bg.currency_id.id),('type','=','purchase')])
                if not product_pricelist_ids:
                    product_pricelist_id = product_pricelist_obj.create(cr, uid, {'name': 'Public Pricelist',
                                                                                  'type':'purchase',
                                                                                  'currency_id':bg.currency_id.id})
                else:
                    product_pricelist_id = product_pricelist_ids[0]
                
                items = []
                for line in bg.banggia_line:
                    items.append((0,0,{
                        'name': line.product_id.name,
                        'product_id': line.product_id.id,
                        'base': 1,
                        'price_surcharge': line.gia,
                    }))
                    
                product_pricelist_version_obj.create(cr, uid, {
                    'pricelist_id':product_pricelist_id,
                    'name': 'Bảng giá ngày '+bg.name[8:10]+'/'+bg.name[5:7]+'/'+bg.name[:4],
                    'date_start': bg.name,
                    'date_end': bg.name,
                    'items_id': items,
                })
            
        return self.write(cr, uid, ids, {'state': 'da_duyet'})
    
    def huy_bo(self, cr, uid, ids, context=None):
        product_pricelist_version_obj = self.pool.get('product.pricelist.version')
        product_pricelist_obj = self.pool.get('product.pricelist')
        for bg in self.browse(cr, uid, ids):
            if bg.type=='ban':
                product_pricelist_ids = product_pricelist_obj.search(cr, uid, [('currency_id','=',bg.currency_id.id),('type','=','sale')])
                product_pricelist_version_ids = product_pricelist_version_obj.search(cr, uid, [('pricelist_id','in', product_pricelist_ids),('date_start','=', bg.name),('date_end','=', bg.name)])
                product_pricelist_version_obj.unlink(cr, uid, product_pricelist_version_ids)
            if bg.type=='mua':
                product_pricelist_ids = product_pricelist_obj.search(cr, uid, [('currency_id','=',bg.currency_id.id),('type','=','purchase')])
                product_pricelist_version_ids = product_pricelist_version_obj.search(cr, uid, [('pricelist_id','in', product_pricelist_ids),('date_start','=', bg.name),('date_end','=', bg.name)])
                product_pricelist_version_obj.unlink(cr, uid, product_pricelist_version_ids)
        return self.write(cr, uid, ids, {'state': 'huy_bo'})
    
    def chinh_sua_lai(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'moi_tao'})
    
bang_gia()

class bang_gia_line(osv.osv):
    _name = 'bang.gia.line'
    _columns = {
        'banggia_id': fields.many2one('bang.gia', 'Bảng giá', ondelete='cascade'),
        'product_id': fields.many2one('product.product', 'Sản phẩm', required=True),
        'gia': fields.float('Giá', required=True),
    }
    
bang_gia_line()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
