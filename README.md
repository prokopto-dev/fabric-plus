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

## License Addendum

- [`scp.py`](https://github.com/jbardin/scp.py) is used by import under the LGPL v2.1 license, and this notice is in accordance with that license.
- [`paramiko-jump`](https://github.com/andrewschenck/paramiko-jump) used under Apache License 2.0, see `fabricplus/paramiko_modifications/client.py` for license details.
- [`fabric`](https://github.com/fabric/fabric) is used, and falls under a BSD-2-Clause license, which doesn't restrict its use as an imported library, but is noted here anyways.

## TODO

- [ ] Add some unit testing
- [ ] Add documentation, docstrings
- [ ] Add examples in README.md
- [ ] Add installation instructions to README.md
- [x] Add dependency management - Done with `poetry`
- [ ] Port over some more functionality from `scp.py`, maybe remove requirement for the library itself by imported all functionality
- [x] Make more `Transfer`-object-like.
- [x] Possibly expand to be drop-in replacement for `Transfer`, with added `scp` functionality.
- [x] Maybe add a connection object wrapper that does similar things, adding `scp` functionality.
- [x] Add inspiration/references to other projects like paramiko-jump and paramiko-scp (scp.py)
- [ ] Define version compatibility
- [x] Add jump-run and `su` commands for connection, including notes about how it works with parallelism
- [ ] Add notes on how to run things in parallel in docs
- [x] Finish allowing a jumphost to passed into the ConnectionPlus object so we can go ahead construct those connections; should allow several types of objects to be passed in, including an IP/url, Connection/Plus, or SSH/JumpClient
- [ ] Add typing to all of the `client.py` file
  - [ ] Add typing to upstream `paramiko-jump` via PR.
- [ ] Package and deliver via PyPI.
- [ ] Convert all docstrings to `sphinx` / `rst` style for doc generation