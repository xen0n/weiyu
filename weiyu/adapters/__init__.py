#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / adapter / package
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

__all__ = [
        'adapter_hub',
        ]

from ..helpers.hub import BaseHub
from ..helpers.modprober import ModProber
from ..registry.classes import UnicodeRegistry
from ..signals import signal_hub

ADAPTERS_KEY = 'adapters'
KNOWN_MIDDLEWARE_KEY = 'known_middlewares'
USED_MIDDLEWARE_KEY = 'used_middlewares'

PROBER = ModProber(
        'weiyu.adapters',
        '%s',
        {
            'wsgi': 'http.wsgi',
            'tornado': 'http.tornado_',
            },
        )


class AdapterHub(BaseHub):
    registry_name = 'weiyu.adapter'
    registry_class = UnicodeRegistry
    handlers_key = ADAPTERS_KEY

    def __init__(self):
        super(AdapterHub, self).__init__()
        self._middlewares = self._reg[KNOWN_MIDDLEWARE_KEY] = {}
        self._middleware_in_use = self._reg[USED_MIDDLEWARE_KEY] = {}

    def make_app(self, adapter):
        PROBER.modprobe(adapter)
        return self.do_handling(adapter)

    def declare_middleware(self, name):
        def _decorator_(obj):
            if name in self._middlewares:
                raise ValueError(
                        "middleware '%s' already declared" % (
                            name,
                            )
                        )

            self._middlewares[name] = obj
            return obj
        return _decorator_

    def register_middleware_chain(self, router_type, chain, middleware_names):
        signal_name = '%s-middleware-%s' % (router_type, chain, )

        for name in middleware_names:
            # Instantiate each middleware object only once
            try:
                middleware = self._middleware_in_use[name]
            except KeyError:
                middleware_cls = self._middlewares[name]
                middleware = self._middleware_in_use[name] = middleware_cls()

            method = getattr(middleware, 'do_%s' % (chain, ))
            signal_hub.append_listener_to(signal_name)(method)


adapter_hub = AdapterHub()


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
