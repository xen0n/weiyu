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

from collections import OrderedDict

import six

from ..helpers.misc import smartstr

STATUS_REACHED, STATUS_FORWARD, STATUS_NOROUTE = range(3)


def is_router(tgt):
    return isinstance(tgt, (RouterBase, ))


class DispatchError(Exception):
    pass


# XXX Make up clearer names for all those "target"s!

class RouterBase(object):
    def __init__(
            self,
            target_initializers,
            name=None,
            parent=None,
            scope='',
            ):
        self.name, self.scope, self.parent = name, scope, parent
        self.route_table = [
                self.__class__.target_type(router=self, *i)
                for i in target_initializers
                ]

        # Fix sub-routers' parents.
        for tgt in self.route_table:
            if tgt.target_is_router:
                tgt.target.parent = tgt

    def lookup(self, querystr, prev_args=None, prev_kwargs=None):
        # XXX is this needed, or am I overly sensitive?
        querystr = smartstr(querystr)

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
            raise DispatchError(
                    "query string %s: nowhere to dispatch" % (
                        repr(querystr),
                        ))

        # append resolved positional args to args passed in
        extended_args = list(args)
        extended_args.extend(more_args)

        return target, extended_args, kwargs, data

    def dispatch(self, querystr, *args):
        target, ext_args, kwargs, data = self.dry_dispatch(querystr, *args)
        return target(*ext_args, **kwargs)

    def build_reverse_map(self):
        scope = self.scope
        map_ = {scope: {}}  # OrderedDict()
        this_scope = map_[scope]

        # According to the ctor, route_table is guaranteed to be a list,
        # so reversing using slicing syntax is fine.
        for entry in self.route_table[::-1]:
            if entry.target_is_router:
                chld_map = entry.target.reverse_map
                for chld_scope, chld_scopemap in six.iteritems(chld_map):
                    if chld_scope in map_:
                        map_[chld_scope].update(chld_scopemap)
                    else:
                        map_[chld_scope] = chld_scopemap
            else:
                tgt_spec = entry.data.get('target_spec', None)
                this_scope[tgt_spec] = entry.reverse_pattern

        return map_

    @property
    def reverse_map(self):
        try:
            return self._reverse_map
        except AttributeError:
            map_ = self._reverse_map = self.build_reverse_map()
            return map_


class RouterTargetBase(object):
    def __init__(self, target, extra_data=None, router=None):
        self.target, self.data, self.router = target, extra_data, router

        # for nested processing
        self.target_is_router = is_router(target)

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

    @property
    def reverse_pattern(self):
        try:
            return self._reverse_pattern
        except AttributeError:
            pat = self._get_reverse_pattern()
            if self.router.parent is not None:
                parent_pat = self.router.parent.reverse_pattern
            else:
                # no parent target, use an empty one
                parent_pat = ('', set(), )

            # merge the parent's reverse pattern
            pat_str = parent_pat[0] + pat[0]
            pat_vars = set(parent_pat[1])
            pat_vars.update(pat[1])
            self._reverse_pattern = (pat_str, pat_vars, )
            return self._reverse_pattern

    def _get_reverse_pattern(self):
        return


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
