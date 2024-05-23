.. image:: https://img.shields.io/pypi/v/fabricplus
   :alt: PyPI - Version
.. image:: https://img.shields.io/pypi/pyversions/fabricplus
   :alt: PyPI - Python Version
.. image:: https://img.shields.io/pypi/l/fabricplus
   :alt: PyPI - License

Welcome to FabricPlus's documentation!
======================================

This site covers FabricPlus's usage and API documentation.

It also serves as the main website for FabricPlus

If you are not familiar with ``Fabric``, the first thing you should do is visit the main `Fabric website <http://www.fabfile.org/>`_.

If you are not familiar with the underlying behavior of ``Fabric``, then you should read the `Fabric documentation <http://docs.fabfile.org/en/latest/>`_.

What is FabricPlus?
-------------------

FabricPlus is a wrapper around several Fabric sourced objects to provide new functionality not currently a part of the main Fabric library.  This includes:

- ``ConnectionPlus`` object that wraps the ``Connection`` object from Fabric and extends it with:
  
  - Built-in support for ``jumphost`` (a.k.a. ``bastion``) connectivity with ``MFA`` / ``2FA`` support  via `paramiko-jump <https://github.com/andrewschenck/paramiko-jump>`_.
  - Built-in support for ``scp`` protocol transfer via the ``ssh`` connection, via `scp.py <https://github.com/jbardin/scp.py>_`.
  - Added support for ``su`` command execution via the ``Connection`` object for user switching, instead of needing to use ``sudo``.

- ``TransferPlus`` object that wraps the ``Transfer`` object from Fabric and extends it with:
  
  - Built-in support for ``scp`` protocol transfer via the ``ssh`` transport used by the parent ``Connection``.

.. _getting_started:

Getting Started
---------------

.. toctree::
    :maxdepth: 2

    getting-started

.. _contributing:

Concurrency
-----------

If you'd like a little information on how to run Connections in parallel, here's a small doc with some notes.

.. toctree::
    :maxdepth: 2

    parallelism

Contributing
------------

Interested in contributing to FabricPlus?  Great!  We have a guide for that!

.. toctree::
    :maxdepth: 2

    contributing

.. _api-docs:

API
---

Just here to figure out how the API works?

.. toctree::
    :maxdepth: 1
    :glob:
    :caption: API Documentation

    api/*


.. _contact:

Contact
-------

If you need to get in touch about a bug, issue in the docs, or clarification, see the page below!

.. toctree::
    :maxdepth: 2

    contact
