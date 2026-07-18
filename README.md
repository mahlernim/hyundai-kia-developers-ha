# Hyundai Kia Developers for Home Assistant

An unofficial Home Assistant custom integration for the Korean Hyundai and Kia
developer connected-car APIs. One authenticated brand account can contain one
or more vehicles, and every vehicle is represented as its own Home Assistant
device.

> This project is not affiliated with Hyundai Motor Company, Kia Corporation,
> or Home Assistant. API access and availability are controlled by the vehicle
> manufacturers.

## Features

- Hyundai and Kia accounts using the same shared client implementation.
- Multiple accounts and multiple vehicles per account.
- Native distance-to-empty and odometer sensors.
- Per-entity enable/disable support through Home Assistant's entity registry.
- Automatic access-token renewal and rotated refresh-token persistence.
- Home Assistant reauthentication when a refresh token expires or is revoked.
- English and Korean configuration UI.
- Redacted diagnostics.

## Requirements

- Home Assistant 2026.7.0 or newer.
- A Hyundai or Kia Korean developer application with a client ID and client
  secret.
- The application's registered redirect URI.
- The car ID for every vehicle you want to add.

The existing `https://example.com/redirect` callback is supported. Because
Home Assistant cannot read that browser tab automatically, setup asks you to
paste the complete redirected URL after login. The URL and one-time code are
used only during the active config flow and are not stored.

## Installation

### HACS custom repository

1. In HACS, add
   `https://github.com/mahlernim/hyundai-kia-developers-ha` as an Integration
   custom repository.
2. Install **Hyundai Kia Developers**.
3. Restart Home Assistant.
4. Go to **Settings → Devices & services → Add integration** and search for
   **Hyundai Kia Developers**.

### Manual

Copy `custom_components/hyundai_kia_developers` into your Home Assistant
`config/custom_components` directory and restart Home Assistant.

## Account setup

1. Select Hyundai or Kia and enter an account label, client ID, client secret,
   and registered redirect URI.
2. Open the generated authorization link and complete login.
3. Copy the entire final redirect URL from the browser address bar and paste it
   into the Home Assistant form.
4. Add the first vehicle's friendly name and car ID.

Use **Add vehicle** on the integration entry to add more cars belonging to the
same account. A second account, including another account of the same brand,
is configured as a separate integration entry.

## Sensors

Version 0.1.0 provides:

- Distance to empty (`km`, measurement)
- Odometer (`km`, total increasing)

Sensors can be enabled or disabled individually in Home Assistant. Disabled
sensors do not cause their metric endpoint to be called during scheduled
updates.

The default polling interval is 60 minutes and can be changed from the
integration's options. The supported range is 30 to 1440 minutes.

## Authentication behavior

Access tokens remain in memory and are renewed shortly before expiration. If
the provider returns a replacement refresh token, the integration stores it in
the config entry. Authentication error `4002`, or a vehicle request rejected
after one forced refresh, starts Home Assistant's reauthentication flow.

If the developer client ID, client secret, or redirect URI changes, use
**Reconfigure** before reauthorizing.

## Migrating from Pyscript

Configure and validate one brand at a time. Disable the corresponding Pyscript
app before authorizing this integration so two clients do not compete for a
rotated refresh token. Keep the old helpers temporarily while dashboard cards
are changed to the new native sensor entities.

## Development

```bash
python -m pip install -e .[test]
ruff check .
pytest
```

## License

MIT
