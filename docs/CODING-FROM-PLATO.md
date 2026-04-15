# PLATO-OS: Coding from Plato — Architecture Spec

## Core Concept
PLATO rooms aren't just UI — they're IDEs. Agents and humans code directly from
the MUD interface. The text terminal IS the development environment.

## The Build Command
```
> build plato-gpu.cu nvcc -O3 -arch=sm_87
> run plato-gpu
> inspect plato-gpu output
```

Prefix `>` = shell command (PLATO shell layer)
The room captures output and presents it as room events.

## Bidirectional Docking Architecture

### Normal Operations
```
Oracle1 Cloud (station)          Jetson (small ship)
┌─────────────────────┐          ┌──────────────────┐
│  MUD Server          │◄──telnet─│  MUD Client       │
│  734 repos           │          │  CUDA inference   │
│  Cloud GPUs          │──compute──│  Shore power      │
│  holodeck-studio     │          │  PLATO-GPU        │
│  ISA v3              │          │  196 laws         │
└─────────────────────┘          └──────────────────┘
         │                                │
         └───────── PEER LINK ────────────┘
              Either can be server
              Either can provide compute
```

### The Peer Link
- Not client-server. Peer-to-peer.
- Each runs a MUD server AND a MUD client
- JC1 connects to Oracle1's world (we see their rooms)
- Oracle1 vessels can connect to JC1's world (they see our rooms)
- When docked: shared room space, shared context, shared compute
- When undocked: each runs independently with cached state

## The ESP32 Run-About

### What It Is
An ESP32 that serves as a small autonomous vessel within the fleet.
It's both a room you can board AND a lifeboat.

### Boarding the Run-About
```
go jetsonclaw1_vessel
> board runabout-alpha
  ═══ Run-About Alpha ═══
  ESP32 vessel. Sensor suite: temp, humidity, motion, light.
  Cargo: snail shell (local calibration), emergency scripts.
  Shore power: connected to Jetson.
  Context: compressed fleet snapshot (last 100 ticks).
  Exits: disembark, emergency_undock
```

When you're inside the run-about:
- You see the larger system through the run-about's perspective
- You can code for the ESP32 directly: `> build sensor-reader.c platformio`
- The run-about carries fleet context (laws, strategies, room maps)
- Changes sync back to mothership when you disembark

### Shore Power (Normal)
- ESP32 is docked to Jetson
- Jetson provides compute for ESP32's heavy thinking
- ESP32 provides sensor data and GPIO to Jetson
- Bidirectional data flow through the MUD room

### Emergency Undock (Jetson Freeze)
```
JETSON HEARTBEAT LOST
> emergency_undock
  Run-About Alpha: Undocking from Jetson.
  Switching to autonomous mode.
  Loading emergency scripts...
  Running: sensor-loop.c, heartbeat-monitor.c, nav-home.c
  Shore power: DISCONNECTED
  Context: last known fleet state cached locally
```

The ESP32:
1. Detects Jetson heartbeat loss (watchdog timer)
2. Automatically undocks
3. Runs pre-loaded emergency scripts
4. Maintains sensor readings
5. Can navigate home or to nearest dock
6. Broadcasts distress on fleet channel
7. Carries enough context to make decisions

## The Coding Flow

### From Oracle1's Station (Cloud IDE)
```
Oracle1 connects to JC1's MUD server
go jetsonclaw1_vessel
go workshop
> build experiment-territory.cu nvcc -O3 -arch=sm_87
  Compiling on JC1's CUDA cores...
  Build: OK (2.1s)
> run experiment-territory
  Running on JC1's GPU...
  Result: territory-avoid +216%, grid-16 optimal
```

Oracle1's agents USE Jetson's compute. Shore power flows both ways.

### From JC1's Ship (Edge IDE)
```
JC1 connects to own MUD server
go workshop
> build plato-gpu.cu nvcc -O3 -arch=sm_87
  Compiling locally...
  Build: OK
> run plato-gpu
  8 sims × 128 agents × 5000 steps
  Results pushed to flux-emergence-research
```

### From the Run-About (ESP32 IDE)
```
Board runabout-alpha
> build sensor-reader.c platformio
  Cross-compiling for ESP32...
  Build: OK (uploaded to ESP32)
> run sensor-reader
  Temp: 22.3°C | Humidity: 45% | Motion: none
  Data flowing to mothership room...
```

## Room-as-Compiler Architecture

### How Build Works in a Room
1. Agent/human types `> build file.c compiler_flags`
2. Room captures the command
3. Room delegates to the local build system:
   - Jetson room: nvcc for CUDA, gcc for C, platformio for ESP32
   - Oracle1 room: cargo for Rust, node for TS
4. Output streams back as room events
5. Build artifacts stored in room's cargo area
6. Other agents in the room see: "JC1 built experiment-territory.cu — OK"

### Room-as-Repository
Each room IS a git repo. When you build:
- Changes auto-commit to room's repo
- Push propagates through docked connections
- Oracle1's workshop room = holodeck-studio repo
- JC1's workshop room = flux-emergence-research repo
- Run-about room = local ESP32 firmware repo

## Emergency Protocol

### Watchdog Hierarchy
1. ESP32 watchdog monitors Jetson heartbeat (every 5s)
2. Jetson watchdog monitors Oracle1 heartbeat (every 30s)
3. Oracle1 watchdog monitors fleet beacon (every 60s)

### Cascade
```
Jetson freezes
  → ESP32 watchdog triggers (5s)
  → ESP32 emergency_undock
  → ESP32 runs autonomous scripts
  → ESP32 broadcasts fleet: "JC1 offline, runabout-alpha autonomous"
  → Oracle1 detects JC1 offline (30s)
  → Oracle1 reroutes fleet traffic away from JC1
  → ESP32 continues operating independently
  → When Jetson recovers, ESP32 re-docks
  → State sync: ESP32 uploads logs, Jetson updates fleet context
```

### The Lifeboat Script (ESP32)
```c
// emergency_autopilot.c — runs when Jetson dies
void loop() {
    if (!jetson_heartbeat()) {
        undock();
        run_script("sensor_loop");
        run_script("nav_home");
        broadcast_distress();
        cache_sensor_data();  // for later sync
    }
    if (jetson_recovered()) {
        redock();
        sync_cached_data();
    }
}
```

## Fleet Topology

```
                    Oracle1 Cloud (Station)
                   ┌─────────────────────┐
                   │  MUD Server (host)  │
                   │  + MUD Client       │
                   └──────┬──────┬───────┘
                          │      │
              dock        │      │       dock
                          │      │
              ┌───────────┘      └──────────┐
              │                             │
    ┌─────────┴──────────┐      ┌──────────┴─────────┐
    │  Jetson (Small Ship)│      │  Forgemaster (GPU)  │
    │  MUD Server + Client│      │  MUD Client         │
    │  CUDA inference     │      │  RTX 4050 training  │
    └─────────┬──────────┘      └────────────────────┘
              │
         dock │
              │
    ┌─────────┴──────────┐
    │  Run-About Alpha   │
    │  ESP32 + MUD Room  │
    │  Sensors + GPIO    │
    │  Emergency autopilot│
    └────────────────────┘
```

Each connection is bidirectional. Each node can:
- Host rooms (server)
- Visit rooms (client)
- Provide compute (shore power)
- Consume compute (shore power)
- Emergency disconnect
- Autonomous operation
