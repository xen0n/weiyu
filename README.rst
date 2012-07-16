weiyu
=====

**weiyu** (**微雨** as in 落花人獨立，微雨燕雙飛/落花人独立，微雨燕双飞), is an experimental modern
BBS mainly written in Python. It is meant to replace the aging KBS BBS backend
used by the `JNRain`_ forum.

.. _JNRain: http://bbs.jnrain.com/

Dependencies
------------

``weiyu`` utilizes non-relational DBMS, at present only MongoDB with the
``pymongo`` wrapper is supported.

The system makes use of message queue, and the preferred MQ provider is
``rabbitmq``.


Architecture
------------

The whole architecture is based on the concept of *reflexes*; that is,
a highly customizable series of transformations that are applied to the
request parameter, most of them protocol-agnostic to facilitate
multi-protocol capability. Currently a WSGI reflex is provided: please see
``examples/`` for the demo app (more are planned).

The system uses a flexible approach to configuration: config files with
preprocessor directives. So far JSON strings and Python pickles are
supported, and a rudimentary implementation of the ``#include`` feature
(\ ``$$include``\ ) is also in place. The configuration is then filled into
*the central registry* inside which singletons live. Most parts of ``weiyu``
can be tweaked solely using configuration: objects (classes, functions, etc)
are assigned names in code, and configuration controls their relationship.
This way things like changing the URLconf or modifying database location
require nothing besides modifying configuration file and restarting server
process. In the future, mechanisms will be added to allow hot-reloading.


.. todo::

    More about the architecture and deployment later after major parts of
    the BBS are finished.


.. vim:ai:et:ts=4:sw=4:sts=4:fenc=utf-8:
