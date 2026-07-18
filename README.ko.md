# Home Assistant용 Hyundai Kia Developers

[English](README.md) | [한국어](README.ko.md)

![Hyundai Kia Developers](custom_components/hyundai_kia_developers/brand/logo.png)

대한민국 현대자동차 및 기아 개발자 커넥티드 카 API를 사용하는 비공식,
비영리 Home Assistant 커스텀 통합 구성요소입니다. 브랜드 계정 하나에 여러
차량을 추가할 수 있으며 각 차량은 Home Assistant 장치 하나로 표시됩니다.

> 이 프로젝트는 현대자동차, 기아 또는 Home Assistant와 제휴하거나 이들의
> 승인·후원을 받지 않았습니다. Hyundai와 Kia 명칭 및 관련 상표의 권리는 각
> 소유자에게 있으며, 여기서는 API 호환성을 식별하기 위해서만 사용합니다.

## 주요 기능

- 하나의 공통 구현으로 현대 및 기아 계정 지원
- OAuth 후 자동 계정 이름 생성 및 차량 검색
- 계정별 복수 차량과 복수 계정 지원
- 주행 가능 거리, 누적 주행 거리, EV/PHEV 충전 및 차량 경고 엔티티
- 차량 종류별 엔티티 필터링과 엔티티별 활성화/비활성화
- 액세스 토큰 자동 갱신, 회전된 리프레시 토큰 저장 및 재인증
- 한국어/영어 설정 화면과 민감정보를 제거한 진단 정보

## 요구 사항

- Home Assistant 2026.7.0 이상
- 대한민국 현대 또는 기아 개발자 회원 및 개발 프로젝트
- 본인의 Bluelink 또는 Kia Connect 계정에 등록된 차량

현대와 기아는 개발자 회원 및 프로젝트를 각각 만들어야 합니다. 가입부터 첫
엔티티 확인까지 [한국어 개발 프로젝트 설정 안내](docs/developer-setup.ko.md)를
따르세요.

## 설치

### HACS 커스텀 저장소

1. HACS의 **Custom repositories**에서
   `https://github.com/mahlernim/hyundai-kia-developers-ha`를
   **Integration** 유형으로 추가합니다.
2. **Hyundai Kia Developers**를 설치하고 Home Assistant를 재시작합니다.
3. **설정 → 기기 및 서비스 → 통합 구성요소 추가**에서
   **Hyundai Kia Developers**를 검색합니다.

### 수동 설치

`custom_components/hyundai_kia_developers` 폴더를 Home Assistant의
`config/custom_components` 아래에 복사하고 재시작합니다.

## 설정 요약

1. 해당 개발자 콘솔에서 프로젝트를 만들고 **My Vehicle**에서 본인 차량을
   활성화한 뒤 Account API Redirect URL을 정확히
   `https://example.com/redirect`로 등록합니다.
2. 통합 구성요소를 추가하고 Hyundai 또는 Kia를 선택한 뒤 프로젝트의 Client
   ID와 Client Secret을 입력합니다.
3. 인증 링크를 열어 로그인한 후 브라우저 주소 표시줄의 최종
   `https://example.com/redirect?...` URL 전체를 복사합니다.
4. 전체 URL을 Home Assistant에 붙여 넣고 검색된 차량을 선택합니다.

`example.com` 페이지가 비어 있거나 오류를 표시해도 괜찮습니다. 주소 표시줄의
전체 URL만 필요합니다. 설정이 완료될 때까지 URL 안의 인증 코드는 비밀번호처럼
보호하세요.

계정 이름은 `Kia`, `Kia 2`, `Hyundai`처럼 자동 생성됩니다. 같은 계정의 다른
차량은 계정 메뉴의 **차량 추가**에서 추가합니다.

## 엔티티

모든 차량에 주행 가능 거리와 누적 주행 거리가 기본 활성화됩니다. 호환되는
EV/PHEV에는 배터리 잔량, 충전 상태 및 API가 제공하는 경우 PHEV 통합 주행
가능 거리가 추가됩니다. 케이블 연결, 충전기 정보, 목표 충전량, 남은 충전 시간과
7개 경고 이진 센서는 기본 비활성화 상태로 제공됩니다.

같은 API 응답의 값은 한 번의 요청을 공유하며 비활성화된 엔티티는 해당 API를
호출하지 않습니다. 기본 조회 주기는 60분이며 30~1440분으로 변경할 수 있습니다.

## 인증과 오류 `4002`

액세스 토큰은 메모리에만 유지되며 만료 전에 갱신됩니다. 새 리프레시 토큰이
발급되면 즉시 저장합니다.

- **토큰 엔드포인트**의 `4002`는 인증 또는 갱신 자격 증명이 더 이상 허용되지
  않아 재인증이 필요하다는 뜻입니다.
- **차량 데이터 엔드포인트**의 `4002`는 차량 요청이 잘못되었다는 뜻이며 OAuth
  자격 증명 만료를 의미하지는 않습니다.
- 강제 토큰 갱신 후에도 차량 요청이 인증 실패하면 Home Assistant 재인증을
  시작합니다.

Client ID, Client Secret 또는 Redirect URI는 **재구성**에서 바꿀 수 있습니다.
브랜드는 바꿀 수 없으므로 다른 브랜드는 별도 계정으로 추가하세요.

## Pyscript에서 이전

회전되는 리프레시 토큰을 두 클라이언트가 동시에 사용하지 않도록 새 통합
구성요소를 인증하기 전에 기존 현대/기아 Pyscript를 비활성화하세요. 엔티티 매핑,
Recorder 보존 기간 및 기존 이력을 수정하지 않는 Grafana/InfluxDB 쿼리는
[Pyscript 이전 및 이력 안내](docs/pyscript-migration.ko.md)를 참고하세요.

## 지원 및 개발

문제를 등록하기 전에 [SECURITY.md](SECURITY.md)를 읽고 GitHub 이슈 양식을
사용하세요. 자격 증명, OAuth 리디렉션 코드, 리프레시 토큰 또는 차량 ID를 절대
게시하지 마세요. 기여 방법은 [CONTRIBUTING.md](CONTRIBUTING.md)에 있습니다.

## 라이선스

MIT
