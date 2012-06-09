#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# weiyu / utilities / KBS low-level structures description
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

import sys
import struct
from ctypes import *


# Site constants
IDLEN, NAMELEN, OLDPASSLEN, MD5PASSLEN = 12, 40, 14, 16
FILENAME_LEN, OWNER_LEN, ARTICLE_TITLE_LEN = 20, 14, 60

# IPv4
##IPLEN = 16
# IPv6
IPLEN = 46

MAXCLUB = 128


# Structure layouts
fileheader_fmt = b'@%(fnlen)dsIIIiIII2s%(ownerlen)dsIiI%(titlelen)ds4B' % {
        b'fnlen': FILENAME_LEN,
        b'ownerlen': OWNER_LEN,
        b'titlelen': ARTICLE_TITLE_LEN,
        }

# b'@%(fnlen)dsIIIiIII2s%(ownerlen)dsIiI%(titlelen)ds4B'
class fileheader(Structure):
    _fields_ = [
            ('filename', c_char * FILENAME_LEN),
            ('id', c_uint),
            ('groupid', c_uint),
            ('reid', c_uint),
            ('o_bid', c_int),
            ('o_id', c_uint),
            ('o_groupid', c_uint),
            ('o_reid', c_uint),
            ('innflag', c_char * 2),
            ('owner', c_char * OWNER_LEN),
            ('eff_size', c_uint),
            ('posttime', c_int),
            ('attachment', c_uint),
            ('title', c_char * ARTICLE_TITLE_LEN),
            ('accessed', c_ubyte * 4),
            ]


# b'@14sBBi46sII14s2b40s4I4I16sIiii2IiiiiI7i'
class userec(Structure):
    _fields_ = [
            ('userid', c_char * (IDLEN + 2)),
            ('flags', c_ubyte),
            ('title', c_ubyte),
            ('firstlogin', c_int),
            ('lasthost', c_char * IPLEN),
            ('numlogins', c_uint),
            ('numposts', c_uint),
            ('passwd', c_char * OLDPASSLEN),
            ('unused_padding', c_byte * 2),
            ('username', c_char * NAMELEN),
            ('club_read_rights', c_uint * (MAXCLUB >> 5)),
            ('club_write_rights', c_uint * (MAXCLUB >> 5)),
            ('md5passwd', c_char * MD5PASSLEN),
            ('userlevel', c_uint),
            ('lastlogin', c_int),
            ('stay', c_int),
            ('signature', c_int),
            ('userdefine', c_uint * 2),
            ('notedate', c_int),
            ('noteline', c_int),
            ('unused_atppp', c_int),
            ('exittime', c_int),
            ('usedspace', c_uint),
            ('unused', c_int * 7),
            ]


# main function
def main(argc, argv):
    return 0


if __name__ == '__main__':
    sys.exit(main(len(sys.argv), sys.argv))


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
