# my-skills

A small, growing collection of [Claude Code](https://claude.com/claude-code) **skills** that I use day-to-day and have polished enough to share. Each skill is a self-contained folder with a `SKILL.md` (and optional `references/` for templates and supporting material) that Claude loads on demand.

I keep this repo public so others can use these skills directly, fork and adapt them, or open issues / PRs to improve them.

## Skills in this repo

| Skill | What it does |
|---|---|
| [`teach-me/`](./teach-me) | Interactive teaching skill for papers and technical topics. Plans a curriculum, teaches in small chunks with structured visuals, tracks side-threads, accumulates LaTeX notes, and produces a final PDF. Two modes: **topic mode** (you name a subject) and **paper mode** (you upload a PDF). |

More skills will be added here over time as I clean them up for general use.

## Installing a skill

Claude Code loads skills from `~/.claude/skills/`. To install one of these skills, drop the skill's folder into that directory.

### Option 1 — clone and symlink (recommended)

This way you get updates with a `git pull`:

```bash
git clone https://github.com/MehdiJenab/my-skills.git ~/src/my-skills
ln -s ~/src/my-skills/teach-me ~/.claude/skills/teach-me
```

### Option 2 — copy the folder

```bash
git clone https://github.com/MehdiJenab/my-skills.git /tmp/my-skills
cp -r /tmp/my-skills/teach-me ~/.claude/skills/
```

### Verify

Start a new Claude Code session and check that the skill is listed:

```
/skills
```

You should see the skill name and its trigger description.

## Using a skill

Each skill defines its own trigger phrases in its `SKILL.md` description. For example, `teach-me` triggers on phrases like *"teach me X"*, *"walk me through this paper"*, or `/teach_me`. See each skill's `SKILL.md` for details.

## Contributing

Issues and PRs are welcome — improvements to existing skills, bug fixes, better examples, or clearer instructions. If you build a derivative skill that diverges significantly, please fork rather than send a PR; these skills reflect a particular pedagogical and stylistic taste that I want to keep coherent.

## License

[MIT](./LICENSE) — use, modify, and redistribute freely.
