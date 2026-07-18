# Hyundai Kia Developers for Home Assistant

[English](README.md) | [한국어](README.ko.md)

![Hyundai Kia Developers](custom_components/hyundai_kia_developers/brand/logo.png)

An unofficial, non-profit Home Assistant custom integration for the Korean
Hyundai and Kia developer connected-car APIs. One brand account can contain
multiple vehicle subentries, and each vehicle appears as a Home Assistant
device.

> This project is not affiliated with, endorsed by, or sponsored by Hyundai
> Motor Company, Kia Corporation, or Home Assistant. Hyundai and Kia names and
> related trademarks belong to their respective owners. They are used only to
> identify API compatibility.

## Features

- Hyundai and Kia accounts through one shared implementation.
- Automatic account naming and post-OAuth vehicle discovery.
- Multiple accounts and multiple vehicles per account.
- Native distance, EV/PHEV charging, and vehicle-warning entities.
- Vehicle-type filtering and per-entity enable/disable support.
- Automatic access-token renewal, refresh-token rotation persistence, and
  Home Assistant reauthentication.
- English/Korean setup UI and redacted diagnostics.

## Requirements

- Home Assistant 2026.7.0 or newer.
- A Korean Hyundai or Kia developer membership and project.
- The vehicle registered to your own Bluelink or Kia Connect account.

Hyundai and Kia require separate developer memberships and projects. Follow the
[English developer-project guide](docs/developer-setup.md) from signup through
the first working entity.

## Installation

### HACS custom repository

1. Open HACS, select **Custom repositories**, and add
   `https://github.com/mahlernim/hyundai-kia-developers-ha` as an
   **Integration** repository.
2. Install **Hyundai Kia Developers** and restart Home Assistant.
3. Open **Settings → Devices & services → Add integration** and search for
   **Hyundai Kia Developers**.

### Manual

Copy `custom_components/hyundai_kia_developers` into Home Assistant's
`config/custom_components` directory and restart Home Assistant.

## Setup overview

1. Create a project in the appropriate developer console, enable your owned
   vehicle under **My Vehicle**, and register the exact Account API Redirect URL
   `https://example.com/redirect`.
2. Add the integration, select Hyundai or Kia, and enter the project's Client
   ID and Client Secret.
3. Open the authorization link, sign in, then copy the complete final
   `https://example.com/redirect?...` URL from the browser address bar.
4. Paste that complete URL into Home Assistant and select a discovered vehicle.

The `example.com` page itself may be blank or show an error; only its complete
address-bar URL is needed. Treat the authorization code in that URL like a
password until the setup flow consumes it.

Account entries are named automatically (`Kia`, `Kia 2`, `Hyundai`, etc.). Use
**Add vehicle** on an account entry to add another unconfigured car.

## Entities

Distance to empty and odometer are enabled for every vehicle. Compatible
EV/PHEV vehicles also receive enabled EV battery, charging, and (when supplied)
combined PHEV range entities. Cable connection, charger details, charge target,
remaining charge time, and seven warning binary sensors are available but
disabled by default.

Related values share one endpoint request. Disabled entities do not activate
their endpoint. The default polling interval is 60 minutes and can be changed
from 30 to 1440 minutes.

## Authentication and error `4002`

Access tokens remain in memory and are renewed shortly before expiration. Any
rotated refresh token is saved immediately.

- A `4002` response from the **token endpoint** means the authorization or
  refresh credential is no longer accepted and requires reauthorization.
- A `4002` response from a **vehicle data endpoint** means that vehicle request
  is invalid; it does not by itself prove that the OAuth credential expired.
- A vehicle request still rejected as unauthorized after one forced token
  refresh starts Home Assistant reauthentication.

Use **Reconfigure** to replace a Client ID, Client Secret, or redirect URI. The
brand is immutable; create a separate entry for the other brand.

## Migrating from Pyscript

Disable the old Hyundai/Kia Pyscripts before authorizing this integration so two
clients do not compete for a rotated refresh token. The
[Pyscript migration and history guide](docs/pyscript-migration.md) includes
entity mappings, Recorder retention constraints, and Grafana/InfluxDB union
queries that preserve existing history without rewriting it.

## Support and development

Before reporting a problem, read [SECURITY.md](SECURITY.md) and use a GitHub
issue form. Never post credentials, OAuth redirect codes, refresh tokens, or car
IDs. Contributions are described in [CONTRIBUTING.md](CONTRIBUTING.md).

```bash
python -m pip install -e .[test]
ruff format --check .
ruff check .
pytest
```

## License

MIT
