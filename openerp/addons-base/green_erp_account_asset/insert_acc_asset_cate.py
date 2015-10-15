# -*- encoding: utf-8 -*-
##############################################################################
#
#
##############################################################################

from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
from openerp import SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from datetime import datetime
import datetime
import calendar

class account_asset_category(osv.osv):
    _inherit = "account.asset.category"
    
    def init(self, cr):
        tam_ids = self.pool.get('bang.tam.init').search(cr,1,[('name', '=', 'account.asset.category')])
        if not tam_ids:
            new_id = self.pool.get('bang.tam.init').create(cr,1,{
                                                        'name': 'account.asset.category',
                                                        })
        tam_ids = self.pool.get('bang.tam.init').search(cr,1,[('name', '=', 'account.asset.category'),('da_chay', '=', False)])
        if tam_ids:
            seq_ids = self.pool.get('ir.sequence').search(cr,1,[('name', '=', 'Nhật ký tài sản')])
            self.pool.get('account.journal').create(cr,1,{
                              'name': 'Nhật ký tài sản',
                              'code': '08',
                              'type': 'general',
                              'company_id': 1,
                              'update_posted': True,
                              'group_invoice_lines': True,
                              'sequence_id': seq_ids[0],
                              })
            journal_ids = self.pool.get('account.journal').search(cr,1,[('code', '=', '08')])
            account_asset_tscdhh_ids = self.pool.get('account.account').search(cr,1,[('code', '=', '2111')])
            account_depreciation_tscdhh_ids = self.pool.get('account.account').search(cr,1,[('code', '=', '2111')])
            self.create(cr,1,{
                              'name': 'TSCD hữu hình',
                              'company_id': 1,
                              'journal_id': journal_ids[0],
                              'account_asset_id': account_asset_tscdhh_ids[0],
                              'account_depreciation_id': account_depreciation_tscdhh_ids[0],
                              'method_time': 'number',
                              'method': 'linear',
                              'method_number': 5,
                              'porata': True,
                              'method_period': 1,
                              })
            
            account_asset_ncvkt_ids = self.pool.get('account.account').search(cr,1,[('code', '=', '2111')])
            account_depreciation_ncvkt_ids = self.pool.get('account.account').search(cr,1,[('code', '=', '2141')])
            self.create(cr,1,{
                              'name': 'Nhà cửa, vật kiến trúc',
                              'company_id': 1,
                              'journal_id': journal_ids[0],
                              'account_asset_id': account_asset_ncvkt_ids[0],
                              'account_depreciation_id': account_depreciation_ncvkt_ids[0],
                              'method_time': 'number',
                              'method': 'linear',
                              'method_number': 60,
                              'porata': True,
                              'method_period': 1,
                              })
            
            account_asset_mmtb_ids = self.pool.get('account.account').search(cr,1,[('code', '=', '2112')])
            account_depreciation_mmtb_ids = self.pool.get('account.account').search(cr,1,[('code', '=', '2141')])
            self.create(cr,1,{
                              'name': 'Máy móc, thiết bị',
                              'company_id': 1,
                              'journal_id': journal_ids[0],
                              'account_asset_id': account_asset_mmtb_ids[0],
                              'account_depreciation_id': account_depreciation_mmtb_ids[0],
                              'method_time': 'number',
                              'method': 'linear',
                              'method_number': 60,
                              'porata': True,
                              'method_period': 1,
                              })
            
            account_asset_ptvttd_ids = self.pool.get('account.account').search(cr,1,[('code', '=', '2113')])
            account_depreciation_ptvttd_ids = self.pool.get('account.account').search(cr,1,[('code', '=', '2141')])
            self.create(cr,1,{
                              'name': 'Phương tiện vận tải truyền dẫn',
                              'company_id': 1,
                              'journal_id': journal_ids[0],
                              'account_asset_id': account_asset_ptvttd_ids[0],
                              'account_depreciation_id': account_depreciation_ptvttd_ids[0],
                              'method_time': 'number',
                              'method': 'linear',
                              'method_number': 72,
                              'porata': True,
                              'method_period': 1,
                              })
            
            account_asset_tbdcql_ids = self.pool.get('account.account').search(cr,1,[('code', '=', '2114')])
            account_depreciation_tbdcql_ids = self.pool.get('account.account').search(cr,1,[('code', '=', '2141')])
            self.create(cr,1,{
                              'name': 'Thiết bị, dụng cụ quản lý',
                              'company_id': 1,
                              'journal_id': journal_ids[0],
                              'account_asset_id': account_asset_tbdcql_ids[0],
                              'account_depreciation_id': account_depreciation_tbdcql_ids[0],
                              'method_time': 'number',
                              'method': 'linear',
                              'method_number': 60,
                              'porata': True,
                              'method_period': 1,
                              })
            
            account_asset_tscdhhk_ids = self.pool.get('account.account').search(cr,1,[('code', '=', '2118')])
            account_depreciation_tscdhhk_ids = self.pool.get('account.account').search(cr,1,[('code', '=', '2141')])
            self.create(cr,1,{
                              'name': 'TSCD hữu hình khác',
                              'company_id': 1,
                              'journal_id': journal_ids[0],
                              'account_asset_id': account_asset_tscdhhk_ids[0],
                              'account_depreciation_id': account_depreciation_tscdhhk_ids[0],
                              'method_time': 'number',
                              'method': 'linear',
                              'method_number': 60,
                              'porata': True,
                              'method_period': 1,
                              })
            
            account_asset_tscdvh_ids = self.pool.get('account.account').search(cr,1,[('code', '=', '2131')])
            account_depreciation_tscdvh_ids = self.pool.get('account.account').search(cr,1,[('code', '=', '2131')])
            self.create(cr,1,{
                              'name': 'TSCD vô hình',
                              'company_id': 1,
                              'journal_id': journal_ids[0],
                              'account_asset_id': account_asset_tscdvh_ids[0],
                              'account_depreciation_id': account_depreciation_tscdvh_ids[0],
                              'method_time': 'number',
                              'method': 'linear',
                              'method_number': 60,
                              'porata': True,
                              'method_period': 1,
                              })
            
            account_asset_qsdd_ids = self.pool.get('account.account').search(cr,1,[('code', '=', '2131')])
            account_depreciation_qsdd_ids = self.pool.get('account.account').search(cr,1,[('code', '=', '2143')])
            self.create(cr,1,{
                              'name': 'Quyền sử dụng đất',
                              'company_id': 1,
                              'journal_id': journal_ids[0],
                              'account_asset_id': account_asset_qsdd_ids[0],
                              'account_depreciation_id': account_depreciation_qsdd_ids[0],
                              'method_time': 'number',
                              'method': 'linear',
                              'method_number': 60,
                              'porata': True,
                              'method_period': 1,
                              })
            
            account_asset_qph_ids = self.pool.get('account.account').search(cr,1,[('code', '=', '2132')])
            account_depreciation_qph_ids = self.pool.get('account.account').search(cr,1,[('code', '=', '2143')])
            self.create(cr,1,{
                              'name': 'Quyền phát hành',
                              'company_id': 1,
                              'journal_id': journal_ids[0],
                              'account_asset_id': account_asset_qph_ids[0],
                              'account_depreciation_id': account_depreciation_qph_ids[0],
                              'method_time': 'number',
                              'method': 'linear',
                              'method_number': 60,
                              'porata': True,
                              'method_period': 1,
                              })
            
            account_asset_bqbsc_ids = self.pool.get('account.account').search(cr,1,[('code', '=', '2133')])
            account_depreciation_bqbsc_ids = self.pool.get('account.account').search(cr,1,[('code', '=', '2143')])
            self.create(cr,1,{
                              'name': 'Bản quyền, bằng sáng chế',
                              'company_id': 1,
                              'journal_id': journal_ids[0],
                              'account_asset_id': account_asset_bqbsc_ids[0],
                              'account_depreciation_id': account_depreciation_bqbsc_ids[0],
                              'method_time': 'number',
                              'method': 'linear',
                              'method_number': 60,
                              'porata': True,
                              'method_period': 1,
                              })
            
            account_asset_nhhh_ids = self.pool.get('account.account').search(cr,1,[('code', '=', '2134')])
            account_depreciation_nhhh_ids = self.pool.get('account.account').search(cr,1,[('code', '=', '2143')])
            self.create(cr,1,{
                              'name': 'Nhãn hiệu hàng hóa',
                              'company_id': 1,
                              'journal_id': journal_ids[0],
                              'account_asset_id': account_asset_nhhh_ids[0],
                              'account_depreciation_id': account_depreciation_nhhh_ids[0],
                              'method_time': 'number',
                              'method': 'linear',
                              'method_number': 60,
                              'porata': True,
                              'method_period': 1,
                              })
            
            account_asset_pmmt_ids = self.pool.get('account.account').search(cr,1,[('code', '=', '2135')])
            account_depreciation_pmmt_ids = self.pool.get('account.account').search(cr,1,[('code', '=', '2143')])
            self.create(cr,1,{
                              'name': 'Phần mềm máy tính',
                              'company_id': 1,
                              'journal_id': journal_ids[0],
                              'account_asset_id': account_asset_nhhh_ids[0],
                              'account_depreciation_id': account_depreciation_nhhh_ids[0],
                              'method_time': 'number',
                              'method': 'linear',
                              'method_number': 60,
                              'porata': True,
                              'method_period': 1,
                              })
            
            account_asset_gpvgpnq_ids = self.pool.get('account.account').search(cr,1,[('code', '=', '2136')])
            account_depreciation_gpvgpnq_ids = self.pool.get('account.account').search(cr,1,[('code', '=', '2143')])
            self.create(cr,1,{
                              'name': 'Giấy phép và giấy phép nhượng quyền',
                              'company_id': 1,
                              'journal_id': journal_ids[0],
                              'account_asset_id': account_asset_gpvgpnq_ids[0],
                              'account_depreciation_id': account_depreciation_gpvgpnq_ids[0],
                              'method_time': 'number',
                              'method': 'linear',
                              'method_number': 60,
                              'porata': True,
                              'method_period': 1,
                              })
            
            account_asset_tscdvhk_ids = self.pool.get('account.account').search(cr,1,[('code', '=', '2138')])
            account_depreciation_tscdvhk_ids = self.pool.get('account.account').search(cr,1,[('code', '=', '2143')])
            self.create(cr,1,{
                              'name': 'TSCD vô hình khác',
                              'company_id': 1,
                              'journal_id': journal_ids[0],
                              'account_asset_id': account_asset_tscdvhk_ids[0],
                              'account_depreciation_id': account_depreciation_tscdvhk_ids[0],
                              'method_time': 'number',
                              'method': 'linear',
                              'method_number': 60,
                              'porata': True,
                              'method_period': 1,
                              })
            
            account_asset_cpttnh_ids = self.pool.get('account.account').search(cr,1,[('code', '=', '2421')])
            account_depreciation_cpttnh_ids = self.pool.get('account.account').search(cr,1,[('code', '=', '2421')])
            self.create(cr,1,{
                              'name': 'Chi phí trả trước ngắn hạn',
                              'company_id': 1,
                              'journal_id': journal_ids[0],
                              'account_asset_id': account_asset_cpttnh_ids[0],
                              'account_depreciation_id': account_depreciation_cpttnh_ids[0],
                              'method_time': 'number',
                              'method': 'linear',
                              'method_number': 12,
                              'porata': True,
                              'method_period': 1,
                              })
            
            account_asset_cpttdh_ids = self.pool.get('account.account').search(cr,1,[('code', '=', '2422')])
            account_depreciation_cpttdh_ids = self.pool.get('account.account').search(cr,1,[('code', '=', '2422')])
            self.create(cr,1,{
                              'name': 'Chi phí trả trước dài hạn',
                              'company_id': 1,
                              'journal_id': journal_ids[0],
                              'account_asset_id': account_asset_cpttdh_ids[0],
                              'account_depreciation_id': account_depreciation_cpttdh_ids[0],
                              'method_time': 'number',
                              'method': 'linear',
                              'method_number': 36,
                              'porata': True,
                              'method_period': 1,
                              })
            self.pool.get('bang.tam.init').write(cr,1,tam_ids,{
                                                               'da_chay': True,
                                                               })
account_asset_category()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
