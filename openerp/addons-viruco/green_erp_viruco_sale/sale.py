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


class sale_order(osv.osv):
    _inherit = "sale.order"
    _columns = {
        'thoigian_giaohang':fields.datetime('Thời gian giao hàng'),
        'nguoi_gioithieu_id':fields.many2one('res.partner','Người giới thiệu',readonly=True,states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}),
        'dieukien_giaohang_id':fields.many2one('dieukien.giaohang','Điều kiện giao hàng'),
        'hop_dong_id':fields.many2one('hop.dong','Hợp đồng',readonly=True,states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}),
        'hinhthuc_giaohang_id':fields.many2one('hinhthuc.giaohang','Hình thức giao hàng'),
        'so_chuyenphatnhanh':fields.char('Số chuyển phát nhanh',size=1024),
        'thanhtoan':fields.boolean('Thanh toán'),
        'ngay_thanhtoan':fields.date('Ngày thanh toán'),
        'dagui_nganhang':fields.boolean('Đã gửi ngân hàng'),
        'ngaygui_nganhang':fields.date('Ngày gửi ngân hàng'),
        'dagui_hopdong':fields.boolean('Đã gửi hợp đồng'),
        'ngaygui_hopdong':fields.date('Ngày gửi hợp đồng'),
        'dagui_hoadon':fields.boolean('Đã gửi hóa đơn'),
        'ngaygui_hoadon':fields.date('Ngày gửi hóa đơn'),
        'dagui_chungtugoc':fields.boolean('Đã gửi chứng từ gốc'),
        'ngaygui_chungtugoc':fields.date('Ngày gửi chứng từ gốc'),
    }
    
sale_order()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
