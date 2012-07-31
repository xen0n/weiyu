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

from ..helpers.misc import smartstr
from ..db.mapper import mapper_hub
from ..db.mapper.base import Document
from .passwd import STRUCT_AUTH_PASSWD, _do_chkpasswd

STRUCT_AUTH_USER = 'weiyu.auth.user'

mapper_hub.register_struct(STRUCT_AUTH_USER)


@mapper_hub.decoder_for(STRUCT_AUTH_USER, 1)
def user_decoder_v1(obj):
    # {u: uid, e: email, p: passwd object, r: roles, ...}
    # Note that passwd hashes are directly stored without any processing
    _id = obj.get('_id', None)
    uid, email, pswd_obj, roles = obj['u'], obj['e'], obj['p'], obj['r']

    return User(
            _id=_id,
            uid=uid,
            email=email,
            passwd=pswd_obj,
            roles=roles,
            )


@mapper_hub.encoder_for(STRUCT_AUTH_USER, 1)
def user_encoder_v1(obj):
    return {
            'u': obj['uid'],
            'e': obj['email'],
            'p': obj['passwd'],
            'r': obj['roles'],
            }


class User(Document):
    struct_id = STRUCT_AUTH_USER

    def chkpasswd(self, plain_passwd):
        # unify to Unicode
        plain_passwd = smartstr(plain_passwd)

        return _do_chkpasswd(self['uid'], plain_passwd, self['passwd'])

    def setpasswd(self, old_passwd, new_passwd):
        if not self.chkpasswd(old_passwd):
            # old password is wrong
            return False

        # new_passwd must be passed in as unicode
        new_passwd = smartstr(new_passwd)
        self['passwd'] = mapper_hub.encode(
                STRUCT_AUTH_PASSWD,
                {
                    'userid': self['uid'],
                    'passwd': new_passwd,
                    },
                )
        
        # TODO: invalidate sessions?
        return True

    def has_role(self, role):
        role = smartstr(role)

        return role in self['roles']


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
