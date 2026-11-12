# AgentShiftBench

What happens to a tool-using agent when the tool changes after the agent was built? An argument gets renamed, a number starts meaning something else, a write times out after it has already gone through.

This is a small simulator for that question. Six mock tools (read, compute, write) meet nine kinds of drift, and three runtime policies try to get the task done. No network, no real side effects, standard library only.

## What I found (v0.2.0)

5 seeds × 1,080 episodes, every task and drift pair equally often, 16,200 policy runs.

| Policy | Task done correctly | Wrong or stale value reported as done | Duplicate write | Tool calls per task |
|---|---|---|---|---|
| naive | 33.3% | 18.5% | 0.0% | 1.00 |
| retry_only | 48.2% | 18.5% | 3.7% | 1.41 |
| contract_guard | 63.0% | 3.7% | 0.0% | 1.63 |

- Retrying fixed timeouts and rate limits but did nothing for wrong answers, and every time a write had gone through before its reply was lost, it sent the write a second time.
- The contract guard cut wrong-but-reported answers from 18.5% to 3.7%. All of what is left is the silent semantic change: when the tool changes what a number means and nothing in the response says so, every policy reports the wrong number.
- It cost 0.22 extra tool calls per task over retrying, all of it from re-reading the schema after a rename.
- Nobody recovers from a revoked permission or stale data; the guard just declines to report instead of reporting the wrong thing.

These numbers follow from the rules in the simulator, so read them as a worked example of the mechanisms, not as rates from real systems. With 1 to 3 transient failures and 3 attempts, about two thirds of timeout and rate-limit episodes recover, which is where the remaining spread between seeds comes from.

## Drifts

| Drift | What the agent sees |
|---|---|
| stable | nothing changes |
| schema_change | old argument name returns `unknown_argument` |
| semantic_change | compute result changes and `contract_version` goes up |
| silent_semantic_change | compute result changes, response looks normal |
| stale_response | result is marked not fresh |
| transient_timeout | 1 to 3 timeouts, then normal |
| ambiguous_commit | first write goes through but the reply is a timeout |
| permission_change | `permission_denied` |
| rate_limit | 1 to 3 rate-limit errors, then normal |

## Policies

- `naive`: one call, takes whatever comes back.
- `retry_only`: up to 3 attempts on timeouts and rate limits.
- `contract_guard`: same 3 attempts, plus: re-reads the schema once on `unknown_argument`, refuses responses that are not fresh or carry a different contract version, sends an idempotency key on writes, stops on permission errors.

No policy is told which drift is active. They only see the tool's replies.

## Run it

Python 3.9 or newer, nothing to install.

```bash
python3 -m unittest discover -s tests -v
python3 run_experiment.py --episodes 1080 --seeds 17 29 43 71 101 --out results
```

This writes `results/episodes.csv`, `results/summary.csv` and `results/run_metadata.json`. The committed `results/` folder is this exact run.

## Limits

- Six hand-written mock tools and rules I chose. Real APIs drift in more ways and less cleanly.
- The guard is hand-coded, not learned, and no language model is involved.
- Latency is in abstract units, not milliseconds.
- Idempotency is ideal here: the server always recognises a repeated key.

More in `docs/`.

## Citation

See `CITATION.cff`. MIT licence.
