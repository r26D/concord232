# Panel state: active trouble (multi-bus and more)

The `/panel` JSON includes trouble tracking when the integration receives **ALARM** messages from the panel.

## Fields

- **`trouble`** — `true` if at least one active trouble is being tracked
- **`trouble_count`** — number of active items
- **`trouble_detail`** — human-readable summary, e.g. `Bus 1: Bus Receiver Failure; Bus 4: Bus Device Failure` when more than one bus is in trouble
- **`trouble_buses`** — present when every active item is a **Bus Device** source: sorted bus numbers, e.g. `[1, 4]`

## Behavior

- Trouble messages are **accumulated** until a matching **restoral** (same source and specific type) is received, so multiple simultaneous bus issues all appear in `trouble_detail` instead of only the last message.
- The active set is **cleared** when the serial link **reconnects** (a fresh run should request updated panel state as usual).
- A **warning** line is logged when the active summary string changes, so log output matches the combined detail, not a single short label.

## Related types

Paired event families include system trouble (15/16), fire trouble, non-fire trouble, and alarm (see `TROUBLE_RESTORAL_PAIRS` in `concord232.concord`).
