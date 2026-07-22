# Hyundai Kia Genesis Developers for Home Assistant

[한국어](README.md) | **English**

![Hyundai Kia Genesis Developers](custom_components/hyundai_kia_developers/brand/logo.png)

An unofficial Home Assistant integration for viewing vehicle data from the
Korean Hyundai, Kia, and Genesis developer APIs. It supports multiple accounts
and vehicles, discovers owned vehicles automatically, and renews authorization
when needed.

> This integration supports the Korean developer service only. Accounts,
> projects, and vehicles from other regions are not compatible.

## Requirements

- Home Assistant 2026.7.0 or newer
- HACS
- A Korean Hyundai, Kia, or Genesis developer membership and project
- A vehicle registered to your own Bluelink, Kia Connect, or Genesis Connected
  Services account

Each brand requires a separate developer membership and project. Shared
vehicles may not be available through the developer API.

## Install with HACS

1. In HACS, open **Custom repositories**.
2. Add `https://github.com/mahlernim/hyundai-kia-developers-ha` as an
   **Integration** repository.
3. Install **Hyundai Kia Genesis Developers** and restart Home Assistant.

## Prepare the developer project

Follow the [English developer-project guide](docs/developer-setup.en.md) to
create the project, register the vehicle, save all three URLs, and obtain the
Client ID and Client Secret.

All three brands use these values.

| Setting | Value |
| --- | --- |
| Account API Redirect URL | `https://example.com/redirect` |
| Data API Redirect URL | `https://example.com/redirect` |
| Data API Callback URL | `https://example.com/callback` |

Each field has its own **Save** button. Saving one field does not save either
of the other fields.

## Add an account and vehicle in Home Assistant

1. Open **Settings → Devices & services → Add integration** and select
   **Hyundai Kia Genesis Developers**.
2. Choose Hyundai, Kia, or Genesis.
3. Enter the Client ID and Client Secret from that brand's project.
4. Open the authorization link, sign in to the connected-car account, and
   approve access.
5. When the browser reaches `example.com`, copy the complete address-bar URL
   and paste it into Home Assistant. A blank or error page is expected.
6. Select the discovered vehicle and confirm its name.

The redirected URL contains a single-use authorization code. Do not include it
in logs, screenshots, messages, or issues.

## Entities

| Entity | Availability | Default |
| --- | --- | --- |
| Distance to empty | All vehicles | Enabled |
| Odometer | All vehicles | Enabled |
| EV battery level and charging | EV and PHEV | Enabled |
| Combined distance to empty | PHEV, when supplied by the API | Enabled |
| Charging cable, charger type, charge target, and remaining charging time | EV and PHEV | Disabled |
| Fuel, tire, lamp, smart-key battery, washer-fluid, brake-fluid, and engine-oil warnings | When supplied by the vehicle | Disabled |

Disabled entities can be enabled from the vehicle's Home Assistant device
page. Vehicle data is refreshed every 60 minutes by default. The integration
options allow an interval from 30 to 1440 minutes.

## Accounts and vehicles

Account names are generated automatically, for example `Kia`, `Hyundai`, and
`Genesis`. Use **Add vehicle** on an existing account to add another owned
vehicle. Add a separate account for each brand.

## Troubleshooting

- **No vehicles found** Confirm the brand account, connected-service contract,
  and **My vehicle registration** status in the developer project.
- **The redirect page shows an error** This is expected. Paste the complete URL
  from the browser address bar into Home Assistant.
- **Client ID is not registered** Copy the credentials from the selected
  brand's project and confirm that all three URLs were saved with their separate
  **Save** buttons.
- **Authorization expired** Follow the reauthentication prompt. Use
  **Reconfigure** only when the Client ID, Client Secret, or Redirect URL has
  changed.
- **Error `4002`** During authorization or token renewal it requires
  reauthorization. During a vehicle update it means the request was invalid and
  does not by itself mean that account authorization expired.
- **A value has not changed** Wait for the next polling interval or reload the
  integration entry.
- **An entity is missing** Some entities depend on the vehicle type and data
  made available by the manufacturer.

## Disclaimer and license

This non-profit project is not affiliated with, endorsed by, or sponsored by
Hyundai Motor Company, Kia Corporation, Genesis, or Home Assistant. Hyundai,
Kia, and Genesis names and related trademarks belong to their respective owners
and are used only to identify API compatibility.

Licensed under the [MIT License](LICENSE).
