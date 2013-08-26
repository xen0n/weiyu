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

'''
Base classes for rendering
~~~~~~~~~~~~~~~~~~~~~~~~~~

This module provides the basic object rendering infrastructure, with
both pre-rendering and post-rendering hooks.

'''

from __future__ import unicode_literals, division

__all__ = ['RenderContext', 'Renderable', ]

import six

from .exc import RenderingError


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
    are called with the result object and a ``RenderContext`` instance, and
    are expected to return a tuple ``(proceed, new_result, new_context, )``.
    If  ``proceed == False``, the actual rendering will be skipped and
    post-processor hooks will be invoked. The rendering result will be set
    to ``new_result`` in this case.

    The post-processors work almost the same way; they
    are invoked with two parameters, the first being the newest
    intermediate result of rendering, the second the final render context
    object. Their return values are interpreted in a similar fashion,
    *replacing the whole result string* when the returned value's type is a
    subclass of ``unicode``.

    '''

    def __init__(self, pre_hooks=None, post_hooks=None):
        self.pre_hooks = pre_hooks if pre_hooks is not None else []
        self.post_hooks = post_hooks if post_hooks is not None else []

    def _do_render(self, result, context):
        raise NotImplementedError

    def render(self, result=None, context=None):
        result = {} if result is None else result
        context = RenderContext() if context is None else context

        if not is_render_context(context):
            raise RenderingError(
                    'class of context must be subclass of RenderContext'
                    )

        skip_render, rendered = False, None
        cooked_result, cooked_ctx = result, context

        # Execute the preprocess hooks.
        for hook in self.pre_hooks:
            proceed, new_result, new_ctx = hook(cooked_result, cooked_ctx)

            # context
            if not is_render_context(new_ctx):
                raise RenderingError(
                        'new context not subclass of RenderContext'
                        )

            # update the result and context
            cooked_result, cooked_ctx = new_result, new_ctx

            # skip rendering?
            if not proceed:
                skip_render, rendered = True, cooked_result
                break

        # do the actual render if none of the preprocess hooks demanded early
        # return
        if not skip_render:
            rendered = self._do_render(cooked_result, cooked_ctx)

        # Execute the postprocess hooks, w/ the result string and context.
        for hook in self.post_hooks:
            new_rendered = hook(rendered, cooked_ctx)

            if new_rendered is None:
                # skip to the next one
                continue
            elif issubclass(type(new_rendered), six.text_type):
                # update (replace) rendered string
                rendered = new_rendered
            else:
                raise RenderingError(
                        "invalid post-process hook return type: got '%s'"
                        % str(type(new_rendered))
                        )

        return rendered


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
