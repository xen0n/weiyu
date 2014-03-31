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

import os
import inspect
import warnings

import six

from ..adapters import adapter_hub
from ..db import db_hub
from ..router import router_hub
from ..registry.classes import UnicodeRegistry
from ..registry.loader import BaseConfig
from ..registry.provider import request as regrequest
from .viewloader import ViewLoader

# XXX Force load of HTTPSessionMiddleware
from ..adapters.http import base
del base

CONFIG_LOADED = False


def _ensure_site_registry():
    return regrequest(
            'site',
            autocreate=True,
            nodup=False,
            klass=UnicodeRegistry,
            )


def _do_load_router(typ, filename):
    router = router_hub.init_router_from_config(typ, filename)
    return router_hub.register_router(router)


def load_router(typ, filename=None):
    if filename is not None:
        # configured by app stub
        return _do_load_router(typ, filename)

    reg_site = _ensure_site_registry()
    if 'urls' in reg_site:
        # configured by registry
        return _do_load_router(typ, reg_site['urls'])

    # probe for different defaults
    if os.path.exists('Rain.d/root.URLfile'):
        if os.path.exists('urls.txt'):
            warnings.warn(
                    'Rain.d/root.URLfile overrides urls.txt, please migrate '
                    'and delete the old URL routing files to avoid any '
                    'possible inconsistencies',
                    DeprecationWarning,
                    )
        return _do_load_router(typ, 'Rain.d/root.URLfile')

    if os.path.exists('urls.txt'):
        warnings.warn(
                'The filename \'urls.txt\' for URL routing is '
                'deprecated, please move to Rain.d/root.URLfile (no other '
                'changes needed)',
                DeprecationWarning,
                )
        return _do_load_router(typ, 'urls.txt')

    raise RuntimeError('no default URL routing configuration found')


def _do_load_config(path):
    global CONFIG_LOADED
    if CONFIG_LOADED:
        return

    # this has no return value as of now, safe to discard returned None
    BaseConfig.get_config(path).populate_central_regs()

    # Refresh the hubs' internal cached references, this MUST be done
    # after config has loaded.
    db_hub._init_refresh_map()

    CONFIG_LOADED = True


def load_config(path=None):
    if path is not None:
        _do_load_config(path)
    else:
        # Default config file.
        if os.path.exists('Rain.d/config.yml'):
            # 1. Rain.d ((again) new default)
            if any(
                    os.path.exists(f)
                    for f in ('Rainfile.yml', 'conf.yml', 'conf.json')
                    ):
                warnings.warn(
                        'Rain.d/config.yml overrides the config files with '
                        'old default names, please migrate and delete the '
                        'old configuration files to avoid any possible '
                        'inconsistencies',
                        DeprecationWarning,
                        )
            _do_load_config('Rain.d/config.yml')
        elif os.path.exists('Rainfile.yml'):
            # 2. Rainfile (old default)
            warnings.warn(
                    'The filename \'Rainfile.yml\' for configuration is '
                    'deprecated, please move to Rain.d/config.yml (no other '
                    'changes needed)',
                    DeprecationWarning,
                    )
            _do_load_config('Rainfile.yml')
        elif os.path.exists('conf.yml'):
            # 3. conf.yml (old^2 default)
            warnings.warn(
                    'The filename \'conf.yml\' for configuration is '
                    'deprecated, please move to Rain.d/config.yml (no other '
                    'changes needed)',
                    DeprecationWarning,
                    )
            _do_load_config('conf.yml')
        elif os.path.exists('conf.json'):
            # 4. conf.json (VERY VERY old default, since weiyu's inception)
            warnings.warn(
                    'JSON configuration stored in \'conf.json\' is LONG '
                    'deprecated. Please consider migrating your '
                    'configurations to YAML for better readability and ease '
                    'of maintenance, then store it in Rain.d/config.yml',
                    DeprecationWarning,
                    )
            _do_load_config('conf.json')
        else:
            raise RuntimeError('no default configuration found')


def load_views(path_or_config):
    if isinstance(path_or_config, six.string_types):
        # this is a path to views.json
        return ViewLoader().fileconfig(path_or_config)()

    # direct config by dict
    return ViewLoader(path_or_config)()


def boot(
        conf_path=None,
        views_path=None,
        router_type='http',
        root_router_file=None,
        ):
    # initialize registries, views, router, in that order
    # registry
    load_config(conf_path)

    # make an empty site registry if not present
    reg_site = _ensure_site_registry()

    # determine if ViewLoader is configured by registry
    if views_path is not None:
        # external file configured by app stub
        load_views(views_path)
    else:
        # extract config from site registry
        if 'views' in reg_site:
            view_config = reg_site['views']
            load_views(view_config)
        else:
            # old behavior, which is an implicit (specified via default)
            # views.json, kept for compatibility
            warnings.warn(
                    'Implicit views.json is discouraged, please put the '
                    'view config directly into main config file',
                    PendingDeprecationWarning,
                    )
            load_views('views.json')

    # init router
    load_router(router_type, root_router_file)

    # register middlewares according to config
    middleware_decl = (
            reg_site['middlewares']
            if 'middlewares' in reg_site
            else {}
            )

    def call_register_middleware(kind):
        middlewares = middleware_decl.get(kind, [])
        adapter_hub.register_middleware_chain(
                router_type,
                kind,
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
