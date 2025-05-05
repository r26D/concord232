from unittest.mock import MagicMock

import pytest

from concord232.client.client import Client


@pytest.fixture
def client():
    c = Client("http://localhost")
    c._session = MagicMock()
    return c


def test_list_zones_json_method(client):
    resp = MagicMock()
    resp.json = {"zones": [1, 2]}
    client._session.get.return_value = resp
    assert client.list_zones() == [1, 2]


def test_list_zones_json_callable(client):
    resp = MagicMock()
    resp.json = lambda: {"zones": [3, 4]}
    client._session.get.return_value = resp
    assert client.list_zones() == [3, 4]


def test_list_partitions_json_method(client):
    resp = MagicMock()
    resp.json = {"partitions": [1, 2]}
    client._session.get.return_value = resp
    assert client.list_partitions() == [1, 2]


def test_list_partitions_json_callable(client):
    resp = MagicMock()
    resp.json = lambda: {"partitions": [3, 4]}
    client._session.get.return_value = resp
    assert client.list_partitions() == [3, 4]


def test_arm(client):
    resp = MagicMock(status_code=200)
    client._session.get.return_value = resp
    assert client.arm("stay") is True
    resp.status_code = 400
    assert client.arm("stay") is False


def test_disarm(client):
    resp = MagicMock(status_code=200)
    client._session.get.return_value = resp
    assert client.disarm("1234") is True
    resp.status_code = 400
    assert client.disarm("1234") is False


def test_send_keys(client):
    resp = MagicMock(status_code=200)
    client._session.get.return_value = resp
    assert client.send_keys("1", group=True, partition=2) is True
    resp.status_code = 400
    assert client.send_keys("1", group=True, partition=2) is False


def test_get_version_404(client):
    resp = MagicMock(status_code=404)
    client._session.get.return_value = resp
    assert client.get_version() == "1.0"


def test_get_version_success(client):
    resp = MagicMock(status_code=200)
    resp.json.return_value = {"version": "1.2"}
    client._session.get.return_value = resp
    assert client.get_version() == "1.2"
