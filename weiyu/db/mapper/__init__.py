#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / object-nonrelational mapping / package
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
        'mapper_hub',
        ]

from functools import partial
from ...helpers.hub import BaseHub
from ...registry.classes import UnicodeRegistry


OP_DECODE, OP_ENCODE = range(2)
DECODERS_KEY, ENCODERS_KEY = 'decoders', 'encoders'

VERSION_FIELD = 'v'


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

        # curry struct id into our mapper shim
        self.register_handler(name, partial(_mapper_shim_, name=name))

    def decode(self, name, obj, version=None):
        return self.do_handling(name, OP_DECODE, obj, version)

    def encode(self, name, obj, version=None):
        return self.do_handling(name, OP_ENCODE, obj, version)

    def register_decoder(self, name, version):
        # you aren't registering negative versions, huh?
        assert version >= 0

        def _decorator_(fn):
            decoders = self._decoders[name]
            if version in decoders:
                raise ValueError(
                        "decoder for struct id '%s' ver %s already"
                        "exists: %s" % (
                            name,
                            unicode(version),
                            repr(decoders[version]),
                            )
                        )

            decoders[version] = fn
            return fn
        return _decorator_

    def register_encoder(self, name, version):
        assert version >= 0

        def _decorator_(fn):
            # update maxver if necessary
            encoders, maxver = self._encoders[name]
            if version in encoders:
                raise ValueError(
                        "encoder for struct id '%s' ver %s already"
                        "exists: %s" % (
                            name,
                            unicode(version),
                            repr(encoders[version]),
                            )
                        )

            encoders[version] = fn
            if version > maxver:
                self._encoders[name][1] = version

            return fn
        return _decorator_

    def _do_decode(self, name, obj, version):
        decoders = self._decoders[name]

        if version is not None:
            use_version = version
        else:
            try:
                obj_version = obj[VERSION_FIELD]
            except KeyError:
                raise ValueError(
                        'object %s has no version field' % (repr(obj), )
                        )

        try:
            decoder = decoders[use_version]
        except KeyError:
            raise TypeError(
                    "no decoder for struct id '%s' version %s" % (
                        name,
                        unicode(use_version),
                        )
                    )

        return decoder(obj)

    def _do_encode(self, name, obj, version):
        # Always encode in the latest version unless explicitly specified
        encoders, maxver = self._encoders[name]
        use_version = maxver if version is None else version

        try:
            encoder = encoders[use_version]
        except KeyError:
            raise TypeError(
                    "no encoder for struct id '%s' version %s" % (
                        name,
                        unicode(use_version),
                        )
                    )

        result = encoder(obj)
        result[VERSION_FIELD] = maxver
        return result


# Mapper shim
def _mapper_shim_(hub, op, name, obj, version):
    if op == OP_DECODE:
        return hub._do_decode(name, obj, version)
    elif op == OP_ENCODE:
        return hub._do_encode(name, obj, version)
    raise RuntimeError('Impossible codepath!')


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
