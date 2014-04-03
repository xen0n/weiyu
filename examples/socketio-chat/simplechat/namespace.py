#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / examples / simple Socket.IO chat - chat namespace

from __future__ import unicode_literals

from socketio.namespace import BaseNamespace
from socketio.mixins import RoomsMixin, BroadcastMixin

from weiyu.async import async_hub
from weiyu import registry


@async_hub.register_ns('socketio', '')
class ChatNamespace(BaseNamespace, RoomsMixin, BroadcastMixin):
    def _get_nickname_list(self):
        reg = registry.request(
                'chat',
                nodup=False,
                autocreate=True,
                )

        if 'nicknames' not in reg:
            reg['nicknames'] = []

        return reg['nicknames']

    def on_nickname(self, nickname):
        self._get_nickname_list().append(nickname)
        self.socket.session['nickname'] = nickname
        self.broadcast_event('announcement', '%s has connected' % nickname)
        self.broadcast_event('nicknames', self._get_nickname_list())
        # Just have them join a default-named room
        self.join('main_room')

    def recv_disconnect(self):
        # Remove nickname from the list.
        nickname = self.socket.session['nickname']
        self._get_nickname_list().remove(nickname)
        self.broadcast_event('announcement', '%s has disconnected' % nickname)
        self.broadcast_event('nicknames', self._get_nickname_list())

        self.disconnect(silent=True)

    def on_user_message(self, msg):
        self.emit_to_room('main_room', 'msg_to_room',
            self.socket.session['nickname'], msg)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
