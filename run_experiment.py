#!/usr/bin/env python3
import argparse
from agentshiftbench.experiment import run

if __name__ == '__main__':
    p = argparse.ArgumentParser(description='Run AgentShiftBench synthetic experiments')
    p.add_argument('--episodes', type=int, default=1000, help='episodes per seed and drift condition')
    p.add_argument('--seeds', type=int, nargs='+', default=[17, 29, 43, 71, 101])
    p.add_argument('--out', default='results')
    args = p.parse_args()
    run(args.episodes, args.seeds, args.out)
