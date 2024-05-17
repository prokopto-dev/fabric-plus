from fabric.connection import Connection, opens
from fabricplus.transfer import TransferPlus
from paramiko import WarningPolicy, SSHClient
from fabricplus.paramiko_modifications.client import SSHJumpClient
from scp import SCPClient

from typing import Optional, Union

class ConnectionPlus(Connection):
    def __init__(self, *args, jumphost_target: Optional[Union[SSHJumpClient, SSHClient, str, Connection]] = None, **kwargs):
        """
        Args:
        
        """
        super().__init__(*args, **kwargs)
        self._scp: Optional[SCPClient] = None
        self.client = self.__setup_jumphost(jumphost_target)
        self.client.set_missing_host_key_policy(WarningPolicy())
        self.client.load_system_host_keys()

        
    
    # def __setup_client(self, jumphost_target: Optional[Union[SSHJumpClient, SSHClient, str, Connection]] = None) -> SSHJumpClient:
        
    
    @opens
    def scp(self):
        if self._scp is None:
            try:
                # Ignoring type because we're handling the exception in cases of Nones.
                self._scp = SCPClient(self.client.get_transport()) # type: ignore
            except AttributeError:
                raise AttributeError("The base fabric Connection object does not have a client initialized.")
        return self._scp
