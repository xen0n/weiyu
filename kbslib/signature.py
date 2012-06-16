#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# weiyu / kbslib / signature file parser
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
    from .sitecfg import KBS_ENCODING, SIGN_LINES
else:
    from sitecfg import KBS_ENCODING, SIGN_LINES


def assemble_signature(tmplist):
    return '\n'.join(tmplist)


def extract_signatures(stream):
    # XXX naive approach...
    content = stream.read().rstrip(b'\n')
    lines = content.decode(KBS_ENCODING, 'ignore').split('\n')

    result, tmp = [], []
    for line in lines:
        tmp.append(line)

        if len(tmp) == SIGN_LINES:
            sign = assemble_signature(tmp)
            result.append(sign)
            tmp = []

    if tmp:
        result.append(assemble_signature(tmp))

    return result


def read_signatures_from_file(filename):
    # text mode, yes... hopefully no \r\n's will escape thru
    with open(filename, 'r') as fp:
        return extract_signatures(fp)


# main function
def main(argc, argv):
    if argc < 2:
        print >>sys.stderr, u'usage: %s <signatures files>' % argv[0]
        return 1

    filenames = argv[1:]
    for fname in filenames:
        signatures = read_signatures_from_file(fname)
        print '%s: %d signature(s)' % (fname, len(signatures), )
        print '\n-=-=-=-=-=-=-=-=-=-=-\n'.join(signatures)
        print '-=-=-=-=-=-=-=-=-=-=-\n'

    return 0


if __name__ == '__main__':
    sys.exit(main(len(sys.argv), sys.argv))


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
