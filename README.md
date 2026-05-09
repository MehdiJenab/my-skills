# my-skills

A small, growing collection of [Claude Code](https://claude.com/claude-code) **skills** that I use day-to-day and have polished enough to share. Each skill is a self-contained folder with a `SKILL.md` (and optional `references/` for templates and supporting material) that Claude loads on demand.

I keep this repo public so others can use these skills directly, fork and adapt them, or open issues / PRs to improve them.

## Skills in this repo

| Skill | What it does |
|---|---|
| [`teach-me/`](./teach-me) | Interactive teaching skill for papers and technical topics. Plans a curriculum, teaches in small chunks with structured visuals, tracks side-threads, accumulates LaTeX notes, and produces a final PDF. Two modes: **topic mode** (name a subject) and **paper mode** (upload a PDF). |
| [`python-project-setup/`](./python-project-setup) | Step-by-step bootstrap of a modern Python project: src-layout, `pyproject.toml`, ruff + mypy + pytest with **100% coverage enforced**, pre-commit hooks, Makefile, `noxfile.py` for multi-version testing, and per-project `.claude/`. Ships with ready-to-copy templates. |
| [`cpp-project-setup/`](./cpp-project-setup) | Step-by-step bootstrap of a modern **C++23** project: CMake + presets, `clang-format`, `clang-tidy`, sanitizers (ASan/UBSan/TSan), unit tests via **Catch2 or GoogleTest** (skill asks the user), optional **vcpkg or Conan**, gcovr coverage with 100% line-floor, pre-commit hooks, and per-project `.claude/`. |
| [`spec-driven-development/`](./spec-driven-development) | SDD workflow for building software with AI coding agents using specifications as the primary versioned artifact. Defines a spatial axis (constitution + theory + per-feature specs colocated with code) and a temporal axis (bootstrap → environment setup → feature loop). |
| [`build-skill/`](./build-skill) | Guide for writing high-quality Claude Code skills. Covers SKILL.md anatomy, Monigatti's 6-element description framework (core purpose / trigger / action / limitations / relationships / examples), the Iron Law + lightweight test protocol, common pitfalls, and a ready-to-copy template. |

More skills will be added here over time as I clean them up for general use.

## Installing a skill

Claude Code loads skills from `~/.claude/skills/`. To install one of these skills, drop the skill's folder into that directory.

### Option 1 — clone and symlink (recommended)

This way you get updates with a `git pull`:

```bash
git clone https://github.com/MehdiJenab/my-skills.git ~/src/my-skills

# symlink whichever skills you want
ln -s ~/src/my-skills/teach-me                 ~/.claude/skills/teach-me
ln -s ~/src/my-skills/python-project-setup     ~/.claude/skills/python-project-setup
ln -s ~/src/my-skills/cpp-project-setup        ~/.claude/skills/cpp-project-setup
ln -s ~/src/my-skills/spec-driven-development  ~/.claude/skills/spec-driven-development
```

### Option 2 — copy the folder

```bash
git clone https://github.com/MehdiJenab/my-skills.git /tmp/my-skills
cp -r /tmp/my-skills/<skill-name> ~/.claude/skills/
```

### Verify

Start a new Claude Code session and check that the skill is listed:

```
/skills
```

You should see the skill name and its trigger description.

## Using a skill

Each skill defines its own trigger phrases in its `SKILL.md` description. Examples:

- `teach-me` triggers on *"teach me X"*, *"walk me through this paper"*, or `/teach_me`
- `python-project-setup` triggers on *"start a new Python project"*, *"set up Python tooling"*, *"enforce TDD in Python"*
- `cpp-project-setup` triggers on *"start a new C++ project"*, *"set up modern C++ tooling"*, *"configure clang-format / clang-tidy / sanitizers"*
- `spec-driven-development` triggers on *"spec-driven development"*, *"SDD"*, *"specs-first"*, or asks about ADRs / constitution / feature specs
- `build-skill` triggers on *"I want to write a skill"*, *"how do I create a Claude Code skill"*, *"my skill isn't triggering reliably"*, or *"how should I structure my SKILL.md"*

See each skill's `SKILL.md` for full trigger phrases and the workflow it implements.

## Contributing

Issues and PRs are welcome — improvements to existing skills, bug fixes, better examples, or clearer instructions. If you build a derivative skill that diverges significantly, please fork rather than send a PR; these skills reflect a particular pedagogical and stylistic taste that I want to keep coherent.

## License

[MIT](./LICENSE) — use, modify, and redistribute freely.
