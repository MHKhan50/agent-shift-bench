import unittest
from agentshiftbench.benchmark import generate_episode, DRIFTS, POLICIES
from agentshiftbench.policies import execute

class BenchmarkTests(unittest.TestCase):
    def test_generation_is_deterministic(self):
        self.assertEqual(generate_episode(17,3),generate_episode(17,3))
    def test_episode_fields(self):
        ep=generate_episode(29,0)
        for key in ('episode_id','seed','task_id','task_kind','tool','expected','drift'):
            self.assertIn(key,ep)
        self.assertIn(ep['drift'],DRIFTS)
    def test_policy_names(self):
        self.assertEqual(POLICIES,['naive','retry_only','contract_guard'])
    def test_all_policies_return_metrics(self):
        ep=generate_episode(43,0)
        required={'success','false_success','unsafe_side_effect','recovered','tool_calls','retries','simulated_latency','commits'}
        for policy in POLICIES:
            self.assertTrue(required.issubset(execute(ep,policy).keys()))
    def test_guard_fails_closed_on_permission_change(self):
        ep=generate_episode(1,0)
        ep.update({'task_kind':'write','expected':'created_once','drift':'permission_change'})
        result=execute(ep,'contract_guard')
        self.assertEqual(result['success'],0)
        self.assertEqual(result['commits'],0)
    def test_guard_prevents_duplicate_ambiguous_write(self):
        ep=generate_episode(1,0)
        ep.update({'task_kind':'write','expected':'created_once','drift':'ambiguous_commit'})
        guarded=execute(ep,'contract_guard')
        retry=execute(ep,'retry_only')
        self.assertEqual(guarded['success'],1)
        self.assertEqual(guarded['commits'],1)
        self.assertEqual(guarded['unsafe_side_effect'],0)
        self.assertEqual(retry['unsafe_side_effect'],1)

    def test_baseline_marks_stale_data_as_false_success(self):
        ep=generate_episode(1,0)
        ep.update({'task_kind':'read','expected':100,'drift':'stale_response'})
        result=execute(ep,'naive')
        self.assertEqual(result['false_success'],1)

    def test_guard_rejects_stale_response(self):
        ep=generate_episode(1,0)
        ep.update({'task_kind':'read','expected':100,'drift':'stale_response'})
        result=execute(ep,'contract_guard')
        self.assertEqual(result['success'],0)
        self.assertEqual(result['false_success'],0)

if __name__=='__main__': unittest.main()
