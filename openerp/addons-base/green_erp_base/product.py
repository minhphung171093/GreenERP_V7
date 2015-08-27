# -*- coding: utf-8 -*-
##############################################################################
#
##############################################################################

from osv import osv, fields
import decimal_precision as dp
from tools.translate import _
import time
DATE_FORMAT = "%Y-%m-%d"
from openerp import SUPERUSER_ID
import xlrd
from lxml import etree

import os
from openerp import modules


class product_product(osv.osv):
    _inherit = "product.product"
    
    _columns = {
        'shop_ids': fields.many2many('sale.shop', 'product_shop_rel', 'product_id', 'shop_id', 'Product Shop'),
    }
    
product_product()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: