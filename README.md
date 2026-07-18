# Hyundai Kia Developers for Home Assistant

An unofficial Home Assistant custom integration for the Korean Hyundai and Kia
developer connected-car APIs. One authenticated brand account can contain one
or more vehicle subentries, and each vehicle is represented as a Home Assistant
device.

> This project is not affiliated with Hyundai Motor Company, Kia Corporation,
> or Home Assistant. API access and availability are controlled by the vehicle
> manufacturers.

## Features

- Hyundai and Kia accounts through one shared API implementation.
- Automatic account titles and post-OAuth vehicle discovery.
- Multiple accounts and multiple vehicles per account.
- Editable vehicle names with manual car-ID entry only as a discovery fallback.
- Native distance, EV/PHEV charging, and vehicle-warning entities.
- Vehicle-type filtering so EV-only entities are not created for GN, HEV, or
  FCEV vehicles.
- Per-entity enable/disable support; disabled entities do not activate their API
  endpoint.
- Automatic access-token renewal, refresh-token rotation persistence, and
  Home Assistant reauthentication.
- English and Korean configuration UI and redacted diagnostics.

## Requirements

- Home Assistant 2026.7.0 or newer.
- A Hyundai or Kia Korean developer application with a client ID, client secret,
  and registered redirect URI.

The existing `https://example.com/redirect` callback is supported. The page may
show an error after login; copy its complete address-bar URL into Home Assistant.
The URL and one-time code are not stored.

## Installation

### HACS custom repository

1. Add `https://github.com/mahlernim/hyundai-kia-developers-ha` to HACS as an
   Integration custom repository.
2. Install **Hyundai Kia Developers** and restart Home Assistant.
3. Open **Settings → Devices & services → Add integration** and search for
   **Hyundai Kia Developers**.

### Manual

Copy `custom_components/hyundai_kia_developers` into the Home Assistant
`config/custom_components` directory and restart Home Assistant.

## Setup

1. Select Hyundai or Kia and enter the developer client ID, client secret, and
   registered redirect URI.
2. Open the generated authorization link and complete login.
3. Paste the entire final redirected URL into Home Assistant.
4. Select one vehicle returned by the account and confirm or edit its name.

Account entries are named automatically (`Kia`, `Kia 2`, `Hyundai`, etc.).
They can be renamed later. Use **Add vehicle** on an account entry to add another
unconfigured car. If discovery is temporarily unavailable or returns no cars,
the flow offers retry and manual car-ID entry.

## Entities

Enabled for every vehicle:

- Distance to empty
- Odometer

Enabled for EV/PHEV vehicles:

- EV battery level
- Charging
- PHEV combined distance to empty when supplied by the API

Available but disabled by default:

- Charging cable connection, charger type, target charge level, and remaining
  charging time
- Low fuel, tire pressure, lamp wire, smart-key battery, washer fluid, brake
  fluid, and engine oil warnings

Enable optional entities from the vehicle's entity list. Related values from one
API response share one request; for example, all charging entities use one
charging endpoint. The default polling interval is 60 minutes and can be changed
from 30 to 1440 minutes.

## Authentication behavior

Access tokens remain in memory and are renewed shortly before expiration. Any
replacement refresh token is saved immediately. Error `4002`, or a vehicle
request rejected after a forced refresh, starts Home Assistant reauthentication.

Use **Reconfigure** to change the client ID, secret, or redirect URI. Brand is
immutable; create a separate entry for another brand.

## Migrating from Pyscript

Disable the corresponding Pyscript before authorizing this integration so two
clients do not compete for a rotated refresh token. Existing v0.1 vehicle
subentries and entity IDs remain compatible with v0.2.

## Development

```bash
python -m pip install -e .[test]
ruff check .
pytest
```

## License

MIT
