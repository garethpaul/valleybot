from collections import OrderedDict
import threading


MAX_RECENT_SLACK_SIGNATURES = 1024


class RecentSlackSignatures(object):
    def __init__(self, max_entries=MAX_RECENT_SLACK_SIGNATURES):
        self.max_entries = max_entries
        self._inflight = set()
        self._completed = OrderedDict()
        self._lock = threading.Lock()

    def claim(self, signature):
        with self._lock:
            if signature in self._inflight or signature in self._completed:
                return False
            self._inflight.add(signature)
            return True

    def complete(self, signature):
        with self._lock:
            self._inflight.discard(signature)
            self._completed[signature] = None
            while len(self._completed) > self.max_entries:
                self._completed.popitem(last=False)

    def release(self, signature):
        with self._lock:
            self._inflight.discard(signature)
            self._completed.pop(signature, None)
