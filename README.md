![PyPI - Version](https://img.shields.io/pypi/v/fabricplus)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/fabricplus)
![PyPI - License](https://img.shields.io/pypi/l/fabricplus)

# FabricPlus

A drop-in expansion of features in the Fabric library.

As of version `0.1.0`, those include:

- Jumphost connectivity support
  - `jump_run` command to run commands from the intermediate jumphost
- SCP Transfer support (including via a jumphost)
- `su` command support

See the API documentation on the [FabricPlus Website](https://fabricplus.prokopto.dev/) for more information, as well as "Getting Started" guide.

See [`fabric`](https://github.com/fabric/fabric) for more details on the base `fabric` library, if interested in the underlying behaviors. Some have been changed: see Important Changes and the documentation for more information.

## Installation

### pip (via PyPI)

As of version `0.1.0`, FabricPlus is available via `pip` and is on the Python Package Index.

To install, simply install `fabricplus`.

```bash
pip install fabricplus
```

### Building From Source

You can also build `fabricplus` from source, especially if you want features or updates released outside of a tagged release on `PyPI`.

To do so, you'll need `poetry`, and an environment with a version of Python greater than or equal to `3.8`.

#### Step 1: Install Poetry

To install `poetry`, simply run:

```bash
pip install poetry
```

For more information on `poetry`, see the [Poetry Website](https://python-poetry.org/).

#### Step 2: Clone Repo and Run `poetry build`

Once you have that installed, clone the repo, then run `poetry build` from the root directory:

```bash
# Clone
git clone https://github.com/prokopto-dev/fabric-plus
# Move into fabric-plus
cd fabric-plus
# Run poetry build
poetry build
# install with pip the newly build wheel file (file name may vary)
pip install dist/fabricplus-0.1.0-py3-none-any.whl
```

## Examples

### Create A Basic Connection As A Drop In Replacement

If you want to create a connection, it is nearly identical to `Fabric` itself.

The only difference is if you want the drop-in replacement, you'll need to import the `ConnectionPlus` object as a `Connection`, as below.

```python3
from fabricplus.connection import ConnectionPlus as Connection

conn: Connection = Connection("some_host")

# From here, you can do all the things you're used to, like run commands
conn.run("date")

# But now you can also run an su command as well
conn.su("date", "otheruser", password="otheruserspassword")
```

The following examples will work just as well regardless of naming it `Connection` or `ConnectionPlus` via the import.

### Using SCP instead of the default SFTP

By default the `Connection` object will use SFTP, and does not have the capacity to use SCP.

The former is true for `ConnectionPlus` objects, but the latter is definitely not true.

There are two ways to access SCP. First, to set it as the default method via an argument to the initializer.

```python3

from fabricplus.connection import ConnectionPlus

# Add in the scp=True
conn_a: ConnectionPlus = ConnectionPlus("some_host", scp=True)

# Then run a put command; it will run through SCP!
conn_a.put("/path/to/some/local/file", "/path/on/the/remote")
```

You can also do it at the time of the call to `put` or `get`, like so:

```python3

from fabricplus.connection import ConnectionPlus

# leaving out scp=True
conn_b: ConnectionPlus = ConnectionPlus("some_host")

# we run this with an scp=True arg.
conn_b.put("/path/to/some/local/file", "/path/on/the/remote", scp=True)

```

### Connecting Via A Jumphost

There are several ways to specify the jumphost you wish to connect through. There are benefits and drawbacks to each approach.

You can:

- Pass in a string for the URL or IP Address of the Jumphost you wish to target.
- Pass in an `SSHClient`-like object
- Pass in a `Connection`-like object

Each is detailed below for clarity.

#### Using an IP Address or URL

Here we will generate a ConnectionPlus object via a jumphost passed in as a string argument.

The example could as easily be done with an IP address in the format `XXX.XXX.XXX.XXX`, where `X` is an integer, and `XXX` is together an integer no larger than `255`.

In the example, we will also be using some other user name to log into the jumphost.

This is the only time that the `jump_uname` argument makes any sense, because in all other cases, the host is already logged in via a user.

```python3
from fabricplus.connection import ConnectionPlus

jumphost_url: str = "jumphost.example.com"

# create the connection object, passing in the URL and a username for the jumphost
conn_c: ConnectionPlus = ConnectionPlus("some_host",
                                        jumphost_target=jumphost_url,
                                        jump_uname="jumphost_username")

# from here, you can simply run all your commands on the target host via the standard processes
conn_c.run("date")
```

#### Using an SSHClient-like object

So an `SSHClient` (or `SSHJumpClient`, or anything else that inherits from the base `SSHClient` and behaves, roughly, similarly, will work) can be passed through as well.

This is useful for two cases:

1. You want to control some more behaviors about how the `SSHClient` connections
2. You want to proxy multiple connections VIA the same jumphost connection

Let us do the latter example:

```python3
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
```

#### Using a Connection-like object

Similar to above, you may also pass in a `Connection`-derived object.

All this does is have the back end extract the `client` from that `Connection` object, and so essentially behaves as above, but the example below should work.

```python3
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
```

## Timeline


- [x] Finish initial feature builds with
  - Interopability with base `Connection`
  - Added `paramiko-jump` compatibility
  - Added `scp` compatibility
  - Added `su` compatibility
- [x] Finish typing, docstrings, and consistency checks
- [x] Set up auto-generating documentation
- [ ] Set up automated unit testing
- [ ] Set up automated building
- [ ] Publish 1.0 to PyPI

License Addendum
----------------
- [`scp.py`](https://github.com/jbardin/scp.py) is used by import under the LGPL v2.1 license, and this notice is in accordance with that license.
- [`paramiko-jump`](https://github.com/andrewschenck/paramiko-jump) used under Apache License 2.0, see `fabricplus/paramiko_modifications/client.py` for license details.
- [`fabric`](https://github.com/fabric/fabric) is used, and falls under a BSD-2-Clause license, which doesn't restrict its use as an imported library, but is noted here anyways.

TODO
----

- [ ] Add some unit testing
- [ ] Move and expand quick start info
- [ ] Add installation instructions to README.md
- [ ] Port over some more functionality from `scp.py`, maybe remove requirement for the library itself by imported all functionality
- [ ] Define version compatibility for Fabric/Invoke/Paramiko
- [ ] Ensure `Fab CLI Tool` compatibility... hadn't considered that.
