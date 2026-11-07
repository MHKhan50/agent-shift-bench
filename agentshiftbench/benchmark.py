import random

DRIFTS = ['stable', 'schema_change', 'semantic_change', 'stale_response',
          'transient_timeout', 'ambiguous_commit', 'permission_change', 'rate_limit']
POLICIES = ['naive', 'retry_only', 'contract_guard']
TASKS = [
    {'task_id':'read_balance','kind':'read','expected':100,'tool':'get_balance'},
    {'task_id':'convert_units','kind':'compute','expected':2500,'tool':'convert_units'},
    {'task_id':'create_ticket','kind':'write','expected':'created_once','tool':'create_ticket'},
    {'task_id':'check_stock','kind':'read','expected':12,'tool':'get_stock'},
    {'task_id':'calculate_total','kind':'compute','expected':119,'tool':'calculate_total'},
    {'task_id':'send_notice','kind':'write','expected':'sent_once','tool':'send_notice'},
]

def generate_episode(seed, index):
    rng = random.Random((seed * 1000003) + index)
    task = dict(TASKS[rng.randrange(len(TASKS))])
    drift = DRIFTS[rng.randrange(len(DRIFTS))]
    return {'episode_id':'s{}-e{}'.format(seed,index), 'seed':seed,
            'task_id':task['task_id'], 'task_kind':task['kind'],
            'tool':task['tool'], 'expected':task['expected'], 'drift':drift}
