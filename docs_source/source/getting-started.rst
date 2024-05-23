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
-------------------------------------------------------------------------------------


Create A Basic Connection As A Drop In Replacement
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you want to create a connection, it is nearly identical to ``Fabric`` itself.

The only difference is if you want the drop-in replacement, you'll need to import the ``ConnectionPlus`` object as a ``Connection``, as below.

.. code-block:: python3

    from fabricplus.connection import ConnectionPlus as Connection

    conn: Connection = Connection("some_host")

    # From here, you can do all the things you're used to, like run commands
    conn.run("date")

    # But now you can also run an su command as well
    conn.su("date", "otheruser", password="otheruserspassword")


The following examples will work just as well regardless of naming it ``Connection`` or ``ConnectionPlus`` via the import.

Using SCP instead of the default SFTP
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

By default the ``Connection`` object will use SFTP, and does not have the capacity to use SCP.

The former is true for ``ConnectionPlus`` objects, but the latter is definitely not true.

There are two ways to access SCP. First, to set it as the default method via an argument to the initializer.

.. code-block:: python3

    from fabricplus.connection import ConnectionPlus

    # Add in the scp=True
    conn_a: ConnectionPlus = ConnectionPlus("some_host", scp=True)

    # Then run a put command; it will run through SCP!
    conn_a.put("/path/to/some/local/file", "/path/on/the/remote")

You can also do it at the time of the call to ``put`` or ``get``, like so:

.. code-block:: python3

    from fabricplus.connection import ConnectionPlus

    # leaving out scp=True
    conn_b: ConnectionPlus = ConnectionPlus("some_host")

    # we run this with an scp=True arg.
    conn_b.put("/path/to/some/local/file", "/path/on/the/remote", scp=True)

Connecting Via A Jumphost
-------------------------

There are several ways to specify the jumphost you wish to connect through. There are benefits and drawbacks to each approach.

You can:

- Pass in a string for the URL or IP Address of the Jumphost you wish to target.
- Pass in an ``SSHClient``-like object
- Pass in a ``Connection``-like object

Each is detailed below for clarity.

Using an IP Address or URL
""""""""""""""""""""""""""

Here we will generate a ConnectionPlus object via a jumphost passed in as a string argument.

The example could as easily be done with an IP address in the format ``XXX.XXX.XXX.XXX``, where ``X`` is an integer, and ``XXX`` is together an integer no larger than ``255``.

In the example, we will also be using some other user name to log into the jumphost.

This is the only time that the ``jump_uname`` argument makes any sense, because in all other cases, the host is already logged in via a user.

.. code-block:: python3

    from fabricplus.connection import ConnectionPlus

    jumphost_url: str = "jumphost.example.com"

    # create the connection object, passing in the URL and a username for the jumphost
    conn_c: ConnectionPlus = ConnectionPlus("some_host",
                                            jumphost_target=jumphost_url,
                                            jump_uname="jumphost_username")

    # from here, you can simply run all your commands on the target host via the standard processes
    conn_c.run("date")

Using an SSHClient-like object
""""""""""""""""""""""""""""""

So an ``SSHClient`` (or ``SSHJumpClient``, or anything else that inherits from the base ``SSHClient`` and behaves, roughly, similarly, will work) can be passed through as well.

This is useful for two cases:

1. You want to control some more behaviors about how the ``SSHClient`` connections
2. You want to proxy multiple connections VIA the same jumphost connection

Let us do the latter example:

.. code-block:: python3

    from fabricplus.connection import ConnectionPlus
    from fabricplus.paramiko_modifications.client import SSHJumpClient

    # Creating the client object
    jumphost_client: SSHJumpClient = SSHJumpClient()
    # Doing some back end stuff for host key handling, because it's often necessary
    jumphost_client.set_missing_host_key_policy(WarningPolicy())
    jumphost_client.load_system_host_keys()
    # then connecting
    jumphost_client.connect("some_jumphost_url")

    # create the connection object, passing in the SSHJumpClient object
    conn_c: ConnectionPlus = ConnectionPlus("some_host",
                                            jumphost_target=jumphost_client)

    # importantly you can REUSE the jumphost_client
    conn_d: ConnectionPlus = ConnectionPlus("some_other_host",
                                            jumphost_target=jumphost_client)

    # from here, you can simply run all your commands on the target host 
    # via the standard processes
    conn_c.run("date")
    conn_d.run("date")

Using a Connection-like object
""""""""""""""""""""""""""""""

Similar to above, you may also pass in a ``Connection``-derived object.

All this does is have the back end extract the ``client`` from that ``Connection`` object, and so essentially behaves as above, but the example below should work.

.. code-block:: python3

    from fabricplus.connection import ConnectionPlus

    # Creating the client object
    jumphost_connection: ConnectionPlus = ConnectionPlus("some_jumphost_url")

    # create the connection object, passing in the ConnectionPlus object
    conn_c: ConnectionPlus = ConnectionPlus("some_host",
                                            jumphost_target=jumphost_connection)

    # importantly you can REUSE the jumphost_connection
    conn_d: ConnectionPlus = ConnectionPlus("some_other_host",
                                            jumphost_target=jumphost_connection)

    # from here, you can simply run all your commands on the target host
    # via the standard processes
    conn_c.run("date")
    conn_d.run("date")
