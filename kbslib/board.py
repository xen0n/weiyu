#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# weiyu / kbslib / board directory operations
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

import sys

if __name__ != '__main__':
    # XXX try to reduce this duplication!
    from .sitecfg import KBS_ENCODING
    from .llops import unpack, pythonize
    from .llstruct import fileheader
else:
    from sitecfg import KBS_ENCODING
    from llops import unpack, pythonize
    from llstruct import fileheader


class Board(object):
    # TODO: boardheader, fileheader, integration w/ kbslib.post...
    pass


# main function
def main(argc, argv):
    if argc < 3:
        print >>sys.stderr, u'usage: %s <BBSHOME> <board name(s)>' % argv[0]
        return 1

    # TODO

    return 0


if __name__ == '__main__':
    sys.exit(main(len(sys.argv), sys.argv))


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
