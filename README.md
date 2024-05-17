# Fabric-SCP

A wrapper for `fabric` and `scp.py` to simplify creating a SCP connection via an existing connection.

I may eventually be forking out a version of `paramiko` and `fabric` for the purposes maintaining these as core features.

## Goals

A bunch of clients I target in my own use of `fabric` have a few funky features, including *not* supporting SFTP.

As of time of writing (20240516), `fabric` only supports `sftp` protocol for it's transfer.

This is also true for `paramiko`.

[`scp.py`](https://github.com/jbardin/scp.py) does a fine job of handling taking a transport from an `SSHClient` and turning it into an `SCPClient`.

What I needed was a way to do the same thing with a connection.

## Features

- Takes in a fabric `Connection`-type object.
- Works with [`paramiko-jump`](https://github.com/andrewschenck/paramiko-jump) by [@andrewschenck](https://github.com/andrewschenck), allowing for `scp` file transfers via jumphost connections.


## License Addendum

- [`scp.py`](https://github.com/jbardin/scp.py) is used by import under the LGPL v2.1 license, and this notice is in accordance with that license.
- [`fabric`](https://github.com/fabric/fabric) is used, and falls under a BSD-2-Clause license, which doesn't restrict its use as an imported library, but is noted here anyways.

## TODO

- [ ] Add some unit testing
- [ ] Add dependency management
- [ ] Port over some more functionality from `scp.py`, maybe remove requirement for the library itself by imported all functionality
- [ ] Make more `Transport`-object-like.
- [ ] Possibly expand to be drop-in replacement for `Transport`, with added `scp` functionality.
- [ ] Maybe add a connection object wrapper that does similar things, adding `scp` functionality.
- [ ] Add inspiration/references to other projects like paramiko-jump and paramiko-scp (scp.py)
- [ ] Define version compatibility
