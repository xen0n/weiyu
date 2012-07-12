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

u'''
JSON renderer
-------------

.. todo::

    This part of documentation is yet to be written.

'''

from __future__ import unicode_literals, division

__all__ = ['JSONRenderable', ]

from json import dumps

from . import render_hub
from .base import Renderable


class JSONRenderable(Renderable):
    def _do_render(self, context):
        return dumps(dict(context))


@render_hub.register_handler('json')
def json_render_handler(hub, name, *args, **kwargs):
    # template name is meaningless in JSON rendering, thus ignored.
    return JSONRenderable(*args, **kwargs)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
