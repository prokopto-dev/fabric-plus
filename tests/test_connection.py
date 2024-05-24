import pytest
from unittest.mock import MagicMock, patch

from fabricplus.connection import ConnectionPlus


@pytest.mark.parametrize("host, user, connect_kwargs", [
    ("hostname", "username", {"password": "password"}),
    ("hostname", "username", {"key_filename": "key_filename"}),
    ("hostname", "username", {"key_filename": "key_filename", "password": "password"})
])
def test_connectionplus_base_init(host, user, connect_kwargs):
    conn_plus = ConnectionPlus(host, user, connect_kwargs=connect_kwargs)
    assert conn_plus.host == host
    assert conn_plus.user == user
    for key, value in connect_kwargs.items():
        assert conn_plus.connect_kwargs[key] == value

@pytest.mark.parametrize("host, scp, jump_uname, jump_port, connect_kwargs", [
    ("hostname", True, "jump_uname", 22, {"password": "password"}),
    ("hostname", False, "jump_uname", 22, {"key_filename": "key_filename"}),
    ("hostname", True, "jump_uname", None, {"key_filename": "key_filename"}),
    ("hostname", None, None, None, None),
    ("hostname", True, None, 22, {"key_filename": "key_filename", "password": "password"})
])
def test_connectionplus_init_with_new_args(host, scp, jump_uname, jump_port, connect_kwargs):
    conn_plus = ConnectionPlus(host, scp=scp, jump_uname=jump_uname, jump_port=jump_port, connect_kwargs=connect_kwargs)
    assert conn_plus.host == host
    assert conn_plus._ConnectionPlus__scp == scp
    if connect_kwargs is not None:
        for key, value in connect_kwargs.items():
            assert conn_plus.connect_kwargs[key] == value

@patch('fabricplus.connection.ConnectionPlus._ConnectionPlus__client_setup', autospec=True, return_value=None)
def test_connect_init_client_failure(self):
    with pytest.raises(AttributeError):
        ConnectionPlus("hostname", connect_kwargs={"client": "paramiko"})