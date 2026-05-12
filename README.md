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

下面展示几组实际生成结果。相同请求在不同会话中可能因为随机抽样与模型发挥而变化；需要复现结构化提示词时，可使用脚本的 `--seed` 参数。

### 示例一：金丹境追索破障法术

```text
$xiuzhen-art-generator 生成一个金丹境法术，偏追索、破障和宗门秘传风格
```

生成结果：

```text
《照垣追真敕》

类型：法术
境界：金丹境
基调：宗门秘传、追索破障、执法镇山
核心用途：追摄敌踪、照破遮掩、拆解禁制与幻障

核心三位：
- 天位：观、分、证
- 地位：敕符、镜光、残息
- 人位：追索、破障、显真

此术以“观”为主动力，借金丹神识凝成一线照真之意；以“分”剥离假象、阵纹、障眼法与真实痕迹；以“证”借宗门法脉作准，确认被追之人、物、术是否与残息相合。

其力来源于施术者金丹神识、宗门祖师敕符，以及目标遗留的一缕气息。气息越新、因果越近，术力越盛；若追索对象曾入过本宗山门、受过本宗法器所伤，效果尤强。

施术需一枚宗门敕符、一面可承神识的铜镜或水镜，以及目标残息。残息可以是血迹、衣角、断发、兵器划痕、残留法力，或被目标触碰过的封禁。

此术不能直接伤敌，但能让同门剑修、阵师或执法长老准确出手。若用于斗法，可在敌人遁逃或藏形的一瞬照出其真气转折，使其藏身术失效半息到三息。

限制与反噬：
- 必须有残息为引，凭空不可施展。
- 残息越杂，误判越多；目标若主动断因、换身、借血脉替劫，追索结果会偏移。
- 强行照破高阶禁制时，镜光可能反冲识海，使施术者七窍渗血、金丹震鸣，严重者数日不能动用神识。

诸名：
1. 《照垣追真敕》：兼有破障、追索与宗门敕令之意。
2. 《三照分障术》：突出三重照验和拆分遮掩的机制。
3. 《金镜证踪法》：偏执法堂风格，强调以镜光验证真踪。
4. 《破隐照息符》：更像配套符术名，适合低阶残篇或外门简化版。
```

### 示例二：三门筑基防护法术

```text
生成三门适合筑基修士的防护法术，要求各自的天位、地位、人位不要重复
```

生成结果：

```text
1. 愿符守身术
   三位：天位「愿」；地位「符」；人位「护持」
   机制：以自身守命之愿灌入护身符，受击时符纹先替修士承压，化作一层淡金愿障；愿力越纯，越能抵住阴煞、飞针、低阶术火等突袭。
   限制：只能护住施术者近身三尺，遇到连续重击会迅速耗尽符力；若临阵心志动摇，愿障会出现裂纹。

2. 藏影避锋法
   三位：天位「藏」；地位「影」；人位「避锋」
   机制：将气机暂藏入自身影中，使来袭法器与术法误判落点，适合筑基修士在斗法中避过第一轮杀招。
   限制：必须有影可借，强光、无影之地或被神识锁死时效果大减；不能硬挡范围轰击，只能偏移针对性攻击。

3. 衡水卸甲咒
   三位：天位「衡」；地位「水」；人位「卸力」
   机制：以水汽成环，借“衡”意把外来冲击分散到周身灵水中，令刀罡、拳劲、土石冲撞先被缓冲再滑开。
   限制：对锐利穿透类法器防护较弱；施术者需保持灵力平稳，若强行承受高出一阶的攻击，水环会反噬经脉。
```

### 示例三：元婴期因果梦境法宝

```text
设计一件偏因果与梦境的元婴期法宝，给出名称、来历、使用代价和克制方式
```

生成结果：

```text
还因梦灯

类型：元婴期法宝
基调：因果牵缠、梦境锁魂
核心用途：以梦为媒，追索因果、逼问旧债、困住元婴出窍之身。

来历：
此灯出自眠霞宗末代宗主之手。传说她渡元婴心魔劫失败后，将自身梦府炼成灯盏，又以三百名背誓弟子的旧誓为灯芯，铸成此宝。灯火不照肉身，只照人与人之间未了的因果。

能力：
持灯者需取得目标一缕因果凭据，如旧物、血字、誓言、姓名真音。点灯后，目标会在入梦、入定或元婴出窍时坠入“还因梦”。梦中一切幻象都由其真实因果演化，越是亏欠、背誓、杀业深重，梦境越难挣脱。持灯者可借梦追踪目标方位，逼其显露隐秘，或暂时封住元婴远遁。

使用代价：
每点一次灯，持灯者必须抵押自身一段真实记忆作为灯油。若强行困杀同阶元婴，梦灯会反噬，将持灯者也卷入对方因果之中；轻则梦魇缠身、道心生裂，重则分不清自身记忆与他人旧债。

克制方式：
无因果凭据时，此灯只能照出模糊梦影，难以锁定目标。清净道心、斩缘秘术、替身因果、无梦定法皆可削弱其效力。若目标主动偿还关键因果，或以更高阶法宝镇住本命元婴，梦灯便会失去锁链，只剩追踪余光。
```

### 示例四：连续生成与避重

```text
接着上一批宗门秘传生成，偏防护和追索，不要重复上一批核心意象
```

生成结果：

| 名称 | 三位 | 机制 | 与上一批避重说明 |
|---|---|---|---|
| 《玄檐归息牒》 | 天位：息；地位：门牒、檐铃；人位：护持、识返 | 守山弟子以门牒记住来客气息，檐铃不响则藏院，轻响则标记来路，急响则把闯入者一步步引回入门处。 | 避开攻伐显象，核心转为“气息留痕”和“宗门门户防护”。 |
| 《清渠照影箓》 | 天位：映；地位：渠水、符箓；人位：追索、辨伪 | 将一缕残气落入清渠，水面不现人形，只现其经行之处的“倒影断点”，可追查潜入、易容和替身术。 | 不沿用上一批的正面斗法意象，改写为低声、隐性的查证秘术。 |
| 《素壁闭声章》 | 天位：静；地位：素壁、墙灰；人位：隔绝、守秘 | 以墙灰封住一室之声与神识波纹，外人只能听见预先留下的空谈；若有人强窥，灰痕会记下窥探方向。 | 避开强烈杀伤和外放异象，突出宗门密议、藏经阁、闭关室的防护用途。 |
| 《回针寻踪法》 | 天位：回；地位：衣针、旧线；人位：追迹、牵引 | 取失踪者旧衣一线穿针，针尖不指人，只指“最后被改写过的路径”，适合追查掳掠、阵门挪移和伪造脚印。 | 不重复上一批的主战核心，改用旧物、线迹、路径回溯作为追索主轴。 |

### 脚本生成结构化提示词

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
