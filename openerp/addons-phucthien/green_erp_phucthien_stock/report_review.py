# -*- coding: utf-8 -*-
##############################################################################
#
#
##############################################################################

import time
from osv import fields, osv
from tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
import decimal_precision as dp
from tools.translate import _
from openerp import SUPERUSER_ID
from datetime import datetime
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

class dulieu_donghang_review(osv.osv):
    _name = "dulieu.donghang.review"
    _columns = {
        'name': fields.char('Name', size=1024),
        'tu_ngay':fields.date('Từ ngày'),
        'den_ngay':fields.date('Đến ngày'),
        'date_from_title':fields.char('Từ ngày', size=1024),
        'date_to_title':fields.char('Đến ngày', size=1024),
        'dulieu_donghang_review_line':fields.one2many('dulieu.donghang.review.line','dulieu_donghang_id','Review In'),

        }
#     def print_xls(self, cr, uid, ids, context=None):
#         if context is None:
#             context = {}
# #         datas = {'ids': context.get('active_ids', [])}
#         datas = {'ids': ids}
#         datas['model'] = 'congno.vacine'
#         datas['form'] = self.read(cr, uid, ids)[0]
#         datas['form'].update({'active_id':context.get('active_ids',False)})
#         return {'type': 'ir.actions.report.xml', 'report_name': 'congno_vacine_report', 'datas': datas}    
dulieu_donghang_review()

class dulieu_donghang_review_line(osv.osv):
    _name = "dulieu.donghang.review.line"
    _columns = {
        'dulieu_donghang_id':fields.many2one('dulieu.donghang.review','Report In',ondelete='cascade'),
        'stt': fields.char('STT', size=1024),
        'so_phieuxuat':fields.char('Số Phiếu Xuất'),
        'ngay':fields.char('Ngày'),
        'khach_hang':fields.char('Tên Khách Hàng'),
        'sl_nhietke':fields.char('Số Lượng Nhiệt Kế Còn Lại'),
        'bb_giaonhan':fields.char('Biên Bản Giao Nhận'),
        }
dulieu_donghang_review_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
