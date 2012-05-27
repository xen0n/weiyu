#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# weiyu / utilities / KBS low-level structures description
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
from collections import namedtuple


# Site constants
FILENAME_LEN, OWNER_LEN, ARTICLE_TITLE_LEN = 20, 14, 60

# Structure layouts
fileheader_fmt = b'@%(fnlen)dsIIIiIII2s%(ownerlen)dsIiI%(titlelen)ds4B' % {
        b'fnlen': FILENAME_LEN,
        b'ownerlen': OWNER_LEN,
        b'titlelen': ARTICLE_TITLE_LEN,
        }

fileheader_t = struct.Struct(fileheader_fmt)
fileheader_record = namedtuple(
        b'fileheader',
        (
            b'filename id groupid reid'
            b' o_bid o_id o_groupid o_reid'
            b' innflag owner eff_size'
            b' posttime attachment title'
            b' accessed1 accessed2 accessed3 accessed4'
            ),
        )


# main function
def main(argc, argv):
    return 0


if __name__ == '__main__':
    sys.exit(main(len(sys.argv), sys.argv))


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
