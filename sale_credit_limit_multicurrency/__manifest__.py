##############################################################################
#
#    Copyright (C) 2015  ADHOC SA  (http://www.adhoc.com.ar)
#    All Rights Reserved.
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
    'name': 'Sale Exception Credit Limit for dmd',
    'version': "1.1.0.0",
    'author': 'Making',
    'website': 'https://www.making.com.ar',
    'license': 'AGPL-3',
    'depends': [
        'sale_exception',
        'sale_exception_credit_limit',
        'sale_exceptions_ignore_approve',
    ],
    'data': [
    'views/res.partner.xml',
    ],
    'demo': [
    ],
    'installable': True,
}
