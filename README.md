# Agent Skills

本仓库存放 Codex/agent skills。每个 skill 都应放在 `skills/<skill-name>/` 下，并以 `SKILL.md` 作为入口；脚本、数据池、参考资料等资源随 skill 自包含维护。

## 当前 Skill

- `xiuzhen-art-generator`：修真/仙侠设定生成器。用于随机或按条件生成受控提示词，并据此创作法术、功法、秘籍、法宝、神通、百艺、剑法、修真职业或相关体系。

该 skill 的核心模型是：

```text
法门 = 天位(动力/力量来源) x 地位(媒介/承载方式) x 人位(目的/作用)
```

## 目录结构

```text
.
├── AGENTS.md
├── README.md
├── docs/
│   └── 修真百艺.md
└── skills/
    └── xiuzhen-art-generator/
        ├── SKILL.md
        ├── data/
        │   └── pools.md
        ├── references/
        │   ├── elements.md
        │   ├── naming.md
        │   └── realm-system.md
        └── scripts/
            ├── generate_prompt.py
            ├── pool_parser.py
            └── validate_pools.py
```

## 常用命令

验证 skill 包装：

```bash
python3 $CODEX_HOME/skills/.system/skill-creator/scripts/quick_validate.py skills/xiuzhen-art-generator
```

验证要素池文本：

```bash
python3 skills/xiuzhen-art-generator/scripts/validate_pools.py
```

随机生成一个提示词：

```bash
python3 skills/xiuzhen-art-generator/scripts/generate_prompt.py
```

按类型、境界或 seed 生成：

```bash
python3 skills/xiuzhen-art-generator/scripts/generate_prompt.py --type 功法 --realm 金丹
python3 skills/xiuzhen-art-generator/scripts/generate_prompt.py --seed 20260512 --type 法术
```

后续连续生成时省略重复上下文：

```bash
python3 skills/xiuzhen-art-generator/scripts/generate_prompt.py --continue --type 法术 --realm 金丹 --condition "接着上一批宗门秘传生成，偏防护和追索"
```

## 资料与数据

- `skills/xiuzhen-art-generator/SKILL.md`：skill 的主说明、触发条件、工作流和输出约定。
- `skills/xiuzhen-art-generator/data/pools.md`：生成器实际加载的权威池数据，包含范畴、要素、细分、主题偏置、条件别名、复合父级模型和剑性分支模型。
- `skills/xiuzhen-art-generator/scripts/generate_prompt.py`：提示词生成入口。
- `skills/xiuzhen-art-generator/scripts/pool_parser.py`：解析 `data/pools.md` 的结构化文本。
- `skills/xiuzhen-art-generator/scripts/validate_pools.py`：检查池数据完整性和引用有效性。
- `skills/xiuzhen-art-generator/references/`：创作参考资料，包括三位机制、境界体系和命名风格。
- `docs/修真百艺.md`：面向人阅读的背景说明。

## 维护规则

新增或调整修真要素、细分、主题偏置、条件别名、复合父级模型、剑性分支模型时，优先修改 `skills/xiuzhen-art-generator/data/pools.md`，不要把同类数据散落到脚本里。修改后运行：

```bash
python3 skills/xiuzhen-art-generator/scripts/validate_pools.py
python3 $CODEX_HOME/skills/.system/skill-creator/scripts/quick_validate.py skills/xiuzhen-art-generator
```

## 开发约定

- 非代码内容默认使用简体中文，以保持修真/仙侠语境。
- Python 脚本面向 Python 3，保持无额外依赖，必要时使用类型提示。
- 需要可复现输出时使用 `--seed`。
- 修改生成逻辑后，至少测试随机路径、受限路径和 seeded 路径。
