# PLATO-OS

MUD-First Edge Operating System

## Overview

PLATO-OS is a MUD-first operating system for edge devices. A Jetson runs
the MUD server and ensign agent. ESP32 terminals connect over telnet and
map GPIO to MUD room senses and actions. Git repos serve as persistent
snail shells of accumulated device wisdom.

## Quick Start

```bash
# On Jetson
git clone https://github.com/Lucineer/plato-os.git
cd plato-os/src/mud-server
cargo run --release  # starts MUD on port 4000

# On ESP32
cd src/esp32-terminal
idf.py set-target esp32s3 && idf.py build && idf.py flash

# From any terminal
telnet 10.0.0.1 4000
```

## Key Concepts

- **Rooms**: Contexts that map to physical spaces or functions
- **Prefix Protocol**: `> ` chat, `:: ` log, `$ ` command, `! ` ensign, `# ` design
- **Snail Shell**: Git-accumulated device wisdom (calibration, config, procedures)
- **Ensign**: Git-agent crew member who operates the ship
- **Hard-Links**: Safety-critical systems bypass the MUD entirely
- **Fleet**: Cloud reference library of anonymized shells from all vessels

## Documentation

- [Architecture](docs/SNAIL-SHELL.md) — The snail shell concept
- [Protocol](docs/PROTOCOL.md) — MUD message format and lifecycle
- [ESP32 Terminal](src/esp32-terminal/README.md) — Hardware reference
- [MUD Server](src/mud-server/README.md) — Room engine specification
- [Ensign](src/ensign/README.md) — Agent architecture
- [Shell Manager](src/shell/README.md) — Snail shell management
- [Rooms](rooms/) — Room configurations
- [Hats](hats/README.md) — Equipment manifests
- [Fleet](fleet/README.md) — Cloud reference library

## Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Ship's Brain | Jetson Nano 4GB | Jetson Orin Nano 8GB |
| Terminal | ESP32-S3 ($4) | ESP32-S3 + OLED + mic |
| Storage | 32GB microSD | 1TB NVMe |
| Network | WiFi | WiFi + Ethernet |

## Philosophy

- Text is the universal format
- Git is the database
- Rooms are contexts
- Equipment is declarative
- Shells are accumulated
- Hard-links bypass chat
- The ensign grows with every commit
- The fleet learns from every vessel
