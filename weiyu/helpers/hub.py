#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / helpers / module hub management
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

'''
Dispatch hub module
~~~~~~~~~~~~~~~~~~~

'''

from __future__ import unicode_literals, division

__all__ = ['BaseHub', ]

from functools import partial

from ..registry.provider import request


class BaseHub(object):
    '''A module-level hub used to register handlers for the types of data it
    can process. It works by keeping a type-to-handler mapping ``dict`` in a
    registry; as a side effect, handlers can be added, modified or deleted
    on the fly, during system operation.

    The class is meant for usage in package-level ``__init__.py`` files::

        # in one of your __init__.py files:

        # best to only "expose" the Hub instance
        __all__ = ['Hub', ]

        from weiyu.helpers.hub import BaseHub
        from weiyu.registry.classes import UnicodeRegistry


        class SpamEggHub(BaseHub):
            # specify several required properties
            registry_name = 'sketch'
            registry_class = UnicodeRegistry
            handlers_key = 'handlers'


        # instantiate a single Hub instance
        Hub = SpamEggHub()

    Then you can register your functions like this::

        # in spam.py, which is inside the abovementioned package

        from . import Hub


        # handler function
        @Hub.register_handler('spam')
        def spam_handler(*args, **kwargs):
            pass


        # do similar things for the other .py files containing handlers to
        # be registered

    Just be sure to have ``import``\ ed the module before operation starts;
    otherwise the handler mapping is not there, for obvious reasons. This
    may get fixed in some later revisions.

    The class attributes that must be present in subclasses is described
    below:

    :attr registry_name: name of the registry used to hold the
      type-to-handler mapping;
    :attr registry_class: the proper registry class to use, if the registry
      named by ``registry_name`` does not exist at the time of hub creation;
    :attr handlers_key: key which the type-to-handler mapping resides in.

    To avoid excessive attribute lookups when retrieving reference to the
    internal mapping, the mapping ``dict`` is cached. If it turns out that
    dynamically substituting the handler mapping object is necessary, you
    need to ensure that :meth:`refresh_handler_map` is called right after
    applying the object replacement, and before any potential call to get a
    handler. As long as you don't totally replace the mapping object (which
    is almost always the case), calling this method is NOT needed and
    meaningless, as it will read back the same reference.

    '''

    def __init__(self):
        cls = self.__class__
        self._reg = request(
                cls.registry_name,
                autocreate=True,
                nodup=False,
                klass=cls.registry_class,
                )

        if cls.handlers_key not in self._reg:
            self._reg[cls.handlers_key] = {}

        # this is to reduce attribute lookups
        self.refresh_handler_map()

    def refresh_handler_map(self):
        '''Re-reads in-registry reference to the type-to-handler mapping.

        This method exists only in case the mapping needs to be pointed to
        a brand-new object; it should not be called in most cases.

        '''

        self._handlers = self._reg[self.__class__.handlers_key]

    def register_handler(self, typ):
        '''Decorator to register a handler for type ``typ``; the decorated
        object is returned untouched.

        In case a handler for ``typ`` is already registered, the previous
        reference is replaced by the new one.

        '''

        def _decorator_(thing):
            # NOTE: Doesn't work with FunctionValueRegistry
            self._handlers[typ] = thing
            return thing
        return _decorator_

    def remove_handler(self, typ):
        '''Removes the handler associated with type ``typ``; does nothing
        if the handler does not exist.

        '''

        try:
            self._handlers.pop(typ)
        except KeyError:
            pass

    def get_handler(self, typ):
        '''Get the handler associated with type ``typ``.

        .. note::
            Exceptions are intentionally not caught in this method, you
            may have to explicitly deal with the possible cases.

        '''

        # NOTE: Exception is intentionally propagated, a KeyError for
        # unregistered handler is nice...
        # Also, handlers' signatures all have a 'hub' argument as their
        # first parameter, so we'd curry the hub itself into the resulting
        # callable.
        return partial(self._handlers[typ], self)

    def do_handling(self, typ, *args, **kwargs):
        '''Get the handler, and additionally do the work of invoking the
        handler with the proper argument specified, in one step. This is
        a shortcut method.

        '''

        return self.get_handler(typ)(*args, **kwargs)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
