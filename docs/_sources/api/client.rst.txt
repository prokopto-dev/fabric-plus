==========
``client``
==========

This is a module that offers a modified version of the ``paramiko-jump``-sourced ``SSHJumpClient`` class.

That itself is a subclass of ``paramiko.SSHClient`` that adds the ability to use a jump host to connect to a target host.

For documentation on its behavior, see the `paramiko client documentation <http://docs.paramiko.org/en/stable/api/client.html>`_.

``paramiko-jump`` is used under the terms of the `Apache License 2.0 <https://www.apache.org/licenses/LICENSE-2.0>`_.

Copyright (c) 2020, `Andrew Schenck <https://github.com/andrewschenck>`_.

.. automodule:: fabricplus.paramiko_modifications.client