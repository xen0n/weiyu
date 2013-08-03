#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / rendering / package
#
# Copyright (C) 2012-2013 Wang Xuerui <idontknw.wang-at-gmail-dot-com>
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
        'render_hub',
        ]

from ..helpers.hub import BaseHub
from ..helpers.modprober import ModProber
from ..helpers.annotation import get_annotation
from ..registry.classes import UnicodeRegistry

from .exc import RenderingError
from .base import RenderContext

PROBER = ModProber('weiyu.rendering', '%srenderer')


class RenderHub(BaseHub):
    registry_name = 'weiyu.rendering'
    registry_class = UnicodeRegistry
    handlers_key = 'handlers'

    # template thing
    def get_template(self, typ, name=None, *args, **kwargs):
        if typ not in self._handlers:
            # Do delayed loading of renderer module
            PROBER.modprobe(typ)

        # name=None is here so those templateless renderers (like JSON)
        # can be used w/o a dummy parameter
        return self.do_handling(typ, name, *args, **kwargs)

    def render_view(self, renderable_fn, result, context, typ):
        render_info = get_annotation(renderable_fn, 'rendering')

        if typ not in render_info:
            # this format is not supported by view
            # TODO: maybe specialize this exception's type
            raise RenderingError(
                    'This format ("%s") is not supported by view' % typ
                    )

        ctx = RenderContext(context)
        handler_args, handler_kwargs = render_info[typ]
        tmpl = self.get_template(typ, *handler_args, **handler_kwargs)
        return tmpl.render(result, ctx)


render_hub = RenderHub()


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
