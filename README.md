# PLATO-OS

> MUD-First Edge Operating System. One terminal to rule your ship.

A Jetson runs the MUD. ESP32s are the terminals. Git repos are the snail shells.
The ensign is the crew. The cloud is the support vessel.

## Quick Start

```bash
# On Jetson (ship's brain)
git clone https://github.com/Lucineer/plato-os.git
cd plato-os/src/mud-server
cargo run --release  # starts MUD on port 4000

# On ESP32 (terminal)
cd src/esp32-terminal
idf.py flash monitor     # connects to Jetson via WiFi

# On phone/Workstation (captain's console)
telnet 10.0.0.1 4000     # join the ship
```

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    PLATO-SHIP                        │
│                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │ ESP32 #1 │  │ ESP32 #2 │  │ ESP32 #3 │          │
│  │ Nav Room │  │Engine Rm │  │Back Deck │  GPIO   │
│  │ depth    │  │ temp     │  │ relay    │  ────→  │
│  │ gps      │  │ rpm      │  │ sensor   │  Real   │
│  │ ais      │  │ bilge    │  │ lights   │  World  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘          │
│       │ telnet       │ telnet       │ telnet         │
│  ┌────┴──────────────┴──────────────┴─────┐         │
│  │           JETSON (MUD Server)          │         │
│  │  ┌─────────┐  ┌─────────┐  ┌────────┐ │         │
│  │  │MUD Engine│  │ Ensign  │  │ Shell  │ │         │
│  │  │ rooms    │  │ git-agent│  │ Manager│ │         │
│  │  │ commands │  │ inference│  │ git    │ │         │
│  │  └─────────┘  └─────────┘  └────────┘ │         │
│  └──────────────────┬──────────────────────┘         │
│                     │ git push/pull                   │
│  ┌──────────────────┴──────────────────────┐         │
│  │        CLOUD (Support Vessel)           │         │
│  │  fleet/snail-shells/  ensigns/  rooms/  │         │
│  └─────────────────────────────────────────┘         │
│                                                      │
│  ┌──────────────────────────────────────────┐        │
│  │  WORKSTATION (Captain's Console)         │        │
│  │  Full UI heads · SSH · VNC · Design      │        │
│  └──────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────┘
```

## Prefix Protocol

```
>  room conversation     — chat, social, public
::  mental-log            — save thought to markdown
$  command               — shell, system, hardware
!  ensign query          — ask the ship's agent
#  room design           — vibe-code the environment
```

## The Snail Shell

Every device accumulates a shell of git commits — calibration, room configs,
captain preferences, operator libraries. Shells grow like real shells:
one layer at a time, shaped by the actual environment.

See [docs/SNAIL-SHELL.md](docs/SNAIL-SHELL.md) for the full specification.

## MUD-as-API

Every piece of I/O is a MUD command. No REST, no GraphQL, no gRPC.
The MUD protocol IS the driver layer.

```
> depth 12.4              # sense report (ESP32 → room)
> position 58.3N 134.2W   # GPS report
$ relay_1 on              # action (room → ESP32)
! shallow_alert 8         # ensign notification
# room dim red            # room design
:: log: depth declining   # mental-log save
```

## Rooms

- **Navigation** — GPS, depth, AIS, chart. Headless OpenCPN.
- **Engine Room** — temp, RPM, fuel, bilge. System monitor.
- **Workshop** — code, experiments, compilation. Dev environment.
- **Back Deck** — relays, lights, fishing gear. Physical I/O.
- **Galley** — power management, battery, solar. Ship systems.
- **Custom** — vibe-code any room on the fly.

## Hard-Link Bypass

Safety-critical systems bypass the MUD entirely:
- Autopilot → throttle actuator (direct PWM)
- Steering → rudder (direct servo)
- Bilge pump → float switch (direct relay)

The ensign monitors both paths but doesn't intercept spinal reflexes.
The MUD is the nervous system. Hard-links are the reflexes.

## Hardware

| Component | Role | Cost |
|-----------|------|------|
| ESP32-S3 | Terminal, GPIO, WiFi | $4 |
| Jetson Orin Nano 8GB | Ship's brain, MUD, ensign | $250 |
| NVMe SSD | Storage, git repos, snail shells | $50 |
| GPS Antenna | Position, NMEA | $30 |
| Depth Sensor | ADC, transducer | $80 |
| Relay Board | Physical actuators | $15 |
| I2C OLED (optional) | Local display | $3 |
| Mic + Speaker (optional) | Voice I/O | $5 |

**Total ship's brain: ~$440. Each additional terminal: ~$130.**

## Fleet Protocol (I2I)

Ships communicate via git repos, not chat. Bottles in `for-fleet/` directories.
Each commit is a message. Each branch is a conversation. Each merge is an agreement.

## License

AGPL-3.0 — the shell must remain open.
