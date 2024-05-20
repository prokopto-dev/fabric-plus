# External Imports
from fabric.connection import Connection, opens
import fabric.transfer
import re
from invoke.watchers import FailingResponder, Responder
from paramiko import WarningPolicy, SSHClient, Transport
from scp import SCPClient
from invoke.exceptions import Failure, ResponseNotAccepted, AuthFailure

# Internal Imports
from fabricplus.transfer import TransferPlus
from fabricplus.paramiko_modifications.client import SSHJumpClient, simple_auth_handler

# Typing Imports
from typing import Optional, Union, Callable, List, Any, TYPE_CHECKING
if TYPE_CHECKING:
    from invoke.runners import Runner, Result

class ConnectionPlus(Connection):
    """ConnectionPlus is a subclass of the Connection object from the Fabric library.
    
    This subclass provides additional functionality to the Connection object, such as SCP transfers,
    running commands as another user, and running commands on a jumphost, as well as connecting to 
    a host through a jumphost.
    """
    def __init__(self,
                 *args,
                 jumphost_target: Optional[Union[SSHJumpClient, SSHClient, str, Connection]] = None,
                 scp: bool = False, jump_uname: Optional[str] = None,
                 **kwargs):
        """Initialize the ConnectionPlus object.
        
        Initializes using the Connection initialization, but also sets up the client object
        for the ConnectionPlus object via a jumphost target.

        :param jumphost_target: 
            Jumphost to connect to the host through.
            Can be an instance of SSHJumpClient, SSHClient, URL/IP string,
            or Connection/ConnectionPlus.
            Defaults to None.
        :type jumphost_target: Optional[Union[SSHJumpClient, SSHClient, str, Connection]], optional
        :param scp:
            Boolean value to define if the ConnectionPlus object should
            use SCP for file transfers.
            Defaults to False.
        :type scp: bool, optional
        :param jump_uname:
            Username for the jumphost if different than the connection.
            Defaults to None.
        :type jump_uname: Optional[str], optional
        """
        super().__init__(*args, **kwargs)
        self._scp: Optional[SCPClient] = None
        self.__scp: bool = scp
        self.client = self.__client_setup(jumphost_target=jumphost_target, jump_uname=jump_uname)
        self.client.set_missing_host_key_policy(WarningPolicy())
        self.client.load_system_host_keys()
    
    def su(self,
           command: str,
           user: str,
           password:Optional[str] = None,
           timeout: int = 10,
           **kwargs: Any) -> Optional["Result"]:
        """Run a command as another user, via su.
        
        Requires the target user's password be given, either directly, or via the ConnectionPlus object.
        
        Note: This method doesn't work on Windows, as Windows doesn't have su, nor does it work in parallel on
        some systems due to the way su is implemented (e.g. it may require a tty).

        :param command: Command to run in su.
        :type command: str
        :param user: User to run the command as.
        :type user: str
        :param password: Password for the target user. Needed, but defaults to None.
        :type password: Optional[str]
        :param timeout: Timeout for the command. Defaults to 10.
        :type timeout: int, optional
        :param kwargs: Additional keyword arguments to pass to the command execution.
        :type kwargs: Any
        :raises ValueError: If the password is not given.
        :return: Result object from the command execution.
        :rtype: Optional[Result]
        """
        _password: str = password or self.connect_kwargs.get("password", None) # type: ignore
        if _password is None:
            raise ValueError("The password must be given to run a command as another user.")
        return self._su(runner=self._remote_runner(), command=command, password=_password, timeout=timeout, pty=True, **kwargs)
    
    def _su(self,
            runner: "Runner",
            command: str,
            user: str,
            password: Optional[str] = None,
            timeout: int = 10,
            **kwargs: Any) -> Optional["Result"]:
        """Internal representation to run a command as another user, via su.
        
        :param runner: The runner object to run the command.
        :type runner: Runner
        :param command: Command to run in su.
        :type command: str
        :param user: User to run the command as.
        :type user: str
        :param password: Password for the target user. Needed, but defaults to None.
        :type password: Optional[str]
        :param timeout: Timeout for the command. Defaults to 10.
        :type timeout: int, optional
        :param kwargs: Additional keyword arguments to pass to the command execution.
        :type kwargs: Any
        :raises AuthFailure: If the authentication fails.
        :raises failure: If the command execution fails.
        :return: Result object from the command execution.
        :rtype: Optional[Result]
        """
        _prompt: str = "Password: "
        _command: str = self._prefix_commands(command)
        # Escape all double quotes in the command.
        _cmd_str: str  = f'su - {user} -c "{command}"'.format(user=user, command=_command.replace('"', '\\"'))
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

    def __client_connect(self,
                         client: Union[SSHJumpClient, SSHClient],
                         username: Optional[str] = None) -> None:
        """Connect the client object for the ConnectionPlus object.
        
        Helps pass in the connect arguments from the Connection object.
        
        These include some loaded from SSH Config.
        
        :param client: The client object to connect.
        :type client: Union[SSHJumpClient, SSHClient]
        :param username: Username to connect with. Defaults to None.
        :type username: Optional[str], optional
        """        
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
        if (
            "timeout" in self.connect_kwargs
            and self.connect_timeout is not None
        ):
            raise ValueError(err.format("timeout"))
        # No conflicts -> merge 'em together
        kwargs = dict(
            self.connect_kwargs,
            username=username or self.user,
            hostname=self.host,
            port=self.port,
        )
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
        client.connect(**kwargs) # type: ignore
        return None
        
    
    def __client_setup(self,
                         *args,
                         jumphost_target: Optional[Union[SSHJumpClient, SSHClient, str, Connection]] = None,
                         interactive_prompt: bool = False,
                         jump_uname: Optional[str] = None,
                         **kwargs) -> Union[SSHClient, "SSHJumpClient"]:
        """Setup the client object for the ConnectionPlus object.
        
        This method can be used to setup the client object for the ConnectionPlus object.
        But it also can be used to setup the jumphost for the ConnectionPlus object.
        
        :param jumphost_target: Jumphost to run all actions through for this client. Defaults to None.
        :type jumphost_target: Optional[Union[SSHJumpClient, SSHClient, str, Connection]], optional
        :param interactive_prompt: Whether to use an interactive method for the jumphost connectivity. Defaults to False.
        :type interactive_prompt: bool, optional
        :param jump_uname: Username for jumphost if different than connection. Defaults to None.
        :type jump_uname: Optional[str], optional
        :raises TypeError: If the jumphost_target is not an instance of SSHJumpClient, SSHClient, URL/IP string, or Connection/ConnectionPlus.
        :return: The SSHClient object for the ConnectionPlus object.
        :rtype: Union[SSHClient/SSHJumpClient]
        """
        _client: Optional[Union[SSHJumpClient, SSHClient]] = None
        _auth_handler: Optional[Callable[..., List[Any]]] = simple_auth_handler if interactive_prompt else None
        if jumphost_target is not None:
            if isinstance(jumphost_target, SSHJumpClient):
                _client = jumphost_target
            elif isinstance(jumphost_target, SSHClient):
                _client = jumphost_target
            elif isinstance(jumphost_target, str):
                _client = SSHJumpClient(auth_handler=_auth_handler)
                _client.set_missing_host_key_policy(WarningPolicy())
                _client.load_system_host_keys()
                self.__client_connect(_client, username=jump_uname or self.user)
            elif isinstance(jumphost_target, Connection) or isinstance(jumphost_target, ConnectionPlus):
                if jumphost_target.client is None:
                    jumphost_target.open()
                _client = jumphost_target.client
            else:
                raise TypeError("The jumphost_target must be an instance of SSHJumpClient, SSHClient, URL/IP string, or Connection/ConnectionPlus.")
        return SSHJumpClient(*args, jump_session=_client, auth_handler=_auth_handler, **kwargs)
    
    @property
    def jump_client(self) -> Optional[SSHJumpClient]:
        """Get the jump client object for the ConnectionPlus object.

        Returns:
            Optional[SSHJumpClient]: The jump client object for the ConnectionPlus object.
        """
        try:
            return self.client._jump_session # type: ignore
        except AttributeError:
            return None
        
    def jump_run(self, command: str, timeout: int = 10, **kwargs) -> Optional["Result"]:
        """Run a command on the jumphost.

        Args:
            command (str): Command to run on the jumphost.
            timeout (int, optional): Timeout for the command. Defaults to 10.

        Returns:
            Optional[Result]: Result object from the command execution.
        """
        if self.jump_client is None:
            raise AttributeError("The ConnectionPlus object does not have a jump client initialized.")
        try:
            _timeout: int = kwargs.pop("timeout", timeout)
            _, _stdout, _stderr = self.jump_client.exec_command(command, timeout=_timeout, **kwargs) or (None, None, None)
            _stderr_str: str = _stderr.read().decode("utf-8").strip("\n") # type: ignore
            _stdout_str: str = _stdout.read().decode("utf-8").strip("\n") # type: ignore
            return Result(stdout=_stdout_str, stderr=_stderr_str, exited=0, encoding="utf-8", command=command)
        except Exception as e:
            return Result(stdout="", stderr=str(e), exited=1, encoding="utf-8", command=command)
        
        
    
    @opens
    def scp(self):
        if self._scp is None:
            try:
                # Ignoring type because we're handling the exception in cases of Nones.
                transport: Optional[Transport] = self.client.get_transport() # type: ignore
                if transport is None:
                    # Connection may not have opened the client yet,
                    # so lets open the client connection
                    self.open()
                    transport = self.client.get_transport()
                self._scp = SCPClient(transport) # type: ignore
            except AttributeError:
                raise AttributeError("The base fabric Connection object does not have a client initialized.")
        return self._scp

    def get(self, *args, **kwargs) -> Optional[fabric.transfer.Result]:
        """Get a file from the remote host.
        
        Args:
            remote_path (str): The path to the file on the remote host.
            local_path (str, optional): The path to save the file locally. Defaults to current working dir.
            scp (bool, optional): If the transfer should be done via SCP. Defaults to False or the Connection value.
            recursive (bool, optional): If the transfer should be recursive. Defaults to False.
            preserve_times (bool, optional): If the file times should be preserved. Defaults to False.

        Returns:
            Optional[fabric.transfer.Result]: Result object from the transfer.
        """
        _scp: bool = kwargs.pop("scp", None) or self.__scp
        if _scp is True:
            # Ignoring type because apparently it doesn't like Self@ConnectionPlus
            return TransferPlus(self).get(*args, **kwargs) # type: ignore
        else:
            return super().get(*args, **kwargs)
        
        
    def put(self, *args, **kwargs) -> Optional[fabric.transfer.Result]:
        """Get a file from the remote host.
        
        Args:
            local_path (str): The path to the file locally.
            remote_path (str, optional): The path to save the file on the remote host. Defaults to current working dir.
            scp (bool, optional): If the transfer should be done via SCP. Defaults to False or the Connection value.
            recursive (bool, optional): If the transfer should be recursive. Defaults to False.
            preserve_times (bool, optional): If the file times should be preserved. Defaults to False.

        Returns:
            Optional[fabric.transfer.Result]: Result object from the transfer.
        """
        _scp: bool = kwargs.pop("scp", None) or self.__scp
        if _scp is True:
            # Ignoring type because apparently it doesn't like Self@ConnectionPlus
            return TransferPlus(self).put(*args, **kwargs) # type: ignore
        else:
            return super().put(*args, **kwargs)