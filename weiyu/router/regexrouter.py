#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / router / regex based router
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
            'RegexRouterTarget',
            'RegexRouter',
            ]

import re

from ..helpers.misc import smartstr
from ..helpers.regex_helper import normalize

from . import router_hub
from .base import *


def args_from_match(match, named_groups):
    kwargs = match.groupdict()
    args = [i for idx, i in enumerate(match.groups())
            if idx not in named_groups
            ]
    return (args, kwargs, )


class RegexRouterTarget(RouterTargetBase):
    # __slots__ = ['name', 'pattern', 'target', '_namedgrps', ]

    def __init__(self, pattern, target, extra_data=None, router=None):
        super(RegexRouterTarget, self).__init__(target, extra_data, router)

        self.pattern = re.compile(smartstr(pattern))
        self._namedgrps = [i - 1 for i in self.pattern.groupindex.values()]

    def check(self, querystr, prev_args, prev_kwargs):
        match = self.pattern.match(smartstr(querystr))

        if not match:
            return (STATUS_NOROUTE, None, None, None, )

        curr_args, curr_kwargs = args_from_match(match, self._namedgrps)

        # update the previous context
        args = prev_args[:]
        args.extend(curr_args)

        kwargs = prev_kwargs.copy()
        kwargs.update(curr_kwargs)

        # support for nested routing
        if not self.target_is_router:
            return (STATUS_REACHED, args, kwargs, None, )

        # target is router, forward
        # since the RE matches at the beginning, safely assume its span()
        # starts at 0.
        # now, extract the substring for further routing...
        new_qs = querystr[match.span()[1]:]

        # and indicate this status.
        return (STATUS_FORWARD, args, kwargs, new_qs, )

    def _get_reverse_pattern(self):
        # self.pattern is a compiled pattern
        pat = normalize(self.pattern.pattern)
        assert len(pat) == 1
        pat_str, pat_vars = pat[0]
        return (pat_str, set(pat_vars), )


@router_hub.register_router_class('regex')
class RegexRouter(RouterBase):
    target_type = RegexRouterTarget


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
