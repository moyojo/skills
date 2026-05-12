# Agent Skills

This repository contains GitHub/agent skills. Each skill is a self-contained directory under `skills/` with a required `SKILL.md` and optional bundled resources.

## Skills

- `xiuzhen-art-generator`: Randomly or conditionally generates a controlled prompt for creating a xiuzhen spell, cultivation method, manual, or magic treasure.

## Layout

```text
skills/
└── xiuzhen-art-generator/
    ├── SKILL.md
    ├── agents/openai.yaml
    ├── references/
    └── scripts/
```

Validate a skill with:

```bash
python3 $CODEX_HOME/skills/.system/skill-creator/scripts/quick_validate.py skills/xiuzhen-art-generator
```

