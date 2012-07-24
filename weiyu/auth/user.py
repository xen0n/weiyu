#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / auth / user
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

from ..db.mapper import mapper_hub
from .passwd import _do_chkpasswd

STRUCT_AUTH_USER = 'weiyu.auth.user'

mapper_hub.register_struct(STRUCT_AUTH_USER)


@mapper_hub.decoder_for(STRUCT_AUTH_USER, 1)
def user_decoder_v1(obj):
    # {u: uid, e: email, p: passwd object, r: roles, ...}
    # Note that passwd hashes are directly stored without any processing
    uid, email, pswd_obj, roles = obj['u'], obj['e'], obj['p'], obj['r']
    return User(
            uid=uid,
            email=email,
            passwd=pswd_obj,
            roles=roles,
            )


@mapper_hub.encoder_for(STRUCT_AUTH_USER, 1)
def user_encoder_v1(obj):
    return {
            'u': obj.uid,
            'e': obj.email,
            'p': obj.passwd,
            'r': obj.roles,
            }


class User(object):
    def __init__(self, uid, email, passwd, roles):
        self.uid = uid
        self.email = email
        self.passwd = passwd
        self.roles = roles

    def chkpasswd(self, plain_passwd):
        # unify to Unicode
        passwd_str = unicode(plain_passwd, 'utf-8')
        return _do_chkpasswd(self.uid, passwd_str, self.passwd)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
