# Test Coverage Notes

## Configuration for Testing

The server now supports configuration via a `config.ini` file. Tests that depend on server settings (such as serial port, listen address, or port) can use a test-specific config file or override settings with command-line arguments. See the README for config file details.

## Current Coverage

- `concord_helpers.py`: Fully tested
- `client.py`: Fully tested
- `concord.py`: Only protocol utility functions are tested
- `concord_commands.py`: Only KEYPRESS_CODES and bytes_to_num are tested
- `model.py`: Only Zone.bypassed is tested
- `mail.py`: No tests

## Missing Tests

| Module                | What's Missing?                                                                 |
|-----------------------|---------------------------------------------------------------------------------|
| concord.py            | SerialInterface & AlarmPanelInterface methods                                   |
| concord_commands.py   | Command handler functions, builder functions                                   |
| model.py              | Partition, System, LogEvent, User, concord232Extension classes & properties     |
| mail.py               | All email-related functions                                                     |

### Recommendations

- Add unit tests for the classes and methods listed above, especially for business logic and error handling.
- For `concord.py` and `concord_commands.py`, consider using mocks for hardware/serial dependencies.
- For `mail.py`, use mocks for config and SMTP.
