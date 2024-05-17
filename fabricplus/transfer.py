import fabric
import scp

from typing import Optional, Any

class TransferPlus:
    """
    `.Connection`-wrapping class responsible for managing file upload and download via SCP.
    
    Currently utilizes the paramiko based `scp.py` library.
    """

    def __init__(self,
                 connection: fabric.Connection,
                 buffer_size: int = 16384,
                 socket_timeout: int = 10,
                 progress: Optional[Any] = None,
                 progress4: Optional[Any] = None,
                 limit_bw: Optional[Any] = None) -> None :
        self.connection: fabric.Connection = connection
        self.scp: scp.SCPClient = scp.SCPClient(transport=self.connection.client.get_transport(),
                                                buff_size=buffer_size,
                                                socket_timeout=socket_timeout,
                                                progress=progress,
                                                progress4=progress4,
                                                limit_bw=limit_bw)


    def put(self,
            local_path: str,
            remote_path: str = '.',
            preserve_times: bool = True,
            recursive: bool = False) -> None:
        """
        Uploads a file from the local filesystem to the remote filesystem.
        
        Direct passthrough wrapper of the `scp.put` method.
        
        Parameters:
            local_path (required, str): Path to the local file to upload.
            remote_path (optional, str): Path to the remote location to upload to. 
                Default is the current remote directory.
            preserve_times (optional, bool): Whether or not to preserve the file's timestamps. Default is True.
            recursive (optional, bool): Whether or not to upload the file recursively. Default is False.
        """
        self.scp.put(local_path, remote_path,recursive=recursive, preserve_times=preserve_times)
    
    def get(self, remote_path: str, local_path: str ='.', preserve_times: bool = True, recursive: bool = False) -> None:
        """
        Downloads a file from the remote filesystem to the local filesystem.
        
        Direct passthrough wrapper of the `scp.get` method.
        
        Parameters:
            remote_path (required, str): Path to the remote file to download.
            local_path (optional, str): Path to the local location to download to. 
                Default is the current local directory.
            preserve_times (optional, bool): Whether or not to preserve the file's timestamps. Default is True.
            recursive (optional, bool): Whether or not to download the file recursively. Default is False.
        """
        self.scp.get(remote_path, local_path, recursive=recursive, preserve_times=preserve_times)
    
    def __enter__(self) -> None:
        """Allows for context usage of the `with` statement with a SCPTransfer object.
        """
        self.scp.__enter__()
    
    def __exit__(self, *args, **kwargs) -> None:
        """Allows for context usage of the `with` statement with a SCPTransfer object.
        """
        self.scp.__exit__(*args, **kwargs)
        
    def close(self) -> None:
        self.scp.close()

