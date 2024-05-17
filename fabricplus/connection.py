from fabric.connection import Connection, opens
import fabric.transfer
from fabricplus.transfer import TransferPlus
from paramiko import WarningPolicy, SSHClient, Transport
from fabricplus.paramiko_modifications.client import SSHJumpClient, simple_auth_handler
from scp import SCPClient

from typing import Optional, Union, Callable, List, Any

class ConnectionPlus(Connection):
    def __init__(self, *args, jumphost_target: Optional[Union[SSHJumpClient, SSHClient, str, Connection]] = None, scp: bool = False, jump_uname: Optional[str] = None, **kwargs):
        """
        Args:
        
        """
        super().__init__(*args, **kwargs)
        self._scp: Optional[SCPClient] = None
        self.__scp: bool = scp
        self.client = self.__setup_jumphost(jumphost_target=jumphost_target, username=jump_uname)
        self.client.set_missing_host_key_policy(WarningPolicy())
        self.client.load_system_host_keys()
        
    def __connect_client(self,
                         client: Union[SSHJumpClient, SSHClient],
                         username: Optional[str] = None) -> None:
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
            username=self.user,
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
        client.connect(**kwargs)
        return None
        
    
    def __setup_jumphost(self,
                         *args,
                         jumphost_target: Optional[Union[SSHJumpClient, SSHClient, str, Connection]],
                         interactive_prompt: bool = False,
                         jump_uname: Optional[str] = None,
                         **kwargs) -> SSHClient:
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
                self.__connect_client(_client)
            elif isinstance(jumphost_target, Connection):
                if jumphost_target.client is None:
                    jumphost_target.open()
                _client = jumphost_target.client
            else:
                raise TypeError("The jumphost_target must be an instance of SSHJumpClient, SSHClient, str, or Connection.")
        return SSHJumpClient(*args, jump_session=_client, auth_handler=_auth_handler, **kwargs)
    
    @property
    def jump_client(self) -> Optional[SSHJumpClient]:
        try:
            return self.client._jump_session # type: ignore
        except AttributeError:
            return None
    
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
        if self.__scp is True:
            return TransferPlus(self).get(*args, **kwargs)
        else:
            return super().get(*args, **kwargs)
        
        
    def put(self, *args, **kwargs) -> Optional[fabric.transfer.Result]:
        if self.__scp is True:
            return TransferPlus(self).put(*args, **kwargs)
        else:
            return super().put(*args, **kwargs)