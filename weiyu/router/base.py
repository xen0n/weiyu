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
            'STATUS_REACHED',
            'STATUS_FORWARD',
            'STATUS_NOROUTE',
            ]

STATUS_REACHED, STATUS_FORWARD, STATUS_NOROUTE = range(3)


class DispatchError(Exception):
    pass


# XXX Make up clearer names for all those "target"s!

class RouterBase(object):
    def __init__(self, target_initializers, name=None):
        self.name = name
        self.route_table = [
                self.__class__.target_type(*i)
                for i in target_initializers
                ]

    def lookup(self, querystr, prev_args=None, prev_kwargs=None):
        # XXX is this needed, or am I overly sensitive?
        querystr = unicode(querystr)

        if prev_args is None:
            prev_args = []

        if prev_kwargs is None:
            prev_kwargs = {}

        # sequentially check our "route table"
        for entry in self.route_table:
            # return is of form ``(hit, target, args, kwargs, )``
            result = entry.lookup(
                    querystr,
                    prev_args,
                    prev_kwargs,
                    )

            if result[0]:
                # successful match
                return result

        # match failure
        return (False, None, None, None, None, )

    def dry_dispatch(self, querystr, *args):
        '''Do all things except actually invoking callback function,
        returns the calculated parameters that can be used to do a real
        dispatch.

        '''

        hit, target, more_args, kwargs, data = self.lookup(querystr)

        if not hit:
            raise DispatchError("query string %s: nowhere to dispatch"
                                % repr(querystr)
                                )

        # append resolved positional args to args passed in
        extended_args = list(args)
        extended_args.extend(more_args)

        return target, extended_args, kwargs, data

    def dispatch(self, querystr, *args):
        target, ext_args, kwargs, data = self.dry_dispatch(querystr, *args)
        return target(*ext_args, **kwargs)


class RouterTargetBase(object):
    def __init__(self, target, extra_data=None):
        self.target, self.data = target, extra_data

        # for nested processing
        self.target_is_router = issubclass(type(target), RouterBase)

    def check(self, querystr):
        # return is assumed to be in the form of
        # (hit_status, args, kwargs, new_qs, )
        # since it is unnecessary and redundant to return self.target
        # to an internal method
        raise NotImplementedError

    def lookup(self, querystr, prev_args, prev_kwargs):
        # return value is of form (hit, target, args, kwargs, )
        # result is of form (status, args, kwargs, new_querystr, )
        status, args, kwargs, new_qs = self.check(
                querystr,
                prev_args,
                prev_kwargs,
                )

        if status == STATUS_REACHED:
            # reached end, make args a tuple
            # XXX Is this necessary?
            return (True, self.target, tuple(args), kwargs, self.data, )
        elif status == STATUS_NOROUTE:
            return (False, None, None, None, None, )
        elif status == STATUS_FORWARD:
            # do nested routing
            return self.target.lookup(new_qs, args, kwargs)

        # unreachable if check function behaves properly
        raise DispatchError('Impossible check result %s, bug detected'
                % repr((status, args, kwargs, new_qs, ))
                )


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
