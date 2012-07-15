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
from .exc import RenderError
from .base import RenderContext


def render_view_func(renderable_fn, context, acceptable_formats):
    render_info = renderable_fn._weiyu_rendering_

    for fmt in acceptable_formats:
        if fmt not in render_info:
            # this format is not supported by view, skip it
            continue

        # decide to render in this format
        ctx = RenderContext(context)
        handler_args, handler_kwargs = render_info[fmt]
        tmpl = render_hub.get_template(fmt, *handler_args, **handler_kwargs)
        return tmpl.render(ctx)

    # TODO: maybe specialize this exception's type
    raise RenderError('No acceptable format is supported by view')


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
