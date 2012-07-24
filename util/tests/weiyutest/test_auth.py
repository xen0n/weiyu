#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / test suite / weiyu.auth
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

from weiyu.auth import passwd

# ``user`` is actually a deprecated module that went away in Python 3.0, and
# is not depended upon by any part of weiyu. so using that name is ok
from weiyu.auth import user


class TestAuthPasswd(unittest.TestCase):
    def setUp(self):
        self.userid = 'testuser123'
        self.passwd = '*JE&%5e^&YU4w%ftWRtfSEfAEt%$&Ww47%6w56T#Wtq345q2'
        self.psw_packet = {'userid': self.userid, 'passwd': self.passwd, }

        self.stored_hashes = {
                'kbs': b'\xdb6\xe2\xd2ev\xcc\xc8\xe3b9\xe8\xb7g\xa0\xde',
                }

    def test_kbs_hash(self):
        self.assertEqual(
                passwd.kbs_encode(self.psw_packet),
                {'p': self.stored_hashes['kbs'], },
                )

    def test_hash_decode_stub(self):
        self.assertRaises(
                TypeError,
                passwd.hash_decode_stub,
                {'_V': 1, 'p': self.stored_hashes['kbs'], },
                )

    def test_chkpasswd(self):
        self.assertTrue(
                passwd._do_chkpasswd(
                    self.userid,
                    self.passwd,
                    {'_V': 1, 'p': self.stored_hashes['kbs'], },
                    )
                )


class TestAuthUser(unittest.TestCase):
    def setUp(self):
        self.test_uid = 'testuser'
        self.test_email = 'test@example.com'
        self.test_pswd = {'_V': 1, 'p': 'non-sense-things', }
        self.test_roles = ['role1', 'role2', ]

        self.user_objs = {
                1: {
                    '_V': 1,
                    'u': self.test_uid,
                    'e': self.test_email,
                    'p': self.test_pswd,
                    'r': self.test_roles,
                    },
                }

        self.ref_user = user.User(
                uid=self.test_uid,
                email=self.test_email,
                passwd=self.test_pswd,
                roles=self.test_roles,
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


for testcase in [TestAuthPasswd, TestAuthUser, ]:
    suite = unittest.TestLoader().loadTestsFromTestCase(testcase)
    unittest.TextTestRunner(verbosity=2).run(suite)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
