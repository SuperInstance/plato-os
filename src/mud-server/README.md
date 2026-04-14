# PLATO MUD Server

The room engine. Runs on Jetson. Serves ESP32 terminals and human clients
over telnet. Manages rooms, ensign agents, shell persistence, and the
prefix protocol.

## Prefix Protocol

Every input line is prefixed to determine its layer:

| Prefix | Layer | Description |
|--------|-------|-------------|
| `> ` | Room | Conversation, visible to all in room |
| `:: ` | Mental-log | Save to markdown, private workspace |
| `$ ` | Command | Shell/system access |
| `! ` | Ensign | Query the ship's agent |
| `# ` | Room Design | Vibe-code the room |

## Room Model

```
Room
├── name: string
├── description: string (vibe-coded, modifiable)
├── occupants: [Client]
├── senses: Map<string, SenseValue>     # latest sensor readings
├── actions: Map<string, ActionQueue>   # pending actuator commands
├── alerts: [Alert]                     # active notifications
├── tick_rate: Duration                 # how often to broadcast state
├── equipment: EquipmentManifest        # what hardware is connected
├── shell: ShellLayers                  # accumulated wisdom
└── history: Vec<Event>                 # room log (git-persisted)
```

## Event Types

```rust
enum Event {
    // Room lifecycle
    RoomCreated { name: String, description: String },
    RoomModified { changes: String },
    
    // Occupancy
    ClientJoined { client: String, equipment: Option<String> },
    ClientLeft { client: String },
    
    // Senses (from ESP32 terminals)
    Sense { source: String, key: String, value: f64, unit: String },
    SenseBatch { source: String, readings: Vec<(String, f64, String)> },
    
    // Actions (to ESP32 terminals)
    Action { target: String, key: String, value: String },
    Ambient { r: u8, g: u8, b: u8 },
    Alert { severity: Severity, message: String },
    
    // Conversation
    Chat { from: String, text: String },
    EnsignQuery { from: String, query: String },
    MentalLog { from: String, text: String },
    
    // System
    Heartbeat { client: String },
    ShellUpdate { client: String, layer: String, hash: String },
    ConfigUpdate { key: String, value: String },
}
```

## Persistence

Every room event is logged and periodically committed to git:

```
rooms/navigation/
  room.toml              # room description, config
  equipment.toml         # connected hardware manifest
  shell/                 # snail shell layers
  history/
    2026-04-14.md        # day's events
    2026-04-13.md
```

Commits happen every 60 seconds or on significant events (alerts, config changes).

## Hard-Link Monitoring

The MUD server can monitor hardware buses without controlling them:

```toml
[hardlinks]
gps = { type = "nmea-listen", port = "/dev/ttyUSB0", baud = 4800 }
autopilot = { type = "nmea-listen", port = "/dev/ttyUSB1", baud = 38400 }
```

These are read-only. The ensign sees what the autopilot is doing but
cannot intercept steering commands. Spinal reflexes stay direct.

## API (for workstation UI)

The MUD server also exposes a WebSocket endpoint for richer clients:

```
ws://10.0.0.1:4001/ws?room=navigation&token=<auth>
```

Sends JSON event stream. Receives JSON commands. Used by workstation
chartplotter, phone dashboard, etc. Same data as telnet, structured.

## Build & Run

```bash
cd src/mud-server
cargo build --release
./target/release/plato-mud --port 4000 --ws-port 4001 --rooms-dir ../rooms/
```

## Design Principles

1. **Text is the universal format.** Every event can be rendered as a single line.
2. **Git is the database.** No SQLite, no Redis. Commits are persistence.
3. **Rooms are contexts.** Enter a room, everything is scoped to that room.
4. **Equipment is declarative.** The manifest describes what hardware exists.
5. **Shells are accumulated.** Every commit grows the device's wisdom.
6. **Hard-links bypass.** Safety systems never go through text chat.
