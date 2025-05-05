from typing import Any, Dict, List, Optional, cast

import requests


class Client(object):
    """
    Client for interacting with the concord232 server HTTP API.
    Provides methods to list zones, partitions, arm/disarm, send keys, and get version info.
    """

    def __init__(self, url: str) -> None:
        """
        Initialize the client with the server URL.
        Args:
            url (str): Base URL of the concord232 server.
        """
        self._url = url
        self._session = requests.Session()
        self._last_event_index = 0

    def list_zones(self) -> List[Dict[str, Any]]:
        """
        Retrieve the list of zones from the server.
        Returns:
            list: List of zone dictionaries.
        """
        r = self._session.get(self._url + "/zones")
        data = r.json()
        return cast(List[Dict[str, Any]], data["zones"])

    def list_partitions(self) -> List[Dict[str, Any]]:
        """
        Retrieve the list of partitions from the server.
        Returns:
            list: List of partition dictionaries.
        """
        r = self._session.get(self._url + "/partitions")
        data = r.json()
        return cast(List[Dict[str, Any]], data["partitions"])

    def arm(self, level: str, option: Optional[str] = None) -> bool:
        """
        Arm the system to the specified level with an optional option.
        Args:
            level (str): 'stay' or 'away'.
            option (str, optional): 'silent' or 'instant'.
        Returns:
            bool: True if successful, False otherwise.
        """
        params: Dict[str, str] = {"cmd": "arm", "level": level}
        if option is not None:
            params["option"] = option
        r = self._session.get(self._url + "/command", params=params)
        return r.status_code == 200

    def disarm(self, master_pin: str) -> bool:
        """
        Disarm the system using the master PIN.
        Args:
            master_pin (str): The master PIN code.
        Returns:
            bool: True if successful, False otherwise.
        """
        params: Dict[str, str] = {"cmd": "disarm", "master_pin": master_pin}
        r = self._session.get(self._url + "/command", params=params)
        return r.status_code == 200

    def send_keys(self, keys: str, group: bool = False, partition: int = 1) -> bool:
        """
        Send keypresses to the panel.
        Args:
            keys (str): Keys to send.
            group (bool): Whether to send as a group.
            partition (int): Partition number.
        Returns:
            bool: True if successful, False otherwise.
        """
        params: Dict[str, str] = {
            "cmd": "keys",
            "keys": keys,
            "group": str(group).lower(),
            "partition": str(partition),
        }
        r = self._session.get(self._url + "/command", params=params)
        return r.status_code == 200

    def get_version(self) -> str:
        """
        Get the API version from the server.
        Returns:
            str: Version string.
        """
        r = self._session.get(self._url + "/version")
        if r.status_code == 404:
            return "1.0"
        else:
            data = r.json()
            return cast(str, data["version"])
