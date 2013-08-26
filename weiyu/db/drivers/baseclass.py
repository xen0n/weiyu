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

import six


class BaseDriver(six.with_metaclass(abc.ABCMeta)):
    '''Baseclass for database drivers.'''

    @abc.abstractmethod
    def start(self):
        '''Prepare for database operations.'''

        pass

    @abc.abstractmethod
    def finish(self):
        '''Be done with the database.

        The connection may be returned to some kind of pools, or closed.

        '''

        pass

    def __call__(self, bucket):
        '''Get a database connection for the selected bucket of data.

        This connection is driver-specific, for the developers to fully
        leverage the details of underlying database infrastructure.

        '''

        return DBOperationContext(self, bucket)

    @abc.abstractmethod
    def get_bucket(self, bucket):
        '''Get a driver-specific bucket/collection/table object to operate
        on.

        '''

        pass


class DBOperationContext(object):
    def __init__(self, driver, bucket):
        self.driver, self.bucket = driver, bucket

    def __enter__(self):
        self.driver.start()
        return self.driver.get_bucket(self.bucket)

    def __exit__(self, exc_type, exc_value, traceback):
        self.driver.finish()

    def __repr__(self):
        return b'<DBOperationContext: driver=%s, bucket=%s>' % (
                repr(self.driver),
                self.bucket,
                )


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
