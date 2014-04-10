#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / rendering / pass-through renderer
#
# Copyright (C) 2014 Wang Xuerui <idontknw.wang-at-gmail-dot-com>
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
Pass-through renderer
---------------------

This renderer just passes the input bytestring through. Useful if the view
takes care of the rendering details itself.

'''

from __future__ import unicode_literals, division

__all__ = ['PassthruRenderable', ]

from ..helpers.misc import smartbytes
from . import render_hub
from .base import Renderable


class PassthruRenderable(Renderable):
    def _do_render(self, result, context):
        return smartbytes(result), {}


@render_hub.register_handler('passthru')
def passthru_render_handler(hub, name, *args, **kwargs):
    # template name ignored
    return PassthruRenderable(*args, **kwargs)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
