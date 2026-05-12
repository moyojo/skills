---
name: xiuzhen-art-generator
description: 生成修真/仙侠设定的受控随机提示词，并据此创作法术、功法、秘籍、法宝、神通、百艺、修真职业或相关体系。用户要求创建、随机生成、有限条件随机、构思、设计或优化修真法门时使用本技能。
---

# 修真百艺生成器

使用本技能生成或创作修真世界中的法术、功法、秘籍、法宝、神通、百艺或相关设定。

核心模型：

```text
法门 = 天位(动力/力量来源) x 地位(媒介/承载方式) x 人位(目的/作用)
```

## 工作流

1. 常规生成时不要由 agent 读取 `references/*.md` 或 `data/pools.md`。脚本会从这些资料中提取创作上下文，去掉维护命令、文件路径说明、维护手册和池格式手册后一次性输出。
2. 运行 `scripts/generate_prompt.py` 抽取或约束天位、地位、人位。默认随机策略是小说可用率加权；用户要求“完全随机”“强随机”“force random”或“全池随机”时使用 `--force-random`。普通创作流程使用文本输出，不用 `--json`；文本输出包含“创作上下文包 + 本次抽样提示词”，必须整体作为创作依据。
3. 用户显式指定的 `--heaven`、`--earth`、`--human`、`--name-style`、`--type`、`--realm` 是硬约束，必须保留。若强制项与境界冲突，只能写成误读、残式、低阶入口、旁门代价、局部小术或高阶传承的浅层用法。
4. 在当前上下文中直接使用生成器打印的完整提示词，产出最终设定。
5. 需要复现时，附上 seed、强制参数和自动合理化诊断。

调试、维护池子、排查抽样、扩展范畴或用户明确要求解释资料来源时，才读取参考文件：

- `data/pools.md`：脚本加载的权威池数据。
- `references/elements.md`：要素分类与三位机制说明。
- `references/realm-system.md`：境界、尺度、身份与功法等阶链说明。
- `references/naming.md`：命名文体、后缀和避坑说明。

新增或调整要素、细分、主题偏置、条件别名、复合父级模型时，优先改 `data/pools.md`，改完运行 `python3 scripts/validate_pools.py`。

## 快速开始

```bash
python3 scripts/generate_prompt.py
python3 scripts/generate_prompt.py --type 法宝
python3 scripts/generate_prompt.py --type 功法 --realm 元婴
python3 scripts/generate_prompt.py --seed 20260512 --type 法术
python3 scripts/generate_prompt.py --condition "偏医毒蛊疫，不要纯攻击" --rarity 失传
python3 scripts/generate_prompt.py --theme 魂梦心识 --type 秘籍
python3 scripts/generate_prompt.py --type 法宝 --name-style 祭文悲怆
python3 scripts/generate_prompt.py --type 剑法 --heaven 剑 --heaven 分 --heaven 灭 --composition-mode 纯化
python3 scripts/generate_prompt.py --force-random
python3 scripts/generate_prompt.py --type 秘籍 --realm 金丹 --force-random
```

约束三位：

```bash
python3 scripts/generate_prompt.py --heaven 愿 --earth 梦 --human 净化
python3 scripts/generate_prompt.py --heaven 剑 --heaven 分 --earth 形 --human 灭 --human 感应
```

## 生成原则

- 脚本输出是常规生成的唯一资料入口。不要在脚本输出之外把参考 Markdown 再输入一遍。
- 默认生成目标是小说可用率。随机项应优先落在当前境界能承担、读者能理解、剧情能使用的尺度。
- `--force-random` 只取消未指定项的可用率加权，不取消境界适配；抽到的偏门、上古或仙古要素仍必须被降尺度、补限制或合理化。
- 天位必须解释力量来源、增长方式、衰竭点、失控形态和度量方法，不能只是氛围词。
- 地位是媒介，人位是目的。默认允许多地位、多人位：至少应能同时解释效果如何生成，以及如何锁定、承载或约束目标。
- 主题、类型、境界或上下文只能改变权重、解释绑定、后处理或显式强制项，不能把开放维度缩成小池随机。
- 元婴只规定层级特色，如神魂、出窍、化身、远遁、生存、因果、洞府防护、传承或高阶威慑；具体效用由人位决定，不默认要求某个固定功能。
- 写功法时，目标境界高于练气必须说明功法等阶链：总纲、逐阶特殊之处、配套术法、递进/拆分/合一路径。
- 写剑修、剑法或以 `剑` 为道形统合时，`剑` 不消耗普通天位数量；其他天位仍从完整大池抽样。剑修默认比同境界普通修士更强势，强势体现在杀伤、破防、抢先手、压迫选择、越过防御资源和终结战斗。
- 剑性六纲不是固定能力清单，每一纲都必须由已抽到或绑定的真实天位解释。不要在正文复述六纲判据，要转译成具体剑路、局势、承压、修炼门槛、禁忌和后果。
- 输出不要只给名字和风味文本。最终设定应暴露机制、启动方式、限制、反噬、修炼或使用门槛，以及一个具体使用场景。

## 输出约定

返回：

- 设定总览：类型、境界、基调、核心用途
- 核心三位：天位、地位、人位
- 天位动力学：来源、增长、衰竭、失控、度量
- 复合结构与纯化取舍
- 地位媒介与施展/修炼方式
- 功法等阶链：仅当类型为功法时必填
- 人位用途与效果
- 限制、代价与反噬；若类型为剑法，改写为修炼门槛、修士风险与反噬
- 境界适配与等阶差距
- 适配场景
- 诸名：至少三个，默认五个，按贴合度排序；每个名字只附一句短说明
- 一段可直接放入小说设定集的正文
