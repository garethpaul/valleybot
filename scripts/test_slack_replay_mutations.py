#!/usr/bin/env python3
"""Mutation-sensitive contracts for Slack replay claim ownership."""
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def validate(replay_source, app_source, adapter_source):
    for contract in (
            "self._inflight = set()",
            "self._completed = OrderedDict()",
            "if signature in self._inflight or signature in self._completed:",
            "self._inflight.add(signature)",
            "def complete(self, signature):",
            "while len(self._completed) > self.max_entries:",
            "self._completed.popitem(last=False)"):
        require(contract in replay_source, "missing replay state contract")

    complete_start = replay_source.index("def complete(self, signature):")
    release_start = replay_source.index("def release(self, signature):", complete_start)
    require(
        "self._inflight.discard(signature)"
        in replay_source[complete_start:release_start],
        "completion must retire the in-flight claim",
    )

    for source in (app_source, adapter_source):
        claim = source.index("recent_slack_signatures.claim(slack_signature)")
        respond = source.index("bot.respond(command_text)", claim)
        complete = source.index(
            "recent_slack_signatures.complete(slack_signature)", respond
        )
        release = source.index(
            "recent_slack_signatures.release(slack_signature)", complete
        )
        require(claim < respond < complete < release, "invalid handler ownership order")


def replace_once(source, old, new):
    require(source.count(old) == 1, "mutation target must appear exactly once")
    return source.replace(old, new, 1)


def main():
    replay_source = (ROOT / "slack_replay.py").read_text(encoding="utf-8")
    app_source = (ROOT / "app.py").read_text(encoding="utf-8")
    adapter_source = (ROOT / "slack.py").read_text(encoding="utf-8")
    validate(replay_source, app_source, adapter_source)

    mutations = {
        "in-flight state removed": (
            replace_once(replay_source, "self._inflight = set()", "self._inflight = {}"),
            app_source,
            adapter_source,
        ),
        "claim ignores in-flight": (
            replace_once(
                replay_source,
                "if signature in self._inflight or signature in self._completed:",
                "if signature in self._completed:",
            ),
            app_source,
            adapter_source,
        ),
        "completion keeps in-flight claim": (
            replace_once(
                replay_source,
                "def complete(self, signature):\n"
                "        with self._lock:\n"
                "            self._inflight.discard(signature)",
                "def complete(self, signature):\n"
                "        with self._lock:\n"
                "            self._inflight.add(signature)",
            ),
            app_source,
            adapter_source,
        ),
        "completed bound removed": (
            replace_once(
                replay_source,
                "while len(self._completed) > self.max_entries:",
                "while False:",
            ),
            app_source,
            adapter_source,
        ),
        "Bottle completion removed": (
            replay_source,
            replace_once(
                app_source,
                "recent_slack_signatures.complete(slack_signature)",
                "recent_slack_signatures.release(slack_signature)",
            ),
            adapter_source,
        ),
        "event completion removed": (
            replay_source,
            app_source,
            replace_once(
                adapter_source,
                "recent_slack_signatures.complete(slack_signature)",
                "recent_slack_signatures.release(slack_signature)",
            ),
        ),
    }

    for label, sources in mutations.items():
        try:
            validate(*sources)
        except (AssertionError, ValueError):
            continue
        raise AssertionError("{0} mutation unexpectedly passed".format(label))

    print("Slack replay contract passed (6 mutations rejected)")


if __name__ == "__main__":
    main()
