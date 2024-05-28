import pytest
from unittest.mock import MagicMock, patch
import scp  # type: ignore
from fabricplus.transfer import TransferPlus


def test_transferplus_init():
    connection = MagicMock()
    transfer = TransferPlus(connection)
    assert transfer.connection == connection


@patch("scp.SCPClient", autospec=True)
def test_transferplus_scp(self):
    connection = MagicMock()
    connection.scp = MagicMock(return_value=scp.SCPClient)
    transfer = TransferPlus(connection)
    assert transfer.scp == scp.SCPClient


@patch("scp.SCPClient", autospec=True)
def test_transferplus_get(self):
    connection = MagicMock()
    connection.scp = MagicMock(return_value=scp.SCPClient)
    transfer = TransferPlus(connection)
    transfer.get("remote_path", "local_path")
    transfer.scp.get.assert_called_once_with("remote_path", "local_path")


@patch("scp.SCPClient", autospec=True)
def test_transferplus_put(self):
    connection = MagicMock()
    connection.scp = MagicMock(return_value=scp.SCPClient)
    transfer = TransferPlus(connection)
    transfer.put("local_path", "remote_path")
    transfer.scp.put.assert_called_once_with("local_path", "remote_path")


def test_transferplus_get_no_scp():
    connection = MagicMock()
    connection.scp = MagicMock(side_effect=AttributeError)
    transfer = TransferPlus(connection)
    with pytest.raises(AttributeError):
        transfer.get("remote_path", "local_path")
