# Agent Skills

本仓库存放可安装到 Codex 等 coding agent 的 skills。每个 skill 都放在 `skills/<skill-name>/` 下，并以 `SKILL.md` 作为入口；脚本、数据池、参考资料等资源随 skill 自包含维护。

推荐在 `GPT-5.5` 且 reasoning effort 设为 `high` 的 Codex 会话中使用本仓库的创作型 skill。该配置更适合处理长设定、多约束、中文文化语境和命名风格一致性。

## 当前 Skill

- `xiuzhen-art-generator`：修真/仙侠设定生成器。用于随机或按条件生成受控提示词，并据此创作法术、功法、秘籍、法宝、神通、百艺、剑法、修真职业或相关体系。

该 skill 的核心模型是：

```text
法门 = 天位(动力/力量来源) x 地位(媒介/承载方式) x 人位(目的/作用)
```

## 安装

推荐使用 `skills` CLI 从 GitHub 链接安装。下面的命令会从 `https://github.com/moyojo/skills` 拉取 skill，不依赖本地仓库路径。

先查看仓库中可安装的 skills：

```bash
npx skills add https://github.com/moyojo/skills --list
```

安装到当前项目，供 Codex 在该项目内使用：

```bash
npx skills add https://github.com/moyojo/skills --skill xiuzhen-art-generator --agent codex --yes
```

安装为全局 Codex skill，供所有项目使用：

```bash
npx skills add https://github.com/moyojo/skills --skill xiuzhen-art-generator --agent codex --global --yes
```

查看已安装 skills：

```bash
npx skills list --agent codex
```

更新时重新运行同一条 GitHub 安装命令即可：

```bash
npx skills add https://github.com/moyojo/skills --skill xiuzhen-art-generator --agent codex --yes
```

如果是在本仓库内开发或调试，也可以从本地目录安装当前工作区版本：

```bash
npx skills add . --skill xiuzhen-art-generator --agent codex --yes
```

## 使用

安装后，在 Codex 中直接提出修真/仙侠设定生成需求即可触发 skill。也可以显式点名 skill：

```text
$xiuzhen-art-generator 生成一个金丹境剑法，偏追索、破障和宗门秘传风格
```

更多示例：

```text
生成三门适合筑基修士的防护法术，要求各自的天位、地位、人位不要重复
```

```text
设计一件偏因果与梦境的元婴期法宝，给出名称、来历、使用代价和克制方式
```

```text
接着上一批宗门秘传生成，偏防护和追索，不要重复上一批核心意象
```

如果只想生成结构化提示词，也可以直接运行脚本：

```bash
python3 skills/xiuzhen-art-generator/scripts/generate_prompt.py --type 功法 --realm 金丹
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
