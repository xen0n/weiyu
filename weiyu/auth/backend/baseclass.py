#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / auth backend / backend interface
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

from functools import wraps

CAPS_UPDATE, CAPS_ADD, CAPS_REMOVE = range(3)


def ensure_conn(fn):
    '''Check if the database connection has already been established.

    Raises ``NotConnectedError`` if a connection object is not present.

    .. warning::
        This is an internal function, not meant for outside use. **Do not**
        use it.

    '''

    @wraps(fn)
    def __wrapper__(self, *args, **kwargs):
        if self.connection is None:
            raise NotConnectedError
        # fn is a bound method, so don't pass self around
        return fn(*args, **kwargs)
    return __wrapper__


def ensure_disconn(fn):
    '''Check if the database connection has not yet been established.

    Raises ``AlreadyConnectedError`` if a connection object is present.

    .. warning::
        This is an internal function, not meant for outside use. **Do not**
        use it.

    '''

    @wraps(fn)
    def __wrapper__(self, *args, **kwargs):
        if self.connection is not None:
            raise AlreadyConnectedError
        # fn is a bound method, so don't pass self around
        return fn(*args, **kwargs)
    return __wrapper__


class AuthBackendBase(object):
    def __init__(self):
        self.connection = None


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
