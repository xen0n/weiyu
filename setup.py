#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division

# distribute and setuptools have merged since setuptools-0.7,
# so no more distribute_setup stuff here.
# Rest of the script should continue to work without modification.
from setuptools import setup
from setuptools import find_packages

from weiyu.__version__ import VERSION_STR


setup(
        name='weiyu',
        version=VERSION_STR.split(' ')[0],  # strip out the possible VCS commit
        description='Yet another Python Web framework, as modular and configurable as possible',
        author='Wang Xuerui',
        author_email='idontknw.wang+pypi@gmail.com',
        license='GPLv3+',
        url='https://github.com/xen0n/weiyu/',
        download_url='https://github.com/xen0n/weiyu/',
        install_requires=('decorator>=3.4.0', 'ply>=3.4', 'PyYAML>=3.10', 'six>=1.3.0', ),
        extras_require={
            'beaker': ['Beaker>=1.6.3', ],
            'mako': ['Mako>=0.7.1', ],
            'mongodb': ['pymongo>=2.2.1', ],
            'riak': ['riak>=2.0.0', ],
            'cherrypy': ['cherrypy>=3.2', ],
            'tornado': ['tornado>=2.4', ],
            'socketio': ['gevent-socketio>=0.3.5-rc2', ],
            'celery': ['celery>3.0', ],
            'memcached': ['python-memcached>=1.48', ],
            'redis': ['redis>=2.7.0', ],
            'hiredis': ['hiredis>=0.1.1', ],
            'ujson': ['ujson>=1.19', ],
            'yaml': [],
            'ghwebhook': ['ipaddr>=2.1.10', ],
            'scss': ['pyScss>=1.1.5', ],
            },
        packages=find_packages(exclude=['examples', 'tests']),
        classifiers=[
            'Development Status :: 2 - Pre-Alpha',
            'Environment :: Web Environment',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.2',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: Implementation :: CPython',
            'Programming Language :: Python :: Implementation :: PyPy',
            'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
            'Topic :: Internet :: WWW/HTTP :: WSGI',
            'Topic :: Software Development :: Libraries :: Application Frameworks',
            'Topic :: Software Development :: Libraries :: Python Modules',
        ],
        )


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
