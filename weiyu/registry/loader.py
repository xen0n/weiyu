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

As much of weiyu's functionality relies on the registries, there should be
a convenient way of pre-loading configuration data before performing any
significant actions. This module serves just that purpose, providing several
configuration formats free to choose from; of course, you are also free to
roll your own loader by inheriting :class:`.BaseConfig` and implement the
``_do_loads`` method. At present, only JSON and Python pickles are
available for use; more is expected to be added.


Basics
------

Global configuration files which is used by
:meth:`BaseConfig.populate_central_regs` to populate (possibly) multiple
registries must have a Pythonized format like this::

    {
        u'registry.name.1': {
            u'class': u'ClassNameOfRegistry', # must be bytes or unicode
            u'no_update': True or False,
            u'data': {
                # this is the actual configuration data
                u'spam': u'foo',
                u'eggs': 42,
                u'etc': u'etc',
                }
            },

        # optionally more registries, or directives to follow
    }

The ``class`` attribute must specify one of the registry types "exported"
in :mod:`weiyu.registry.classes`; this limitation may be lifted in future
versions of weiyu.

The ``no_update`` boolean, whose value is directly passed as the
``nodup`` parameter to :func:`weiyu.registry.provider.request`,
indicates that an exception should be raised when a registry with the
same name already exists (possibly initialized to an empty one by its
associated module). It really should be set to ``False`` for populating
registries initialized by modules. Only set this to ``True`` when you are
sure that no module will try to create the registry before you load the
configuration.


Preprocessing directives
------------------------

Directives are just sections in the config file with names starting with
``$$``. They are then parsed by :meth:`BaseConfig.process_directives`.

Currently there is only one directive implemented: the (top-level) include
directive ``$$include``. Its parameter is a ``list`` of files to source:
content of the files are read and processed in order, overwriting values
if they already exist. It does not support including files into a variable,
for example, at the moment. Also it does not detect circular includes, any
such situation the loader will loop infinitely and eventually crash with a
:exc:`MemoryError`. Don't try that.


Classes
-------

'''

from __future__ import unicode_literals, division

from os.path import abspath
from functools import wraps
import abc
import json

try:
    import cPickle as pickle
except ImportError:
    # at least there REALLY should be pickle, so I'm not going to catch
    # any exception
    import pickle

from .classes import VALID_REGISTRY_TYPES
from .provider import request


class BaseConfig(object):
    '''Base class for prepopulated config storages. It has an interface
    inspired by ``pickle``: methods such as :meth:`loads` and :meth:`load`
    exist and more or less behaves like the standard library counterpart.

    The :meth:`_do_loads` method is abstract, it is up to you to decide the
    way configuration files map to Python object in a subclass.

    '''

    __metaclass__ = abc.ABCMeta

    def __init__(self, path=None):
        '''Constructor function.

        :param path: Path to config file. Defaults to ``None``; If this is
        the case, data may be loaded by directly calling :meth:`loads` or
        :meth:`load` with the appropriate type of data source.

        '''

        self.path, self.data = path, None

    @abc.abstractmethod
    def _do_loads(self, s, *args, **kwargs):
        '''Constructs a Python object from input. This method is abstract.

        :param s: The input string.

        .. note::

            Don't do preprocessing in this method; they are to be done by
            :meth:`loads` and the other interface methods. Just construct
            the "raw" deserialized form.

        '''

        pass

    def loads(self, s, *args, **kwargs):
        '''Loads configuration from a string.
        '''

        raw_data = self._do_loads(s, *args, **kwargs)
        self.data = self.process_directives(raw_data)
        return self.data

    def load(self, fp=None, *args, **kwargs):
        '''Loads configuration from a file-like object with a ``read`` method.

        .. note::

            The implementation at this point is naive. It just tries to read
            the whole input, then feeds the string into :meth:`loads`. Beware
            if the input is potentially very large.

        '''

        # XXX this function's a naive wrapper to get rid of some duplication

        if fp is None:
            # invoke ``self.load_from_path`` to read the file specified
            # by ``self.path``
            return self.load_from_path(None)

        # Unicode cleanness
        return self.loads(
                fp.read().decode('utf-8', 'replace'),
                *args, **kwargs
                )

    def load_from_path(self, path=None):
        '''Loads configuration from path ``path``; if ``path`` is ``None``,
        try to use ``self.path``. If that value is also ``None``, a
        :exc:`ValueError` is ``raise``\ d.

        '''

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

    def ensure_data_presence(self):
        '''When called, checks if ``self.data`` is ``None``. If it is the
        case, calls :meth:`load_from_path` to load configuration from
        ``self.path``. Note that this method does NOT ensure the
        *consistency* between the stored state and the config file's data;
        it just checks for presence.

        '''

        if self.data is None:
            self.load_from_path(None)

    def populate_registry(self, registry):
        '''Populates a single registry instance. For filling the global
        registry, use :meth:`populate_central_regs`.

        '''

        self.ensure_data_presence()
        for k, v in self.data.iteritems():
            registry.register(k, v)

    def populate_central_regs(self):
        '''Fills the central registry, i.e. the
        :class:`.classes.RegistryRegistry` singleton. Config data format
        used for this method is described above.

        '''

        self.ensure_data_presence()
        for k, v in self.data.iteritems():
            # k is registry name, v is a dict
            # v's format is as follows:
            # {'class': '<class name of registry>',
            #  'no_update': True/False,
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
            if v_keys != ('class', 'data', 'no_update', ):
                raise ValueError('malformed pythonized registry definition')

            # types of class and data...
            if not isinstance(v['class'], (str, unicode, )):
                raise ValueError('registry class name not of string type')

            if not isinstance(v['no_update'], bool):
                raise ValueError('no_update property must be boolean')
            nodup = v['no_update']

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
            reg = request(k, autocreate=True, nodup=nodup, klass=cls)
            for reg_k, reg_v in v['data'].iteritems():
                reg[reg_k] = reg_v


class JSONConfig(BaseConfig):
    '''JSON config backend.'''

    def _do_loads(self, s, *args, **kwargs):
        dump = json.loads(s, *args, **kwargs)
        # TODO: some canonicalization or such
        return dump


class PickleConfig(BaseConfig):
    '''Python pickle config backend.'''

    def _do_loads(self, s, *args, **kwargs):
        return pickle.loads(s, *args, **kwargs)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
