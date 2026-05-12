# Repository Guidelines

## Project Structure & Module Organization

This repository stores Codex/agent skills. Each skill lives under `skills/<skill-name>/` and should be self-contained.

- `skills/xiuzhen-art-generator/SKILL.md`: main skill instructions and workflow.
- `skills/xiuzhen-art-generator/scripts/`: executable helper scripts, currently `generate_prompt.py`.
- `skills/xiuzhen-art-generator/references/`: supporting reference material loaded only when needed.
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

## Skill 语言与文化语境

当 skill 面向中文创作、世界观构建、仙侠、修真或其他中文文化材料时，非代码内容默认使用简体中文。这包括 `SKILL.md`、参考 Markdown、agent prompt、eval 描述、评分标准和面向用户的示例。

代码标识符、CLI 参数、文件路径和机器读取的 schema key 可以保留英文以维持兼容性。不要因为项目其他部分使用英文，就把概念性说明也写成英文；中文措辞本身就是提示词语境的一部分，会引导模型进入更合适的文化和文学表达。

## Random Generation Policy

禁止小池随机/缩池随机。生成器需要随机抽取天位、地位、人位或其他核心设定要素时，默认候选集必须保持为完整大池；主题、类型、用户条件、境界或上下文只能作为权重、后处理、解释绑定、约束校验或显式强制项，不能把候选集缩成少数预设元素再随机。

例如，剑法可以自动补入 `剑` 作为道形统合标记，表示本次多天位要铸道为剑；但其他天位仍必须从完整天位池抽样，剑性六纲应在抽样后绑定解释来源。不能把“剑道主题”缩成 `分/边界/义/灭/观/感应` 之类的小池。只有用户明确指定 `--heaven`、`--earth`、`--human`、`--include`、`--exclude` 等硬约束时，才允许直接固定或排除对应元素。

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
