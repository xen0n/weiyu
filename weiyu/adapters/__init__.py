#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / adapter / package
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
        'adapter_hub',
        ]

from ..helpers.hub import BaseHub
from ..registry.classes import UnicodeRegistry

ADAPTERS_KEY = 'adapters'


class AdapterHub(BaseHub):
    registry_name = 'weiyu.adapter'
    registry_class = UnicodeRegistry
    handlers_key = ADAPTERS_KEY

    def __init__(self):
        super(AdapterHub, self).__init__()

    def make_app(self, adapter):
        return self.do_handling(adapter)


adapter_hub = AdapterHub()


# Force loading of adapters
from . import _reg
del _reg


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
