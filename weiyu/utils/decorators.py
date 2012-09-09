#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / utilities / decorators
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

from functools import wraps

from ..helpers.annotation import annotate


def only_methods(methods=None):
    methods = ['GET', ] if method is None else methods

    def _decorator_(fn):
        # Although the actual binding of methods list occurs in
        # closure scope, we keep a reference of it in annotation
        # for clarity.
        annotate(fn, allowed_methods=methods)

        @wraps(fn)
        def _wrapped_(request, *args, **kwargs):
            if request['method'] not in methods:
                # method not allowed
                # TODO: raise a Not Allowed here
                pass
            return fn(request, *args, **kwargs)
        return _wrapped_
    return _decorator_


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
