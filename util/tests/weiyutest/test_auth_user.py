#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / test suite / weiyu.auth.user
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

import unittest

# ``user`` is actually a deprecated module that went away in Python 3.0, and
# is not depended upon by any part of weiyu. so using that name is ok
from weiyu.auth import user
from .common_auth import AuthTestConfig as cfg

class TestAuthUser(unittest.TestCase):
    def setUp(self):
        self.user_objs = {
                1: {
                    '_V': 1,
                    'u': cfg.userid,
                    'e': cfg.email,
                    'p': cfg.psw_objs[1],
                    'r': cfg.roles,
                    },
                }

        self.ref_user = user.User(
                uid=cfg.userid,
                email=cfg.email,
                passwd=cfg.psw_objs[1],
                roles=cfg.roles,
                )

    def test_user_decode_v1(self):
        user_obj = self.user_objs[1]
        usr = user.user_decoder_v1(user_obj)
        ref = self.ref_user

        self.assertEqual(usr.uid, ref.uid)
        self.assertEqual(usr.email, ref.email)
        self.assertEqual(usr.passwd, ref.passwd)
        self.assertEqual(usr.roles, ref.roles)

    def test_user_encode_v1(self):
        user_obj = user.user_encoder_v1(self.ref_user)
        ref = self.user_objs[1]

        for prop in ['u', 'e', 'p', 'r', ]:
            self.assertEqual(user_obj[prop], ref[prop])

    def test_user_chkpasswd(self):
        self.assertTrue(self.ref_user.chkpasswd(cfg.passwd))

    def test_user_setpasswd(self):
        ref_user = self.ref_user

        # first change to new_passwd
        # because of possible salting, do not check passwd hash objects'
        # equality
        self.assertTrue(ref_user.setpasswd(cfg.passwd, cfg.new_passwd))
        self.assertFalse(ref_user.chkpasswd(cfg.passwd))
        self.assertTrue(ref_user.chkpasswd(cfg.new_passwd))

        # then switch back to preserve global state
        self.assertTrue(ref_user.setpasswd(cfg.new_passwd, cfg.passwd))
        self.assertTrue(ref_user.chkpasswd(cfg.passwd))
        self.assertFalse(ref_user.chkpasswd(cfg.new_passwd))

    def test_user_has_role(self):
        ref_user = self.ref_user

        self.assertTrue(ref_user.has_role('role1'))
        self.assertFalse(ref_user.has_role('doesnotexist'))


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
