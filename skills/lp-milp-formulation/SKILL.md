---
name: lp-milp-formulation
version: "26.04.00"
description: LP/MILP concepts and going from problem text to formulation. What LP/MILP are, required formulation questions, typical modeling elements, and how to parse problem statements (parameters, constraints, decisions, objective).
---

# LP/MILP Formulation

Concepts and workflow for going from a problem description to a clear formulation. No API code here.

## What is LP / MILP

- **LP**: Linear objective, linear constraints, continuous variables.
- **MILP**: Same plus some integer or binary variables (e.g. scheduling, facility location, selection).

## Required questions (problem formulation)

Ask these if not already clear:

1. **Decision variables** — What are they? Bounds?
2. **Objective** — Minimize or maximize? Linear expression in the variables?
3. **Constraints** — Linear inequalities/equalities? Names and meaning?
4. **Variable types** — All continuous (LP) or some integer/binary (MILP)?

## Typical modeling elements

- **Continuous variables** — production amounts, flow, etc.
- **Binary variables** — open/close, yes/no (e.g. facility open, item selected).
- **Linking constraints** — e.g. production only if facility open (Big-M or indicator).
- **Resource constraints** — linear cap on usage (materials, time, capacity).

---

## Problem statement parsing

When the user gives **problem text**, classify every sentence and then summarize before formulating.

**Classify every sentence** as **parameter/given**, **constraint**, **decision**, or **objective**. Watch for **implicit constraints** (e.g. committed vs optional phrasing) and **implicit objectives** (e.g. "determine the plan" + costs → minimize total cost).

**Ambiguity:** If anything is still ambiguous, ask the user or solve all plausible interpretations and report all outcomes; do not assume a single interpretation.

### 🔒 MANDATORY: When in Doubt — Ask

- If there is **any doubt** about whether a constraint or value should be included, **ask the user** and state the possible interpretations.

### 🔒 MANDATORY: Complete-Path Runs — Try All Variants

- When the user asks to **run the complete path** (e.g. end-to-end, full pipeline), run all plausible variants and **report all outcomes** so the user can choose; do not assume a single interpretation.

### Three labels

| Label | Meaning | Examples (sentence type) |
|-------|--------|---------------------------|
| **Parameter / given** | Fixed data, inputs, facts. Not chosen by the model. | "Demand is 100 units." "There are 3 factories." "Costs are $5 per unit." |
| **Constraint** | Something that must hold. May be explicit or **implicit** from phrasing. | "Capacity is 200." "All demand must be met." "At least 2 shifts must be staffed." |
| **Decision** | Something we choose or optimize. | "How much to produce." "Which facilities to open." "How many workers to hire." |
| **Objective** | What to minimize or maximize. May be **explicit** ("minimize cost") or **implicit** ("determine the plan" with costs given). | "Minimize total cost." "Determine the production plan" (with costs) → minimize total cost. |

### Implicit constraints: committed vs optional phrasing

**Committed/fixed phrasing** → treat as **parameter** or **implicit constraint** (everything mentioned is given or must happen). Not a decision.

| Phrasing | Interpretation | Why |
|----------|-----------------|-----|
| "Plans to produce X products" | **Constraint**: all X must be produced. | Commitment; production level is fixed. |
| "Operates 3 factories" | **Parameter**: all 3 are open. Not a location-selection problem. | Current state is fixed. |
| "Employs N workers" | **Parameter**: all N are employed. Not a hiring decision. | Workforce size is given. |
| "Has a capacity of C" | **Parameter** (C) + **constraint**: usage ≤ C. | Capacity is fixed. |
| "Must meet all demand" | **Constraint**: demand satisfaction. | Explicit requirement. |

**Optional/decision phrasing** → treat as **decision**.

| Phrasing | Interpretation | Why |
|----------|-----------------|-----|
| "May produce up to …" | **Decision**: how much to produce. | Optional level. |
| "Can choose to open" (factories, sites) | **Decision**: which to open. | Selection is decided. |
| "Considers hiring" | **Decision**: how many to hire. | Hiring is under consideration. |
| "Decides how much to order" | **Decision**: order quantities. | Explicit decision. |
| "Wants to minimize/maximize …" | **Objective** (drives decisions). | Goal; decisions are the levers. |

### Implicit objectives — do not miss

**If the problem asks to "determine the plan" (or similar) but does not state "minimize" or "maximize" explicitly, the objective is often implicit.** You **MUST** identify it and state it before formulating; do not build a model with no objective.

| Phrasing / context | Likely implicit objective | Why |
|-------------------|---------------------------|-----|
| "Determine the production plan" + costs given (per unit, per hour, etc.) | **Minimize total cost** (production + inspection/sales + overtime, etc.) | Plan is chosen; costs are specified → natural goal is to minimize total cost. |
| "Determine the plan" + costs and revenues given | **Maximize profit** (revenue − cost) | Both sides of the ledger → optimize profit. |
| "Try to determine the monthly production plan" + workshop hour costs, inspection/sales costs | **Minimize total cost** | All cost components are given; no revenue to maximize → minimize total cost. |

**Rule:** When the problem gives cost (or cost and revenue) data and asks to "determine", "find", or "establish" the plan, **always state the objective explicitly** (e.g. "I'm treating the objective as minimize total cost, since only costs are given."). If both cost and revenue are present, state whether you use "minimize cost" or "maximize profit". Ask the user if unclear.

### Parsing checklist

1. Split the problem text into sentences. Label each: parameter | constraint | decision | objective.
2. - [ ] **Objective is identified:** Explicit ("minimize/maximize X") or implicit ("determine the plan" + costs → minimize total cost; + revenues → maximize profit). Never formulate without stating the objective.
3. - [ ] Committed phrasing ("plans to", "operates", "employs") → not decisions.
4. - [ ] Optional phrasing ("may", "can choose", "considers") → decisions.
5. - [ ] Implicit constraints from committed phrasing are written out (e.g. "all X must be produced").
6. - [ ] **🔒 MANDATORY — Ambiguity:** Any phrase that could be read two ways → ask the user or solve all interpretations and report all outcomes.
7. - [ ] Summary is produced before formulating (parameters, constraints, decisions, **objective**).

### Example

**Text:** "The company operates 3 factories and plans to produce 500 units. It may use overtime at extra cost. Minimize total cost."

| Sentence / phrase | Label | Note |
|-------------------|-------|------|
| "Operates 3 factories" | Parameter | All 3 open; not facility selection. |
| "Plans to produce 500 units" | Constraint (implicit) | All 500 must be produced. |
| "May use overtime at extra cost" | Decision | How much overtime is a decision. |
| "Minimize total cost" | Objective | Drives decisions. |

Result: Parameters = 3 factories, 500 units target. Constraints = produce exactly 500 (implicit from "plans to produce"). Decisions = production allocation across factories, overtime amounts. Objective = minimize cost.

**Implicit-objective example:** A problem that asks to "determine the production plan" (or similar) and gives cost components (e.g. workshop, inspection, sales) but does not state "minimize" or "maximize" → **Objective is implicit: minimize total cost**. Always state it explicitly: "The objective is to minimize total cost."

---

<!-- skill-evolution:start — piecewise-linear with integer totals -->
## Piecewise-linear objectives with integer production

When modeling **concave piecewise-linear** profit/cost functions (e.g. decreasing marginal profit for bulk sales), the standard approach uses continuous segment variables with upper bounds equal to each segment's width. For a maximization with concave profit, the solver fills higher-profit segments first naturally.

**Gotcha:** If the quantity being produced is discrete (pieces, units, items), the **total production** variable must be **INTEGER**, even though segment variables can remain **CONTINUOUS**. Without this, the LP relaxation may yield a fractional total that produces a different (higher or lower) objective than the true integer optimum.

### Pattern

```
x_total  — INTEGER (total production of a product)
s1, s2, … — CONTINUOUS (amount sold in each price segment, bounded by segment width)

Link: x_total = s1 + s2 + …
Resource constraints use x_total.
Objective uses segment variables × segment profit rates.
```
<!-- skill-evolution:end -->

<!-- skill-evolution:start — cutting stock waste = total area minus useful area -->
## Cutting stock / trim loss problems

**Gotcha:** Waste includes both **trim loss** (unused width within a pattern) and **over-production** (excess beyond demand). Minimizing only trim loss ignores over-production. Instead, minimize total material consumed — since useful area is constant, this is equivalent to minimizing waste:

```
minimize  sum_j (stock_width_j × x_j)
```

where `x_j` is the amount cut using pattern `j`.
<!-- skill-evolution:end -->
## Goal programming (preemptive / lexicographic)
<!-- skill-evolution:start — goal programming section -->

Goal programming optimizes multiple objectives in priority order. Implement it as **sequential solves** — one per priority level.

### Formulation pattern

1. **Hard constraints** — capacity limits, non-negativity, etc. These hold in every phase.
2. **Goal constraints** — for each goal, introduce deviation variables (d⁻ for underachievement, d⁺ for overachievement) and write an equality: `expression + d⁻ − d⁺ = target`.
3. **Solve sequentially by priority:**
   - Phase 1: minimize (or maximize) the relevant deviation for the highest-priority goal.
   - Phase k: fix all higher-priority deviations at their optimal values, then optimize priority k's deviation.

### Variable types in goal programming

Deviation variables (d⁻, d⁺) and slack variables are always **continuous**. Decision variables must still be **INTEGER** when they represent discrete/countable quantities (units, vehicles, workers, etc.).

---

<!-- skill-evolution:start — inventory capacity must bound stock-after-purchase -->
## Multi-period inventory / purchasing models

For each period *t* with balance `stock[t] = stock[t-1] + buy[t] - sell[t]`:

- **End-of-period capacity**: `stock[t] <= capacity` — always needed.
- **After-purchase capacity**: `stock[t-1] + buy[t] <= capacity` — only needed when purchases arrive before sales within a period (sequential operations).

**Default:** Use only end-of-period capacity unless the problem explicitly states within-period sequencing. If the model already has `sell[t] <= stock[t-1]` (cannot sell what was bought this period), that prevents unbounded buy-sell cycling without needing the after-purchase constraint.
<!-- skill-evolution:end -->

<!-- skill-evolution:start — blending with shared mixing tank (intermediate processing) -->
## Blending with shared intermediate processing

When raw materials are **mixed together first** (e.g., in a shared tank) before allocation to products, the standard blending LP (`x[i][j]` per raw material per product) breaks down. The shared mixing step forces **identical proportions** in every product receiving the intermediate, creating a bilinear constraint that is not LP-representable.

### Linearization strategies

1. **Single-product allocation:** Check profitability of the intermediate in each product first. If only one product benefits, allocate all intermediate there — the proportionality constraint vanishes. This is the most common resolution.
2. **Parametric:** Fix the intermediate's quality attribute as a parameter `σ`, making it a virtual raw material. Solve the LP for a grid of `σ` values.
3. **Scenario enumeration:** For 2-3 products, enumerate allocation scenarios (all to product 1, all to product 2, split). Single-recipient cases are standard LPs; splits use strategy 2.
<!-- skill-evolution:end -->
