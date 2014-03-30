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

'''
Mako renderer
-------------

This renderer, and the associated handler for type ``'mako'``, provides
integration with the `Mako templating system`_. It reads configuration
from the key ``'mako'`` in registry ``'weiyu.rendering'``.

.. _Mako templating system: http://www.makotemplates.org/


Configuration options
^^^^^^^^^^^^^^^^^^^^^

Path to template directories can (and must) be configured. Also optionally
one may specify a directory for storing compiled template code.

+------------+-----------------+-------------------------------------+
|Config key  |Type of value    |Meaning                              |
+============+=================+=====================================+
|directories |list of strings  |Paths to template directories        |
+------------+-----------------+-------------------------------------+
|module_dir  |(unicode) string |Path to store compiled template code |
|            |                 |in, typically one in ``/tmp``        |
+------------+-----------------+-------------------------------------+

'''

from __future__ import unicode_literals, division

__all__ = ['MakoRenderable', ]

from os.path import abspath

import six

from mako.lookup import TemplateLookup

from . import render_hub
from .base import Renderable

from ..registry.provider import request

TMPL_LOOKUP_KEY = 'lookup_obj'
DIRECTORIES_KEY = 'directories'
MODULE_DIR_KEY = 'module_dir'

_EXTENDED_PATH_HANDLERS = {}


class MakoRenderable(Renderable):
    def __init__(self, tmpl, *args, **kwargs):
        super(MakoRenderable, self).__init__(*args, **kwargs)
        self._template = tmpl

    def _do_render(self, result, context):
        real_ctx = result.copy()
        real_ctx.update(context)
        return self._template.render_unicode(**real_ctx), {}


def _path_handler(name):
    def _decorator_(fn):
        _EXTENDED_PATH_HANDLERS[name] = fn
        return fn
    return _decorator_


@_path_handler('pkg_resources')
def _handle_pkg_resources_path(cfg):
    import pkg_resources

    pkg, res = cfg['package'], cfg['resource']
    if not pkg_resources.resource_isdir(pkg, res):
        raise ValueError(
                'Resource is not a directory: {0} in package {1}'.format(
                    res,
                    pkg,
                    ))

    return pkg_resources.resource_filename(pkg, res)


def _ensure_lookup(__cache=[]):
    try:
        return __cache[0]
    except IndexError:
        pass

    render_reg = request('weiyu.rendering')
    # TODO: config default value here, or proper exc handling
    mako_params = render_reg['mako']

    abspath_dirs = []
    for i in mako_params[DIRECTORIES_KEY]:
        if isinstance(i, six.text_type):
            # canonicalize template dirs to absolute path
            abspath_dirs.append(abspath(i))
        elif isinstance(i, dict):
            # extended configuration
            path_type = i['type']
            if path_type not in _EXTENDED_PATH_HANDLERS:
                raise RuntimeError("path type '%s' not available" % path_type)

            path_handler = _EXTENDED_PATH_HANDLERS[path_type]
            processed_path = path_handler(i)
            abspath_dirs.append(processed_path)

    kwargs = {'directories': abspath_dirs, }

    try:
        kwargs['module_directory'] = mako_params[MODULE_DIR_KEY]
    except KeyError:
        pass

    # instantiate TemplateLookup singleton and expose it in registry
    lookup = mako_params[TMPL_LOOKUP_KEY] = TemplateLookup(**kwargs)

    # also save cache
    __cache.append(lookup)

    return lookup


@render_hub.register_handler('mako')
def mako_render_handler(hub, name, *args, **kwargs):
    # TODO: possibly map template names to filenames here
    tmpl = _ensure_lookup().get_template(name)
    return MakoRenderable(tmpl, *args, **kwargs)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
