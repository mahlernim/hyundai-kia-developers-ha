# Troubleshooting setup and vehicle data

[한국어](troubleshooting.md) | **English**

A missing-vehicle message can occur at different stages. First determine whether
you are still on the provider website or have already returned to Home Assistant.

## “No registered vehicles” on the provider page

This occurs before Home Assistant receives an authorization code or vehicle list.
The integration cannot change the list on that page or add a vehicle to it.

**First check whether you share your own vehicle with anyone, including family.**
A shared vehicle is excluded from the registration list even when you own it and
hold its connected-service contract. Vehicles shared with you are also excluded.
This restriction applies at vehicle access consent and is documented in the
[Hyundai](https://developers.hyundai.com/web/v1/hyundai/guide_api),
[Kia](https://developers.kia.com/web/v1/kia/guide_api), and
[Genesis](https://developers.genesis.com/web/v1/genesis/guide_api) API guides.

1. Check **vehicle sharing** in the relevant manufacturer app, such as Bluelink,
   Kia Connect, or MY GENESIS. Include sharing with family members.
2. If you choose to stop sharing, do so in that app. This also removes the other
   person's shared access in the app. Keeping sharing enabled prevents registration
   of this vehicle.
3. Confirm that the selected brand and Client ID belong to the developer project
   where the vehicle was registered.
4. Complete registration and consent under **My vehicle registration** and confirm
   that the vehicle is **active**.
5. Select **Sign in again** in Home Assistant to open a fresh authorization link
   and check the list again. Use the connected-service contract holder account.
   Sign out of the provider or use a private window if a different account's
   session is still active.

The delay before the list reflects stopped sharing has not been established, nor
has continued integration access after sharing is enabled again. Do not assume
that temporarily stopping sharing is sufficient for continued use.

If these checks do not resolve the issue, ask the provider's developer support to
check the project-to-vehicle link and account status. Explain that the problem
occurs on the provider's authorization page before returning to Home Assistant.

**Service Agreement** is a separate Data API consent step that requires an access
token. It is not documented as a workaround for an empty vehicle list before an
authorization code is issued. The integration does not automatically open this
separate consent page. Deleting projects or registering vehicles again is not
recommended as a general remedy.

In Home Assistant, leave the redirected URL empty and select **I cannot proceed
with provider login or vehicle consent** to open guidance and a setup diagnostic
summary. This records a request for help, not automatic detection of an error on
the provider website.

## Errors inside Home Assistant

| Message | Meaning and next action |
| --- | --- |
| Redirect URL or authorization code error | Check the registered address and the final URL containing `code` and `state`. A URL from a different setup attempt cannot be used. |
| Authorization code exchange failed | Codes are single-use. Choose **Sign in again** and follow the new authorization link. |
| Empty vehicle list | Login completed, but the API returned no vehicles. First check whether you share your own vehicle with someone, then check activation and consent for the same project. An empty list alone does not prove that the account is wrong. |
| Error `4045` | The vehicle list or data is unavailable. This is treated separately from a successful empty list. |
| Error `4046` | The provider could not find a registered vehicle. Check registration and activation for this project. |
| Error `5005` | Data API consent is required. Complete consent using the provider's Service Agreement guidance, then retry. |
| Error `5006` | Check the project's permission to use the requested API. |
| Request limit reached | Wait for the displayed interval, then retry. The fallback is 60 seconds when the server does not supply a delay. |
| Some existing vehicles are missing | Sign in again or explicitly continue with the current access. Existing vehicle entries remain, but requests for omitted vehicles may fail. |

**Retry** repeats the failed check with the current token. **Sign in again** starts
a new authorization attempt. If the Client ID, Client Secret, or Redirect URL is
wrong, restart setup or use **Reconfigure** on an existing account.

**Enter Car ID manually** is available when discovery returns an empty list or error
`4045` and you know the Car ID supplied by the provider API. A Car ID is not a VIN.
Manual entry cannot bypass permissions or consent and will not create an entry
unless vehicle data confirms the ID. A discovered vehicle can still be added when
some current data is unavailable.

## Values do not change after setup

The API may return the last data uploaded by the vehicle. Scheduled polling and
the **Refresh vehicle data** button do not force the vehicle to upload a new
snapshot. Repeated refreshes increase API usage.

Some entities are disabled by default or depend on data the vehicle supplies.
Check the [entity guide](../README.en.md#entities) for their availability.

## Reporting a problem

Use the [bug report form](https://github.com/mahlernim/hyundai-kia-developers-ha/issues/new?template=bug_report.yml)
and include the integration version, Home Assistant version, brand, failed stage,
and reproduction steps. The setup recovery screen provides a diagnostic summary
even before an account entry exists. `unknown` means the information was unavailable
or omitted from the public summary.

For configured accounts, you can download diagnostics from Home Assistant. Inspect
material before sharing it. Do not include Client IDs, Client Secrets, authorization
codes, tokens, full redirected URLs, Car IDs, VINs, or personal information. Send
account details needed by the provider only through its private support channel.

## Official documentation

- [Hyundai developer console guide](https://developers.hyundai.com/web/v1/hyundai/guide_console)
- [Kia developer API guide](https://developers.kia.com/web/v1/kia/guide_api)
- [Genesis developer API guide](https://developers.genesis.com/web/v1/genesis/guide_api)
- [Hyundai account authorization API](https://developers.hyundai.com/web/v1/hyundai/specification/account/account_authorize)
- [Hyundai Service Agreement API](https://developers.hyundai.com/web/v1/hyundai/specification/data/service_agreement)

[Back to installation and usage](../README.en.md)
