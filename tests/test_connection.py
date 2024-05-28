import pytest
from unittest.mock import MagicMock, patch
from invoke.exceptions import Failure, ResponseNotAccepted, AuthFailure
from invoke.runners import Result
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

@patch('fabricplus.connection.ConnectionPlus._su', autospec=True)
def test_connectionplus_su_pass(self):
    conn_plus = ConnectionPlus("hostname")
    conn_plus.su("date", user="username", password="password")
    conn_plus._su.assert_called_once()

@patch('fabricplus.connection.ConnectionPlus._su', autospec=True)
def test_connectionplus_su_fail_no_pw(self):
    conn_plus = ConnectionPlus("hostname")
    with pytest.raises(ValueError):
        conn_plus.su("date", user="username")

@patch('invoke.runners.Runner.run', autospec=True)
def test_connectionplus__su_pass(self):
    conn_plus = ConnectionPlus("hostname")
    conn_plus._ConnectionPlus__client = MagicMock()
    conn_plus._su(runner=conn_plus._remote_runner(), command="date", user="username", password="password", pty=True, timeout=10)

@patch('invoke.runners.Runner.run', autospec=True, side_effect=Failure(Result()))
def test_connectionplus__su_fail_fail(self):
    conn_plus = ConnectionPlus("hostname")
    conn_plus._ConnectionPlus__client = MagicMock()
    with pytest.raises(Failure):
        conn_plus._su(runner=conn_plus._remote_runner(), command="date", user="username", password="password", pty=True, timeout=10)

@patch('invoke.runners.Runner.run', autospec=True, side_effect=Failure(Result(), reason=ResponseNotAccepted("ResponseNotAccepted")))
def test_conenctionplus__su_fail_response_fail(self):
    conn_plus = ConnectionPlus("hostname")
    conn_plus._ConnectionPlus__client = MagicMock()
    with pytest.raises(AuthFailure):
        conn_plus._su(runner=conn_plus._remote_runner(), command="date", user="username", password="password", pty=True, timeout=10)