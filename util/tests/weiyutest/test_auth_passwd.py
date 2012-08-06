#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / test suite / weiyu.auth.passwd
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
from .common_auth import AuthTestConfig as cfg


class TestAuthPasswd(unittest.TestCase):
    def test_kbs_hash(self):
        self.assertEqual(
                passwd.kbs_encode(cfg.psw_packet),
                {'p': cfg.stored_hashes['kbs'], },
                )

    def test_hash_decode_stub(self):
        self.assertRaises(
                TypeError,
                passwd.hash_decode_stub,
                cfg.psw_objs[1],
                )

    def test_chkpasswd(self):
        self.assertTrue(
                passwd._do_chkpasswd(
                    cfg.userid,
                    cfg.passwd,
                    cfg.psw_objs[1],
                    )
                )


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
