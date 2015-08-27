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
import random
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from green_erp_viruco_sale.report import amount_to_text_vn
class Parser(report_sxw.rml_parse):
        
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        pool = pooler.get_pool(self.cr.dbname)
        self.localcontext.update({
            'get_month_name':self.get_month_name,
            'get_consignee':self.get_consignee,
            'get_packages':self.get_packages,
        })
    
    def get_month_name(self, month):
        _months = {1:_("JAN"), 2:_("FEB"), 3:_("MAR"), 4:_("APR"), 5:_("MAY"), 6:_("JUN"), 7:_("JUL"), 8:_("AUG"), 9:_("SEP"), 10:_("OCT"), 11:_("NOV"), 12:_("DEC")}
        d = _months[month]
        return d
        
    def get_consignee(self,draft_bl):
        consignee = ''
        if draft_bl.consignee_id:
            consignee = draft_bl.consignee_id.name
        elif draft_bl.consignee_text:
            consignee =  draft_bl.consignee_text
        else:
            consignee = 'To Order'
        return consignee
    
    def get_packages(self,line):
        packages = 'PACKING IN' +' '+ str(line.packages_qty)
        if line.packages_id:
            packages +=' ' + line.packages_id.name
        packages +=' '+line.packages_weight
        return packages
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
