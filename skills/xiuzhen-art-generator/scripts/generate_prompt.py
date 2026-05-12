#!/usr/bin/env python3
"""Generate a controlled prompt for xiuzhen art creation."""

from __future__ import annotations

import argparse
import json
import random
import textwrap
import time
from pathlib import Path
from dataclasses import asdict, dataclass, replace
from typing import Iterable

from pool_parser import parse_pool_file


SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "data"
ROOT_DIR = SCRIPT_DIR.parent


POOL_DATA = parse_pool_file(DATA_DIR / "pools.md")
ELEMENTS = POOL_DATA["elements"]
REFINEMENTS = POOL_DATA["refinements"]
THEMES = POOL_DATA["themes"]
THEME_ELEMENTS = POOL_DATA["theme_elements"]
CONDITION_ALIASES = POOL_DATA["condition_aliases"]
CUSTOM_ELEMENTS = POOL_DATA["custom_elements"]
COMPOSITE_PARENT_MODELS = POOL_DATA["composite_parent_models"]
SWORD_BRANCH_MODELS = POOL_DATA["sword_branch_models"]
SWORD_MOMENTUM_STORAGE_CONTEXTS = POOL_DATA["sword_momentum_storage_contexts"]
SWORD_MOMENTUM_FIXED_CONTEXTS = POOL_DATA["sword_momentum_fixed_contexts"]
SWORD_MOMENTUM_BORROW_CONTEXTS = POOL_DATA["sword_momentum_borrow_contexts"]
SWORD_MOMENTUM_BY_SOURCE = POOL_DATA["sword_momentum_by_source"]
HIGH_SCALE_REFINEMENTS = POOL_DATA["high_scale_refinements"]
HIGH_RISK_ELEMENTS = POOL_DATA["high_risk_elements"]
REFERENCE_CONTEXT_FILES = (
    ("修真要素参考", ROOT_DIR / "references" / "elements.md"),
    ("境界体系参考", ROOT_DIR / "references" / "realm-system.md"),
    ("命名参考", ROOT_DIR / "references" / "naming.md"),
    ("范畴要素池", DATA_DIR / "pools.md"),
)
MAINTENANCE_CONTEXT_PATTERNS = (
    "权威池数据在",
    "`data/pools.md`",
    "修改池子后运行",
    "python3 ",
    "scripts/",
    "validate_pools",
    "格式约定",
    "要素行格式",
    "关联池用",
    "分支偏置` 写成",
)

TYPES = ("法术", "功法", "秘籍", "法宝", "神通", "百艺", "剑法")
REALMS = ("练气", "筑基", "金丹", "元婴", "化神", "炼虚", "合体", "大乘")
RANDOM_MODES = ("usable", "force")
SWORD_BRANCHES = tuple(SWORD_BRANCH_MODELS)
REALM_RANK = {realm: index for index, realm in enumerate(REALMS)}
REALM_CONTEXT = {
    "练气": {
        "status": "外门弟子、底层散修、宗门劳力或侦察炮灰",
        "lifespan": "约100-150岁",
        "scale": "个人生存、小法术、低阶符器、基础修炼，不应有战略级效果",
        "fit": "适合侦查、护身、基础攻击、防身、入门功法、低阶百艺",
    },
    "筑基": {
        "status": "内门弟子、正式修士、小家族核心、小宗门长老候选",
        "lifespan": "约200-300岁",
        "scale": "稳定道基、个人洞府、小队行动、地方小影响力",
        "fit": "适合个人标志法门、可靠战斗手段、小型阵法或家族传承",
    },
    "金丹": {
        "status": "宗门长老、真传顶层、大族老祖、地方霸主",
        "lifespan": "约500-1000年以上",
        "scale": "可镇守一方，能压制低阶群体，拥有正经法宝和地域声望",
        "fit": "适合具名法宝、长老级功法、地方压制、强战斗或高价值百艺",
    },
    "元婴": {
        "status": "大宗高层或老祖，也可以是强大散修、游方老怪、隐洞修士、客卿或避债避劫的逍遥修士",
        "lifespan": "千年以上；元婴可出窍，存在夺舍可能",
        "scale": "高端威慑与个人自由并存；可影响宗门战争，也可服务远遁、避劫、闭关、断因果、生存、化身或洞府经营",
        "fit": "功能必须有高阶分量，具体效用由人位决定；可落在魂魄出窍、远遁保命、洞府防护、断因果、避天机、保化身、破大阵或战略威慑",
    },
    "化神": {
        "status": "超级势力太上长老、隐世老祖、域中支柱，也可以是独行求道者",
        "lifespan": "数千年",
        "scale": "可影响一域格局或禁地风险，开始触碰法则、元神、神识压制和道痕",
        "fit": "适合法则化、领域化、跨地域远行/威慑、避灾断缘或接近神话的传承",
    },
    "炼虚": {
        "status": "顶尖老怪物、宗门真正底蕴、接近飞升序列",
        "lifespan": "以千年计",
        "scale": "触及虚空、界域、法则缝隙，能决定大势力兴衰",
        "fit": "适合虚空、界域、道体、宗门命运级法门或法宝",
    },
    "合体": {
        "status": "顶尖老怪物、镇压大势力气运的底蕴",
        "lifespan": "以千年计",
        "scale": "身与道、法与域高度合一，出手可改写大片地域格局",
        "fit": "适合身道合一、领域合一、族运宗运级重器和高阶传承",
    },
    "大乘": {
        "status": "近飞升存在、凡界巅峰、传说中的定海神针",
        "lifespan": "极长，常闭关避劫或备飞升",
        "scale": "凡界巅峰，牵涉飞升、天劫、界面规则和族群存亡",
        "fit": "适合飞升准备、界面边界、天劫应对、镇族镇宗终极底蕴",
    },
}
REALM_STAGE_FOCUS = {
    "练气": "引气、辨性、开感官、立基本循环、养出最小媒介；配低阶侦测、护身或小术。",
    "筑基": "稳道基、固媒介、定主辅结构；配身法、护法、基础攻击或百艺专长。",
    "金丹": "结成核心权柄，压缩、统筹或封存前两阶所得；配本命术、丹域雏形、镇压、破阵或炼宝法。",
    "元婴": "进入神魂、元婴、化身、远遁、生存、因果或高阶威慑尺度；配套术法按本次人位决定，可表现为出窍、避劫、洞府防护、断追索、化身经营或其他同阶用途。",
    "化神": "将元婴经验外化为法域、道痕、类法则或神识威压；配领域、跨域感应、规则干涉或灾劫应对。",
    "炼虚": "处理虚空、界面与法则缝隙；配跨域、开界、避界灾或虚实转化法。",
    "合体": "身与道、法与域高度合一；配身道合一、领域合一、镇族镇宗或族运宗运级法门。",
    "大乘": "面向飞升、天劫、界面规则和族群存亡；配替劫、飞升准备、镇界或渡劫法。",
}
RARITIES = ("坊市常见", "宗门秘传", "旁门异术", "上古失传", "仙古残篇")
DEFAULT_RARITY_WEIGHTS = {
    "练气": (("坊市常见", 10), ("宗门秘传", 5), ("旁门异术", 3), ("上古失传", 1), ("仙古残篇", 0)),
    "筑基": (("坊市常见", 8), ("宗门秘传", 7), ("旁门异术", 4), ("上古失传", 1), ("仙古残篇", 0)),
    "金丹": (("坊市常见", 3), ("宗门秘传", 9), ("旁门异术", 5), ("上古失传", 1), ("仙古残篇", 0)),
    "元婴": (("坊市常见", 1), ("宗门秘传", 8), ("旁门异术", 5), ("上古失传", 2), ("仙古残篇", 0)),
    "化神": (("坊市常见", 0), ("宗门秘传", 5), ("旁门异术", 4), ("上古失传", 3), ("仙古残篇", 1)),
    "炼虚": (("坊市常见", 0), ("宗门秘传", 4), ("旁门异术", 3), ("上古失传", 4), ("仙古残篇", 2)),
    "合体": (("坊市常见", 0), ("宗门秘传", 3), ("旁门异术", 2), ("上古失传", 5), ("仙古残篇", 3)),
    "大乘": (("坊市常见", 0), ("宗门秘传", 2), ("旁门异术", 2), ("上古失传", 5), ("仙古残篇", 4)),
}
COMPOSITION_MODES = ("单纯", "多天位", "多媒介", "多目的", "复合法门", "纯化")
NAME_STYLE_PROFILES = {
    "诗经国风": {
        "fit": "巫器、妖术、野神法、古部落传承、草木鸟兽法",
        "texture": "草木、鸟兽、劳作、婚恋、道路与祭物；朴素粗纯，像风谣里长出的术名",
        "tokens": ("白茅", "葛藟", "蒹葭", "卷耳", "鹿鸣", "采薇", "桑中", "雎鸠", "苕华", "鲂尾"),
        "examples": ("白茅束", "葛藟索", "蒹葭隔水", "卷耳迷途", "鹿鸣鼓", "采薇镰"),
    },
    "诗经粗纯": {
        "fit": "上古巫祝、荒山野神、妖族、古部落、原始祭器、草木鸟兽法",
        "texture": "草木鸟兽、采摘、道路、祭器、原始巫性；朴素、生僻、粗粝",
        "tokens": ("卷耳", "白茅", "蒹葭", "雎鸠", "葛藟", "鹿鸣", "鲂尾", "采薇", "苕华", "桑中"),
        "examples": ("卷耳筐", "白茅束", "鹿鸣鼓", "采薇镰", "蒹葭隔水", "白茅束鬼"),
    },
    "雅颂礼乐": {
        "fit": "祭器、宗门正法、宗族传承、祖灵庇护、礼制法宝",
        "texture": "宗庙、礼乐、肃穆、祖灵与受命；庄重而不堆砌威词",
        "tokens": ("清庙", "玄鸟", "肃雍", "维岳", "祖灵", "玉磬", "告命", "镇坛", "宗祧", "礼器"),
        "examples": ("清庙玉磬", "玄鸟告命符", "肃雍步", "维岳镇坛印", "祖灵玉册"),
    },
    "楚辞骚体": {
        "fit": "女仙、水府、魂术、招魂、云水遁法、香草法宝",
        "texture": "香草美人、巫觋、云水、招魂；华美而带幽远神巫气",
        "tokens": ("兰泽", "湘君", "蘅皋", "九歌", "杜若", "芳洲", "云中", "招魂", "佩兰", "沅湘"),
        "examples": ("兰泽招魂", "湘君佩", "蘅皋渡影", "九歌行神法", "杜若返魂符"),
    },
    "甲骨卜辞": {
        "fit": "卜筮、预知、灾异、诅咒、兽骨符器、问鬼术",
        "texture": "贞问、灾异、兽骨、天命；短硬、古拙、像刻在骨上的问句",
        "tokens": ("贞风", "翌日", "灼龟", "卜雨", "骨契", "问鬼", "旬亡", "告祖", "灾眚", "龟兆"),
        "examples": ("贞风骨契", "翌日问鬼", "灼龟听命", "卜雨骨符", "旬亡占"),
    },
    "金文钟鼎": {
        "fit": "重器、宗族法宝、镇社印、功业传承、受命法",
        "texture": "铸器、受命、祖考、功业；厚重，有铜锈和宗族秩序感",
        "tokens": ("乍雷", "受命", "祖考", "铭功", "镇社", "铜鼎", "宗彝", "金册", "大钺", "作宝"),
        "examples": ("乍雷铜鼎", "受命盘", "祖考钺", "铭功镇社印", "宗彝金册"),
    },
    "祝盟誓辞": {
        "fit": "契约法、血盟、誓咒、背盟反噬、神罚法宝",
        "texture": "对天起誓、断牲取信、背盟招殃；严厉、公开、有神明见证",
        "tokens": ("白水", "告天", "断牲", "背盟", "招殃", "血誓", "盟书", "歃血", "神罚", "同盟"),
        "examples": ("白水盟符", "告天血誓", "断牲盟书", "背盟招殃咒", "歃血契"),
    },
    "汉乐府": {
        "fit": "行旅术、军中法、民间异术、劳生法宝、边地小术",
        "texture": "长歌、民间叙事、战争与生计；直白里有苦味",
        "tokens": ("饮马", "长城窟", "陌上桑", "东门行", "十五从军", "陇头", "妇病", "孤儿", "行路", "采桑"),
        "examples": ("饮马符", "长城窟步", "陌上桑影", "东门行刀", "陇头水咒"),
    },
    "古诗十九首": {
        "fit": "遁法、命数、伤逝神通、漂泊法宝、离别心法",
        "texture": "漂泊、离别、岁月消磨；低声而长，适合不归与迟暮",
        "tokens": ("迢迢", "去日", "行行", "明月", "客衣", "生年", "旧交", "远道", "浮云", "相思"),
        "examples": ("迢迢星佩", "去日苦多法", "行行无归步", "明月照客衣", "浮云避世符"),
    },
    "建安风骨": {
        "fit": "剑修、战法、豪士法宝、乱世功法、军阵神通",
        "texture": "慷慨、短歌、乱世、志气；悲壮但骨头硬",
        "tokens": ("横槊", "短歌", "白骨", "烈士", "铜雀", "慷慨", "秋风", "军行", "壮心", "野哭"),
        "examples": ("横槊铜箫", "短歌问命", "白骨露野剑", "烈士暮年诀", "慷慨破阵法"),
    },
    "魏晋玄言": {
        "fit": "神魂法、心法、解脱术、忘形法宝、清谈禁制",
        "texture": "清虚、玄理、忘言、坐谈；机制不宜太热闹，要像一念解形",
        "tokens": ("虚舟", "忘言", "濠上", "玄谈", "坐忘", "清虚", "物外", "无待", "形解", "玄同"),
        "examples": ("虚舟印", "忘言简", "濠上观鱼法", "玄谈解形术", "坐忘灯"),
    },
    "游仙诗": {
        "fit": "飞遁、长生、仙府法宝、餐霞炼气、云中行术",
        "texture": "登真、餐霞、控鹤、步虚；轻而高远，有仙府道书感",
        "tokens": ("餐霞", "控鹤", "步虚", "青童", "登真", "云车", "玉京", "羽衣", "流霞", "洞天"),
        "examples": ("餐霞瓶", "控鹤符", "步虚履", "青童引路术", "登真玉简"),
    },
    "志怪乡谈": {
        "fit": "妖术、旁门、精怪法宝、民间怪事、狐鬼小术",
        "texture": "荒诞而朴素，怪事像乡谈；不要写成宏大史诗",
        "tokens": ("剪纸", "井中月", "石羊", "狐灯", "瓦上", "鬼市", "借路", "竹马", "墙影", "夜谈"),
        "examples": ("剪纸马", "井中月", "指石羊", "狐灯照路术", "瓦上听鬼符"),
    },
    "六朝骈文": {
        "fit": "华贵法宝、女仙术、幻术、宫阙禁制、对偶法名",
        "texture": "对偶、华美、缛丽、宫殿感；辞采繁密但仍要可读",
        "tokens": ("双鸾", "流霞", "金铺", "玉树", "珠帘", "凤诏", "并影", "合景", "分香", "绮殿"),
        "examples": ("双鸾佩", "流霞合景", "金铺照夜", "玉树分香法", "珠帘并影"),
    },
    "盛唐空灵": {
        "fit": "高阶身法、剑意、仙人法宝、遁法、幻术",
        "texture": "羚羊挂角、无迹可求；像空中之音、水中之月，不解释机制",
        "tokens": ("月下", "空山", "水中", "无迹", "听潮", "过云", "照夜", "天外", "梦里", "风前"),
        "examples": ("月下杯", "空山环", "无迹履", "过云剑", "水月换形", "过云不留"),
    },
    "羚羊挂角": {
        "fit": "身法、幻术、仙人法宝、遁法、梦法、无迹剑术",
        "texture": "空灵、忽现、不可凑泊；名字不解释机制，像风月云水一闪而过",
        "tokens": ("月下", "空山", "水中", "无迹", "听潮", "过云", "照夜", "天外", "梦里", "风前"),
        "examples": ("月下杯", "空山环", "无迹履", "过云剑", "水月换形", "过云不留"),
    },
    "李白豪逸": {
        "fit": "酒器、剑修、狂仙神通、远游遁法、豪放法宝",
        "texture": "醉、月、天门、长风，忽然拔高；豪逸不是堆大词",
        "tokens": ("邀月", "长风", "青天", "斗酒", "天门", "落星", "大鹏", "飞流", "明月", "剑歌"),
        "examples": ("邀月杯", "长风破浪术", "青天揽月手", "斗酒御剑", "天门飞剑"),
    },
    "王维山水": {
        "fit": "心法、隐遁、静修法宝、洞府禁制、洗念术",
        "texture": "空山、松风、溪声、白云；山水里带禅意和静气",
        "tokens": ("空山", "松下", "溪声", "白云", "竹里", "鹿柴", "寒泉", "柴门", "清磬", "入定"),
        "examples": ("空山磬", "松下入定法", "溪声洗念", "白云藏身", "竹里听心符"),
    },
    "边塞诗": {
        "fit": "军阵、战法、戍边法宝、关塞传讯、铁衣法",
        "texture": "大漠、胡天、霜旗、笳声、铁衣；壮阔但有人间寒苦",
        "tokens": ("玉门", "瀚海", "龙沙", "霜旗", "胡天", "铁衣", "羌笛", "塞下", "孤城", "烽燧"),
        "examples": ("玉门砂印", "瀚海听笳术", "龙沙解甲符", "霜旗敕马", "铁衣护身法"),
    },
    "岑参奇伟": {
        "fit": "异域法宝、极境神通、奇寒奇热法、边地秘术",
        "texture": "火山、热海、飞雪、奇景；边塞气象诡丽而壮阔",
        "tokens": ("热海", "火山", "轮台", "白草", "飞雪", "胡沙", "走马", "天山", "瀚海", "雪令"),
        "examples": ("热海铜瓶", "火山雪令", "轮台风鼓", "白草连天术", "天山飞雪符"),
    },
    "高适沉雄": {
        "fit": "军政法、阵书、兵符、将帅法宝、败阵反思术",
        "texture": "战争判断、将帅讽刺、士卒悲壮；沉雄而有现实利害",
        "tokens": ("营州", "塞下", "孤军", "败阵", "请命", "断策", "军牒", "问将", "边庭", "战骨"),
        "examples": ("营州军牒", "塞下断策", "孤军请命书", "败阵问将法", "边庭锁阵符"),
    },
    "山水田园": {
        "fit": "隐居法、灵田法宝、洞府小阵、农桑修行、避世术",
        "texture": "归隐、农桑、柴门、溪桥；轻淡但可藏深机",
        "tokens": ("柴门", "南山", "溪桥", "荷锄", "归田", "松径", "种玉", "烟村", "春畦", "竹杖"),
        "examples": ("柴门符", "南山种玉法", "溪桥听雨", "荷锄入梦术", "春畦养气诀"),
    },
    "新乐府讽谕": {
        "fit": "因果法、照世镜、戒律术、民瘼愿力、平冤法宝",
        "texture": "现实、民瘼、讽刺、世道不平；名字要有世情重量",
        "tokens": ("卖炭", "悯农", "织妇", "观市", "平冤", "采薪", "饥民", "断机", "盐铁", "苦役"),
        "examples": ("卖炭照夜符", "悯农尺", "织妇断机咒", "观市平冤镜", "采薪问税法"),
    },
    "晚唐苦吟": {
        "fit": "阴寒法宝、孤绝剑意、鬼修小术、梦魇法、迟暮心法",
        "texture": "残灯、霜虫、冷雨、孤馆；寒瘦、孤绝、苦到骨里",
        "tokens": ("苦雨", "残棋", "霜虫", "孤馆", "冷烛", "荒阶", "断梦", "听更", "瘦影", "秋灯"),
        "examples": ("苦雨灯", "残棋问鬼", "霜虫断梦", "孤馆听更术", "冷烛照魂符"),
    },
    "晚唐绮艳": {
        "fit": "魅术、幻术、女修法宝、梦法、香奁类法器",
        "texture": "香奁、金缕、梦、绮丽而阴郁；艳中带冷",
        "tokens": ("金缕", "绮窗", "残香", "红烛", "宝奁", "梦帕", "照魄", "换影", "翠袖", "夜妆"),
        "examples": ("金缕梦帕", "绮窗迷香", "残香照魄", "红烛换影术", "翠袖藏魂"),
    },
    "婉约词": {
        "fit": "幻术、情咒、梦法、帘幕法宝、离魂小术",
        "texture": "帘幕、斜月、残酒、梦回；软而不弱，缠绵里藏术",
        "tokens": ("斜月", "帘钩", "梦雨", "残酒", "离亭", "燕归", "罗幕", "小楼", "春恨", "香冷"),
        "examples": ("斜月帘钩", "梦雨迷香", "残酒照魂", "离亭燕咒", "罗幕藏身"),
    },
    "豪放词": {
        "fit": "战神通、军魂法宝、壮怀剑法、山河法术",
        "texture": "关河、铁马、壮怀、江山；慷慨但带词调回响",
        "tokens": ("铁马", "冰河", "关河", "挑灯", "拍阑", "江山", "醉里", "弓刀", "北望", "壮怀"),
        "examples": ("铁马冰河印", "关河入梦", "醉里挑灯术", "拍阑问剑法", "北望弓符"),
    },
    "咏物词": {
        "fit": "小型法宝、灵物、寄托心法、避劫小术",
        "texture": "借物写心、托物藏锋；名字像物名，内里有术",
        "tokens": ("孤梅", "雁字", "柳眼", "蝉衣", "藏雪", "回魂", "窥春", "避劫", "落絮", "寒枝"),
        "examples": ("孤梅藏雪", "雁字回魂", "柳眼窥春", "蝉衣避劫术", "寒枝寄命"),
    },
    "元曲散曲": {
        "fit": "旁门、旅人法、江湖术、市井法宝、鬼市异术",
        "texture": "市井、荒凉、俚俗里有苍凉；不要太仙，要有人间尘土",
        "tokens": ("西风", "瘦马", "枯藤", "昏鸦", "古道", "归店", "断桥", "酒旗", "客路", "荒村"),
        "examples": ("西风瘦马符", "枯藤栖鸦", "古道问魂", "昏鸦归店术", "断桥照影"),
    },
    "竹枝歌谣": {
        "fit": "地域宗门、民间术、渡水法、采药法、江湖传讯",
        "texture": "地方口音、江水、渡口、风俗；明快而带乡土",
        "tokens": ("巴山", "江口", "踏歌", "青溪", "竹符", "唤舟", "采药", "渡水", "渔灯", "峡雨"),
        "examples": ("巴山竹符", "江口唤舟", "踏歌渡水", "青溪采药法", "渔灯引路"),
    },
    "谣谚童谣": {
        "fit": "谶语、童子法、诅咒、民间预言、灾异符",
        "texture": "简短、预言、民间恐惧；像街巷里传开的怪歌",
        "tokens": ("赤乌", "白犬", "三更", "童子", "唱灾", "拍门", "过桥", "无头", "黑月", "儿歌"),
        "examples": ("赤乌谣", "白犬过桥咒", "三更拍门符", "童子唱灾法", "黑月儿歌"),
    },
    "大赋都邑": {
        "fit": "巨型法宝、仙城、洞天、山河阵图、界域法",
        "texture": "铺张、宫阙、山川、万物罗列；宏大但必须有形制",
        "tokens": ("上林", "甘泉", "海赋", "云梦", "万象", "承露", "量潮", "吞波", "宫阙", "列山"),
        "examples": ("上林万象图", "甘泉承露盘", "海赋量潮图", "云梦吞波阵", "列山金阙图"),
    },
    "洛神神美": {
        "fit": "女仙、水府、月宫、幻术、身法、镜类法宝、魅神法",
        "texture": "美而不可逼近；水、月、云、风、衣佩、身姿中藏危险",
        "tokens": ("惊鸿", "流雪", "蔽月", "回风", "凌波", "秋水", "游龙", "朝霞", "芙蕖", "罗袜"),
        "examples": ("惊鸿佩", "流雪罗", "蔽月纱", "凌波袜", "回雪转身", "云蔽月形"),
    },
    "祭文悲怆": {
        "fit": "遗物、复仇法、招魂术、禁术、断门传承",
        "texture": "有旧事、死别、遗骨、未竟之愿；悲而克制，有礼法骨架",
        "tokens": ("归", "櫬", "孤城", "旧骨", "断门", "遗书", "问名", "何赎", "不归", "百身"),
        "examples": ("还骨匣", "百身印", "孤城砚", "不归铃", "魂知旧路咒", "归櫬召魂仪"),
    },
    "诔哀吊": {
        "fit": "亡者法宝、阴司术、招魂、葬器、旧友遗法",
        "texture": "悼亡、追述、伤逝；比祭文更冷、更像给一生收束",
        "tokens": ("故人", "吊影", "哀江", "旧冢", "闻声", "引魂", "寒碑", "亡名", "归魄", "孤坟"),
        "examples": ("故人灯", "吊影符", "哀江引魂", "旧冢闻声法", "寒碑锁魄"),
    },
    "墓志碑铭": {
        "fit": "封印、葬器、命籍、镇墓法宝、葬仙禁制",
        "texture": "一生压成数行字，沉重而冷；名字像刻在石上的结论",
        "tokens": ("残碑", "石志", "没字", "葬仙", "封名", "锁年", "墓门", "寒铭", "玄碣", "死籍"),
        "examples": ("残碑封名", "石志锁年", "没字碑", "葬仙铭", "玄碣断命"),
    },
    "铭箴戒": {
        "fit": "戒尺、印、佩、护身法、宗门戒法、自律心法",
        "texture": "警策、约束、器上文字；短而硬，像随身铭文",
        "tokens": ("戒贪", "照心", "慎独", "铭骨", "止欲", "守中", "知止", "无欺", "刻心", "戒尺"),
        "examples": ("戒贪尺", "照心铭", "慎独佩", "铭骨护身法", "知止印"),
    },
    "颂赞庙堂": {
        "fit": "正道法宝、神祇法、护国符、庙堂传承、功德法",
        "texture": "礼赞、神圣化、庙堂光；正大而有制度仪式感",
        "tokens": ("清庙", "昭德", "太平", "圣灵", "护国", "金章", "颂印", "庙光", "嘉德", "赞书"),
        "examples": ("清庙颂印", "昭德金章", "太平赞", "圣灵护国符", "嘉德玉书"),
    },
    "表章陈情": {
        "fit": "请命法、护国法、愿力法宝、冤屈申诉、保命术",
        "texture": "臣子陈情，恭敬而沉痛；力量来自申告、请命与名分",
        "tokens": ("陈情", "请命", "伏阙", "泣血", "上表", "青章", "哀请", "叩阙", "封章", "申命"),
        "examples": ("陈情箓", "请命青章", "伏阙符", "泣血上表法", "叩阙保身符"),
    },
    "奏疏议": {
        "fit": "天庭法、宗门戒律、请雨章、匡正法、天机议策",
        "texture": "条陈利害、匡正君上；理性、制度化、有公文压力",
        "tokens": ("谏雷", "平妖", "论劫", "请雨", "上清", "奏章", "疏牒", "议法", "条陈", "劾鬼"),
        "examples": ("谏雷疏", "平妖奏", "论劫议", "上清请雨章", "劾鬼青词"),
    },
    "策问对策": {
        "fit": "天机术、问道术、临机破局、局势推演、试炼法",
        "texture": "临场答问、治世推演；像以问答逼出天地之理",
        "tokens": ("问天", "对劫", "策断", "三问", "定局", "阴阳", "临策", "问道", "对机", "策书"),
        "examples": ("问天策", "对劫书", "策断阴阳", "三问定局法", "临策破阵"),
    },
    "诏敕令": {
        "fit": "号令法宝、雷令、山水调遣、禁制、天庭权柄",
        "texture": "最高命令，不解释；名字要短促、有权力落下的重量",
        "tokens": ("青敕", "敕山", "金门", "闭海", "雷令", "禁门", "敕水", "开岳", "天诏", "令牌"),
        "examples": ("青敕牌", "敕山令", "金门诏", "闭海令", "敕水雷牌"),
    },
    "檄移公文": {
        "fit": "战争神通、破阵法、调遣山水、驱逐异类、宣战符",
        "texture": "讨伐、通告、声罪致讨；文字像兵马先行",
        "tokens": ("讨妖", "羽林", "声罪", "移山", "移海", "告水府", "逐瘴", "檄书", "军移", "讨逆"),
        "examples": ("讨妖檄", "羽林檄", "声罪符", "移山文", "逐瘴移文法"),
    },
    "论说辨解": {
        "fit": "破法、解析神通、格物术、破执心法、学派法宝",
        "texture": "辩理、穷源、破执；名字像一条判断，不像招式喊名",
        "tokens": ("原火", "辨龙", "解梦", "格物", "照形", "破执", "名理", "穷源", "析法", "论气"),
        "examples": ("原火简", "辨龙诀", "解梦书", "格物照形术", "破执镜"),
    },
    "诸子语体": {
        "fit": "诡辩法、道术、法家禁制、名实术、寓言法宝",
        "texture": "寓言、辩难、法术势、名实；古怪而有哲学机锋",
        "tokens": ("名实", "守雌", "齐物", "以无", "胜有", "两可", "势禁", "兼爱", "无待", "坐忘"),
        "examples": ("名实印", "守雌符", "齐物镜", "以无胜有法", "两可断形"),
    },
    "算经穷理": {
        "fit": "阵法、天机、空间法、禁制、分界法宝",
        "texture": "筹、率、方田、勾股、割圆；像老修士把天地当算题推到白头",
        "tokens": ("九章", "割圆", "方田", "坐算", "玉筹", "分界", "勾股", "衍数", "率法", "算珠"),
        "examples": ("九章玉筹", "割圆见天", "方田分界", "坐算天倾", "勾股量界法"),
    },
    "数算穷理": {
        "fit": "星盘、阵法、禁制、天机术、命数、推演法宝",
        "texture": "皓首穷经、推步星历、以数穷理；像老修士把天地当算题推到白头",
        "tokens": ("三垣", "七政", "河洛", "玄象", "太乙", "璇玑", "衍数", "律吕", "九章", "岁差"),
        "examples": ("三垣推步盘", "七政量天尺", "河洛错简", "太乙算珠", "坐算天倾", "以筹问劫"),
    },
    "历法推步": {
        "fit": "星术、命数、劫运、岁时法宝、天象推演",
        "texture": "日月星辰、岁差、节气；冷静测天，以时序断祸福",
        "tokens": ("三垣", "岁差", "七政", "推步", "定星", "移命", "节气", "璇玑", "量天", "知劫"),
        "examples": ("三垣推步盘", "岁差观天镜", "七政量天尺", "推步知劫法", "定星移命诀"),
    },
    "律吕候气": {
        "fit": "音法、气机、封禁、节候术、微妙感应法宝",
        "texture": "音律、天地气候、灰管候气；细微而精确",
        "tokens": ("黄钟", "律吕", "候气", "听灰", "知春", "吹律", "解冻", "定魂", "灰管", "宫商"),
        "examples": ("黄钟候气管", "律吕定魂", "听灰知春", "吹律解冻法", "宫商锁魄"),
    },
    "河洛象数": {
        "fit": "天机盘、阵图、卦数法、造化推演、命局法宝",
        "texture": "图、书、卦、数、造化；玄而有格局，不是随口神算",
        "tokens": ("河洛", "玄象", "错简", "铜筹", "衍数", "太乙", "问局", "藏机", "卦图", "生成"),
        "examples": ("河洛错简", "玄象铜筹", "衍数藏机", "太乙问局法", "卦图照命"),
    },
    "医书本草": {
        "fit": "疗伤法宝、毒术、脉法、药性法、救命秘术",
        "texture": "药性、脉象、毒、救命；清楚、精细，有药气和手感",
        "tokens": ("青囊", "本草", "寸关尺", "尝百草", "还魂", "解毒", "脉印", "药炉", "寒热", "针经"),
        "examples": ("青囊针", "本草还魂", "寸关尺脉印", "尝百草解毒法", "寒热辨魄"),
    },
    "丹书火候": {
        "fit": "炼丹、炼器、内丹、炉鼎法宝、火候心法",
        "texture": "炉、铅汞、龙虎、九转；关键在火候次第，不在大词",
        "tokens": ("龙虎", "火候", "铅汞", "九转", "玉液", "小炉", "还形", "丹砂", "伏火", "抽添"),
        "examples": ("龙虎火候图", "铅汞小炉", "九转灰", "玉液还形法", "伏火丹砂诀"),
    },
    "史传纪传": {
        "fit": "命籍、因果、传承、列仙谱、断命法宝",
        "texture": "人物命运、成败兴亡；像把一生写成传",
        "tokens": ("太史", "列仙", "世家", "本纪", "断命", "传牒", "金册", "命笔", "书年", "成败"),
        "examples": ("太史笔", "列仙牒", "世家金册", "本纪断命法", "命笔书年"),
    },
    "谱牒族谱": {
        "fit": "宗族法宝、血脉术、名分封锁、认祖归真法",
        "texture": "血脉、宗支、名分；温情和压迫并存",
        "tokens": ("玉牒", "玄宗", "断嗣", "认祖", "归真", "谱箓", "封名", "宗支", "血籍", "昭穆"),
        "examples": ("玉牒封名", "玄宗谱箓", "断嗣符", "认祖归真法", "昭穆血册"),
    },
    "方志地记": {
        "fit": "洞天、地域法术、地脉法宝、山川禁制、寻路法",
        "texture": "山川、郡县、物产、异闻；像地方志里夹着法术",
        "tokens": ("山川志", "洞天", "郡斋", "地肺", "藏雨", "开门", "旧图", "物产", "异闻", "县牒"),
        "examples": ("山川志", "洞天旧图", "郡斋藏雨法", "地肺开门符", "县牒锁山"),
    },
    "山海经气": {
        "fit": "妖族法宝、荒古神通、异兽法、远国奇术",
        "texture": "异兽、远国、神山、怪木；陌生、粗大、神话地理感",
        "tokens": ("烛阴", "青丘", "海外", "乘黄", "量山", "骨尺", "狐灯", "过海", "怪木", "远国"),
        "examples": ("烛阴骨尺", "青丘狐灯", "海外量山", "乘黄过海术", "怪木封天"),
    },
    "游记行纪": {
        "fit": "探洞、遁行、寻宝、远游法宝、山水试炼",
        "texture": "亲历、山水、奇境、路途；像修士亲手记下的行程",
        "tokens": ("石梁", "雪岭", "入峡", "寻源", "问洞", "行囊", "听猿", "古渡", "栈道", "溪源"),
        "examples": ("石梁记符", "雪岭行囊", "入峡听猿", "寻源问洞法", "古渡照路"),
    },
    "兵书奇正": {
        "fit": "阵法、军修、战斗法宝、兵势神通、虚实术",
        "texture": "阵、势、奇正、虚实；法名要像能排兵布阵",
        "tokens": ("握奇", "八阵", "虚实", "背水", "成阵", "奇正", "军势", "掎角", "疑兵", "阵石"),
        "examples": ("握奇符", "八阵石", "虚实旗", "背水成阵法", "奇正剑图"),
    },
    "军令边防": {
        "fit": "边塞法宝、传讯术、急报、烽燧法、关牒禁制",
        "texture": "驿骑、烽燧、关塞、急报；快、硬、有边防制度感",
        "tokens": ("烽燧", "急脚", "玉门", "夜传", "军令", "递符", "关牒", "驿骑", "边报", "符檄"),
        "examples": ("烽燧木", "急脚递符", "玉门关牒", "夜传军令术", "驿骑火符"),
    },
    "道教科仪": {
        "fit": "雷法、驱邪、召将、醮坛法宝、科仪符器",
        "texture": "章、表、符、箓、坛、醮；制度化召神驱邪",
        "tokens": ("玉枢", "三官", "步斗", "五雷", "解厄", "召雷", "役将", "醮坛", "青词", "雷章"),
        "examples": ("玉枢雷章", "三官解厄牒", "步斗召雷仪", "五雷役将印", "醮坛青词"),
    },
    "符箓云篆": {
        "fit": "符器、封禁、役鬼、驱邪、文字法宝",
        "texture": "文字即力量，形似不可读；笔画、朱文、雷书都要有作用",
        "tokens": ("云篆", "雷书", "朱文", "六丁", "断祟", "摄召", "黑符", "铁券", "符胆", "急急"),
        "examples": ("云篆黑符", "雷书铁券", "朱文断祟", "摄召六丁法", "符胆役鬼"),
    },
    "佛经题名": {
        "fit": "佛门法宝、净化术、观心法、护持法、业障消解",
        "texture": "如是、功德、净业、护持；清净庄严，不要玄幻化堆词",
        "tokens": ("净业", "无垢", "宝月", "琉璃", "观心", "净障", "护持", "功德", "莲灯", "如是"),
        "examples": ("净业瓶", "无垢灯", "宝月观心", "琉璃净障法", "莲灯护命"),
    },
    "密教仪轨": {
        "fit": "印法、火法、护身、坛城法宝、真言咒",
        "texture": "真言、明王、护摩、坛城；密、热、仪轨严整",
        "tokens": ("不动", "白伞盖", "莲华", "军荼利", "护摩", "明王", "坛城", "真言", "火印", "忿怒"),
        "examples": ("不动尊印", "白伞盖咒", "莲华护摩", "军荼利火印", "明王坛城"),
    },
    "禅宗公案": {
        "fit": "顿悟法、破妄术、心法、不可解释的神通",
        "texture": "当头棒喝、不可解释；名字像一句公案，不像功能说明",
        "tokens": ("拈花", "一喝", "无门", "来处", "断流", "照破", "棒喝", "本来", "无树", "问祖"),
        "examples": ("拈花印", "一喝断流", "无门关", "照破来处法", "本来无树灯"),
    },
    "戒律清规": {
        "fit": "禁制、宗门戒法、清净法宝、照身镜、止语术",
        "texture": "规矩、禁戒、清净；力量来自约束自身和照见犯戒",
        "tokens": ("百戒", "清规", "止语", "犯戒", "照身", "木鱼", "戒简", "净律", "斋堂", "持戒"),
        "examples": ("百戒简", "清规木鱼", "止语符", "犯戒照身镜", "净律护心"),
    },
    "唐传奇": {
        "fit": "情咒、梦法、女仙法宝、仙凡相遇、红线遁术",
        "texture": "情债、梦境、仙凡相遇；故事性强，但名字要留白",
        "tokens": ("枕中", "红线", "离魂", "霍小玉", "玉钗", "梦枕", "情债", "仙客", "前缘", "绛纱"),
        "examples": ("枕中玉", "红线遁", "离魂钗", "霍小玉灯", "梦枕还身"),
    },
    "宋元话本": {
        "fit": "江湖法宝、民间术、市井因果、公案奇遇",
        "texture": "市井、因果、公案、奇遇；像说书人口里的异术",
        "tokens": ("青灯", "瓦舍", "卖药", "错认", "前身", "断案", "听鬼", "葫芦", "勾栏", "话本"),
        "examples": ("青灯断案", "瓦舍听鬼", "卖药葫芦", "错认前身法", "勾栏照妖"),
    },
    "志怪笔记": {
        "fit": "妖修、鬼修、异物、花妖狐鬼、夜雨谈鬼",
        "texture": "狐鬼花妖，近人情；像笔记里随手记下的怪事",
        "tokens": ("狐窗", "花妖", "夜雨", "纸人", "借路", "谈鬼", "灯影", "画壁", "异物", "瓶中"),
        "examples": ("狐窗灯", "花妖镜", "夜雨谈鬼", "纸人借路术", "画壁藏身"),
    },
    "公案小说": {
        "fit": "破幻、问魂、审判法、冤魂法宝、证据术",
        "texture": "审问、证据、冤魂、铁面；名字要有升堂断案感",
        "tokens": ("乌盆", "铁面", "问尸", "三更", "升堂", "照冤", "证骨", "验魂", "断案", "公牍"),
        "examples": ("乌盆照冤", "铁面符", "问尸牒", "三更升堂法", "证骨照魂"),
    },
    "侠义小说": {
        "fit": "剑器、轻身、暗杀术、夜行法宝、暗器法",
        "texture": "夜行、义气、暗器、江湖；轻快而锋利",
        "tokens": ("红线", "夜渡", "飞檐", "袖里", "藏锋", "义胆", "暗针", "短剑", "江湖", "夜雨"),
        "examples": ("红线针", "夜渡衣", "飞檐符", "袖里藏锋法", "义胆短剑"),
    },
    "农书月令": {
        "fit": "四时法、灵田法宝、物候术、节律修行、收魂法",
        "texture": "四时、物候、耕作、天地节律；朴实但与天时紧密相连",
        "tokens": ("惊蛰", "白露", "月令", "候雁", "启户", "收魂", "铜牌", "归符", "春耕", "秋收"),
        "examples": ("惊蛰启户", "白露收魂", "月令铜牌", "候雁归符", "春耕养气法"),
    },
    "水经地理": {
        "fit": "水脉法、渡河术、地理寻龙、暗渠禁制、江河法宝",
        "texture": "江河、渡口、源流、暗渠；名字应有水路和地脉",
        "tokens": ("弱水", "三峡", "水脉", "问源", "寻龙", "渡牒", "听猿", "暗渠", "江源", "伏流"),
        "examples": ("弱水渡牒", "三峡听猿", "水脉图", "问源寻龙术", "伏流开门符"),
    },
    "茶香琴谱": {
        "fit": "清供法宝、雅事法、感官术、调心法、识鬼术",
        "texture": "茶经、香谱、琴谱的清供微感；不宜大喊大杀",
        "tokens": ("松风", "返魂香", "焦尾", "煮雪", "分茶", "听心", "香谱", "琴徽", "茶烟", "清供"),
        "examples": ("松风炉", "返魂香谱", "焦尾听心", "煮雪分茶法", "茶烟避劫"),
    },
    "棋谱局势": {
        "fit": "天机局、阵法、换命术、困敌法、因果收束",
        "texture": "局、劫、眼、势、弃子；冷静、算尽、胜负未明",
        "tokens": ("劫眼", "弃子", "收官", "锁局", "黑白", "问劫", "官子", "活眼", "棋枰", "入局"),
        "examples": ("劫眼棋枰", "弃子换命", "收官锁局", "黑白问劫法", "活眼避杀"),
    },
    "谱录品评": {
        "fit": "鉴别法宝、清赏术、灵物品第、辨香识鬼、花木法",
        "texture": "等第、清赏、鉴别；名字像雅人品物，功能藏在品评里",
        "tokens": ("照品", "清赏", "花谱", "辨香", "识鬼", "藏形", "品第", "鉴真", "香录", "物谱"),
        "examples": ("照品镜", "清赏录", "花谱藏形", "辨香识鬼术", "鉴真小印"),
    },
    "营造工匠": {
        "fit": "机关法宝、营造术、洞府禁制、尺度法、锁山法",
        "texture": "尺寸、榫卯、宫室、机关；工匠气要压过玄幻套词",
        "tokens": ("鲁班", "斗拱", "榫卯", "量殿", "成界", "锁山", "规矩", "墨线", "木经", "机关"),
        "examples": ("鲁班尺", "斗拱藏雷", "榫卯锁山", "量殿成界法", "墨线封门"),
    },
}
NAME_STYLES = tuple(NAME_STYLE_PROFILES)
NAMING_POOLS = {
    "功法": {
        "suffixes": ("功", "诀", "决", "法", "心法", "真功", "变", "化", "篇", "卷", "真解", "秘录", "金章", "典", "经"),
        "patterns": (
            "[意象]+[修炼动作]+[后缀]",
            "[来历/地名]+[天文/自然]+[真解/秘录]",
            "[数字]+[身体/魂魄]+[功/诀/变]",
            "[大道/哲学]+[极致动词]+[典/篇]",
        ),
        "avoid": "除非是宗门根本传承或顶级经文，否则优先用功、诀、真解、秘录、变、金章等。",
    },
    "秘籍": {
        "suffixes": ("篇", "卷", "残卷", "真解", "秘录", "图", "谱", "录", "赋", "问", "答"),
        "patterns": (
            "[残缺/层次]+[核心意象]+[篇/卷]",
            "[典故句式]+[问/答]",
            "[观想对象]+[图/谱/录]",
        ),
        "avoid": "秘籍可以残缺、分卷、问答、图谱化，不要全部写成完整经书。",
    },
    "法宝": {
        "suffixes": ("剑", "刀", "尺", "锥", "印", "镜", "钟", "铃", "幡", "旗", "鼎", "瓶", "炉", "塔", "舟", "珠", "盘", "图", "阵图", "甲", "罩", "囊", "翅", "莲台"),
        "patterns": (
            "[颜色/材质]+[自然/神兽]+[器型]",
            "[功能动词]+[天地/大道]+[器型]",
            "[来历/神话]+[数字/形容]+[器型]",
            "[材质/属性]+[动作/效果]+[器型]",
        ),
        "avoid": "法宝必须有具象器型。",
    },
    "法术": {
        "suffixes": ("术", "法", "咒", "禁", "诀", "印", "掌", "指", "光", "影", "遁", "火", "雷"),
        "patterns": (
            "[属性]+[动作]+[术/法/咒]",
            "[目标/效果]+[印/掌/指]",
            "[数字/方位]+[遁/禁/咒]",
        ),
        "avoid": "法术命名应短促、可施展，不要像长期功法。",
    },
    "神通": {
        "suffixes": ("神通", "大神通", "秘技", "术", "法", "掌", "指", "拳", "爪", "印", "式", "眼", "瞳", "翼", "身", "遁", "变", "化"),
        "patterns": (
            "[神兽/属性]+[动作]+[部位/式]",
            "[数字/极致]+[意象]+[神通]",
            "[哲学/气势]+[效果]+[式]",
            "[短句式典故]",
        ),
        "avoid": "神通重画面和爆发，名字通常 3-7 字，不要拖成长篇经名。",
    },
    "剑法": {
        "suffixes": ("剑诀", "剑法", "剑式", "剑招", "剑气", "剑步", "剑谱", "剑章", "剑图", "剑录", "剑阵", "剑意", "剑心诀", "剑典", "剑纲", "剑藏", "剑碑", "剑印", "剑道", "剑经"),
        "patterns": (
            "[剑路/动作]+[剑式/剑招/剑步]",
            "[来历]+[剑谱/剑图/剑章]",
            "[意象/权柄]+[剑章/剑图/剑诀/剑阵]",
            "[剑道分支]+[剑诀/剑阵/剑意]",
            "[意象]+[剑心诀/剑纲/剑藏]",
            "[极高阶]+[剑道/剑经]",
        ),
        "avoid": "剑法命名要匹配境界身份；剑经只适合高阶或根本传承。",
    },
    "百艺": {
        "suffixes": ("术", "法", "谱", "录", "图", "诀", "真解", "秘要", "手札", "工书"),
        "patterns": (
            "[百艺门类]+[技艺动作]+[谱/录/秘要]",
            "[材料/对象]+[处理动作]+[术/法]",
            "[传承来源]+[工书/手札]",
        ),
        "avoid": "百艺偏职业和工艺，不要总写成大战斗经文。",
    },
}
REALM_COMPLEXITY = {
    "练气": {"maturity": "低阶随意取用", "heavens": (1, 1), "quality": (0.35, 0.95)},
    "筑基": {"maturity": "低阶粗配成型", "heavens": (1, 2), "quality": (0.55, 1.1)},
    "金丹": {"maturity": "中阶君臣佐使", "heavens": (2, 3), "quality": (0.8, 1.45)},
    "元婴": {"maturity": "高阶纲目分明", "heavens": (2, 4), "quality": (1.0, 1.9)},
    "化神": {"maturity": "高阶近道统摄", "heavens": (3, 5), "quality": (1.25, 2.4)},
    "炼虚": {"maturity": "顶阶虚实统合", "heavens": (4, 6), "quality": (1.5, 3.0)},
    "合体": {"maturity": "顶阶身道合一", "heavens": (4, 7), "quality": (1.8, 3.6)},
    "大乘": {"maturity": "顶级铸天为一", "heavens": (5, 8), "quality": (2.2, 4.5)},
}

ROLE_COMPLEXITY = {
    "练气": {"earths": (1, 2), "humans": (1, 2)},
    "筑基": {"earths": (2, 2), "humans": (2, 2)},
    "金丹": {"earths": (2, 3), "humans": (2, 3)},
    "元婴": {"earths": (2, 3), "humans": (2, 3)},
    "化神": {"earths": (2, 4), "humans": (2, 4)},
    "炼虚": {"earths": (3, 4), "humans": (3, 4)},
    "合体": {"earths": (3, 5), "humans": (3, 5)},
    "大乘": {"earths": (3, 5), "humans": (3, 5)},
}

@dataclass(frozen=True)
class ElementDraw:
    role: str
    name: str
    category: str
    meaning: str
    refinement: str
    usable_expression: str
    skill_degree: int
    output_ceiling: int
    structure_role: str
    quality: float
    quality_label: str
    composite_branch: str | None
    skill_label: str
    output_label: str
    forced: bool
    diagnostics: tuple[str, ...]
    branch_bindings: tuple[tuple[str, str, str], ...] = ()


@dataclass(frozen=True)
class Draw:
    request: dict[str, object]
    seed: int
    random_mode: str
    kind: str
    realm: str
    rarity: str
    composition_mode: str
    theme: str | None
    maturity: str
    naming: dict[str, object]
    heavens: tuple[ElementDraw, ...]
    earths: tuple[ElementDraw, ...]
    humans: tuple[ElementDraw, ...]
    extras: tuple[ElementDraw, ...]
    conditions: tuple[str, ...]
    diagnostics: tuple[str, ...]
    prompt: str


def label(value: int) -> str:
    if value <= 20:
        return "初识"
    if value <= 40:
        return "小成"
    if value <= 60:
        return "登堂"
    if value <= 80:
        return "大成"
    if value <= 95:
        return "通玄"
    return "近道"


def quality_label(value: float) -> str:
    if value < 0.75:
        return "低质偏散"
    if value < 1.25:
        return "同阶正常"
    if value < 2.0:
        return "同阶精良"
    if value < 3.0:
        return "越阶强质"
    return "近道顶质"


HEAVEN_STRUCTURE_ROLES = (
    "核心纲领",
    "供能主源",
    "辅助供能",
    "纲位天位",
    "制衡天位",
    "纯化候选",
    "残留/借势",
)

LOW_REALMS = {"练气", "筑基"}
MID_REALMS = {"金丹", "元婴"}
HIGH_REALMS = {"化神", "炼虚", "合体", "大乘"}
LOW_REALM_OUTPUT_CAP = {"练气": 55, "筑基": 70}
LOW_REALM_QUALITY_CAP = {"练气": 0.95, "筑基": 1.1}
LOW_USABILITY_STYLES = (
    "志怪乡谈",
    "汉乐府",
    "山水田园",
    "竹枝歌谣",
    "医书本草",
    "农书月令",
    "水经地理",
    "营造工匠",
    "侠义小说",
    "元曲散曲",
    "茶香琴谱",
)
MID_USABILITY_STYLES = (
    "雅颂礼乐",
    "金文钟鼎",
    "建安风骨",
    "边塞诗",
    "晚唐苦吟",
    "祝盟誓辞",
    "符箓云篆",
    "兵书奇正",
    "方志地记",
    "谱录品评",
)
HIGH_USABILITY_STYLES = (
    "大赋都邑",
    "诏敕令",
    "山海经气",
    "道教科仪",
    "密教仪轨",
    "佛经题名",
    "河洛象数",
    "历法推步",
    "洛神神美",
    "李白豪逸",
)
HIGH_SCALE_STYLES = {"大赋都邑", "诏敕令", "山海经气", "颂赞庙堂", "密教仪轨"}


def all_elements() -> dict[str, tuple[str, str]]:
    result = dict(CUSTOM_ELEMENTS)
    for category, items in ELEMENTS.items():
        for name, meaning in items.items():
            if name not in result:
                result[name] = (category, meaning)
    return result


def parse_csv(values: Iterable[str] | None) -> list[str]:
    if not values:
        return []
    parsed: list[str] = []
    for value in values:
        parsed.extend(part.strip() for part in value.split(",") if part.strip())
    return parsed


def weighted_choice(rng: random.Random, weighted_items: Iterable[tuple[str, int]]) -> str:
    items = [(item, weight) for item, weight in weighted_items if weight > 0]
    total = sum(weight for _, weight in items)
    pick = rng.randint(1, total)
    upto = 0
    for item, weight in items:
        upto += weight
        if pick <= upto:
            return item
    return items[-1][0]


def choose_default_rarity(rng: random.Random, realm: str) -> str:
    return weighted_choice(rng, DEFAULT_RARITY_WEIGHTS[realm])


def condition_elements(conditions: tuple[str, ...]) -> tuple[str, ...]:
    text = " ".join(conditions)
    result: list[str] = []
    for key, names in CONDITION_ALIASES.items():
        if key in text:
            result.extend(names)
    return tuple(dict.fromkeys(result))


def forced_expression(name: str, refinement: str, realm: str) -> tuple[str, tuple[str, ...]]:
    if realm not in LOW_REALMS:
        return refinement, ()
    replacement = HIGH_SCALE_REFINEMENTS.get(refinement)
    if replacement:
        return replacement, (f"低境界将「{refinement}」合理化为「{replacement}」，避免越级到战略/魂魄/法则尺度。",)
    if name in HIGH_RISK_ELEMENTS:
        expression = f"低阶可承受的{refinement}"
        return expression, (f"保留用户指定或抽到的高风险要素「{name}」，但限定为{realm}可使用的浅层表达。",)
    return refinement, ()


def tune_scores_for_realm(
    role: str,
    name: str,
    realm: str,
    forced: bool,
    quality: float,
    skill_degree: int,
    output_ceiling: int,
) -> tuple[float, int, int, tuple[str, ...]]:
    diagnostics: list[str] = []
    if realm in LOW_REALMS:
        max_output = LOW_REALM_OUTPUT_CAP[realm]
        max_quality = LOW_REALM_QUALITY_CAP[realm]
        if role.startswith("天位") and quality > max_quality:
            diagnostics.append(f"{realm}默认追求小说可用率，将天位质量从 {quality:.2f} 压到 {max_quality:.2f}。")
            quality = max_quality
        if output_ceiling > max_output:
            diagnostics.append(f"{realm}出力上限不应越级，将 {output_ceiling}/100 降为 {max_output}/100。")
            output_ceiling = max_output
        if skill_degree > 80 and not forced:
            skill_degree = rng_style_value(skill_degree, 65)
    elif realm == "金丹":
        output_ceiling = min(output_ceiling, 88)
    return round(quality, 2), skill_degree, output_ceiling, tuple(diagnostics)


def rng_style_value(value: int, cap: int) -> int:
    return min(value, cap)


def make_element(
    role: str,
    name: str,
    rng: random.Random,
    realm: str,
    forced: bool = False,
    structure_role: str | None = None,
    composite_branch: str | None = None,
    quality_range: tuple[float, float] = (0.5, 1.5),
) -> ElementDraw:
    elements = all_elements()
    if name not in elements:
        known = "、".join(sorted(elements))
        raise SystemExit(f"Unknown element '{name}'. Known elements: {known}")
    category, meaning = elements[name]
    refinement = rng.choice(REFINEMENTS.get(name, (meaning,)))
    quality = round(rng.uniform(*quality_range), 2) if role.startswith("天位") else 1.0
    if role.startswith("天位"):
        base = min(95, max(10, int(25 + quality * 18)))
        skill_degree = rng.randint(max(1, base - 25), 100)
        output_ceiling = rng.randint(max(1, base - 20), 100)
    else:
        skill_degree = rng.randint(1, 100)
        output_ceiling = rng.randint(1, 100)
    chosen_composite_branch = composite_branch
    diagnostics: list[str] = []
    if role.startswith("天位") and name in CUSTOM_ELEMENTS:
        structure_role = structure_role or "道形统合"
        model = COMPOSITE_PARENT_MODELS.get(name)
        if model and chosen_composite_branch is None:
            chosen_composite_branch = rng.choice(model["branches"])
    elif role.startswith("天位"):
        structure_role = structure_role or "供能主源"
    elif role.startswith("地位"):
        structure_role = structure_role or "主承载媒介"
    elif role.startswith("人位"):
        structure_role = structure_role or "主效用"
    else:
        structure_role = structure_role or "附加牵引"
    usable_expression, expression_diagnostics = forced_expression(name, refinement, realm)
    diagnostics.extend(expression_diagnostics)
    quality, skill_degree, output_ceiling, score_diagnostics = tune_scores_for_realm(
        role, name, realm, forced, quality, skill_degree, output_ceiling
    )
    diagnostics.extend(score_diagnostics)
    return ElementDraw(
        role=role,
        name=name,
        category=category,
        meaning=meaning,
        refinement=refinement,
        usable_expression=usable_expression,
        skill_degree=skill_degree,
        output_ceiling=output_ceiling,
        structure_role=structure_role,
        quality=quality,
        quality_label=quality_label(quality) if role.startswith("天位") else "质量不适用",
        composite_branch=chosen_composite_branch,
        skill_label=label(skill_degree),
        output_label=label(output_ceiling),
        forced=forced,
        diagnostics=tuple(diagnostics),
    )


def choose_element(
    role: str,
    rng: random.Random,
    fixed: str | None,
    used: set[str],
    excluded: set[str],
    realm: str,
    structure_role: str | None = None,
    composite_branch: str | None = None,
    preferred: tuple[str, ...] = (),
    quality_range: tuple[float, float] = (0.5, 1.5),
) -> ElementDraw:
    if fixed:
        if fixed in excluded:
            raise SystemExit(f"Element '{fixed}' is excluded but was fixed as {role}.")
        used.add(fixed)
        return make_element(
            role,
            fixed,
            rng,
            realm,
            forced=True,
            structure_role=structure_role,
            composite_branch=composite_branch,
            quality_range=quality_range,
        )

    fallback_choices = [name for name in all_elements() if name not in used and name not in excluded]
    if not fallback_choices:
        raise SystemExit("No elements remain after applying exclusions.")
    preferred_set = {
        name for name in preferred if name in all_elements() and name not in used and name not in excluded
    }
    if preferred_set:
        name = weighted_choice(rng, [(choice, 4 if choice in preferred_set else 1) for choice in fallback_choices])
    else:
        name = rng.choice(fallback_choices)
    used.add(name)
    return make_element(
        role,
        name,
        rng,
        realm,
        structure_role=structure_role,
        composite_branch=composite_branch,
        quality_range=quality_range,
    )


def heaven_structure_roles(names: list[str], mode: str) -> list[str]:
    if not names:
        return []
    if len(names) == 1:
        return ["道形统合" if names[0] in CUSTOM_ELEMENTS else "供能主源"]
    roles: list[str] = []
    for index, name in enumerate(names):
        if name in CUSTOM_ELEMENTS:
            roles.append("道形统合")
        elif index == 0:
            roles.append("核心纲领")
        elif index == 1:
            roles.append("供能主源")
        elif mode == "纯化" and index == len(names) - 1:
            roles.append("纯化候选")
        elif index == len(names) - 1 and len(names) >= 4:
            roles.append("制衡天位")
        else:
            roles.append("纲位天位")
    return roles


def earth_structure_roles(count: int, mode: str) -> tuple[str, ...]:
    if count <= 0:
        return ()
    if count == 1:
        return ("主承载媒介",)
    if mode == "多媒介":
        pattern = ("主承载媒介", "传导/触发媒介", "锁定/感知媒介", "稳态/约束媒介", "代价/反噬承载")
    elif mode == "纯化":
        pattern = ("主承载媒介", "纯化候选媒介", "残留/代价媒介", "稳态/约束媒介")
    else:
        pattern = ("主承载媒介", "锁定/感知媒介", "传导/触发媒介", "稳态/约束媒介", "代价/反噬承载")
    return tuple(pattern[index] if index < len(pattern) else f"辅助媒介{index + 1}" for index in range(count))


def human_structure_roles(count: int, mode: str) -> tuple[str, ...]:
    if count <= 0:
        return ()
    if count == 1:
        return ("主效用",)
    if mode == "多目的":
        pattern = ("主效用", "索敌/识别", "约束/封锁", "收束/终局", "副效用/代价转换")
    elif mode == "纯化":
        pattern = ("主效用", "纯化候选目的", "残留副效用", "约束/封锁")
    else:
        pattern = ("主效用", "索敌/识别", "传递/扩散", "约束/封锁", "收束/终局")
    return tuple(pattern[index] if index < len(pattern) else f"辅助目的{index + 1}" for index in range(count))


def choose_many(
    role: str,
    rng: random.Random,
    fixed: list[str],
    count: int,
    used: set[str],
    excluded: set[str],
    realm: str,
    structure_roles: tuple[str | None, ...] = (),
    composite_branches: dict[str, str] | None = None,
    preferred: tuple[str, ...] = (),
    quality_range: tuple[float, float] = (0.5, 1.5),
) -> tuple[ElementDraw, ...]:
    composite_branches = composite_branches or {}
    draws: list[ElementDraw] = []
    for index, name in enumerate(fixed):
        structure_role = structure_roles[index] if index < len(structure_roles) else None
        draws.append(
            choose_element(
                role,
                rng,
                name,
                used,
                excluded,
                realm,
                structure_role,
                composite_branches.get(name),
                quality_range=quality_range,
            )
        )
    while len(draws) < count:
        index = len(draws)
        structure_role = structure_roles[index] if index < len(structure_roles) else None
        draws.append(choose_element(role, rng, None, used, excluded, realm, structure_role, None, preferred, quality_range))
    return tuple(draws)


def bind_composite_branches(
    rng: random.Random,
    realm: str,
    heavens: tuple[ElementDraw, ...],
    earths: tuple[ElementDraw, ...],
    humans: tuple[ElementDraw, ...],
    extras: tuple[ElementDraw, ...],
) -> tuple[ElementDraw, ...]:
    composite_indexes = [index for index, item in enumerate(heavens) if item.name in COMPOSITE_PARENT_MODELS]
    if not composite_indexes:
        return heavens

    rebound = list(heavens)
    for index in composite_indexes:
        parent = rebound[index]
        model = COMPOSITE_PARENT_MODELS[parent.name]
        branch_biases = model.get("branch_biases", {})
        selected = [item for item in (*heavens, *earths, *humans, *extras) if item.name != parent.name]
        selected_by_name = {item.name: item for item in selected}
        element_names = [name for name in all_elements() if name != parent.name]
        bindings: list[tuple[str, str, str]] = []
        for branch in model["branches"]:
            preferred = tuple(branch_biases.get(branch, ()))
            focused_selected_heavens = [
                name
                for name in preferred
                if name in selected_by_name and selected_by_name[name].role.startswith("天位")
            ]
            focused_selected = focused_selected_heavens or [name for name in preferred if name in selected_by_name]
            if focused_selected:
                weighted = [
                    (
                        name,
                        8
                        + (8 if selected_by_name[name].role.startswith("天位") else 0)
                        + (4 if selected_by_name[name].forced else 0),
                    )
                    for name in focused_selected
                ]
            else:
                weighted = []
                for name in element_names:
                    weight = 1
                    if name in preferred:
                        weight += 10
                    if name in selected_by_name:
                        weight += 8
                        if selected_by_name[name].role.startswith("天位"):
                            weight += 4
                    weighted.append((name, weight))
            source = weighted_choice(rng, weighted)
            if source in selected_by_name:
                expression = selected_by_name[source].usable_expression
            else:
                refinement = rng.choice(REFINEMENTS.get(source, (all_elements()[source][1],)))
                expression, _ = forced_expression(source, refinement, realm)
            bindings.append((branch, source, expression))

        rebound[index] = replace(parent, branch_bindings=tuple(bindings))
    return tuple(rebound)


def infer_theme(kind: str, conditions: tuple[str, ...], explicit: str | None) -> str | None:
    if explicit:
        return explicit
    text = " ".join(conditions)
    for theme in THEMES:
        if theme in text:
            return theme
    aliases = {
        "毒": "医毒蛊疫",
        "蛊": "医毒蛊疫",
        "梦": "魂梦心识",
        "魂": "魂梦心识",
        "阵": "阵禁界域",
        "符": "符箓契令",
        "卜": "卜筮星数",
        "星": "卜筮星数",
        "丹": "丹药食养",
        "器": "器械工巧",
    }
    for key, theme in aliases.items():
        if key in text:
            return theme
    return None


def preferred_elements(theme: str | None, conditions: tuple[str, ...]) -> tuple[str, ...]:
    names: list[str] = []
    names.extend(THEME_ELEMENTS.get(theme or "", ()))
    names.extend(condition_elements(conditions))
    return tuple(dict.fromkeys(names))


def usability_weighted_styles(
    kind: str,
    realm: str,
    rarity: str,
    theme: str | None,
) -> list[tuple[str, int]]:
    weights = {style: 1 for style in NAME_STYLES}
    if realm in LOW_REALMS:
        for style in LOW_USABILITY_STYLES:
            weights[style] = weights.get(style, 1) + 8
        for style in HIGH_SCALE_STYLES:
            weights[style] = 0 if rarity == "坊市常见" else 1
    elif realm in MID_REALMS:
        for style in MID_USABILITY_STYLES:
            weights[style] = weights.get(style, 1) + 6
        for style in LOW_USABILITY_STYLES:
            weights[style] = weights.get(style, 1) + 2
    else:
        for style in HIGH_USABILITY_STYLES:
            weights[style] = weights.get(style, 1) + 6
        for style in MID_USABILITY_STYLES:
            weights[style] = weights.get(style, 1) + 2
    if kind == "法宝":
        for style in ("营造工匠", "金文钟鼎", "谱录品评", "算经穷理", "数算穷理"):
            weights[style] = weights.get(style, 1) + 3
    if kind == "剑法":
        for style in ("建安风骨", "侠义小说", "边塞诗", "盛唐空灵", "羚羊挂角"):
            weights[style] = weights.get(style, 1) + 4
    if theme == "医毒蛊疫":
        weights["医书本草"] = weights.get("医书本草", 1) + 8
        weights["志怪乡谈"] = weights.get("志怪乡谈", 1) + 3
    if theme == "剑道":
        weights["建安风骨"] = weights.get("建安风骨", 1) + 6
        weights["侠义小说"] = weights.get("侠义小说", 1) + 4
    if kind == "剑法":
        weights["建安风骨"] = weights.get("建安风骨", 1) + 6
        weights["侠义小说"] = weights.get("侠义小说", 1) + 4
    return list(weights.items())


def naming_scale_note(style: str, realm: str, explicit: bool) -> tuple[str, ...]:
    if style in HIGH_SCALE_STYLES and realm in LOW_REALMS:
        if explicit:
            return (f"用户强制命名来源「{style}」，保留文体气质，但必须缩小为{realm}可用的小器、小术或仿古残式。",)
        return (f"命名来源「{style}」尺度偏高，已要求输出时收束为{realm}可用形制。",)
    return ()


def strip_fenced_blocks(lines: Iterable[str]) -> list[str]:
    result: list[str] = []
    in_fence = False
    for line in lines:
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            result.append(line)
    return result


def trim_repeated_blank_lines(lines: Iterable[str]) -> list[str]:
    result: list[str] = []
    previous_blank = False
    for line in lines:
        blank = not line.strip()
        if blank and previous_blank:
            continue
        result.append(line)
        previous_blank = blank
    while result and not result[0].strip():
        result.pop(0)
    while result and not result[-1].strip():
        result.pop()
    return result


def skip_maintenance_sections(label_text: str, lines: list[str]) -> list[str]:
    if label_text != "修真要素参考":
        return lines
    result: list[str] = []
    skip_until_heading = False
    for line in lines:
        if line.strip() == "选择规则：":
            skip_until_heading = True
            continue
        if skip_until_heading and line.startswith("## "):
            skip_until_heading = False
        if not skip_until_heading:
            result.append(line)
    return result


def creative_context_text(label_text: str, path: Path) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()
    if label_text == "范畴要素池":
        try:
            start = lines.index("# 范畴")
            lines = lines[start:]
        except ValueError:
            pass
    lines = skip_maintenance_sections(label_text, lines)
    lines = strip_fenced_blocks(lines)
    filtered = [
        line
        for line in lines
        if not any(pattern in line for pattern in MAINTENANCE_CONTEXT_PATTERNS)
    ]
    filtered = trim_repeated_blank_lines(filtered)
    return "\n".join(filtered)


def build_reference_context() -> str:
    lines = [
        "以下是修真百艺创作上下文。",
    ]
    for label_text, path in REFERENCE_CONTEXT_FILES:
        lines.extend(
            [
                "",
                f"===== BEGIN {label_text} =====",
                creative_context_text(label_text, path),
                f"===== END {label_text} =====",
            ]
        )
    return "\n".join(lines)


def build_prompt(draw: Draw) -> str:
    realm = REALM_CONTEXT[draw.realm]
    lines = [
        "你是一个专写修真/仙侠设定的创作代理。具备极高的古汉语文学水平和世界观架构能力充满想象力和逻辑推演能力。",
        "",
        "任务：生成一件完整的修真设定，类型为「{kind}」。".format(kind=draw.kind),
        "基调：{rarity}，适配境界：{realm}。".format(rarity=draw.rarity, realm=draw.realm),
        "组合模式：{mode}。".format(mode=draw.composition_mode),
        *([f"主题偏向：{draw.theme}。"] if draw.theme else []),
        "复合成熟度：{maturity}。".format(maturity=draw.maturity),
        (
            "生成策略：强制随机模式，未指定项按全池随机抽取；用户强制指定的参数必须保留，最终仍会被降尺度、补限制或改细分来适配境界。"
            if draw.random_mode == "force"
            else "生成策略：默认以小说中可直接使用为优先；用户强制指定的参数必须保留，但会被降尺度、补限制或改细分来适配境界。"
        ),
        "",
        "境界尺度：",
        f"- 身份地位：{realm['status']}。",
        f"- 常见寿元：{realm['lifespan']}。",
        f"- 力量尺度：{realm['scale']}。",
        f"- 作品适配：{realm['fit']}。",
        "",
        "核心模型：法门 = 天位(动力/力量来源，可多项式组合) x 地位(媒介/承载方式，可复合) x 人位(目的/作用，可多目标)。",
    ]
    if draw.diagnostics:
        lines.extend(["", "自动合理化诊断："])
        lines.extend(f"- {diagnostic}" for diagnostic in draw.diagnostics)
    if draw.earths and draw.humans:
        lines.extend(
            [
                "",
                "三位配工提示：",
                "- 多个天位、地位或人位都不是平行罗列，必须落入一个能自圆其说的构型。按各项标注的结构角色组织：地位要说明主承载、传导/触发、锁定/感知、稳态/约束或代价承载如何接力；人位要说明主效用、索敌/识别、传递/扩散、约束/封锁或收束/终局如何凝聚为一个目的链。",
                "- 若本次地位或人位只有一项，必须说明同一媒介或目的如何兼任生成、承载、锁定、传递或约束职责；若有多项，不得写成两个途径两个效果并列，必须判断主辅、先后、互补、制衡、转化或纯化关系。",
            ]
        )
    lines.extend(
        [
            "",
            "天位/动力：",
            *[format_element(item) for item in draw.heavens],
            "",
            "地位/媒介：",
            *[format_element(item) for item in draw.earths],
            "",
            "人位/目的：",
            *[format_element(item) for item in draw.humans],
        ]
    )
    parent_guides = []
    for item in draw.heavens:
        model = COMPOSITE_PARENT_MODELS.get(item.name)
        if model:
            if item.name == "剑":
                parent_guides.append(format_sword_pattern_guide(item, draw, model))
            else:
                parent_guides.append(format_composite_pattern_guide(item, model))
    if parent_guides:
        lines.extend(["", "生成用机制约束："])
        lines.extend(f"- {guide}" for guide in parent_guides)
    if draw.extras:
        lines.extend(["", "附加要素："])
        lines.extend(format_element(item) for item in draw.extras)
    if draw.conditions:
        lines.extend(["", "用户或随机附加条件："])
        lines.extend(f"- {condition}" for condition in draw.conditions)

    if draw.kind == "功法":
        lines.extend(format_cultivation_method_chain(draw))

    lines.extend(
        [
            "",
            "命名资料（只用于后段「诸名」，不要压过机制正文）：",
            f"- 文体气质：{draw.naming['style']}（{draw.naming['texture']}）",
            f"- 适合对象：{draw.naming['fit']}",
            f"- 气质词根：{'、'.join(draw.naming['tokens'])}",
            f"- 风味例子：{'、'.join(draw.naming['examples'])}",
            f"- 推荐后缀池：{'、'.join(draw.naming['suffixes'])}",
            f"- 推荐模板：{draw.naming['pattern']}",
            f"- 诸名数量：输出 {draw.naming['name_count']}；宁缺毋滥，按贴合度排序，不要称为候选，不强行定唯一正名。",
            f"- 异名语境来源池：{'；'.join(draw.naming['registers'])}",
            f"- 命名避坑：{draw.naming['avoid']}",
        ]
    )

    lines.extend(
        [
            "",
            "生成要求：",
            "- 这些要素来自扩展 PMEST 八分面：本体、属性、过程、互作、场域、时序、符号、目的；也可简称体、性、化、缘、域、时、识、愿。允许继续细分，但细分必须服务机制。",
            "- 五行是低中阶修士和百艺体系最常用的公共语法，因为它能把药性、材性、脉性、阵性、器性等偏性整理成可教学、可交易、可诊断、可配伍的生克旺衰关系；但五行不是唯一真理，也不能替代本次天位的来源、增长、衰竭、失控和度量。",
            "- 输出重心必须符合修真小说世界观设定的比重：天位动力学与复合结构约占 45%-55%，施展/效果/代价/境界约占 25%-35%，诸名约占 10%-15%，设定集正文负责收束。不要让命名解释占据开头或最长篇幅。",
            "- 先立设定总览、核心三位、天位动力学和复合结构，再写诸名。名称是世界内流传层，不是正文主结构。",
            "- 「诸名」输出三到五个，宁缺毋滥；内部先拟不少于八个草名，再淘汰标签名、机制说明名、套模板名、只换后缀名、过长题解名和删掉说明就不成立的名字。若五个里只有一个好名，宁可输出三个，不补烂名。",
            "- 「诸名」第一名必须是正文可直接使用的主名：角色能叫出口，旁白能承接，读者不用看说明也能记住。其余名字才是可信异名、俗称、讹称、题名、口令、残卷名或禁称；不要强行指定唯一正名。",
            "- 异名语境是来源池，不是配额表。不要机械逐条覆盖宗门、手札、坊市、敌人、地方志；同一批名字可以来自相近语体，只要都像真实流传过。",
            "- 每个名字后只附一句短说明，写清谁会这样叫、取法什么文体或语体、为什么贴合本设定；说明必须短于机制段落，且不能靠说明拯救一个空泛名字。只有根本传承、顶级经文或刻意古典风才使用 经。",
            "- 名字不能把天位、地位、人位和用途直接拼成标题。若读起来像用途说明、论文题目或游戏技能描述，改成器物、动作、地点、题跋、口令、工名、俗称或传闻名。",
            "- 名字超过八到十字时，必须有明确文本形制理由，例如卷名、题跋、公文、仪轨、残本、碑铭、医案或手札；否则缩短。",
            "- 名称要有文体/语体来源，像从诗、骚、乐府、骈赋、祭诔、碑铭、奏疏、诏敕、檄移、论说、算经、历法、医书、兵书、道佛科仪、志怪话本、农书水经、棋谱营造、题跋问答、行旅手札等文本里长出来，而不是古风词堆叠。每个名字体现至少一个来源、形制、功能、意象、境界、机制或流传语境。",
            "- 反对浅层掉书袋。不要只把古书词、典故词、生僻字贴在一起；要吸收文体的真实功能：诏敕有命令落下的压力，方志有地理物产和异闻口吻，医书有辨证、脉象和药性手感，题跋问答有具体人事和留白，乡谈笔记有像亲眼听来的怪事。",
            "- 至少一个名字可以尝试浅白见深：用平淡日常、行旅小记、器物记名、问答题跋、乡谈笔记或僧道手札的低姿态语气承载高阶仙意。关键是具体场景、人物关系、留白和大义隐伏，不要靠宏大词自夸。",
            "- 文体/语体来源不等于世界内来历。默认不要因为名称取法甲骨、金文、诗骚、山海经、道佛科仪或古书语气，就把作品写成上古遗物、仙古残篇、仙人真传、遗迹出土或禁忌神物；只有基调明确为「上古失传」「仙古残篇」或用户指定相关来历时，才使用这种背景。",
            "- 避免九霄、归墟、灭世、镇魔、弑神、无上、玄天、神霄这类高频玄幻词连续堆叠；除非用户指定该风格。",
            (
                "- 本次启用强制随机模式：未指定项按全池随机抽取，但凡是自动合理化诊断中写出的降尺度、浅层表达、补配限制，都必须体现在最终设定里。"
                if draw.random_mode == "force"
                else "- 默认目标是小说可用率，不是全池真随机。凡是自动合理化诊断中写出的降尺度、浅层表达、补配限制，都必须体现在最终设定里。"
            ),
            "- 用户强制指定的天/地/人、类型、境界或命名来源必须保留；如果它们与境界冲突，不得删除，只能写成误读、残式、浅层用法、旁门代价、局部小术或高阶传承的低阶入口。",
            "- 对每个天位分别解释来源、增长方式、衰竭点、失控形态和度量方法；不要把天位当作装饰词。",
            "- 天位数量与质量要匹配境界和复合成熟度：低阶可以随意选取一两个粗糙天位；中阶应有君臣佐使或主次制衡；高阶应纲目分明；顶阶才追求铸天为一、结构完美、质量顶级。",
            "- 天位质量以1.00为同境界正常水平，可高可低，不是比例上限。低质天位可能拖累结构；高质天位可以越阶支撑，但必须有代价。",
            "- 复合天位不是简单权重相加。先判断是否存在更具象、更复杂的整体道形，如剑、丹、阵、符、医、兵等；若存在，先说明各天位如何在整体中就位，而不是写成上位概念统摄子项。",
            "- 写剑修或剑法时，把生成用机制约束只用于构造机制，不要把六纲定义句、整体道形总纲或提示词解释原样写入任何输出小节，尤其不要写进设定集正文。浅层时可以写属性剑气、蓄势、勇气、道心、剑招意境、无形斩等通俗形态；深层时必须转译为具体力量运行、局势变化、承压方式、本心约束、斩击形态或自性规则。",
            "- 剑修默认比同境界普通修士更强势，且极善杀伐。剑法要体现杀伤、破防、抢先手、压迫敌方选择、越过防御资源或终结战斗的优势；不要为了平衡强行给剑法本身添加削弱。剑修的难处通常在修士侧：难练、难学、难精，极于剑时容易被剑性六纲反塑，心性、判断、行事和道途走偏锋。若本次剑法确有缺陷，必须来自抽样结构或用户条件，例如残篇、误修、低质、多天位冲突、旁门或克制关系。",
            "- 剑法命名要有境界下限：练气可用剑谱、剑式、剑招、剑步；筑基到金丹可用剑图、剑章；金丹到元婴应优先剑诀、剑阵、剑意、剑心诀。金丹剑法的主名必须有长老级秘传、镇守一方或同阶斗法的分量，不要把第一名写成弟子入门册、小队撤退术或凡俗武馆招式。",
            "- 剑性六纲中的每一纲都不是固定能力，而是一个天位槽位：剑气、剑势、剑胆、剑心、剑意、剑道都必须从已抽到或绑定的真实天位解释。尤其剑势可以是气势、局势、形势、时势、名势、权势、军势、数势、象势、蓄势等；根据绑定天位写法变化，不得默认只有一两种势。",
            "- 若剑势绑定「藏/蓄势/养势」，蓄势必须写成同级对手必须处理的危险信号：越久不破，出剑越重或越难避；不能写成单纯前摇过长、只能守固定地点、还不如不蓄势的弱点。只有绑定大势、阵禁、山门、峡道、洞府、城池等上下文时，才写成长期经营的固定杀局。",
            "- 对每个天位、地位、人位都使用给定结构角色。天位可为道形统合、核心纲领、供能主源、纲位天位、制衡天位、纯化候选；地位可为主承载、传导/触发、锁定/感知、稳态/约束、代价承载；人位可为主效用、索敌/识别、传递/扩散、约束/封锁、收束/终局。主辅只是最简单的特例，不得把所有复合结构都写成主辅权重。",
            "- 解释多天位如何在整体道形中组合：就位、相乘、相加、互补、制衡、冲突、纯化。若组合不纯，说明代价。",
            "- 若组合模式为「纯化」，必须说明哪一个天位被削弱、舍弃、上收为整体道形、下放为地位/人位或保留为残留，以及为什么这样反而更强。",
            "- 让地位成为具体媒介：身体、材料、符号、器物、仪轨、空间、梦境、数术等均可。多个地位必须组成媒介链或媒介阵列，例如一个负责承载伤害，一个负责感知锁定，一个负责传导触发，一个负责稳态约束；不能把两个地位写成两条互不相干的施法途径。",
            "- 让人位决定实际用途。多个人位必须凝聚为目的链，例如主效用负责杀伤/封印/治疗，索敌负责识别对象，约束负责边界和敌我，收束负责终局后果；不能写成两个同等独立效果并列。攻击型法术若没有明确范围攻击设定，必须说明索敌、瞄准或避开己方的机制；非攻击型法门也要说明作用对象如何被识别、触达或排除。",
            "- 匹配境界尺度但保留修士个人追求：高阶作品必须有高阶分量、资源消耗、风险或道途意义；元婴及以上可以是护宗镇城，也可以服务散修的逍遥、远遁、避劫、闭关、断因果、保命、化身经营或求道自由，不能只写成日常小便利。元婴只规定层级，不规定固定效用，具体效果必须由本次人位决定。",
            "- 说明该作品为什么适合此境界，以及低一大境界为何难以承受或完整使用，高一大境界为何可能嫌其不足或需纯化升级。",
            *(
                [
                    "- 因类型为功法，必须写功法等阶链：先写总纲，再从练气逐阶写到目标境界。每阶都要有独立修炼重心、标志性效果、配套术法或应用法门、限制代价，并说明它如何向目标境界靠拢。",
                    "- 功法等阶链要判断自身属于递进式、拆分式或先拆后合式：递进式让同类效果逐阶强化；拆分式让每阶各掌一支能力，高阶合一；先拆后合式先分修气、身、魂、器、术、势等支脉，中高阶建立君臣佐使并由整体道形收束。",
                    "- 不要把低阶只写成最高阶的弱化版。低阶应承担根基、媒介、校准、索敌、护身、蓄势、结丹准备、元婴层级铺垫等功能中的至少一种；具体职责由本次人位决定，不要默认某个境界的法门必须何种作用。",
                ]
                if draw.kind == "功法"
                else []
            ),
            "- 同时体现技艺程度与出力上限：高技艺低出力偏精细，低技艺高出力偏粗暴危险。",
            *(
                [
                    "- 给出修炼门槛、掌控难度、修士被剑性反塑的风险和至少一个适配场景；不要把这些默认写成功法本身为了平衡而自带的削弱。",
                ]
                if draw.kind == "剑法"
                else ["- 给出限制、代价、反噬和至少一个适配场景。"]
            ),
            "- 设定集正文必须像小说资料条目，不像提示词解析。不要出现任何元说明、判据名、提示词小标题、抽样诊断或世界观大纲原句；要用具体物象、动作、资源、禁忌和后果来表现。",
            "",
            "按以下结构输出：",
            "1. 设定总览（类型、境界、基调、核心用途，用一小段定调）",
            "2. 核心三位",
            "3. 天位动力学（逐天位写来源、增长、衰竭、失控、度量）",
            "4. 复合结构与纯化取舍",
            "5. 地位媒介与施展/修炼方式",
            *(
                ["6. 功法等阶链（总纲、逐阶特殊之处、配套术法、递进/拆分/合一路径）"]
                if draw.kind == "功法"
                else []
            ),
            f"{7 if draw.kind == '功法' else 6}. 人位用途与效果",
            (
                f"{8 if draw.kind == '功法' else 7}. 修炼门槛、修士风险与反噬"
                if draw.kind == "剑法"
                else f"{8 if draw.kind == '功法' else 7}. 限制、代价与反噬"
            ),
            f"{9 if draw.kind == '功法' else 8}. 境界适配与等阶差距",
            f"{10 if draw.kind == '功法' else 9}. 适配场景",
            f"{11 if draw.kind == '功法' else 10}. 诸名（输出三到五个；宁缺毋滥；第一名须可直接入正文；每个名字只附一句短说明）",
            f"{12 if draw.kind == '功法' else 11}. 设定集正文",
        ]
    )
    return "\n".join(lines)


def format_cultivation_method_chain(draw: Draw) -> list[str]:
    target_index = REALM_RANK[draw.realm]
    stages = REALMS[: target_index + 1]
    stage_lines = [f"- {stage}：{REALM_STAGE_FOCUS[stage]}" for stage in stages]
    return [
        "",
        "功法等阶链要求：",
        "- 先写总纲：说明此功法把哪些天位、地位、人位收束为同一条修行主轴，为什么各阶都属于同一部功法。",
        "- 选择结构类型：递进式、拆分式、先拆后合式三者择一或混合，但必须解释选择理由。",
        "- 逐阶写到目标境界；每阶都要有自己的特殊之处、修炼重心、配套术法或应用法门、限制代价，并说明如何向最高阶靠拢。",
        "- 低阶不能只是最高阶效果的缩水版；它们应承担根基、媒介、分支、校准、护身、索敌、蓄势、成丹、元婴层级铺垫、法域准备等不同职责。具体职责由人位决定，不要把元婴功法默认写成某个固定功能。",
        *stage_lines,
    ]


def format_element(item: ElementDraw) -> str:
    forced_text = "用户强制；" if item.forced else ""
    usable_text = f"小说可用表达：{item.usable_expression}；" if item.usable_expression != item.refinement else ""
    if item.role.startswith("天位"):
        structure_text = f"复合结构角色：{item.structure_role}；天位质量 {item.quality:.2f}「{item.quality_label}」；"
    elif item.role.startswith(("地位", "人位")):
        structure_text = f"结构角色：{item.structure_role}；"
    else:
        structure_text = f"结构角色：{item.structure_role}；" if item.structure_role != "附加牵引" else ""
    branch_text = f"本次侧重纲目：{item.composite_branch}；" if item.composite_branch else ""
    bindings_text = ""
    if item.branch_bindings:
        label_text = "六纲天位抽样" if item.name == "剑" else "分支天位抽样"
        pairs = "、".join(f"{branch}取{source}/{expression}" for branch, source, expression in item.branch_bindings)
        bindings_text = f"{label_text}：{pairs}；"
    return (
        f"- {item.role}：{item.name}（{item.category}；{item.meaning}；"
        f"本次细分：{item.refinement}；"
        f"{usable_text}"
        f"{forced_text}"
        f"{branch_text}"
        f"{bindings_text}"
        f"{structure_text}"
        f"技艺程度 {item.skill_degree}/100「{item.skill_label}」；"
        f"出力上限 {item.output_ceiling}/100「{item.output_label}」）"
    )


def sword_branch_depth(
    branch: str,
    realm: str,
    parent_quality: float,
    conditions: tuple[str, ...],
    selected_names: tuple[str, ...],
    binding: tuple[str, str] | None = None,
) -> tuple[str, str, str]:
    model = SWORD_BRANCH_MODELS[branch]
    text = " ".join((*conditions, *selected_names))
    context_hit = any(token in text for token in model["contexts"])
    realm_ready = REALM_RANK[realm] >= REALM_RANK[model["min_realm"]]
    quality_ready = parent_quality >= model["quality"]
    if realm_ready and (quality_ready or context_hit):
        interpretation = model["essence"]
        if binding:
            source, expression = binding
            if branch == "剑势":
                style = SWORD_MOMENTUM_BY_SOURCE.get(source, f"势态：以「{source}/{expression}」决定局面如何倾斜")
                interpretation = (
                    f"{interpretation} 本纲本次以「{source}/{expression}」为真实天位，具体写成{style}。"
                    "势会随交锋变化；除非绑定大势、阵禁或固定地形，不要默认写成只能守一处的杀局。"
                )
            else:
                interpretation = f"{interpretation} 本纲本次以「{source}/{expression}」为真实天位，不得只写成固定标签。"
        return "深层", interpretation, "境界、质量或天位绑定足以触及本质机制。"
    if binding:
        source, expression = binding
        if branch == "剑势":
            style = SWORD_MOMENTUM_BY_SOURCE.get(source, f"势态：以「{source}/{expression}」形成低解析度压迫")
            shallow = (
                f"{model['vulgar']}；本纲本次抽到「{source}/{expression}」，浅层写成{style}，"
                "不要脱离天位写成通用气场或固定杀局"
            )
        else:
            shallow = f"{model['vulgar']}；本纲本次抽到「{source}/{expression}」，浅层也要带出这个天位的味道"
    else:
        shallow = model["vulgar"]
    reason = []
    if not realm_ready:
        reason.append(f"未到{model['min_realm']}")
    if not quality_ready:
        reason.append(f"剑之道形质量低于{model['quality']:.2f}")
    if not context_hit:
        reason.append("缺少对应上下文牵引")
    return "浅层", shallow, "、".join(reason) + "，故暂按通俗/庸俗理解处理。"


def format_sword_pattern_guide(
    item: ElementDraw,
    draw: Draw,
    model: dict[str, object],
) -> str:
    selected_names = tuple(element.name for element in (*draw.heavens, *draw.earths, *draw.humans, *draw.extras))
    bindings = {branch: (source, expression) for branch, source, expression in item.branch_bindings}
    branch_lines = []
    for branch in model["branches"]:
        level, interpretation, reason = sword_branch_depth(
            branch,
            draw.realm,
            item.quality,
            draw.conditions,
            selected_names,
            bindings.get(branch),
        )
        branch_lines.append(f"{branch}[{level}]：{interpretation}（{reason}）")
    binding_text = ""
    if item.branch_bindings:
        binding_text = " 本次六纲天位抽样：" + "、".join(
            f"{branch}={source}/{expression}" for branch, source, expression in item.branch_bindings
        ) + "。"
    branches = "；".join(branch_lines)
    return (
        f"{model['definition']} "
        f"每一纲都必须由某个真实天位解释，不能把剑势、剑胆、剑意等当作独立固定能力，也不能写成某个上位概念下的子项。"
        f"{binding_text}"
        f"低阶、低质或缺少上下文时按浅层剑法生成，只有某纲达到境界/质量门槛或被上下文牵引时才展开深层机制。"
        f"六纲处理表：{branches}。"
    )


def format_composite_pattern_guide(
    item: ElementDraw,
    model: dict[str, object],
) -> str:
    bindings = {branch: (source, expression) for branch, source, expression in item.branch_bindings}
    branch_lines = []
    for branch in model["branches"]:
        note = model["branch_notes"][branch]
        if branch in bindings:
            source, expression = bindings[branch]
            branch_lines.append(f"{branch}={note}，本次由「{source}/{expression}」解释")
        else:
            branch_lines.append(f"{branch}={note}")
    binding_text = ""
    if item.branch_bindings:
        binding_text = " 本次分支天位抽样：" + "、".join(
            f"{branch}={source}/{expression}" for branch, source, expression in item.branch_bindings
        ) + "。"
    return (
        f"{model['definition']} "
        f"这些分支是整体道形中的功能槽位，必须由真实天位、地位或人位解释，不要写成静态目录。"
        f"{binding_text}"
        f"分支处理表：{'；'.join(branch_lines)}。"
    )


def bounded_count(rng: random.Random, bounds: tuple[int, int]) -> int:
    lower, upper = bounds
    return rng.randint(lower, upper)


def default_counts(mode: str, rng: random.Random, realm: str, kind: str) -> tuple[int, int, int]:
    realm_min, realm_max = REALM_COMPLEXITY[realm]["heavens"]
    role_complexity = ROLE_COMPLEXITY[realm]
    earth_min, earth_max = role_complexity["earths"]
    human_min, human_max = role_complexity["humans"]
    is_sword = kind == "剑法"
    sword_bonus = 1 if is_sword and realm_max > realm_min else 0

    if mode == "单纯":
        heaven = min(realm_max, realm_min + sword_bonus)
        return heaven, earth_min, human_min
    if mode == "多天位":
        lower = min(max(2, realm_min), realm_max)
        if is_sword:
            lower = min(realm_max, lower + 1)
        return rng.randint(lower, realm_max), earth_min, bounded_count(rng, (human_min, human_max))
    if mode == "多媒介":
        heaven = min(realm_max, realm_min + sword_bonus)
        return heaven, bounded_count(rng, (max(2, earth_min), earth_max)), human_min
    if mode == "多目的":
        heaven = min(realm_max, realm_min + sword_bonus)
        return heaven, earth_min, bounded_count(rng, (max(2, human_min), human_max))
    if mode == "纯化":
        lower = min(max(2, realm_min), realm_max)
        if is_sword:
            lower = min(realm_max, lower + 1)
        return rng.randint(lower, realm_max), earth_min, human_min
    heaven_lower = min(realm_max, realm_min + sword_bonus)
    return rng.randint(heaven_lower, realm_max), bounded_count(rng, (earth_min, earth_max)), bounded_count(rng, (human_min, human_max))


def build_draw(args: argparse.Namespace) -> Draw:
    seed = args.seed if args.seed is not None else time.time_ns()
    rng = random.Random(seed)
    used: set[str] = set()
    excluded = set(parse_csv(args.exclude))
    conditions = tuple(args.condition or ())
    random_mode = args.random_mode or "usable"
    if args.force_random:
        if args.random_mode == "usable":
            raise SystemExit("--random-mode usable conflicts with --force-random")
        random_mode = "force"

    kind = args.type or rng.choice(TYPES)
    realm = args.realm or rng.choice(REALMS)
    rarity = args.rarity or (rng.choice(RARITIES) if random_mode == "force" else choose_default_rarity(rng, realm))
    raw_fixed_heavens = parse_csv(args.heaven)
    fixed_heavens = list(raw_fixed_heavens)
    fixed_earths = parse_csv(args.earth)
    fixed_humans = parse_csv(args.human)
    auto_sword_added = False
    if kind == "剑法" and "剑" not in fixed_heavens:
        fixed_heavens.insert(0, "剑")
        auto_sword_added = True
    fixed_total = len(fixed_heavens) + len(fixed_earths) + len(fixed_humans)
    if args.composition_mode:
        composition_mode = args.composition_mode
    elif fixed_total == 0:
        composition_mode = rng.choice(COMPOSITION_MODES)
    elif max(len(fixed_heavens), len(fixed_earths), len(fixed_humans)) > 1 or fixed_total > 3:
        composition_mode = "复合法门"
    else:
        composition_mode = "单纯"

    complexity = REALM_COMPLEXITY[realm]
    heaven_count, earth_count, human_count = default_counts(composition_mode, rng, realm, kind)
    sword_marker_count = 1 if "剑" in fixed_heavens else 0
    fixed_non_sword_heavens = len([name for name in fixed_heavens if name != "剑"])
    requested_non_sword_heavens = max(heaven_count, fixed_non_sword_heavens, args.heaven_count or 0)
    heaven_count = requested_non_sword_heavens + sword_marker_count
    earth_count = max(earth_count, len(fixed_earths), args.earth_count or 0)
    human_count = max(human_count, len(fixed_humans), args.human_count or 0)
    theme = infer_theme(kind, conditions, args.theme)
    preferred = preferred_elements(theme, conditions)

    quality_range = complexity["quality"]
    heaven_names_for_roles = fixed_heavens + [""] * max(0, heaven_count - len(fixed_heavens))
    heaven_roles = tuple(heaven_structure_roles(heaven_names_for_roles, composition_mode))
    composite_branches = {"剑": args.sword_branch} if args.sword_branch else {}
    heavens = choose_many(
        "天位/动力",
        rng,
        fixed_heavens,
        heaven_count,
        used,
        excluded,
        realm,
        heaven_roles,
        composite_branches,
        preferred,
        quality_range,
    )
    if auto_sword_added and heavens:
        heavens = (replace(heavens[0], forced=False), *heavens[1:])
    earth_roles = earth_structure_roles(earth_count, composition_mode)
    human_roles = human_structure_roles(human_count, composition_mode)
    earths = choose_many(
        "地位/媒介",
        rng,
        fixed_earths,
        earth_count,
        used,
        excluded,
        realm,
        earth_roles,
        preferred=preferred,
    )
    humans = choose_many(
        "人位/目的",
        rng,
        fixed_humans,
        human_count,
        used,
        excluded,
        realm,
        human_roles,
        preferred=preferred,
    )

    extras: list[ElementDraw] = []
    for fixed in parse_csv(args.include):
        if fixed not in used:
            used.add(fixed)
            extras.append(make_element("附加", fixed, rng, realm, forced=True))

    for _ in range(args.extra_count):
        extras.append(choose_element("附加", rng, None, used, excluded, realm, preferred=preferred))

    heavens = bind_composite_branches(rng, realm, heavens, earths, humans, tuple(extras))

    naming = build_naming(kind, rng, realm, rarity, theme, args.name_style, random_mode)
    all_draws = (*heavens, *earths, *humans, *extras)
    diagnostics = list(naming_scale_note(str(naming["style"]), realm, args.name_style is not None))
    forced = raw_fixed_heavens + fixed_earths + fixed_humans + parse_csv(args.include)
    if forced:
        diagnostics.append(f"保留用户强制要素：{'、'.join(forced)}；其余随机项围绕这些要素合理化。")
    if random_mode == "force":
        diagnostics.append("强制随机模式：未指定项按全池随机抽取；最终仍按境界合理化。")
    elif args.rarity is None:
        diagnostics.append(f"默认稀有度按{realm}小说可用率加权抽取，避免普通低中阶作品频繁落成上古/仙古来历。")
    condition_bias = condition_elements(conditions)
    if condition_bias:
        diagnostics.append(f"用户条件已转为可用率偏置：{'、'.join(condition_bias)}。")
    diagnostics.extend(message for item in all_draws for message in item.diagnostics)
    diagnostics_tuple = tuple(dict.fromkeys(diagnostics))
    request = {
        "type": args.type,
        "random_mode": random_mode,
        "realm": args.realm,
        "rarity": args.rarity,
        "composition_mode": args.composition_mode,
        "theme": args.theme,
        "name_style": args.name_style,
        "heaven": tuple(raw_fixed_heavens),
        "earth": tuple(fixed_earths),
        "human": tuple(fixed_humans),
        "conditions": conditions,
        "include": tuple(parse_csv(args.include)),
        "exclude": tuple(parse_csv(args.exclude)),
        "extra_count": args.extra_count,
        "sword_branch": args.sword_branch,
    }

    draft = Draw(
        request=request,
        seed=seed,
        random_mode=random_mode,
        kind=kind,
        realm=realm,
        rarity=rarity,
        composition_mode=composition_mode,
        theme=theme,
        maturity=complexity["maturity"],
        naming=naming,
        heavens=heavens,
        earths=earths,
        humans=humans,
        extras=tuple(extras),
        conditions=conditions,
        diagnostics=diagnostics_tuple,
        prompt="",
    )
    return replace(draft, prompt=build_prompt(draft))


def build_naming(
    kind: str,
    rng: random.Random,
    realm: str,
    rarity: str,
    theme: str | None,
    explicit_style: str | None,
    random_mode: str,
) -> dict[str, object]:
    pool = NAMING_POOLS.get(kind, NAMING_POOLS["功法"])
    style = explicit_style or (
        rng.choice(NAME_STYLES)
        if random_mode == "force"
        else weighted_choice(rng, usability_weighted_styles(kind, realm, rarity, theme))
    )
    profile = NAME_STYLE_PROFILES[style]
    suffix_pool = list(pool["suffixes"])
    if (
        kind in {"功法", "剑法"}
        and realm not in {"化神", "炼虚", "合体", "大乘"}
        and rarity not in {"上古失传", "仙古残篇"}
    ):
        suffix_pool = [
            suffix
            for suffix in suffix_pool
            if suffix not in {"经", "剑经", "剑道", "剑纲", "剑藏"}
        ]
    if kind == "剑法":
        sword_suffixes_by_realm = {
            "练气": {"剑法", "剑式", "剑招", "剑气", "剑步", "剑谱"},
            "筑基": {"剑法", "剑诀", "剑式", "剑谱", "剑图", "剑章", "剑录"},
            "金丹": {"剑诀", "剑图", "剑章", "剑阵", "剑意", "剑心诀", "剑典"},
            "元婴": {"剑诀", "剑阵", "剑意", "剑心诀", "剑典", "剑碑", "剑印"},
            "化神": {"剑意", "剑心诀", "剑典", "剑纲", "剑碑", "剑印", "剑道", "剑经"},
            "炼虚": {"剑典", "剑纲", "剑藏", "剑碑", "剑印", "剑道", "剑经"},
            "合体": {"剑典", "剑纲", "剑藏", "剑碑", "剑印", "剑道", "剑经"},
            "大乘": {"剑纲", "剑藏", "剑碑", "剑印", "剑道", "剑经"},
        }
        suffix_pool = [suffix for suffix in suffix_pool if suffix in sword_suffixes_by_realm[realm]]
        realm_suffix_pool = list(suffix_pool)
    patterns = list(pool["patterns"])
    if kind == "剑法":
        sword_patterns_by_realm = {
            "练气": (
                "[剑路/动作]+[剑式/剑招/剑步]",
                "[意象]+[剑谱/剑法/剑气]",
            ),
            "筑基": (
                "[来历]+[剑谱/剑图/剑章]",
                "[意象/道基]+[剑图/剑章/剑诀]",
            ),
            "金丹": (
                "[意象/权柄]+[剑章/剑图/剑诀/剑阵]",
                "[镇守对象/地域]+[剑图/剑章/剑阵]",
                "[剑道分支]+[剑诀/剑阵/剑意]",
            ),
            "元婴": (
                "[神魂/法域/生存意象]+[剑诀/剑阵/剑意]",
                "[剑道分支]+[剑诀/剑阵/剑心诀]",
                "[来历/高阶威慑]+[剑典/剑碑/剑印]",
            ),
            "化神": (
                "[法则/道痕]+[剑意/剑心诀/剑典]",
                "[领域/威权]+[剑纲/剑碑/剑印]",
            ),
            "炼虚": (
                "[虚空/界域]+[剑典/剑纲/剑藏]",
                "[法则缝隙]+[剑碑/剑印/剑道]",
            ),
            "合体": (
                "[身道合一]+[剑纲/剑藏/剑道]",
                "[族运/宗运]+[剑碑/剑印/剑经]",
            ),
            "大乘": (
                "[飞升/天劫/镇界]+[剑纲/剑藏/剑道]",
                "[近道遗刻]+[剑碑/剑印/剑经]",
            ),
        }
        patterns = list(sword_patterns_by_realm[realm])
    if kind == "功法" and realm in LOW_REALMS:
        patterns = [pattern for pattern in patterns if "大道/哲学" not in pattern]
    style_suffix_bias = {
        "诗经国风": {"筐", "铃", "符", "束", "简", "环", "索", "鼓", "镰", "佩", "笛", "法"},
        "祭文悲怆": {"匣", "印", "砚", "符", "铃", "券", "仪", "咒", "法", "碑", "简"},
        "盛唐空灵": {"杯", "簪", "环", "鉴", "履", "珠", "剑", "弦", "简", "影", "遁", "身"},
        "羚羊挂角": {"杯", "簪", "环", "鉴", "履", "珠", "剑", "弦", "简", "影", "遁", "身"},
        "洛神神美": {"佩", "罗", "纱", "珰", "袜", "璧", "带", "镜", "灯", "玉", "身", "影"},
        "算经穷理": {"盘", "尺", "简", "筹", "珠", "仪", "图", "管", "镜", "术", "法"},
        "数算穷理": {"盘", "尺", "简", "筹", "珠", "仪", "图", "管", "镜", "术", "法"},
        "历法推步": {"盘", "尺", "简", "筹", "珠", "仪", "图", "管", "镜", "术", "法"},
        "律吕候气": {"管", "钟", "铃", "磬", "尺", "图", "法", "术", "诀"},
        "河洛象数": {"盘", "图", "简", "筹", "珠", "镜", "术", "法", "诀"},
        "诗经粗纯": {"筐", "铃", "符", "束", "简", "环", "索", "鼓", "镰", "佩", "笛", "法"},
    }
    public_writing_styles = {
        "表章陈情",
        "奏疏议",
        "策问对策",
        "诏敕令",
        "檄移公文",
        "论说辨解",
        "史传纪传",
        "谱牒族谱",
        "方志地记",
        "游记行纪",
        "军令边防",
    }
    ritual_styles = {
        "雅颂礼乐",
        "甲骨卜辞",
        "金文钟鼎",
        "祝盟誓辞",
        "墓志碑铭",
        "铭箴戒",
        "颂赞庙堂",
        "道教科仪",
        "符箓云篆",
        "佛经题名",
        "密教仪轨",
        "戒律清规",
    }
    craft_styles = {
        "医书本草",
        "丹书火候",
        "农书月令",
        "水经地理",
        "茶香琴谱",
        "棋谱局势",
        "谱录品评",
        "营造工匠",
    }
    fallback_bias: set[str] = set()
    if style in public_writing_styles:
        fallback_bias = {"书", "牒", "章", "符", "令", "策", "议", "疏", "录", "图", "法", "术", "印"}
    elif style in ritual_styles:
        fallback_bias = {"符", "箓", "印", "牒", "章", "简", "碑", "铭", "灯", "瓶", "法", "咒", "仪"}
    elif style in craft_styles:
        fallback_bias = {"图", "谱", "录", "尺", "针", "炉", "盘", "镜", "法", "术", "诀", "手札", "工书"}
    elif style in {"楚辞骚体", "六朝骈文", "晚唐绮艳", "婉约词"}:
        fallback_bias = {"佩", "罗", "纱", "镜", "灯", "影", "咒", "法", "术", "遁", "身"}
    elif style in {"建安风骨", "边塞诗", "岑参奇伟", "高适沉雄", "豪放词", "兵书奇正"}:
        fallback_bias = {"剑", "刀", "印", "旗", "符", "牒", "图", "阵图", "法", "术", "诀", "式"}
    elif style in {"志怪乡谈", "元曲散曲", "谣谚童谣", "唐传奇", "宋元话本", "志怪笔记", "公案小说", "侠义小说"}:
        fallback_bias = {"灯", "镜", "符", "钗", "针", "衣", "葫芦", "牒", "法", "术", "咒", "遁"}
    biased_suffixes = [suffix for suffix in suffix_pool if suffix in style_suffix_bias.get(style, fallback_bias)]
    if biased_suffixes:
        suffix_pool = biased_suffixes
    elif kind == "剑法":
        suffix_pool = realm_suffix_pool
    suffixes = tuple(rng.sample(suffix_pool, k=min(8, len(suffix_pool))))
    registers = [
        "宗门玉册或谱录中的题名，重制度、传承和等阶",
        "修士手札、题跋或行旅小记里的私称，重亲历、具体场景和留白",
        "坊市、弟子或散修口耳相传的俗称，短促好记，便于小说中使用",
        "敌人、受术者或旁观者给出的畏称，重后果、压迫感和误读",
        "后世评话、地方志或志怪笔记中的异名，重故事、地理和传闻",
    ]
    if kind == "法宝":
        registers.insert(1, "器主、炼器师或旧藏目录里的器名，重形制、材料和器物手感")
    elif kind in {"法术", "神通", "剑法"}:
        registers.insert(1, "施展时的口令、招式名或战场短称，重动作、声势和临场识别")
    elif kind in {"功法", "秘籍"}:
        registers.insert(1, "卷首、分篇、残本或授徒时使用的篇名，重修炼路径和文本形态")
    elif kind == "百艺":
        registers.insert(1, "匠人、医家、丹师或阵师操作时使用的工名，重步骤和手艺触感")
    if style in public_writing_styles:
        registers.append("章表、公文、方志或史传中的记录名，重制度、地理和事功")
    elif style in ritual_styles:
        registers.append("科仪、祭告、符箓或清规中的仪式名，重生效条件和禁忌")
    elif style in craft_styles:
        registers.append("工书、医案、谱录或月令中的操作名，重物候、尺度和辨证")
    avoid = pool["avoid"]
    if kind == "剑法":
        sword_realm_notes = {
            "练气": "练气剑法可以用剑谱、剑式、剑招、剑步，读感应像弟子能练的入门或实用小册。",
            "筑基": "筑基剑法开始有道基和图式，主名优先剑图、剑章，也可保留剑谱作宗门图谱而非凡俗小册。",
            "金丹": "金丹剑法应有长老级门槛和镇守一方的分量，主名优先剑图、剑章、剑诀、剑阵；避免剑谱、剑招、剑步作第一主名，除非明确写成低阶残本或外门误称。",
            "元婴": "元婴剑法应进入神魂、法域、远遁、生存或高阶威慑尺度，主名优先剑诀、剑阵、剑意、剑心诀、剑典。",
        }
        avoid = f"{avoid} {sword_realm_notes.get(realm, '高阶剑法才可使用剑纲、剑藏、剑碑、剑印、剑道、剑经等近道形制。')}"
        if REALM_RANK[realm] >= REALM_RANK["金丹"]:
            avoid = (
                f"{avoid} 金丹及以上不要用“断后”这类掩护撤退、小队战术读感的词作主名；"
                "若要表达截断，应写成断路、截势、截焰、定劫、镇关、锁江等能体现同阶斗法或镇守权柄的动作。"
            )
    return {
        "style": style,
        "fit": profile["fit"],
        "texture": profile["texture"],
        "tokens": tuple(rng.sample(profile["tokens"], k=min(6, len(profile["tokens"])))),
        "examples": tuple(rng.sample(profile["examples"], k=min(4, len(profile["examples"])))),
        "suffixes": suffixes,
        "pattern": rng.choice(patterns or list(pool["patterns"])),
        "name_count": "3-5 个",
        "registers": tuple(dict.fromkeys(registers[:6])),
        "avoid": avoid,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a xiuzhen art prompt from constrained random dimensions."
    )
    parser.add_argument("--type", choices=TYPES, help="Target output type.")
    parser.add_argument("--seed", type=int, help="Random seed for reproducibility.")
    parser.add_argument("--heaven", action="append", help="Fixed 天位 element. Repeat or comma-separate.")
    parser.add_argument("--earth", action="append", help="Fixed 地位 element. Repeat or comma-separate.")
    parser.add_argument("--human", action="append", help="Fixed 人位 element. Repeat or comma-separate.")
    parser.add_argument("--heaven-count", type=int, help="Minimum number of 天位 elements.")
    parser.add_argument("--earth-count", type=int, help="Minimum number of 地位 elements.")
    parser.add_argument("--human-count", type=int, help="Minimum number of 人位 elements.")
    parser.add_argument("--composition-mode", choices=COMPOSITION_MODES, help="How multiple elements should combine.")
    parser.add_argument("--sword-branch", choices=SWORD_BRANCHES, help="Required focus branch for the 剑 composite heaven, such as 剑意.")
    parser.add_argument("--theme", choices=THEMES, help="Preferred xiuzhen art family/theme.")
    parser.add_argument("--name-style", choices=NAME_STYLES, help="Literary naming style.")
    parser.add_argument("--random-mode", choices=RANDOM_MODES, help="Random strategy for unspecified fields.")
    parser.add_argument("--force-random", action="store_true", help="Shortcut for --random-mode force.")
    parser.add_argument("--realm", choices=REALMS, help="Target cultivation realm.")
    parser.add_argument("--rarity", choices=RARITIES, help="Rarity or provenance.")
    parser.add_argument("--condition", action="append", help="Additional user condition.")
    parser.add_argument("--include", action="append", help="Comma-separated required extra elements.")
    parser.add_argument("--exclude", action="append", help="Comma-separated excluded elements.")
    parser.add_argument("--extra-count", type=int, default=0, help="Number of random extra elements.")
    parser.add_argument(
        "--continue",
        "--omit-context",
        dest="continuation",
        action="store_true",
        help="Continuation mode: omit bundled reference Markdown already present in the conversation.",
    )
    parser.add_argument("--json", action="store_true", help="Debug/integration only: output machine-readable JSON instead of the creative prompt.")
    args = parser.parse_args()

    if args.extra_count < 0:
        raise SystemExit("--extra-count must be >= 0")

    draw = build_draw(args)
    if args.json:
        payload = asdict(draw)
        payload["effective"] = {
            "type": draw.kind,
            "random_mode": draw.random_mode,
            "realm": draw.realm,
            "rarity": draw.rarity,
            "composition_mode": draw.composition_mode,
            "theme": draw.theme,
            "naming_style": draw.naming["style"],
            "heavens": [item.name for item in draw.heavens],
            "earths": [item.name for item in draw.earths],
            "humans": [item.name for item in draw.humans],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    print(f"Seed: {draw.seed}")
    print()
    if args.continuation:
        print("接着生成模式：已省略创作上下文包；沿用本会话此前生成器输出过的修真百艺参考上下文。")
        print()
    else:
        print(build_reference_context())
        print()
    print("===== BEGIN generated-request =====")
    print(textwrap.dedent(draw.prompt).strip())
    print("===== END generated-request =====")


if __name__ == "__main__":
    main()
