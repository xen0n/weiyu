#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / examples / Working with Celery - Celery file
#
# This file is in public domain.

from __future__ import absolute_import, unicode_literals, division

import os

from celery import Celery

from weiyu.init import load_config

_project_root = os.path.join(os.path.dirname(__file__), '..')
os.chdir(_project_root)
load_config('Rainfile.yml')

celery = Celery(
        'tasktest',
        broker='amqp://test:test@localhost:5672/test_vhost',
        backend='amqp://test:test@localhost:5672/test_vhost',
        include=['tasktest.tasks', ],
        )


if __name__ == '__main__':
    celery.start()


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
