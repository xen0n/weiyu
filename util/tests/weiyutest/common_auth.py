#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / test suite / common data for weiyu.auth
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

PASSWD_VERSIONS = (
        (1, 'kbs', ),
        )


class AuthTestConfig(object):
    userid = 'testuser123'
    email = 'test@example.com'
    passwd = '*JE&%5e^&YU4w%ftWRtfSEfAEt%$&Ww47%6w56T#Wtq345q2'
    new_passwd = r"-+|0\\!n.eOO!>UFg lO`J3_/1p)kLB'"
    roles = ['role1', 'role2', ]

    psw_packet = {'userid': userid, 'passwd': passwd, }
    stored_hashes = {
        'kbs': b'\xdb6\xe2\xd2ev\xcc\xc8\xe3b9\xe8\xb7g\xa0\xde',
        }
    new_stored_hashes = {
        'kbs': b'V\xa5+\xf0\xa7\x9a$q9\xfb\xa2_\x87Q\xa1^',
        }

    psw_objs, new_psw_objs = {}, {}
    for _ver, _name in PASSWD_VERSIONS:
        psw_objs[_ver] = {'_V': _ver, 'p': stored_hashes[_name], }
        new_psw_objs[_ver] = {'_V': _ver, 'p': new_stored_hashes[_name], }
    del _ver, _name


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
