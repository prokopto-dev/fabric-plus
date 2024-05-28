.. image:: https://img.shields.io/pypi/v/fabricplus
   :alt: PyPI - Version
   :target: https://pypi.org/project/fabricplus/
.. image:: https://img.shields.io/github/actions/workflow/status/prokopto-dev/fabric-plus/testing.yml?logo=github&label=testing
   :alt: GitHub Actions Workflow Status
   :target: https://github.com/prokopto-dev/fabric-plus/actions/
.. image:: https://img.shields.io/pypi/pyversions/fabricplus
   :alt: PyPI - Python Version
   :target: https://pypi.org/project/fabricplus/
.. image:: https://img.shields.io/pypi/l/fabricplus
   :alt: PyPI - License
   :target: https://pypi.org/project/fabricplus/
.. image:: https://img.shields.io/badge/GitHub-FabricPlus-blue?style=flat&logo=github&link=https%3A%2F%2Fgithub.com%2Fprokopto-dev%2Ffabric-plus
   :alt: Static Badge
   :target: https://github.com/prokopto-dev/fabric-plus

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
  - Built-in support for ``scp`` protocol transfer via the ``ssh`` connection, via `scp.py <https://github.com/jbardin/scp.py>`_.
  - Added support for ``su`` command execution via the ``Connection`` object for user switching, instead of needing to use ``sudo``.

- ``TransferPlus`` object that wraps the ``Transfer`` object from Fabric and extends it with:
  
  - Built-in support for ``scp`` protocol transfer via the ``ssh`` transport used by the parent ``Connection``.

.. _quickstart:

Quickstart
----------

If you're looking to get started quickly, here's a brief set of examples for usage. Otherwise, read the "Getting Started" section below.

.. code-block:: python3

    # importing as Connection
    from fabricplus.connection import ConnectionPlus as Connection

    # Creating a basic connection
    conn_1: Connection = Connection("host1.example.com")

    # Creating a jumphost connection, and then a host connection via that jumphost
    jumphost_1: Connection = Connection("jumphost.example.com")
    conn_via_jh: Connection = Connection("host2.example.com", jump_target=jumphost_1)

    # Creating a host that uses SCP for transfers by default
    conn_2: Connection("host3.example.com", scp=True)

    # Running a get via SCP on the host1/conn_1, which doesn't use SCP by default
    conn_1.get("/path/to/some/remote/file", scp=True)

    # Running a command as some other user via su
    conn_1.su("date", user="someotheruser", password="someuserspasswd")

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
