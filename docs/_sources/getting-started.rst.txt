===============
Getting Started
===============

Welcome! This tutorial highlights the basics of the features added by the ``FabricPlus`` library;
for more information on the base ``Fabric`` library itself, please see the `Fabric documentation <http://docs.fabfile.org/en/latest/>`_.

This tutorial assumes you are already familiar with the ``Fabric`` library and its usage.

A Note About Imports
--------------------

``FabricPlus``, and in turn, it's ``ConnectionPlus`` object, inherits and imports directly from the ``Fabric`` library.

It also imports and modifies some things from the ``paramiko`` library.

The expected use case for this library is simply to import the ``ConnectionPlus`` object, and use that directly.

But you may want to modify the behavior of underlying objects, or use them directly.

In this case, importing and using objects from ``paramiko``, or ``invoke``, just as in the base ``Fabric`` library, is still possible.

Installation
------------

As of ``FabricPlus`` version 0.1.0, the library is available on PyPI at the `FabricPlus Project Page <https://pypi.org/project/fabricplus/>`_.

To install ``FabricPlus``, simply run:

.. code-block:: bash

    pip install fabricplus

Or, if you prefer to install from source (requires ``poetry``):

.. code-block:: bash

    # Clone the repository
    git clone https://github.com/prokopto-dev/fabric-plus.git
    # Go into the directory
    cd fabric-plus
    # Run the poetry build command
    poetry build
    # Install the newly built wheel file
    pip install dist/fabricplus-0.1.0-py3-none-any.whl

.. note::

    The version number may change, so be sure to check the version number of the wheel file you build.

Using ``ConnectionPlus`` As A Drop-In Replacement for ``Fabric``'s ``Connection``
---------------------------------------------------------------------------------

The ``ConnectionPlus`` object inherits nearly everything from the parent ``Connection`` class.
