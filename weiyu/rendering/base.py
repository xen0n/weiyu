#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / rendering / base operations
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

from .exc import RenderingError

__all__ = ['RenderContext', 'Renderable', ]


class RenderContext(dict):
    pass


def is_render_context(obj):
    return issubclass(type(obj), RenderContext)


class Renderable(object):
    def __init__(self, pre_hooks=None, post_hooks=None):
        self.pre_hooks = pre_hooks if pre_hooks is not None else []
        self.post_hooks = post_hooks if post_hooks is not None else []

    def _do_render(self, context):
        raise NotImplementedError

    def render(self, context=None):
        if context is None:
            context = RenderContext()

        if not is_render_context(context):
            raise RenderingError(
                    u'class of context must be subclass of RenderContext'
                    )

        real_context, result = context, None

        # Execute the preprocess hooks.
        for hook in self.pre_hooks:
            newly_cooked = hook(real_context)

            if newly_cooked is None:
                # do nothing, proceed to the next hook
                continue
            elif is_render_context(newly_cooked):
                # update the context
                real_context = newly_cooked
            elif issubclass(type(newly_cooked), unicode):
                # bypass the actual rendering
                result = newly_cooked
            else:
                raise RenderingError(
                        u"invalid pre-process hook return type: got '%s'"
                        % str(type(newly_cooked))
                        )

        # do the actual render if none of the preprocess hooks demanded early
        # return
        if result is None:
            result = self._do_render(real_context)

        # Execute the postprocess hooks, w/ the result string and context.
        for hook in self.post_hooks:
            new_result = hook(result, real_context)
            
            if new_result is None:
                # skip to the next one
                continue
            elif issubclass(type(new_result), unicode):
                # update (replace) result string
                result = new_result
            else:
                raise RenderingError(
                        u"invalid post-process hook return type: got '%s'"
                        % str(type(new_result))
                        )

        return result


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
