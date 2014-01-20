#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / object-nonrelational mapper / base model
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
        'Document',
        ]

import six

from .. import db_hub
from . import mapper_hub

from ...helpers.metaprogramming import classproperty, classinstancemethod


class MetaDocument(type):
    def __new__(cls, name, bases, attrs):
        new_cls = super(MetaDocument, cls).__new__(cls, name, bases, attrs)

        # first check if we are creating some abstract Document classes
        try:
            if new_cls._abstract_:
                # indeed we are, let it go without a struct_id
                # but make its subclasses require the check by default
                del new_cls._abstract_
                return new_cls
        except AttributeError:
            pass

        # check presence and validity of struct_id
        # because it's defined in Document we don't have to guard against
        # struct_id's absence, as those who manage to delete it are not going
        # anywhere anyway
        new_struct_id = new_cls.struct_id

        if new_struct_id is None:
            raise TypeError('struct_id required for subclasses of Document')

        if not isinstance(new_struct_id, six.text_type):
            raise TypeError(
                    'struct_id must be of type %s' % (repr(six.text_type), )
                    )

        # auto-register struct in mapper_hub if not already done
        mapper_hub.register_struct(new_struct_id)

        return new_cls


@six.add_metaclass(MetaDocument)
class Document(dict):
    # only struct id is needed here, database association is done in
    # configuration file
    struct_id = None

    # for allowing this class itself to exist without a struct_id
    _abstract_ = True

    def __repr__(self):
        return b'<%s: %s>' % (
                self.struct_id,
                super(Document, self).__repr__(),
                )

    @classproperty
    def storage(cls):
        '''Get the driver-specific object for operating the underlying
        storage.

        This should be the collection object ready for operations, provided
        by the database driver.

        '''

        assert cls.struct_id is not None
        return db_hub.get_storage(cls.struct_id)

    @classmethod
    def encoder(cls, version):
        '''Shortcut for registering a encoder for use with the class.

        ``struct_id`` is just the one set in class declaration, you only have
        to pass in the version.

        '''

        return mapper_hub.encoder_for(cls.struct_id, version)

    @classmethod
    def decoder(cls, version):
        '''Shortcut for registering a decoder for use with the class.

        ``struct_id`` is just the one set in class declaration, you only have
        to pass in the version.

        '''

        return mapper_hub.decoder_for(cls.struct_id, version)

    @classinstancemethod
    def encode(self, cls=None, obj=None, version=None):
        '''Encode the document into a database-ready form.

        This method, and its companion :meth:`decode`, can be invoked both
        as class method and as instance method; if invoked from an instance,
        the parameter ``obj`` is ignored.

        '''

        assert cls.struct_id is not None
        return mapper_hub.encode(cls.struct_id, self or obj, version)

    @classinstancemethod
    def decode(self, cls=None, obj=None, version=None):
        assert cls.struct_id is not None
        return mapper_hub.decode(cls.struct_id, self or obj, version)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
