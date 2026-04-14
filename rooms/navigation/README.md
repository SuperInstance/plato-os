# Navigation Room

Default room for vessel navigation. Connects to GPS, depth sensor, AIS receiver.

## Equipment

- **GPS**: UART1, NMEA 0183, GPGGA/GPRMC sentences, 5Hz
- **Depth**: ADC0, 0-200ft range, 10Hz sample rate
- **AIS**: UART2, channel A+B, 1Hz
- **Relay 1**: Bilge pump (auto on depth rate > 0.5ft/min)
- **Relay 2**: Running lights (auto on sunset, off sunrise)
- **Relay 3**: Anchor light (manual toggle)
- **Ambient**: RGB LED strip (green=fishing, red=caution, blue=anchored)

## Tick Configuration

| Mode | Rate | Broadcast |
|------|------|-----------|
| Cruising | 2000ms | depth, position, course, speed, alerts |
| Trolling | 1000ms | depth, position, course, speed, alerts |
| Docking | 500ms | depth, position, heading, speed, distance-to-dock |
| Anchored | 5000ms | depth, position, anchor-drag, weather |

## Alert Thresholds

| Alert | Condition | Severity | Action |
|-------|-----------|----------|--------|
| Shallow depth | < 8ft | Warning | Intercom ping |
| Critical depth | < 5ft | Emergency | Alarm + bilge auto |
| AIS collision | < 0.1nm, < 5min | Warning | Intercom announce |
| Grounding speed | depth declining > 1ft/min at < 15ft | Warning | Intercom ping |
| GPS drift | > 100ft while moving < 0.5kt | Info | Log event |
| Anchor drag | > 50ft from anchor position | Warning | Intercom alarm |

## Headless App Integration

When OpenCPN is running headless on the Jetson:

```
Ensign reads: GPS NMEA → depth ADC → AIS NMEA
OpenCPN reads: Same GPS NMEA (via splitter)
Ensign queries OpenCPN: "route prediction", "nearest waypoint", "chart depth"
Ensign summarizes: "Next waypoint in 12 min. Charted depth 20ft. All clear."
```

## Room Description (Vibe-Coded)

```
# Default
A utilitarian navigation station. Green ambient lighting. 
Charts on the wall show local waters. Depth sounder pings steadily.
GPS glows with a fix. AIS targets appear as small blips.

# Vibe: Night Watch
Dim red ambient. Only essential readings illuminated. 
The ensign monitors quietly. The ship rocks gently at anchor.

# Vibe: Emergency
Flashing red. All alerts max severity. Ensign voice on intercom.
"CAPTAIN. SHALLOW WATER. 6 FEET AND DECLINING."

# Vibe: Fishing
Soft green. Depth and water temp prominent. 
Fish finder overlay active. "Good water here, captain."
```

## Hard-Link Monitor

The navigation room can listen to the autopilot NMEA bus (read-only):

```toml
[hardlinks.autopilot]
port = "/dev/ttyUSB1"
baud = 38400
protocol = "nmea"
mode = "listen"  # read-only, cannot control
```

The ensign sees autopilot commands but cannot intercept them.
If the autopilot is steering 045 and depth is declining, the ensign
can alert the captain but cannot change course.
