#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / helpers / generic call reflector
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

__all__ = ['CallReflector', ]


class CallReflector(object):
    '''Lookup syntax transformer.

    This class converts the syntax of form ``object.a.b.func(*args, **kwargs)``
    into ``reflector.func(pathbase.a.b, *args, **kwargs)``. Meant to be used
    with subclasses of ``PathBuilderBase`` (defined in ``pathbuilder.py``).

    '''

    def __init__(self, target, path_type):
        self.__target = target
        self.path_type = path_type

    def __getattr__(self, att):
        def _reflector_(path_obj, *args, **kwargs):
            if not issubclass(type(path_obj), self.path_type):
                raise ValueError(u'path object type mismatch')

            real_target = self.__target.__getattr__(unicode(path_obj))
            real_att_unbound = real_target.__class__.__dict__[att]

            if not hasattr(real_att_unbound, '__call__'):
                raise AttributeError(u"'%s' attribute is not callable" % att)

            return real_att_unbound(real_target, *args, **kwargs)

        return _reflector_


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
