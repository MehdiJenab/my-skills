---
name: build-skill
description: >
  Guide for writing high-quality Claude Code skills — SKILL.md anatomy, description writing
  using the 6-element framework, the Iron Law (no skill without a failing test), common
  pitfalls, and a ready-to-copy template.
  Trigger: user wants to create a new Claude Code skill, edit or improve an existing skill,
  asks "how do I write a skill", "how do I make Claude do X reliably", "how should I structure
  my SKILL.md", or wants to publish a skill. Do NOT use for general prompting advice or
  system-prompt questions that are not about Claude Code skills specifically.
  Action: explains what a skill is and its three types, walks through SKILL.md anatomy,
  teaches the 6-element description framework (core purpose / trigger / action / limitations /
  relationships / examples), covers the Iron Law + lightweight test protocol, lists common
  pitfalls with fixes, and provides a ready-to-copy SKILL.md template.
  Limitations: covers Claude Code skills only — not OpenAI functions, LangChain tools, or
  MCP servers (use the mcp-builder skill for those); does not include the full Anthropic eval
  infrastructure (grader agents, benchmark scripts, HTML viewer) — use the skill-creator skill
  if you need that; does not cover skills for Claude.ai artifacts.
  Relationships: for building MCP servers use mcp-builder; for the full eval loop with grader
  agents and benchmarks use the skill-creator skill; for spec-driven project setup that
  references skills as a tool use spec-driven-development.
  Examples: "I want to write a skill that makes Claude always run tests before committing"
  → technique skill, Iron Law applies, walk through all 7 sections;
  "how should I write the description for my skill?" → jump to Section 3 (6-element framework);
  "my skill isn't triggering reliably" → jump to Section 3 + Section 5 (pitfalls);
  "I have a workflow I keep explaining to Claude, how do I turn it into a skill?" → full walkthrough.
---

# Build Skill — Writing High-Quality Claude Code Skills

A skill is reusable process documentation that Claude loads on demand and follows precisely.
This guide synthesizes the Anthropic skill-creator workflow, the superpowers TDD discipline,
and Leonie Monigatti's 6-element description framework into one practical reference.

---

## Section 1 — What a skill is (and isn't)

### Definition

A skill is a `SKILL.md` file that Claude Code loads into its context window when it recognizes
a relevant trigger. The agent then reads and follows the skill's instructions, using the full
body as its operating procedure.

**The context window picture** (per Monigatti's agentic search talk):

```
CONTEXT WINDOW
┌──────────────────────────────┐
│ System prompt                │
│ Skills YAML frontmatter  ←── │ ← routing layer: always in context
│ Tool list                    │
│ Memory file | History        │
│ User message                 │
│ [Full skill body loaded here]│ ← loads only when triggered
└──────────────────────────────┘
```

The **YAML frontmatter** (name + description) is the routing layer — always present, used to
decide which skill to load. The **body** is loaded on demand when the trigger fires.

### Three skill types

| Type | What it encodes | Example |
|---|---|---|
| **Technique** | How to perform a task step-by-step | `build-skill`, `cpp-project-setup` |
| **Pattern** | A recurring structure or template to apply | `spec-driven-development` |
| **Reference** | A lookup table, rule set, or decision guide | `naming-convention` |

### What a skill is NOT

- A narrative essay or tutorial written for human readers
- General advice ("write clean code")
- A system prompt or user-level instruction
- A substitute for a well-named tool with a clear description

---

## Section 2 — SKILL.md anatomy

### Frontmatter

```yaml
---
name: skill-name          # kebab-case, verb-noun preferred (e.g. build-skill, not skill-building)
description: >            # YAML folded scalar — collapses to one long string for the LLM
  [6-element description — see Section 3]
---
```

**Critical constraint:** `description` must be ≤ 1024 characters. The description is the
routing signal, not the skill body. Write it for the LLM routing engine, not for humans.

**The Iron Rule of the description:** it is the triggering condition, NOT a summary of the
skill body. If you put workflow instructions in the description, the agent will follow the
description and ignore the body. Keep it to: what it does, when to invoke, when NOT to invoke,
and examples.

### Body

The body is imperative, structured, and read top-to-bottom by the agent. Use:

- **Headers** (`##`, `###`) to separate sections — the agent uses these to navigate
- **Numbered steps** for ordered procedures the agent must follow in sequence
- **Bullet lists** for unordered options, rules, or considerations
- **Tables** for comparisons, decision matrices, or reference lookups
- **Code blocks** for exact commands, templates, or syntax the agent should copy

**Avoid:** prose paragraphs that explain *why* something is done — put the why in a short
italicized note if needed, but keep the main flow imperative. The agent reads this as
instructions, not suggestions.

### File organization

| When | Structure |
|---|---|
| Simple skill with no external files | `SKILL.md` only |
| Skill with reusable templates/configs | `SKILL.md` + `templates/` |
| Skill with heavy reference material (>100 lines) | `SKILL.md` + `references/` |

Keep skills self-contained. Prefer inlining short templates in the body over adding a
`templates/` directory — fewer moving parts.

---

## Section 3 — Writing the description (6-element framework)

Derived from Leonie Monigatti's tool-description framework (Elastic, "Agentic Search for Context
Engineering", 2026). Apply all six elements in this order:

```yaml
description: >
  [1. Core purpose — one sentence: what the skill does]
  [2. Trigger — when to invoke it AND explicit NOT-trigger cases]
  [3. Action — what it does, briefly (key steps or decisions)]
  [4. Limitations — hard constraints, what it doesn't cover]
  [5. Relationships — which other skills to use instead, when to chain]
  [6. Examples — 3-4 concrete "user phrase" → "what skill does" pairs]
```

### Element-by-element guide

**1. Core purpose** — One sentence. What does the skill produce or guide? Start with a noun
phrase or a verb ("Step-by-step guide for...", "Workflow for...", "Reference for deciding...").

**2. Trigger** — Two parts:
- *When to use:* List specific phrases and contexts. Be specific enough to avoid misfires.
- *Do NOT use when:* Explicit NOT-trigger cases prevent the skill from firing on tangentially
  related prompts. If you skip this, expect false positives.

**3. Action** — Brief: what does the agent do after loading this skill? Key steps or decisions.
Enough to set expectations, not a full restatement of the body. Users reading the description
should know what they're getting into.

**4. Limitations** — Hard constraints: unsupported inputs, unsupported platforms, assumptions
about environment, what the skill explicitly leaves out.

**5. Relationships** — Which other skill should be used instead? Which skill to run first?
Which skill to chain afterward? Cross-linking makes the skill ecosystem navigable.

**6. Examples** — The highest-leverage element. Concrete `"user phrase" → what skill does`
pairs. Three to four is enough. These are few-shot signals that teach the routing engine
*how* to invoke the skill, not just *when*. Without examples, trigger accuracy degrades.

### Example: good vs. bad description

**Bad — workflow summary (agent follows this instead of body):**
```yaml
description: "When writing a skill: first plan the frontmatter, then write a failing test,
then draft the body, then run evals, then refine. Make sure to include all 6 elements."
```

**Good — triggering condition only:**
```yaml
description: >
  Guide for writing high-quality Claude Code skills.
  Trigger: user wants to create or improve a skill, asks how to write a SKILL.md, or
  wants Claude to reliably follow a repeated workflow. Do NOT use for general prompting.
  Action: walks through anatomy, description framework, Iron Law + test, pitfalls, template.
  Limitations: Claude Code skills only; no eval infrastructure included.
  Examples: "how do I write a skill?" → full walkthrough; "my skill isn't triggering" → jump to pitfalls.
```

---

## Section 4 — The Iron Law + lightweight test

### The Iron Law

> **No skill without a failing test first.**

Before writing a single line of the skill body, document what Claude does *wrong* without it.
If Claude already does the right thing unaided, the skill isn't needed.

### Lightweight test protocol (no eval infrastructure required)

**Step 1 — Write the failing test (before writing the skill)**

Document 2-3 realistic prompts that should trigger the skill. For each, describe what correct
behavior looks like.

```
TEST-01: "I want to write a skill that enforces my code review checklist"
Expected: walks through skill anatomy, asks for Iron Law test, shows template
Without skill: Claude likely improvises a SKILL.md without Iron Law discipline

TEST-02: "my skill for running tests isn't firing reliably"
Expected: jumps to description framework + pitfalls section
Without skill: Claude may suggest prompt engineering instead

TEST-03 (NOT-trigger): "how do I write a good system prompt?"
Expected: answers directly WITHOUT loading this skill
```

**Step 2 — Run WITHOUT the skill**

With the skill NOT installed, send TEST-01. Document the failure mode concretely:
what did Claude do instead? This is your baseline.

**Step 3 — Write the minimal skill that passes the test**

Write the SKILL.md. Focus on the test case first — don't over-engineer.

**Step 4 — Run WITH the skill**

Install the skill, send TEST-01 again. Does the agent now follow the skill body correctly?
Verify the behavior is what you documented in Step 1.

**Step 5 — Test the NOT-trigger**

Send TEST-03. Does the skill stay silent? If it fires on unrelated prompts, tighten the
`Do NOT use when` clause in the description.

---

## Section 5 — Common pitfalls and fixes

| Pitfall | What goes wrong | Fix |
|---|---|---|
| **Description = workflow summary** | Agent follows the description instead of loading and reading the body | Description = triggering condition only. Keep workflow in the body. |
| **No NOT-trigger clause** | Skill fires on tangentially related prompts | Add explicit "Do NOT use when..." to the description |
| **No examples in description** | Agent mis-triggers or under-triggers | Add 3-4 `"phrase" → behavior` examples |
| **Skill covers too many topics** | Agent gets confused about when to stop, mixes unrelated guidance | One clear purpose per skill. Split broad skills into focused ones. |
| **Narrative prose in body** | Agent reads instructions as suggestions, skips steps | Use imperative numbered steps. Replace "you should" with "do". |
| **No Iron Law test** | Skill duplicates what Claude already does correctly, or misses the real failure mode | Always document what Claude does wrong WITHOUT the skill first |
| **Skill too long (>500 words)** | Agent skips to the end, misses middle steps | Split into type-specific sections. Lead with the most frequently needed content. |
| **Instructions in passive voice** | Agent hedges ("I might want to...") | Use active imperatives: "Ask the user...", "Create the file...", "Run the test..." |

---

## Section 6 — Template

Copy and fill in the placeholders:

```markdown
---
name: your-skill-name
description: >
  [Core purpose — one sentence: what this skill does.]
  Trigger: [phrases that should fire this skill]. Do NOT use [explicit NOT-trigger cases].
  Action: [what the agent does after loading — key steps or decisions, briefly].
  Limitations: [hard constraints: platforms, versions, out-of-scope topics].
  Relationships: [which other skill to use instead or chain with].
  Examples: "[user phrase]" → [behavior]; "[user phrase]" → [behavior];
  "[not-trigger phrase]" → answered directly without this skill.
---

# Skill Title — Short Description

One sentence: what this skill produces and why it matters.

---

## When to use this skill

- Specific situation A
- Specific situation B
- Do NOT use when: [explicit exclusion]

---

## Step 1 — [First major step]

[Imperative instructions. Numbered if ordered, bulleted if unordered.]

---

## Step 2 — [Second major step]

[...]

---

## Quick reference

| Concept | Rule |
|---|---|
| [Key term] | [Concise rule] |
```

---

## Section 7 — Adding a skill to my-skills

1. **Create the folder:**
   ```bash
   mkdir -p my-skills/<skill-name>
   ```

2. **Write `SKILL.md`** using the template above. Run the Iron Law test before finalizing.

3. **Audit for personal info** before committing:
   ```bash
   grep -rniE "your-name|your-employer|your-email|/home/your-user" <skill-name>/
   ```

4. **Commit:**
   ```bash
   git add <skill-name>/
   git commit -m "Add <skill-name> skill: [one-line description of what it does]"
   git push
   ```

5. **Symlink for local use:**
   ```bash
   ln -s /path/to/my-skills/<skill-name> ~/.claude/skills/<skill-name>
   ```

6. **Update README.md** — add a row to the skills table with name, link, and one-line description.

7. **Restart Claude Code** to pick up the new skill in the routing layer.
