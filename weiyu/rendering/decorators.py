#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / rendering / decorator
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
Decorator interface
~~~~~~~~~~~~~~~~~~~

'''

from __future__ import unicode_literals, division

__all__ = [
        'renderable',
        ]

import six

from ..helpers.annotation import annotate, get_annotation


def renderable(handler, *args, **kwargs):
    '''Marks an object as "renderable" by a certain handler, recording the
    render handler and associated instantiation parameter(s) in the object's
    attribute.

    :param handler: Name of the render handler.

    .. warning::

        The attribute used to store rendering information is currently
        ``_weiyu_rendering_``; this is an *implementation detail*\ .
        **Never** touch it outside the rendering engine proper as the exact
        detail of rendering attribute can be possibly radically different
        across versions.

    '''

    handler = six.text_type(handler)

    def _decorator_(thing):
        try:
            render_info = get_annotation(thing, 'rendering')
        except AttributeError:
            render_info = {}
        except KeyError:
            render_info = {}

        render_info[handler] = (args, kwargs, )

        annotate(thing, rendering=render_info)
        return thing
    return _decorator_


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
