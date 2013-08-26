#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / rendering / JSON renderer
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
JSON renderer
-------------

.. todo::

    This part of documentation is yet to be written.

'''

from __future__ import unicode_literals, division

__all__ = ['JSONRenderable', ]

try:
    # favor esnme's ujson accelerated library
    from ujson import dumps
except ImportError:
    # fallback on the stdlib
    from json import dumps

    # use compact encoding, so construct a shim to keep the function
    # signature consistent
    from functools import partial
    dumps = partial(dumps, separators=(',', ':', ))

from . import render_hub
from .base import Renderable

# FIXME: this doesn't work for [lte IE 7], as a Save As dialog would pop up.
# We need to sniff the UA string and return text/javascript in that case.
JSON_COMMON_EXTRAS = {
        'mimetype': 'application/json',
        }


class JSONRenderable(Renderable):
    def _do_render(self, result, context):
        # only expose the desired result object
        return dumps(dict(result)), JSON_COMMON_EXTRAS


@render_hub.register_handler('json')
def json_render_handler(hub, name, *args, **kwargs):
    # template name is meaningless in JSON rendering, thus ignored.
    return JSONRenderable(*args, **kwargs)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
