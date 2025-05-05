import subprocess
import sys
import os
import pytest

CONCORD_CLIENT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../concord232_client")
)
PYTHON = sys.executable


# Helper to run the CLI with arguments
def run_cli(args, input=None):
    cmd = [PYTHON, CONCORD_CLIENT] + args
    env = {**os.environ, "PYTHONUNBUFFERED": "1", "CONCORD232_TEST_MODE": "1"}
    result = subprocess.run(
        cmd,
        input=input,
        capture_output=True,
        text=True,
        env=env,
    )
    return result


@pytest.fixture(autouse=True)
def patch_client(monkeypatch):
    # Patch concord232.client.Client methods to avoid real HTTP calls
    import concord232.client.client

    monkeypatch.setattr(
        concord232.client.client.Client,
        "list_zones",
        lambda self: [
            {"number": 1, "name": "Front", "state": False, "type": "Door"},
            {"number": 2, "name": "Garage", "state": True, "type": "Motion"},
        ],
    )
    monkeypatch.setattr(
        concord232.client.client.Client,
        "list_partitions",
        lambda self: [
            {"number": 1, "zones": 2, "arming_level": "Off"},
            {"number": 2, "zones": 1, "arming_level": "Stay"},
        ],
    )
    monkeypatch.setattr(
        concord232.client.client.Client,
        "send_keys",
        lambda self, keys, group, partition=None: True,
    )
    monkeypatch.setattr(
        concord232.client.client.Client, "get_version", lambda self: "1.2.3"
    )
    monkeypatch.setattr(
        concord232.client.client.Client, "disarm", lambda self, pin: True
    )
    monkeypatch.setattr(
        concord232.client.client.Client, "arm", lambda self, level: True
    )
    yield


def test_summary_output():
    result = run_cli(["summary"])
    assert result.returncode == 0
    assert "Zone" in result.stdout
    assert "Front" in result.stdout
    assert "Garage" in result.stdout
    assert "Partition" in result.stdout
    assert "Stay" in result.stdout or "Off" in result.stdout


def test_arm_stay_partition():
    result = run_cli(["arm-stay", "--partition", "2"])
    assert result.returncode == 0


def test_disarm_requires_master():
    result = run_cli(["disarm"])
    assert result.returncode == 0
    assert "Master pin required" in result.stdout


def test_disarm_with_master():
    result = run_cli(["disarm", "--master", "1234", "--partition", "2"])
    assert result.returncode == 0


def test_keys_requires_keys():
    result = run_cli(["keys"])
    assert result.returncode == 0
    assert "Keys required" in result.stdout


def test_keys_with_args():
    result = run_cli(["keys", "--keys", "1234*", "--partition", "2"])
    assert result.returncode == 0


def test_version():
    result = run_cli(["version"])
    assert result.returncode == 0
    assert "1.2.3" in result.stdout
