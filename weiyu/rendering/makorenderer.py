#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / rendering / Mako renderer
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
Mako Renderer
~~~~~~~~~~~~~

'''

from __future__ import unicode_literals, division

__all__ = ['MakoRenderable', ]

from os.path import abspath

from mako.lookup import TemplateLookup

from . import Hub
from .base import Renderable

from ..registry.provider import request

TMPL_LOOKUP_KEY = 'lookup_obj'
DIRECTORIES_KEY = 'directories'
MODULE_DIR_KEY = 'module_dir'


class MakoRenderable(Renderable):
    def __init__(self, tmpl, *args, **kwargs):
        super(MakoRenderable, self).__init__(*args, **kwargs)
        self._template = tmpl

    def _do_render(self, context):
        return self._template.render(**dict(context))


@Hub.register_handler('mako')
def mako_render_handler(name, *args, **kwargs):
    render_reg = request('weiyu.rendering')
    # TODO: config default value here, or proper exc handling
    mako_params = render_reg['mako']
    if TMPL_LOOKUP_KEY not in mako_params:
        # canonicalize template dirs to absolute path
        abspath_dirs = [abspath(i) for i in mako_params[DIRECTORIES_KEY]]

        # instantiate TemplateLookup singleton
        mako_params[TMPL_LOOKUP_KEY] = TemplateLookup(
                directories=abspath_dirs,
                module_directory=mako_params[MODULE_DIR_KEY],
                )

    lookup = mako_params[TMPL_LOOKUP_KEY]
    # TODO: possibly map template names to filenames here
    tmpl = lookup.get_template(name)
    return MakoRenderable(tmpl, *args, **kwargs)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
