import fabric
from fabric.transfer import Transfer
import scp

from typing import Optional, Any, TYPE_CHECKING, Union
if TYPE_CHECKING:
    from fabricplus.connection import ConnectionPlus
    
    

class TransferPlus(Transfer):
    """
    `.Connection`-wrapping and `.ConnectionPlus`-wrapping class responsible for managing file upload/download.

    .. versionadded:: 1.0
    """

    def __init__(self,
                 connection: Union[fabric.Connection, ConnectionPlus]) -> None:
        self.connection: Union[fabric.Connection, ConnectionPlus] = connection

    @property
    def scp(self):
        try:
            return self.connection.scp
        except AttributeError:
            raise AttributeError("The base fabric Connection object does not have an SCP client"
                                 ", use ConnectionPlus instead.")
    
    def get(self, *args, **kwargs) -> None:
        return self.scp.get(*args, **kwargs)
    
    def put(self, *args, **kwargs) -> None:
        return self.scp.put(*args, **kwargs)