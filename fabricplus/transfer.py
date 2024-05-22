import fabric
from fabric.transfer import Transfer
import scp

from typing import Union, TypeVar

# Type hint for a fabric Connection object.
Conn = TypeVar("Conn", bound=fabric.connection.Connection)

class TransferPlus(Transfer):
    """TransferPlus is a subclass of the base fabric Transfer object, overloading
    the parent object to provide additional functionality for SCP transfers.
    """

    def __init__(self,
                 connection: Conn) -> None:
        """Initializes the TransferPlus object.

        :param connection: A fabric Connection-like object.
        :type connection: fabric.Connection
        """
        self.connection: Conn = connection

    @property
    def scp(self) -> scp.SCPClient:
        """Returns an SCP client object for the connection.

        :raises AttributeError: If the base fabric Connection object does not have an SCP client.
        :return: An SCP client object.
        :rtype: scp.SCPClient
        """
        try:
            return self.connection.scp()
        except AttributeError:
            raise AttributeError("The base fabric Connection object does not have an SCP client"
                                 ", use ConnectionPlus instead.")
    
    def get(self, *args, **kwargs) -> None:
        """Get a file from the remote host.
        
        :param remote_path: The path to the file on the remote host.
        :type remote_path: str
        :param local_path: The path to save the file locally. Defaults to current working dir.
        :type local_path: str, optional
        :param scp: If the transfer should be done via SCP. Defaults to False or the Connection value.
        :type scp: bool, optional
        :param recursive: If the transfer should be recursive. Defaults to False.
        :type recursive: bool, optional
        :param preserve_times: If the file times should be preserved. Defaults to False.
        :type preserve_times: bool, optional
        :return: None
        :rtype: None
        """
        return self.scp.get(*args, **kwargs)
    
    def put(self, *args, **kwargs) -> None:
        """Put a file on the remote host.
        
        :param local_path: The path to the file on the local host.
        :type local_path: str
        :param remote_path: The path to save the file remotely. Defaults to current working dir for the session.
        :type remote_path: str, optional
        :param scp: If the transfer should be done via SCP. Defaults to False or the Connection value.
        :type scp: bool, optional
        :param recursive: If the transfer should be recursive. Defaults to False.
        :type recursive: bool, optional
        :param preserve_times: If the file times should be preserved. Defaults to False.
        :type preserve_times: bool, optional
        :return: None
        :rtype: None
        """
        return self.scp.put(*args, **kwargs)