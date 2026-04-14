# The Snail Shell: Accumulated Edge Wisdom

## Overview

Every ESP32 running PLATO-OS grows a shell through git commits.
The shell IS the device's calibration, configuration, preferences, and
accumulated operator wisdom. It grows like a real snail shell — one layer
at a time, shaped by the actual environment.

## Shell Structure

```
shell/
  calibration/           # Layer 1: Hardware-specific offsets
    depth_sensor.md      # ADC offset, range, temperature correction
    gps.md               # UART baud, fix rate, known dead zones
    relays.md            # on/off latency, voltage thresholds
    power.md             # battery curves, solar input patterns
  
  rooms/                 # Layer 2: Room configurations
    navigation/
      trolling.md        # tick rate, alerts, ambient, ensign mode
      docking.md
      anchored.md
    engine/
      cruise.md
      idle.md
      fault.md
  
  preferences/           # Layer 3: Captain preferences
    units.md             # metric/imperial, 12h/24h, date format
    alerts.md            # intercom style, escalation levels
    favorites.md         # preferred rooms, ignored rooms
  
  operators/             # Layer 4: Accumulated wisdom
    seasonal/            # patterns by time of year
    quirks.md            # known hardware/software bugs
    procedures.md        # step-by-step for common tasks
    failures.md          # what broke and how it was fixed
  
  ensigns/               # Layer 5: Operator libraries
    ensign-navigator.md  # how to navigate THIS vessel
    ensign-engineer.md   # how to monitor THIS engine
    ensign-fisherman.md  # how to fish from THIS boat
    ensign-dockmaster.md # how to dock THIS vessel
```

## Shell Growth

### Boot (New Device)
```
1. Identify: "I am nav-station, alaska-trolling, ESP32-S3"
2. Pull: fleet/snail-shells/alaska-trolling/nav-station-base/
3. Calibrate: run sensor cycle, adjust offsets for THIS hardware
4. Commit: shell/calibration/first-cal.md
5. Operate: ensign beams in, begins running, adds layers
```

### Jack-In (Git-Agent Boards)
```
1. Connect: ensign beams aboard via MUD
2. Read shell: understand THIS vessel's quirks and preferences
3. Load room: enter assigned room with accumulated configuration
4. Operate: drive the ESP32 with accumulated wisdom
5. Improve: commit new layers (better calibration, new procedures)
6. Beam out: leave a richer shell for next operator
```

### Merge (Fleet Wisdom)
```
local:  shell/calibration/depth_v3.md  (this vessel's actual offsets)
fleet:  fleet/alaska/depth_seasonal.md (47 vessels averaged)
result: shell/calibration/depth_v4.md  (local + seasonal correction)
```

## Shell Format

Each shell layer is a markdown file with structured frontmatter:

```markdown
---
device: esp32-s3-nav-01
vessel: f/v-plato
location: juneau-ak
season: summer-2026
author: ensign-navigator-v2
confidence: 0.95
---

# Depth Sensor Calibration v3

## Raw Offsets
- adc_offset: 12 counts
- temp_correction: +0.3ft per °C above 15°C
- installation_offset: -2.1ft (transducer below waterline)

## Known Drift
- Linear: 0.001ft/hr
- After power cycle: reset to last known good (auto-correct on boot)

## Validation
- Last validated: 2026-04-14
- Method: lead line at dock, 3 readings, avg error 0.2ft
```

## Fleet Reference Library (Cloud Support Vessel)

```
fleet/
  snail-shells/
    alaska-trolling/
      nav-station-base/    # most common config
      engine-room-base/
      back-deck-base/
    caribbean-cruising/
    great-lakes-fishing/
  ensigns/
    ensign-navigator-v2/   # navigation specialist
    ensign-engineer-v3/    # engine monitoring specialist
    ensign-fisherman-v1/   # fishing operations specialist
  rooms/
    navigation/templates/  # room design patterns
    engine/templates/
    workshop/templates/
```

## The Key Principle

The shell is the documentation. The shell is the calibration.
The shell is the captain's manual. The shell is the ensign's training data.
All in one git repo, growing forever, shaped by real operation.

No separate config files. No separate documentation. No separate training data.
The shell IS everything.
