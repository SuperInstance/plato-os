# PLATO-OS Protocol Specification

## Transport

- **Default**: Telnet (TCP port 4000), raw text, newline-delimited
- **Rich clients**: WebSocket (TCP port 4001), JSON event stream
- **ESP32 terminals**: Telnet only (minimal memory footprint)

## Message Format

All messages are single-line, UTF-8, newline-terminated (`\r\n`).

### Prefix Protocol

Every client message MUST start with a prefix:

```
> text             Room conversation
:: text            Mental-log (saved to markdown)
$ command          System command
! query            Ensign query
# directive        Room design
```

### Server Messages (no prefix — server doesn't pretend to be human)

```
OK [detail]                Command acknowledged
ERR [code] [message]       Command failed
EVENT [type] [data]        Room event broadcast
SENSE [source] [k=v...]    Sensor reading batch
ACTION [target] [k=v...]   Actuator command
ALERT [severity] [msg]     Notification
PING                       Heartbeat request
CONFIG [k=v...]            Room configuration
WELCOME [room] [info]      Room joined
```

## Connection Lifecycle

```
Client                          Server
  |                               |
  |--- CONNECT (telnet/ws) ------>|
  |<-- PLATO-OS v0.1.0 -----------|
  |                               |
  |--- AUTH <token> ------------->|  (optional)
  |<-- OK auth'd as captain ------|
  |                               |
  |--- JOIN <room> [EQUIP <id>] ->|
  |<-- WELCOME <room> <info> -----|
  |                               |
  |--- SENSE depth 12.4 ft ------>|  (ESP32 only)
  |                               |
  |<-- EVENT sense depth=12.4 ----|  (broadcast to room)
  |                               |
  |--- > hello everyone ---------|  (chat)
  |<-- EVENT chat captain "hello" |  (broadcast)
  |                               |
  |--- ! ensign depth trend ------>|  (ensign query)
  |<-- ENSIGN "Depth declining..."|  (response)
  |                               |
  |--- $ ls /dev/ttyUSB* -------->|  (command)
  |<-- OK /dev/ttyUSB0\n/dev/ttyUSB1 |
  |                               |
  |--- :: note about depth -------|  (mental-log)
  |<-- OK saved to mental-log/2026-04-14.md |
  |                               |
  |--- # room dim red ------------>|  (room design)
  |<-- CONFIG ambient=red --------|
  |                               |
  |--- LEAVE --------------------->|
  |<-- OK goodbye ----------------|
  |                               |
  |--- DISCONNECT ---------------->|
  |                               |
```

## Equipment Manifest (JSON, sent on JOIN)

```json
{
  "hat_id": "nav_hat_v1",
  "senses": {
    "depth": {"type": "adc", "unit": "ft", "range": "0-200"},
    "position": {"type": "nmea", "protocol": "GPGGA"}
  },
  "actions": {
    "relay_1": {"type": "gpio", "description": "bilge pump"},
    "ambient": {"type": "pwm_rgb"}
  }
}
```

## Room State (broadcast on tick)

```
EVENT state room=navigation depth=12.4ft position=58.3N,134.2W \
  course=045 speed=3.2kt relay_1=off ambient=green \
  occupants=3 alerts=0
```

## Error Codes

| Code | Meaning |
|------|---------|
| E001 | Unknown prefix |
| E002 | Room not found |
| E003 | Permission denied |
| E004 | Invalid command |
| E005 | Equipment not found |
| E006 | Sensor failure |
| E007 | Room full |
| E008 | Already in room |
