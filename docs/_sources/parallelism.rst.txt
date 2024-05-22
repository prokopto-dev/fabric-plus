===============================
Running Connections In Parallel
===============================

It is possible to run multiple connections at the same time, and have them handled in a multi-threaded or multi-processing library.

Testing is generally done using the ``concurrent.futures`` library, which is a high-level interface for asynchronously executing functions in a separate thread or process.

The advantage of using ``concurrent.futures`` is that it behaves similar to the way the ``Connection`` object expects to be used, in that it runs in the hopes it works, and resolves errors after rather than interactively.

Creating a bunch of connections
-------------------------------

Here's an example of how one might use ``concurrent.futures`` to run multiple connections at the same time.

.. code-block:: python3

    import concurrent.futures
    from fabricplus.connection import ConnectionPlus as Connection
    from traceback import format_exc


    # Create a list of hosts
    hosts: list[str] = [
        "host1",
        "host2",
        "host3",
        "host4",
        "host5",
        "host6",
        "host7",
        "host8",
        "host9",
        "host10",
    ]
    connections: list[Connection] = []
    # Create a list of connections, concurrently
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(Connection, host) for host in hosts]
        tb: Optional[str] = None
        # the code below helps handle tracebacks and errors; 
        # with out it, silent failures may occur
        for future in concurrent.futures.as_completed(futures):
            try:
                tb = None
                connections.append(future.result())
            except Exception as e:
                tb = traceback.format_exc()
            finally:
                if tb:
                    print(f"Error: {tb}")


    # Now you can use the connections, presuming they worked
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(connection.run, "ls -l") for connection in connections]
        tb: Optional[str] = None
        for future in concurrent.futures.as_completed(futures):
            try:
                tb = None
                print(future.result())
            except Exception as e:
                tb = traceback.format_exc()
            finally:
                if tb:
                    print(f"Error: {tb}")


Important Note on ``SU`` In Parallelism
---------------------------------------

The ``SU`` command is a special command that is used to switch users. 

It is one of the features I built this library for, and it generally works great.

However, on some hosts, the ``SU`` command does NOT work in a non-interactive shell.

This is because of some complex kernel behaviors in older versions to avoid a security vulnerability.

Personally, I have found that ``CentOS 7`` and older, as well as simmilar versions of ``RHEL`` and ``Fedora`` have all had the same issue.

The same may be true for other distributions, but I have found that ``Debian`` and ``Ubuntu`` have not had this issue.

If you are using a host that has this issue, you will need to use the ``sudo`` command to switch users.