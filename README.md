# Home Assistant용 Hyundai Kia Genesis Developers

**한국어** | [English](README.en.md)

![Hyundai Kia Genesis Developers](custom_components/hyundai_kia_developers/brand/logo.png)

대한민국 현대, 기아 및 제네시스 개발자 API에서 차량 정보를 조회하는 비공식 Home
Assistant 통합 구성요소입니다. 여러 계정과 차량을 지원하고, 본인 소유 차량을
자동으로 검색하며, 가능한 경우 인증을 자동으로 갱신합니다.

> 이 통합 구성요소는 대한민국 개발자 서비스만 지원합니다. 다른 지역의 계정,
> 프로젝트 및 차량은 호환되지 않습니다.

## 요구 사항

- Home Assistant 2026.7.0 이상
- HACS
- 대한민국 현대, 기아 또는 제네시스 개발자 회원 및 프로젝트
- 본인 Bluelink, Kia Connect 또는 Genesis Connected Services 계정에 등록된 차량

각 브랜드의 개발자 회원과 프로젝트를 별도로 만들어야 합니다. 공유받은 차량은
개발자 API에서 제공되지 않을 수 있습니다.

## HACS로 설치

1. HACS에서 **Custom repositories**를 엽니다.
2. `https://github.com/mahlernim/hyundai-kia-developers-ha`를
   **Integration** 유형으로 추가합니다.
3. **Hyundai Kia Genesis Developers**를 설치하고 Home Assistant를 재시작합니다.

## 개발자 프로젝트 준비

[한국어 개발자 프로젝트 등록 안내](docs/developer-setup.md)에 따라 프로젝트 생성,
차량 등록, URL 세 개 저장, Client ID와 Client Secret 확인을 순서대로 진행하세요.

세 브랜드 모두 다음 값을 사용합니다.

| 설정 항목 | 값 |
| --- | --- |
| 계정 API Redirect URL | `https://example.com/redirect` |
| 데이터 API Redirect URL | `https://example.com/redirect` |
| 데이터 API Callback URL | `https://example.com/callback` |

각 입력란 오른쪽의 **저장** 버튼을 따로 눌러야 합니다. 한 번만 누르면 나머지 값은
저장되지 않습니다.

## Home Assistant에 계정과 차량 추가

1. **설정 → 기기 및 서비스 → 통합 구성요소 추가**에서
   **Hyundai Kia Genesis Developers**를 선택합니다.
2. Hyundai, Kia 또는 Genesis를 선택합니다.
3. 프로젝트의 Client ID와 Client Secret을 입력합니다.
4. 인증 링크를 열고 커넥티드 카 계정으로 로그인한 뒤 접근을 승인합니다.
5. 브라우저가 `example.com`에 도착하면 주소 표시줄의 전체 URL을 복사해 Home
   Assistant에 붙여 넣습니다. 페이지가 비어 있거나 오류가 표시되어도 괜찮습니다.
6. 검색된 차량을 선택하고 이름을 확인합니다.

리디렉션 URL에는 일회용 인증 코드가 포함됩니다. 로그, 스크린샷, 메시지 또는
이슈에 공유하지 마세요.

## 엔티티

| 엔티티 | 제공 대상 | 기본 상태 |
| --- | --- | --- |
| 주행 가능 거리 | 모든 차량 | 활성화 |
| 누적 주행 거리 | 모든 차량 | 활성화 |
| EV 배터리 잔량 및 충전 상태 | EV 및 PHEV | 활성화 |
| 통합 주행 가능 거리 | API가 값을 제공하는 PHEV | 활성화 |
| 충전 케이블, 충전기 유형, 목표 충전량 및 남은 충전 시간 | EV 및 PHEV | 비활성화 |
| 연료, 타이어, 램프, 스마트키 배터리, 워셔액, 브레이크액 및 엔진오일 경고 | 차량이 제공하는 경우 | 비활성화 |

비활성화된 엔티티는 Home Assistant의 차량 장치 페이지에서 활성화할 수 있습니다.
차량 정보는 기본 60분마다 갱신되며 통합 구성요소 옵션에서 30분부터 1440분까지
변경할 수 있습니다.

## 계정과 여러 차량

계정 이름은 `Kia`, `Hyundai`, `Genesis`처럼 자동 생성됩니다. 같은 계정의 다른
본인 소유 차량은 **차량 추가**로 추가합니다. 브랜드마다 별도 계정으로 추가하세요.

## 문제 해결

- **차량이 검색되지 않음** 브랜드 계정, 커넥티드 서비스 계약, 개발자 프로젝트의
  **내차량등록** 상태를 확인하세요.
- **리디렉션 페이지에 오류가 표시됨** 정상입니다. 브라우저 주소 표시줄의 전체
  URL을 Home Assistant에 붙여 넣으세요.
- **Client ID가 등록되지 않음** 선택한 브랜드의 프로젝트에서 자격 증명을 다시
  복사하고 URL 세 개를 정확히 입력한 뒤 각 **저장** 버튼을 눌렀는지 확인하세요.
- **인증이 만료됨** Home Assistant의 재인증 안내를 따르세요. Client ID, Client
  Secret 또는 Redirect URL이 바뀐 경우에만 **재구성**을 사용하세요.
- **오류 `4002`** 인증 또는 토큰 갱신 중에는 재인증이 필요합니다. 차량 정보 갱신
  중에는 차량 요청이 잘못되었다는 뜻이며 계정 인증 만료를 의미하지는 않습니다.
- **값이 갱신되지 않음** 다음 조회 주기를 기다리거나 통합 구성요소를 다시
  불러오세요.
- **엔티티가 없음** 일부 엔티티는 차량 종류와 제조사가 제공하는 데이터에 따라
  달라집니다.

## 고지 및 라이선스

이 비영리 프로젝트는 현대자동차, 기아, 제네시스 또는 Home Assistant와 제휴하거나
이들의 승인이나 후원을 받지 않았습니다. Hyundai, Kia 및 Genesis 명칭과 관련
상표의 권리는 각 소유자에게 있으며 여기서는 API 호환성을 식별하기 위해서만
사용합니다.

[MIT License](LICENSE)에 따라 배포됩니다.
