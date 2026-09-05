# 보안 정책 · Security policy

## 한국어

취약점이나 자격 증명 노출은 공개 이슈로 신고하지 마세요.
[GitHub 비공개 취약점 신고](https://github.com/mahlernim/hyundai-kia-developers-ha/security/advisories/new)를
사용해 주세요. 사용할 수 없다면 유지관리자의 GitHub 프로필에 안내된 비공개 연락
방법을 이용하세요.

재현에 필요한 최소한의 정보만 보내 주세요. Client ID, Client Secret, 액세스 토큰과
갱신 토큰, 인증 코드, 전체 리디렉션 URL, Car ID, VIN, Home Assistant 액세스 토큰을
포함하지 마세요. 보안 수정은 최신 정식 릴리스에 제공합니다.

자격 증명은 Home Assistant 설정 항목에 저장됩니다. 액세스 토큰은 메모리에
보관하고, 갱신 토큰이 교체되면 이후 인증을 위해 저장합니다. 설정 복구 화면의
진단 요약에는 인증 정보나 차량 식별자를 포함하지 않습니다. 다운로드한 진단
정보도 주요 식별자를 가리지만, 공유 전 내용을 직접 확인해 주세요.

자격 증명이나 인증 URL을 공개했다면 해당 현대, 기아 또는 제네시스 개발자
서비스에서 폐기·재발급 방법을 확인하고 통합 구성요소를 다시 인증하세요.

## English

### Reporting a vulnerability

Do not open a public issue for a vulnerability or suspected credential leak.
Use GitHub's private vulnerability reporting for this repository. If that
option is unavailable, contact the maintainer through the private contact method
listed on their GitHub profile.

Include only the minimum reproduction details. Never include a Client ID,
Client Secret, access or refresh token, authorization code, complete OAuth
redirect URL, car ID, VIN, Home Assistant access token, or unredacted diagnostics.

### Supported versions

Security fixes are provided for the latest published release. Users should
update before reporting behavior already fixed on `main`.

### Credential handling

Credentials are stored in Home Assistant config entries. Access tokens are
kept in memory; rotated refresh tokens are persisted so later refreshes remain
valid. The setup recovery summary excludes credentials and vehicle identifiers.
Downloaded diagnostics redact configured credentials, tokens, and vehicle IDs, but
reporters must inspect exported material before sharing it.

If a secret or OAuth redirect URL has been disclosed, revoke or rotate it in
the appropriate Hyundai, Kia, or Genesis developer service and reauthorize the integration.
