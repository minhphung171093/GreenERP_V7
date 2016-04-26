# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'GreenERP Ve Loto',
    'version': '1.1',
    "author" : "nguyentoanit@gmail.com",
    'website': 'http://incomtech.com/',
    "category": 'GreenERP',
    'sequence': 1,
    'description': """
    """,
    'depends': ['green_erp_base','green_erp_ql_tra_thuong','product','sale','purchase','account_accountant','report_aeroo','report_aeroo_ooo','stock'],
    'data': [
        'security/ql_ve_loto_security.xml',
        'security/ir.model.access.csv',
        'ql_ve_loto_view.xml',
        'report/chitiet_vetuchon_trungthuong_view.xml',
        'report/doanhthu_xoso_tuchon_view.xml',
        'report/ket_qua_xoso_view.xml',
        'report/veban_theolo_report_view.xml',
        'report/doanhthu_xoso_tuchon_theothoigian_view.xml',
        'report/tonghop_vetuchon_tonkho_report_view.xml',
        'report/vetuchon_dangluuhanh_report_view.xml',
        'report/chitiet_vetuchon_trungthuong_theongay_view.xml',
        'report/tonghop_doanhthu_tieuthu_view.xml',
        'report/tonghop_doanhthu_tieuthu_all_view.xml',
        'report/tonghop_trungthuong_view.xml',
        'report/tonghop_trungthuong_theongay_view.xml',
        'report/tonghop_trungthuong_theodl_view.xml',
        'report/veban_theolo_theongay_report_view.xml',
        'report/phieu_xuat_kho_view.xml',
        'report/quyettoan_ve_ngay_view.xml',
        'report/tonghop_doanhthu_tieuthu_theothoigian_view.xml',
        'report/quyettoan_ve_thang_view.xml',
        'report/bangke_chitiet_hethan_view.xml',
        'report/chitiet_trathuong_ngay_view.xml',
        'report/chitiet_chi_uyquyen_view.xml',
        'report/tonghop_chi_uyquyen_view.xml',
        'report/tonghop_chi_uyquyen_all_view.xml',
        'report/bangke_hethan_datra_view.xml',
        'report/dttt_all_dly_theo_tgian_view.xml',
        'report/thtt_theo_tgian_dly1_view.xml',
        'report/thtt_theo_tgian_all_dly_view.xml',
        
        'wizard/chitiet_vetuchon_trungthuong_view.xml',
        'wizard/doanhthu_xoso_tuchon_view.xml',
        'wizard/veban_theolo_view.xml',
        'wizard/tonghop_vetuchon_tonkho_view.xml',
        'wizard/vetuchon_dangluuhanh_view.xml',
        'wizard/chitiet_vetuchon_trungthuong_theongay_view.xml',
        'wizard/tonghop_doanhthu_tieuthu_view.xml',
        'wizard/tonghop_doanhthu_tieuthu_all_view.xml',
        'wizard/doanhthu_xoso_tuchon_theothoigian_view.xml',
        'wizard/tonghop_trungthuong_view.xml',
        'wizard/tonghop_trungthuong_theongay_view.xml',
        'wizard/tonghop_trungthuong_theodl_view.xml',
        'wizard/tonghop_doanhthu_tieuthu_theothoigian_view.xml',
        'wizard/veban_theolo_theongay_view.xml',
        'wizard/stock_partial_picking_view.xml',
        'wizard/quyettoan_ve_thang_view.xml',
        'wizard/bangke_chitiet_hethan_view.xml',
        'wizard/chitiet_trathuong_ngay_view.xml',
        'wizard/chitiet_chi_uyquyen_view.xml',
        'wizard/tonghop_chi_uyquyen_view.xml',
        'wizard/tonghop_chi_uyquyen_all_view.xml',
        'wizard/bangke_hethan_datra_view.xml',
        'wizard/dttt_all_dly_theo_tgian_view.xml',
        'wizard/thtt_theo_tgian_dly1_view.xml',
        'wizard/thtt_theo_tgian_all_dly_view.xml',
        
        'ql_ve_loto_schedule.xml',
        'purchase_view.xml',
        'stock_view.xml',
        'sale_view.xml',
        'import_ve_loto_view.xml',
        'dongbo_view.xml',
        'ql_tra_thuong_view.xml',
        'menu.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
