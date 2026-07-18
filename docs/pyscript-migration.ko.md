# 현대/기아 Pyscript에서 이전

[English](pyscript-migration.md) | [한국어](pyscript-migration.ko.md)

## 인증 전 준비

새 통합 구성요소를 인증하기 전에 기존 현대 및 기아 Pyscript를 비활성화하세요.
두 클라이언트가 같은 리프레시 토큰을 회전시키면 한쪽 자격 증명이 무효가 될 수
있습니다. 보존할 이력을 확인하기 전에는 기존 helper 엔티티를 삭제하지 마세요.

## 엔티티 매핑

새 엔티티 이름은 설정할 때 지정한 차량 이름에 따라 달라집니다.

| 기존 Pyscript helper | 새 통합 구성요소 엔티티 |
| --- | --- |
| `input_number.kia_distance` | `sensor.<차량>_distance_to_empty` |
| `input_number.kia_odometer` | `sensor.<차량>_odometer` |
| `input_number.hyundai_distance` | `sensor.<차량>_distance_to_empty` |
| `input_number.hyundai_odometer` | `sensor.<차량>_odometer` |

이력을 합치기 위해 새 엔티티 ID를 기존 helper ID로 바꾸는 것은 권장하지
않습니다. Recorder는 메타데이터와 보존 정책을 사용하므로 같은 ID를 재사용하면
데이터 출처가 불명확해질 수 있습니다.

## Recorder 보존 한계

Recorder의 단기 상태 이력은 설정된 `purge_keep_days` 동안만 남습니다. 삭제된
행은 엔티티 ID를 변경해도 복구되지 않습니다. 장기 통계는 올바른 상태 클래스와
장치 클래스를 가진 엔티티만 생성하며 기존 `input_number` 이력이 새 센서의 장기
통계로 자동 연결되지는 않습니다.

필요한 Recorder 이력이 남아 있는 동안 기존 helper는 비활성화 상태로 유지하고,
대시보드에서 기존/신규 엔티티를 별도 시리즈로 함께 표시할 수 있습니다.

## 이력을 수정하지 않는 Grafana/InfluxDB 연결

기존 및 신규 상태가 InfluxDB에 저장되어 있다면 저장된 데이터를 바꾸지 말고
쿼리에서 두 entity tag를 합칩니다. Home Assistant가 단위를 measurement로
저장한 InfluxQL 구성(예: `km`)의 주행 가능 거리 예시는 다음과 같습니다.

```sql
SELECT "value"
FROM "km"
WHERE (
  "entity_id" = 'kia_distance'
  OR "entity_id" = 'niro_distance_to_empty'
)
AND $timeFilter
```

누적 주행 거리는 같은 방식으로 `kia_odometer`와 `niro_odometer`를 사용합니다.
연속된 Grafana 시리즈 하나로 표시하려면 **GROUP BY entity_id**를 사용하지 않고
패널 별칭을 고정합니다. 실제 InfluxDB 스키마에 맞게 measurement와 entity tag를
바꾸세요. 두 엔티티가 같은 시간에 기록된 구간은 Grafana 변환으로 별도 확인할
수 있습니다.

Flux 예시:

```flux
from(bucket: "homeassistant")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r.entity_id == "kia_distance" or
    r.entity_id == "niro_distance_to_empty")
```

새 통합 구성요소가 안정적으로 갱신되고 필요한 이력이 Recorder 또는 InfluxDB에
남아 있음을 확인한 후 기존 Pyscript 자동화를 제거하세요.
