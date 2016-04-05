# -*- coding: utf-8 -*-################################################################################    OpenERP, Open Source Management Solution#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).##    This program is free software: you can redistribute it and/or modify#    it under the terms of the GNU Affero General Public License as#    published by the Free Software Foundation, either version 3 of the#    License, or (at your option) any later version.##    This program is distributed in the hope that it will be useful,#    but WITHOUT ANY WARRANTY; without even the implied warranty of#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the#    GNU Affero General Public License for more details.##    You should have received a copy of the GNU Affero General Public License#    along with this program.  If not, see <http://www.gnu.org/licenses/>.###############################################################################import timefrom openerp.osv import fields, osvfrom openerp.tools.translate import _from datetime import datetimeimport openerp.addons.decimal_precision as dpfrom xlrd import open_workbook,xldate_as_tuplefrom openerp import pooler, toolsimport osfrom openerp import modulesfrom dateutil.relativedelta import relativedeltabase_path = os.path.dirname(modules.get_module_path('green_erp_base_customer'))class res_country_state(osv.osv):    _inherit = "res.country.state"    _columns = {#         'quan_huyen_lines': fields.one2many('res.city', 'state_id', 'Quận/huyện'),    }#     def init(self, cr):#         country_obj = self.pool.get('res.country')#         wb = open_workbook(base_path + '/green_erp_base_customer/data/TinhTP.xls')#         for s in wb.sheets():#             if (s.name =='Sheet1'):#                 for row in range(1,s.nrows):#                     val0 = s.cell(row,0).value#                     val1 = s.cell(row,1).value#                     val2 = s.cell(row,2).value#                     country_ids = country_obj.search(cr, 1, [('code','=',val2)])#                     if country_ids:#                         state_ids = self.search(cr, 1, [('name','=',val1),('code','=',val0),('country_id','in',country_ids)])#                         if not state_ids:#                             self.create(cr, 1, {'name': val1,'code':val0,'country_id':country_ids[0]})        res_country_state()class res_city(osv.osv):    _name = 'res.city'    _columns = {        'name': fields.char('Name', size=128, required=True),        'state_id': fields.many2one('res.country.state', 'State'),        'country_id': fields.related('state_id', 'country_id', type='many2one', readonly=True, relation='res.country', string='Country'),        'postcode_line': fields.one2many('postal.code', 'city_id', 'Postal Codes')    }    #     def init(self, cr):#         state_obj = self.pool.get('res.country.state')#         wb = open_workbook(base_path + '/green_erp_base_customer/data/QuanHuyen.xls')#         for s in wb.sheets():#             if (s.name =='Sheet1'):#                 for row in range(1,s.nrows):#                     val0 = s.cell(row,0).value#                     val1 = s.cell(row,1).value#                     state_ids = state_obj.search(cr, 1, [('name','=',val1)])#                     if state_ids:#                         quan_huyen_ids = self.search(cr, 1, [('name','=',val0),('state_id','in',state_ids)])#                         if not quan_huyen_ids:#                             self.create(cr, 1, {'name': val0,'state_id':state_ids[0]})    res_city()    class postal_code(osv.osv):    _name = 'postal.code'    _columns = {        'name': fields.char('Postal Code', size=128, required=True),        'city_id': fields.many2one('res.city', 'City', ondelete='cascade', required=True)    }    postal_code()class res_partner(osv.osv):    _inherit = "res.partner"    _columns = {        'country_id': fields.many2one('res.country', 'Country'),        'state_id': fields.many2one("res.country.state", 'State', domain="[('country_id','=',country_id)]"),        'city': fields.many2one('res.city', 'City', domain="[('state_id','=',state_id)]"),        'zip': fields.many2one('postal.code', 'Zip', change_default=True, domain="[('city_id','=',city)]"),        'vat': fields.char('MST', size=32, help="Tax Identification Number. Check the box if this contact is subjected to taxes. Used by the some of the legal statements."),        'gsk_code': fields.char('Mã GSK', size=50),        'kv_benh_vien':fields.many2one('kv.benh.vien','Khu vực bệnh viện'),        'target_ban_hang':fields.one2many('target.ban.hang','partner_id','Target BH'),        'diachi_giaohang_line':fields.one2many('diachi.giaohang','partner_id','Danh sách địa chỉ giao hàng'),        'so_thich': fields.char('Sở thích', size=1024),        'ngay_sinh': fields.date('Ngày sinh'),        'ngay_ky_niem': fields.date('Ngày kỷ niệm'),        'gioi_tinh': fields.selection([('name','Nam'),('nu','Nữ')],'Giới tính'),    }        _defaults = {        'type': 'default', # type 'default' is wildcard and thus inappropriate        'date': lambda *a: time.strftime('%Y-%m-%d'),    }        def onchange_country_id(self, cr, uid, ids, country_id, context=None):        value = {'state_id':False,'city':False,'zip':False}#         if country_id:#             country = self.pool.get('res.country').browse(cr, uid, country_id)#             phone_code = country.phone_code#             company_id = country.company_id.id#             value.update({'phone':phone_code,'company_id':company_id, 'default_shipping_id': country.default_shipping_id.id or False})        return {'value':value}        def onchange_state(self, cr, uid, ids, state_id, context=None):        return {'value':{'city':False,'zip':False}}        def onchange_city(self, cr, uid, ids, city, context=None):        return {'value':{'zip':False}}    #     def create(self, cr, uid, vals, context=None):#         country_pool = self.pool.get('res.country')#         if vals.get('country_id',False):#             vals.update({'image':country_pool.read(cr, uid, vals['country_id'], ['flag'])['flag']})#         return super(res_partner, self).create(cr, uid, vals, context=context)#     #     def write(self, cr, uid, ids, vals, context=None):#         country_pool = self.pool.get('res.country')#         if vals.get('country_id',False):#             vals.update({'image':country_pool.read(cr, uid, vals['country_id'], ['flag'])['flag']})#         return super(res_partner, self).write(cr, uid, ids, vals, context=context)        def address_get(self, cr, uid, ids, adr_pref=None, context=None):        """ Find contacts/addresses of the right type(s) by doing a depth-first-search        through descendants within company boundaries (stop at entities flagged ``is_company``)        then continuing the search at the ancestors that are within the same company boundaries.        Defaults to partners of type ``'default'`` when the exact type is not found, or to the        provided partner itself if no type ``'default'`` is found either. """        adr_pref = set(adr_pref or [])        if 'default' not in adr_pref:            adr_pref.add('default')        result = {}        visited = set()        for partner in self.browse(cr, uid, filter(None, ids), context=context):            current_partner = partner            while current_partner:                to_scan = [current_partner]                # Scan descendants, DFS                while to_scan:                    record = to_scan.pop(0)                    visited.add(record)                    if record.type in adr_pref and not result.get(record.type):                        result[record.type] = record.id                    #Thanh: Get default for contact instead of company                    if record.type == 'default' and record.id != partner.id:                        result[record.type] = record.id                    if len(result) == len(adr_pref):                        return result                    to_scan = [c for c in record.child_ids                                 if c not in visited                                 if not c.is_company] + to_scan                # Continue scanning at ancestor if current_partner is not a commercial entity                if current_partner.is_company or not current_partner.parent_id:                    break                current_partner = current_partner.parent_id        # default to type 'default' or the partner itself        default = result.get('default', partner.id)        for adr_type in adr_pref:            result[adr_type] = result.get(adr_type) or default         return result        def show_street_city(self, cr, uid, ids, context=None):        if context is None:            context = {}        if isinstance(ids, (int, long)):            ids = [ids]        res = []        for record in self.browse(cr, uid, ids, context=context):            name = record.parent_id and record.parent_id.name + ' / ' or ''            name += record.name + ' / '            name += record.street and record.street + ' / ' or ''            name += record.city and record.city.name + ' / ' or ''            if name:                name = name[:-3]            res.append((record.id, name))        return res        def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):        if context is None:            context = {}        if context.get('search_partner_dldh_id'):            sql = '''                select partner_id from dulieu_donghang            '''            cr.execute(sql)            partner_ids = [row[0] for row in cr.fetchall()]            args += [('id','not in',partner_ids)]        if uid == 24:#             sql = '''#                 select id from res_partner where #                     customer = 't' and #                     street LIKE '%Q.Gò Vấp%' or street LIKE '%Q. Gò Vấp%' or street LIKE '%Quận Gò Vấp%' or#                     street LIKE '%Q.Tân Bình%' or street LIKE '%Q. Tân Bình%' or street LIKE '%Quận Tân Bình%' or#                     street LIKE '%Q1%' or street LIKE '%Q.1%' or street LIKE '%Quận 1%' or#                     street LIKE '%Q.Tân Phú%' or street LIKE '%Q. Tân Phú%' or street LIKE '%Quận Tân Phú%' or#                     street LIKE '%Q3%' or street LIKE '%Q.3%' or street LIKE '%Quận 3%' or#                     street LIKE '%Q10%' or street LIKE '%Q.10%' or street LIKE '%Quận 10%' or#                     street LIKE '%Q11%' or street LIKE '%Q.11%' or street LIKE '%Quận 11%' or#                     street LIKE '%Q4%' or street LIKE '%Q.4%' or street LIKE '%Quận 4%' or#                     street LIKE '%Q5%' or street LIKE '%Q.5%' or street LIKE '%Quận 5%' or#                     street LIKE '%Q6%' or street LIKE '%Q.6%' or street LIKE '%Quận 6%' or#                     street LIKE '%Q8%' or street LIKE '%Q.8%' or street LIKE '%Quận 8%' or#                     street LIKE '%Q.Bình Tân%' or street LIKE '%Q. Bình Tân%' or street LIKE '%Quận Bình Tân%' or#                     street LIKE '%Q7%' or street LIKE '%Q.7%' or street LIKE '%Quận 7%' or#                     street LIKE '%H.Bình Chánh%' or street LIKE '%H. Bình Chánh%' or street LIKE '%Huyện Bình Chánh%' or#                     street LIKE '%H.Nhà Bè%' or street LIKE '%H. Nhà Bè%' or street LIKE '%Huyện Nhà Bè%' or#                     street LIKE '%H.Cần Giờ%' or street LIKE '%H. Cần Giờ%' or street LIKE '%Huyện Cần Giờ%' or#                     #                     street2 LIKE '%Q.Gò Vấp%' or street2 LIKE '%Q. Gò Vấp%' or street2 LIKE '%Quận Gò Vấp%' or#                     street2 LIKE '%Q.Tân Bình%' or street2 LIKE '%Q. Tân Bình%' or street2 LIKE '%Quận Tân Bình%' or#                     street2 LIKE '%Q1%' or street2 LIKE '%Q.1%' or street2 LIKE '%Quận 1%' or #                     street2 LIKE '%Q.Tân Phú%' or street2 LIKE '%Q. Tân Phú%' or street2 LIKE '%Quận Tân Phú%' or#                     street2 LIKE '%Q3%' or street2 LIKE '%Q.3%' or street2 LIKE '%Quận 3%' or#                     street2 LIKE '%Q10%' or street2 LIKE '%Q.10%' or street2 LIKE '%Quận 10%' or#                     street2 LIKE '%Q11%' or street2 LIKE '%Q.11%' or street2 LIKE '%Quận 11%' or#                     street2 LIKE '%Q4%' or street2 LIKE '%Q.4%' or street2 LIKE '%Quận 4%' or#                     street2 LIKE '%Q5%' or street2 LIKE '%Q.5%' or street2 LIKE '%Quận 5%' or#                     street2 LIKE '%Q6%' or street2 LIKE '%Q.6%' or street2 LIKE '%Quận 6%' or#                     street2 LIKE '%Q8%' or street2 LIKE '%Q.8%' or street2 LIKE '%Quận 8%' or#                     street2 LIKE '%Q.Bình Tân%' or street2 LIKE '%Q. Bình Tân%' or street2 LIKE '%Quận Bình Tân%' or#                     street2 LIKE '%Q7%' or street2 LIKE '%Q.7%' or street2 LIKE '%Quận 7%' or#                     street2 LIKE '%H.Bình Chánh%' or street2 LIKE '%H. Bình Chánh%' or street2 LIKE '%Huyện Bình Chánh%' or#                     street2 LIKE '%H.Nhà Bè%' or street2 LIKE '%H. Nhà Bè%' or street2 LIKE '%Huyện Nhà Bè%' or#                     street2 LIKE '%H.Cần Giờ%' or street2 LIKE '%H. Cần Giờ%' or street2 LIKE '%Huyện Cần Giờ%'#                     #             '''#             cr.execute(sql)            sql = '''                select id from res_partner where customer = 't' and user_id = %s            '''%(uid)            cr.execute(sql)            thuy_ids = [row[0] for row in cr.fetchall()]            args += [('id','in',thuy_ids)]        return super(res_partner, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)        def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):        if not args:            args = []        if not context:            context = {}        contact_ids = []        if context.get('parent_company_id',False):            contact_ids = self.search(cr, uid, [('parent_id','=',context['parent_company_id'])], limit=limit, context=context)            args += [('parent_id','!=',context['parent_company_id'])]        if name:            # Be sure name_search is symetric to name_get            name = name.split(' / ')[-1]            ids = self.search(cr, uid, [('name', operator, name)] + args, limit=limit, context=context)        else:            ids = self.search(cr, uid, args, limit=limit, context=context)                        ids = contact_ids + ids        if context.get('show_street_city',False):            return self.show_street_city(cr, uid, ids, context)        else:            return self.name_get(cr, uid, ids, context)        def name_get(self, cr, uid, ids, context=None):        if context is None:            context = {}        if isinstance(ids, (int, long)):            ids = [ids]        res = []        for record in self.browse(cr, uid, ids, context=context):            name = record.name#             if record.parent_id and not record.is_company:#                 name =  "%s, %s" % (record.parent_id.name, name)            if context.get('show_address'):                name = name + "\n" + self._display_address(cr, uid, record, without_company=True, context=context)                name = name.replace('\n\n','\n')                name = name.replace('\n\n','\n')            if context.get('show_email') and record.email:                name = "%s <%s>" % (name, record.email)            res.append((record.id, name))        return res        #Thanh: Redisplay Address    def _display_address(self, cr, uid, address, without_company=False, context=None):        '''        The purpose of this function is to build and return an address formatted accordingly to the        standards of the country where it belongs.        :param address: browse record of the res.partner to format        :returns: the address formatted in a display that fit its country habits (or the default ones            if not country is specified)        :rtype: string        '''        # get the information that will be injected into the display format        # get the address format#         address_format = "%(street)s, %(street2)s, %(city_name)s, %(state_name)s, %(zip_name)s, %(country_name)s"        address_format = "%(company_name)s / %(street)s / %(street2)s / %(city_name)s"        args = {            'city_name': address.city.name or '',            'zip_name': address.zip.name or '',            'state_code': address.state_id and address.state_id.code or '',            'state_name': address.state_id and address.state_id.name or '',            'country_code': address.country_id and address.country_id.code or '',            'country_name': address.country_id and address.country_id.name or '',            'company_name': address.parent_id and address.parent_id.name or '',        }        for field in self._address_fields(cr, uid, context=context):            args[field] = getattr(address, field) or ''#         if without_company:#             args['company_name'] = ''#         elif address.parent_id:#             #Thanh: No need to show compnay name# #             address_format = '%(company_name)s\n' + address_format#             address_format = address_format        return address_format % args    res_partner()class lien_he(osv.osv_memory):    _name = "lien.he"        _columns = {        'name': fields.char('Tên', size=1024, required=True),        'so_thich': fields.char('Sở thích', size=1024),        'ngay_sinh': fields.date('Ngày sinh'),        'ngay_ky_niem': fields.date('Ngày kỷ niệm'),        'gioi_tinh': fields.selection([('name','Nam'),('nu','Nữ')],'Giới tính'),        'function': fields.char('Chức vụ', size=128),        'type': fields.selection([('default', 'Default'), ('invoice', 'Invoice'),                                   ('delivery', 'Shipping'), ('contact', 'Contact'),                                   ('other', 'Other')], 'Address Type',            help="Used to select automatically the right address according to the context in sales and purchases documents."),        'street': fields.char('Street', size=128),        'street2': fields.char('Street2', size=128),        'zip': fields.char('Zip', change_default=True, size=24),        'city': fields.char('City', size=128),        'state_id': fields.many2one("res.country.state", 'State'),        'country_id': fields.many2one('res.country', 'Country'),        'country': fields.related('country_id', type='many2one', relation='res.country', string='Country',                                  deprecated="This field will be removed as of OpenERP 7.1, use country_id instead"),        'email': fields.char('Thư điện tử', size=240),        'phone': fields.char('Điện thoại', size=64),        'fax': fields.char('Fax', size=64),        'mobile': fields.char('Số di động', size=64),        'birthdate': fields.char('Birthdate', size=64),        'use_parent_address': fields.boolean('Use Company Address', help="Select this if you want to set company's address information  for this contact"),        'image': fields.binary("Image",            help="This field holds the image used as avatar for this contact, limited to 1024x1024px"),    }        def luu(self, cr, uid, ids, context=None):        partner_id=context.get('active_id')        for line in self.browse(cr, uid, ids):            partner_id            self.pool.get('res.partner').create(cr, 1, {'parent_id': partner_id,                                                        'name': line.name,                                                        'image': line.image,                                                        'function': line.function,                                                        'email': line.email,                                                        'phone': line.phone,                                                        'mobile': line.mobile,                                                        'ngay_sinh': line.ngay_sinh,                                                        'so_thich': line.so_thich,                                                        'gioi_tinh': line.gioi_tinh,                                                        'street': line.street,                                                        'street2': line.street2,                                                        'city': line.city,                                                        'state_id': line.state_id and line.state_id.id or False,                                                        'zip': line.zip,                                                        'type': line.type,                                                        'country_id': line.country_id and line.country_id.id or False,                                                        })        return {'type': 'ir.actions.act_window_close'}    lien_he()class diachi_giaohang(osv.osv):    _name = 'diachi.giaohang'    _columns = {        'partner_id': fields.many2one('res.partner', 'Khách hàng', ondelete = 'cascade'),        'name': fields.char('Địa chỉ', size=1024, required=True),        }    diachi_giaohang()class kv_benh_vien(osv.osv):    _name = 'kv.benh.vien'    _columns = {        'name': fields.char('Tên', size=1024, required=True),        }    kv_benh_vien()class mail_mail(osv.Model):    _inherit = 'mail.mail'         def _get_default_mail_server_id(self, cr, uid, context=None):        this = self.pool.get('res.users').browse(cr, 1, uid, context=context)        ir_mail_server_id = False        if this.email:            ir_mail_server = self.pool.get('ir.mail_server')            ir_mail_server_ids = ir_mail_server.search(cr, 1, [('smtp_user','=',this.email)], order='sequence')            if ir_mail_server_ids:                ir_mail_server_id = ir_mail_server_ids[0]        return ir_mail_server_id         _defaults = {        'mail_server_id': lambda self, cr, uid, ctx=None: self._get_default_mail_server_id(cr, uid, ctx),    }mail_mail()class res_partner_bank(osv.osv):    _inherit = 'res.partner.bank'    _columns = {                'bank_name': fields.char('Bank Name'),                }res_partner_bank()class target_ban_hang(osv.osv):    _name = 'target.ban.hang'    _columns = {        'partner_id': fields.many2one('res.partner', 'Khách hàng', ondelete = 'cascade'),        'tu_ngay': fields.date('Từ ngày', required=True),        'den_ngay': fields.date('Đến ngày', required=True),        'target_bh_line': fields.one2many('target.bh.line','target_id','Target ban hang line')    }    _defaults = {        'tu_ngay': lambda *a: time.strftime('%Y-%m-01'),        'den_ngay': lambda *a: str(datetime.now() + relativedelta(months=+1, day=1, days=-1))[:10],                 }    target_ban_hang()class target_bh_line(osv.osv):    _name = 'target.bh.line'        def amount_sale_order_line(self, cr, uid, ids, field_name, args, context=None):        res = {}        for line in self.browse(cr,uid,ids,context=context):            total = 0.0            if line.loai == 'so_luong':                sql = '''                    select case when sum(product_uom_qty)!=0 then sum(product_uom_qty) else 0 end product_uom_qty                    from sale_order_line where product_id = %s and order_id in (select id from sale_order                    where state not in ('draft', 'sent', 'cancel', 'waiting_date') and date_order between '%s' and '%s')                '''%(line.product_id.id, line.target_id.tu_ngay, line.target_id.den_ngay)                cr.execute(sql)                total = cr.dictfetchone()['product_uom_qty']            if line.loai == 'so_tien':                sql = '''                    select case when sum(product_uom_qty*price_unit)!=0 then sum(product_uom_qty*price_unit) else 0 end thanh_tien                    from sale_order_line where product_id = %s and order_id in (select id from sale_order                    where state not in ('draft', 'sent', 'cancel', 'waiting_date') and date_order between '%s' and '%s')                '''%(line.product_id.id, line.target_id.tu_ngay, line.target_id.den_ngay)                cr.execute(sql)                total = cr.dictfetchone()['thanh_tien']            res[line.id] = total        return res        _columns = {        'target_id': fields.many2one('target.ban.hang', 'Target Bán Hàng', ondelete = 'cascade'),        'product_id': fields.many2one('product.product', 'Sản phẩm', required = True),        'loai': fields.selection([('so_luong', 'Số lượng'),('so_tien', 'Số tiền')],'Loại chỉ tiêu', required = True),        'gia_tri': fields.float('Giá trị'),#         'gt_hien_tai': fields.float('Giá trị hiện tại', readonly = True),        'gt_hien_tai': fields.function(amount_sale_order_line, type='float',string='Giá trị hiện tại'),    }    #     def onchange_product_id(self, cr, uid, ids, product_id=False, loai=False):#         vals = {}#         if product_id:#             total = 0.0#             if loai == 'so_luong':#                 sql = '''#                     select case when sum(product_uom_qty)!=0 then sum(product_uom_qty) else 0 end product_uom_qty#                     from sale_order_line where product_id = %s and order_id in (select id from sale_order#                     where state not in ('draft', 'sent', 'cancel', 'waiting_date'))#                 '''%(product_id)#                 cr.execute(sql)#                 total = cr.dictfetchone()['product_uom_qty']#             if loai == 'so_tien':#                 sql = '''#                     select case when sum(product_uom_qty*price_unit)!=0 then sum(product_uom_qty*price_unit) else 0 end thanh_tien#                     from sale_order_line where product_id = %s and order_id in (select id from sale_order#                     where state not in ('draft', 'sent', 'cancel', 'waiting_date'))#                 '''%(product_id)#                 cr.execute(sql)#                 total = cr.dictfetchone()['thanh_tien']#             vals = {'gt_hien_tai':total,#                 }#         return {'value': vals}     target_bh_line()# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
