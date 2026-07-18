# Changelog

## 0.2.1

- Added original integration icons and landscape logos for local Home Assistant
  branding.
- Added complete English and Korean setup documentation, including developer
  project creation and the OAuth redirect-paste flow.
- Added a Pyscript history migration guide with Recorder and Grafana/InfluxDB
  guidance.
- Added security, contribution, and issue-reporting policies for public release.
- Corrected the endpoint-specific meaning of API error `4002`.
- Added Korean HACS metadata and expanded continuous-integration validation.
- No runtime, entity, polling, config-flow, or config-entry schema behavior
  changed in this release.

## 0.2.0

- Added automatic account naming and post-OAuth vehicle discovery.
- Added editable discovered-vehicle naming and a failure-only manual fallback.
- Added EV/PHEV battery and charging entities.
- Added seven optional warning binary sensors.
- Added vehicle-type applicability filtering and endpoint-grouped polling.
- Added documented distance and duration unit normalization.
- Preserved v0.1 account, vehicle, device, and entity compatibility.

## 0.1.0

- Initial Hyundai/Kia account, multi-vehicle, DTE, odometer, OAuth, reauth, and
  refresh-token rotation support.
