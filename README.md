# human-approval-gate

Agents plan alone, act only after a person says yes, and record every step in a hash-chained audit log that shows any tampering.

**This is a scripted demo.** It represents the governance process I use in Palladium, my own agent framework. It is not a sample or excerpt of that system, and no Palladium code or data is in it.

- Live page: https://demos.obviouslogic.ai/human-approval-gate/
- Source: https://github.com/obviouslogic-ai/human-approval-gate

## How it fits Palladium governance

In Palladium, an agent can plan on its own, but anything that changes the world waits for my approval, and every decision is logged so it can be checked later. This repo acts that rule out in about 100 lines of standard-library Python.

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

The page fits one screen. Press **Submit the plan**: the agent plans, then waits for you to **Approve** or **Reject**. The steps run (or don't), the log fills in, then the page edits entry 1 and `verify()` turns red. Press **Replay** to run it again. The explanation sits behind **About this demo** in the corner. Add `?fast=1` to skip the pauses.

The page runs this repo's real Python in the browser through Pyodide, so what you click is the same code the tests cover. Styling comes from `web/kit/`, shared across all five demos.

## Tests

```sh
python3 -m unittest -v
```

## License

MIT
