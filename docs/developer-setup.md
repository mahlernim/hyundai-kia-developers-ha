# Developer project and first vehicle setup

[English](developer-setup.md) | [한국어](developer-setup.ko.md)

This guide covers the Korean developer service. Accounts, projects, and API
access from other regions are not interchangeable with it.

## 1. Prepare the connected-car account

The vehicle must be registered to the account you will authorize in Bluelink
(Hyundai) or Kia Connect (Kia). A vehicle shared with you by another owner may
not appear in the developer console or vehicle-list API.

Hyundai and Kia developer memberships are separate. If you own one vehicle from
each brand, complete this guide twice and create two Home Assistant accounts.

## 2. Join and create a project

1. Open the official console guide for your brand:
   [Hyundai console guide](https://developers.kia.com/web/v1/hyundai/guide_console)
   or [Kia console guide](https://developers.kia.com/web/v1/kia/guide_console).
2. Sign up for that brand's developer membership and sign in to its console:
   [Hyundai Developer Console](https://console.developers.hyundai.com) or
   [Kia Developer Console](https://console.developers.kia.com).
3. Create a development project. The console exposes the APIs available to a
   development project; accept the applicable terms shown there.
4. Open the project overview and copy its **Client ID** and **Client Secret** to
   a password manager. Never commit, screenshot, or post either value.
5. In project settings, set the **Account API Redirect URL** to exactly:

   ```text
   https://example.com/redirect
   ```

   The scheme, hostname, path, and absence of a trailing slash must match.

## 3. Activate the vehicle

Open **My Vehicle** in the developer console. Select and activate the vehicle
owned by your connected-car account. If it is absent, verify the brand account,
vehicle ownership, and active Bluelink/Kia Connect subscription. Shared vehicles
may be unavailable by design.

## 4. Add the Home Assistant integration

1. Install the integration and restart Home Assistant.
2. Go to **Settings → Devices & services → Add integration**, search for
   **Hyundai Kia Developers**, and choose the correct brand.
3. Enter the project Client ID, Client Secret, and
   `https://example.com/redirect`.
4. Open the authorization URL presented by Home Assistant. Sign in with the
   same connected-car account and approve access.
5. After authorization, the browser navigates to `example.com`. The page may
   show an error. Copy the **complete current URL** from the address bar,
   including `code` and `state`, and paste it into Home Assistant immediately.
6. Select a discovered vehicle and confirm or edit its suggested name.
7. Open the new device and confirm that distance-to-empty and odometer values
   update. Add another unconfigured vehicle from the account menu if required.

The one-time redirect code is sensitive. Do not place the URL in logs, issues,
chat, or screenshots. The integration exchanges the code and does not store the
submitted URL.

## Scope and use

This integration targets the documented Korean APIs and is intended for
personal development use. Developer access does not grant permission for a
commercial service. Review the current console terms and contact the respective
manufacturer before commercial or redistributed use. API availability, quotas,
and policies remain under manufacturer control.
