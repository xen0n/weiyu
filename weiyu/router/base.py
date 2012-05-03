#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / router / base functionality
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

__all__ = [
            'RouterTargetBase',
            'RouterBase',
            ]


class DispatchError(Exception):
    pass


class RouterTargetBase(object):
    def __init__(self, name, target):
        self.name = name
        self.target = target

    def check(self, querystr):
        raise NotImplementedError


class RouterBase(object):
    def __init__(self, name, target_initializers):
        self.name = name
        self.targets = [self.__class__.target(*i)
                        for i in target_initializers
                        ]

    def check(self, querystr):
        # XXX is this needed, or am I overly sensitive?
        querystr = unicode(querystr)

        for target in self.targets:
            hit, args, kwargs = target.check(querystr)

            if hit:
                return (True, target, args, kwargs, )

        return (False, None, None, None, )

    def dispatch(self, querystr):
        hit, target, args, kwargs = self.check(querystr)

        if not hit:
            raise DispatchError("query string %s: nowhere to dispatch"
                                % repr(querystr)
                                )

        return target.target(*args, **kwargs)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
