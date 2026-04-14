# Engine Room

Monitoring room for vessel propulsion and mechanical systems.

## Equipment

- **Temp sensors**: ADC for coolant, exhaust, oil (3 channels)
- **RPM sensor**: GPIO counter from tachometer
- **Fuel level**: ADC for tank sender
- **Bilge pump**: Relay (auto on water level, manual override)
- **Bilge counter**: GPIO counter (pump cycles per hour)
- **Ambient**: RGB LED (green=normal, yellow=caution, red=fault)

## Alert Thresholds

| Alert | Condition | Severity |
|-------|-----------|----------|
| High coolant | > 200°F | Warning |
| Overheat | > 220°F | Emergency |
| Low oil | < 20psi | Emergency |
| High RPM | > 3000 for > 30s | Warning |
| Bilge cycling | > 10 cycles/hour | Warning |
| Fuel low | < 15% | Warning |
| Fuel critical | < 5% | Emergency |

## Tick Configuration

| Mode | Rate |
|------|------|
| Running | 2000ms |
| Idle | 10000ms |
| Fault | 500ms |
