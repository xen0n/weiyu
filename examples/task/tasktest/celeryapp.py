#!/usr/bin/env python
# -*- coding: utf-8 -*-
# weiyu / examples / Task queue integration - Celery file
#
# This file is in public domain.

from __future__ import unicode_literals, division

from weiyu.registry.loader import JSONConfig
from weiyu.tasks import task_hub

# load up registries
conf = JSONConfig('conf.json')
conf.populate_central_regs()

celery = task_hub.get_app('tasktest')


if __name__ == '__main__':
    celery.start()


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
