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

from ..adapters import adapter_hub
from ..db import db_hub
from ..router import router_hub
from ..rendering.decorators import renderable
from ..registry.loader import BaseConfig
from ..utils.decorators import view
from ..utils.viewloader import ViewLoader


def expose(fn):
    '''``__all__`` registry helper.'''

    __all__.append(fn.func_name)
    return fn


# Expose convenient aliases.
expose(renderable)
expose(view)

make_app = adapter_hub.make_app
expose(make_app)


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
        view_name = name or _transform_view_name(fn.func_name)
        return router_hub.endpoint('http', view_name)(fn)

    if callable(name):
        # Quick and dirty check to see if name is actually a function
        # (the @http case).
        fn, name = name, None
        return _decorator_(fn)

    return _decorator_


@expose
def load_router(typ, filename):
    router = router_hub.init_router_from_config(typ, filename)
    return router_hub.register_router(router)


@expose
def load_config(path):
    ret = BaseConfig.get_config(path).populate_central_regs()

    # Refresh the hubs' internal cached references, this MUST be done
    # after config has loaded.
    db_hub._init_refresh_map()

    return ret


@expose
def load_views(path):
    return ViewLoader(path)()


@expose
def load_all(
        conf_path='conf.json',
        views_path='views.json',
        router_type='http',
        root_router_file='urls.txt',
        ):
    # initialize registries, views, router, in that order
    load_config(conf_path)
    load_views(views_path)
    load_router(router_type, root_router_file)


@expose
def inject_app(app_type='wsgi', var='application', *args, **kwargs):
    # Make app
    load_all(*args, **kwargs)
    app = make_app(app_type)

    # Then inject the object into the caller's global namespace
    parentframe = inspect.getouterframes(inspect.currentframe())[1][0]
    parentframe.f_globals[var] = app


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
