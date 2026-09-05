# Changelog

## 0.2.10

### 한국어

- 제조사 인증 화면, 토큰 발급, 차량 목록과 데이터 확인 단계에 맞는 오류 안내와
  복구 화면을 추가했습니다. 설정 전에도 안전한 진단 요약을 복사할 수 있습니다.
- 요청 제한과 응답 지연을 처리하고, 재시도 시 대기 시간과 현재 인증을 유지합니다.
  인증 코드 교환에 실패하면 새 인증 절차를 시작합니다.
- 빈 차량 목록과 오류 `4045`를 구별하고, 재인증 중 확인되지 않은 목록을 다른
  계정으로 단정하지 않도록 수정했습니다. 일부 기존 차량이 빠지면 저장 전에 안내합니다.
- 재시도 시 입력한 차량 이름을 유지하고, 수동 Car ID 등록에는 차량 데이터 확인을
  요구합니다. 정상 설정의 단계와 API 요청 수는 유지됩니다.
- 한국어·영문 설치 및 문제 해결 안내, 기여·보안 정책과 이슈 양식을 정리했습니다.

### English

- Added recovery guidance for provider authorization, token exchange, vehicle
  discovery, and validation, with safe diagnostics available before setup completes.
- Handled rate limits and response-body timeouts. Retries respect the wait interval
  and reuse current authorization. Failed code exchange requires a fresh sign-in.
- Distinguished empty lists from error `4045` and stopped treating inconclusive
  reauthentication results as a different account. Partial vehicle access now
  requires a choice before saving.
- Preserved entered vehicle names on retry and required vehicle data to confirm
  manually entered Car IDs. Successful setup keeps its steps and API request count.
- Updated Korean and English setup, troubleshooting, contribution and security
  guidance, and issue forms.

## 0.2.9

- Added safe provider error codes, endpoint identifiers, and HTTP statuses to
  downloaded diagnostics for unavailable vehicle metrics.
- Distinguished provider rejections from successful responses containing
  invalid metric data without including API response bodies.

## 0.2.8

- Accepted successful warning responses with documented Boolean states or a
  message identifier when no warning is active.
- Added an enabled combined vehicle warning with stable active and unavailable
  warning attributes.
- Added an enabled connected-service free-days sensor with contract date and
  expiration attributes when the provider supplies a free-service end date.
- Added an account-level button for immediately refreshing all enabled vehicle
  data.

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
