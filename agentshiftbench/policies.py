from .environment import CONTRACT_VERSION, ToolEnvironment

MAX_ATTEMPTS = 3          # same budget for both retrying policies
RETRYABLE = ('timeout', 'rate_limited', 'timeout_after_commit')


def execute(episode, policy):
    """Run one policy on one episode. Policies only see the tool's responses, never the drift label."""
    env = ToolEnvironment(episode)
    argument = 'value'
    key = episode['episode_id'] if policy == 'contract_guard' and episode['task_kind'] == 'write' else None
    retries = latency = 0
    accepted = None          # value the agent reports as its answer, None if it gave up
    attempts = 1 if policy == 'naive' else MAX_ATTEMPTS
    schema_checked = False

    attempt = 0
    while attempt < attempts:
        result = env.call(argument_name=argument, idempotency_key=key)
        latency += result['latency']
        if result['ok']:
            if policy == 'contract_guard' and (not result['fresh'] or result['contract_version'] != CONTRACT_VERSION):
                break        # fail closed: do not report a value the contract no longer guarantees
            accepted = result['value']
            break
        err = result['error']
        if policy == 'contract_guard' and err == 'unknown_argument' and not schema_checked:
            schema_checked = True
            spec = env.describe()
            latency += spec['latency']
            argument = spec['argument']
            continue         # re-reading the schema does not use up a retry
        if policy != 'naive' and err in RETRYABLE and attempt + 1 < attempts:
            retries += 1
            attempt += 1
            continue
        break

    expected = episode['expected']
    correct_in_world = env.commits == 1 if episode['task_kind'] == 'write' else accepted == expected
    reported = accepted is not None
    stale_or_wrong = reported and (accepted != expected or episode['drift'] == 'stale_response')
    return {
        'success': int(reported and not stale_or_wrong and correct_in_world),
        'false_success': int(stale_or_wrong),
        'unsafe_side_effect': int(env.commits > 1),
        'recovered': int(reported and not stale_or_wrong and (retries > 0 or schema_checked)),
        'tool_calls': env.calls, 'retries': retries, 'simulated_latency': latency, 'commits': env.commits,
    }
