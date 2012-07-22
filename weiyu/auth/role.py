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


STRUCT_AUTH_ROLE = 'weiyu.auth.role'

CAPS_KEY = 'c'


@mapper_hub.decoder_for(STRUCT_AUTH_ROLE, 1)
def role_decoder_v1(obj):
    caps = obj[CAPS_KEY]
    return Role(obj)


@mapper_hub.encoder_for(STRUCT_AUTH_ROLE, 1)
def role_encoder_v1(obj):
    caps = obj.capabilities
    return {CAPS_KEY: caps, }


class Role(object):
    '''This class describes a *role* that owns 0 or more *capabilities*.

    The concept "role" is similar to "group", but differs in that one user
    can have multiple "identities", and he/she can choose which role or
    identity to use when he/she decides to perform a certain privileged
    operation. This can reduce mistakes by privileged users.

    '''

    def __init__(self, backend):
        self.backend = backend

    def has_caps(self, caps):
        # TODO: self.backend.check, also to use Django's Q object-like
        # helpers I hope...
        pass


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
