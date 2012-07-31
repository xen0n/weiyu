#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / auth / role management
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

from ..db.mapper import mapper_hub
from ..db.mapper.base import Document

STRUCT_AUTH_ROLE = 'weiyu.auth.role'


@mapper_hub.decoder_for(STRUCT_AUTH_ROLE, 1)
def role_decoder_v1(obj):
    # {
    #   'n': name, 'd': description,
    #   'c': [cap1, cap2, etc, ], 'x': [deny1, deny2, etc, ],
    # }
    name, desc, caps, deny = obj['n'], obj['d'], obj['c'], obj['x']
    return Role(
            name=name,
            desc=desc,
            caps=caps,
            deny=deny,
            )


@mapper_hub.encoder_for(STRUCT_AUTH_ROLE, 1)
def role_encoder_v1(obj):
    return {
            'n': obj['name'],
            'd': obj['desc'],
            'c': obj['caps'],
            'x': obj['deny'],
            }


class Role(Document):
    '''This class describes a *role* that owns 0 or more *capabilities*.

    The concept "role" is similar to "group", but differs in that one user
    can have multiple "identities", and he/she can choose which role or
    identity to use when he/she decides to perform a certain privileged
    operation. This can reduce mistakes by privileged users.

    '''

    struct_id = STRUCT_AUTH_ROLE


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
