#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / hooking mechanism / hook decorator
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
Hook decorator
~~~~~~~~~~~~~~

This module provides the mechanism to attach both pre- and post-processing
hooks to any function, via the ``hookable`` decorator.

.. note::
    ``weiyu.hooks.registry`` must be ``import``\ ed first, or the required
    registry ``'weiyu.hooks'`` won't be in place when referenced.

'''

from __future__ import unicode_literals, division

__all__ = [
            'PrematureStopRequest',
            'hookable',
            ]

from functools import wraps

from weiyu.registry.provider import request

# protect this initialization against Sphinx's autodoc
try:
    import __builtin__
    __builtin__.__WEIYU_IN_SPHINX_AUTODOC
    del __builtin__
except NameError:
    HOOK_REGISTRY = request('weiyu.hooks')


# TODO: move this into another file
class PrematureStopRequest(Exception):
    '''Exception class used to prematurely end a call to hooked function.

    Instantiate this class with the value you want to return.

    '''

    def __init__(self, retval):
        self.retval = retval


def hookable(name=None):
    '''Makes a function or method hookable by ``name``.
    
    If ``name`` is ``None`` (as is the case when the decorator is used as
    ``@hookable()``), the function's ``func_name`` is used.

    '''

    def _decorator_(fn):
        # register a record
        # registering based on the fn passed in is *impractical*, since
        # after executing the decorator, the fn would be replaced by our
        # freshly generated wrapper...
        hook_name = name if name is not None else unicode(fn.func_name)
        HOOK_REGISTRY[hook_name] = ([], [], )
        hooks_ref = HOOK_REGISTRY[hook_name]

        @wraps(fn)
        def _wrapped_(*args, **kwargs):
            result = None

            try:
                for preprocess_hook in hooks_ref[0]:
                    preprocess_hook(*args, **kwargs)
            except PrematureStopRequest, stop_packet:
                result = stop_packet.retval
            else:
                result = fn(*args, **kwargs)

            for postprocess_hook in hooks_ref[1]:
                result = postprocess_hook(result, *args, **kwargs)

            return result

        return _wrapped_

    return _decorator_


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
