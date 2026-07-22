# Changelog

## 0.2.7

- Accepted the Genesis OAuth success marker `result=0000` while continuing to
  reject nonzero provider result codes.

## 0.2.6

- Added Korean Genesis Developers account, vehicle discovery, and vehicle data
  support.
- Added Genesis-specific authorization parameters, API hosts, and HTTP 200
  token-error handling while retaining the shared Hyundai/Kia vehicle schema.
- Made Korean the primary README and developer setup guide, with linked English
  companion documents.
- Expanded the shared Hyundai, Kia, and Genesis project registration guide with
  step-by-step instructions and a screenshot of the three separate Save buttons.

## 0.2.5

- Allowed vehicle setup to continue when the DTE or odometer endpoint reports
  provider error `4045` because current vehicle data is temporarily unavailable.
- Preserved safe provider error codes and endpoint context during validation.
- Added actionable English and Korean setup guidance for every documented
  vehicle API error code.

## 0.2.4

- Trimmed surrounding whitespace from developer credentials and redirect URIs.
- Added field-level checks for blank credentials and sample placeholders.
- Added a non-blocking confirmation for credentials that differ from commonly
  observed Client ID and Client Secret formats.
- Improved credential troubleshooting and synchronized English OAuth error
  translations.

## 0.2.3

- Added specific, actionable errors for malformed OAuth redirects, provider
  errors, state mismatches, missing codes, rejected token exchanges, and missing
  refresh tokens.

## 0.2.2

- Simplified the English and Korean documentation around HACS installation,
  developer-project preparation, authorization, vehicles, entities, and common
  troubleshooting.

## 0.2.1

- Added original integration icons and landscape logos for local Home Assistant
  branding.
- Added complete English and Korean setup documentation, including developer
  project creation and the OAuth redirect-paste flow.
- Added security, contribution, and issue-reporting policies for public release.
- Clarified the context-specific meaning of API error `4002`.
- Added Korean HACS metadata and expanded continuous-integration validation.

## 0.2.0

- Added automatic account naming and post-OAuth vehicle discovery.
- Added editable discovered-vehicle naming and a failure-only manual fallback.
- Added EV/PHEV battery and charging entities.
- Added seven optional warning binary sensors.
- Added vehicle-type filtering and more efficient polling.
- Added documented distance and duration unit normalization.
- Preserved v0.1 account, vehicle, device, and entity compatibility.

## 0.1.0

- Initial Hyundai/Kia account, multi-vehicle, DTE, odometer, OAuth, reauth, and
  refresh-token rotation support.
