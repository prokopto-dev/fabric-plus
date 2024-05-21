# Fabric-Plus

A drop-in expansion of features in the Fabric library.

See [`fabric`](https://github.com/fabric/fabric) for more details, if interested in the underlying behaviors. Some have been changed: see Important Changes and the documentation for more information.

I may eventually be forking out a version of `paramiko` and `fabric` for the purposes maintaining these as core features of the whole, but for as long as I can, I will be simply providing a drop in replacement for several objects.

## Notes

- Requires Python 3.8+; typing has been added pretty aggressively throughout the library, and as a result, you will need to have a slightly newer version of python than is technically required by the base `Fabric` library.
- Changed default host key handling to do "Warning" instead of "AutoAdd" (default currently in `Fabric`)

## Installation

While in development, I am using [`poetry`](https://python-poetry.org/). You can install poetry by either `pip3 install poetry` or `brew install poetry`; for more details, please look at the website linked.

To build a version, just run `poetry build` from the cloned repo base.

It should handle all other dependency needs on the backend.

NOTE: I will be adding in `PyPI` and package distributions in a short while. But if you need it as an installed package at `v0.1.0`, please do it as defined above.

Thanks!

## Goals

A bunch of clients I target in my own use of `fabric` have a few funky features, including *not* supporting SFTP.

As of time of writing (20240516), `fabric` only supports `sftp` protocol for it's transfer.

This is also true for `paramiko`.

[`scp.py`](https://github.com/jbardin/scp.py) does a fine job of handling taking a transport from an `SSHClient` and turning it into an `SCPClient`.

What I needed was a way to do the same thing with a connection.

## Features

- Provides a drop-in fabric `Connection` replacement called `ConnectionPlus`; should be imported as `Connection`, if desired to be used as a drop-in.
- Provides a drop-in replacement fabric `Transfer` replacement called `TransferPlus`; should be imported as `Transfer` if desited to be used as a drop-in.
- Works with [`paramiko-jump`](https://github.com/andrewschenck/paramiko-jump) by [@andrewschenck](https://github.com/andrewschenck), allowing for `scp` file transfers via jumphost connections.
  - Added `jump_run` command to run commands from jumphost itself, if needed.
- Added a `su` command to the `ConnectionPlus` object; this runs the command using a specified `su` user.
- Tries to be fully typed, though `Fabric` isn't consistently this way, so some inherited functions and attributes may remain untyped.

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



## Timeline


- [x] Finish initial feature builds with
  - Interopability with base `Connection`
  - Added `paramiko-jump` compatibility
  - Added `scp` compatibility
  - Added `su` compatibility
- [ ] Finish typing, docstrings, and consistency checks
- [ ] Set up auto-generating documentation
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
- [ ] Add documentation, docstrings
- [ ] Add examples in README.md
- [ ] Add installation instructions to README.md
- [ ] Port over some more functionality from `scp.py`, maybe remove requirement for the library itself by imported all functionality
- [ ] Define version compatibility
- [ ] including notes about how it works with parallelism for `su` vs `sudo` as a user
- [ ] Add notes on how to run things in parallel in docs
- [ ] Add typing to all of the `client.py` file
- [ ] Add typing to upstream `paramiko-jump` via PR.
- [ ] Package and deliver via PyPI.
