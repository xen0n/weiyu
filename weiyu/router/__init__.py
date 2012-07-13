#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / router / package
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
        'router_hub',
        ]

from ..helpers.hub import BaseHub
from ..registry.classes import UnicodeRegistry


class RouterHub(BaseHub):
    registry_name = 'weiyu.router'
    registry_class = UnicodeRegistry
    handlers_key = 'handlers'

    def __init__(self):
        super(RouterHub, self).__init__()

        if 'endpoints' not in self._reg:
            self._reg['endpoints'] = {}

        if 'routers' not in self._reg:
            self._reg['routers'] = {}

        # cache the references
        self._routers = self._reg['routers']
        self._endpoints = self._reg['endpoints']

    def endpoint(self, typ, name):
        '''decorator for registering routing end points.'''

        def _decorator_(fn):
            if typ not in self._endpoints:
                # this type not already registered, probably not inited yet
                # let's give it a sensible default
                self._endpoints[typ] = {}
            self._endpoints[typ][name] = fn
            return fn
        return _decorator_

    def register_router(self, router):
        # keep a reference to the router
        typ = router.name
        if typ is None:
            raise ValueError(
                    'only named routers can be registered this way'
                    )

        self._routers[typ] = router

        # also reserve a slot in endpoints dict, if one is not already
        # set up
        if typ not in self._endpoints:
            self._endpoints[typ] = {}

        # register the router's dispatch method as handler, and we're done
        # But first construct a shim removing the hub parameter...
        @self.register_handler(typ)
        def _routing_shim_(hub, *args, **kwargs):
            return router.dispatch(*args, **kwargs)

    def dispatch(self, typ, querystr, *args):
        # typically used with args=(request, ) inside the framework
        # TODO: is it really useful to allow passing kwargs also?
        return self.do_handling(typ, querystr, *args)

    def _do_init_router(self, typ, routing_rules, cls, lvl):
        # recursive algorithm, watch out d-:
        # typ is not really useful except checking against endpoint reg
        #
        # let's construct the desired target initializer out of the
        # pattern-to-(endpoint-or-router) list
        _list_types = (list, tuple, )
        _str_types = (str, unicode, )

        result_rules = []
        for pattern, target_spec in routing_rules:
            if isinstance(target_spec, _list_types):
                # this is a router... recursively construct a router out
                # of it
                tgt = self._do_init_router(typ, target_spec, cls, lvl + 1)
            elif isinstance(target_spec, _str_types):
                # target is endpoint... check against endpoint registry
                # this is where typ is used
                # enforce a little bit of encoding requirement, to make
                # messed up encoding problem surface fast
                tgt = self._endpoints[typ][unicode(target_spec)]
            else:
                # unrecognized target specification, pass it thru as is
                tgt = target_spec

            # add a rule
            result_rules.append((pattern, tgt, ))

        # construct a XxxRouter object with the routing rules just created
        # if toplevel router, assign it a name equal to typ
        return cls(result_rules, name=typ if lvl == 0 else None)

    def init_router(self, typ, routing_rules, cls):
        return self._do_init_router(typ, routing_rules, cls, 0)


router_hub = RouterHub()


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
