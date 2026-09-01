# ThermalTrace Home Assistant (HACS)

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![Validate](https://github.com/doodersrage/thermatrace-HACS-component/actions/workflows/validate.yaml/badge.svg)](https://github.com/doodersrage/thermatrace-HACS-component/actions/workflows/validate.yaml)

Official [Home Assistant](https://www.home-assistant.io/) custom integration for [ThermalTrace](https://thermaltrace.dev) — garage and workshop sensor monitoring with freeze alerts, history, and household sharing.

Install via [HACS](https://hacs.xyz/) as a **custom repository**:

```
https://github.com/doodersrage/thermatrace-HACS-component
```

**Product guide:** [thermaltrace.dev/integrations/home-assistant](https://thermaltrace.dev/integrations/home-assistant)

Category: **Integration**

## Features

- **Sensors** — temperature, humidity, CO₂, pressure, PM2.5, VOC, level, energy, and generic numeric probes from a share link
- **Binary sensors** — door, flood/leak, motion, and power states
- **Services** (optional, Pro inbound webhook):
  - `thermaltrace.snooze` — pause freeze alerts (`hours`, default 24)
  - `thermaltrace.vacation` — vacation mode (`days`, default 7)
  - `thermaltrace.clear_snooze` / `thermaltrace.clear_vacation`
  - `thermaltrace.status` — fetch household status snapshot
- **Push service** (optional ingest key):
  - `thermaltrace.push` — POST JSON readings to a push device (`payload` dict)

## Setup

1. Sign in at [thermaltrace.dev](https://thermaltrace.dev)
2. **Dashboard → Share** — create a share link (Pro) with **readings** scope
3. Copy the token from the URL: `https://thermaltrace.dev/share/YOUR_TOKEN`
4. In Home Assistant: **Settings → Devices & services → Add integration → ThermalTrace**
5. Paste the token; leave site URL as `https://thermaltrace.dev` unless self-hosting

### Optional: inbound webhooks (Pro)

Under **Dashboard → Share → Inbound webhooks**, create a webhook and copy the token and signing secret into the integration form. This enables snooze/vacation automations from HA.

### Optional: push from HA

Create a **push device** under **Dashboard → Devices**, copy the ingest key, and add it to the integration. Then call:

```yaml
service: thermaltrace.push
data:
  payload:
    temp1: 42.5
    humidity1: 38
```

## Manual install

Copy `custom_components/thermaltrace` into your Home Assistant `config/custom_components/` directory and restart HA.

## Development

This integration polls `GET /api/share/{token}/readings` every 5 minutes by default (configurable 60–3600 s). Push and inbound calls use the public ThermalTrace HTTP API documented at [thermaltrace.dev/openapi.yaml](https://thermaltrace.dev/openapi.yaml).

## Related

- Main app: [doodersrage/thermaltrace](https://github.com/doodersrage/thermaltrace)
- Manual HA recipes: [Home Assistant guide](https://doodersrage.github.io/thermaltrace/ingest/home-assistant)

## License

MIT — same as ThermalTrace.
