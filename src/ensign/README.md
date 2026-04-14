# The Ensign

The ship's agent. A git-agent that lives in the MUD, reads rooms,
drives equipment, answers queries, and accumulates shell wisdom.

## Role

The ensign is not a chatbot. The ensign is a crew member who happens to
communicate through text. They have specialties, equipment, preferences,
and they get better over time through git commits.

## Architecture

```
Ensign
├── identity: { name, specialty, version, shell_hash }
├── perception: reads all room senses in real-time
├── inference: runs on Jetson GPU (local LLM or rule engine)
├── actions: sends MUD actions to equipment
├── memory: shell layers + mental-logs + room history
└── growth: commits new shell layers after every session
```

## Query Handling

```
Human:  ! ensign, what's the shallowest depth for next 5 minutes?
Ensign: → reads depth sense history (last 5 min)
        → reads GPS sense (course, speed)
        → calculates: current position + course + speed = predicted track
        → checks predicted track against depth chart (if available)
        → responds: "Shallowest predicted: 11.2ft at waypoint 4 (~3 min)
                     Current depth: 14.1ft and trending down.
                     Alert will fire at 8ft."
```

## Night Watch Mode

When the captain is away:

```
Tick 0:   Read all rooms. Check alerts. Report status.
Tick 100: Check depth trend. If declining > 0.5ft/min → log warning.
Tick 200: Check battery. If < 30% → log warning.
Tick 300: Check AIS targets. If collision risk < 5 min → trigger alarm.
Tick N:   Commit hourly summary to shell.
Morning:  Captain asks "what happened?" → ensign reads night log.
```

## Specialties

Ensigns are git-agents with increasing specialization:

```
ensign-navigator-v2/
  ├── SKILL.md          # what this ensign knows
  ├── procedures.md     # step-by-step navigation tasks
  ├── quirks.md         # this vessel's navigation quirks
  └── shell-hooks.md    # which shell layers to load

ensign-engineer-v3/
  ├── SKILL.md
  ├── procedures.md     # engine monitoring, fault detection
  └── shell-hooks.md
```

An ensign can morph between specialties by loading different skill sets.

## Growth Model

```
Session 1: Fresh ensign, reads shell, makes mistakes
         → commits: "Learned: GPS loses fix under bridges, use DR for 30s"
Session 2: Loads previous session's commits
         → avoids bridge GPS loss, navigates smoothly
         → commits: "Learned: depth sensor drifts +0.3ft above 15°C"
Session N: Accumulated wisdom from N sessions
         → handles edge cases automatically
         → can train new ensigns on this vessel's specifics
```

## Interface

The ensign communicates ONLY through the MUD prefix protocol:

```
> Captain, depth is declining. Recommend course adjustment to 050.
  (room chat — visible to all)

:: Depth trend: -0.8ft/min over last 10 minutes. Possible tide change.
  (mental-log — saved to markdown, private)

$ relay_1 on
  (command — drives bilge pump, logged)

# Navigation room: increase tick rate to 200ms, enable depth prediction
  (room design — changes room configuration)
```

## Inference Modes

| Mode | Compute | Use Case |
|------|---------|----------|
| Rule | None | Simple thresholds, pattern matching |
| Local LLM | Jetson GPU | Natural language queries, complex reasoning |
| Cloud LLM | Network | Heavy reasoning, unavailable offline |
| Hybrid | Both | Local first, cloud fallback |

Rule mode costs nothing. Local LLM uses ~2GB VRAM on Jetson.
Cloud mode requires connectivity. The ensign degrades gracefully.
