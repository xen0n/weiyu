#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# weiyu / kbslib / site-specific constants
#
# Copyright (C) 2012 Wang Xuerui <idontknw.wang-at-gmail-dot-com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals, division

# weiyu helper constants
KBS_ENCODING = 'gbk'
SIGN_LINES = 6


# these are original KBS constants from various places...
# remember, grep(1) is your friend
IDLEN, NAMELEN, OLDPASSLEN, MD5PASSLEN, STRLEN = 12, 40, 14, 16, 80
FILENAME_LEN, OWNER_LEN, ARTICLE_TITLE_LEN, BM_LEN = 20, 14, 60, 60
MOBILE_NUMBER_LEN = 17

# from the result of whole KBS tree grepping, this MAX_SIGNATURES is
# apparently NOT used... kind of weird :-/
MAXCLUB, MAX_SIGNATURES = 128, 20


HAVE_IPV6 = True
IPLEN = 46 if HAVE_IPV6 else 16


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
