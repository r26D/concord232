# API Reference

::: concord232

::: concord232.api

## Partition Support

Many API endpoints support targeting a specific partition using the `partition` parameter. This is especially relevant for arming, disarming, and sending keypresses.

### /command endpoint with partition

- **Arm a specific partition:**
  - `/command?cmd=keys&keys=\x02&group=True&partition=2`  (Arm partition 2 to stay)
- **Disarm a specific partition:**
  - `/command?cmd=keys&keys=<PIN>&group=True&partition=3`  (Disarm partition 3 with PIN)
- **Send keys to a specific partition:**
  - `/command?cmd=keys&keys=1234*&group=False&partition=4`

If `partition` is not specified, partition 1 is used by default.

See the main README for more CLI and API usage examples.
