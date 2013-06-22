#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / db drivers / base class
#
# Copyright (C) 2012-2013 Wang Xuerui <idontknw.wang-at-gmail-dot-com>
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

import abc


class BaseDriver(object):
    '''Baseclass for database drivers.'''

    __metaclass__ = abc.ABCMeta

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.finish()
        pass

    @abc.abstractmethod
    def connect(self):
        '''Establish a database connection.'''
        pass

    @abc.abstractmethod
    def finish(self):
        '''Be done with the connection.

        The connection may be returned to some kind of pools, or closed.

        '''

        pass

    @abc.abstractmethod
    def insert(self, bucket, v, k=None):
        '''Insert an entity.

        For backends that auto-generates a key for the entity, ``k`` may be
        ``None``.

        '''

        pass

    @abc.abstractmethod
    def find(self, bucket, criteria):
        '''Query entities in the designated bucket.'''

        pass

    @abc.abstractmethod
    def update(self, bucket, v, k):
        '''Update an entity with the new value.'''

        pass

    @abc.abstractmethod
    def remove(self, bucket, k):
        '''Remove an entity from bucket.'''

        pass


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
