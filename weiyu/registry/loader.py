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
from functools import wraps
import abc
import json

from .classes import VALID_REGISTRY_TYPES
from .provider import request


def ensure_data_presence(fn):
    @wraps(fn)
    def _wrapped_(self, *args, **kwargs):
        if self.data is None:
            self.load_from_path(None)
        return fn(*args, **kwargs)

    return _wrapped_


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

    @ensure_data_presence
    def populate_registry(self, registry):
        for k, v in self.data.iteritems():
            registry.register(k, v)

    @ensure_data_presence
    def populate_registries(self, _registries):
        for k, v in self.data.iteritems():
            # k is registry name, v is a dict
            # v's format is as follows:
            # {'class': '<class name of registry>',
            #  'data': {key1: val1, key2: val2, etc: etc, },
            #  }
            # first a little type sanity check
            if not isinstance(k, (str, unicode, )):
                raise ValueError(
                        'registry name must be string; got %s (of type %s)'
                        % (repr(k), repr(type(k)), )
                        )

            if not isinstance(v, dict):
                raise ValueError(
                        'pythonized config entry must be dict; got type %s'
                        % (repr(type(v)), )
                        )

            # type(v) ok ,move on to strictly match the keys...
            v_keys = tuple(sorted(v.iterkeys()))
            if v_keys != ('class', 'data', ):
                raise ValueError('malformed pythonized registry definition')

            # types of class and data...
            if not isinstance(v['class'], (str, unicode, )):
                raise ValueError('registry class name not of string type')

            # class validation
            try:
                cls = VALID_REGISTRY_TYPES[v['class']]
            except KeyError:
                raise ValueError("registry class name '%s' not valid"
                        % (v['class'], )
                        )

            if not isinstance(v['data'], dict):
                raise ValueError('pythonized data set must be dict')

            # format check (finally...) passed, go on with actually updating
            # NOTE: obviously registries cannot have duplicate names,
            # here we'll rely on RegistryBase's behavior to ensure this :P
            reg = request(k, autocreate=True, nodup=True, klass=cls)
            for reg_k, reg_v in v['data'].iteritems():
                reg[reg_k] = reg_v


class JSONConfig(BaseConfig):
    '''JSON config backend.'''

    def _do_loads(self, s, *args, **kwargs):
        dump = json.loads(s, *args, **kwargs)
        # TODO: some canonicalization or such
        return dump


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
