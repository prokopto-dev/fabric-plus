from fabric.connection import Connection, opens
from fabricplus.transfer import TransferPlus
from fabricplus.paramiko_modifications.client import SSHJumpClient
from scp import SCPClient

from typing import Optional

class ConnectionPlus(Connection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._scp: Optional[SCPClient] = None
        self.client = SSHJumpClient()
    
    @opens
    def scp(self):
        if self._scp is None:
            try:
                # Ignoring type because we're handling the exception in cases of Nones.
                self._scp = SCPClient(self.client.get_transport()) # type: ignore
            except AttributeError:
                raise AttributeError("The base fabric Connection object does not have a client initialized.")
        return self._scp
