# AgentShiftBench v0.1.0

**Beyond Static Benchmarks: Evaluating and Mitigating Tool-Environment Drift in Agentic AI Systems**  
Author: Muzammal Hussain | Masmatix Innovations | 7 November 2026

AgentShiftBench is a reproducible, simulation-first benchmark and reference runtime guard for studying how tool-using agents behave when their external environment changes after integration.

## Research question
When tool contracts or operating conditions drift after an agent is configured, which runtime policy best preserves task correctness while avoiding false success and unsafe/duplicate side effects?

## What v0.1.0 contains
- Deterministic synthetic task and environment generator (seeded).
- Eight drift conditions: stable, schema change, semantic change, stale response, transient timeout, ambiguous commit, permission change, and rate limit.
- Three reference policies: `naive`, `retry_only`, and `contract_guard`.
- Metrics: task success, false-success rate, unsafe/duplicate side effects, recovery rate, tool calls, retries, and simulated latency.
- CSV episode-level results, aggregate summaries, unit tests, protocol, dataset card and data dictionary.

## Important scope statement
This is a **synthetic engineering benchmark**, not evidence about the performance of commercial agents in production. The v0.1 policies are transparent rule-based reference agents, not trained neural networks. Results measure the benchmark's controlled mechanisms. Do not describe them as real-world incident rates or claim a universal solution.

## Requirements
- Python 3.9+
- Standard library only; no pip installation required.

## Quick start

```bash
python3 -m unittest discover -s tests -v
python3 run_experiment.py --episodes 1000 --seeds 17 29 43 --out results
```

Outputs:
- `results/episodes.csv`
- `results/summary.csv`
- `results/run_metadata.json`

Run a small smoke test:

```bash
python3 run_experiment.py --episodes 20 --seeds 17 --out results_smoke
```

## Reproducibility
All environment/task generation is deterministic given a seed. The run metadata records the benchmark version, seeds, episode count, Python version and policy names. Each task is evaluated under every drift condition and policy. No external API or real-world tool is invoked.

## Research workflow
1. Run tests and the smoke experiment.
2. Run the full experiment with the documented seeds.
3. Inspect `results/summary.csv` and episode-level data.
4. Repeat with additional seeds and larger episode counts before making claims.
5. Add independent reviewer scrutiny and a literature review before paper submission.

## Limitations
- The simulator abstracts real API behavior and cannot represent all forms of drift.
- The policies are hand-designed baselines; the guard is not a learned detector.
- Simulated latency is a proxy, not measured wall-clock production latency.
- The v0.1 benchmark does not include human subjects, customer data, or live systems.
- A successful synthetic result does not establish safety in a deployed system.

## Suggested paper structure
1. Introduction and motivation
2. Related work: agent reliability, runtime verification, API evolution, sim-to-real evaluation
3. Benchmark design and threat model
4. Drift taxonomy and policy definitions
5. Experimental protocol
6. Results with uncertainty intervals and ablations
7. Failure analysis
8. Limitations and deployment implications

## Citation
Muzammal Hussain (2026). *AgentShiftBench v0.1.0: Evaluating and Mitigating Tool-Environment Drift in Agentic AI Systems*. Masmatix Innovations. Software/dataset release; cite the versioned repository URL once published. Do not invent a DOI.
