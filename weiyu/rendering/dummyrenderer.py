#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / rendering / dummy renderer
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
Dummy renderer
--------------

This renderer, as its name suggests, does not render anything. This is
useful when implementing certain API endpoints that do not or must not
return any content.

'''

from __future__ import unicode_literals, division

__all__ = ['DummyRenderable', ]

from . import render_hub
from .base import Renderable


class DummyRenderable(Renderable):
    def _do_render(self, result, context):
        # Intentionally left blank
        return b'', {}


@render_hub.register_handler('dummy')
def dummy_render_handler(hub, name, *args, **kwargs):
    # template name is meaningless, thus ignored.
    return DummyRenderable(*args, **kwargs)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
