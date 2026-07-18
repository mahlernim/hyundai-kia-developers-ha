# 개발 프로젝트 및 첫 차량 설정

[English](developer-setup.md) | [한국어](developer-setup.ko.md)

이 안내는 대한민국 개발자 서비스를 대상으로 합니다. 다른 지역의 계정, 프로젝트
및 API 권한과 호환된다고 가정하지 마세요.

## 1. 커넥티드 카 계정 준비

인증에 사용할 Bluelink(현대) 또는 Kia Connect(기아) 계정에 차량이 등록되어
있어야 합니다. 다른 소유자가 공유한 차량은 개발자 콘솔이나 차량 목록 API에
표시되지 않을 수 있습니다.

현대와 기아 개발자 회원은 별도입니다. 두 브랜드 차량을 모두 소유했다면 이
과정을 각각 진행하고 Home Assistant에도 두 계정을 만드세요.

## 2. 가입 및 프로젝트 생성

1. 브랜드별 공식 안내를 엽니다:
   [현대 콘솔 안내](https://developers.kia.com/web/v1/hyundai/guide_console) 또는
   [기아 콘솔 안내](https://developers.kia.com/web/v1/kia/guide_console).
2. 해당 브랜드 개발자 회원에 가입하고 콘솔에 로그인합니다:
   [현대 개발자 콘솔](https://console.developers.hyundai.com) 또는
   [기아 개발자 콘솔](https://console.developers.kia.com).
3. 개발 프로젝트를 만들고 콘솔에 표시되는 API 및 약관을 확인합니다.
4. 프로젝트 개요에서 **Client ID**와 **Client Secret**을 확인해 비밀번호
   관리자에 보관합니다. 커밋, 스크린샷 또는 게시물에 포함하지 마세요.
5. 프로젝트 설정에서 **Account API Redirect URL**을 다음과 정확히 입력합니다.

   ```text
   https://example.com/redirect
   ```

   프로토콜, 호스트, 경로가 같아야 하며 끝에 `/`를 추가하지 않습니다.

## 3. 차량 활성화

개발자 콘솔의 **My Vehicle**을 열어 본인 커넥티드 카 계정 소유 차량을 선택하고
활성화합니다. 차량이 없다면 브랜드 계정, 차량 소유 관계 및 Bluelink/Kia
Connect 가입 상태를 확인하세요. 공유 차량은 정책상 제공되지 않을 수 있습니다.

## 4. Home Assistant 통합 구성요소 추가

1. 통합 구성요소를 설치하고 Home Assistant를 재시작합니다.
2. **설정 → 기기 및 서비스 → 통합 구성요소 추가**에서
   **Hyundai Kia Developers**를 검색하고 올바른 브랜드를 선택합니다.
3. Client ID, Client Secret 및 `https://example.com/redirect`를 입력합니다.
4. Home Assistant가 표시하는 인증 URL을 열고 같은 커넥티드 카 계정으로
   로그인하여 접근을 승인합니다.
5. 인증 후 `example.com`으로 이동합니다. 페이지가 오류를 표시해도 브라우저
   주소 표시줄의 `code`와 `state`를 포함한 **현재 URL 전체**를 복사해 즉시
   Home Assistant에 붙여 넣습니다.
6. 검색된 차량을 선택하고 제안된 이름을 확인하거나 수정합니다.
7. 새 장치에서 주행 가능 거리와 누적 주행 거리 값이 갱신되는지 확인합니다.
   다른 차량은 계정 메뉴의 **차량 추가**에서 추가합니다.

일회용 리디렉션 코드는 민감정보입니다. URL을 로그, 이슈, 채팅 또는 스크린샷에
남기지 마세요. 통합 구성요소는 코드를 교환하고 제출된 URL을 저장하지 않습니다.

## 범위와 이용 조건

이 통합 구성요소는 문서화된 대한민국 API와 개인 개발 용도를 대상으로 합니다.
개발자 권한이 상업 서비스 허가를 의미하지 않습니다. 상업적 또는 재배포 용도는
현재 콘솔 약관을 확인하고 해당 제조사와 협의하세요. API 제공, 할당량 및 정책은
각 제조사가 관리합니다.
