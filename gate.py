"""Human approval gate: an agent plans, waits for a person to approve, acts, and logs.

The log is append-only JSON lines. Each entry stores the hash of the previous
entry, so editing or deleting any line breaks the chain and `verify` catches it.
"""
import hashlib
import json
import sys
from pathlib import Path

GENESIS = "0" * 64


def _hash(entry: dict) -> str:
    body = json.dumps(entry, sort_keys=True).encode()
    return hashlib.sha256(body).hexdigest()


class Log:
    def __init__(self, path: Path):
        self.path = Path(path)

    def entries(self):
        if not self.path.exists():
            return []
        return [json.loads(line) for line in self.path.read_text().splitlines() if line]

    def append(self, event: str, **data) -> dict:
        items = self.entries()
        prev = items[-1]["hash"] if items else GENESIS
        entry = {"seq": len(items), "event": event, "data": data, "prev": prev}
        entry["hash"] = _hash(entry)
        with self.path.open("a") as f:
            f.write(json.dumps(entry, sort_keys=True) + "\n")
        return entry

    def verify(self) -> bool:
        prev = GENESIS
        for i, entry in enumerate(self.entries()):
            claimed = entry.get("hash")
            body = {k: v for k, v in entry.items() if k != "hash"}
            if entry.get("seq") != i or entry.get("prev") != prev or _hash(body) != claimed:
                return False
            prev = claimed
        return True


def plan(task: str) -> list[str]:
    """A stand-in for an agent's planner: one step per comma-separated part."""
    return [step.strip() for step in task.split(",") if step.strip()]


# A step whose first word is one of these changes the world outside the agent.
WRITE_VERBS = {"send", "email", "delete", "merge", "pay", "transfer", "publish", "deploy", "update", "cancel", "refund"}


def risk(step: str) -> str:
    """'write' if the step changes something outside the agent, else 'read'."""
    words = step.split()
    return "write" if words and words[0].lower() in WRITE_VERBS else "read"


def run(task: str, approve, act, log: Log, gated: bool = True) -> list[str]:
    """Plan, ask `approve(steps)` once, then act only if a person said yes.

    With gated=False the plan runs straight through and the log records that
    no one was asked. That mode exists only to show what the gate prevents.
    """
    steps = plan(task)
    log.append("planned", task=task, steps=steps, writes=[s for s in steps if risk(s) == "write"])
    if gated:
        approved = bool(approve(steps))
        log.append("approval", approved=approved)
        if not approved:
            log.append("stopped", reason="not approved")
            return []
    else:
        log.append("approval", approved=None, reason="no gate, nobody asked")
    results = []
    for step in steps:
        result = act(step)
        log.append("acted", step=step, result=result)
        results.append(result)
    return results


def ask_human(steps):
    print("Plan:")
    for i, step in enumerate(steps, 1):
        print(f"  {i}. {step}")
    return input("Approve? [y/N] ").strip().lower() == "y"


if __name__ == "__main__":
    log = Log(Path(sys.argv[2] if len(sys.argv) > 2 else "audit.log"))
    task = sys.argv[1] if len(sys.argv) > 1 else "read report, summarize it, file summary"
    out = run(task, ask_human, lambda s: f"done: {s}", log)
    print("\n".join(out) or "Nothing done.")
    print("log chain valid:", log.verify())
