from fabric.connection import Connection, opens
import fabric.transfer
from fabricplus.transfer import TransferPlus
from paramiko import WarningPolicy, SSHClient, Transport, PKey
from socket import socket
from fabricplus.paramiko_modifications.client import SSHJumpClient
from scp import SCPClient

from typing import Optional, Union

class ConnectionPlus(Connection):
    def __init__(self, *args, jumphost_target: Optional[Union[SSHJumpClient, SSHClient, str, Connection]] = None, scp: bool = False, **kwargs):
        """
        Args:
        
        """
        super().__init__(*args, **kwargs)
        self._scp: Optional[SCPClient] = None
        self.__scp: bool = scp
        self.client = self.__setup_jumphost(jumphost_target=jumphost_target)
        self.client.set_missing_host_key_policy(WarningPolicy())
        self.client.load_system_host_keys()
        
    
    def __setup_jumphost(self, *args, jumphost_target: Optional[Union[SSHJumpClient, SSHClient, str, Connection]], **kwargs) -> SSHClient:
        _client: Optional[Union[SSHJumpClient, SSHClient]] = None
        if jumphost_target is not None:
            if isinstance(jumphost_target, SSHJumpClient):
                _client = jumphost_target
            elif isinstance(jumphost_target, SSHClient):
                _client = jumphost_target
            elif isinstance(jumphost_target, str):
                _client = SSHJumpClient()
                _client.set_missing_host_key_policy(WarningPolicy())
                _client.load_system_host_keys()
                _client.connect(hostname=jumphost_target, **kwargs)
            elif isinstance(jumphost_target, Connection):
                if jumphost_target.client is None:
                    jumphost_target.open()
                _client = jumphost_target.client
            else:
                raise TypeError("The jumphost_target must be an instance of SSHJumpClient, SSHClient, str, or Connection.")
        return SSHJumpClient(*args, jump_session=_client, **kwargs)
    
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