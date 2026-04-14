# Shell Manager

Manages snail shells — the accumulated wisdom of each device, room, and vessel.
Git-based. Every layer is a commit. Every merge is wisdom transfer.

## Commands

```bash
# Initialize a new shell for a device
plato-shell init --device esp32-s3-nav-01 --template alaska-trolling

# Add a calibration layer
plato-shell add --device esp32-s3-nav-01 --layer calibration/depth_v3.md

# Pull fleet wisdom
plato-shell pull --fleet alaska-trolling --room navigation

# Merge fleet wisdom with local shell
plato-shell merge --device esp32-s3-nav-01 --fleet alaska-trolling

# Show shell history
plato-shell log --device esp32-s3-nav-01

# Export shell for new device
plato-shell export --device esp32-s3-nav-01 --format tar.gz
```

## Shell Lifecycle

```
[New ESP32] → init (fleet template) → calibrate (first readings) → operate
    ↑                                                        │
    └──────────── commit layers ← ensign/captain ←───────────┘
```

## Layer Types

| Type | Trigger | Content |
|------|---------|---------|
| Calibration | Boot / periodic | Sensor offsets, ranges, corrections |
| Configuration | Captain / ensign | Room settings, tick rates, alerts |
| Preference | Captain | Units, display, alert style |
| Procedure | Ensign | Step-by-step for common tasks |
| Quirk | Ensign (discovery) | Hardware bugs, workarounds |
| Failure | Ensign (incident) | What broke, root cause, fix |
| Seasonal | Ensign (analysis) | Patterns by time of year |

## Merge Strategy

```
LOCAL:  depth_offset = 12 (measured)
FLEET:  depth_offset = 10 (average of 47 vessels)
RULE:   Use LOCAL if < 30 days old, else blend with FLEET (80/20)

LOCAL:  bilge_auto_threshold = 0.5ft/min
FLEET:  bilge_auto_threshold = 0.3ft/min
RULE:   Use LOCAL (vessel-specific)
```

## Storage

```
shell/
  <device-id>/
    shell.toml           # device identity, template, last merge
    calibration/
    rooms/
    preferences/
    operators/
    ensigns/
    history/
      2026-04-14.md
```

Git-ignored: nothing. Everything committed. The shell IS the repo.
