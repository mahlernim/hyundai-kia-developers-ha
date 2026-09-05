# Hyundai Kia Genesis Developers for Home Assistant

[한국어](README.md) | **English**

![Hyundai Kia Genesis Developers](custom_components/hyundai_kia_developers/brand/logo.png)

An unofficial Home Assistant integration for viewing vehicle data from the
Korean Hyundai, Kia, and Genesis developer APIs. It supports multiple accounts
and vehicles, discovers authorized vehicles automatically, and renews authorization
when needed. It reads vehicle data and does not provide remote controls such as
door locks or climate control.

> This integration supports the Korean developer service only. Accounts,
> projects, and vehicles from other regions are not compatible.

## Requirements

- Home Assistant 2026.7.0 or newer
- HACS
- A Korean Hyundai, Kia, or Genesis developer membership and project
- A vehicle registered to your own Bluelink, Kia Connect, or Genesis Connected
  Services account

Each brand requires a separate developer membership and project. Use the connected
service contract holder account.

> **A vehicle you share with someone else, including a family member, is excluded
> from the registration list even when you own it and sign in with the owner account.**
> Vehicles shared with you are also excluded. Check sharing in the manufacturer app
> before installing.

If you choose to stop sharing, do so in the manufacturer app and start a fresh
authorization attempt to check the list again. Stopping sharing also removes the
other person's shared access in the app. See the [vehicle-sharing guidance](docs/troubleshooting.en.md#no-registered-vehicles-on-the-provider-page).

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
5. At the registered redirect address, copy the complete URL containing `code`
   and `state` and paste it into Home Assistant. An `example.com` page error can
   be ignored only after reaching that final address with both values.
6. Select the discovered vehicle and confirm its name.

The redirected URL contains a single-use authorization code. Do not include it
in logs, screenshots, messages, or issues.

## Entities

| Entity | Availability | Default |
| --- | --- | --- |
| Distance to empty | All vehicles | Enabled |
| Odometer | All vehicles | Enabled |
| Connected service free days remaining | When the API supplies a free-service end date | Enabled |
| EV battery level and charging | EV and PHEV | Enabled |
| Combined distance to empty | PHEV, when supplied by the API | Enabled |
| Charging cable, charger type, charge target, and remaining charging time | EV and PHEV | Disabled |
| Combined vehicle warning | All vehicles | Enabled |
| Individual fuel, tire, lamp, smart-key battery, washer-fluid, brake-fluid, and engine-oil warnings | When supplied by the vehicle | Disabled |
| Refresh vehicle data | Each configured account | Enabled |

Disabled entities can be enabled from the vehicle's Home Assistant device
page. Vehicle data is refreshed every 60 minutes by default. The integration
options allow an interval from 30 to 1440 minutes.

The combined vehicle warning is on when any available warning endpoint reports
a problem. Its `warning_count`, `active_warnings`, and `unavailable_warnings`
attributes provide details using stable identifiers suitable for automations.
Polling it requires seven API requests per vehicle during each refresh. Enabling
individual warning entities reuses those requests. If an individual warning
request fails, the combined sensor continues using the available results and
lists the failed identifier in `unavailable_warnings`.

The connected-service sensor counts down to the free-service end date supplied
by the provider. Its `subscription_date`, `free_service_end_date`, and `expired`
attributes use stable names suitable for automations. The state remains zero
after the date has passed. The sensor is unavailable when the API does not
supply a valid free-service end date. Polling it adds one API request per
enabled vehicle during each refresh.

The account-level **Refresh vehicle data** button requests an immediate update
of every currently enabled endpoint for all vehicles in that account. Each
press therefore repeats the API requests that would run during a scheduled
refresh.

## Accounts and vehicles

Account names are generated automatically, for example `Kia`, `Hyundai`, and
`Genesis`. Use **Add vehicle** on an existing account to add another authorized
vehicle. Add a separate account for each brand.

## Troubleshooting

The [troubleshooting guide](docs/troubleshooting.en.md) distinguishes these cases.

- **No registered vehicles** on the provider login page
- An empty vehicle list or provider error after returning to Home Assistant
- Request limits, failed reauthentication, or missing access to some vehicles
- Unchanged data or missing entities after setup

Select the help option on the authorization form if you cannot proceed on the
provider page. After an error, the recovery screen offers retry or fresh sign-in
as appropriate. Failed reauthentication validation does not change or delete
existing account and vehicle configuration.

## Updates and support

Install the latest release through HACS and restart Home Assistant. See the
[changelog](CHANGELOG.md) and [contribution and bug-report guide](CONTRIBUTING.md).
Report security concerns privately as described in the [security policy](SECURITY.md).

## Disclaimer and license

This non-profit project is not affiliated with, endorsed by, or sponsored by
Hyundai Motor Company, Kia Corporation, Genesis, or Home Assistant. Hyundai,
Kia, and Genesis names and related trademarks belong to their respective owners
and are used only to identify API compatibility.

Licensed under the [MIT License](LICENSE).
