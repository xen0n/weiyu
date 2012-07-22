#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / test suite / test environment initializer
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
import os.path


def get_weiyu_path():
    mypath = os.path.dirname(__file__)
    pkgpath = os.path.realpath(os.path.join(mypath, '../../..'))
    return pkgpath


def init_sys_path():
    sys.path.insert(0, get_weiyu_path())


init_sys_path()


# this must be successful
import weiyu


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
