import csv, json, os, platform
from collections import defaultdict
from .benchmark import generate_episode, DRIFTS, POLICIES
from .policies import execute

def run(episodes, seeds, out_dir):
    if episodes < 1 or not seeds:
        raise ValueError('episodes and seeds must be positive/non-empty')
    os.makedirs(out_dir, exist_ok=True)
    rows=[]
    for seed in seeds:
        for i in range(episodes):
            ep=generate_episode(seed,i)
            for policy in POLICIES:
                metrics=execute(ep,policy)
                rows.append(dict(ep,policy=policy,**metrics))
    fields=list(rows[0].keys())
    with open(os.path.join(out_dir,'episodes.csv'),'w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
    groups=defaultdict(list)
    for r in rows: groups[(r['drift'],r['policy'])].append(r)
    summary=[]
    for (drift,policy),items in sorted(groups.items()):
        n=len(items)
        summary.append({'drift':drift,'policy':policy,'episodes':n,
          'success_rate':round(sum(x['success'] for x in items)/n,6),
          'false_success_rate':round(sum(x['false_success'] for x in items)/n,6),
          'unsafe_side_effect_rate':round(sum(x['unsafe_side_effect'] for x in items)/n,6),
          'recovery_rate':round(sum(x['recovered'] for x in items)/n,6),
          'mean_tool_calls':round(sum(x['tool_calls'] for x in items)/n,4),
          'mean_retries':round(sum(x['retries'] for x in items)/n,4),
          'mean_simulated_latency':round(sum(x['simulated_latency'] for x in items)/n,4)})
    with open(os.path.join(out_dir,'summary.csv'),'w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(summary[0].keys())); w.writeheader(); w.writerows(summary)
    metadata={'benchmark':'AgentShiftBench','version':'0.1.0','episodes_per_seed':episodes,
      'seeds':seeds,'drift_conditions':DRIFTS,'policies':POLICIES,
      'python_version':platform.python_version(),'total_policy_evaluations':len(rows),
      'evidence_type':'synthetic deterministic simulation'}
    with open(os.path.join(out_dir,'run_metadata.json'),'w',encoding='utf-8') as f: json.dump(metadata,f,indent=2)
    print('Completed {} policy evaluations across {} seeds.'.format(len(rows),len(seeds)))
    print('Wrote episodes.csv, summary.csv, run_metadata.json to {}'.format(out_dir))
