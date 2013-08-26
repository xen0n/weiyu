#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / utilities / decorators
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

from __future__ import unicode_literals, division

__all__ = [
        'view',
        'only_methods',
        ]

import decorator

from ..reflex.classes import ReflexResponse
from ..helpers.annotation import annotate


def _view_func_(fn, request, *args, **kwargs):
    status, content, context = fn(request, *args, **kwargs)
    return ReflexResponse(
            status,
            content,
            context,
            request,
            )


def view(fn):
    '''View decorator to avoid having to
    ``from weiyu.reflex.classes import ReflexResponse`` everywhere.

    '''

    return decorator.decorator(_view_func_, fn)


def only_methods(methods=None):
    '''Decorator to only allow certain types of HTTP methods.

    Defaults to ``GET`` only.

    Must occur *after* the ``@view`` decorator.

    '''

    methods = ['GET', ] if methods is None else methods

    def _decorator_(fn):
        # Although the actual binding of methods list occurs in
        # closure scope, we keep a reference of it in annotation
        # for clarity.
        annotate(fn, allowed_methods=methods)

        def _wrapped_(fn, request, *args, **kwargs):
            if request.method not in methods:
                # method not allowed
                # set an Allow header
                allowed_hdr = ', '.join(methods).encode('utf-8')
                return (
                        405,
                        {},
                        {'allowed_methods': allowed_hdr, },
                        )

            return fn(request, *args, **kwargs)
        return decorator.decorator(_wrapped_, fn)
    return _decorator_


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
