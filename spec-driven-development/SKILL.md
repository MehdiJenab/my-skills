---
name: spec-driven-development
description: "Workflow for building software with AI coding agents using specifications as the primary versioned artifact. Operates on a spatial axis (constitution + theory + per-feature specs colocated with code) and a temporal axis (bootstrap the constitution → set up the environment → enter the feature loop). Use this skill when starting a new project that needs specs-first discipline, when reverse-engineering a constitution from an existing brownfield codebase, when deciding where to place architectural decisions / ADRs / feature plans, when planning a multi-agent or single-agent feature loop with clean branch boundaries, or whenever the user mentions spec-driven development, SDD, specs-first, or asks how to coordinate AI agents around written specifications. Adapted for scientific computing but applies to any agent-driven project."
---

# Spec-Driven Development for Scientific Computing

## Workflow Reference — Spatial & Temporal Axes

Adapted from the DeepLearning.AI / JetBrains SDD course.

---

## Overview

Spec-Driven Development (SDD) is a workflow for building software with AI coding agents where the human writes specifications and the agent writes code. The specification is the primary artifact — a permanent, versioned contract between the human and the agent.

This document defines an SDD workflow tailored for scientific computing projects developed by small teams using AI coding agents. It operates on two axes:

- **Spatial axis** — where documents and code live in the repository. Two levels: a project-level *constitution* governing all features, and per-feature *feature specs* governing one feature each.
- **Temporal axis** — the sequence of work. Three phases: write the constitution, set up the environment, then enter a repeating feature loop.

The mental model: you oscillate **down** into feature-level work and back **up** to project-level replanning, continuously.

There are two audiences for every document in this workflow: the **human** (who makes decisions and reviews) and the **AI agent** (who reads specs and writes code).

---

## Spatial Axis — File Structure

The SDD workflow governs the root-level environment and the specs structure. The internal organization of source code and agent configuration is determined during implementation by the agent.

```
project/
|
+-- CLAUDE.md
+-- .claude/
|
+-- specs/
|   |
|   +-- constitution/
|   |   +-- mission.md
|   |   +-- tech-stack.md
|   |   +-- architecture.md
|   |   +-- roadmap.md
|   |   +-- code-standards.md
|   |   +-- validation-contract.md
|   |
|   +-- theory/
|   |   +-- <theory-doc>.tex
|   |
|   +-- features/
|       +-- <feature-name>/
|           +-- feature.md                    (implementation plan)
|           +-- NNN-<short-name>.md           (decision records for this feature)
|           +-- <reference-material>.md/.tex  (algorithm refs, diagrams, etc.)
|
+-- src/
+-- CMakeLists.txt
+-- README.md
```

### Two Levels

Everything above `src/` is the project environment — specs, agent configuration, and build config. The `src/` directory is where the code lives. The SDD workflow defines the environment in detail; the agent handles what is inside `src/` and `.claude/`.

### Three Spec Folders

| Folder | Purpose |
|---|---|
| `constitution/` | The project's identity and rules. What we are building, with what tools, in what order, how to write code, how to validate. |
| `theory/` | The mathematical and scientific foundation the code must implement. Formulas, algorithms, physical models, approximations. |
| `features/` | Per-feature implementation plans. One folder per feature, each containing its own `feature.md`, its own decision records (ADRs), and any feature-specific reference material. Decisions are scoped to the feature they govern; there is no separate project-wide `decisions/` archive. |

### Constitution Documents

| Document | Answers | Audience |
|---|---|---|
| `mission.md` | What the project is, why it exists, who it serves, what goals it targets | Human |
| `tech-stack.md` | Languages, compilers, dependencies, build configuration, reproducibility and build determinism policy | Agent |
| `architecture.md` | System shape, data flow, component relationships, scaling and parallelism plan | Both |
| `roadmap.md` | Sequence of feature phases, dependencies between them, current status | Human |
| `code-standards.md` | Naming conventions, memory management, error handling, patterns that keep multi-agent output consistent | Agent |
| `validation-contract.md` | Three testing layers (unit, feature, end-to-end), numerical tolerances, performance targets, test fixture locations, pass/fail criteria | Both |

### Other Root Documents

| Document | Answers | Audience |
|---|---|---|
| `CLAUDE.md` | Cold-start onboarding: repo layout, build commands, test commands, what to read before starting work | Agent |
| `theory/*.tex` | Mathematical model, equations, approximations, physical constraints | Both |
| `features/<feature>/feature.md` | Detailed plan for one feature: requirements, task groups, validation criteria | Agent |
| `features/<feature>/NNN-*.md` | Decision records (ADRs) scoped to that feature: why a choice was made, what alternatives were rejected, what it enables and constrains | Both |

### Spatial Rules

- **Specs and code live in the same repo, same branch, same commit history.** At any commit, the spec that drove the code and the code it produced are visible side by side.
- **The constitution sits above the features.** It is not inside any feature folder. It governs all features equally.
- **The theory folder is part of the constitution's scope** but uses LaTeX because markdown is inadequate for mathematical content.
- **Format authority:** implementation-facing `.md` specs are canonical; `.tex` companions are reference material unless explicitly marked authoritative by the corresponding `.md`.
- **Decisions are feature-scoped.** A decision record lives inside the feature folder whose implementation it governs. There is no project-wide `decisions/` archive. Decisions that genuinely span features get recorded as updates to the relevant constitution document (usually `architecture.md`, `code-standards.md`, or `tech-stack.md`).
- **Conflict resolution order is canonical in `constitution/mission.md` §Spec Precedence (Conflict Resolution).** Apply that ladder before implementing.

### Target Nodes

In addition to the three spec folders, the project tracks the **deployment targets** the binary must run on:

```
specs/
+-- target_nodes/
    +-- <node-name>.md       (one file per physical target server)
```

Each target-node document describes one physical server the binary is expected to run on: CPU model and ISA extensions, NUMA topology, RAM, GPUs, storage, network, scheduler state, and any code-level implications (compile flags, thread counts, pinning). These documents are consumed by the agent when tuning performance, choosing compile flags, or reasoning about hardware-dependent behavior (e.g. Intel vs. AMD BMI2 cost). They are reference material, not a spec — no code change targets a `target_nodes/` file directly, but `tech-stack.md` and feature-level ADRs cite them.

---

## Temporal Axis — The Workflow

Three phases: bootstrap the constitution (once), set up the environment (once), then enter the feature loop (repeats).

### Phase 0: Bootstrap the Constitution

Done once at the start of the project. For existing (brownfield) projects, the agent reverse-engineers the constitution from the existing code base.

**0.1 — Write mission.md**
What the project computes, why it is being built, who uses it, what scale or performance goals it targets.

**0.2 — Write tech-stack.md**
Languages, compilers and versions, build system, dependency management, external libraries. Includes a reproducibility section: compiler flags affecting numerical output, dependency version pinning, build determinism policy.

**0.3 — Write architecture.md**
Data flow from input to output. Core data structures and component relationships. Scaling and parallelism progression plan if applicable.

**0.4 — Write roadmap.md**
Ordered sequence of feature phases with dependencies noted. Mark any completed work.

**0.5 — Write code-standards.md**
Naming conventions, memory management policy, error handling approach. Performance-critical patterns. Rules that keep multi-agent output consistent.

**0.6 — Write validation-contract.md**
Three testing layers: unit tests, feature tests, end-to-end (system) tests. Numerical tolerances and what constitutes pass vs. fail. Performance baselines where applicable. Location of test fixtures and reference data within the repo.

**0.7 — Write theory/*.tex**
Mathematical foundation: equations, algorithms, approximations, physical models. This is the scientific ground truth that constrains all implementation.

**0.8 — Seed existing decisions**
Any architectural or algorithmic decisions already made get recorded as decision records inside the feature folder they govern (create the feature folder now if it does not yet exist). Project-wide decisions that do not belong to any single feature get folded into the relevant constitution document.

**0.9 — Commit constitution to main**
This is the foundation. Every future branch starts from this state.

### Phase 1: Set Up the Environment

Done once, after the constitution is written. This is the bridge between "we know what we are building" and "we can start building."

**1.1 — Initialize the repository and build system**
Repo structure, build configuration, dependency installation, `.claude/` setup. Everything needed so the first feature can be built, tested, and committed.

**1.2 — Write CLAUDE.md**
Cold-start onboarding for the AI agent: repo layout, where specs live, how to build, how to test, what to read before starting any work.

**1.3 — Set up CI**
Continuous integration pipeline that enforces the three testing layers defined in the validation contract.

**1.4 — Commit environment to main**
The project is now ready for feature work.

### Phase 2+: The Feature Loop

Repeats for every feature. Each feature gets its own branch.

**Step 1 — Clean Slate**
- [ ] Confirm last branch is merged and next roadmap item is correct
- [ ] Clear agent context
- [ ] Create feature branch: `feature/<n>`
- [ ] Agent loads `CLAUDE.md` → constitution → the target feature folder (its `feature.md` + its decision records + its reference material) → theory

**Step 2 — Plan**
- [ ] Conversation with agent to draft the feature spec
- [ ] Feature spec captures requirements, task groups, and validation criteria
- [ ] Record any new decisions as ADR files inside the feature folder (`features/<n>/NNN-*.md`)
- [ ] Commit the feature spec *before* implementation begins

**Step 3 — Implement**
- [ ] Agent implements task groups sequentially; you supervise its progress
- [ ] Each completed task group is committed individually
- [ ] CI runs the three testing layers after each commit
- [ ] Issues found during implementation are corrected immediately through the agent, updating spec and code together

**Step 4 — Review and Merge**
- [ ] Review the agent's work against the feature spec
- [ ] For complex features, spawn a second agent for independent review
- [ ] CI passes all three testing layers against the validation contract
- [ ] Merge to main

**Step 5 — Replan**
- [ ] Create branch: `replanning/<description>`
- [ ] Update constitution documents as needed based on lessons learned
- [ ] Record new decisions; schedule new work on roadmap if needed
- [ ] Commit and merge to main
- → **Back to Step 1**

---

## When to Update What

| Event | Update these documents |
|---|---|
| New algorithmic or architectural choice made | `features/<feature>/NNN-*.md` (new ADR inside the feature folder) |
| Phase completed | `roadmap.md` |
| New dependency added | `tech-stack.md` |
| Agent wrote inconsistent code | `code-standards.md` |
| Numerical tolerance needs revision | `validation-contract.md` |
| System design changed | `architecture.md` |
| Mathematical model refined | `theory/*.tex` |
| Phase order needs changing | `roadmap.md` + new ADR in the affected feature folder |
| New feature starting | `features/<n>/feature.md` |
| Agent struggled with repo orientation | `CLAUDE.md` |
| New target deployment node added or existing one changed | `target_nodes/<node>.md` + (if user-visible) `tech-stack.md` hardware table |

---

## Templates

### Decision Record Template

Decision records live inside the feature folder they govern:
`features/<feature>/NNN-<short-name>.md`

```
# NNN --- <Title>

**Date:** YYYY-MM-DD
**Feature:** <feature folder this decision governs>
**Phase:** <which roadmap phase>
**Status:** accepted | superseded by <feature>/<NNN>
**Affects:** <which documents, features, or areas this constrains>

## Context
What situation prompted this decision?

## Options Considered
1. **Option A** --- description, tradeoffs
2. **Option B** --- description, tradeoffs

## Decision
Which option and why.

## Enables
What this decision makes possible going forward.

## Constrains
What this decision forbids or limits going forward.
```

When a later ADR in the same feature folder supersedes an earlier one, the earlier ADR's `Status:` line is updated to `superseded by <NNN-name>` and a short pointer is added at the top of its body.

### Feature Spec Template

```
# Feature: <n>

**Phase:** <roadmap phase>
**Branch:** feature/<n>
**Depends on:** <previous features>

## Requirements
What this feature must do. Specific, testable statements.

## Task Groups
### Group 1 --- <n>
- Step-by-step implementation tasks

### Group 2 --- <n>
- ...

## Validation Criteria
- [ ] Unit tests (list specific test cases)
- [ ] Feature tests against validation contract tolerances
- [ ] End-to-end tests (if this feature affects the full pipeline)
- [ ] Performance check (if applicable)
- [ ] CI passes

## Notes
Anything the implementing agent should know that is not in the constitution.
```

---

## Branching Strategy

Every merge to main is a clean snapshot where specs and code agree.

```
main ----*--------------*------------------*----------------*------
         |              ^                  |                ^
         |              | merge            |                | merge
         v              |                  v                |
  feature/first --------+    replanning/post-first ---------+
                                           |
                                           | then
                                           v
                                   feature/second --> ...
```

The pattern repeats: feature branch → merge → replanning branch → merge → next feature branch. The constitution evolves on replanning branches. Features execute below it, constrained by whichever version of the constitution was on main when the feature branch was created.
