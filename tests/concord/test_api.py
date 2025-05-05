import pytest
from unittest.mock import MagicMock, patch
from concord232 import api

@pytest.fixture
def client():
    api.CONTROLLER = MagicMock()
    api.CONTROLLER.panel = {'status': 'ok'}
    api.CONTROLLER.zones = {1: {'partition_number': 1, 'area_number': 1, 'group_number': 1, 'zone_number': 1, 'zone_text': 'Zone 1', 'zone_state': 'open', 'zone_type': 'door'}}
    api.CONTROLLER.partitions = {1: {'partition_number': 1, 'area_number': 1, 'arming_level': 1, 'arming_level_code': 1, 'partition_text': 'Partition 1'}}
    with api.app.test_client() as client:
        yield client

def test_panel(client):
    resp = client.get('/panel')
    assert resp.status_code == 200
    assert 'panel' in resp.get_json()

def test_zones(client):
    resp = client.get('/zones')
    assert resp.status_code == 200
    assert 'zones' in resp.get_json()
    assert isinstance(resp.get_json()['zones'], list)

def test_partitions(client):
    resp = client.get('/partitions')
    assert resp.status_code == 200
    assert 'partitions' in resp.get_json()
    assert isinstance(resp.get_json()['partitions'], list)

def test_command_arm_stay(client):
    resp = client.get('/command?cmd=arm&level=stay')
    assert resp.status_code == 200
    api.CONTROLLER.arm_stay.assert_called()

def test_command_arm_away(client):
    resp = client.get('/command?cmd=arm&level=away')
    assert resp.status_code == 200
    api.CONTROLLER.arm_away.assert_called()

def test_command_disarm(client):
    resp = client.get('/command?cmd=disarm&master_pin=1234')
    assert resp.status_code == 200
    api.CONTROLLER.disarm.assert_called_with('1234')

def test_command_keys(client):
    resp = client.get('/command?cmd=keys&keys=*&group=1&partition=1')
    assert resp.status_code == 200
    api.CONTROLLER.send_keys.assert_called()

def test_version(client):
    resp = client.get('/version')
    assert resp.status_code == 200
    assert resp.get_json()['version'] == '1.1'

def test_equipment(client):
    resp = client.get('/equipment')
    assert resp.status_code == 200
    api.CONTROLLER.request_all_equipment.assert_called()

def test_all_data(client):
    resp = client.get('/all_data')
    assert resp.status_code == 200
    api.CONTROLLER.request_dynamic_data_refresh.assert_called() 