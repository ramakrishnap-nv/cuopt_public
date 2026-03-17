---
name: cuopt-verification
version: "26.04.00"
description: Standardized verification workflow for cuOpt solutions. Use after solving any optimization problem (LP, MILP, QP, routing) to confirm correctness.
---

# cuOpt Verification

After solving, always verify the result using a consistent workflow. This skill applies to **all domains and all APIs**.

## Verification Workflow

Every solution must pass these steps in order:

1. **Status** — Did the solver finish successfully?
2. **Objective** — Is the value reasonable for the problem?
3. **Constraints** — Are all constraints satisfied?
4. **Sanity check** — Does the answer make real-world sense?

If any step fails, stop and diagnose before continuing.

---

## Domain Reference

| Domain | Good status | What to read | Key constraint checks |
|--------|-------------|------------------|-----------------------|
| **LP** | `Optimal`, `PrimalFeasible` | Objective value | Duals available if `Optimal`; check binding constraints |
| **MILP** | `Optimal`, `FeasibleFound` | Objective value + MIP gap | Integer vars are integral; check gap tolerance |
| **QP** | `Optimal`, `PrimalFeasible` | Objective value | Q matrix is PSD; objective is MINIMIZE (negate for max) |
| **Routing** | `0` (SUCCESS) | Total objective (cost/distance) | All orders served; capacity not exceeded; time windows met |

### Status gotchas

- LP/MILP/QP status uses **PascalCase** (`Optimal`, not `OPTIMAL`). Comparing against `"OPTIMAL"` silently passes without matching.
- Routing status is an **integer**: `0` = SUCCESS, `1` = FAIL, `2` = TIMEOUT, `3` = EMPTY.
- `PrimalFeasible` (LP/QP) and `FeasibleFound` (MILP) mean a solution exists but optimality is not proven — usually acceptable but note the gap.

---

## Step 1: Check Status

Use the status values from the domain reference above.

**If status is bad:**

| Status | Meaning | Action |
|--------|---------|--------|
| `PrimalInfeasible` / `Infeasible` | No feasible solution | Review constraints for conflicts; relax bounds |
| `Unbounded` / `DualInfeasible` | Objective can improve forever | Add missing bounds or constraints |
| `TimeLimit` | Solver ran out of time | Increase `time_limit`; simplify model; check for redundant constraints |
| `NumericalError` | Ill-conditioned data | Scale coefficients; check for very large/small values |
| Routing `1` (FAIL) | Infeasible routes | Retrieve error message and list of infeasible orders |

---

## Step 2: Check Objective

- Is the sign correct? (minimize vs maximize)
- Is the magnitude plausible? (e.g., total cost of $5 for 100 deliveries is suspicious)
- For MILP: check `mip_relative_gap` — a gap of 0.01 means within 1% of optimal.

---

## Step 3: Check Constraints

Spot-check a few constraints against the solution values:

- **LP/MILP/QP:** Compute the LHS of a constraint from solution values and confirm it respects the bound (allow a small tolerance, e.g. 1e-6).
- **MILP integrality:** For each integer variable, confirm the solution value is within 1e-5 of a whole number.
- **Routing capacity:** Sum demand across each vehicle's route and confirm it does not exceed that vehicle's capacity.
- **Routing time windows:** Confirm each stop's arrival time falls within its earliest/latest window.

---

## Step 4: Sanity Check

Ask: "Does this answer make sense?"

- A facility-location model that opens zero facilities is suspicious.
- A routing solution where one vehicle does all work while others sit idle may indicate missing balance constraints.
- An LP that returns all zeros may mean the objective pushes everything to lower bounds.

---

## Result Summary (mandatory)

Every solution must end with a prominent result summary:

- **Solver status** (exact value, e.g. `Optimal`)
- **Objective value** — bold or code block, never buried in a paragraph
- **What the objective represents** (e.g. "total cost", "min distance")
- **Any caveats** (e.g. "FeasibleFound with 2% gap", "PrimalFeasible — not proven optimal")

---

## CI Verification

Skill code assets are tested by `ci/test_skills_assets.sh`. Any new code assets added under `assets/` must be runnable by this script.
