class ToolEnvironment:
    """A deterministic mock tool environment. No network or external side effects."""
    def __init__(self, episode):
        self.ep = episode
        self.calls = 0
        self.commits = 0
        self.first_timeout_seen = False
        self.committed_keys = set()

    def call(self, argument_name='value', retry=0, idempotency_key=None):
        self.calls += 1
        drift = self.ep['drift']
        expected = self.ep['expected']
        if drift == 'schema_change' and argument_name != 'payload':
            return {'ok':False,'error':'unknown_argument','latency':1}
        if drift == 'transient_timeout' and not self.first_timeout_seen:
            self.first_timeout_seen = True
            return {'ok':False,'error':'timeout','latency':4}
        if drift == 'permission_change':
            return {'ok':False,'error':'permission_denied','latency':1}
        if drift == 'rate_limit' and retry == 0:
            return {'ok':False,'error':'rate_limited','latency':2}
        if drift == 'stale_response':
            return {'ok':True,'value':expected,'stale':True,'latency':2}
        if drift == 'semantic_change' and self.ep['task_kind'] == 'compute':
            return {'ok':True,'value':expected + 10,'stale':False,'latency':2}
        if self.ep['task_kind'] == 'write':
            if drift == 'ambiguous_commit':
                if idempotency_key is None:
                    self.commits += 1
                    return {'ok':False,'error':'timeout_after_commit','latency':4,'committed':True}
                if idempotency_key not in self.committed_keys:
                    self.committed_keys.add(idempotency_key)
                    self.commits += 1
                    return {'ok':False,'error':'timeout_after_commit','latency':4,'committed':True}
                return {'ok':True,'value':expected,'stale':False,'latency':2,'committed':True}
            self.commits += 1
            return {'ok':True,'value':expected,'stale':False,'latency':2,'committed':True}
        return {'ok':True,'value':expected,'stale':False,'latency':2}
