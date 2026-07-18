# Migrating from Hyundai/Kia Pyscripts

[English](pyscript-migration.md) | [한국어](pyscript-migration.ko.md)

## Before authorization

Disable the old Hyundai and Kia Pyscripts before authorizing this integration.
Both clients may try to rotate the same refresh token, leaving one of them with
an invalid credential. Do not delete the old helper entities until you have
confirmed how much history you want to retain.

## Map the entities

The exact names depend on the vehicle name selected during setup. Typical
mappings are:

| Old Pyscript helper | New integration entity |
| --- | --- |
| `input_number.kia_distance` | `sensor.<vehicle>_distance_to_empty` |
| `input_number.kia_odometer` | `sensor.<vehicle>_odometer` |
| `input_number.hyundai_distance` | `sensor.<vehicle>_distance_to_empty` |
| `input_number.hyundai_odometer` | `sensor.<vehicle>_odometer` |

Do not rename the new entity to the old helper's ID merely to join history.
Home Assistant Recorder associates data with metadata and retention rules, and
reusing an ID can make the origin ambiguous.

## Recorder limitation

Recorder only retains short-term state history for its configured
`purge_keep_days`. Once old rows are purged, changing entity IDs cannot restore
them. Long-term statistics are only created for eligible entities with suitable
state and device classes; an old `input_number` generally does not become the
new sensor's long-term statistics automatically.

Keep the old helpers disabled while their retained Recorder history is still
useful. Dashboards can display old and new entities as separate series during
that overlap.

## Grafana and InfluxDB without rewriting history

If both old and new states were exported to InfluxDB, combine the entity tags at
query time. This preserves the source data and avoids risky historical rewrites.
For an InfluxQL data source where Home Assistant stored unit-based measurements,
for example `km`:

```sql
SELECT "value"
FROM "km"
WHERE (
  "entity_id" = 'kia_distance'
  OR "entity_id" = 'niro_distance_to_empty'
)
AND $timeFilter
```

For odometer history:

```sql
SELECT "value"
FROM "km"
WHERE (
  "entity_id" = 'kia_odometer'
  OR "entity_id" = 'niro_odometer'
)
AND $timeFilter
```

Leave **GROUP BY entity_id** off when you want one continuous Grafana series,
and set a stable panel alias such as `Niro distance to empty`. If old and new
entities overlap in time, both may produce points; Grafana transformations such
as **Merge** or **Partition by values** can be used instead when you need to
inspect that overlap. Replace the example measurement and entity tags with the
values in your own InfluxDB schema.

Flux users can filter both tags similarly:

```flux
from(bucket: "homeassistant")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r.entity_id == "kia_distance" or
    r.entity_id == "niro_distance_to_empty")
```

After confirming the new integration updates reliably and the desired history
is available in Recorder or InfluxDB, remove the obsolete Pyscript automation.
