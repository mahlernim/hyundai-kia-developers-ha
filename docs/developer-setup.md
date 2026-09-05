# 현대, 기아 및 제네시스 개발자 프로젝트 등록 안내

**한국어** | [English](developer-setup.en.md)

현대, 기아 및 제네시스 개발자 콘솔은 동일한 프로젝트 등록 흐름과 설정 화면을
사용합니다. 연결할 브랜드마다 회원 가입과 프로젝트 생성을 각각 진행하세요.

## 시작하기 전에

- 차량의 Bluelink, Kia Connect 또는 Genesis Connected Services 계약자 계정을
  준비합니다.
- **본인 명의 차량을 가족 등에게 공유한 경우에도 차주 계정의 등록 가능한 차량
  목록에 표시되지 않습니다.** 다른 사람에게 공유받은 차량도 제외됩니다.
- 제조사 앱의 차량 공유 상태를 먼저 확인하세요. 공유를 해제하기로 했다면 해제 후
  새 인증으로 목록을 다시 확인합니다. 공유받은 사람의 앱 접근도 종료됩니다.
- Client ID, Client Secret 및 인증 코드가 포함된 URL은 공개하지 않습니다.

## 1. 개발자 콘솔에 가입하고 로그인

| 브랜드 | 공식 안내 | 프로젝트 목록 |
| --- | --- | --- |
| 현대 | [콘솔 안내](https://developers.hyundai.com/web/v1/hyundai/guide_console) | [현대 프로젝트 목록](https://console.developers.hyundai.com/web/v1/project/project_list) |
| 기아 | [콘솔 안내](https://developers.kia.com/web/v1/kia/guide_console) | [기아 프로젝트 목록](https://console.developers.kia.com/web/v1/project/project_list) |
| 제네시스 | [콘솔 안내](https://developers.genesis.com/web/v1/genesis/guide_console) | [제네시스 프로젝트 목록](https://console.developers.genesis.com/web/v1/project/project_list) |

사용할 브랜드의 개발자 서비스에 가입하고 프로젝트 목록을 엽니다.

## 2. 신규 프로젝트 생성

1. 프로젝트 목록에서 **신규프로젝트 등록**을 누릅니다.
2. 프로젝트 이름과 콘솔에서 요구하는 정보를 입력합니다.
3. 약관을 확인하고 프로젝트 생성을 완료합니다.
4. 생성된 프로젝트를 열어 상세 화면으로 이동합니다.

브랜드가 둘 이상이면 각 브랜드 콘솔에서 별도 프로젝트를 만드세요. 다른 브랜드의
Client ID와 Client Secret을 함께 사용할 수 없습니다.

## 3. 내 차량 등록

1. 프로젝트 상세 화면에서 **내차량등록**을 누릅니다.
2. 커넥티드 서비스 계약자 계정에 연결된 차량을 선택합니다.
3. 차량 등록과 필요한 약관 동의를 완료합니다.
4. 같은 프로젝트에서 차량이 **활성화** 상태인지 확인합니다. 목록에 보이는 것만으로
   활성화가 완료되었다고 판단하지 마세요.

차량이 보이지 않으면 로그인한 개발자 계정이 커넥티드 서비스 계약자 계정과
일치하는지 확인하세요. 제조사 인증 화면에서 차량이 없다고 표시되면 인증 코드를
받기 전에 진행이 막힐 수 있습니다. [단계별 문제 해결 안내](troubleshooting.md)를
확인하세요.

## 4. URL 세 개를 각각 저장

프로젝트 상세 화면에서 **설정**을 누릅니다. 아래 값을 정확히 입력하세요.

| 구역 | 항목 | 값 |
| --- | --- | --- |
| 계정 API | Redirect URL | `https://example.com/redirect` |
| 데이터 API | Redirect URL | `https://example.com/redirect` |
| 데이터 API | Callback URL | `https://example.com/callback` |

![개발자 콘솔의 URL 설정과 개별 저장 버튼](assets/developer-console-url-settings.png)

각 입력란 오른쪽에 별도의 **저장** 버튼이 있습니다. 첫 번째 값을 저장해도 두 번째와
세 번째 값은 저장되지 않습니다. 세 값을 입력한 뒤 **저장**을 총 세 번 누르세요.

다음 사항도 확인하세요.

- 대소문자와 경로를 표의 값과 동일하게 입력합니다.
- URL 끝에 `/`를 추가하지 않습니다.
- 계정 API와 데이터 API의 Redirect URL은 같은 값입니다.
- Callback URL만 `/callback`으로 끝납니다.
- 화면을 다시 열어 세 값이 모두 남아 있는지 확인합니다.

## 5. Client ID와 Client Secret 확인

1. 프로젝트 상세 화면의 **프로젝트 개요**를 누릅니다.
2. **Client ID**와 **Client Secret**을 복사합니다.
3. 비밀번호 관리자와 같은 안전한 위치에 보관합니다.

Client Secret을 GitHub 이슈, 로그 또는 스크린샷에 포함하지 마세요. 자격 증명이
노출되었다면 제조사의 자격 증명 폐기·재발급 기능이나 비공개 지원 채널을 이용한 뒤
Home Assistant에서 **재구성**으로 새 값을 입력하세요.

## 6. Home Assistant에서 인증

1. Home Assistant에서 **설정 → 기기 및 서비스 → 통합 구성요소 추가**를 엽니다.
2. **Hyundai Kia Genesis Developers**를 선택합니다.
3. 프로젝트와 같은 브랜드를 선택하고 Client ID와 Client Secret을 입력합니다.
4. 표시된 인증 링크를 열고 커넥티드 서비스 계정으로 로그인합니다.
5. 차량을 선택하고 접근에 동의합니다.
6. 등록한 리디렉션 주소로 이동하면 `code`와 `state`가 있는 전체 URL을 복사합니다.
7. 복사한 URL을 Home Assistant 입력란에 붙여 넣습니다.

`example.com`의 오류는 등록한 최종 주소에 `code`와 `state`가 모두 있는 경우에만
무시할 수 있습니다. 제조사 로그인 화면의 오류는 별도로 해결해야 합니다. URL의
일회용 인증 코드를 공유하지 마세요. Data API 동의 오류가 발생하면
[문제 해결 안내](troubleshooting.md#home-assistant에서-오류가-발생할-때)를 확인하세요.

인증을 마친 뒤 Home Assistant에서 차량을 선택하고 이름을 확인합니다. [Home Assistant 사용 안내](../README.md#home-assistant에-계정과-차량-추가)로
돌아가세요.
