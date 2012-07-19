#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / object-nonrelational mapper / base model
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

from .. import db_hub
from . import mapper_hub


class Document(dict):
    struct_id = None
    db_name = None
    collection = None

    def __getattr__(self, k):
        if k in self:
            # XXX This can override member methods!!
            return self[k]
        return super(Document, self).__getattr__(k)

    def __setattr__(self, k, v):
        self[k] = v


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
