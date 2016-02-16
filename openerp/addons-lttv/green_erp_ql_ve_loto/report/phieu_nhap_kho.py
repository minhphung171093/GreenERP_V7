# -*- coding: utf-8 -*-
##############################################################################
#
#    HLVSolution, Open Source Management Solution
#
##############################################################################
import time
from openerp.report import report_sxw
from openerp import pooler
from openerp.osv import osv
from openerp.tools.translate import _
from green_erp_ql_ve_loto.report import amount_to_text_vn
import random
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class Parser(report_sxw.rml_parse):
        
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        pool = pooler.get_pool(self.cr.dbname)
        self.localcontext.update({
            'get_tong': self.get_tong,
            'convert': self.convert,
        })
    
    def get_tong(self,move_lines):
        tong = 0
        for line in move_lines:
            tong += line.product_qty
        return tong
    
    def convert(self,amount):
        amt_vn = amount_to_text_vn.amount_to_text(amount,'Vé');
        return amt_vn
    