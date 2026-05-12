# Agent Skills

This repository contains GitHub/agent skills. Each skill is a self-contained directory under `skills/` with a required `SKILL.md` and optional bundled resources.

## Skills

- `xiuzhen-art-generator`: Randomly or conditionally generates a controlled prompt for creating a xiuzhen spell, cultivation method, manual, or magic treasure.

## Layout

```text
skills/
└── xiuzhen-art-generator/
    ├── SKILL.md
    ├── references/
    └── scripts/
```

Validate a skill with:

```bash
python3 $CODEX_HOME/skills/.system/skill-creator/scripts/quick_validate.py skills/xiuzhen-art-generator
python3 skills/xiuzhen-art-generator/scripts/validate_pools.py
```

The xiuzhen generator's element pools live in `skills/xiuzhen-art-generator/data/pools.md`.
Edit that text file for facets, elements, refinements, theme biases, condition aliases, and composite parent models.
