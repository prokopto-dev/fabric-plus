![PyPI - Version](https://img.shields.io/pypi/v/fabricplus)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/fabricplus)
![PyPI - License](https://img.shields.io/pypi/l/fabricplus)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/prokopto-dev/fabric-plus/testing.yml?logo=github&label=testing)

# FabricPlus

A drop-in expansion of features in the Fabric library.

As of version `0.1.0`, those include:

- Jumphost connectivity support
  - `jump_run` command to run commands from the intermediate jumphost
- SCP Transfer support (including via a jumphost)
- `su` command support

See the API documentation on the [FabricPlus Website](https://fabricplus.prokopto.dev/) for more information, as well as "Getting Started" guide.

See [`fabric`](https://github.com/fabric/fabric) for more details on the base `fabric` library, if interested in the underlying behaviors. Some have been changed: see Important Changes and the documentation for more information.

## Note On Changelogs

### v1.0.1

- Bugfix: `su` command had an invalid argument when processing subcommands. Fixed.

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

## Quick-Start

The following is all the basic *new* features in one small block.

```python3
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
```

License Addendum
----------------
- [`scp.py`](https://github.com/jbardin/scp.py) is used by import under the LGPL v2.1 license, and this notice is in accordance with that license.
- [`paramiko-jump`](https://github.com/andrewschenck/paramiko-jump) used under Apache License 2.0, see `fabricplus/paramiko_modifications/client.py` for license details.
- [`fabric`](https://github.com/fabric/fabric) is used, and falls under a BSD-2-Clause license, which doesn't restrict its use as an imported library, but is noted here anyways.