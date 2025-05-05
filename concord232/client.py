import requests


class Client(object):
    """
    Client for interacting with the concord232 server HTTP API.
    Provides methods to list zones, partitions, arm/disarm, send keys, and get version info.
    """
    def __init__(self, url):
        """
        Initialize the client with the server URL.
        Args:
            url (str): Base URL of the concord232 server.
        """
        self._url = url
        self._session = requests.Session()
        self._last_event_index = 0

    def list_zones(self):
        """
        Retrieve the list of zones from the server.
        Returns:
            list: List of zone dictionaries.
        """
        r = self._session.get(self._url + '/zones')
        try:
            return r.json['zones']
        except TypeError:
            return r.json()['zones']

    def list_partitions(self):
        """
        Retrieve the list of partitions from the server.
        Returns:
            list: List of partition dictionaries.
        """
        r = self._session.get(self._url + '/partitions')
        try:
            return r.json['partitions']
        except TypeError:
            return r.json()['partitions']

    def arm(self, level, option = None):
        """
        Arm the system to the specified level with an optional option.
        Args:
            level (str): 'stay' or 'away'.
            option (str, optional): 'silent' or 'instant'.
        Returns:
            bool: True if successful, False otherwise.
        """
        r = self._session.get(
            self._url + '/command',
            params={'cmd': 'arm',
                    'level': level,
                    'option': option})
        return r.status_code == 200

    def disarm(self, master_pin):
        """
        Disarm the system using the master PIN.
        Args:
            master_pin (str): The master PIN code.
        Returns:
            bool: True if successful, False otherwise.
        """
        r = self._session.get(
            self._url + '/command',
            params={'cmd': 'disarm',
                    'master_pin': master_pin})
        return r.status_code == 200

    def send_keys(self, keys, group=False, partition=1):
        """
        Send keypresses to the panel.
        Args:
            keys (str): Keys to send.
            group (bool): Whether to send as a group.
            partition (int): Partition number.
        Returns:
            bool: True if successful, False otherwise.
        """
        r = self._session.get(
            self._url + '/command',
            params={'cmd': 'keys',
                    'keys': keys,
                    'group': group,
                    'partition': partition})
        return r.status_code == 200

    def get_version(self):
        """
        Get the API version from the server.
        Returns:
            str: Version string.
        """
        r = self._session.get(self._url + '/version')
        if r.status_code == 404:
            return '1.0'
        else:
            return r.json()['version']
