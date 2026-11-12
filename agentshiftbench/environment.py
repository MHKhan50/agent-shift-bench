CONTRACT_VERSION = 1


class ToolEnvironment:
    """Deterministic mock tool. No network and no real side effects.

    The agent only sees what a real API would show: an error code, a value, an
    `as_of` freshness flag and a `contract_version` field. It never sees the drift label.
    """

    def __init__(self, episode):
        self.ep = episode
        self.calls = 0
        self.commits = 0
        self.transient_left = episode.get('failures_before_recovery', 1)
        self.committed_keys = set()

    def describe(self):
        """Return the tool's current argument schema (one extra call)."""
        self.calls += 1
        arg = 'payload' if self.ep['drift'] == 'schema_change' else 'value'
        return {'argument': arg, 'latency': 1}

    def _reply(self, value, latency=2, fresh=True, version=CONTRACT_VERSION):
        return {'ok': True, 'value': value, 'fresh': fresh, 'contract_version': version, 'latency': latency}

    def call(self, argument_name='value', idempotency_key=None):
        self.calls += 1
        drift, expected, kind = self.ep['drift'], self.ep['expected'], self.ep['task_kind']

        if drift == 'schema_change' and argument_name != 'payload':
            return {'ok': False, 'error': 'unknown_argument', 'latency': 1}
        if drift == 'permission_change':
            return {'ok': False, 'error': 'permission_denied', 'latency': 1}
        if drift in ('transient_timeout', 'rate_limit') and self.transient_left > 0:
            self.transient_left -= 1
            err = 'timeout' if drift == 'transient_timeout' else 'rate_limited'
            return {'ok': False, 'error': err, 'latency': 4 if err == 'timeout' else 2}
        if drift == 'stale_response':
            return self._reply(expected, fresh=False)
        if drift == 'semantic_change' and kind == 'compute':
            # the provider changed what the number means and bumped the version
            return self._reply(expected + 10, version=CONTRACT_VERSION + 1)
        if drift == 'silent_semantic_change' and kind == 'compute':
            # same change, but nothing in the response says so
            return self._reply(expected + 10)

        if kind == 'write':
            if idempotency_key is not None and idempotency_key in self.committed_keys:
                return self._reply(expected)          # server recognises the repeat
            self.commits += 1
            if idempotency_key is not None:
                self.committed_keys.add(idempotency_key)
            if drift == 'ambiguous_commit' and self.commits == 1:
                return {'ok': False, 'error': 'timeout_after_commit', 'latency': 4}
            return self._reply(expected)
        return self._reply(expected)
