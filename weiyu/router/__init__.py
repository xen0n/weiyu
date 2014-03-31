#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / router / package
#
# Copyright (C) 2012-2014 Wang Xuerui <idontknw.wang-at-gmail-dot-com>
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

import os
import errno

import six

from ..helpers.hub import BaseHub
from ..helpers.modprober import ModProber
from ..registry.classes import UnicodeRegistry

# this does not cause circular import
from .config.parser import parse_config

from .reverser import reverser_for_router

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

    def reverser_for(self, router_name):
        return reverser_for_router(self._routers[router_name])

    def _probe_router_class(self, cls_name):
        try:
            return self._classes[cls_name]
        except KeyError:
            pass

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
        return self._classes[cls_name]

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
        this_file, inherited_klass, inherited_renderer, scope, host = (
                parent_info['__file__'],
                parent_info['inherited_klass'],
                parent_info['inherited_renderer'],
                parent_info['scope'],
                parent_info['host'],
                )
        include_path, cls_name = None, None

        if not isinstance(attrib_list, _list_types):
            # Always use a list for attributes.
            attrib_list = [attrib_list]

        for attrib in attrib_list:
            # Router class spec.
            if '=' not in attrib:
                # The class spec attrib does not contain '='.
                # This flaky way of determining class spec can be used
                # at least for now, as no other parameter-less attributes
                # exist so far.
                cls_name = attrib
                continue

            # Router properties.
            k, v = attrib.split('=', 1)

            if k == 'renderer':
                # case: renderer=xxx
                # record the renderer to inherit
                inherited_renderer = v
            elif k == 'include':
                # case: include=xxx
                # it must appear as the only attribute, if used!
                if len(attrib_list) > 1:
                    # throw an exception.
                    raise RuntimeError(
                            'include directive must appear on its own'
                            )
                include_path = v
            elif k == 'scope':
                # case: scope=xxx
                scope = v
            elif k == 'default-type':
                # case: default-type=xxx
                inherited_klass = v
            elif k == 'host':
                # case: host=xxx
                host = v
            else:
                # Unknown attribute, ignore it for compatibility with future
                # versions.
                # TODO: log warnings
                continue

        # Process include.
        if include_path is not None:
            # There must be no other routing rules described... or we would
            # not know what to include.
            if len(routing_rules) > 1:
                raise RuntimeError(
                        'included router description should not contain '
                        'any rules'
                        )

            # Resolve include path.
            if this_file is not None:
                # Resolve relative to the current file.
                this_dir = os.path.dirname(this_file)
            else:
                # Current file path is unavailable, resolve relative to the
                # current working directory (old behavior).
                this_dir = os.getcwdu()

            include_path_resolved = os.path.abspath(
                    os.path.join(
                        this_dir,
                        include_path,
                        ))

            # Allow for extension (.URLfile) omission.
            #
            # Since it is not the default any more, .txt is not considered
            # here. The worst thing can happen is a failed open() call, so
            # no worries.
            #
            # I decided to not allow funky things like including something
            # like 'foo.URLfile.URLfile'...
            if not include_path_resolved.endswith('.URLfile'):
                # Likely the filename extension is omitted, add it back.
                suffixed_path = include_path_resolved + '.URLfile'

                # Try the suffixed version first...
                try:
                    return self.init_router_from_config(typ, suffixed_path)
                except IOError as e:
                    # Only ignore ENOENT here.
                    if e.errno != errno.ENOENT:
                        raise

            return self.init_router_from_config(typ, include_path_resolved)

        # Load the requested (built-in) router class.
        #
        # Custom router classes should be registered before config load, like
        # before.
        #
        # TODO: allow registration of custom modules in modprober mechanism

        # Override with inherited class name if not specified already.
        # This works even inside the same router node.
        cls_name = cls_name if cls_name is not None else inherited_klass
        cls = self._probe_router_class(cls_name)

        # Process rules.
        result_rules = []
        for pattern, target_spec, extra_data in routing_rules[1:]:
            if isinstance(target_spec, _list_types):
                # this is a router... recursively construct a router out
                # of it
                my_info = {
                        '__file__': this_file,
                        'inherited_klass': inherited_klass,
                        'inherited_renderer': inherited_renderer,
                        'scope': scope,
                        'host': host,
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
                host=host,
                )

    def init_router(self, typ, routing_rules, filename=None):
        return self._do_init_router(
                typ,
                routing_rules,
                0,
                {
                    '__file__': filename,
                    'inherited_klass': None,
                    'inherited_renderer': None,
                    'scope': '',
                    'host': None,
                    },
                )

    def init_router_from_config(self, typ, filename):
        config = parse_config(filename)
        return self.init_router(typ, config, filename)


router_hub = RouterHub()


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
