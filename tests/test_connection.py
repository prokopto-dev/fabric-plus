import pytest
from unittest.mock import MagicMock, patch
from invoke.exceptions import Failure, ResponseNotAccepted, AuthFailure
from invoke.runners import Result, Runner
from paramiko.client import SSHClient
from fabric.connection import Connection
from paramiko.file import BufferedFile
from fabricplus.connection import ConnectionPlus
from fabricplus.paramiko_modifications.client import SSHJumpClient


import codecs


def b(x) -> bytes:
    return codecs.latin_1_encode(x)[0]


@pytest.mark.parametrize(
    "host, user, connect_kwargs",
    [
        ("hostname", "username", {"password": "password"}),
        ("hostname", "username", {"key_filename": "key_filename"}),
        (
            "hostname",
            "username",
            {"key_filename": "key_filename", "password": "password"},
        ),
    ],
)
def test_connectionplus_base_init(host, user, connect_kwargs):
    conn_plus = ConnectionPlus(host, user, connect_kwargs=connect_kwargs)
    assert conn_plus.host == host
    assert conn_plus.user == user
    for key, value in connect_kwargs.items():
        assert conn_plus.connect_kwargs[key] == value


@pytest.mark.parametrize(
    "host, scp, jump_uname, jump_port, connect_kwargs",
    [
        ("hostname", True, "jump_uname", 22, {"password": "password"}),
        ("hostname", False, "jump_uname", 22, {"key_filename": "key_filename"}),
        ("hostname", True, "jump_uname", None, {"key_filename": "key_filename"}),
        ("hostname", None, None, None, None),
        (
            "hostname",
            True,
            None,
            22,
            {"key_filename": "key_filename", "password": "password"},
        ),
    ],
)
def test_connectionplus_init_with_new_args(
    host, scp, jump_uname, jump_port, connect_kwargs
):
    conn_plus = ConnectionPlus(
        host,
        scp=scp,
        jump_uname=jump_uname,
        jump_port=jump_port,
        connect_kwargs=connect_kwargs,
    )
    assert conn_plus.host == host
    assert conn_plus._ConnectionPlus__scp == scp
    if connect_kwargs is not None:
        for key, value in connect_kwargs.items():
            assert conn_plus.connect_kwargs[key] == value


@patch(
    "fabricplus.connection.ConnectionPlus._ConnectionPlus__client_setup",
    autospec=True,
    return_value=None,
)
def test_connect_init_client_failure(self):
    with pytest.raises(AttributeError):
        ConnectionPlus("hostname", connect_kwargs={"client": "paramiko"})


@patch("fabricplus.connection.ConnectionPlus._su", autospec=True)
def test_connectionplus_su_pass(self):
    conn_plus = ConnectionPlus("hostname")
    conn_plus.su("date", user="username", password="password")
    conn_plus._su.assert_called_once()


@patch("fabricplus.connection.ConnectionPlus._su", autospec=True)
def test_connectionplus_su_fail_no_pw(self):
    conn_plus = ConnectionPlus("hostname")
    with pytest.raises(ValueError):
        conn_plus.su("date", user="username")


@patch("invoke.runners.Runner.run", autospec=True)
def test_connectionplus__su_pass(self):
    conn_plus = ConnectionPlus("hostname")
    conn_plus._ConnectionPlus__client = MagicMock()
    conn_plus._su(
        runner=conn_plus._remote_runner(),
        command="date",
        user="username",
        password="password",
        pty=True,
        timeout=10,
    )


@patch("invoke.runners.Runner.run", autospec=True, side_effect=Failure(Result()))
def test_connectionplus__su_fail_fail(self):
    conn_plus = ConnectionPlus("hostname")
    conn_plus._ConnectionPlus__client = MagicMock()
    with pytest.raises(Failure):
        conn_plus._su(
            runner=conn_plus._remote_runner(),
            command="date",
            user="username",
            password="password",
            pty=True,
            timeout=10,
        )


@patch(
    "invoke.runners.Runner.run",
    autospec=True,
    side_effect=Failure(Result(), reason=ResponseNotAccepted("ResponseNotAccepted")),
)
def test_conenctionplus__su_fail_response_fail(self):
    conn_plus = ConnectionPlus("hostname")
    conn_plus._ConnectionPlus__client = MagicMock()
    with pytest.raises(AuthFailure):
        conn_plus._su(
            runner=conn_plus._remote_runner(),
            command="date",
            user="username",
            password="password",
            pty=True,
            timeout=10,
        )


@patch("fabricplus.connection.ConnectionPlus.open_gateway", autospec=True)
@patch("paramiko.client.SSHClient.connect", autospec=True)
def test_connectionplus__client_setup(self, m2):
    conn_plus = ConnectionPlus("hostname")
    conn_plus._ConnectionPlus__client_setup()


@patch("fabricplus.connection.ConnectionPlus.open_gateway", autospec=True)
@patch("paramiko.client.SSHClient.connect", autospec=True)
def test_connectionplus__client_connect_pass_no_changes(self, m2):
    conn_plus = ConnectionPlus("hostname")
    conn_plus._ConnectionPlus__client_connect(conn_plus.client)


@patch("fabricplus.connection.ConnectionPlus.open_gateway", autospec=True)
@patch("paramiko.client.SSHClient.connect", autospec=True)
@patch(
    "fabricplus.connection.ConnectionPlus.is_connected",
    autospec=True,
    return_value=True,
)
def test_connectionplus__client_connect_pass_already_connected(self, m2, m3):
    conn_plus = ConnectionPlus("hostname")
    conn_plus._ConnectionPlus__client_connect(conn_plus.client)


@patch("fabricplus.connection.ConnectionPlus.open_gateway", autospec=True)
@patch("paramiko.client.SSHClient.connect", autospec=True)
def test_connectionplus__client_connect_pass_no_kwargs(self, m2):
    conn_plus = ConnectionPlus("hostname")
    conn_plus.connect_kwargs = None  # type:  ignore
    conn_plus._ConnectionPlus__client_connect(conn_plus.client)


@patch("fabricplus.connection.ConnectionPlus.open_gateway", autospec=True)
@patch("paramiko.client.SSHClient.connect", autospec=True)
@pytest.mark.parametrize(
    "connect_kwargs",
    [
        {"username": "username"},
        {"hostname": "hostname"},
        {"port": 22},
    ],
)
def test_connectionplus__client_connect_fail_kwargs(self, m2, connect_kwargs):
    conn_plus = ConnectionPlus("hostname", connect_kwargs=connect_kwargs)
    with pytest.raises(ValueError):
        conn_plus._ConnectionPlus__client_connect(conn_plus.client)


@patch("fabricplus.connection.ConnectionPlus.open_gateway", autospec=True)
@patch("paramiko.client.SSHClient.connect", autospec=True)
def test_connectionplus__client_connect_fail_timeout(self, m2):
    conn_plus = ConnectionPlus(
        "hostname", connect_kwargs={"timeout": 10}, connect_timeout=10
    )
    with pytest.raises(ValueError):
        conn_plus._ConnectionPlus__client_connect(conn_plus.client)


@patch("fabricplus.connection.ConnectionPlus.open_gateway", autospec=True)
@patch("paramiko.client.SSHClient.connect", autospec=True)
def test_connectionplus__client_connect_pass_internal_timeout(self, m2):
    conn_plus = ConnectionPlus("hostname", connect_timeout=10)
    conn_plus._ConnectionPlus__client_connect(conn_plus.client)


@patch("fabricplus.connection.ConnectionPlus.open_gateway", autospec=True)
@patch("paramiko.client.SSHClient.connect", autospec=True)
def test_connectionplus__client_connect_pass_empty_keyfile(self, m2):
    conn_plus = ConnectionPlus("hostname")
    conn_plus.connect_kwargs = {"key_filename": None}
    conn_plus._ConnectionPlus__client_connect(conn_plus.client)


@patch("fabricplus.connection.ConnectionPlus.open_gateway", autospec=True)
@patch(
    "fabricplus.paramiko_modifications.client.SSHJumpClient.connect", return_value=None
)
def test_connectionplus__client_connect_pass_kwargs(self, m2):
    conn_plus = ConnectionPlus("hostname", connect_kwargs={"allow_agent": True})
    conn_plus.authentication.strategy_class = MagicMock()
    conn_plus.authentication.strategy_class.name = "SSHJumpClient"
    conn_plus._ConnectionPlus__client_connect(conn_plus.client)


@patch(
    "fabricplus.connection.ConnectionPlus.open_gateway",
    autospec=True,
    return_value=True,
)
@patch(
    "fabricplus.paramiko_modifications.client.SSHJumpClient.connect", return_value=None
)
def test_connectionplus__client_connect_pass_sock(self, m2):
    conn_plus = ConnectionPlus("hostname", connect_kwargs={"allow_agent": True})
    conn_plus.gateway = MagicMock()
    conn_plus._ConnectionPlus__client_connect(conn_plus.client)


@patch("fabricplus.paramiko_modifications.client.SSHJumpClient", autospec=True)
def test_connectionplus__client_setup_jump_client(self):
    jump_client = SSHJumpClient()
    conn_plus = ConnectionPlus("hostname", jumphost_target=jump_client)
    assert conn_plus.client._jump_session == jump_client  # type: ignore


@patch("fabricplus.paramiko_modifications.client.SSHJumpClient", autospec=True)
@patch("paramiko.client.SSHClient", autospec=True)
def test_connectionplus__client_setup_base_client(self, m2):
    jump_client = SSHClient()
    conn_plus = ConnectionPlus("hostname", jumphost_target=jump_client)
    assert conn_plus.client._jump_session == jump_client  # type: ignore


@patch("fabricplus.paramiko_modifications.client.SSHJumpClient", autospec=True)
@patch(
    "fabricplus.connection.ConnectionPlus._ConnectionPlus__client_connect",
    autospec=True,
)
def test_connectionplus__client_setup_str(self, m2):
    jump_client = "hostname"
    conn_plus = ConnectionPlus("hostname", jumphost_target=jump_client)
    assert isinstance(conn_plus.client._jump_session, SSHJumpClient)  # type: ignore


@patch("fabric.connection.Connection.open", autospec=True)
@pytest.mark.parametrize(
    "jump_conn",
    [
        (ConnectionPlus("hostname")),
        (Connection("hostname")),
    ],
)
def test_connectionplus__client_setup_conns(self, jump_conn):
    conn_plus = ConnectionPlus("hostname", jumphost_target=jump_conn)
    assert conn_plus.client._jump_session == jump_conn.client  # type: ignore


@patch("fabric.connection.Connection.open", autospec=True)
@pytest.mark.parametrize(
    "jump_conn",
    [
        (ConnectionPlus("hostname")),
        (Connection("hostname")),
    ],
)
def test_connectionplus__client_setup_conns_try_open(self, jump_conn):
    jump_conn.client = None
    conn_plus = ConnectionPlus("hostname", jumphost_target=jump_conn)


def test_connectionplus__client_setup_conns_fail_type():
    with pytest.raises(TypeError):
        ConnectionPlus("hostname", jumphost_target=22)  # type: ignore


@patch("fabric.connection.Connection.open", autospec=True)
@patch("fabric.connection.Connection.open_gateway", autospec=True)
@patch("paramiko.client.SSHClient.connect", autospec=True)
@pytest.mark.parametrize(
    "jump_conn",
    [
        (ConnectionPlus("hostname")),
        (Connection("hostname")),
        ("hostname"),
        (SSHJumpClient()),
        (SSHClient()),
    ],
)
def test_connectionplus_jump_client_pass(self, m2, m3, jump_conn):
    conn_plus = ConnectionPlus("hostname", jumphost_target=jump_conn)
    assert isinstance(conn_plus.jump_client, SSHJumpClient) or isinstance(
        conn_plus.jump_client, SSHClient
    )


@patch("fabric.connection.Connection.open", autospec=True)
@patch("fabric.connection.Connection.open_gateway", autospec=True)
@patch("paramiko.client.SSHClient.connect", autospec=True)
def test_connectionplus_jump_client_fail(self, m2, m3):
    with pytest.raises(AttributeError):
        conn_plus = ConnectionPlus("hostname")
        conn_plus.client = None
        conn_plus.jump_client


@patch("fabric.connection.Connection.open", autospec=True)
@patch("fabric.connection.Connection.open_gateway", autospec=True)
@patch("paramiko.client.SSHClient.connect", autospec=True)
def test_connectionplus_jump_run_fail_no_client(self, m2, m3):
    with pytest.raises(AttributeError):
        conn_plus = ConnectionPlus("hostname")
        conn_plus.jump_run("date")


@patch("fabric.connection.Connection.open", autospec=True)
@patch("fabric.connection.Connection.open_gateway", autospec=True)
@patch("paramiko.client.SSHClient.connect", autospec=True)
@patch("paramiko.client.SSHClient.exec_command", side_effect=Exception("Exception"))
def test_connectionplus_jump_run_fail_exception(self, m2, m3, m4):
    conn_plus = ConnectionPlus("hostname", jumphost_target="hostname2")
    result = conn_plus.jump_run("date")
    assert result.exited == 1  # type: ignore
    assert result.stdout == ""  # type: ignore
    assert result.stderr == "Exception"  # type: ignore


@patch("fabric.connection.Connection.open", autospec=True)
@patch("fabric.connection.Connection.open_gateway", autospec=True)
@patch("paramiko.client.SSHClient.connect", autospec=True)
@patch(
    "fabricplus.paramiko_modifications.client.SSHJumpClient.exec_command",
    autospec=True,
    return_value=(BufferedFile(), BufferedFile(), BufferedFile()),
)
@patch("paramiko.file.BufferedFile.read", return_value=b("date\n"))
def test_connectionplus_jump_run_pass(self, m2, m3, m4, m5):
    conn_plus = ConnectionPlus("hostname", jumphost_target="hostname2")
    result = conn_plus.jump_run("date")
    assert isinstance(result, Result)


@patch("fabric.connection.Connection.open", autospec=True)
@patch("fabric.connection.Connection.open_gateway", autospec=True)
@patch("paramiko.client.SSHClient.get_transport", autospec=True)
@patch("paramiko.client.SSHClient.connect", autospec=True)
def test_connectionplus_scp_pass(self, m2, m3, m4):
    conn_plus = ConnectionPlus("hostname", scp=True)
    conn_plus.scp()


@patch("fabric.connection.Connection.open", autospec=True)
@patch("fabric.connection.Connection.open_gateway", autospec=True)
@patch("paramiko.client.SSHClient.get_transport", autospec=True)
@patch("paramiko.client.SSHClient.connect", autospec=True)
def test_connectionplus_scp_fail_no_init(self, m2, m3, m4):
    conn_plus = ConnectionPlus("hostname", scp=True)
    conn_plus.client = None
    with pytest.raises(AttributeError):
        conn_plus.scp()


@patch("fabric.connection.Connection.open", autospec=True)
@patch("fabric.connection.Connection.open_gateway", autospec=True)
@patch("paramiko.client.SSHClient.get_transport", autospec=True, return_value=None)
@patch("paramiko.client.SSHClient.connect", autospec=True)
def test_connectionplus_scp_fail_no_transport(self, m2, m3, m4):
    conn_plus = ConnectionPlus("hostname", scp=True)
    with pytest.raises(AttributeError):
        conn_plus.scp()


@patch("fabric.connection.Connection.open", autospec=True)
@patch("fabric.connection.Connection.open_gateway", autospec=True)
@patch("paramiko.client.SSHClient.get_transport", autospec=True)
@patch("paramiko.client.SSHClient.connect", autospec=True)
@patch("fabricplus.transfer.TransferPlus.get", autospec=True)
def test_connectionplus_scp_get_pass(self, m2, m3, m4, m5):
    conn_plus = ConnectionPlus("hostname", scp=True)
    conn_plus.get("remote", "local")


@patch("fabric.connection.Connection.open", autospec=True)
@patch("fabric.connection.Connection.open_gateway", autospec=True)
@patch("paramiko.client.SSHClient.get_transport", autospec=True)
@patch("paramiko.client.SSHClient.connect", autospec=True)
@patch("fabricplus.transfer.TransferPlus.put", autospec=True)
def test_connectionplus_scp_put_pass(self, m2, m3, m4, m5):
    conn_plus = ConnectionPlus("hostname", scp=True)
    conn_plus.put("remote", "local")
