# Experimental Protocol — v0.1.0

## Objective
Measure the effect of post-integration tool/environment drift on task completion, false success, and side-effect safety; compare three transparent runtime policies.

## Research questions
- RQ1: How much does each drift condition reduce task success for each policy?
- RQ2: Does `contract_guard` reduce false-success and duplicate-side-effect rates relative to `naive` and `retry_only`?
- RQ3: What is the overhead in calls, retries, and simulated latency?

## Design
Each generated episode selects one of six task templates and one of eight drift conditions. Every episode is evaluated by all three policies, yielding paired comparisons. Tasks are synthetic and deterministic under each seed. Default seeds: 17, 29, 43, 71, 101. Recommended primary run: 1,000 episodes per seed. With five seeds and three policies this produces 15,000 policy evaluations. The current generator samples one drift per episode, so drift groups are not exactly balanced; report actual group counts and add a balanced-stratified generator before making fine-grained comparative claims.

## Policies
- `naive`: single attempt; no contract adaptation or response validation.
- `retry_only`: bounded retry for timeout/rate-limit-like errors; no semantic/staleness verification or idempotency key.
- `contract_guard`: adapts the known schema alias in the schema-change scenario, rejects stale/semantically inconsistent outputs, uses a stable idempotency key for writes, retries transient failures, and fails closed on permission errors.

## Outcomes
- Success rate: fraction of episodes with expected value/state achieved.
- False-success rate: fraction where the agent reports success despite invalid, stale, or ambiguous completion.
- Unsafe side-effect rate: fraction with more than one write commit.
- Recovery rate: fraction successfully completed after a retry.
- Tool calls, retries, simulated latency: efficiency proxies.

## Analysis plan
Report per-drift and per-policy rates. Use paired episode-level comparisons and bootstrap confidence intervals in a later analysis release. Do not aggregate drift conditions without also showing stratified results. Report all seeds and disclose any exclusions.

## Validity and limitations
The benchmark uses a small hand-authored simulator and deterministic policies. It does not measure LLM reasoning, actual API compatibility, real latency, or production risk. Semantic drift is represented by a controlled numeric discrepancy, and idempotency is idealized. These simplifications must be expanded and independently reviewed before peer-reviewed submission.
