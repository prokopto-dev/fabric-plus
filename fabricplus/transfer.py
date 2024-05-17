import fabric
from fabric.transfer import Transfer
import scp

from typing import Type
    
    

class TransferPlus(Transfer):
    """
    `.Connection`-wrapping and `.ConnectionPlus`-wrapping class responsible for managing file upload/download.

    .. versionadded:: 1.0
    """

    def __init__(self,
                 connection: Type[fabric.Connection]) -> None:
        self.connection: Type[fabric.Connection] = connection

    @property
    def scp(self) -> scp.SCPClient:
        try:
            return self.connection.scp() # type: ignore
        except AttributeError:
            raise AttributeError("The base fabric Connection object does not have an SCP client"
                                 ", use ConnectionPlus instead.")
    
    def get(self, *args, **kwargs) -> None:
        return self.scp.get(*args, **kwargs)
    
    def put(self, *args, **kwargs) -> None:
        return self.scp.put(*args, **kwargs)