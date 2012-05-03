#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / hooking mechanism / central registry interaction
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

u'''
Hook information registry
~~~~~~~~~~~~~~~~~~~~~~~~~


'''

from __future__ import unicode_literals, division

from weiyu.registry.classes import FunctionKeyRegistry, FunctionlikeTypes


class HookRegistry(UnicodeRegistry):
    '''Registry for registering registries.

    In order to ensure true singleton pattern, all registries should be
    acquired from the central registry. Which explains why this very class
    exists...

    '''

    def normalize_value(self, value):
        if not issubclass(type(value), RegistryBase):
            raise ValueError("'%s': not a registry" % (repr(value), ))

        return value


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
