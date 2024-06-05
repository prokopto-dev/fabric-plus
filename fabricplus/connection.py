# External Imports
from fabric.connection import Connection, opens
import fabric.transfer
import re
from invoke.watchers import FailingResponder, Responder
from paramiko import WarningPolicy, SSHClient, Transport
from invoke.runners import Result

from scp import SCPClient
from invoke.exceptions import Failure, ResponseNotAccepted, AuthFailure

# Internal Imports
from fabricplus.transfer import TransferPlus
from fabricplus.paramiko_modifications.client import SSHJumpClient, simple_auth_handler

# Typing Imports
from typing import Optional, Union, Callable, List, Any, AnyStr, TYPE_CHECKING, TypeVar
from paramiko.channel import ChannelFile, ChannelStderrFile

if TYPE_CHECKING:
    from invoke.runners import Runner  # pragma: no cover

# Type Variable For Connection-Like objects
Conn = TypeVar("Conn", bound=Connection, covariant=True)
# Type Variable For SSHClient-Like objects
Client = Union[SSHJumpClient, SSHClient]


class ConnectionPlus(Connection):
    """ConnectionPlus is a subclass of the Connection object from the Fabric library.

    This subclass provides additional functionality to the Connection object, such as SCP transfers,
    running commands as another user, and running commands on a jumphost, as well as connecting to
    a host through a jumphost.
    """

    def __init__(
        self,
        *args,
        jumphost_target: Optional[Union[Client, str, Conn]] = None,
        scp: Optional[bool] = None,
        jump_uname: Optional[str] = None,
        jump_port: Optional[int] = None,
        **kwargs,
    ):
        """Initialize the ConnectionPlus object.

        Initializes using the Connection initialization, but also sets up the client object
        for the ConnectionPlus object via a jumphost target.

        See the Connection object documentation for additional arguments.

        :param args: Additional arguments to pass to the Connection object.
        :param jumphost_target:
            Jumphost to connect to the host through.
            Can be an instance of SSHJumpClient, SSHClient, URL/IP string,
            or Connection/ConnectionPlus.
            Defaults to None.
        :param scp:
            Boolean value to define if the ConnectionPlus object should
            use SCP for file transfers.
            Defaults to False.
        :param jump_uname:
            Username for the jumphost if different than the connection.
            Defaults to None.
        :param jump_port:
            Port for the jumphost if different than the default SSH_PORT.
            Defaults to None.
        :param kwargs:
            Additional keyword arguments to pass to the Connection object.
        """
        super().__init__(*args, **kwargs)
        self._scp: Optional[SCPClient] = None
        self.__scp: Optional[bool] = scp
        self.client: Optional[Client] = self.__client_setup(
            jumphost_target=jumphost_target, jump_uname=jump_uname, jump_port=jump_port
        )
        if self.client is None:
            raise AttributeError(
                "The ConnectionPlus object could not initialize it's client."
            )
        self.client.set_missing_host_key_policy(WarningPolicy())
        self.client.load_system_host_keys()

    def su(
        self,
        command: str,
        user: str,
        password: Optional[str] = None,
        timeout: int = 10,
        **kwargs: Any,
    ) -> Optional["Result"]:
        """Run a command as another user, via su.

        Requires the target user's password be given, either directly, or via the ConnectionPlus object.

        Note: This method doesn't work on Windows, as Windows doesn't have su, nor does it work in parallel on
        some systems due to the way su is implemented (e.g. it may require a tty).

        :param command: Command to run in su.
        :param user: User to run the command as.
        :param password: Password for the target user. Needed, but defaults to None.
        :param timeout: Timeout for the command. Defaults to 10.
        :param kwargs: Additional keyword arguments to pass to the command execution.
        :raises ValueError: If the password is not given.
        :return: Result object from the command execution.
        :rtype: Optional[Result]
        """
        _password: str = password or self.connect_kwargs.get("password", None)
        if _password is None:
            raise ValueError(
                "The password must be given to run a command as another user."
            )
        return self._su(
            runner=self._remote_runner(),
            command=command,
            user=user,
            password=_password,
            timeout=timeout,
            pty=True,
            **kwargs,
        )

    def _su(
        self,
        runner: "Runner",
        command: str,
        user: str,
        password: Optional[str] = None,
        timeout: int = 10,
        **kwargs: Any,
    ) -> Optional["Result"]:
        """Internal representation to run a command as another user, via su.

        :param runner: The runner object to run the command.
        :param command: Command to run in su.
        :param user: User to run the command as.
        :param password: Password for the target user. Needed, but defaults to None.
        :param timeout: Timeout for the command. Defaults to 10.
        :param kwargs: Additional keyword arguments to pass to the command execution.
        :raises AuthFailure: If the authentication fails.
        :raises failure: If the command execution fails.
        :return: Result object from the command execution.
        :rtype: Optional[Result]
        """
        _prompt: str = "Password: "
        _command: str = self._prefix_commands(command)
        # Escape all double quotes in the command.
        _cmd_str: str = f'su - {user} -c "{command}"'.format(
            user=user, command=_command.replace('"', '\\"')
        )
        _watcher: FailingResponder = FailingResponder(
            pattern=re.escape(_prompt),
            response="{password}\n".format(password=password),
            sentinel="Sorry, try again.\n",
        )
        watchers: List[Union[FailingResponder, Responder]] = kwargs.pop("watchers", [])
        watchers.append(_watcher)
        try:
            return runner.run(_cmd_str, timeout=timeout, watchers=watchers, **kwargs)
        except Failure as failure:
            if isinstance(failure.reason, ResponseNotAccepted):
                raise AuthFailure(result=failure.result, prompt=_prompt)
            else:
                raise failure

    def __client_connect(
        self, client: Client, username: Optional[str] = None, port: Optional[int] = None
    ) -> None:
        """Connect the client object for the ConnectionPlus object.

        Helps pass in the connect arguments from the Connection object.

        These include some loaded from SSH Config.

        :param client: The client object to connect.
        :param username: Username to connect with. Defaults to None.
        :param port: Port to connect with. Defaults to None.
        """
        # Ensure dict-ness
        if self.connect_kwargs is None:
            self.connect_kwargs: dict[str, Any] = {}
        # Short-circuit
        if self.is_connected:
            return
        err = "Refusing to be ambiguous: connect() kwarg '{}' was given both via regular arg and via connect_kwargs!"  # noqa
        # These may not be given, period
        for key in """
            hostname
            port
            username
        """.split():
            if key in self.connect_kwargs:
                raise ValueError(err.format(key))
        # These may be given one way or the other, but not both
        if "timeout" in self.connect_kwargs and self.connect_timeout is not None:
            raise ValueError(err.format("timeout"))
        # No conflicts -> merge 'em together
        kwarg_updates: dict[str, Any] = {
            "hostname": self.host,
            "port": port or self.port,
            "username": username or self.user,
        }
        kwargs: dict[str, Any] = (
            self.connect_kwargs.copy() if self.connect_kwargs else kwarg_updates
        )
        kwargs.update(kwarg_updates)
        if self.gateway:
            kwargs["sock"] = self.open_gateway()
        if self.connect_timeout:
            kwargs["timeout"] = self.connect_timeout
        # Strip out empty defaults for less noisy debugging
        if "key_filename" in kwargs and not kwargs["key_filename"]:
            del kwargs["key_filename"]
        auth_strategy_class = self.authentication.strategy_class
        if auth_strategy_class is not None:
            # Pop connect_kwargs related to auth to avoid giving Paramiko
            # conflicting signals.
            for key in (
                "allow_agent",
                "key_filename",
                "look_for_keys",
                "passphrase",
                "password",
                "pkey",
                "username",
            ):
                kwargs.pop(key, None)

            kwargs["auth_strategy"] = auth_strategy_class(
                ssh_config=self.ssh_config,
                fabric_config=self.config,
                username=username or self.user,
            )
        client.connect(**kwargs)
        return None

    def __client_setup(
        self,
        *args,
        jumphost_target: Optional[Union[Client, str, Conn]] = None,
        interactive_prompt: bool = False,
        jump_uname: Optional[str] = None,
        jump_port: Optional[int] = None,
        **kwargs,
    ) -> Optional[Client]:
        """Setup the client object for the ConnectionPlus object.

        This method can be used to setup the client object for the ConnectionPlus object.
        But it also can be used to setup the jumphost for the ConnectionPlus object.

        :param jumphost_target: Jumphost to run all actions through for this client. Defaults to None.
        :param interactive_prompt: Whether to use an interactive method for the jumphost connectivity. Defaults to False.
        :param jump_uname: Username for jumphost if different than connection. Defaults to None.
        :param jump_port: Port for the jumphost if different than default SSH_PORT. Defaults to None.
        :raises TypeError: If the jumphost_target is not an instance of SSHJumpClient, SSHClient, URL/IP string, or Connection/ConnectionPlus.
        :return: The SSHClient object for the ConnectionPlus object.
        :rtype: Union[SSHClient/SSHJumpClient]
        """
        _client: Optional[Client] = None
        _auth_handler: Optional[Callable[..., List[Any]]] = (
            simple_auth_handler if interactive_prompt else None
        )
        if jumphost_target is not None:
            if isinstance(jumphost_target, SSHJumpClient):
                _client = jumphost_target
            elif isinstance(jumphost_target, SSHClient):
                _client = jumphost_target
            elif isinstance(jumphost_target, str):
                _client = SSHJumpClient(auth_handler=_auth_handler)
                _client.set_missing_host_key_policy(WarningPolicy())
                _client.load_system_host_keys()
                self.__client_connect(
                    _client, username=jump_uname or self.user, port=jump_port
                )
            elif isinstance(jumphost_target, Connection) or isinstance(
                jumphost_target, ConnectionPlus
            ):
                if jumphost_target.client is None:
                    jumphost_target.open()
                _client = jumphost_target.client
            else:
                raise TypeError(
                    "The jumphost_target must be an instance of SSHJumpClient, SSHClient, URL/IP string, or Connection/ConnectionPlus."
                )
        return SSHJumpClient(
            *args, jump_session=_client, auth_handler=_auth_handler, **kwargs
        )

    @property
    def jump_client(self) -> Optional[Client]:
        """
        Get the jump client object for the ConnectionPlus object.

        :return: The jump client object for the ConnectionPlus object.
        :rtype: Optional[SSHJumpClient]
        """
        if self.client is None:
            raise AttributeError(
                "The ConnectionPlus object does not have a client initialized."
            )
        return (
            self.client._jump_session
            if isinstance(self.client, SSHJumpClient)
            else None
        )

    def jump_run(self, command: str, timeout: int = 10, **kwargs) -> Optional["Result"]:
        """Run a command on the jumphost.

        :param command: Command to run on the jumphost.
        :param timeout: Timeout for the command. Defaults to 10.
        :param kwargs: Additional keyword arguments to pass to the command execution.
        :raises AttributeError: If the ConnectionPlus object does not have a jump client initialized.
        :return: Result object from the command execution.
        :rtype: Optional[Result]
        """
        if self.jump_client is None:
            raise AttributeError(
                "The ConnectionPlus object does not have a jump client initialized."
            )
        try:
            _timeout: int = kwargs.pop("timeout", timeout)
            # typehints for exec_command aren't porting over, so do them here
            # See: PEP-0526 for more information
            _stderr: ChannelStderrFile
            _stdout: ChannelFile
            _, _stdout, _stderr = self.jump_client.exec_command(
                command, timeout=_timeout, **kwargs
            ) or (None, None, None)
            _stderr_str: str = _stderr.read().decode("utf-8").strip("\n")
            _stdout_str: str = _stdout.read().decode("utf-8").strip("\n")
            return Result(
                stdout=_stdout_str,
                stderr=_stderr_str,
                exited=0,
                encoding="utf-8",
                command=command,
            )
        except Exception as e:
            return Result(
                stdout="", stderr=str(e), exited=1, encoding="utf-8", command=command
            )

    @opens
    def scp(self) -> SCPClient:
        """Get the SCP client object for the ConnectionPlus object.

        Will open an SCP client object if one is not already open.

        :raises AttributeError: If the base fabric Connection object does not have an SSH client initialized.
        :raises AttributeError: If the base fabric Connection object does not have an SCP client initialized.
        :raises AttributeError: If the ConnectionPlus object could not initialize it's client.
        :return: The SCP client object for the ConnectionPlus object.
        :rtype: SCPClient
        """
        if self._scp is None:
            try:
                self.open()
                if self.client is None:
                    raise AttributeError(
                        "The ConnectionPlus object could" " not initialize it's client."
                    )
                transport: Optional[Transport] = self.client.get_transport()
                if transport is None:
                    raise AttributeError(
                        "The ConnectionPlus object could"
                        " not initialize it's transport."
                    )
                self._scp = SCPClient(transport)
            except AttributeError:
                raise AttributeError(
                    "The base fabric Connection object does "
                    "not have a client initialized."
                )
        return self._scp

    def get(self, *args, **kwargs) -> Optional[fabric.transfer.Result]:
        """Get a file from the remote host.

        :param remote_path: The path to the file on the remote host.
        :param local_path: The path to save the file locally. Defaults to current working dir.
        :param scp: If the transfer should be done via SCP. Defaults to False or the Connection value.
        :param recursive: If the transfer should be recursive. Defaults to False.
        :param preserve_times: If the file times should be preserved. Defaults to False.
        :return: Result object from the transfer, or None.
        :rtype: Optional[fabric.transfer.Result]
        """
        _scp: Optional[bool] = kwargs.pop("scp", None) or self.__scp
        if _scp is not None and _scp is True:
            TransferPlus(self).get(*args, **kwargs)
            return None
        else:
            # not covering this, as its just a call to the base version and is covered by
            # fabric's base tests.
            return super().get(*args, **kwargs)  # pragma: no cover

    def put(self, *args, **kwargs) -> Optional[fabric.transfer.Result]:
        """Put a file on the remote host.

        :param local_path: The path to the file on the local host.
        :param remote_path: The path to save the file remotely. Defaults to current working dir for the session.
        :param scp: If the transfer should be done via SCP. Defaults to False or the Connection value.
        :param recursive: If the transfer should be recursive. Defaults to False.
        :param preserve_times: If the file times should be preserved. Defaults to False.
        :return: Result object from the transfer.
        :rtype: Optional[fabric.transfer.Result]
        """
        _scp: Optional[bool] = kwargs.pop("scp", None) or self.__scp
        if _scp is not None and _scp is True:
            TransferPlus(self).put(*args, **kwargs)
            return None
        else:
            # not covering this, as its just a call to the base version and is covered by
            # fabric's base tests.
            return super().put(*args, **kwargs)  # pragma: no cover
