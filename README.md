# human-approval-gate

A small demo of one rule: an AI agent may plan on its own, but it does not act until a person approves the plan, and everything it does is written to a log nobody can quietly edit.

## How it works

1. **Plan.** The agent turns a task into steps.
2. **Pause.** It shows the whole plan to a person and waits for yes or no.
3. **Act.** Only after a yes does it run the steps.
4. **Log.** Every stage is appended to `audit.log`. Each line holds the SHA-256 hash of the line before it, so changing or removing any line breaks the chain and `Log.verify()` returns `False`.

## Run it

```
python3 gate.py "read report, summarize it, file summary"
```

## Test it

```
python3 -m unittest -v
```

Python 3.10+, standard library only.

## Why

Human in the loop only works if the pause comes before the action and the record cannot be rewritten afterward. This demo keeps both in about 80 lines.

## Demo

Terminal recording: `demo.cast` (play with `asciinema play demo.cast`).
