# -*- coding: utf-8 -*-
import datetime
import time
from itertools import groupby
from operator import itemgetter
import openerp.addons.decimal_precision as dp
import math
from openerp import netsvc
from openerp import tools
from openerp.osv import fields, osv
from openerp.tools.translate import _
import base64
import xlrd
from xlrd import open_workbook,xldate_as_tuple
DATE_FORMAT = "%Y-%m-%d"

class import_ve_loto(osv.osv):
    _name = "import.ve.loto"
    _columns = {
        'name': fields.char('Name',size=500,required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'date': fields.date('Date',required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'file': fields.binary('File',required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'file_name':  fields.char('Filename', 100, readonly=True),
        'import_ve_loto_line': fields.one2many('import.ve.loto.line', 'import_ve_loto_id', 'Import Ve Loto Lines', readonly=True, states={'draft':[('readonly',False)]}),
        'state': fields.selection([
            ('draft','Draft'),
            ('import','Imported'),
            ],'Status', select=True, readonly=True)
    }
    _defaults = {
        'file_name': 'danh_sach_ve_loto.xls',
        'state':'draft',
        'date': lambda *a: time.strftime('%Y-%m-%d'),    
    }
    
    def get_vietname_date(self, date):
        if not date:
            date = time.strftime(DATE_FORMAT)
        date = datetime.strptime(date, DATE_FORMAT)
        return date.strftime('%Y/%m/%D')
    
    def read_file(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids[0])
        sql = '''
            delete from import_ve_loto_line where import_ve_loto_id = %s
        '''%(this.id)
        cr.execute(sql)
        try:
            recordlist = base64.decodestring(this.file)
            excel = xlrd.open_workbook(file_contents = recordlist)
            sh = excel.sheet_by_index(0)
        except Exception, e:
            raise osv.except_osv(_('Warning!'), str(e))
        if sh:
            for row in range(1,sh.nrows):
                ma_dl = sh.cell(row, 1).value
                ma_dl_str = str(ma_dl)
                ma_ban = sh.cell(row, 2).value
                ma_ban_str = str(ma_ban)
                check_madl = 0
                check_maban = 0
                for x in range(len(ma_dl_str)):
                    if ma_dl_str[x]=='-':
                        check_madl += 1
                        break
                for x in range(len(ma_ban_str)):
                    if ma_ban_str[x]=='-':
                        check_maban += 1
                        break
                if len(ma_dl_str)==3:
                    ma_dl_str = '0'+ma_dl_str
                if len(ma_ban_str)==3:
                    ma_ban_str = '0'+ma_ban_str
                    
                if check_madl== 0 and check_maban!=0:
                    dl = 'ĐL'+ma_dl_str[:2]
                elif check_madl== 0 and check_maban==0:
                    dl = 'ĐL'+ma_dl_str[:2]+'-'+ma_ban_str[:2]
                else:
                    raise osv.except_osv(_('Cảnh báo!'),_('Dòng %s: Đại lý không đúng!')%(row+1))
                daily_ids = self.pool.get('res.partner').search(cr, uid, [('dai_ly','=',True),('ma_daily','=',dl)])
                menh_gia = sh.cell(row, 3).value
                if menh_gia == '-':
                    raise osv.except_osv(_('Cảnh báo!'),_('Dòng %s: Mệnh giá không đúng!')%(row+1))
                if menh_gia==0:
                    menh_gia_ids = self.pool.get('product.product').search(cr, uid, [('menh_gia','=',True),('default_code','=','MG-05.000')])
                elif menh_gia==1:
                    menh_gia_ids = self.pool.get('product.product').search(cr, uid, [('menh_gia','=',True),('default_code','=','MG-10.000')])
                elif menh_gia==2:
                    menh_gia_ids = self.pool.get('product.product').search(cr, uid, [('menh_gia','=',True),('default_code','=','MG-20.000')])
                elif menh_gia==3:
                    menh_gia_ids = self.pool.get('product.product').search(cr, uid, [('menh_gia','=',True),('default_code','=','MG-50.000')])
                else:
                    menh_gia_ids = []
                sophieu = sh.cell(row, 4).value
                tong_sai_kythuat = sh.cell(row, 6).value
                tong_sai_kythuat_str = str(tong_sai_kythuat)
                check_tong_sai_kythuat = 0
                for x in range(len(tong_sai_kythuat_str)):
                    if tong_sai_kythuat_str[x]=='-':
                        check_tong_sai_kythuat += 1
                        break
                if check_tong_sai_kythuat==0:
                    tong_sai_kythuat = int(tong_sai_kythuat)
                else:
                    tong_sai_kythuat = 0
                vals = []
                stt = 1
                for n_col in range(7,sh.ncols,20):
                    dem = 1
                    temp = 0
                    so_dt_2_d = ''
                    sl_2_d = 0
                    so_dt_2_c = ''
                    sl_2_c = 0
                    so_dt_2_dc = ''
                    sl_2_dc = 0
                    so_dt_2_18 = ''
                    sl_2_18 = 0
                    so_dt_3_d = ''
                    sl_3_d = 0
                    so_dt_3_c = ''
                    sl_3_c = 0
                    so_dt_3_dc = ''
                    sl_3_dc = 0
                    so_dt_3_7 = ''
                    sl_3_7 = 0
                    so_dt_3_17 = ''
                    sl_3_17 = 0
                    so_dt_4_16 = ''
                    sl_4_16 = 0
                    for col in range(n_col,n_col+20,2):
                        cell = sh.cell(row, col).value
                        cell_1 = sh.cell(row, col+1).value
                        check = 0
                        cell_str = str(cell)
                        cell_1_str = str(cell_1)
                        for x in range(len(cell_str)):
                            if cell_str[x]=='-':
                                check += 1
                                break
                        if check == 0:
                            for x in range(len(cell_1_str)):
                                if cell_1_str[x]=='-':
                                    check += 1
                                    break
                        cell_str = cell_str[:-2]
                        
                        if menh_gia!=3:
                            if check == 0 and dem==1:
                                if len(cell_str) == 2:
                                    so_dt_2_d = cell_str
                                else:
                                    so_dt_2_d = '0'+cell_str
                                sl_2_d = cell_1
                                temp+=1
                            if check == 0 and dem==3:
                                if len(cell_str) == 2:
                                    so_dt_2_c = cell_str
                                else:
                                    so_dt_2_c = '0'+cell_str
                                sl_2_c = cell_1
                                temp+=1
                        if check == 0 and dem==5:
                            if len(cell_str) == 2:
                                so_dt_2_dc = cell_str
                            else:
                                so_dt_2_dc = '0'+cell_str
                            sl_2_dc = cell_1
                            temp+=1
                        if check == 0 and dem==7:
                            if len(cell_str) == 2:
                                so_dt_2_18 = cell_str
                            else:
                                so_dt_2_18 = '0'+cell_str
                            sl_2_18 = cell_1
                            temp+=1
                        if menh_gia!=3:
                            if check == 0 and dem==9:
                                if len(cell_str) == 3:
                                    so_dt_3_d = cell_str
                                elif len(cell_str) == 2:
                                    so_dt_3_d = '0'+cell_str
                                else:
                                    so_dt_3_d = '00'+cell_str
                                sl_3_d = cell_1
                                temp+=1
                            if check == 0 and dem==11:
                                if len(cell_str) == 3:
                                    so_dt_3_c = cell_str
                                elif len(cell_str) == 2:
                                    so_dt_3_c = '0'+cell_str
                                else:
                                    so_dt_3_c = '00'+cell_str
                                sl_3_c = cell_1
                                temp+=1
                        if check == 0 and dem==13:
                            if len(cell_str) == 3:
                                so_dt_3_dc = cell_str
                            elif len(cell_str) == 2:
                                so_dt_3_dc = '0'+cell_str
                            else:
                                so_dt_3_dc = '00'+cell_str
                            sl_3_dc = cell_1
                            temp+=1
                        if check == 0 and dem==15:
                            if len(cell_str) == 3:
                                so_dt_3_7 = cell_str
                            elif len(cell_str) == 2:
                                so_dt_3_7 = '0'+cell_str
                            else:
                                so_dt_3_7 = '00'+cell_str
                            sl_3_7 = cell_1
                            temp+=1
                        if check == 0 and dem==17:
                            if len(cell_str) == 3:
                                so_dt_3_17 = cell_str
                            elif len(cell_str) == 2:
                                so_dt_3_17 = '0'+cell_str
                            else:
                                so_dt_3_17 = '00'+cell_str
                            sl_3_17 = cell_1
                            temp+=1
                        
                        if check == 0 and dem==19:
                            if len(cell_str) == 4:
                                so_dt_4_16 = cell_str
                            elif len(cell_str) == 3:
                                so_dt_4_16 = '0'+cell_str
                            elif len(cell_str) == 2:
                                so_dt_4_16 = '00'+cell_str
                            else:
                                so_dt_4_16 = '000'+cell_str
                            sl_4_16 = cell_1
                            temp+=1
                        dem += 2
                    if temp > 0:
                        vals.append((0,0,{
                            'name': stt,
                            'so_dt_2_d': so_dt_2_d,
                            'sl_2_d': sl_2_d,
                            'so_dt_2_c': so_dt_2_c,
                            'sl_2_c': sl_2_c,
                            'so_dt_2_dc': so_dt_2_dc,
                            'sl_2_dc': sl_2_dc,
                            'so_dt_2_18': so_dt_2_18,
                            'sl_2_18': sl_2_18,
                            
                            'so_dt_3_d': so_dt_3_d,
                            'sl_3_d': sl_3_d,
                            'so_dt_3_c': so_dt_3_c,
                            'sl_3_c': sl_3_c,
                            'so_dt_3_dc': so_dt_3_dc,
                            'sl_3_dc': sl_3_dc,
                            'so_dt_3_7': so_dt_3_7,
                            'sl_3_7': sl_3_7,
                            'so_dt_3_17': so_dt_3_17,
                            'sl_3_17': sl_3_17,
                            
                            'so_dt_4_16': so_dt_4_16,
                            'sl_4_16': sl_4_16,
                        }))
                        stt += 1
                stt = 1
                kyve_ids = self.pool.get('ky.ve').search(cr, uid, [('ky_hien_tai','=',True)])
                self.pool.get('import.ve.loto.line').create(cr, uid, {
                    'import_ve_loto_id': this.id,
                    've_loto_2_line': vals,
                    'product_id': menh_gia_ids and menh_gia_ids[0] or False,
                    'ngay': time.strftime('%Y-%m-%d'),
                    'ky_ve_id': kyve_ids and kyve_ids[0] or False,
                    'daily_id': daily_ids and daily_ids[0] or False,
                    'sophieu': sophieu,
                    'tong_sai_kythuat': tong_sai_kythuat,
                })
        return True
    
    def importloto(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids):
            if line.import_ve_loto_line:
                for ve_loto in line.import_ve_loto_line:
                    loto = []
                    for ve_loto_line in ve_loto.ve_loto_2_line:
                        loto.append((0,0,{
                            'name': ve_loto_line.name,
                            'so_dt_2_d': ve_loto_line.so_dt_2_d,
                            'sl_2_d': ve_loto_line.sl_2_d,
                            'so_dt_2_c': ve_loto_line.so_dt_2_c,
                            'sl_2_c': ve_loto_line.sl_2_c,
                            'so_dt_2_dc': ve_loto_line.so_dt_2_dc,
                            'sl_2_dc': ve_loto_line.sl_2_dc,
                            'so_dt_2_18': ve_loto_line.so_dt_2_18,
                            'sl_2_18': ve_loto_line.sl_2_18,
                            
                            'so_dt_3_d': ve_loto_line.so_dt_3_d,
                            'sl_3_d': ve_loto_line.sl_3_d,
                            'so_dt_3_c': ve_loto_line.so_dt_3_c,
                            'sl_3_c': ve_loto_line.sl_3_c,
                            'so_dt_3_dc': ve_loto_line.so_dt_3_dc,
                            'sl_3_dc': ve_loto_line.sl_3_dc,
                            'so_dt_3_7': ve_loto_line.so_dt_3_7,
                            'sl_3_7': ve_loto_line.sl_3_7,
                            'so_dt_3_17': ve_loto_line.so_dt_3_17,
                            'sl_3_17': ve_loto_line.sl_3_17,
                            
                            'so_dt_4_16': ve_loto_line.so_dt_4_16,
                            'sl_4_16': ve_loto_line.sl_4_16,       
                        }))
                    self.pool.get('ve.loto').create(cr, uid, {
                        'daily_id': ve_loto.daily_id.id,
                        'product_id': ve_loto.product_id.id,
                        'ky_ve_id': ve_loto.ky_ve_id.id,
                        'ngay': ve_loto.ngay,
                        'sophieu': ve_loto.sophieu,
                        'tong_cong': ve_loto.tong_cong,
                        'tong_sai_kythuat': ve_loto.tong_sai_kythuat,
                        'so_chungtu': ve_loto.so_chungtu,
                        'thanh_tien': ve_loto.thanh_tien,
                        've_loto_2_line': loto,
                    })            
            else:
                raise osv.except_osv(_('Cảnh báo!'), _('Không có dữ liệu!'))
        return self.write(cr, uid, ids,{'state':'import'})
import_ve_loto()

class import_ve_loto_line(osv.osv):
    _name = "import.ve.loto.line"
    
    def _get_total(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for loto in self.browse(cr, uid, ids, context=context):
            res[loto.id] = {
                'tong_cong': 0.0,
                'thanh_tien': 0.0,
            }
            soluong = 0
            for line in loto.ve_loto_2_line:
                soluong += line.sl_2_d + line.sl_2_c + line.sl_2_dc + line.sl_2_18 + line.sl_3_d + line.sl_3_c + line.sl_3_dc + line.sl_3_7 + line.sl_3_17 + line.sl_4_16 
            res[loto.id]['tong_cong'] = soluong
            res[loto.id]['thanh_tien'] = soluong*loto.product_id.list_price
        return res
    
    _columns = {
        'name': fields.char('Mã phiếu', size=128,required=False),
        'daily_id': fields.many2one('res.partner','Đại lý',domain="[('dai_ly','=',True)]",required=False),
        'ngay': fields.date('Ngày xổ số',required=False),
        'so_chungtu': fields.char('Số chứng từ', size=128,required=False),
        'product_id': fields.many2one('product.product','Mệnh giá',domain="[('menh_gia','=',True)]",required=False),
        'ky_ve_id': fields.many2one('ky.ve','Kỳ vé',required=False),
        'sophieu': fields.integer('Số phiếu',required=False),
        'tong_cong': fields.function(_get_total,type='float',digits=(16,0),store=True,multi='tong',string='Tổng cộng số lượng'),
        'tong_sai_kythuat': fields.integer('Tổng cộng vé ghi sai, SKT'),
        'thanh_tien': fields.function(_get_total,type='float',store=True,multi='tong',string='Thành tiền',digits=(16,0)),
        've_loto_2_line': fields.one2many('import.chitiet.ve.loto.line','import_ve_loto_line_id','Line2', readonly=False),
        've_loto_3_line': fields.one2many('import.chitiet.ve.loto.line','import_ve_loto_line_id','Line3', readonly=False),
        've_loto_4_line': fields.one2many('import.chitiet.ve.loto.line','import_ve_loto_line_id','Line4', readonly=False),
        'import_ve_loto_id': fields.many2one('import.ve.loto', 'Import Ve Loto', ondelete='cascade'),
    }
import_ve_loto_line()

class import_chitiet_ve_loto_line(osv.osv):
    _name = "import.chitiet.ve.loto.line"
    _columns = {
        'import_ve_loto_line_id': fields.many2one('import.ve.loto.line', 'Import Ve Loto', ondelete='cascade'),
        'name': fields.integer('STT'),
        
        'so_dt_2_d': fields.char('Số DT',size=2),
        'sl_2_d': fields.integer('SL'),
        'so_dt_2_c': fields.char('Số DT',size=2),
        'sl_2_c': fields.integer('SL'),
        'so_dt_2_dc': fields.char('Số DT',size=2),
        'sl_2_dc': fields.integer('SL'),
        'so_dt_2_18': fields.char('Số DT',size=2),
        'sl_2_18': fields.integer('SL'),
        
        'so_dt_3_d': fields.char('Số DT',size=3),
        'sl_3_d': fields.integer('SL'),
        'so_dt_3_c': fields.char('Số DT',size=3),
        'sl_3_c': fields.integer('SL'),
        'so_dt_3_dc': fields.char('Số DT',size=3),
        'sl_3_dc': fields.integer('SL'),
        'so_dt_3_7': fields.char('Số DT',size=3),
        'sl_3_7': fields.integer('SL'),
        'so_dt_3_17': fields.char('Số DT',size=3),
        'sl_3_17': fields.integer('SL'),
        
        'so_dt_4_16': fields.char('Số DT',size=4),
        'sl_4_16': fields.integer('SL'),
    }
import_chitiet_ve_loto_line()
