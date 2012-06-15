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
if __name__ != '__main__':
    from . import sitecfg
else:
    # XXX kludge!
    import sitecfg


# helper
def c_str(l):
    return c_char * l


# Structure layouts
class fileheader(Structure):
    _fields_ = [
            ('filename', c_str(sitecfg.FILENAME_LEN)),
            ('id', c_uint),
            ('groupid', c_uint),
            ('reid', c_uint),
            ('o_bid', c_int),
            ('o_id', c_uint),
            ('o_groupid', c_uint),
            ('o_reid', c_uint),
            ('innflag', c_str(2)),
            ('owner', c_str(sitecfg.OWNER_LEN)),
            ('eff_size', c_uint),
            ('posttime', c_int),
            ('attachment', c_uint),
            ('title', c_str(sitecfg.ARTICLE_TITLE_LEN)),
            ('accessed', c_ubyte * 4),
            ]


class _board_data_t(Union):
    _fields_ = [
            ('adv_club', c_uint),
            ('group_total', c_uint),
            ]


class boardheader(Structure):
    _fields_ = [
            ('filename', c_str(sitecfg.STRLEN)),
            ('BM', c_str(sitecfg.BM_LEN)),
            ('title', c_str(sitecfg.STRLEN)),
            ('level', c_uint),
            ('idseq', c_uint),
            ('clubnum', c_uint),
            ('flag', c_uint),
            ('board_data', _board_data_t),
            ('createtime', c_int),
            ('score_level', c_uint),
            ('ann_path', c_str(128)),
            ('group', c_int),
            ('title_level', c_byte),
            ('des', c_str(195)),
            ]


class userec(Structure):
    _fields_ = [
            ('userid', c_str(sitecfg.IDLEN + 2)),
            ('flags', c_ubyte),
            ('title', c_ubyte),
            ('firstlogin', c_int),
            ('lasthost', c_str(sitecfg.IPLEN)),
            ('numlogins', c_uint),
            ('numposts', c_uint),
            ('passwd', c_str(sitecfg.OLDPASSLEN)),
            ('unused_padding', c_byte * 2),
            ('username', c_str(sitecfg.NAMELEN)),
            ('club_read_rights', c_uint * (sitecfg.MAXCLUB >> 5)),
            ('club_write_rights', c_uint * (sitecfg.MAXCLUB >> 5)),
            ('md5passwd', c_str(sitecfg.MD5PASSLEN)),
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


class userdata(Structure):
    _fields_ = [
            ('userid', c_str(sitecfg.IDLEN + 2)),
            ('__reserved', c_byte * 2),
            ('realemail', c_str(sitecfg.STRLEN - 16)),
            ('realname', c_str(sitecfg.NAMELEN)),
            ('address', c_str(sitecfg.STRLEN)),
            ('email', c_str(sitecfg.STRLEN)),
            ('gender', c_byte),
            ('birthyear', c_ubyte),
            ('birthmonth', c_ubyte),
            ('birthday', c_ubyte),
            ('reg_email', c_str(sitecfg.STRLEN)),
            ('mobileregistered', c_int),
            ('mobilenumber', c_str(sitecfg.MOBILE_NUMBER_LEN)),
            ('OICQ', c_str(sitecfg.STRLEN)),
            ('ICQ', c_str(sitecfg.STRLEN)),
            ('MSN', c_str(sitecfg.STRLEN)),
            ('homepage', c_str(sitecfg.STRLEN)),
            ('userface_img', c_int),
            ('userface_url', c_str(sitecfg.STRLEN)),
            ('userface_width', c_ubyte),
            ('userface_height', c_ubyte),
            ('group', c_uint),
            ('country', c_str(sitecfg.STRLEN)),
            ('province', c_str(sitecfg.STRLEN)),
            ('city', c_str(sitecfg.STRLEN)),
            ('shengxiao', c_ubyte),
            ('bloodtype', c_ubyte),
            ('religion', c_ubyte),
            ('profession', c_ubyte),
            ('married', c_ubyte),
            ('education', c_ubyte),
            ('graduateschool', c_str(sitecfg.STRLEN)),
            ('character', c_ubyte),
            ('photo_url', c_str(sitecfg.STRLEN)),
            ('telephone', c_str(sitecfg.STRLEN)),
            ('smsprefix', c_str(41)),
            ('smsend', c_str(41)),
            ('smsdef', c_uint),
            ('signum', c_int),
            ('this_field_is_reserved_by_atppp', c_int),
            ('lastinvite', c_int),
            ]


# main function
def main(argc, argv):
    from ctypes import sizeof
    structs = [userec, userdata, fileheader, boardheader, ]

    for s in structs:
        print ('sizeof(%s) == %d' % (unicode(s), sizeof(s), ))

    return 0


if __name__ == '__main__':
    sys.exit(main(len(sys.argv), sys.argv))


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
