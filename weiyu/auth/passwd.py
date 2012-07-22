#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / auth / password operation
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

from hashlib import md5

from ..db.mapper import mapper_hub

PASSWD_HASH_TYP = 'psw-hash'
KBS_HASH = 1
KBS_PASSMAGIC = r'wwj&kcn4SMTHBBS MD5 p9w2d gen2rat8, //grin~~, 2001/5/7'

mapper_hub.register_struct(PASSWD_HASH_TYP)


# Check routine
def _do_chkpasswd(userid, passwd, stored_hash):
    hash_ver = mapper_hub.get_version(stored_hash)
    hashed_input = mapper_hub.encode(
            PASSWD_HASH_TYP,
            {'userid': userid, 'passwd': passwd, },
            hash_ver,
            )

    return hashed_input['p'] == stored_hash['p']


# Hashers
@mapper_hub.encoder_for(PASSWD_HASH_TYP, KBS_HASH)
def kbs_encode(obj, passmagic=KBS_PASSMAGIC):
    # obj is {u'userid': userid, u'passwd': plaintext_password, }
    userid, passwd = obj['userid'], obj['passwd']
    # XXX Must not be permissive here, or this explicit encoding will
    # instantly become a vulnerability!!
    data = ''.join([passmagic, passwd, passmagic, userid, ]).encode('utf-8')
    return {'p': md5(data).digest(), }


# Decode stub that only raises an exception
def hash_decode_stub(obj):
    raise TypeError('Password hashes are not (trivially) reversible!')


mapper_hub.decoder_for(PASSWD_HASH_TYP, KBS_HASH)(hash_decode_stub)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
