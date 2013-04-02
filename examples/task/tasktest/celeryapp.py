#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / examples / Task queue integration - Celery file
#
# This file is in public domain.

from __future__ import unicode_literals, division

from weiyu.shortcuts import load_config
from weiyu.tasks import task_hub

load_config('conf.json')
celery = task_hub.get_app('tasktest')


if __name__ == '__main__':
    celery.start()


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
