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

import inspect
from functools import wraps

import six

from .. import init
from ..adapters import adapter_hub
from ..router import router_hub
from ..rendering.decorators import renderable
from ..utils.decorators import view


def expose(fn):
    '''``__all__`` registry helper.'''

    __all__.append(fn.__name__)
    return fn


# Expose convenient aliases.
expose(renderable)
expose(view)

make_app = adapter_hub.make_app
expose(make_app)

boot, inject_app = init.boot, init.inject_app
expose(boot)
expose(inject_app)

# Special case: the former load_all() got renamed to boot(), we need to
# preserve its name for compatibility (actually that's because I'm too lazy
# to rename all these occurences in my apps...)
load_all = init.boot

# NOTE: This str() call is correct as it IS the 'string' type recognized by
# the IMPORT_STAR thing, and it isn't that easy to make one using six.
__all__.append(str('load_all'))


@expose
def jsonview(fn):
    '''Short for doing ``@renderable('json')`` and ``@view`` in a row.'''

    return renderable('json')(view(fn))


def _transform_view_name(name):
    tmpname = name[:-5] if name.endswith('_view') else name
    return tmpname.replace('_', '-')


@expose
def http(name=None):
    '''Register a view for the HTTP router.

    If ``name`` is given as a string, this is a convenient form of
    ``@router_hub.endpoint('http', name)``. If ``name`` is not given
    (``@http()``), or if the decorator is used directly (``@http``), view
    name is derived from the function name by removing a ``_view`` suffix
    if present, and then replacing all underscores with hyphens.

    '''

    def _decorator_(fn):
        view_name = name or _transform_view_name(fn.__name__)
        return router_hub.endpoint('http', view_name)(fn)

    if callable(name):
        # Quick and dirty check to see if name is actually a function
        # (the @http case).
        fn, name = name, None
        return _decorator_(fn)

    return _decorator_



# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
