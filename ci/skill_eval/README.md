# cuOpt skill evaluation — OptiMind Industry-OR

Generate NV-ACES `evals.json` for cuOpt LP/MILP skills from the
[OptiMind Industry-OR dataset](https://github.com/microsoft/OptiGuide/blob/main/optimind/data/optimind_cleaned_classified_industryor.csv)
(microsoft/OptiGuide), then drive [astra-skill-eval] against those skills.

The dataset has 99 rows: `problem_class` (domain tags), `question`
(natural-language optimisation problem), `answer` (numeric optimum).

Target skills (one evals file each):

- `skills/cuopt-lp-milp-api-python/evals/evals.json`
- `skills/cuopt-lp-milp-api-cli/evals/evals.json`
- `skills/cuopt-lp-milp-api-c/evals/evals.json`

## Dependencies

- **Generating evals.json** — Python 3.9+ stdlib only. No install.
- **Running the evaluation** — `astra-skill-eval-cli` (internal NVIDIA PyPI,
  needs VPN / NVIDIA network):

  ```bash
  uv venv && source .venv/bin/activate
  uv pip install 'astra-skill-eval-cli[harbor]' \
    --index-url https://urm.nvidia.com/artifactory/api/pypi/nv-shared-pypi/simple \
    --extra-index-url https://pypi.org/simple
  ```

  `--deep` and `--agent-eval` additionally require:

  ```bash
  export NVIDIA_INFERENCE_KEY="sk-..."   # https://inference.nvidia.com/key-management
  ```

  `--agent-eval` needs Docker (Harbor backend) and — for cuOpt examples that
  exercise the solver — a GPU on the host.

## Usage

```bash
# 25-case sample for cuopt-lp-milp-api-python (defaults)
python3 ci/skill_eval/build_optimind_evals.py

# Full set (99 cases) across all three LP/MILP skills
python3 ci/skill_eval/build_optimind_evals.py --all --sample-size 0

# Only the MILP-labelled problems (51 rows) — see MILP_LABELS in the script
python3 ci/skill_eval/build_optimind_evals.py --milp-only

# Offline from a local copy of the CSV
python3 ci/skill_eval/build_optimind_evals.py \
  --source path/to/optimind_cleaned_classified_industryor.csv
```

Key flags:

| Flag | Default | Purpose |
|---|---|---|
| `--source` | GitHub raw URL | Dataset URL or local CSV path |
| `--sample-size` | `25` | `0` = all numeric-answer rows |
| `--seed` | `42` | Sampling seed (reproducible) |
| `--only <name>` | `cuopt-lp-milp-api-python` | Populate one specific skill |
| `--all` | off | Populate all three LP/MILP skills |
| `--milp-only` / `--lp-only` | off | Partition by the MILP label allowlist |

## Running the evaluator

Four NV-ACES layers, increasing cost:

```bash
# 1. Static structural checks — no API key, seconds
astra-skill-eval validate skills/cuopt-lp-milp-api-python
astra-skill-eval evaluate skills/cuopt-lp-milp-api-python --static

# 2. LLM-as-judge on the skill docs — needs NVIDIA_INFERENCE_KEY
astra-skill-eval evaluate skills/cuopt-lp-milp-api-python --deep

# 3. Live agent evaluation + Skill Lift (A/B with vs without skill)
#    needs Docker + NVIDIA_INFERENCE_KEY + claude-code in the Harbor image
astra-skill-eval evaluate skills/cuopt-lp-milp-api-python --agent-eval -a claude-code

# 4. Cross-agent comparison
astra-skill-eval evaluate skills/cuopt-lp-milp-api-python \
  --agent-eval -a claude-code,cursor-cli,mini-swe-agent,openhands
```

### Agent-eval cost (rough)

Skill Lift runs every case twice (with and without the skill). At ~2 min per
session:

| Scope | Sessions | Wall time |
|---|---|---|
| 99 × 1 skill × 1 agent | 198 | ~7 h |
| 99 × 3 skills × 1 agent | 594 | ~20 h |
| 99 × 3 skills × 4 agents | 2,376 | ~80 h |

Recommended ladder: `--static` every iteration, `--deep` per PR, `--agent-eval`
nightly/weekly on a self-hosted GPU runner.

## Configuring the agent

### Claude Code with an internal NVIDIA endpoint

Claude Code supports `ANTHROPIC_BASE_URL` + `ANTHROPIC_AUTH_TOKEN` (or
`ANTHROPIC_API_KEY`). Persist them in `~/.claude/settings.json`:

```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://<nvidia-internal-endpoint>",
    "ANTHROPIC_AUTH_TOKEN": "<nvidia-issued-token>"
  }
}
```

Local `claude` picks this up directly. **Inside a Harbor container it does
not** — the container doesn't mount `~/.claude`. To pass through, either:

1. Confirm the Harbor adapter forwards `ANTHROPIC_*` from the host (check
   `astra-skill-eval info` and the skill's `evals/environment/docker-compose.yaml`).
2. Add the env block manually to the skill's compose file:

   ```yaml
   services:
     agent:
       environment:
         ANTHROPIC_BASE_URL: ${ANTHROPIC_BASE_URL}
         ANTHROPIC_AUTH_TOKEN: ${ANTHROPIC_AUTH_TOKEN}
   ```

### Keys, clarified

- `NVIDIA_INFERENCE_KEY` — the **judge** (and the optional `-a nat` agent).
  Not what powers claude-code.
- `ANTHROPIC_API_KEY` / `ANTHROPIC_AUTH_TOKEN` — the **claude-code agent**
  being tested.

Use `-a nat` if you want a fully-NVIDIA inference path without a proxy.

## Caveats

- **LP vs MILP classification is best-effort.** OptiMind tags problems by
  domain (`Knapsack`, `Set Cover`, `Transportation Problem`), not by solver
  class. `MILP_LABELS` in the script is a hand-curated allowlist; 51 rows are
  classed MILP, 48 LP. Revise the set if you disagree.
- **Dataset is 99 rows**, not 981 (multi-line CSV fields inflate `wc -l`).
- **evals.json is not committed.** Regenerate on demand; each generation is
  deterministic under a fixed `--seed`.
- **Tolerance is advisory only.** `1e-3 relative` sits in `ground_truth` and
  `expected_behavior` for the LLM judge to enforce. There is no programmatic
  scoring. For a hard numeric check, either add `expected_script` to each
  entry or post-process judge output.
- **Script requires network access by default** (fetches GitHub raw CSV). Use
  `--source <local-path>` for offline/air-gapped runs.

## Repo layout

```
ci/skill_eval/
├── README.md                     # this file
└── build_optimind_evals.py       # generator (stdlib only)

skills/<name>/evals/evals.json    # generated, not committed
```

[astra-skill-eval]: https://urm.nvidia.com/artifactory/api/pypi/nv-shared-pypi/simple
