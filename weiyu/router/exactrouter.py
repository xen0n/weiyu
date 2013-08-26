#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / router / exact-matching router
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
            'ExactRouterTarget',
            'ExactRouter',
            ]

import re

from ..helpers.misc import smartstr
from . import router_hub
from .base import *


class ExactRouterTarget(RouterTargetBase):
    '''
    This target cannot extract any arguments from query strings; useful
    when a large tree of, say, API endpoints are to be exposed, and the
    parameters are not passed through the query string. It's supposed
    to be faster than regex-based lookups in such static cases.

    .. note::
        No separator is automatically removed from the matched query
        string for nested lookups; you should specify the separator such
        as '/' yourself in the target pattern.

    '''

    def __init__(self, pattern, target, extra_data=None, router=None):
        super(ExactRouterTarget, self).__init__(target, extra_data, router)

        self.pattern = smartstr(pattern)
        self._pat_len = len(self.pattern)

    def check(self, querystr, prev_args, prev_kwargs):
        match = querystr.startswith(self.pattern)

        if not match:
            return (STATUS_NOROUTE, None, None, None, )

        # support for nested routing
        if not self.target_is_router:
            return (STATUS_REACHED, prev_args, prev_kwargs, None, )

        # target is router, forward
        # since the RE matches at the beginning, safely assume its span()
        # starts at 0.
        # now, extract the substring for further routing...
        new_qs = querystr[self._pat_len:]

        # and indicate this status.
        return (STATUS_FORWARD, prev_args, prev_kwargs, new_qs, )

    def _get_reverse_pattern(self):
        return (self.pattern, set(), )


@router_hub.register_router_class('exact')
class ExactRouter(RouterBase):
    target_type = ExactRouterTarget


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
