# 기여 안내 · Contributing

## 한국어

Hyundai Kia Genesis Developers의 오류 수정, 기능 제안과 문서 개선을 환영합니다.
먼저 기존 이슈와 최신 릴리스를 확인하고, 문제가 계속되면 버그 신고 양식을 사용해
주세요. 설정 중 오류가 발생했다면 실패한 단계와 복구 화면의 진단 요약을 함께
적어 주세요. [문제 해결 안내](docs/troubleshooting.md)에서 확인할 항목을 볼 수 있습니다.

Client ID, Client Secret, 토큰, 인증 코드가 포함된 URL, Car ID, VIN과 개인정보를
이슈나 PR에 포함하지 마세요. 첨부할 진단 정보와 로그도 공유 전에 확인하세요.

- 한국어 사용자가 이해하기 쉬운 안내와 동등한 영문 안내를 함께 제공합니다.
- 화면 문구를 변경하면 `strings.json`, `translations/en.json`, `translations/ko.json`을
  함께 수정합니다. 한국어 문서는 기본 문서로, 영문 문서는 `.en.md`로 연결합니다.
- 변경된 동작과 호환성 영향을 설명하고, 필요한 회귀 테스트를 추가합니다.
- 테스트에는 가상 계정과 차량 데이터를 사용합니다. 실제 API 응답을 포함하지 않습니다.
- 설정 구조가 바뀌지 않는 패치에서는 설정 항목의 `VERSION`과 `MINOR_VERSION`을
  유지합니다. 구조를 변경하면 마이그레이션과 테스트가 필요합니다.

## 개발 환경 및 검증 · Development and validation

Python 3.14와 Home Assistant 2026.7 이상을 사용합니다.
Use Python 3.14 and Home Assistant 2026.7 or newer.

```bash
python -m pip install -e ".[test]" ruff
ruff format --check .
ruff check .
pytest
```

CI에서 위 검사와 Home Assistant **hassfest**, **HACS validation**을 실행합니다.
CI runs these checks together with Home Assistant **hassfest** and **HACS validation**.

## English

Bug fixes, feature proposals, and documentation improvements are welcome. Search
existing issues and check the latest release before using the bug report form.
For setup failures, include the failed stage and diagnostic summary from the
recovery screen. See the [troubleshooting guide](docs/troubleshooting.en.md).

Do not include Client IDs, Client Secrets, tokens, authorization codes or full
redirected URLs, Car IDs, VINs, or personal information. Inspect diagnostics and
logs before sharing them.

- Keep Korean user guidance clear and provide equivalent English guidance.
- Update `strings.json`, `translations/en.json`, and `translations/ko.json` together
  when changing interface text. Link primary Korean documents to `.en.md` companions.
- Explain the behavior and compatibility impact, and add relevant regression tests.
- Use synthetic account and vehicle fixtures instead of captured API responses.
- Keep config-entry `VERSION` and `MINOR_VERSION` unchanged for patches without a
  schema change. Schema changes require a migration and tests.

기여한 내용에는 저장소의 [MIT License](LICENSE)가 적용됩니다.
Contributions are licensed under this repository's [MIT License](LICENSE).
