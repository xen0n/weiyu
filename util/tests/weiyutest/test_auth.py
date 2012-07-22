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


suite = unittest.TestLoader().loadTestsFromTestCase(TestAuthPasswd)
unittest.TextTestRunner(verbosity=2).run(suite)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
