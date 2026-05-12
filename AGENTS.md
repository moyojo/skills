# Repository Guidelines

## Project Structure & Module Organization

This repository stores Codex/agent skills. Each skill lives under `skills/<skill-name>/` and should be self-contained.

- `skills/xiuzhen-art-generator/SKILL.md`: main skill instructions and workflow.
- `skills/xiuzhen-art-generator/scripts/`: executable helper scripts, currently `generate_prompt.py`.
- `skills/xiuzhen-art-generator/references/`: supporting reference material loaded only when needed.
- `skills/xiuzhen-art-generator/agents/`: agent configuration, such as `openai.yaml`.
- `docs/`: human-facing background documentation.
- `evals/`: evaluation assets or future test cases.

## Build, Test, and Development Commands

There is no build step for this repository. Validate and exercise skills directly:

```bash
python3 $CODEX_HOME/skills/.system/skill-creator/scripts/quick_validate.py skills/xiuzhen-art-generator
python3 skills/xiuzhen-art-generator/scripts/generate_prompt.py
python3 skills/xiuzhen-art-generator/scripts/generate_prompt.py --type 功法 --realm 金丹
```

The validation command checks skill packaging. The script commands smoke-test random generation and constrained generation.

## Coding Style & Naming Conventions

Use Markdown for skill instructions and references. Keep headings descriptive, examples runnable, and instructions concise. Skill directories use kebab-case, for example `xiuzhen-art-generator`.

Python scripts should target Python 3, use 4-space indentation, type hints where practical, and avoid unnecessary dependencies. Prefer explicit CLI flags with `argparse`; keep outputs deterministic when a `--seed` option is supplied.

## Testing Guidelines

Before submitting changes, run the skill validator and at least one representative script invocation. For generator logic, test both random and constrained paths, including seeded output:

```bash
python3 skills/xiuzhen-art-generator/scripts/generate_prompt.py --seed 20260512 --type 法术
```

When adding eval fixtures, place them under `evals/` and name them after the skill or behavior being checked.

## Commit & Pull Request Guidelines

This repository currently has no commit history to infer conventions from. Use concise conventional-style commits going forward, such as `feat: add realm eval cases` or `fix: preserve seeded prompt output`.

Pull requests should include a short summary, changed skill paths, validation commands run, and sample output when generation behavior changes. Link related issues when applicable. Include screenshots only for UI or rendered documentation changes.

## Agent-Specific Instructions

Do not symlink environment-local Codex state between Windows and WSL. Use WSL Bash commands by default in this repository. Keep skill resources portable and avoid absolute paths inside skill content unless documenting a local validation command.
