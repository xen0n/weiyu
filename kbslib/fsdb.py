#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# weiyu / kbslib / filesystem database interop
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

from os.path import join as pathjoin
from os.path import abspath  # , normpath

from ctypes import sizeof

from .llops import unpack, pythonize


BOARD_DIRNAME = 'boards'
USER_DIRNAME = 'home'
MAIL_DIRNAME = 'mail'

PARAM_BBSHOME = 'BBSHOME'


def get_prefixed_path(s):
    return pathjoin(s[0].upper(), s)


class BaseFSDB(object):
    def __init__(self, cfg):
        # cfg should be a dict-like thing holding parameters such as
        # $BBSHOME and etc
        self.cfg = cfg

    def param(self, key):
        return self.cfg[key]

    def bbshomepath(self, *args):
        return abspath(pathjoin(self.param(PARAM_BBSHOME), *args))

    def read_raw_record_iter(self, path, cstruct):
        rec_size = sizeof(cstruct)

        with open(path, 'rb') as fp:
            fp.seek(0, 2)
            file_length = fp.tell()
            if file_length % rec_size != 0:
                raise ValueError('file length not multiple of record size')
            fp.seek(0, 0)

            while True:
                record = fp.read(rec_size)

                if not record:
                    break

                yield record

    def read_record_iter(self, path, cstruct):
        for rec in self.read_raw_record_iter(path, cstruct):
            yield unpack(cstruct, rec)

    def read_into_dict(self, path, cstruct, key):
        result = {}

        # XXX id must be unique, or the earlier records WILL be overwritten
        for obj in self.read_record_iter(path, cstruct):
            pyobj = pythonize(obj)
            result[pyobj[key]] = pyobj

        return result


class ReadOnlyFSDB(BaseFSDB):
    def get_board_dir(self, boardname):
        return self.bbshomepath(
                BOARD_DIRNAME,
                boardname,
                )

    def get_user_dir(self, username):
        return self.bbshomepath(
                USER_DIRNAME,
                get_prefixed_path(username),
                )

    def get_mail_dir(self, username):
        return self.bbshomepath(
                MAIL_DIRNAME,
                get_prefixed_path(username),
                )


# main function
def main(argc, argv):
    '''simple test of exported functions'''

    bbshome, test_id, test_brd = '/srv/test-bbshome/', 'testid', 'TestBoard'
    rofsdb = ReadOnlyFSDB({PARAM_BBSHOME: bbshome})

    testcases = (
            ('User directory', rofsdb.get_user_dir, (test_id, ), {}),
            ('Board directory', rofsdb.get_board_dir, (test_brd, ), {}),
            )

    print '$BBSHOME for test: %s' % (bbshome, )
    print 'ID for test: %s' % (test_id, )
    print 'Board name for test: %s\n' % (test_brd, )

    for case_name, target_fn, args, kwargs in testcases:
        print '%s: %s' % (case_name, target_fn(*args, **kwargs), )

    return 0


if __name__ == '__main__':
    import sys

    sys.exit(main(len(sys.argv), sys.argv))


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
