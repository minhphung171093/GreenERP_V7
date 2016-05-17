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


class res_partner_bank(osv.osv):
    _inherit = "res.partner.bank"
    _columns = {
        'kichhoat': fields.boolean('Kích hoạt'),
    }
res_partner_bank()

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
        'name_eng':fields.char('Tên tiếng Anh',size=1024,required=True),
        'description': fields.text('Ghi chú'),
    }
    
#     def name_get(self, cr, uid, ids, context=None):
#         res = []
#         if not ids:
#             return res
#         for line in self.browse(cr,uid,ids):
#             if context.get('ten_ngoai',False):
#                 cate_name = line.name_eng
#                 res.append((line.id,cate_name))
#         return res 

           
chatluong_sanpham()
class quycach_donggoi(osv.osv):
    _name = 'quycach.donggoi'
    _columns = {
        'name':fields.char('Tên',size=1024,required=True),
        'name_eng':fields.char('Tên tiếng Anh',size=1024,required=True),
        'description': fields.text('Ghi chú'),
    }
    
quycach_donggoi()
class bank_detail(osv.osv):
    _name = 'bank.detail'
    _columns = {
        'name':fields.char('Bank name',size=1024,required=True),
        'swift_code':fields.char('Swift Code',size=1024,required=True),
        'account_no':fields.char('Account No',size=1024,required=True),
        'address':fields.text('Address'),
    }
    
bank_detail()
class quycach_baobi(osv.osv):
    _name = 'quycach.baobi'
    _columns = {
        'name':fields.char('Tên',size=1024,required=True),
        'name_eng':fields.char('Tên tiếng Anh',size=1024,required=True),
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
        'name':fields.char('Term',size=1024,required=True),
        'discharge':fields.char('Discharge',size=1024,required=True),
        'description': fields.text('Ghi chú'),
    }
    
    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        reads = self.read(cr, uid, ids, ['name','discharge'], context=context)
        res = []
        for record in reads:
            name = record['name'] + ' ' + record['discharge']
            res.append((record['id'], name))
        return res
    
dieukien_giaohang()

class chat_luong(osv.osv):
    _name = 'chat.luong'
    _columns = {
        'name':fields.text('Chất lượng',size=1024,required=True),
    }
    
chat_luong()


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

class shipping_line(osv.osv):
    _name = 'shipping.line'
    _columns = {
        'name':fields.char('Name',size=1024,required=True),
        'description': fields.text('Description'),
    }
    
shipping_line()

class forwarder_line(osv.osv):
    _name = 'forwarder.line'
    _columns = {
        'name':fields.char('Name',size=1024,required=True),
        'description': fields.text('Description'),
    }
    
forwarder_line()

class so_hopdong(osv.osv):
    _name = 'so.hopdong'
    def _get_nam(self, cr, uid, ids, context=None):
        curent_date = time.strftime('%Y-%m-%d')
        nam = curent_date[:4]
        return nam
    
    _columns = {
        'name':fields.integer('Số hợp đồng ngoại',required=True, states={'da_duyet': [('readonly', True)]}),
        'nam': fields.char('Năm',readonly=True),
        'state': fields.selection([
            ('moi_tao', 'Mới tạo'),
            ('da_duyet', 'Đã duyệt'),
            ], 'Trạng thái',readonly=True, states={'moi_tao': [('readonly', False)]}),
    }
    _defaults = {
        'nam':_get_nam,
        'state':'moi_tao',
                 }
    def duyet(self, cr, uid, ids, context=None):
        hopdong_model, hd_ngoai_id = self.pool.get('ir.model.data').get_object_reference(cr,uid, 'green_erp_viruco_base', 'sequence_hopdong_ngoai_1_item')
        self.pool.get('ir.sequence').check_access_rule(cr,uid, [hd_ngoai_id], 'read', context = context)
        for line in self.browse(cr,uid,ids):
            curent_date = time.strftime('%Y-%m-%d')
            nam = curent_date[:4]
            if nam == line.nam:
                self.pool.get('ir.sequence').write(cr,uid,[hd_ngoai_id],{'number_next_actual':line.name})
        return self.write(cr, uid, ids, {'state': 'da_duyet'})
    
so_hopdong()

class dk_thanhtoan(osv.osv):
    _name = 'dk.thanhtoan'
    _columns = {
        'name':fields.char('Name',size=1024,required=True),
        'description': fields.text('Description'),
        'dat_coc': fields.float('Giá trị đặt cọc'),
        'loai': fields.selection([
            ('lc', 'LC'),
            ('dp', 'DP'),
            ], 'Loại',required=True),
    }
    _defaults={
        'dat_coc':0.0,
               }
    
dk_thanhtoan()

class hd_incoterm(osv.osv):
    _name = 'hd.incoterm'
    _columns = {
        'name':fields.char('Name',size=1024,required=True),
        'description': fields.text('Description'),
    }
    
hd_incoterm()
class bang_gia(osv.osv):
    _name = 'bang.gia'
    _columns = {
        'name':fields.char('Tên',readonly=True),
        'date_start':fields.date('Từ ngày',required=True,readonly=True, states={'moi_tao': [('readonly', False)]}),
        'date_end':fields.date('Đến ngày',required=True,readonly=True, states={'moi_tao': [('readonly', False)]}),
        'currency_id': fields.many2one('res.currency', 'Đơn vị tiền tệ', required=True,readonly=True, states={'moi_tao': [('readonly', False)]}),
        'banggia_line': fields.one2many('bang.gia.line', 'banggia_id', 'Chi tiết bảng giá',readonly=True, states={'moi_tao': [('readonly', False)]}),
        'type': fields.selection([('mua','Mua'),('ban','Bán')],'Loại bảng giá'),
        'ghi_chu':fields.text('Ghi Chú',states={'moi_tao': [('readonly', False)]}),
        'state': fields.selection([
            ('moi_tao', 'Mới tạo'),
            ('da_duyet', 'Đã duyệt'),
            ('huy_bo', 'Hủy bỏ'),
            ], 'Trạng thái',readonly=True, states={'moi_tao': [('readonly', False)]}),
    }
    
    _defaults = {
        'date_start': lambda *a: time.strftime('%Y-%m-%d'),
        'date_end': lambda *a: time.strftime('%Y-%m-%d'),
        'state': 'moi_tao',
    }
    
    def _check_bg(self,cr,uid,ids):
        bg = self.browse(cr,uid,ids[0])
        sql = '''
            select id from bang_gia where id!=%s and currency_id=%s and type = '%s' and (date_start between '%s' and '%s' or date_end between '%s' and '%s')
        '''%(bg.id,bg.currency_id.id,bg.type,bg.date_start,bg.date_end,bg.date_start,bg.date_end)
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

    def create(self, cr, uid, vals, context=None):
        if 'type' in vals:
            if (vals['type']=='ban'):
                currency_obj = self.pool.get('res.currency')
                currency = currency_obj.browse(cr, uid, vals['currency_id'])
                vals['name'] =  u'Bảng giá bán công bố'+u' ('+currency.name+u')'
            if (vals['type']=='mua'):
                currency_obj = self.pool.get('res.currency')
                currency = currency_obj.browse(cr, uid, vals['currency_id'])
                vals['name'] =  u'Bảng giá mua công bố'+u' ('+currency.name+u')'
        new_id = super(bang_gia, self).create(cr, uid, vals, context=context)    
        return new_id

    def write(self, cr, uid, ids, vals, context=None):
        for line in self.browse(cr,uid,ids):
            if line.type=='ban':
                line.name =  u'Bảng giá bán công bố'+u' ('+line.currency_id.name+u')'
            if line.type=='mua':
                line.name =  u'Bảng giá mua công bố'+u' ('+line.currency_id.name+u')'
        new_write = super(bang_gia, self).write(cr, uid, ids, vals, context=context)    
        return new_write  
    
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
                        'nha_sanxuat_id': line.nha_sanxuat_id and line.nha_sanxuat_id.id or False,
                        'chatluong_id': line.chatluong_id and line.chatluong_id.id or False,
                        'quycach_donggoi_id': line.quycach_donggoi_id and line.quycach_donggoi_id.id or False,
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
#                 else:
#                     product_pricelist_id = product_pricelist_ids[0]
                 
#                 items = []
#                 for line in bg.banggia_line:
#                     items.append((0,0,{
#                         'name': line.product_id.name,
#                         'product_id': line.product_id.id,
#                         'base': 1,
#                         'price_surcharge': line.gia,
#                     }))
                     
                    product_pricelist_version_obj.create(cr, uid, {
                        'pricelist_id':product_pricelist_id,
                        'name': 'Bảng giá bán từ ngày '+bg.date_start[8:10]+'/'+bg.date_start[5:7]+'/'+bg.date_start[:4]+' đến ngày '+bg.date_end[8:10]+'/'+bg.date_end[5:7]+'/'+bg.date_end[:4],
    #                     'date_start': bg.date_start,
    #                     'date_end': bg.date_end,
    #                     'items_id': items,
                    })
            if bg.type=='mua':
                product_pricelist_ids = product_pricelist_obj.search(cr, uid, [('currency_id','=',bg.currency_id.id),('type','=','purchase')])
                if not product_pricelist_ids:
                    product_pricelist_id = product_pricelist_obj.create(cr, uid, {'name': 'Public Pricelist',
                                                                                  'type':'purchase',
                                                                                  'currency_id':bg.currency_id.id})
#                 else:
#                     product_pricelist_id = product_pricelist_ids[0]
                 
#                 items = []
#                 for line in bg.banggia_line:
#                     items.append((0,0,{
#                         'name': line.product_id.name,
#                         'product_id': line.product_id.id,
#                         'base': 1,
#                         'price_surcharge': line.gia,
#                     }))
                     
                    product_pricelist_version_obj.create(cr, uid, {
                        'pricelist_id':product_pricelist_id,
                        'name': 'Bảng giá mua từ ngày '+bg.date_start[8:10]+'/'+bg.date_start[5:7]+'/'+bg.date_start[:4]+' đến ngày '+bg.date_end[8:10]+'/'+bg.date_end[5:7]+'/'+bg.date_end[:4],
    #                     'date_start': bg.date_start,
    #                     'date_end': bg.date_end,
    #                     'items_id': items,
                    })
            
        return self.write(cr, uid, ids, {'state': 'da_duyet'})
    
    def huy_bo(self, cr, uid, ids, context=None):
#         product_pricelist_version_obj = self.pool.get('product.pricelist.version')
#         product_pricelist_obj = self.pool.get('product.pricelist')
#         for bg in self.browse(cr, uid, ids):
#             if bg.type=='ban':
#                 product_pricelist_ids = product_pricelist_obj.search(cr, uid, [('currency_id','=',bg.currency_id.id),('type','=','sale')])
#                 product_pricelist_version_ids = product_pricelist_version_obj.search(cr, uid, [('pricelist_id','in', product_pricelist_ids),('date_start','=', bg.name),('date_end','=', bg.name)])
#                 product_pricelist_version_obj.unlink(cr, uid, product_pricelist_version_ids)
#             if bg.type=='mua':
#                 product_pricelist_ids = product_pricelist_obj.search(cr, uid, [('currency_id','=',bg.currency_id.id),('type','=','purchase')])
#                 product_pricelist_version_ids = product_pricelist_version_obj.search(cr, uid, [('pricelist_id','in', product_pricelist_ids),('date_start','=', bg.name),('date_end','=', bg.name)])
#                 product_pricelist_version_obj.unlink(cr, uid, product_pricelist_version_ids)
        return self.write(cr, uid, ids, {'state': 'huy_bo'})
    
    def chinh_sua_lai(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'moi_tao'})

    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        
        if context.get('search_banggia_mua_id'):
            banggia_ids = []
            if context.get('ngay') and context.get('currency_company_id'):
                sql = '''
                    select id from bang_gia
                        where type = 'mua' and currency_id = %s and state in ('da_duyet') and ('%s' between date_start and date_end)
                '''%(context.get('currency_company_id'),context.get('ngay'))
                cr.execute(sql)
                banggia_ids = [row[0] for row in cr.fetchall()]
            args += [('id','in',banggia_ids)]
        if context.get('search_banggia_mua_ngoai_id'):
            banggia_ids = []
            if context.get('ngay') and context.get('currency_company_id'):
                sql = '''
                    select id from bang_gia
                        where type = 'mua' and currency_id != %s and state in ('da_duyet') and ('%s' between date_start and date_end)
                '''%(context.get('currency_company_id'),context.get('ngay'))
                cr.execute(sql)
                banggia_ids = [row[0] for row in cr.fetchall()]
            args += [('id','in',banggia_ids)]
        if context.get('search_banggia_ban_id'):
            banggia_ids = []
            if context.get('ngay') and context.get('currency_company_id'):
                sql = '''
                    select id from bang_gia
                        where type = 'ban' and currency_id = %s and state in ('da_duyet') and ('%s' between date_start and date_end)
                '''%(context.get('currency_company_id'),context.get('ngay'))
                cr.execute(sql)
                banggia_ids = [row[0] for row in cr.fetchall()]
            args += [('id','in',banggia_ids)]
        if context.get('search_banggia_ban_ngoai_id'):
            banggia_ids = []
            if context.get('ngay') and context.get('currency_company_id'):
                sql = '''
                    select id from bang_gia
                        where type = 'ban' and currency_id != %s and state in ('da_duyet') and ('%s' between date_start and date_end)
                '''%(context.get('currency_company_id'),context.get('ngay'))
                cr.execute(sql)
                banggia_ids = [row[0] for row in cr.fetchall()]
            args += [('id','in',banggia_ids)]
        return super(bang_gia, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
       ids = self.search(cr, user, args, context=context, limit=limit)
       return self.name_get(cr, user, ids, context=context)
    
bang_gia()

class bang_gia_line(osv.osv):
    _name = 'bang.gia.line'
    _columns = {
        'banggia_id': fields.many2one('bang.gia', 'Bảng giá', ondelete='cascade'),
        'product_id': fields.many2one('product.product', 'Sản phẩm', required=True),
        'nha_sanxuat_id': fields.many2one('nha.sanxuat', 'Nhà sản xuất'),
        'chatluong_id': fields.many2one('chatluong.sanpham', 'Chất lượng'),
        'quycach_donggoi_id': fields.many2one('quycach.donggoi', 'Đóng gói'),        
        'gia': fields.float('Giá', required=True),
    }
    
bang_gia_line()
class bang_tam_init(osv.osv):
    _name = 'bang.tam.init'

    _columns = {
        'name': fields.char('Ten OBJ', size=1024),
        'da_chay': fields.boolean('Đã chạy'),
    }
bang_tam_init()

class port_of_loading(osv.osv):
    _name = 'port.of.loading'
    _columns = {
        'name':fields.char('Name',size=1024,required=True),
        'descrip': fields.text('Description'),
    }
port_of_loading()

class port_of_discharge(osv.osv):
    _name = 'port.of.discharge'
    _columns = {
        'name':fields.char('Name',size=1024,required=True),
        'descrip': fields.text('Description'),
    }
port_of_discharge()

class place_of_delivery(osv.osv):
    _name = 'place.of.delivery'
    _columns = {
        'name':fields.char('Name',size=1024,required=True),
        'descrip': fields.text('Description'),
    }
place_of_delivery()

class destination_port(osv.osv):
    _name = 'destination.port'
    _columns = {
        'name':fields.char('Name',size=1024,required=True),
        'descrip': fields.text('Description'),
    }
destination_port()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
