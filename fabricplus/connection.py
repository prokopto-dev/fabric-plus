from fabric.connection import Connection
from fabricplus.transfer import TransferPlus

class ConnectionPlus(Connection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scp: TransferPlus = TransferPlus(self)
    
    def put(self, local_path, remote_path='.', preserve_times=True, recursive=False):
        self.scp.put(local_path, remote_path, recursive=recursive, preserve_times=preserve_times)
    
    def get(self, remote_path, local_path='.', preserve_times=True, recursive=False):
        self.scp.get(remote_path, local_path, recursive=recursive, preserve_times=preserve_times)
    
    def __enter__(self):
        self.scp.__enter__()
    
    def __exit__(self, *args, **kwargs):
        self.scp.__exit__(*args, **kwargs)
    
    def close(self):
        self.scp.close()