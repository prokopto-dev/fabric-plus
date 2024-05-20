import fabric
from fabric.transfer import Transfer
import scp

from typing import Type
    
    

class TransferPlus(Transfer):
    """TransferPlus is a subclass of the base fabric Transfer object, overloading
    the parent object to provide additional functionality for SCP transfers.
    """

    def __init__(self,
                 connection: Type[fabric.Connection]) -> None:
        """Initializes the TransferPlus object.
        

        Args:
            connection (Type[fabric.Connection]): The fabric Connection object to use for the transfer.
        """
        self.connection: Type[fabric.Connection] = connection

    @property
    def scp(self) -> scp.SCPClient:
        try:
            return self.connection.scp() # type: ignore
        except AttributeError:
            raise AttributeError("The base fabric Connection object does not have an SCP client"
                                 ", use ConnectionPlus instead.")
    
    def get(self, *args, **kwargs) -> None:
        """Get a file from the remote host.
        Args:
            remote_path (str): The path to the file on the remote host.
            local_path (str, optional): The path to save the file locally. Defaults to current working dir.
            recursive (bool, optional): If the transfer should be recursive. Defaults to False.
            preserve_times (bool, optional): If the file times should be preserved. Defaults to False.

        Returns:
            Optional[fabric.transfer.Result]: Result object from the transfer.
        """
        return self.scp.get(*args, **kwargs)
    
    def put(self, *args, **kwargs) -> None:
        return self.scp.put(*args, **kwargs)