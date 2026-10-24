# human-approval-gate

Agents plan alone, act only after a person says yes, and record every step in a hash-chained audit log that shows any tampering.

**This is a scripted demo that represents the process** I run in my own agent framework. It is not a sample or excerpt of that system, and none of its code or data is in it.

- Live page: https://demos.obviouslogic.ai/human-approval-gate/
- Source: https://github.com/obviouslogic-ai/human-approval-gate

## Why I built this

An agent that plans well still gets things wrong some of the time, and the expensive mistakes are the writes: a deleted folder, an email to the wrong list, a payment run twice. In my own framework an agent can plan on its own, but any step that changes the world waits for a person, and every decision goes into a hash-chained log that shows any later edit. This repo acts that rule out in about 100 lines of standard-library Python.

## The cost, without and with the gate

The page has an illustrative cost model. Every number is an input you can change; none are measured or cited figures.

- Without a gate: runs a month x share of runs with a bad write x cost to undo one.
- With the gate: runs x review minutes x hourly rate, plus the bad writes the reviewer misses (runs x bad share x (1 - catch rate) x cost to undo).
- Defaults: 60 runs, 3% bad, $2,000 to undo, 2 minutes a review, $90 an hour, 90% caught. That gives $3,600 a month without the gate and $540 with it.

## Run the CLI

```sh
python3 gate.py "read report, summarize it, file summary"   # asks y/n, writes audit.log, then verifies the chain
```

Standard library only, no installs.

## Run the page locally

```sh
cd web && ./get-pyodide.sh && cd ..   # once: downloads Pyodide 0.27.7 into web/vendor (gitignored)
python3 -m http.server 8000   # from the folder that holds this repo
# open http://localhost:8000/human-approval-gate/web/
```

The page fits one screen. Pick a task and press **Submit the plan**. The agent plans, `risk()` tags each step as read or write, and the same plan runs in two lanes. Without a gate the flawed write just runs. With the gate the run pauses for **Reject the plan** or **Approve anyway**. Every step lands in the SHA-256 audit log. Tap any entry to tamper with it and `verify()` shows where the chain breaks. Press **Replay** to run it again. The explanation sits behind **About this demo** in the corner. Add `?fast=1` to skip the pauses.

The page runs this repo's real Python in the browser through Pyodide, so what you click is the same code the tests cover. Styling comes from `web/kit/`, shared across all five demos.

## Tests

```sh
python3 -m unittest -v
```

## License

MIT
