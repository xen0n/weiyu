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
--------------

This module provides the mechanism to attach both pre- and post-processing
hooks to any function, via the :func:`hookable` decorator.

'''

from __future__ import unicode_literals, division

__all__ = [
            'hookable',
            ]

from functools import wraps

from ..registry.provider import request


def hookable(name=None):
    '''Makes a function or method hookable by ``name``.

    If ``name`` is ``None`` (as is the case when the decorator is used as
    ``@hookable()``), the function's ``func_name`` is used.

    '''

    # move to closure scope; automatically shielded from autodoc, and since
    # the registry is singleton, putting it anywhere should be OK
    HOOK_REGISTRY = request('weiyu.hooks')

    def _decorator_(fn):
        # register a record
        # registering based on the fn passed in is *impractical*, since
        # after executing the decorator, the fn would be replaced by our
        # freshly generated wrapper...
        hook_name = name if name is not None else unicode(fn.func_name)
        HOOK_REGISTRY[hook_name] = ([], [], )
        hooks_ref = HOOK_REGISTRY[hook_name]

        @wraps(fn)
        def _wrapped_hookable_(*args, **kwargs):
            result = None

            for preprocess_hook in hooks_ref[0]:
                result = preprocess_hook(*args, **kwargs)

                if result is not None:
                    break

            if result is None:
                result = fn(*args, **kwargs)

            for postprocess_hook in hooks_ref[1]:
                result = postprocess_hook(result, *args, **kwargs)

            return result

        return _wrapped_hookable_

    return _decorator_


def hook_before(name, append=False):
    # TODO: document this family of registration
    def _decorator_(fn):
        hook_reg = request('weiyu.hooks')
        target_list = hook_reg[name][0]
        if append:
            target_list.append(fn)
        else:
            target_list.insert(0, fn)

        return fn
    return _decorator_


def hook_after(name, prepend=False):
    def _decorator_(fn):
        hook_reg = request('weiyu.hooks')
        target_list = hook_reg[name][1]
        if prepend:
            target_list.insert(0, fn)
        else:
            target_list.append(fn)

        return fn
    return _decorator_


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
