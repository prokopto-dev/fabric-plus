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

