#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# weiyu / kbslib / low-level structures description
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

# for site constants
from . import sitecfg


# Structure layouts
class fileheader(Structure):
    _fields_ = [
            ('filename', c_char * sitecfg.FILENAME_LEN),
            ('id', c_uint),
            ('groupid', c_uint),
            ('reid', c_uint),
            ('o_bid', c_int),
            ('o_id', c_uint),
            ('o_groupid', c_uint),
            ('o_reid', c_uint),
            ('innflag', c_char * 2),
            ('owner', c_char * sitecfg.OWNER_LEN),
            ('eff_size', c_uint),
            ('posttime', c_int),
            ('attachment', c_uint),
            ('title', c_char * sitecfg.ARTICLE_TITLE_LEN),
            ('accessed', c_ubyte * 4),
            ]


class _board_data_t(Union):
    _fields_ = [
            ('adv_club', c_uint),
            ('group_total', c_uint),
            ]


class boardheader(Structure):
    _fields_ = [
            ('filename', c_char * sitecfg.STRLEN),
            ('BM', c_char * sitecfg.BM_LEN),
            ('title', c_char * sitecfg.STRLEN),
            ('level', c_uint),
            ('idseq', c_uint),
            ('clubnum', c_uint),
            ('flag', c_uint),
            ('board_data', _board_data_t),
            ('createtime', c_int),
            ('score_level', c_uint),
            ('ann_path', c_char * 128),
            ('group', c_int),
            ('title_level', c_byte),
            ('des', c_char * 195),
            ]


class userec(Structure):
    _fields_ = [
            ('userid', c_char * (sitecfg.IDLEN + 2)),
            ('flags', c_ubyte),
            ('title', c_ubyte),
            ('firstlogin', c_int),
            ('lasthost', c_char * sitecfg.IPLEN),
            ('numlogins', c_uint),
            ('numposts', c_uint),
            ('passwd', c_char * sitecfg.OLDPASSLEN),
            ('unused_padding', c_byte * 2),
            ('username', c_char * sitecfg.NAMELEN),
            ('club_read_rights', c_uint * (sitecfg.MAXCLUB >> 5)),
            ('club_write_rights', c_uint * (sitecfg.MAXCLUB >> 5)),
            ('md5passwd', c_char * sitecfg.MD5PASSLEN),
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
