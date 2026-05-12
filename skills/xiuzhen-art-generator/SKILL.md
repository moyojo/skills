---
name: xiuzhen-art-generator
description: Generate controlled prompts for xiuzhen/cultivation-world creative writing. Use this whenever the user asks to create, randomize, brainstorm, design, or refine a 法术, 功法, 秘籍, 法宝, 神通, 百艺, 修真职业, cultivation art, spell, manual, treasure, or related xianxia system by random or constrained random generation.
---

# Xiuzhen Art Generator

Use this skill to generate or write a xiuzhen spell, cultivation method, manual, or magic treasure. The element table is not a fixed taxonomy of the world; it is a sampling aid derived from recurring human categories for understanding reality.

The core model is:

```text
法门 = 天位(动力/力量来源) x 地位(媒介/承载方式) x 人位(目的/作用)
```

## Workflow

1. Read `references/elements.md` only when you need the full element table or category notes. Read `references/realm-system.md` when the request involves realm fit, power scale, social status, sect role, or why a work suits a specific cultivation stage. Read `references/naming.md` when names feel repetitive or the user asks for naming style.
2. Run `scripts/generate_prompt.py` to pick or constrain 天位、地位、人位. Each role can contain one or more elements; the script assigns every element a skill degree, output ceiling, optional local refinement, and a composite-structure role for heaven elements.
3. Use the generated prompt in the current context and produce the final work directly.
4. Include the seed and selected elements when useful for reproducibility.

## Quick Start

Generate a fully random prompt:

```bash
python3 scripts/generate_prompt.py
```

Generate a specific type:

```bash
python3 scripts/generate_prompt.py --type 法宝
python3 scripts/generate_prompt.py --type 功法 --realm 金丹
python3 scripts/generate_prompt.py --type 功法 --realm 元婴
```

Constrain individual dimensions:

```bash
python3 scripts/generate_prompt.py --heaven 愿 --earth 梦 --human 净化
python3 scripts/generate_prompt.py --heaven 剑 --heaven 分 --earth 形 --human 灭 --human 感应
```

Use a seed for reproducibility:

```bash
python3 scripts/generate_prompt.py --seed 20260512 --type 法术
```

Add user conditions without changing the core random draw:

```bash
python3 scripts/generate_prompt.py --condition "偏医毒蛊疫，不要纯攻击" --rarity 失传
```

Bias the random pool toward a 百艺 family or inferred theme:

```bash
python3 scripts/generate_prompt.py --theme 魂梦心识 --type 秘籍
python3 scripts/generate_prompt.py --condition "偏魂梦心识，不要纯攻击"
```

Choose a literary naming style:

```bash
python3 scripts/generate_prompt.py --type 法宝 --name-style 祭文悲怆
python3 scripts/generate_prompt.py --type 神通 --name-style 羚羊挂角
python3 scripts/generate_prompt.py --type 法术 --name-style 数算穷理
python3 scripts/generate_prompt.py --type 法宝 --name-style 甲骨卜辞
python3 scripts/generate_prompt.py --type 神通 --name-style 边塞诗
python3 scripts/generate_prompt.py --type 秘籍 --name-style 丹书火候
```

Generate a multi-heaven or purified path:

```bash
python3 scripts/generate_prompt.py --type 功法 --heaven 剑 --heaven 边界 --heaven 义 --composition-mode 多天位
python3 scripts/generate_prompt.py --type 剑法 --heaven 剑 --heaven 分 --heaven 灭 --composition-mode 纯化
```

## Generation Rules

- Treat 天位 as the most important dimension. It must explain a real dynamics structure: power source, growth method, depletion point, runaway form, and measurement method. A word pasted into flavor text is not a valid 天位.
- Distinguish the real 天位 from the visible topic. A 灵植 art is usually not powered by `生长` unless “growth itself creates power”; it may instead be powered by 灵力, 藏, 等级, 时序, 愿, or another element while 生长/积蓄 acts as medium.
- Treat 地位 as the medium. It can be a body part, artifact material, ritual, symbol, dream, formation, name, number, contract, beast, plant, landscape, or other carrier.
- Treat 人位 as the purpose. It should define what the art does, not just its visual flavor.
- Allow multiple elements in any role. Multi-heaven methods are stronger only when their power sources form a coherent polynomial combination; more 天位 can also make a method impure, unstable, costly, or blocked at higher realms.
- Treat main/auxiliary heavens as only one simple composite pattern. Stronger composite heavens often need a more concrete parent concept that unifies several base heavens, such as 剑统摄分、边界、义、观、感应 into a sword path rather than merely adding them together.
- For composite heavens, identify each heaven's structural role: 统摄父级、核心纲领、供能主源、辅助供能、分支天位、制衡天位、纯化候选、残留/借势. Explain the parent concept before explaining its children.
- Composite heavens are not necessarily binary, and a named parent concept does not always require every branch. Each parent concept can have a different branch count; 剑 has six common纲目, but ordinary sword arts can use only one to three, while higher realms are more likely to integrate more branches.
- Track heaven quality as well as count. `1.00` means normal quality for the current realm; values below 1 are loose, crude, or unstable; values above 1 are refined, high-ceiling, or near-dao. High count with low quality can be worse than fewer high-quality heavens.
- Tie count and quality to realm: low ranks can pick heavens loosely, middle ranks should show 君臣佐使 or clear hierarchy, high ranks should show branch discipline, and top ranks can approach 铸天为一 with many high-quality heavens under one perfect parent structure.
- For advanced or purified forms, explicitly consider whether removing or weakening one 天位 makes the method stronger by reducing drag, contradiction, or dependency.
- Treat the six categories in `references/elements.md` as recurring bottom-level human categories: existence, change, order, relation, cognition, and value. They are expandable; choose a listed element directly when it is already precise, or refine it once into a context-specific subelement when the user request needs novelty or sharper mechanics.
- Use `--theme` or theme words in `--condition` to bias the random pool toward a 百艺 family. Conditions should not remain decorative; they should influence either the sampled elements or the generated mechanism.
- Match realm scale without forcing sect office. 练气/筑基 works should stay personal and practical; 金丹 works can define local authority; 元婴 works should have high-rank weight but may serve a loose cultivator's freedom, escape, retreat, karma-cutting, soul survival, or cave defense; 化神+ works should touch domains, laws, calamity, world boundaries, or dao pursuit.
- Assign separate random values for `技艺程度` and `出力上限`. High skill with low output should feel subtle and precise; low skill with high output should feel dangerous and wasteful.
- If the user provides constraints, honor them first and randomize the remaining dimensions.
- Avoid producing only a name and flavor text. The final generated work should expose mechanism, activation, limits, backlash, cultivation/use requirements, and one concrete scene or use case.
- Avoid repetitive naming. Do not default to `XX经`; choose names by type. 法宝 should usually have a concrete器型, 神通/术法 should be short and action-heavy, 秘籍 can be 篇/卷/真解/图/谱/录/问/答/章/牒/策, and 剑法 can be 剑诀/剑式/剑谱/剑意/剑心诀 unless it is truly a root-level 剑经.
- Use a literary or discourse source before choosing words. Good names should feel like they grew out of an old textual mode, not like generic archaic decoration. The naming map includes 诗经国风、雅颂礼乐、楚辞骚体、甲骨卜辞、金文钟鼎、汉乐府、古诗十九首、建安风骨、魏晋玄言、游仙诗、志怪、六朝骈文、盛唐空灵、李白豪逸、王维山水、边塞诗、晚唐苦吟、婉约词、豪放词、元曲、竹枝歌谣、赋、祭诔、碑铭、奏疏、诏敕、檄移、论说、诸子、算经、历法、律吕、河洛、医书、本草、丹书、史传、方志、山海经、兵书、道教科仪、佛经、密教、禅宗公案、传奇话本、公案小说、农书月令、水经、茶香琴谱、棋谱、谱录品评、营造工匠.
- When no `--name-style` is specified, let the script choose a source that creates texture. When the user specifies a source, obey it, but still match the type: a 法宝 needs a concrete object or document-form carrier; a 神通 may be a phrase, gesture, order, or action; a 秘籍 may be a scroll, chart, register, commentary, memorial, strategy, formula, ritual, or craft note.
- Avoid museum-label or paper-title names. `三垣推步盘` works because it is an object and a procedure; `基于历法推步的高阶命数法宝` does not.

## Output Contract

Return:

- 名称
- 命名来源与文体气质
- 类型
- 核心三位：天位、地位、人位
- 天位动力学：来源、增长、衰竭、失控、度量
- 复合天位结构：统摄父级、核心纲领、供能主源、辅助供能、分支、制衡、纯化候选、残留/借势
- 天位数量与质量：为什么该数量、质量适合当前境界
- 多要素结构：父级概念、分支组合、冲突、纯化取舍
- 原理
- 形制或修炼/施展方式
- 效果
- 限制与代价
- 境界适配与等阶差距
- 失控或反噬
- 适配场景
- 一段可直接放入小说设定集的正文

## Evaluation Rubric

Score generated results out of 10:

- 天位动力学, 0-3: each 天位 has source, growth, depletion, runaway, measurement, and no decorative power words.
- 复合天位结构, 0-2: composite heavens are unified by a meaningful parent concept or explicit structure; main/auxiliary is used only when appropriate.
- 天位数量与质量, 0-1: heaven count and quality match realm and maturity; not every composite is binary or all-branch complete.
- 多要素结构, 0-2: multiple 天/地/人 elements combine coherently, with conflicts, drag, or pure-form tradeoffs explained.
- 范畴与细分, 0-2: elements are treated as bottom-category lenses and refined only when the refinement improves mechanics.
- 条件遵守, 0-2: user constraints affect sampling and output, including theme and targeting requirements.
- 境界适配, 0-1: realm identity, status, freedom/sect orientation, resource scale, and inter-realm gap are plausible.
- 可用性, 0-1: final result is usable in fiction with limits, costs, backlash, and scene use.
- 命名, 0-2: name is type-appropriate, avoids `XX经` defaulting and high-frequency word stacks, and clearly inherits texture from a literary/discourse source without becoming a museum label.
