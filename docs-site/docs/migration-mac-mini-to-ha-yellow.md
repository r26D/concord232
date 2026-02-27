# Migrating concord232 from Mac Mini to Home Assistant Yellow

This guide covers moving the concord232 server from a Mac Mini to a **Home Assistant Yellow** so it runs automatically with Home Assistant.

## Overview

- **Before:** concord232 runs on a Mac Mini (e.g. via `start_server.sh` or a manual/LaunchAgent process).
- **After:** concord232 runs as a **Home Assistant app** (formerly “add-on”) on the Yellow, starts with the host, and is managed from the HA UI.

## Prerequisites

- Home Assistant Yellow (or any host running Home Assistant OS)
- Your Concord 4 panel connected either:
  - **Option A:** USB–serial adapter plugged into the Yellow (or the host running HA)
  - **Option B:** Network serial (e.g. ser2net) on another device, reachable from the Yellow at `host:port`

## Step 1: Add the concord232 app repository

1. In Home Assistant go to **Settings → Apps**. (In older versions this may be **Settings → Add-ons**.)
2. Open the **⋮** (three dots) menu → **Repositories**.
3. Add this repository:
   - **Repository URL:**  
     `https://github.com/r26d/concord232`  
     (or your fork: `https://github.com/YOUR_USERNAME/concord232`)
4. Click **Add**, then **Close**.

## Step 2: Install the Concord232 app

1. In the app store list, find **Concord232** (under the repository you added).
2. Open **Concord232** → **Install**.
3. When installation finishes, do **not** start it yet.

## Step 3: Configure the app

1. Open the **Concord232** app → **Configuration** tab.
2. Set options to match your setup:

**If using a USB–serial adapter on the Yellow**

- **serial:** Device path, e.g. `/dev/ttyUSB0` or `/dev/ttyAMA0`.  
  To see which device appears when you plug in the adapter, use the **Terminal & SSH** app and run:  
  `ls /dev/tty*` before and after plugging in the adapter.
- **port:** `5007` (or another port if you prefer).
- **log:** Leave empty, or set a path like `/config/concord232.log` if you want a log file.

**If using network serial (RFC2217), e.g. ser2net on another host**

- **serial:** `rfc2217://192.168.3.89:5500` (replace with your ser2net host and port).
- **port:** `5007` (or your preferred API port).
- **log:** Optional, as above.

3. Click **Save**.

## Step 4: Start the app and enable “Start on boot”

1. In the Concord232 app, turn **Start on boot** **ON**.
2. Click **Start**.
3. Check the **Log** tab to confirm the server starts and connects (no errors about serial or port).

## Step 5: Point Home Assistant to the server

The Concord Alarm integration in Home Assistant must talk to the concord232 server on the Yellow:

- If the integration runs on the **same** Home Assistant instance (on the Yellow), use:
  - **Host:** `localhost` or `127.0.0.1`
  - **Port:** the app **port** (e.g. `5007`)
- If the integration runs on another Home Assistant instance, use:
  - **Host:** the Yellow’s IP on your LAN
  - **Port:** the app **port** (e.g. `5007`)

Reconfigure or add the **Concord Alarm** integration (Settings → Devices & services → Add integration → “Concord Alarm”) with that host and port.

## Step 6: Decommission the Mac Mini server

Once the app is running and the Concord integration works from HA:

1. Stop any concord232 (or ser2net) processes on the Mac Mini.
2. Optionally remove LaunchAgents, cron jobs, or scripts that were starting the server on the Mac.

## Troubleshooting

| Issue | What to check |
|-------|----------------|
| **App doesn’t appear in the store** | The app must be in a **top-level** folder of the repo (`addon-concord232/`). Remove the repository (⋮ → Repositories → remove it), then add it again. Wait a minute and refresh. Ensure you’re using the repo URL that contains `addon-concord232/` and `repository.yaml` at the root. |
| App won’t start | **Log** tab: missing `serial` or wrong device/URL; port in use. |
| “Serial port” errors | Correct **serial** path (`/dev/ttyUSB0` etc.) or RFC2217 URL; adapter plugged in and not used by another app. |
| Integration can’t connect | Host/port in the Concord Alarm integration match the app (e.g. `localhost:5007`). Firewall on the Yellow usually allows localhost. |
| Device path unknown | Use Terminal & SSH app: `ls /dev/tty*` with adapter unplugged, then plugged in; use the new device. |

## App files in this repo

- **App:** `addon-concord232/` at the repo root (config.yaml, Dockerfile, build.yaml, run.sh, DOCS.md).
- **Repository:** root `repository.yaml` so this repo can be added as an app source in Home Assistant (**Settings → Apps → ⋮ → Repositories**).

The app must live in a **top-level directory** of the repo so the Supervisor can find it. If you fork the repo, keep the `addon-concord232/` folder at the root.

The app installs `concord232` from PyPI and runs `concord232_server` with your configured serial and port, so it behaves like your previous Mac Mini server but managed by HA and started automatically on boot.
