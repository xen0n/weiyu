#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / helpers / module importer
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
        'ModProber',
        ]

import importlib


class ModProber(object):
    def __init__(self, package, name_template, package_map=None):
        self.package = package
        self.name_template = name_template
        self.package_map = package_map or {}

        # Python 3.x needs the parent package to be imported before any
        # relative import can happen, so we mark that case here.
        self._package_imported = False

    def _ensure_parent_package(self):
        if not self._package_imported and self.package is not None:
            # obvious race condition... but does it really matter?
            # worst case is just a repeated import which should really do
            # no harm if the package does not have import-time side effects,
            # which should be the case on any sane codebase.
            importlib.import_module(self.package)
            self._package_imported = True

    def get_relative_path(self, name):
        assert '.' not in name
        return '.' + self.name_template % (self.package_map.get(name, name), )

    def modprobe(self, name):
        self._ensure_parent_package()

        return importlib.import_module(
                self.get_relative_path(name),
                self.package,
                )


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
