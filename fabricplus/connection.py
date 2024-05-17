from fabric.connection import Connection
from fabricplus.transfer import TransferPlus

class ConnectionPlus(Connection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)