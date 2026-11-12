# Experimental Protocol — v0.2.0

## Objective
Measure the effect of post-integration tool/environment drift on task completion, false success, and side-effect safety; compare three transparent runtime policies.

## Research questions
- RQ1: How much does each drift condition reduce task success for each policy?
- RQ2: Does `contract_guard` reduce false-success and duplicate-side-effect rates relative to `naive` and `retry_only`?
- RQ3: What is the overhead in calls, retries, and simulated latency?

## Design
Six task templates are crossed with nine drift conditions, and episodes cycle through the 54 pairs, so every pair appears equally often. The seed sets only how many calls a transient timeout or rate limit lasts (1 to 3). Every episode is run by all three policies. Default run: seeds 17, 29, 43, 71 and 101 with 1,080 episodes each, which is 5,400 episodes and 16,200 policy evaluations.

## Policies
- `naive`: single attempt; no contract adaptation or response validation.
- `retry_only`: up to 3 attempts on timeout and rate-limit errors; no response checks and no idempotency key.
- `contract_guard`: same 3-attempt budget; on `unknown_argument` it re-reads the tool schema once; rejects responses marked not fresh or carrying a different `contract_version`; sends an idempotency key on writes; fails closed on permission errors.

No policy sees the drift label. They act only on what the tool returns.

## Outcomes
- Success rate: fraction of episodes with expected value/state achieved.
- False-success rate: fraction where the agent reports success despite invalid, stale, or ambiguous completion.
- Unsafe side-effect rate: fraction with more than one write commit.
- Recovery rate: fraction successfully completed after a retry.
- Tool calls, retries, simulated latency: efficiency proxies.

## Analysis plan
Report per-drift and per-policy rates. Use paired episode-level comparisons and bootstrap confidence intervals in a later analysis release. Do not aggregate drift conditions without also showing stratified results. Report all seeds and disclose any exclusions.

## Validity and limitations
The benchmark uses a small hand-authored simulator and deterministic policies. It does not measure LLM reasoning, actual API compatibility, real latency, or production risk. Semantic drift is a controlled numeric discrepancy, announced by a version bump in `semantic_change` and unannounced in `silent_semantic_change`, and idempotency is idealized. These simplifications must be expanded and independently reviewed before peer-reviewed submission.
