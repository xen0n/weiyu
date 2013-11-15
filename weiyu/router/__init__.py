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

import six

from ..helpers.hub import BaseHub
from ..helpers.modprober import ModProber
from ..registry.classes import UnicodeRegistry

# this does not cause circular import
from .config.parser import parse_config

PROBER = ModProber('weiyu.router', '%srouter')


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

        if 'classes' not in self._reg:
            self._reg['classes'] = {}

        # cache the references
        self._routers = self._reg['routers']
        self._endpoints = self._reg['endpoints']
        self._classes = self._reg['classes']

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

    def register_router_class(self, name):
        '''Decorator to make a class available for routing.

        This decorator is mainly intended for internal use, to give short
        names to the router classes.

        '''

        def _decorator_(cls):
            if name in self._classes:
                raise ValueError(
                        'duplicate router register name: \'%s\'' % (name, )
                        )

            self._classes[name] = cls
            return cls
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
        # here we'd use dry dispatch instead...
        # But first construct a shim removing the hub parameter...
        @self.register_handler(typ)
        def _routing_shim_(hub, *args, **kwargs):
            return router.dry_dispatch(*args, **kwargs)

    def dry_dispatch(self, typ, querystr, *args):
        # typically used with args=(request, ) inside the framework
        # TODO: is it really useful to allow passing kwargs also?
        return self.do_handling(typ, querystr, *args)

    def reverser_for(self, typ, __cache={}):
        try:
            return __cache[typ]
        except KeyError:
            pass

        router = self._routers[typ]
        map = router.reverse_map
        pat_cache = {}

        def reverser(endpoint, **kwargs):
            # look up the endpoint, memoized.
            try:
                pat_str, pat_vars = pat_cache[endpoint]
            except KeyError:
                # split the possibly scoped endpoint name into components
                try:
                    colon = endpoint.index(':')
                    scope, name = endpoint[:colon], endpoint[colon + 1:]
                except ValueError:
                    scope, name = '', endpoint

                # look up the scope first
                try:
                    scope_map = map[scope]
                except KeyError:
                    # TODO: a NoReverseMatch here, as Django did?
                    raise ValueError(
                            "No scope named '%s' in router type '%s'" % (
                                scope,
                                typ,
                                ))

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
                pat_cache[endpoint] = (pat_str, pat_vars, )

            # verify the parameters
            given_vars = set(six.iterkeys(kwargs))
            if given_vars != pat_vars:
                # parameter mismatch
                raise ValueError('Parameter mismatch')

            # successful match, construct the result
            return pat_str % kwargs

        # memoize the reverser instance
        __cache[typ] = reverser

        return reverser

    def _do_init_router(
            self,
            typ,
            routing_rules,
            lvl,
            parent_info,
            _list_types=(list, tuple, ),
            ):
        # recursive algorithm, watch out d-:
        # typ is not really useful except checking against endpoint reg
        #
        # let's construct the desired target initializer out of the
        # pattern-to-(endpoint-or-router) list
        #
        # Attribute processing.
        attrib_list = routing_rules[0]
        inherited_renderer, scope = (
                parent_info['inherited_renderer'],
                parent_info['scope'],
                )
        include_path, cls_name = None, None

        if isinstance(attrib_list, _list_types):
            # Multiple attributes.
            # separate the router class from the others
            # the class spec is hardcoded to be the 1st attrib in the list
            cls_name = attrib_list[0]

            # Process the other attributes.
            for attrib in attrib_list[1:]:
                k, v = attrib.split('=', 1)

                if k == 'renderer':
                    # case: renderer=xxx
                    # record the renderer to inherit
                    inherited_renderer = v
                elif k == 'include':
                    # case: include=xxx
                    # it must appear as the only attribute, if used!
                    # throw an exception.
                    raise RuntimeError(
                            'include directive must appear on its own'
                            )
                elif k == 'scope':
                    # case: scope=xxx
                    scope = v
        else:
            # only one attribute.
            # it is either the router class spec, or an include directive
            if attrib_list.startswith('include='):
                k, v = attrib_list.split('=', 1)
                include_path = v
            else:
                cls_name = attrib_list

        # Process include.
        if include_path is not None:
            # There must be no other routing rules described... or we would
            # not know what to include.
            if len(routing_rules) > 1:
                raise RuntimeError(
                        'included router description should not contain '
                        'any rules'
                        )

            # The included file is then treated as a normal routing
            # description.
            return self.init_router_from_config(typ, include_path)

        # Load the requested (built-in) router class.
        #
        # Custom router classes should be registered before config load, like
        # before.
        #
        # TODO: allow registration of custom modules in modprober mechanism
        try:
            cls = self._classes[cls_name]
        except KeyError:
            try:
                PROBER.modprobe(cls_name)
            except ImportError:
                raise RuntimeError(
                        'request of unknown router class \'%s\'' % (
                            cls_name,
                            ),
                        )

            # Assume that module has actually registered the wanted class...
            assert cls_name in self._classes
            cls = self._classes[cls_name]

        # Process rules.
        result_rules = []
        for pattern, target_spec, extra_data in routing_rules[1:]:
            if isinstance(target_spec, _list_types):
                # this is a router... recursively construct a router out
                # of it
                my_info = {
                        'inherited_renderer': inherited_renderer,
                        'scope': scope,
                        }
                tgt = self._do_init_router(typ, target_spec, lvl + 1, my_info)
            elif isinstance(target_spec, six.string_types):
                # target is endpoint... check against endpoint registry
                # this is where typ is used
                # enforce a little bit of encoding requirement, to make
                # messed up encoding problem surface fast
                tgt = self._endpoints[typ][six.text_type(target_spec)]
            else:
                # unrecognized target specification, pass it thru as is
                tgt = target_spec

            # process special data
            if extra_data is not None:
                # render_in
                if extra_data.get('render_in', None) == 'inherit':
                    # inherit renderer from parent
                    extra_data['render_in'] = inherited_renderer
            else:
                extra_data = {}

            # remember the target spec for the URL reverser
            extra_data['target_spec'] = target_spec

            # add a rule
            result_rules.append((pattern, tgt, extra_data, ))

        # construct a XxxRouter object with the routing rules just created
        # if toplevel router, assign it a name equal to typ
        return cls(
                result_rules,
                name=typ if lvl == 0 else None,
                scope=scope,
                )

    def init_router(self, typ, routing_rules):
        return self._do_init_router(
                typ,
                routing_rules,
                0,
                {
                    'inherited_renderer': None,
                    'scope': '',
                    },
                )

    def init_router_from_config(self, typ, filename):
        config = parse_config(filename)
        return self.init_router(typ, config)


router_hub = RouterHub()


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
