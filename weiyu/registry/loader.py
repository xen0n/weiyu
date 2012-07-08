#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / central registry / config loader
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
Configuration loader
~~~~~~~~~~~~~~~~~~~~



'''

from __future__ import unicode_literals, division

from os.path import abspath
import abc
import json

from .provider import request, _registries


class BaseConfig(object):
    '''Base class for prepopulated config storages.
    '''

    __metaclass__ = abc.ABCMeta

    def __init__(self, path=None):
        self.path, self.data = path, None

    @abc.abstractmethod
    def _do_loads(self, s, *args, **kwargs):
        pass

    def loads(self, s, *args, **kwargs):
        raw_data = self._do_loads(s, *args, **kwargs)
        self.data = self.process_directives(raw_data)
        return self.data

    def load(self, fp=None, *args, **kwargs):
        # XXX this function's a naive wrapper to get rid of some duplication

        if fp is None:
            # invoke ``self.load_from_path`` to read the file specified
            # by ``self.path``
            return self.load_from_path(None)

        return self.loads(fp.read(), *args, **kwargs)

    def load_from_path(self, path=None):
        if path is None:
            if self.path is None:
                raise ValueError('no usable path configured')
            path = self.path

        return self._do_load_from_path(path)

    def _do_load_from_path(self, path):
        with open(path, 'rb') as fp:
            return self.load(fp)

    def do_include(self, includes):
        tmp = {}
        for path in includes:
            # XXX FIXME: Infinite includes is possible!!
            # NOTE Security is important here, so paths should be
            # at least canonicalized.
            real_path = abspath(path)
            tmp.update(self.load_from_path(real_path))
        return tmp

    def process_directives(self, data):
        # process '$$include': [inc1, inc2, etc, ]
        if '$$include' in data:
            include_list = data.pop('$$include')
            data.update(self.do_include(include_list))

        return data

    def populate_registry(self, registry):
        if self.data is None:
            self.load_from_path(None)

        for k, v in self.data.iteritems():
            registry.register(k, v)

    def populate_registries(self, _registries):
        # TODO
        pass


class JSONConfig(BaseConfig):
    '''JSON config backend.'''

    def _do_loads(self, s, *args, **kwargs):
        dump = json.loads(s, *args, **kwargs)
        # TODO: some canonicalization or such
        return dump


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
