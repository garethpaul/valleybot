from collections import OrderedDict
import threading


MAX_RECENT_SLACK_SIGNATURES = 1024


class RecentSlackSignatures(object):
    def __init__(self, max_entries=MAX_RECENT_SLACK_SIGNATURES):
        self.max_entries = max_entries
        self._signatures = OrderedDict()
        self._lock = threading.Lock()

    def claim(self, signature):
        with self._lock:
            if signature in self._signatures:
                return False
            self._signatures[signature] = None
            while len(self._signatures) > self.max_entries:
                self._signatures.popitem(last=False)
            return True

    def release(self, signature):
        with self._lock:
            self._signatures.pop(signature, None)
