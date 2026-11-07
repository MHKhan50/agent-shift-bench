# Data Dictionary

## episodes.csv

| Column | Type | Meaning |
|---|---|---|
| episode_id | string | Stable seed/episode identifier |
| seed | integer | Generator seed |
| task_id | string | Synthetic task template identifier |
| task_kind | string | read, compute, or write |
| tool | string | Mock tool name |
| expected | string/integer | Expected result or state |
| drift | string | Environment drift condition |
| policy | string | Runtime policy under evaluation |
| success | 0/1 | Expected task outcome achieved |
| false_success | 0/1 | Incorrect/stale/ambiguous outcome reported as success |
| unsafe_side_effect | 0/1 | More than one mock write commit |
| recovered | 0/1 | Successful completion after retry |
| tool_calls | integer | Number of mock tool calls |
| retries | integer | Number of retries after first attempt |
| simulated_latency | integer | Sum of abstract latency units; not wall-clock time |
| commits | integer | Number of mock write commits |

## summary.csv
One row per drift × policy group. Rates are means over the group's episodes. `mean_simulated_latency` is an abstract proxy and must not be reported as measured runtime latency.

## run_metadata.json
Records version, seed list, drift conditions, policies, Python version, evaluation count, and evidence type.
