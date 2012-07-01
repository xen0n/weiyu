#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# weiyu / kbslib / low-level structures operation
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

from ctypes import cast, c_char_p, sizeof, POINTER


def unpack(typ, s):
    actual_len, type_len = len(s), sizeof(typ)
    if actual_len != type_len:
        raise ValueError('size mismatch: %d bytes expected, got %d' % (
                type_len,
                actual_len,
                ))

    # XXX is the string preserved through the corresponding ctypes Structure's
    # lifespan?
    return cast(c_char_p(s[:]), POINTER(typ)).contents


def pythonize(cstruct):
    fields_iter = (field for field, typ in cstruct._fields_)
    return dict(
            (k, getattr(cstruct, k), )
            for k in fields_iter
            )


# main function
def main(argc, argv):
    return 0


if __name__ == '__main__':
    sys.exit(main(len(sys.argv), sys.argv))


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
