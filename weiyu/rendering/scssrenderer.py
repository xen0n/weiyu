#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / rendering / SCSS renderer
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

'''
SCSS renderer
-------------

This renderer is a wrapper around the `pyScss`_ SCSS library. The renderer
reads its configuration from the key ``'scss'`` in registry
``'weiyu.rendering'``.

.. _pyScss: https://github.com/Kronuz/pyScss

'''

from __future__ import unicode_literals, division

__all__ = ['SCSSRenderable', ]

from os.path import abspath

import scss

from . import render_hub
from .base import Renderable

from ..registry.provider import request

SCSS_COMMON_EXTRAS = {
        'mimetype': 'text/css',
        }

SCSS_CONFIG_KEYS = (
        'STATIC_ROOT STATIC_URL ASSETS_ROOT ASSETS_URL LOAD_PATHS'
        ).split(' ')

SCSS_OPTS_KEY = 'opts'
SCSS_DEFAULT_OPTS = {
        'compress': True,
        }


class SCSSRenderable(Renderable):
    def __init__(self, options, *args, **kwargs):
        super(SCSSRenderable, self).__init__(*args, **kwargs)
        self._options = options

    def _do_render(self, result, context):
        # Filename is passed via context due to limitation of @renderable(),
        # which is primarily designed for templating systems.
        filename = context['scss_file']

        # Compiler.
        # result is the context variables of SCSS
        compiler = scss.Scss(scss_vars=result, scss_opts=self._options)

        return compiler.compile(scss_file=filename), SCSS_COMMON_EXTRAS


@render_hub.register_handler('scss')
def scss_render_handler(hub, name, *args, **kwargs):
    render_reg = request('weiyu.rendering')
    # TODO: default value
    scss_params = render_reg['scss']

    if '_inited' not in scss_params:
        # config global params
        for k in SCSS_CONFIG_KEYS:
            if k in scss_params:
                setattr(scss.config, k, scss_params[k])

        # prepare compile options
        options = scss_params['_options'] = SCSS_DEFAULT_OPTS.copy()
        if SCSS_OPTS_KEY in scss_params:
            options.update(scss_params[SCSS_OPTS_KEY])

        scss_params['_inited'] = True

    options = scss_params['_options']

    return SCSSRenderable(options, *args, **kwargs)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
