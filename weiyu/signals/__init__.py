#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / signals / package
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

__all__ = [
        'signal_hub',
        ]

from ..helpers.hub import BaseHub
from ..registry.classes import UnicodeRegistry

LISTENERS_KEY = 'listeners'


class SignalHub(BaseHub):
    registry_name = 'weiyu.signal'
    registry_class = UnicodeRegistry
    handlers_key = 'handlers'  # XXX Not used!

    def __init__(self):
        super(SignalHub, self).__init__()

        if LISTENERS_KEY not in self._reg:
            self._reg[LISTENERS_KEY] = {}

        self._listeners = self._reg[LISTENERS_KEY]

    def append_listener_to(self, name):
        def _decorator_(thing):
            if name in self._listeners:
                self._listeners[name].append(thing)
            else:
                self._listeners[name] = [thing, ]

            return thing
        return _decorator_

    def prepend_listener_to(self, name):
        def _decorator_(thing):
            if name in self._listeners:
                self._listeners[name].insert(0, thing)
            else:
                self._listeners[name] = [thing, ]

            return thing
        return _decorator_

    def fire(self, name, *args, **kwargs):
        try:
            callbacks = self._listeners[name]
        except KeyError:
            raise KeyError(
                    "signal '%s' not claimed by any listener" % (
                        name,
                        ))

        for fn in callbacks:
            fn(*args, **kwargs)

    def fire_nullok(self, name, *args, **kwargs):
        if name not in self._listeners:
            return
        return self.fire(name, *args, **kwargs)


signal_hub = SignalHub()


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
