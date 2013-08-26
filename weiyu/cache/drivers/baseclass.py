#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / cache drivers / base class
#
# Copyright (C) 2013 Wang Xuerui <idontknw.wang-at-gmail-dot-com>
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


class BaseCache(six.with_metaclass(abc.ABCMeta)):
    def __init__(self):
        super(BaseCache, self).__init__()

    @abc.abstractmethod
    def get(self, k):
        return None

    @abc.abstractmethod
    def set(self, k, v, timeout=None):
        return True

    @abc.abstractmethod
    def delete(self, k):
        return True

    def __getitem__(self, k):
        return self.get(k)

    def __setitem__(self, k, v):
        return self.set(k, v)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
