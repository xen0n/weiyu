#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / object-nonrelational mapping / package
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
        'mapper_hub',
        ]

from functools import partial

import six

from .. import db_hub
from ...helpers.hub import BaseHub
from ...registry.classes import UnicodeRegistry


DECODERS_KEY, ENCODERS_KEY = 'decoders', 'encoders'

# don't conflict w/ single-letter props to reduce number of surprises...
VERSION_FIELD = '_V'


class MapperHub(BaseHub):
    registry_name = 'weiyu.db.mapper'
    registry_class = UnicodeRegistry
    handlers_key = 'shims'

    def __init__(self):
        super(MapperHub, self).__init__()

        self._decoders = self._reg[DECODERS_KEY] = {}
        self._encoders = self._reg[ENCODERS_KEY] = {}

    def register_struct(self, name):
        if name not in self._decoders:
            self._decoders[name] = {}

        if name not in self._encoders:
            # [{ver1: encoder1, ver2: encoder2, ...}, max_version]
            self._encoders[name] = [{}, -1]

    def get_version(self, obj):
        try:
            return obj[VERSION_FIELD]
        except KeyError:
            raise TypeError(
                        'object %s has no version field' % (repr(obj), )
                        )

    def decoder_for(self, name, version):
        # you aren't registering negative versions, huh?
        assert version >= 0

        def _decorator_(fn):
            decoders = self._decoders[name]
            if version in decoders:
                raise ValueError(
                        "decoder for struct id '%s' ver %s already"
                        "exists: %s" % (
                            name,
                            six.text_type(version),
                            repr(decoders[version]),
                            )
                        )

            decoders[version] = fn
            return fn
        return _decorator_

    def encoder_for(self, name, version):
        assert version >= 0

        def _decorator_(fn):
            # update maxver if necessary
            encoders, maxver = self._encoders[name]
            if version in encoders:
                raise ValueError(
                        "encoder for struct id '%s' ver %s already"
                        "exists: %s" % (
                            name,
                            six.text_type(version),
                            repr(encoders[version]),
                            )
                        )

            encoders[version] = fn
            if version > maxver:
                self._encoders[name][1] = version

            return fn
        return _decorator_

    def decode(self, name, obj, version=None):
        decoders = self._decoders[name]

        use_ver = version if version is not None else self.get_version(obj)

        try:
            decoder = decoders[use_ver]
        except KeyError:
            raise TypeError(
                    "no decoder for struct id '%s' version %s" % (
                        name,
                        six.text_type(use_ver),
                        )
                    )

        return decoder(obj)

    def encode(self, name, obj, version=None):
        # Always encode in the latest version unless explicitly specified
        encoders, maxver = self._encoders[name]
        use_ver = maxver if version is None else version

        try:
            encoder = encoders[use_ver]
        except KeyError:
            raise TypeError(
                    "no encoder for struct id '%s' version %s" % (
                        name,
                        six.text_type(use_ver),
                        )
                    )

        result = encoder(obj)
        result[VERSION_FIELD] = maxver
        return result


mapper_hub = MapperHub()


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
