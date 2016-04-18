# -*- coding: utf-8 -*-
import datetime
import time
from itertools import groupby
from operator import itemgetter

import math
from openerp import netsvc
from openerp import tools
from openerp.osv import fields, osv
from openerp.tools.translate import _

class res_partner(osv.osv):
    _inherit = "res.partner"
    _order = 'ma_daily'
    def _get_child_ids(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for record in self.browse(cr, uid, ids, context=context):
            if record.child_parent_ids:
                result[record.id] = [x.id for x in record.child_parent_ids]
            else:
                result[record.id] = []
        return result
    
    _columns = {
        'ma_daily': fields.char('Mã ĐL', size=128,required=True),
        'dai_ly': fields.boolean('Đại lý'),
        'parent_id': fields.many2one('res.partner','Đại lý cha', domain="[('dai_ly','=',True),('parent_id','=',False)]"),
        'child_parent_ids': fields.one2many('res.partner','parent_id','Children'),
        'child_id': fields.function(_get_child_ids, type='many2many', relation="res.partner", string="Child"),
        'external_id': fields.integer('ExternalID'),
    }
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('order_by_ma_daily'):
            order = 'ma_daily'
        return super(res_partner, self).search(cr, uid, args, offset, limit, order, context, count)
    
    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            name = record.name
            if record.parent_id and not record.is_company:
                name = "%s, %s" % (record.parent_name, name)
            if context.get('show_address'):
                name = name + "\n" + self._display_address(cr, uid, record, without_company=True, context=context)
                name = name.replace('\n\n','\n')
                name = name.replace('\n\n','\n')
            if context.get('show_email') and record.email:
                name = "%s <%s>" % (name, record.email)
            if record.ma_daily:
                name = '[%s] '%(record.ma_daily) + name
            res.append((record.id, name))
        return res
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if context is None:
            context = {}
        if not name:
            ids = self.search(cr, user, args, limit=limit, context=context)
        else:
            ids = self.search(cr, user, [('name',operator,name)] + args, limit=limit, context=context)
            if not ids:
                ids = self.search(cr, user, [('ma_daily',operator,name)] + args, limit=limit, context=context)
        return self.name_get(cr, user, ids, context=context)
    
res_partner()

class product_product(osv.osv):
    _inherit = "product.product"
    _columns = {
        'menh_gia': fields.boolean('Mệnh giá'),
        'external_id': fields.integer('ExternalID'),
    }
    
    def create(self, cr, uid, values, context=None):
        context = context or {}
        product_product_id = super(product_product, self).create(cr, uid, values, context)
        company = self.pool.get('res.users').browse(cr, uid, uid).company_id
        lichsu_dongbo_obj = self.pool.get('lichsu.dongbo')
        vals={
            'f_table': 'product_product',
            'f_object': 'product.product',
            'f_id': product_product_id,
            'company_id': company.id,
            'type': 'create',
            'state': 'waiting',
              }
        lichsu_dongbo_obj.create(cr, uid, vals, context)
        return product_product_id
    
    def write(self, cr, uid, ids, vals, context=None):
        context = context or {}
        super(product_product, self).write(cr, uid, ids, vals, context=context)
        update_fields = ''
        lichsu_dongbo_obj = self.pool.get('lichsu.dongbo')
        for key in vals.keys():
            update_fields += key+','
        if update_fields:
            update_fields = update_fields[:-1]
            company = self.pool.get('res.users').browse(cr, uid, uid).company_id
            for line in self.browse(cr, uid, ids):
                vals={
                'update_fields': update_fields,
                'f_table': 'product_product',
                'f_object': 'product.product',
                'f_id': line.id,
                'company_id': company.id,
                'type': 'write',
                'state': 'waiting',
                  }
                lichsu_dongbo_obj.create(cr, uid, vals, context)
        return True
    
    def unlink(self, cr, uid, ids, context=None):
        context = context or {}
        lichsu_dongbo_obj = self.pool.get('lichsu.dongbo')
        company = self.pool.get('res.users').browse(cr, uid, uid).company_id
        for line in self.browse(cr, uid, ids):
            vals={
                'f_table': 'product_product',
                'f_object': 'product.product',
                'f_id': line.external_id,
                'company_id': company.id,
                'type': 'unlink',
                'state': 'waiting',
                  }
            lichsu_dongbo_obj.create(cr, uid, vals, context)
        super(product_product, self).unlink(cr, uid, [line.id], context=context)
        return True
    
product_product()

class product_template(osv.osv):
    _inherit = "product.template"
    
    _columns = {
        'list_price': fields.float('Sale Price', digits=(16,7), help="Base price to compute the customer price. Sometimes called the catalog price."),
    }
    
product_template()

class dai_duthuong(osv.osv):
    _name = "dai.duthuong"
    _columns = {
        'name': fields.char('Tên',size=32,required=True),
        'ma': fields.char('Mã',size=32,required=True),
        'thu': fields.selection([('0','Chủ nhật'),('1','Thứ 2'),('2','Thứ 3'),('3','Thứ 4'),('4','Thứ 5'),('5','Thứ 6'),('6','Thứ 7')],'Thứ',required=True),
        'external_id': fields.integer('ExternalID'),
    }
    
    def create(self, cr, uid, values, context=None):
        context = context or {}
        dai_duthuong_id = super(dai_duthuong, self).create(cr, uid, values, context)
        company = self.pool.get('res.users').browse(cr, uid, uid).company_id
        lichsu_dongbo_obj = self.pool.get('lichsu.dongbo')
        vals={
            'f_table': 'dai_duthuong',
            'f_object': 'dai.duthuong',
            'f_id': dai_duthuong_id,
            'company_id': company.id,
            'type': 'create',
            'state': 'waiting',
              }
        lichsu_dongbo_obj.create(cr, uid, vals, context)
        return dai_duthuong_id
    
    def write(self, cr, uid, ids, vals, context=None):
        context = context or {}
        super(dai_duthuong, self).write(cr, uid, ids, vals, context=context)
        update_fields = ''
        lichsu_dongbo_obj = self.pool.get('lichsu.dongbo')
        for key in vals.keys():
            update_fields += key+','
        if update_fields:
            update_fields = update_fields[:-1]
            company = self.pool.get('res.users').browse(cr, uid, uid).company_id
            for line in self.browse(cr, uid, ids):
                vals={
                'update_fields': update_fields,
                'f_table': 'dai_duthuong',
                'f_object': 'dai.duthuong',
                'f_id': line.id,
                'company_id': company.id,
                'type': 'write',
                'state': 'waiting',
                  }
                lichsu_dongbo_obj.create(cr, uid, vals, context)
        return True
    
    def unlink(self, cr, uid, ids, context=None):
        context = context or {}
        lichsu_dongbo_obj = self.pool.get('lichsu.dongbo')
        company = self.pool.get('res.users').browse(cr, uid, uid).company_id
        for line in self.browse(cr, uid, ids):
            vals={
                'f_table': 'dai_duthuong',
                'f_object': 'dai.duthuong',
                'f_id': line.external_id,
                'company_id': company.id,
                'type': 'unlink',
                'state': 'waiting',
                  }
            lichsu_dongbo_obj.create(cr, uid, vals, context)
        super(dai_duthuong, self).unlink(cr, uid, [line.id], context=context)
        return True
    
dai_duthuong()

class ketqua_xoso(osv.osv):
    _name = "ketqua.xoso"
    _order = "name desc"
    
    def default_get(self, cr, uid, fields, context=None):
        res = super(ketqua_xoso, self).default_get(cr, uid, fields, context=context)
        vals = []
        
        for i in range(1,19):
            dm_7_so = False
            if i==1:
                name = 'Giải 8'
                ma = '01'
            elif i==2:
                name = 'Giải 7'
                ma = '02'
            elif i==3:
                name = 'Giải 6.1'
                ma = '03'
            elif i==4:
                name = 'Giải 6.2'
                ma = '04'
            elif i==5:
                name = 'Giải 6.3'
                ma = '05'
            elif i==6:
                name = 'Giải 5'
                ma = '06'
            elif i==7:
                name = 'Giải 4.1'
                ma = '07'
                dm_7_so = True
            elif i==8:
                name = 'Giải 4.2'
                ma = '08'
                dm_7_so = True
            elif i==9:
                name = 'Giải 4.3'
                ma = '09'
                dm_7_so = True
            elif i==10:
                name = 'Giải 4.4'
                ma = '10'
                dm_7_so = True
            elif i==11:
                name = 'Giải 4.5'
                ma = '11'
                dm_7_so = True
            elif i==12:
                name = 'Giải 4.6'
                ma = '12'
                dm_7_so = True
            elif i==13:
                name = 'Giải 4.7'
                ma = '13'
                dm_7_so = True
            elif i==14:
                name = 'Giải 3.1'
                ma = '14'
            elif i==15:
                name = 'Giải 3.2'
                ma = '15'
            elif i==16:
                name = 'Giải 2'
                ma = '16'
            elif i==17:
                name = 'Giải 1'
                ma = '17'
            else:
                name = 'Giải Đặt biệt'
                ma = '18'
            line_vals = {
                'name': name,
                'ma': ma,
                'dm_7_so': dm_7_so,
                  }
            vals.append((0,0,line_vals))
        res.update({
            'ketqua_xoso_line':vals,
            'name': time.strftime('%Y-%m-%d'),
            })
        return res
    
    _columns = {
        'name': fields.date('Ngày xổ số',required=True,states={'validate':[('readonly',True)]}),
        'dai_duthuong_id': fields.many2one('dai.duthuong','Đài dự thưởng',required=False,states={'validate':[('readonly',True)]}),
        'ketqua_xoso_line': fields.one2many('ketqua.xoso.line','ketqua_xoso_id','Line',states={'validate':[('readonly',True)]}),
        'state': fields.selection([('new','New'),('validate','Validate')],'Status'),
        'external_id': fields.integer('ExternalID'),
    }
    
    def create(self, cr, uid, vals, context=None):
        dem = 0
        for line in vals['ketqua_xoso_line']:
            if 'dm_7_so' in line[2] and line[2]['dm_7_so']==True:
                dem+=1
        if dem!=7:
            raise osv.except_osv(_('Cảnh báo!'),_('Chọn danh mục 7 số không đúng!'))
        return super(ketqua_xoso, self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        res = super(ketqua_xoso, self).write(cr, uid, ids, vals, context=context)
        for xoso in self.browse(cr, uid, ids, context):
            dem=0
            for line in xoso.ketqua_xoso_line:
                if line.dm_7_so==True:
                    dem+=1
            if dem!=7:
                raise osv.except_osv(_('Cảnh báo!'),_('Chọn danh mục 7 số không đúng!'))
        return res
    
    def _get_default_dai_duthuong(self, cr, uid, context=None):
        today = datetime.datetime.now().toordinal()
        dai_dt_ids = self.pool.get('dai.duthuong').search(cr, uid, [('thu','=',str(today%7))])
        return dai_dt_ids and dai_dt_ids[0] or False
    
    _defaults = {
        'state': 'new',
        'dai_duthuong_id': _get_default_dai_duthuong,
    }
    
    def onchange_ngay(self, cr, uid, ids, name=False, context=None):
        vals = {}
        if name:
            date = datetime.datetime.strptime(name,'%Y-%m-%d').toordinal()
            dai_dt_ids = self.pool.get('dai.duthuong').search(cr, uid, [('thu','=',str(date%7))])
            vals = {'dai_duthuong_id': dai_dt_ids and dai_dt_ids[0] or False}
        return {'value': vals}
    
    def validate_winning(self, cr, uid, ids, context=None):
        ve_loto_obj = self.pool.get('ve.loto')
        ve_loto_line_obj = self.pool.get('ve.loto.line')
        for xoso in self.browse(cr, uid, ids):
            self.pool.get('dongbo.veloto').create(cr, uid, {'name': xoso.name,'state':'waiting','ket_qua_id':xoso.id})
            self.pool.get('dongbo.daily.trungthuong').create(cr, uid, {'name': xoso.name,'state':'waiting','ket_qua_id':xoso.id})
            ve_loto_ids = ve_loto_obj.search(cr, uid, [('ngay','=',xoso.name),('state','=','new'),('parent_id','=',False)])
            if ve_loto_ids:
                for ketqua in xoso.ketqua_xoso_line:
                    for veloto in ve_loto_obj.browse(cr, uid, ve_loto_ids):
                        for line in veloto.ve_loto_2_line:
                            # 2 so
                            if ketqua.ma =='01' and ketqua.so==line.so_dt_2_d:
                                ve_loto_line_obj.write(cr, uid, [line.id], {'sl_2_d_trung':1})
                                
                            if ketqua.ma =='18' and ketqua.so[-2:]==line.so_dt_2_c:
                                ve_loto_line_obj.write(cr, uid, [line.id], {'sl_2_c_trung':1})
                            
                            sl_2_dc_trung = line.sl_2_dc_trung
                            if ketqua.ma =='01' and ketqua.so==line.so_dt_2_dc:
                                sl_2_dc_trung += 1
                            if ketqua.ma =='18' and ketqua.so[-2:]==line.so_dt_2_dc:
                                sl_2_dc_trung += 1
                            ve_loto_line_obj.write(cr, uid, [line.id], {'sl_2_dc_trung':sl_2_dc_trung})
                            
                            sl_2_18_trung = line.sl_2_18_trung
                            if ketqua.ma in ('01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18') and ketqua.so[-2:]==line.so_dt_2_18:
                                sl_2_18_trung+=1
                            ve_loto_line_obj.write(cr, uid, [line.id], {'sl_2_18_trung':sl_2_18_trung})
                            
                            # 3 so
                            if ketqua.ma =='02' and ketqua.so==line.so_dt_3_d:
                                ve_loto_line_obj.write(cr, uid, [line.id], {'sl_3_d_trung':1})
                                
                            if ketqua.ma =='18' and ketqua.so[-3:]==line.so_dt_3_c:
                                ve_loto_line_obj.write(cr, uid, [line.id], {'sl_3_c_trung':1})
                            
                            sl_3_dc_trung = line.sl_3_dc_trung
                            if ketqua.ma =='02' and ketqua.so==line.so_dt_3_dc:
                                sl_3_dc_trung += 1
                            if ketqua.ma =='18' and ketqua.so[-3:]==line.so_dt_3_dc:
                                sl_3_dc_trung += 1
                            ve_loto_line_obj.write(cr, uid, [line.id], {'sl_3_dc_trung':sl_3_dc_trung})
                            
                            sl_3_7_trung = line.sl_3_7_trung
                            if ketqua.dm_7_so==True and ketqua.ma in ('02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18') and ketqua.so[-3:]==line.so_dt_3_7:
                                sl_3_7_trung+=1
                            ve_loto_line_obj.write(cr, uid, [line.id], {'sl_3_7_trung':sl_3_7_trung})
                            
                            sl_3_17_trung = line.sl_3_17_trung
                            if ketqua.ma in ('02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18') and ketqua.so[-3:]==line.so_dt_3_17:
                                sl_3_17_trung+=1
                            ve_loto_line_obj.write(cr, uid, [line.id], {'sl_3_17_trung':sl_3_17_trung})
                            
                            # 4 so
                            sl_4_16_trung = line.sl_4_16_trung
                            if ketqua.ma in ('03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18') and ketqua.so[-4:]==line.so_dt_4_16:
                                sl_4_16_trung+=1
                            ve_loto_line_obj.write(cr, uid, [line.id], {'sl_4_16_trung':sl_4_16_trung})
                        ve_loto_obj.write(cr, uid, [veloto.id], {'state':'done'})
        return self.write(cr, uid, ids, {'state':'validate'})
    
    def bt_dovelai(self, cr, uid, ids, context=None):
        ve_loto_obj = self.pool.get('ve.loto')
        dongbo_trungthuong_obj = self.pool.get('dongbo.daily.trungthuong')
        ve_loto_line_obj = self.pool.get('ve.loto.line')
        for xoso in self.browse(cr, uid, ids):
            dongbo_trungthuong_ids = dongbo_trungthuong_obj.search(cr, uid, [('ket_qua_id','=',xoso.id),('state','=','done')])
            if dongbo_trungthuong_ids:
                raise osv.except_osv(_('Cảnh báo!'),_('Không thể nhập lại kết quả vì đã đồng bộ dữ liệu cho trả thưởng!'))
            ve_loto_ids = ve_loto_obj.search(cr, uid, [('ngay','=',xoso.name),('state','=','done'),('parent_id','=',False)])
            if ve_loto_ids:
                ve_loto_ids = str(ve_loto_ids).replace('[', '(')
                ve_loto_ids = str(ve_loto_ids).replace(']', ')')
                sql = '''
                    update ve_loto_line set sl_2_d_trung=0, sl_2_c_trung=0, sl_2_dc_trung=0, sl_2_18_trung=0, sl_3_d_trung=0, sl_3_c_trung=0,
                        sl_3_dc_trung=0, sl_3_7_trung=0, sl_3_17_trung=0, sl_4_16_trung=0 where ve_loto_id in %s;
                '''%(ve_loto_ids)
                cr.execute(sql)
                sql = '''
                    update ve_loto set state='new' where id in %s;
                '''%(ve_loto_ids)
                cr.execute(sql)
                sql = '''
                    delete from dongbo_daily_trungthuong where ket_qua_id=%s
                '''%(xoso.id)
                cr.execute(sql)
        return self.write(cr, uid, ids, {'state':'new'})
    
ketqua_xoso()

class ketqua_xoso_line(osv.osv):
    _name = "ketqua.xoso.line"
    _columns = {
        'name': fields.char('Tên',size=32,required=True),
        'ma': fields.char('Mã',size=32,readonly=True),
        'so': fields.char('Số',size=32),
        'dm_7_so': fields.boolean('Danh mục 7 số'),
        'ketqua_xoso_id': fields.many2one('ketqua.xoso','Kết quả xổ số',ondelete='cascade'),
    }
    
ketqua_xoso_line()

class ve_loto(osv.osv):
    _name = "ve.loto"
    def default_get(self, cr, uid, fields, context=None):
        res = super(ve_loto, self).default_get(cr, uid, fields, context=context)
        vals = []
        
        for i in range(1,19):
            line_vals = {
                'name': i,
                  }
            vals.append((0,0,line_vals))
        res.update({
            've_loto_line':vals,
            })
        return res
    
    def _get_total(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for loto in self.browse(cr, uid, ids, context=context):
            res[loto.id] = {
                'tong_cong': 0.0,
                'thanh_tien': 0.0,
            }
            soluong = 0
            sql = '''
                select case when sum(coalesce(sl_2_d,0)+coalesce(sl_2_c,0)+coalesce(sl_2_dc,0)+coalesce(sl_2_18,0)+
                    coalesce(sl_3_d,0)+coalesce(sl_3_c,0)+coalesce(sl_3_dc,0)+coalesce(sl_3_7,0)+coalesce(sl_3_17,0)+coalesce(sl_4_16,0)
                )!=0 
                        
                    then sum(coalesce(sl_2_d,0)+coalesce(sl_2_c,0)+coalesce(sl_2_dc,0)+coalesce(sl_2_18,0)+
                        coalesce(sl_3_d,0)+coalesce(sl_3_c,0)+coalesce(sl_3_dc,0)+coalesce(sl_3_7,0)+coalesce(sl_3_17,0)+coalesce(sl_4_16,0)
                    ) else 0 end tongcong
                    
                    from ve_loto_line
                    
                    where ve_loto_id=%s
            '''%(loto.id)
            cr.execute(sql)
            soluong = cr.fetchone()[0]
#             for line in loto.ve_loto_2_line:
#                 soluong += line.sl_2_d + line.sl_2_c + line.sl_2_dc + line.sl_2_18 + line.sl_3_d + line.sl_3_c + line.sl_3_dc + line.sl_3_7 + line.sl_3_17 + line.sl_4_16 
            res[loto.id]['tong_cong'] = soluong
            res[loto.id]['thanh_tien'] = soluong*int(loto.product_id.list_price)
        return res
    
    def _get_loto(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('ve.loto.line').browse(cr, uid, ids, context=context):
            result[line.ve_loto_id.id] = True
        return result.keys()
    
    _columns = {
        'name': fields.char('Mã phiếu', size=128,required=False),
        'create_uid': fields.many2one('res.users','Người nhập'),
        'create_date': fields.datetime('Ngày chỉnh sửa',readonly=True),
        'daily_id': fields.many2one('res.partner','Đại lý',domain="[('dai_ly','=',True)]",required=True),
        'ngay': fields.date('Ngày xổ số',required=True),
        'so_chungtu': fields.char('Số chứng từ', size=128,required=False),
        'product_id': fields.many2one('product.product','Mệnh giá',domain="[('menh_gia','=',True)]",required=True),
        'ky_ve_id': fields.many2one('ky.ve','Kỳ vé',required=True),
        'sophieu': fields.integer('Số phiếu',required=True),
#         'tong_cong': fields.integer('Tổng cộng số lượng'),
        'tong_sai_kythuat': fields.integer('Tổng cộng vé ghi sai, SKT'),
#         'thanh_tien': fields.float('Thành tiền',digits=(16,0)),
        'tong_cong': fields.function(_get_total,type='float',digits=(16,0),
            store={
                've.loto': (lambda self, cr, uid, ids, c={}: ids, ['state','ve_loto_2_line','ve_loto_3_line','ve_loto_4_line','parent_id','lichsu_line'], 10),
                've.loto.line': (_get_loto, ['name', 've_loto_id', 'sl_2_d', 'sl_2_c', 'sl_2_dc', 'sl_2_18',
                                             'sl_3_d', 'sl_3_c','sl_3_dc', 'sl_3_7', 'sl_3_17', 'sl_4_16'], 10),
            },multi='tong',string='Tổng cộng số lượng'),
        'thanh_tien': fields.function(_get_total,type='float',
            store={
                've.loto': (lambda self, cr, uid, ids, c={}: ids, ['state','ve_loto_2_line','ve_loto_3_line','ve_loto_4_line','parent_id','lichsu_line'], 10),
                've.loto.line': (_get_loto, ['name', 've_loto_id', 'sl_2_d', 'sl_2_c', 'sl_2_dc', 'sl_2_18',
                                             'sl_3_d', 'sl_3_c','sl_3_dc', 'sl_3_7', 'sl_3_17', 'sl_4_16'], 10),
            },multi='tong',string='Thành tiền',digits=(16,0)),
        've_loto_2_line': fields.one2many('ve.loto.line','ve_loto_id','Line2', readonly=False),
        've_loto_3_line': fields.one2many('ve.loto.line','ve_loto_id','Line3', readonly=False),
        've_loto_4_line': fields.one2many('ve.loto.line','ve_loto_id','Line4', readonly=False),
        'state': fields.selection([('new','Mới tạo'),('done','Đã dò')],'Trạng thái'),
        'external_id': fields.integer('ExternalID'),
        'parent_id': fields.many2one('ve.loto','Parent',ondelete='cascade'),
        'lichsu_line': fields.one2many('ve.loto','parent_id','Lịch sử', readonly=False),
    }
    _defaults = {
        'state': 'new',
    }
    
    def write(self, cr, uid, ids, vals, context=None):
        context = context or {}
        for id in ids:
            if 've_loto_2_line' in vals or 've_loto_3_line' in vals or 've_loto_4_line' in vals:
                default = {'lichsu_line':[],'parent_id':id,'state':'new'}
                self.copy(cr, uid, id, default)
        super(ve_loto, self).write(cr, uid, ids, vals, context=context)
        update_fields = ''
        lichsu_dongbo_obj = self.pool.get('lichsu.dongbo')
        for veloto in self.browse(cr, uid, ids):
            if veloto.state=='done':
                temp = 0
                for key in vals.keys():
                    if key not in ['ve_loto_2_line','ve_loto_3_line','ve_loto_4_line','parent_id','lichsu_line']:
                        update_fields += key+','
                    else:
                        temp += 1
                company = self.pool.get('res.users').browse(cr, uid, uid).company_id
                if update_fields:
                    update_fields = update_fields[:-1]
                    for line in self.browse(cr, uid, ids):
                        vals={
                        'update_fields': update_fields,
                        'f_table': 've_loto',
                        'f_object': 've.loto',
                        'f_id': line.id,
                        'company_id': company.id,
                        'type': 'write',
                        'state': 'waiting',
                          }
                        lichsu_dongbo_obj.create(cr, uid, vals, context)
                if not update_fields and temp > 0:
                    for line in self.browse(cr, uid, ids):
                        vals={
                        'update_fields': 'sophieu',
                        'f_table': 've_loto',
                        'f_object': 've.loto',
                        'f_id': line.id,
                        'company_id': company.id,
                        'type': 'write',
                        'state': 'waiting',
                          }
                        lichsu_dongbo_obj.create(cr, uid, vals, context)
        return True
    
    def unlink(self, cr, uid, ids, context=None):
        context = context or {}
        lichsu_dongbo_obj = self.pool.get('lichsu.dongbo')
        company = self.pool.get('res.users').browse(cr, uid, uid).company_id
        for line in self.browse(cr, uid, ids):
            vals={
                'f_table': 've_loto',
                'f_object': 've.loto',
                'f_id': line.external_id,
                'company_id': company.id,
                'type': 'unlink',
                'state': 'waiting',
                  }
            lichsu_dongbo_obj.create(cr, uid, vals, context)
        super(ve_loto, self).unlink(cr, uid, ids, context=context)
        return True
    
ve_loto()

class ky_ve(osv.osv):
    _name = "ky.ve"
    _columns = {
        'name': fields.char('Kỳ vé',size=32,required=True),
        'ma': fields.char('Mã',size=32,required=True),
        'start_date': fields.date('Thời gian bắt đầu',required=True),
        'end_date': fields.date('Thời gian kết thúc',required=True),
        'ky_hien_tai': fields.boolean('Kỳ hiện tại',readonly=True),
        'external_id': fields.integer('ExternalID'),
    }
    
    def _check_date(self, cr, uid, ids, context=None):
        for wiz in self.browse(cr, uid, ids, context=context):
            start_date = wiz.start_date
            end_date = wiz.end_date
            if end_date<start_date:
                return False
            sql = '''
                select id from ky_ve where id != %(id)s 
                    and ('%(start_date)s' between start_date and end_date or '%(end_date)s' between start_date and end_date)
            '''%({
                  'id': wiz.id,
                  'start_date': start_date,
                  'end_date': end_date,
                  })
            cr.execute(sql)
            ky_ve_ids = cr.fetchall()
            if ky_ve_ids:
                return False
        return True
    
    _constraints = [
        (_check_date, 'Thời gian bắt đầu hoặc kết thúc không hợp lệ!', ['Thời gian bắt đầu','Thời gian kết thúc']),
    ]
    
    def create(self, cr, uid, vals, context=None):
        date_now = time.strftime('%Y-%m-%d')
        if date_now >= vals['start_date'] and date_now <= vals['end_date']:
            sql = '''
                update ky_ve set ky_hien_tai = 'f'
            '''
            cr.execute(sql)
            vals['ky_hien_tai'] = True
        ky_ve_id = super(ky_ve, self).create(cr, uid, vals, context)
        company = self.pool.get('res.users').browse(cr, uid, uid).company_id
        lichsu_dongbo_obj = self.pool.get('lichsu.dongbo')
        vals={
            'f_table': 'ky_ve',
            'f_object': 'ky.ve',
            'f_id': ky_ve_id,
            'company_id': company.id,
            'type': 'create',
            'state': 'waiting',
              }
        lichsu_dongbo_obj.create(cr, uid, vals, context)
        return ky_ve_id
    
    def write(self, cr, uid, ids, vals, context=None):
        res = super(ky_ve, self).write(cr, uid, ids, vals, context=context)
        date_now = time.strftime('%Y-%m-%d')
        for kyve in self.browse(cr, uid, ids, context):
            if date_now >= kyve.start_date and date_now <= kyve.end_date:
                sql = '''
                update ky_ve set ky_hien_tai = 't' where id = %s
                '''%(kyve.id)
                cr.execute(sql)
                ky_ve_khac_ids = self.search(cr, uid, [('id','!=',kyve.id)])
                self.write(cr, uid, ky_ve_khac_ids,{'ky_hien_tai': False})
            else:
                sql = '''
                update ky_ve set ky_hien_tai = 'f' where id = %s
            '''%(kyve.id)
            cr.execute(sql)
            
        update_fields = ''
        lichsu_dongbo_obj = self.pool.get('lichsu.dongbo')
        for key in vals.keys():
            update_fields += key+','
        if update_fields:
            update_fields = update_fields[:-1]
            company = self.pool.get('res.users').browse(cr, uid, uid).company_id
            for line in self.browse(cr, uid, ids):
                vals={
                'update_fields': update_fields,
                'f_table': 'ky_ve',
                'f_object': 'ky.ve',
                'f_id': line.id,
                'company_id': company.id,
                'type': 'write',
                'state': 'waiting',
                  }
                lichsu_dongbo_obj.create(cr, uid, vals, context)
        return res
    
    def unlink(self, cr, uid, ids, context=None):
        context = context or {}
        lichsu_dongbo_obj = self.pool.get('lichsu.dongbo')
        company = self.pool.get('res.users').browse(cr, uid, uid).company_id
        for line in self.browse(cr, uid, ids):
            vals={
                'f_table': 'ky_ve',
                'f_object': 'ky.ve',
                'f_id': line.external_id,
                'company_id': company.id,
                'type': 'unlink',
                'state': 'waiting',
                  }
            lichsu_dongbo_obj.create(cr, uid, vals, context)
        super(ky_ve, self).unlink(cr, uid, [line.id], context=context)
        return True
    
    def check_kyhientai(self, cr, uid, context=None):
        date_now = time.strftime('%Y-%m-%d')
        sql = '''
            select id from ky_ve where '%s' between start_date and end_date
        '''%(date_now)
        cr.execute(sql)
        ky_ve_ids = [row[0] for row in cr.fetchall()]
        self.write(cr, uid, ky_ve_ids,{'ky_hien_tai': True})
        ky_ve_khac_ids = self.search(cr, uid, [('id','not in',ky_ve_ids)])
        self.write(cr, uid, ky_ve_khac_ids,{'ky_hien_tai': False})
        return True
    
ky_ve()

class ve_loto_line(osv.osv):
    _name = "ve.loto.line"
    _columns = {
        'name': fields.integer('STT', required=True),
        
        'so_dt_2_d': fields.char('Số DT (Đ)',size=2),
        'sl_2_d': fields.integer('SL (Đ)'),
        'sl_2_d_trung': fields.integer('SLần Trúng (Đ)'),
        'so_dt_2_c': fields.char('Số DT (C)',size=2),
        'sl_2_c': fields.integer('SL (C)'),
        'sl_2_c_trung': fields.integer('SLần Trúng (C)'),
        'so_dt_2_dc': fields.char('Số DT (Đ/C)',size=2),
        'sl_2_dc': fields.integer('SL (Đ/C)'),
        'sl_2_dc_trung': fields.integer('SLần Trúng (Đ/C)'),
        'so_dt_2_18': fields.char('Số DT (18L)',size=2),
        'sl_2_18': fields.integer('SL (18L)'),
        'sl_2_18_trung': fields.integer('SLần Trúng (18L)'),
        
        'so_dt_3_d': fields.char('Số DT (Đ)',size=3),
        'sl_3_d': fields.integer('SL (Đ)'),
        'sl_3_d_trung': fields.integer('SLần Trúng (Đ)'),
        'so_dt_3_c': fields.char('Số DT (C)',size=3),
        'sl_3_c': fields.integer('SL (C)'),
        'sl_3_c_trung': fields.integer('SLần Trúng (C)'),
        'so_dt_3_dc': fields.char('Số DT (Đ/C)',size=3),
        'sl_3_dc': fields.integer('SL (Đ/C)'),
        'sl_3_dc_trung': fields.integer('SLần Trúng (Đ/C)'),
        'so_dt_3_7': fields.char('Số DT (7L)',size=3),
        'sl_3_7': fields.integer('SL (7L)'),
        'sl_3_7_trung': fields.integer('SLần Trúng (7L)'),
        'so_dt_3_17': fields.char('Số DT (17L)',size=3),
        'sl_3_17': fields.integer('SL (17L)'),
        'sl_3_17_trung': fields.integer('SLần Trúng (17L)'),
        
        'so_dt_4_16': fields.char('Số DT (16L)',size=4),
        'sl_4_16': fields.integer('SL (16L)'),
        'sl_4_16_trung': fields.integer('SLần Trúng (16L)'),
        
        've_loto_id': fields.many2one('ve.loto','Vé loto',ondelete='cascade'),
        
    }
    
    _defaults = {
        
    }
ve_loto_line()
