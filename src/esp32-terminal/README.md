# ESP32 PLATO Terminal

Bare-metal PLATO terminal for ESP32-S3. Connects to Jetson MUD server
over WiFi/telnet, maps GPIO to MUD room senses and actions.

## Pin Map (Default Hat)

| Pin | Function | MUD Sense/Action |
|-----|----------|------------------|
| GPIO1 | TX (UART0) | Debug console |
| GPIO3 | RX (UART0) | Debug console |
| GPIO4 | UART1 TX | GPS NMEA out |
| GPIO5 | UART1 RX | GPS NMEA in |
| GPIO6 | UART2 TX | AIS receiver out |
| GPIO7 | UART2 RX | AIS receiver in |
| GPIO8 | ADC1_CH0 | Depth sensor analog |
| GPIO9 | ADC1_CH1 | Water temp analog |
| GPIO10 | GPIO_OUT | Relay 1 (bilge pump) |
| GPIO11 | GPIO_OUT | Relay 2 (running lights) |
| GPIO12 | GPIO_OUT | Relay 3 (anchor light) |
| GPIO13 | PWM0 | LED ambient R |
| GPIO14 | PWM1 | LED ambient G |
| GPIO15 | PWM2 | LED ambient B |
| GPIO16 | I2C_SDA | OLED / sensor bus |
| GPIO17 | I2C_SCL | OLED / sensor bus |
| GPIO18 | GPIO_OUT | Buzzer / intercom |
| GPIO19 | GPIO_IN | Float switch (manual override) |

## Protocol

### Boot Sequence
```
1. Power on → WiFi connect to "PLATO-SHIP"
2. Telnet to 10.0.0.1:4000
3. Send: JOIN Navigation Room EQUIPMENT nav_hat_v1
4. Receive: WELCOME Navigation Room. Equipment: depth,gps,ais,relays,leds.
5. Enter sense loop:
   - Read ADC pins → SENSE depth 12.4 temp 42
   - Read UART → SENSE position 58.3N 134.2W ais_target 3
   - Receive → ACTION relay_1 on → drive GPIO10
   - Receive → AMBIENT 255 0 0 → drive PWM13/14/15
6. Every 100ms: send sense batch
7. Every 10s: send heartbeat
```

### MUD Commands (ESP32 → Server)
```
JOIN <room> EQUIPMENT <hat_id>     # join a room
SENSE <key> <value> [unit]         # report sensor reading
HEARTBEAT                          # still alive
SHELL <hash>                       # current shell version
ERROR <key> <description>          # sensor failure
```

### MUD Commands (Server → ESP32)
```
WELCOME <room> Equipment: <list>   # room joined
ACTION <key> <value>               # drive actuator
AMBIENT <r> <g> <b>               # LED color
ALERT <severity> <message>         # notification
PING                               # request heartbeat
CONFIG <key> <value>               # update tick rate, thresholds
UPDATE <url>                       # pull new shell layer
```

## Equipment Manifest Format

```json
{
  "hat_id": "nav_hat_v1",
  "version": "1.0.0",
  "senses": {
    "depth": {"pin": 8, "type": "adc", "range": "0-200ft", "unit": "ft", "hz": 10},
    "water_temp": {"pin": 9, "type": "adc", "range": "0-30C", "unit": "C", "hz": 1},
    "position": {"uart": 1, "type": "nmea", "protocol": "GPGGA", "hz": 5},
    "ais": {"uart": 2, "type": "nmea", "protocol": "AIVDM", "hz": 1}
  },
  "actions": {
    "relay_1": {"pin": 10, "type": "gpio", "description": "bilge pump"},
    "relay_2": {"pin": 11, "type": "gpio", "description": "running lights"},
    "relay_3": {"pin": 12, "type": "gpio", "description": "anchor light"},
    "ambient": {"pins": [13,14,15], "type": "pwm", "description": "RGB LED strip"},
    "buzzer": {"pin": 18, "type": "gpio", "description": "intercom buzzer"}
  },
  "overrides": {
    "float_switch": {"pin": 19, "type": "gpio_in", "description": "manual bilge override"}
  }
}
```

## Build

```bash
# Requires ESP-IDF v5.x
cd src/esp32-terminal
idf.py set-target esp32s3
idf.py build
idf.py flash monitor
```

## Flash Size

Firmware: ~800KB. PLATO terminal + telnet client + sensor drivers.
Fits easily on ESP32-S3 with 4MB flash. Leaves 3MB for OTA updates and shell cache.
