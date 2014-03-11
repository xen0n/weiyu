#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / router / reverser
#
# Copyright (C) 2013-2014 Wang Xuerui <idontknw.wang-at-gmail-dot-com>
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
        'reverser_for_router',
        'Reverser',
        ]

import six

_REVERSER_CACHE = {}


def reverser_for_router(router):
    key = router.name
    if key is None:
        raise ValueError('only named routers can have reverser at present')

    try:
        return _REVERSER_CACHE[key]
    except KeyError:
        reverser = Reverser(router)
        _REVERSER_CACHE[key] = reverser
        return reverser


class Reverser(object):
    def __init__(self, router):
        self.router = router
        self.map = router.reverse_map
        self.pat_cache = {}

    def _resolve_scope(self, endpoint, __cache={}):
        # split the possibly scoped endpoint name into components
        try:
            # scope, name
            return __cache[endpoint]
        except KeyError:
            pass

        try:
            colon = endpoint.index(':')
            scope, name = endpoint[:colon], endpoint[colon + 1:]
        except ValueError:
            scope, name = '', endpoint

        # memoize
        result = __cache[endpoint] = (scope, name, )
        return result

    def signature(self, endpoint):
        # look up the endpoint, memoized.
        try:
            # pat_str, pat_vars
            return self.pat_cache[endpoint]
        except KeyError:
            pass

        scope, name = self._resolve_scope(endpoint)

        # look up the scope first
        try:
            scope_map = self.map[scope]
        except KeyError:
            # TODO: a NoReverseMatch here, as Django did?
            raise ValueError(
                    "No scope named '%s' in router type '%s'" % (
                        scope,
                        typ,
                        ))

        # get out the pattern signature
        try:
            pat_str, pat_vars = scope_map[name]
        except KeyError:
            raise ValueError(
                    "No endpoint '%s' exposed in scope '%s' of "
                    "router type '%s'" % (
                        name,
                        scope,
                        typ,
                        ))

        # memoize the result
        result = self.pat_cache[endpoint] = (pat_str, pat_vars, )
        return result

    def reverse(self, endpoint, **kwargs):
        pat_str, pat_vars = self.signature(endpoint)

        # verify the parameters
        given_vars = set(six.iterkeys(kwargs))
        if given_vars != pat_vars:
            # parameter mismatch
            raise ValueError('Parameter mismatch')

        # successful match, construct the result
        return pat_str % kwargs


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
