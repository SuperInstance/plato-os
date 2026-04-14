# Fleet: Snail Shell Reference Library

Cloud-hosted collection of accumulated edge wisdom from all vessels.
Pulled by ships during boot or when a new ensign beams aboard.

## Directory Structure

```
fleet/
  snail-shells/
    alaska-trolling/
      nav-station-base/        # most common: Alaska trolling nav
        calibration.md
        seasonal-patterns.md
        common-quirks.md
      engine-room-base/
      back-deck-base/
    caribbean-cruising/
      nav-station-base/
    great-lakes-fishing/
      nav-station-base/
    pnw-puget-sound/
      nav-station-base/
  
  ensigns/
    ensign-navigator-v2/       # navigation specialist
      SKILL.md
      procedures.md
      shell-hooks.md
    ensign-engineer-v3/        # engine monitoring specialist
    ensign-fisherman-v1/       # fishing operations
    ensign-dockmaster-v4/      # docking procedures
  
  rooms/
    navigation/templates/      # room design patterns
    engine/templates/
    workshop/templates/
```

## How Shells Get Here

1. Ensign operates on a vessel for a season
2. Accumulates calibration, quirks, procedures in local shell
3. At season end: `plato-shell push --anonymize --fleet alaska-trolling`
4. Shell is reviewed, deduplicated, merged with fleet average
5. Available for next vessel to pull on boot

## Anonymization

Before pushing to fleet, shells are anonymized:
- Captain preferences removed
- Vessel-specific serial numbers replaced with generic IDs
- Location history aggregated (not precise tracks)
- Retained: sensor calibrations, seasonal patterns, failure modes

## Usage

```bash
# Pull fleet wisdom for this region/activity
plato-shell pull --fleet alaska-trolling --room navigation

# Pull a specialist ensign
plato-shell pull --ensign ensign-navigator-v2

# Push accumulated wisdom (anonymized)
plato-shell push --anonymize --fleet alaska-trolling

# Browse available fleet shells
plato-shell list --fleet
```
