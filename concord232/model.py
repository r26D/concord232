"""
Data models for zones, partitions, system, log events, users, and extension hooks for concord232.
"""

from typing import Any, Dict, List, Optional, Tuple

MSG_TYPES = [
    "UNUSED",
    "Interface Configuration",
    "Reserved",
    "Zone Name",
    "Zone Status",
    "Zones Snapshot",
    "Partition Status",
    "Partitions Snapshot",
    "System Status",
    "X-10 Message Received",
    "Log Event",
    "Keypad Message Received",
    "Reserved",
    "Reserved",
    "Reserved",
    "Reserved",
    "Program Data Reply",
    "Reserved",
    "User Information Reply",
    "Reserved",
    "Reserved",
    "Reserved",
    "Reserved",
    "Reserved",
    "Reserved",
    "Reserved",
    "Reserved",
    "Reserved",
    "Command Failed",
    "Positive Acknowledge",
    "Negative Acknowledge",
    "Message Rejected",
    # 0x20
    "Reserved",
    "Interface Configuration Request",
    "Reserved",
    "Zone Name Request",
    "Zone Status Request",
    "Zones Snapshot Request",
    "Partition Status Request",
    "Partitions Snapshot Request",
    "System Status Request",
    "Send X-10 Message",
    "Log Event Request",
    "Send Keypad Text Message",
    "Keypad Terminal Mode REquest",
    "Reserved",
    "Reserved",
    "Reserved",
    "Program Data Request",
    "Program Data Command",
    "User Information Request with PIN",
    "User Information Request without PIN",
    "Set User Code Command with PIN",
    "Set User Code Command without PIN",
    "Set User Authorization Command with PIN",
    "Set User Authorization Command without PIN",
    "Reserved",
    "Reserved",
    "Store Communication Event Command",
    "Set Clock / Calendar Command",
    "Primary Keypad Function with PIN",
    "Primary Keypad Function without PIN",
    "Secondary Keypad Function",
    "Zone Bypass Toggle",
]


class Zone(object):
    """
    Represents a security system zone, including its number, name, state, and flags.
    """

    STATUS_FLAGS: List[str] = [
        "Faulted",
        "Trouble",
        "Bypass",
        "Inhibit",
        "Low battery",
        "Loss of supervision",
        "Reserved",
    ]

    TYPE_FLAGS: List[List[str]] = [
        [
            "Fire",
            "24 hour",
            "Key-switch",
            "Follower",
            "Entry / exit delay 1",
            "Entry / exit delay 2",
            "Interior",
            "Local only",
        ],
        [
            "Keypad sounder",
            "Yelping Siren",
            "Steady Siren",
            "Chime",
            "Bypassable",
            "Group bypassable",
            "Force armable",
            "Entry guard",
        ],
        [
            "Fast loop response",
            "Double EOL tamper",
            "Trouble",
            "Cross zone",
            "Dialer delay",
            "Swinger shutdown",
            "Restorable",
            "Listen in",
        ],
    ]

    def __init__(self, number: int) -> None:
        """
        Initialize a Zone.
        Args:
            number (int): Zone number.
        """
        self.number: int = number
        self.name: str = "Unknown"
        self.state: Optional[Any] = None
        self.condition_flags: List[str] = []
        self.type_flags: List[str] = []

    @property
    def bypassed(self) -> bool:
        """
        Returns True if the zone is bypassed or inhibited.
        """
        return "Inhibit" in self.condition_flags or "Bypass" in self.condition_flags


class Partition(object):
    """
    Represents a security system partition, including its number and condition flags.
    """

    CONDITION_FLAGS: List[List[str]] = [
        [
            "Bypass code required",
            "Fire trouble",
            "Fire",
            "Pulsing buzzer",
            "TLM fault memory",
            "reserved",
            "Armed",
            "Instant",
        ],
        [
            "Previous alarm",
            "Siren on",
            "Steady siren on",
            "Alarm memory",
            "Tamper",
            "Cancel command entered",
            "Code entered",
            "Cancel pending",
        ],
        [
            "Reserved",
            "Silent exit enabled",
            "Entryguard (stay mode)",
            "Chime mode on",
            "Entry",
            "Delay expiration warning",
            "Exit 1",
            "Exit 2",
        ],
        [
            "LED extinguish",
            "Cross timing",
            "Recent closing being timed",
            "Reserved",
            "Exit error triggered",
            "Auto home inhibited",
            "Sensor low battery",
            "Sensor lost supervision",
        ],
        [
            "Zone bypassed",
            "Force arm triggered by auto arm",
            "Ready to arm",
            "Ready to force arm",
            "Valid PIN accepted",
            "Chime on (sounding)",
            "Error beep (triple beep)",
            "Tone on (activation tone)",
        ],
        [
            "Entry 1",
            "Open period",
            "Alarm sent using phone number 1",
            "Alarm sent using phone number 2",
            "Alarm sent using phone number 3",
            "Cancel report is in the stack",
            "Keyswitch armed",
            "Delay trip in progress (common zone)",
        ],
    ]

    def __init__(self, number: int) -> None:
        """
        Initialize a Partition.
        Args:
            number (int): Partition number.
        """
        self.number: int = number
        self.condition_flags: List[str] = []
        self.last_user: Optional[Any] = None

    @property
    def armed(self) -> bool:
        """
        Returns True if the partition is armed.
        """
        return "Armed" in self.condition_flags


class System(object):
    """
    Represents the overall system state, including panel ID and status flags.
    """

    STATUS_FLAGS: List[List[str]] = [
        [
            "Line seizure",
            "Off hook",
            "Initial handshake received",
            "Download in progress",
            "Dialer delay in progress",
            "Using backup phone",
            "Listen in active",
            "Two way lockout",
        ],
        [
            "Ground fault",
            "Phone fault",
            "Fail to communicate",
            "Fuse fault",
            "Box tamper",
            "Siren tamper/trouble",
            "Low battery",
            "AC fail",
        ],
        [
            "Expander box tamper",
            "Expander AC failure",
            "Expander low battery",
            "Expander loss of supervision",
            "Expander auxiliary output over current",
            "Auxiliary communication channel failure",
            "Expander bell fault",
            "Reserved",
        ],
        [
            "6 digit PIN enabled",
            "Programming token in use",
            "PIN required for local download",
            "Global pulsing buzzer",
            "Global Siren on",
            "Global steady siren",
            "Bus device has line seized",
            "Bus device has requested sniff mode",
        ],
        [
            "Dynamic battery test",
            "AC power on",
            "Low battery memory",
            "Ground fault memory",
            "Fire alarm verification being timed",
            "Smoke power reset",
            "50 Hz line power detected",
            "Timing a high voltage battery change",
        ],
        [
            "Communication since last autotest",
            "Power up delay in progress",
            "Walk test mode",
            "Loss of system time",
            "Enroll requested",
            "Test fixture mode",
            "Control shutdown mode",
            "Timing a cancel window",
        ],
        [
            "reserved",
            "reserved",
            "reserved",
            "reserved",
            "reserved",
            "reserved",
            "reserved",
            "Call back in progress",
        ],
        [
            "Phone line faulted",
            "Voltage present interrupt active",
            "House phone off hook",
            "Phone line monitor enabled",
            "Sniffing",
            "Last read was off hook",
            "Listen in requested",
            "Listen in trigger",
        ],
        [
            "Valid partition 1",
            "Valid partition 2",
            "Valid partition 3",
            "Valid partition 4",
            "Valid partition 5",
            "Valid partition 6",
            "Valid partition 7",
            "Valid partition 8",
        ],
    ]

    def __init__(self) -> None:
        """
        Initialize a System object.
        """
        self.panel_id: Optional[int] = None
        self.status_flags: List[str] = []
        self.last_event: Optional[Any] = None


class LogEvent(object):
    """
    Represents a log event from the panel, including event codes and metadata.
    """

    ZONE_EVENT_CODES: Dict[int, str] = {
        0: "Alarm",
        1: "Alarm restore",
        2: "Bypass",
        3: "Bypass restore",
        4: "Tamper",
        5: "Tamper restore",
        6: "Trouble",
        7: "Trouble restore",
        8: "TX low battery",
        9: "TX low battery restore",
        10: "Zone lost",
        11: "Zone lost restore",
        12: "Start of cross time",
    }

    NONE_EVENT_CODES: Dict[int, str] = {
        17: "Special expansion event",
        18: "Duress",
        19: "Manual fire",
        20: "Auxiliary 2 panic",
        22: "Panic",
        23: "Keypad tamper",
        34: "Telephone fault",
        35: "Telephone fault restore",
        38: "Fail to communicate",
        39: "Log full",
        44: "Auto-test",
        45: "Start program",
        46: "End program",
        47: "Start download",
        48: "End download",
        50: "Ground fault",
        51: "Ground fault restore",
        52: "Manual test",
        54: "Start of listen in",
        55: "Technician on site",
        56: "Technician left",
        57: "Control power up",
        119: "Time set",
        123: "Begin walk-test",
        124: "End walk-test",
        125: "Re-exit",
        127: "Data lost",
    }

    DEVICE_EVENT_CODES: Dict[int, str] = {
        24: "Control box tamper",
        25: "Control box tamper restore",
        26: "AC fail",
        27: "AC fail restore",
        28: "Low battery",
        29: "Low battery restore",
        30: "Over current",
        31: "Over current restore",
        32: "Siren tamper",
        33: "Siren tamper restore",
        36: "Expander trouble",
        37: "Expander trouble restore",
    }

    USER_EVENT_CODES: Dict[int, str] = {
        13: "User code added",
        14: "User code deleted",
        15: "User code changed",
        16: "User code enabled",
        21: "User code disabled",
    }

    def __init__(self) -> None:
        """
        Initialize a LogEvent object.
        """
        self.number: int = 0
        self.log_size: int = 0
        self.event_type: Optional[int] = None
        self.reportable: Optional[Any] = None
        self.zone_user_device: int = 0
        self.partition_number: int = 0
        self.timestamp: Optional[Any] = None
        self.event_string_val: Optional[str] = None

    @property
    def event(self) -> Optional[str]:
        return self.event_string_val

    def get_event_string(self) -> str:
        codes: Dict[int, str] = {
            **self.ZONE_EVENT_CODES,
            **self.NONE_EVENT_CODES,
            **self.DEVICE_EVENT_CODES,
            **self.USER_EVENT_CODES,
        }
        if self.event_type is not None and self.event_type in codes:
            return codes[self.event_type]
        elif self.event_type is not None:
            return f"Unknown event {self.event_type}"
        else:
            return "Unknown event (no type)"

    def get_event_string_for_target(self, target: Optional[int]) -> str:
        if self.event_type is not None and target is not None:
            return f"Unknown event {self.event_type} for target {target}"
        elif self.event_type is not None:
            return f"Unknown event {self.event_type} for unknown target"
        else:
            return "Unknown event (no type) for unknown target"


class User(object):
    """
    Represents a user in the system, including PIN and authority flags.
    """

    AUTHORITY_FLAGS: Tuple[List[str], List[str]] = (
        [
            "Reserved",
            "Arm only",
            "Arm only (during close window)",
            "Master / Program",
            "Arm / Disarm",
            "Bypass enable",
            "Open / close report enable",
        ],
        [
            "Output 1 enable",
            "Output 2 enable",
            "Output 3 enable",
            "Output 4 enable",
            "Arm / disarm",
            "Bypass enable",
            "Open / close report enable",
        ],
    )

    def __init__(self, number: int) -> None:
        """
        Initialize a User object.
        Args:
            number (int): User number.
        """
        self.number: int = number
        self.pin: List[Any] = []
        self.authority_flags: List[str] = []
        self.authorized_partitions: List[Any] = []


class concord232Extension(object):
    """
    Extension hook class for custom integrations with the controller.
    """

    def __init__(self, controller: Any) -> None:
        """
        Initialize the extension with a controller instance.
        Args:
            controller: The main controller object.
        """
        self._controller: Any = controller

    def zone_status(self, zone: Any) -> None:
        """
        Hook for zone status updates.
        Args:
            zone: Zone object.
        """
        pass

    def partition_status(self, partition: Any) -> None:
        """
        Hook for partition status updates.
        Args:
            partition: Partition object.
        """
        pass

    def device_command(self, house: Any, unit: Any, command: Any) -> None:
        """
        Hook for device command events.
        Args:
            house: House code.
            unit: Unit code.
            command: Command code.
        """
        pass

    def system_status(self, system: Any) -> None:
        """
        Hook for system status updates.
        Args:
            system: System object.
        """
        pass

    def log_event(self, event: Any) -> None:
        """
        Hook for log event notifications.
        Args:
            event: LogEvent object.
        """
        pass
