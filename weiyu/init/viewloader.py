#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / framework-level initialization / view loader
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
        'ViewLoader',
        ]

import importlib
import json


class ViewLoader(object):
    def __init__(self, config=None):
        self.config = config or {}

    def fileconfig(self, path):
        with open(path, 'rb') as fp:
            content = fp.read()
        self.config = json.loads(content)

        return self

    def __call__(self):
        cfg = self.config
        pkg_anchor = cfg.get('package', None)
        modules = cfg.get('modules', [])

        for name in modules:
            importlib.import_module(name, pkg_anchor)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
