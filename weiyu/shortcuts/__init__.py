#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / shortcuts / package
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
        ]

from functools import wraps

from ..router import router_hub
from ..rendering.decorator import renderable
from ..reflex.classes import ReflexResponse


def expose(fn):
    '''``__all__`` registry helper.'''

    __all__.append(fn.func_name)
    return fn


# Expose convenient aliases.
expose(renderable)


@expose
def view(fn):
    '''View decorator to avoid having to
    ``from weiyu.reflex.classes import ReflexResponse`` everywhere.

    '''

    @wraps(fn)
    def _view_func_(request, *args, **kwargs):
        status, content, context = fn(request, *args, **kwargs)
        return ReflexResponse(
                status,
                content,
                context,
                request,
                )
    return _view_func_


@expose
def http(name):
    '''Convenient form of ``@router_hub.endpoint('http', name)``.'''

    def _decorator_(fn):
        return router_hub.endpoint('http', name)(fn)
    return _decorator_


@expose
def load_router(typ, filename):
    router = router_hub.init_router_from_config(typ, filename)
    return router_hub.register_router(router)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
