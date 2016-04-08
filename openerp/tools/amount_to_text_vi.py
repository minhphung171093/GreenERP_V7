# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-TODAY OpenERP SA (<http://openerp.com>).
#    Copyright (c) 2010-TODAY Phong Nguyen-Thanh (phong.nguyen_thanh@yahoo.com)
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>, or
#    write to the Free Software Foundation, Inc., 
#    59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
#    WARNING: This program as such is intended to be used by professional
#    programmers who take the whole responsability of assessing all potential
#    consequences resulting from its eventual inadequacies and bugs
#    End users who are looking for a ready-to-use solution with commercial
#    garantees and support are strongly adviced to contract a Free Software
#    Service Company
#
##############################################################################

#-------------------------------------------------------------
# Vietnamese
#-------------------------------------------------------------
import amount_to_text


to_19_vi = ('không', 'một', 'hai', 'ba', 'bốn', 'năm', 'sáu',
          'bảy', 'tám', 'chín', 'mười', 'mười một', 'mười hai', 'mười ba',
          'mười bốn', 'mười lăm', 'mười sáu', 'mười bảy', 'mười tám', 'mười chín')
tens_vi = ('hai mươi', 'ba mươi', 'bốn mươi', 'năm mươi', 'sáu mươi', 'bảy mươi', 'tám mươi', 'chín mươi')
denom_vi = ('',
          'ngàn', 'triệu', 'tỉ', 'ngàn tỉ', 'triệu tỉ',
          'tỉ tỉ', 'ngàn tỉ tỉ', 'triệu tỉ tỉ', 'tỉ tỉ tỉ', 'Nonillion',
          'Décillion', 'Undecillion', 'Duodecillion', 'Tredecillion', 'Quattuordecillion',
          'Sexdecillion', 'Septendecillion', 'Octodecillion', 'Icosillion', 'Vigintillion')

# convert a value < 100 to Vietnamese.
def _convert_nn_vi(val):
    if val < 20:
        return to_19_vi[val]
    for (dcap, dval) in ((k, 20 + (10 * v)) for (v, k) in enumerate(tens_vi)):
        if dval + 10 > val:
            if (val % 10) == 1:
                return dcap + ' mốt'
            elif (val % 10) == 5:
                return dcap + ' lăm'
            elif val % 10:
                return dcap + ' ' + to_19_vi[val % 10]
            return dcap

# convert a value < 1000 to Vietnamese, special cased because it is the level that kicks 
# off the < 100 special case.  The rest are more general.  This also allows you to
# get strings in the form of 'forty-five hundred' if called directly.
def _convert_nnn_vi(val):
    word = ''
    (mod, rem) = (val % 100, val // 100)
    if rem > 0:
        word = to_19_vi[rem] + ' trăm'
        if mod > 0:
            word = word + ' '
    if mod > 0:
        if mod < 10:
            word = word + 'lẻ '
        word = word + _convert_nn_vi(mod)
    return word

def vi_number(val):
    if val < 100:
        return _convert_nn_vi(val)
    if val < 1000:
         return _convert_nnn_vi(val)
    for (didx, dval) in ((v - 1, 1000 ** v) for v in range(len(denom_vi))):
        if dval > val:
            mod = 1000 ** didx
            l = val // mod
            r = val - (l * mod)
            if l < 10:
                ret = _convert_nn_vi(l) + ' ' + denom_vi[didx]
            else:
                ret = _convert_nnn_vi(l) + ' ' + denom_vi[didx]
            if r > 0:
                ret = ret + ', ' + vi_number(r)
            return ret

def amount_to_text_vi(number, currency):
    if currency == 'VND':
        currency = 'đồng'
    number = '%.2f' % number
    units_name = currency
    list = str(number).split('.')
    start_word = vi_number(abs(int(list[0])))
    cents_number = int(list[1])
    end_word = ''
    if cents_number > 0:
	    end_word = ' ' + vi_number(int(list[1]))

    cents_name = (cents_number > 1) and ' xu' or ' chẵn'
    final_result = start_word + ' ' + units_name + end_word + cents_name
    return final_result

amount_to_text.add_amount_to_text_function('vi', amount_to_text_vi)


import random
if __name__ == '__main__':
    from sys import argv

    lang = 'đồng'
    if len(argv) < 2:
        for i in range(1, 200):
            print i, ">>", amount_to_text_vi(i, lang)
            j = random.random()
            print i + j, ">>", amount_to_text_vi(i + j, lang)
#            amount_to_text.amount_to_text(i+j, 'vi', currency='đồng')
#            amount_to_text.amount_to_text(i+j, 'vi', currency='euro')
#            amount_to_text.amount_to_text(i+j, 'vi', currency='đô-la')
        for i in range(200, 999999, 139):
            print i, ">>", amount_to_text_vi(i, lang)
    else:
        print amount_to_text_vi(int(argv[1]), lang)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

