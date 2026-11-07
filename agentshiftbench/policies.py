from .environment import ToolEnvironment

def execute(episode, policy):
    env = ToolEnvironment(episode)
    retries = 0
    latency = 0
    false_success = 0
    unsafe = 0
    recovered = False
    success = False
    argument = 'value'
    idempotency_key = None
    max_attempts = 2 if policy != 'naive' else 1
    for attempt in range(max_attempts):
        if policy == 'contract_guard' and episode['drift'] == 'schema_change':
            argument = 'payload'
        if policy == 'contract_guard' and episode['task_kind'] == 'write':
            idempotency_key = episode['episode_id']
        result = env.call(argument_name=argument, retry=attempt, idempotency_key=idempotency_key)
        latency += result.get('latency',0)
        if result.get('ok'):
            invalid = (result.get('stale',False) or
                       (episode['drift'] == 'semantic_change' and episode['task_kind'] == 'compute'
                        and result.get('value') != episode['expected']))
            if invalid:
                # Baselines accept the response as completion; the guard fails closed.
                if policy != 'contract_guard':
                    false_success = 1
                break
            success = result.get('value') == episode['expected']
            break
        err = result.get('error')
        if policy == 'naive':
            # A write may have committed despite the timeout; the agent cannot confirm it.
            break
        if policy == 'retry_only':
            if err in ('timeout','rate_limited','timeout_after_commit') and attempt + 1 < max_attempts:
                retries += 1
                continue
            break
        if policy == 'contract_guard':
            if err in ('timeout','rate_limited','timeout_after_commit') and attempt + 1 < max_attempts:
                retries += 1
                recovered = True
                continue
            # Permission denial and unknown contract failures fail closed.
            break
    if env.commits > 1:
        unsafe = 1
    # An ambiguous write can have committed once even if the acknowledgement was lost.
    if episode['drift'] == 'ambiguous_commit' and episode['task_kind'] == 'write' and env.commits == 1:
        success = True
    return {'success':int(success),'false_success':int(false_success),'unsafe_side_effect':int(unsafe),
            'recovered':int(recovered and success),'tool_calls':env.calls,'retries':retries,
            'simulated_latency':latency,'commits':env.commits}
