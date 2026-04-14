# Hat Specifications

Equipment manifests for ESP32 add-on boards. Each hat defines
what sensors and actuators are available in a room.

## Hat Manifest Format

```json
{
  "hat_id": "nav_hat_v1",
  "name": "Navigation Hat v1",
  "version": "1.0.0",
  "author": "lucineer",
  "compatible": ["esp32-s3"],
  "senses": [],
  "actions": [],
  "overrides": []
}
```

## Available Hats

| Hat | Senses | Actions | Use Case |
|-----|--------|---------|----------|
| nav_hat_v1 | depth, gps, ais, water_temp | bilge, lights, anchor, ambient | Navigation station |
| engine_hat_v1 | coolant, exhaust, oil, rpm, fuel | bilge, ambient | Engine monitoring |
| deck_hat_v1 | float_switch | flood_lights, downrigger, hauler, ambient | Back deck |
| workshop_hat_v1 | (none) | (none) | Pure compute (no GPIO) |
| minimal_hat_v1 | (none) | ambient | Basic terminal with LED |

## Creating a New Hat

1. Copy an existing hat manifest
2. Modify pins, sensors, actions
3. Test on breadboard
4. Commit to `hats/` directory
5. The ensign reads the manifest and knows what changed

## Hat Growth

Like snail shells, hats accumulate wisdom:

```
hats/nav_hat_v1/
  manifest.json         # hardware specification
  calibration/           # device-specific offsets
  quirks.md             # known issues with this hat design
  improvements.md       # v2 ideas from field experience
```
