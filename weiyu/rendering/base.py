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

u'''
Base classes for rendering
~~~~~~~~~~~~~~~~~~~~~~~~~~

This module provides the basic object rendering infrastructure, with
both pre-rendering and post-rendering hooks.

'''

from __future__ import unicode_literals, division

from .exc import RenderingError

__all__ = ['RenderContext', 'Renderable', ]


class RenderContext(dict):
    '''Render context class.

    Currently this is just another name for ``dict``; may restrict type of
    keys to ``unicode`` only in the future when there is need.

    '''

    pass


def is_render_context(obj):
    return issubclass(type(obj), RenderContext)


class Renderable(object):
    '''Base class for any ``weiyu``-renderable object.

    It supports two distinct sets of pre- and post-rendering hooks.
    The separated sets of hooks seem to be more intuitive than Django's
    middleware system, which actually is what inspired this design.

    The pre-processor or post-processor can be any callable. Pre-processors
    are called with one argument, a ``RenderContext`` instance; its return
    type specifies the action following. A return value of ``None`` just
    makes the system proceed to the next hook (if any); a ``unicode``
    return value causes the actual rendering be skipped and post-processor
    hooks invoked; a return value that is a ``RenderContext`` *replaces*
    the current rendering context. Any other return types would lead to a
    ``RenderingError``. The post-processors work almost the same way; they
    are invoked with two parameters, the first being the newest
    intermediate result of rendering, the second the final render context
    object. Their return values are interpreted in a similar fashion,
    *replacing the whole result string* when the returned value's type is a
    subclass of ``unicode``.

    '''

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
