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

from .base import RouterTargetBase, RouterBase


def args_from_match(match, named_groups):
    kwargs = match.groupdict()
    args = tuple(i for idx, i in enumerate(match.groups())
                 if idx not in named_groups
                 )
    return (args, kwargs, )


class RegexRouterTarget(RouterTargetBase):
    # __slots__ = ['name', 'pattern', 'target', '_namedgrps', ]

    def __init__(self, name, pattern, target):
        super(RegexRouterTarget, self).__init__(name, target)

        self.pattern = re.compile(unicode(pattern))
        self._namedgrps = [i - 1 for i in self.pattern.groupindex.values()]

    def check(self, querystr):
        match = self.pattern.match(unicode(querystr))

        if not match:
            return (False, None, None, )

        args, kwargs = args_from_match(match, self._namedgrps)
        return (True, args, kwargs, )


class RegexRouter(RouterBase):
    target = RegexRouterTarget


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
