#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / framework-level initialization / package
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
        'load_router',
        'load_config',
        'load_views',
        'boot',
        ]

import inspect

from ..adapters import adapter_hub
from ..db import db_hub
from ..router import router_hub
from ..registry.classes import UnicodeRegistry
from ..registry.loader import BaseConfig
from ..registry.provider import request as regrequest
from ..utils.decorators import view
from .viewloader import ViewLoader


def load_router(typ, filename):
    router = router_hub.init_router_from_config(typ, filename)
    return router_hub.register_router(router)


def load_config(path):
    ret = BaseConfig.get_config(path).populate_central_regs()

    # Refresh the hubs' internal cached references, this MUST be done
    # after config has loaded.
    db_hub._init_refresh_map()

    return ret


def load_views(path):
    return ViewLoader().fileconfig(path)()


def boot(
        conf_path='conf.json',
        views_path='views.json',
        router_type='http',
        root_router_file='urls.txt',
        ):
    # initialize registries, views, router, in that order
    load_config(conf_path)
    load_views(views_path)
    load_router(router_type, root_router_file)

    # make an empty site registry if not present
    reg_site = regrequest('site', autocreate=True, klass=UnicodeRegistry)

    # register middlewares according to config
    middleware_decl = reg_site['middlewares'] if 'middlewares' in reg_site else {}

    def call_register_middleware(kind):
        middlewares = middleware_decl.get(kind, [])
        adapter_hub.register_middleware_chain(
                '%s-middleware-%s' % (router_type, kind, ),
                middlewares,
                )

    call_register_middleware('pre')
    call_register_middleware('post')


def inject_app(app_type='wsgi', var='application', *args, **kwargs):
    # Make app
    boot(*args, **kwargs)
    app = adapter_hub.make_app(app_type)

    # Then inject the object into the caller's global namespace
    parentframe = inspect.getouterframes(inspect.currentframe())[1][0]
    parentframe.f_globals[var] = app


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
