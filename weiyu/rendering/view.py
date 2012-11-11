#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / rendering / view renderer
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

from __future__ import unicode_literals, division

__all__ = [
        'render_view_func',
        ]

from . import render_hub
from .exc import RenderingError
from .base import RenderContext

from ..helpers.annotation import get_annotation


def render_view_func(renderable_fn, result, context, typ):
    render_info = get_annotation(renderable_fn, 'rendering')

    if typ not in render_info:
        # this format is not supported by view
        # TODO: maybe specialize this exception's type
        raise RenderingError(
                'This format ("%s") is not supported by view' % typ
                )

    ctx = RenderContext(context)
    handler_args, handler_kwargs = render_info[typ]
    tmpl = render_hub.get_template(typ, *handler_args, **handler_kwargs)
    return tmpl.render(result, ctx)



# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
