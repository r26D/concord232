# Testing Concord232 on the HA box (port 5007)

To verify the Concord232 server is responding, use one of the methods below. **Important:** If you use the **Terminal & SSH** add-on, you are inside an add-on container — `localhost` there is *not* the host, so use **`host.home-assistant`** instead of `localhost`.

## From the HA Terminal & SSH add-on (recommended)

Concord232 runs in its own container. From another add-on, reach the host (where port 5007 is mapped) with:

```bash
curl -s http://host.home-assistant:5007/version
```

- **Success:** `{"version":"1.1"}`
- **Failure:** Empty or connection error → Concord232 app may be stopped, or serial/config error (check app **Log** tab).

## From your computer (same network as the Yellow)

Replace the Yellow’s IP if different:

```bash
curl -s http://192.168.4.36:5007/version
```

## If you have a real shell on the HA host (e.g. SSH to the OS)

Then `localhost` is correct:

```bash
curl -s http://localhost:5007/version
```

## Port check (only when on the host)

On the host, you can check that port 5007 is open. From Terminal & SSH add-on, use the host name:

```bash
nc -zv host.home-assistant 5007
```

(BusyBox `nc` may give no output; prefer `curl` above.)

## Optional: other read-only endpoints

From Terminal & SSH add-on (use `host.home-assistant` if you're in an add-on shell):

```bash
curl -s http://host.home-assistant:5007/panel
curl -s http://host.home-assistant:5007/zones
curl -s http://host.home-assistant:5007/partitions
```

If the controller is not initialized (e.g. serial not connected), these may return `503` or empty data; that still confirms the server is up.

## Summary

| Where you run it | Command |
|------------------|---------|
| Terminal & SSH add-on | `curl -s http://host.home-assistant:5007/version` |
| Your PC (same network) | `curl -s http://192.168.4.36:5007/version` |
| Real host shell | `curl -s http://localhost:5007/version` |

If you get `{"version":"1.1"}`, the Concord integration can use **Host: localhost**, **Port: 5007** (from the integration’s point of view, it runs on the same HA host).
