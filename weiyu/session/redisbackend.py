#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / session handling / Redis-based sessions
#
# Copyright (C) 2013 Wang Xuerui <idontknw.wang-at-gmail-dot-com>
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
        'RedisSessionObject',
        'RedisSession',
        ]

import time
import uuid

import six
import redis

# I don't feel like reinventing the wheel, so...
import Cookie

from beaker.session import SignedCookie

from ..db import db_hub
from . import session_hub


def _generate_sessid():
    return uuid.uuid4().hex


class RedisSessionObject(dict):
    def __init__(
            self,
            sid,
            id=None,
            cookiehdr=None,
            key=None,
            secret=None,
            ttl=None,
            ):
        self.sid = sid
        self.id, self.key, self.secret, self.ttl = id, key, secret, ttl
        self.cookiehdr = cookiehdr
        self.cookie, self._do_set_cookie = None, False

        # first get the appropriate key for db object, generating one if
        # the session is new.
        if cookiehdr is not None:
            # session ID stored in cookie. the code below is again taken
            # from beaker
            if secret is not None:
                try:
                    cookie = SignedCookie(secret, input=cookiehdr)
                except Cookie.CookieError:
                    cookie = SignedCookie(secret, input=None)
            else:
                cookie = Cookie.SimpleCookie(input=cookiehdr)

            if self.id is None and key in cookie:
                self.id = cookie[key].value

            self.cookie = cookie

        if self.id is None:
            # Generate a new ID, and (indirectly) instruct the session
            # middleware to Set-Cookie.
            self.new_id()

        self._drv = db_hub.get_storage(sid)
        # Unlike Beaker, which deals with a file backend without automatic
        # expiration of entries, we don't have to do all that ourselves.
        # Just making sure an EXPIRE is issued for (theoretically) each
        # operation would be enough...
        #
        # if only all the keys are pre-existing. Actually, hashes are
        # created only when they are written to, so we have no choice but
        # to also force an EXPIRE every time a write is issued.
        with self._drv as conn:
            if conn.exists(self.id):
                conn.expire(self.id, self.ttl)
            else:
                self.new_id()

    # helper methods
    def new_id(self):
        old_id = self.id
        self.id, self._do_set_cookie = _generate_sessid(), True

        # migrate the session in DB
        if old_id is not None:
            with self._drv as conn:
                old_content = conn.hgetall(old_id)

                # A hash cannot be empty in Redis, so if it indeed is
                # empty it must not exist.
                if old_content:
                    # the probability of UUID conflicts is ~0,
                    # so why do we have to say while True here?
                    result = False
                    for i in xrange(4):
                        try:
                            result = conn.renamenx(old_id, self.id)
                            if result:
                                # rename successful
                                break
                            # rename failed because target key exists
                            self.id = _generate_sessid()
                        except redis.exceptions.ResponseError:
                            # rename failed because source and destination
                            # are the SAME... or because the source has
                            # VANISHED in operation!
                            self.id = _generate_sessid()

                            if not conn.exists(old_id):
                                # well, the session expired during <<1ms of
                                # execution.
                                # Lucky we have old_content... Just assign it
                                # to self.id. Another edge case is that the
                                # newly-generated id happens to conflict with
                                # something else... Oh well. Let's not go that
                                # far.
                                conn.hmset(self.id, old_content)
                                result = True
                                break

                    if not result:
                        # That many *UUID conflicts* ?
                        # Better go buy some lotteries...
                        raise RuntimeError('Session UUID conflicts!')

        self.set_cookie_prop()

    def _full_refresh(self):
        s = super(RedisSessionObject, self)

        # Single-direction sync from redis.
        # In the rare case of incorrect object type (should never be the
        # case if this code is the only one accessing that db), data stored
        # in the Python dict will be dropped, then the exception is
        # re-raised.
        with self._drv as conn:
            try:
                new_self = conn.hgetall(self.id)
            except redis.exceptions.ResponseError:
                s.clear()
                raise

        s.clear()
        s.update(new_self)

    def __repr__(self):
        return b'RedisSessionObject(%s)' % (
                super(RedisSessionObject, self).__repr__(),
                )

    # Cookie operations
    def set_cookie_prop(self, expires=None, domain=None, path='/'):
        self.cookie[self.key] = self.id
        entry = self.cookie[self.key]

        entry['path'] = path
        if domain is not None:
            entry['domain'] = domain

        if expires is not None:
            # NOTE: assume it's in seconds for the moment
            expire_time = time.gmtime(int(time.time()) + expires)
            expire_str = time.strftime(
                    '%a, %d-%b-%Y %H:%M:%S GMT',
                    expire_time,
                    )
            entry['expires'] = expire_str

        self._do_set_cookie = True

    def generate_cookie_header(self):
        if not self._do_set_cookie:
            # the cookie doesn't want to be refreshed
            return False, ''

        return True, self.cookie[self.key].output(header='')

    # wrappers around the dict interface
    # Operations on non-existent hashes either return None or [], so we
    # don't have to care about the hash's existence. Instead we can make
    # something that wraps Redis in a *really* thin manner...
    def __len__(self):
        with self._drv as conn:
            return conn.hlen(self.id)

    def __iter__(self):
        self._full_refresh()
        return super(RedisSessionObject, self).__iter__()

    def __getitem__(self, key):
        # Fetch the key from db.
        # The reason for not caching queried fields, is possible race
        # conditions with another client which attempts to update the same
        # session, and code complexity.
        # Also, redis makes the overhead relatively bearable, so hopefully
        # performance bottleneck would not occur here.
        with self._drv as conn:
            value = conn.hget(self.id, key)

        super(RedisSessionObject, self).__setitem__(key, value)
        return value

    def __setitem__(self, key, value):
        with self._drv as conn:
            conn.hset(self.id, key, value)
            conn.expire(self.id, self.ttl)

        super(RedisSessionObject, self).__setitem__(key, value)

    def __delitem__(self, key):
        with self._drv as conn:
            conn.hdel(self.id, key)
            conn.expire(self.id, self.ttl)

        try:
            super(RedisSessionObject, self).__delitem__(key)
        except KeyError:
            pass

    def __contains__(self, key):
        with self._drv as conn:
            existence = conn.hexists(self.id, key)
            if not existence:
                try:
                    super(RedisSessionObject, self).__delitem__(key)
                except KeyError:
                    pass

            return existence

    def clear(self):
        with self._drv as conn:
            conn.delete(self.id)

        super(RedisSessionObject, self).clear()

    def get(self, key, default=None):
        return self[key] if key in self else default

    def keys(self):
        # Not HKEYS, but forces a full refresh.
        self._full_refresh()
        return six.iterkeys(super(RedisSessionObject, self))

    def iterkeys(self):
        return self.keys()

    def values(self):
        # Not HVALS, but forces a full refresh.
        self._full_refresh()
        return six.itervalues(super(RedisSessionObject, self))

    def itervalues(self):
        return self.values()

    def items(self):
        self._full_refresh()
        return six.iteritems(super(RedisSessionObject, self))

    def iteritems(self):
        return self.items()

    def setdefault(self, key, default=None):
        with self._drv as conn:
            ret = conn.hsetnx(self.id, key, default)
            conn.expire(self.id, self.ttl)
            if not ret:
                # key already exists
                value = conn.hget(self.id, key)
                super(RedisSessionObject, self).__setitem__(key, value)
                return value

            super(RedisSessionObject, self).__setitem__(key, default)
            return default

    def update(self, obj, **kwargs):
        upd_dict = obj if hasattr(obj, 'keys') else dict(obj)
        upd_dict.update(kwargs)
        with self._drv as conn:
            conn.hmset(self.id, upd_dict)
            conn.expire(self.id, self.ttl)

        super(RedisSessionObject, self).update(upd_dict)

    # useful atomic operations
    def hincrby(self, key, incr=1):
        with self._drv as conn:
            newval = conn.hincrby(self.id, key, incr)
            conn.expire(self.id, self.ttl)
            super(RedisSessionObject, self).__setitem__(key, newval)
            return newval


class RedisSession(object):
    def __init__(self, options=None):
        self.sid = options['struct_id']
        self.key = options['cookie-key']
        self.ttl = options['ttl']
        self.secret = options.get('secret', None)

    def preprocess(self, request):
        request.session = RedisSessionObject(
                self.sid,
                None,
                request.env.get('HTTP_COOKIE', ''),
                self.key,
                self.secret,
                self.ttl,
                )

    def postprocess(self, response):
        request = response.request
        ctx = response.context
        session = request.session

        set_cookie, cookiehdr = session.generate_cookie_header()
        if set_cookie:
            if cookiehdr:
                # append the cookie to response
                new_cookies = ctx.get('cookies', [])
                new_cookies.append(cookiehdr)
                ctx['cookies'] = new_cookies

        return response


@session_hub.register_handler('redis')
def redis_session_handler(hub, options=None):
    return RedisSession(options)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
