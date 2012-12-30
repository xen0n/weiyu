weiyu
=====

**weiyu** is yet another lightweight `Python`_ web framework that is highly
modular and configurable. On top of the framework is **luohua**, an
experimental modern BBS. The two are developed to replace the aging
`KBS BBS`_ backend used by the `JNRain`_ forum.

.. _Python: http://python.org/
.. _KBS BBS: http://dev.kcn.cn/
.. _JNRain: http://bbs.jnrain.com/

Community
---------

* Mailing list
    * weiyu-cn at groups.google.com (Main language: Chinese)


Why the name?
-------------

The two names come from *Lin Jiang Xian* (trad: 臨江仙/simp: 临江仙) by Yan
Jidao, a poet of the Song dynasty. The referenced sentence is
“去年春恨卻來時，落花人獨立，微雨燕雙飛”.


Dependencies
------------

The simple way:

    $ pip install -r requirements.txt

Or the more detailed description:

``weiyu`` utilizes non-relational DBMS, at present only `MongoDB`_ with the
`pymongo`_ wrapper is supported.

.. _MongoDB: http://www.mongodb.org/
.. _pymongo: http://api.mongodb.org/python/current/


The only session backend implemented so far is a wrapper around `Beaker`_.

.. _Beaker: http://beaker.groovie.org/

`Mako templating system`_ is used in one of the renderers, be sure to
install it for all your textual data rendering.

.. _Mako templating system: http://www.makotemplates.org/

The routing module features a micro-language specifically designed for
describing routing rules, and for the parser part `ply`_ is needed.

.. _ply: http://www.dabeaz.com/ply/

The system is planned to make use of message queue, and the preferred MQ
provider is `RabbitMQ`_. `Celery`_ will be required together to provide
task delegation in a future version.

.. _RabbitMQ: http://www.rabbitmq.com/
.. _Celery: http://celeryproject.org/


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
