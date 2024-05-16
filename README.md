# Fabric-SCP

A wrapper for `fabric` and `scp.py` to simplify creating a SCP connection via an existing connection.

I may eventually be forking out a version of `paramiko` and `fabric` for the purposes maintaining these as core features.

## Goals

A bunch of clients I target in my own use of `fabric` have a few funky features, including *not* supporting SFTP.

As of time of writing (20240516), `fabric` only supports `sftp` protocol for it's transfer.

This is also true for `paramiko`.

`scp.py` does a fine job of handling taking a transport from an `SSHClient` and turning it into an `SCPClient`.

What I needed was a way to do the same thing with a connection.

## Features

Most important to me, it works with the `SSHJumpClient` as defined by @andrewschenck in his `paramiko-jump`.

It should work with any connection via `fabric.connection.Connection`.

## TODO

- [ ] Add built-in expansion of `~` and similar behavior
- [ ] Add some unit testing
- [ ] Add dependency management
- [ ] Port over some more functionality from `scp.py`
- [ ] Make more `Transport`-object-like.

