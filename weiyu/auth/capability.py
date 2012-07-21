#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / auth / capability management
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
Capability
----------

'''

from __future__ import unicode_literals, division

from ..db.mapper import mapper_hub


STRUCT_AUTH_CAP = 'weiyu.auth.cap'


@mapper_hub.decoder_for(STRUCT_AUTH_CAP, 1)
def cap_decoder_v1(obj):
    pass


@mapper_hub.encoder_for(STRUCT_AUTH_CAP, 1)
def cap_encoder_v1(obj):
    pass


class Capability(object):
    def __init__(self, name, backend=None):
        self.name, self.backend = name, backend

    def list_users(self):
        return self.backend.


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
