from unittest.mock import patch
from concord232.client import Client

class DualJSONMock:
    def __init__(self, value):
        self._value = value
    @property
    def json(self):
        return self._value
    def json_method(self):
        return self._value
    def __getattr__(self, name):
        if name == 'json':
            return self.json_method
        raise AttributeError(name)

@patch('concord232.client.requests.Session')
def test_list_zones(mock_session):
    mock_instance = mock_session.return_value
    mock_response = DualJSONMock({'zones': [1,2,3]})
    mock_instance.get.return_value = mock_response
    client = Client('http://fake')
    assert client.list_zones() == [1,2,3]

@patch('concord232.client.requests.Session')
def test_list_partitions(mock_session):
    mock_instance = mock_session.return_value
    mock_response = DualJSONMock({'partitions': [4,5]})
    mock_instance.get.return_value = mock_response
    client = Client('http://fake')
    assert client.list_partitions() == [4,5]

@patch('concord232.client.requests.Session')
def test_arm(mock_session):
    mock_instance = mock_session.return_value
    mock_instance.get.return_value.status_code = 200
    client = Client('http://fake')
    assert client.arm('stay') is True

@patch('concord232.client.requests.Session')
def test_disarm(mock_session):
    mock_instance = mock_session.return_value
    mock_instance.get.return_value.status_code = 200
    client = Client('http://fake')
    assert client.disarm('1234') is True

@patch('concord232.client.requests.Session')
def test_send_keys(mock_session):
    mock_instance = mock_session.return_value
    mock_instance.get.return_value.status_code = 200
    client = Client('http://fake')
    assert client.send_keys('*', group=True, partition=2) is True

@patch('concord232.client.requests.Session')
def test_get_version(mock_session):
    mock_instance = mock_session.return_value
    mock_instance.get.return_value.status_code = 200
    mock_instance.get.return_value.json.return_value = {'version': '1.2'}
    client = Client('http://fake')
    assert client.get_version() == '1.2' 