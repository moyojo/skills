#!/usr/bin/env python3
"""Parse the compact xiuzhen pool text format."""

from __future__ import annotations

from pathlib import Path
from typing import Any


FACET_ALIASES = {
    "本体": "体",
    "属性": "性",
    "过程": "化",
    "互作": "缘",
    "场域": "域",
    "时序": "时",
    "符号": "识",
    "目的": "愿",
}


def split_values(text: str) -> tuple[str, ...]:
    return tuple(part.strip() for part in text.split("、") if part.strip())


def split_field(text: str) -> tuple[str, str]:
    if "：" not in text:
        raise ValueError(f"Expected full-width colon in line: {text}")
    key, value = text.split("：", 1)
    return key.strip(), value.strip()


def parse_heading(line: str) -> tuple[int, str]:
    level = len(line) - len(line.lstrip("#"))
    return level, line[level:].strip()


def parse_facet_heading(text: str) -> tuple[str, str, str]:
    name_part, description = split_field(text)
    if "（" in name_part and name_part.endswith("）"):
        name, short = name_part[:-1].split("（", 1)
    else:
        name = name_part
        short = FACET_ALIASES.get(name_part, name_part)
    return name.strip(), short.strip(), description


def parse_element_line(line: str) -> tuple[str, str, tuple[str, ...]]:
    name, body = split_field(line[2:].strip())
    if "｜" in body:
        meaning, refinements = body.split("｜", 1)
        return name, meaning.strip(), split_values(refinements)
    return name, body.strip(), ()


def parse_note_map(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for item in (part.strip() for part in text.split("；") if part.strip()):
        if "=" not in item:
            continue
        key, value = item.split("=", 1)
        result[key.strip()] = value.strip()
    return result


def parse_bias_map(text: str) -> dict[str, tuple[str, ...]]:
    result: dict[str, tuple[str, ...]] = {}
    for item in (part.strip() for part in text.split("；") if part.strip()):
        if "=" not in item:
            continue
        key, value = item.split("=", 1)
        result[key.strip()] = split_values(value)
    return result


def parse_pool_file(path: Path) -> dict[str, Any]:
    current_section = ""
    current_subsection = ""
    current_facet = ""
    current_theme = ""
    current_composite = ""
    current_branch = ""
    in_replacements = False
    in_momentum_sources = False

    facets: dict[str, dict[str, str]] = {}
    elements: dict[str, dict[str, str]] = {}
    refinements: dict[str, tuple[str, ...]] = {}
    themes: dict[str, dict[str, tuple[str, ...]]] = {}
    condition_aliases: dict[str, tuple[str, ...]] = {}
    high_risk_elements: set[str] = set()
    high_scale_refinements: dict[str, str] = {}
    custom_elements: dict[str, tuple[str, str]] = {}
    composite_parent_models: dict[str, dict[str, Any]] = {}
    sword_branch_models: dict[str, dict[str, Any]] = {}
    sword_branch_focus: dict[str, tuple[str, ...]] = {}
    sword_momentum_by_source: dict[str, str] = {}
    sword_momentum_storage_contexts: tuple[str, ...] = ()
    sword_momentum_fixed_contexts: tuple[str, ...] = ()
    sword_momentum_borrow_contexts: tuple[str, ...] = ()

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("#"):
            level, title = parse_heading(line)
            in_replacements = False
            in_momentum_sources = False
            if level == 1:
                current_section = title
                current_subsection = ""
                continue
            if level == 2:
                current_subsection = title
                if current_section == "范畴":
                    name, short, description = parse_facet_heading(title)
                    current_facet = name
                    facets[name] = {"alias": short, "description": description}
                    elements.setdefault(name, {})
                elif current_section == "主题":
                    current_theme = title
                    themes.setdefault(title, {"elements": (), "arts": ()})
                elif current_section == "复合":
                    current_composite = title
                    composite_parent_models.setdefault(title, {"branch_notes": {}, "branch_biases": {}})
                elif current_section == "剑分支模型":
                    current_branch = title
                    sword_branch_models.setdefault(title, {})
                continue

        if current_section == "范畴" and line.startswith("- "):
            name, meaning, refs = parse_element_line(line)
            elements[current_facet][name] = meaning
            refinements[name] = refs or (meaning,)
            continue

        if current_section == "风险":
            if line.startswith("- 高风险："):
                _, values = split_field(line[2:].strip())
                high_risk_elements.update(split_values(values))
                continue
            if line.startswith("- 低阶替代表达"):
                in_replacements = True
                continue
            if in_replacements and line.startswith("- "):
                key, value = split_field(line[2:].strip())
                high_scale_refinements[key] = value
                continue

        if current_section == "主题":
            key, value = split_field(line)
            if key == "要素":
                themes[current_theme]["elements"] = split_values(value)
            elif key == "子艺":
                themes[current_theme]["arts"] = split_values(value)
            continue

        if current_section == "条件" and line.startswith("- "):
            key, value = split_field(line[2:].strip())
            condition_aliases[key] = split_values(value)
            continue

        if current_section == "复合":
            key, value = split_field(line)
            if key == "类别":
                category = value
                meaning = custom_elements.get(current_composite, ("复合", ""))[1]
                custom_elements[current_composite] = (category, meaning)
            elif key == "释义":
                category = custom_elements.get(current_composite, ("复合", ""))[0]
                custom_elements[current_composite] = (category, value)
            elif key == "定义":
                composite_parent_models[current_composite]["definition"] = value
            elif key == "分支":
                branches = split_values(value)
                composite_parent_models[current_composite]["branches"] = branches
                refinements[current_composite] = branches
            elif key == "分支说明":
                composite_parent_models[current_composite]["branch_notes"] = parse_note_map(value)
            elif key == "分支偏置":
                biases = parse_bias_map(value)
                composite_parent_models[current_composite]["branch_biases"] = biases
                if current_composite == "剑":
                    sword_branch_focus.update(biases)
            continue

        if current_section == "剑分支模型":
            key, value = split_field(line)
            model = sword_branch_models[current_branch]
            if key == "浅层":
                model["vulgar"] = value
            elif key == "深层":
                model["essence"] = value
            elif key == "最低境界":
                model["min_realm"] = value
            elif key == "质量":
                model["quality"] = float(value)
            elif key == "上下文":
                model["contexts"] = split_values(value)
            continue

        if current_section == "剑分支偏置" and line.startswith("- "):
            key, value = split_field(line[2:].strip())
            sword_branch_focus[key] = split_values(value)
            continue

        if current_section == "剑势":
            if line == "势源：":
                in_momentum_sources = True
                continue
            if in_momentum_sources and line.startswith("- "):
                key, value = split_field(line[2:].strip())
                sword_momentum_by_source[key] = value
                continue
            key, value = split_field(line)
            if key == "蓄势上下文":
                sword_momentum_storage_contexts = split_values(value)
            elif key == "固定杀局上下文":
                sword_momentum_fixed_contexts = split_values(value)
            elif key == "借势上下文":
                sword_momentum_borrow_contexts = split_values(value)

    return {
        "facets": facets,
        "elements": elements,
        "refinements": refinements,
        "themes": tuple(themes),
        "theme_elements": {name: spec["elements"] for name, spec in themes.items()},
        "theme_arts": {name: spec["arts"] for name, spec in themes.items()},
        "condition_aliases": condition_aliases,
        "custom_elements": custom_elements,
        "composite_parent_models": composite_parent_models,
        "sword_branch_models": sword_branch_models,
        "sword_branch_focus": sword_branch_focus,
        "sword_momentum_storage_contexts": sword_momentum_storage_contexts,
        "sword_momentum_fixed_contexts": sword_momentum_fixed_contexts,
        "sword_momentum_borrow_contexts": sword_momentum_borrow_contexts,
        "sword_momentum_by_source": sword_momentum_by_source,
        "high_scale_refinements": high_scale_refinements,
        "high_risk_elements": high_risk_elements,
    }
