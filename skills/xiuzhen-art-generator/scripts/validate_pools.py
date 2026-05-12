#!/usr/bin/env python3
"""Validate xiuzhen pool text data."""

from __future__ import annotations

from pathlib import Path

from pool_parser import parse_pool_file


ROOT = Path(__file__).resolve().parents[1]
POOL_PATH = ROOT / "data" / "pools.md"
REQUIRED_FACETS = ("本体", "属性", "过程", "互作", "场域", "时序", "符号", "目的")


def validate_refs(label: str, refs: tuple[str, ...], known: set[str]) -> None:
    missing = [name for name in refs if name not in known]
    if missing:
        raise SystemExit(f"{label} references unknown elements: {', '.join(missing)}")


def main() -> None:
    data = parse_pool_file(POOL_PATH)

    facets = data["facets"]
    elements = data["elements"]
    missing = [facet for facet in REQUIRED_FACETS if facet not in facets or facet not in elements]
    if missing:
        raise SystemExit(f"pools.md missing required facets: {', '.join(missing)}")

    known: set[str] = set()
    for facet, items in elements.items():
        if not items:
            raise SystemExit(f"Facet {facet} has no elements.")
        for name, meaning in items.items():
            if not meaning:
                raise SystemExit(f"Element {facet}.{name} needs a meaning.")
            refs = data["refinements"].get(name, ())
            if not refs:
                raise SystemExit(f"Element {facet}.{name} needs at least one refinement.")
            known.add(name)

    known.update(data["custom_elements"])

    validate_refs("risk.high_elements", tuple(data["high_risk_elements"]), known)

    for theme, refs in data["theme_elements"].items():
        validate_refs(f"theme {theme}", refs, known)

    for alias, refs in data["condition_aliases"].items():
        validate_refs(f"condition {alias}", refs, known)

    for branch, refs in data["sword_branch_focus"].items():
        validate_refs(f"sword branch {branch}", refs, known)

    for name, model in data["composite_parent_models"].items():
        branches = tuple(model.get("branches", ()))
        if not branches:
            raise SystemExit(f"Composite {name} must define branches.")
        notes = model.get("branch_notes", {})
        missing_notes = [branch for branch in branches if branch not in notes]
        if missing_notes:
            raise SystemExit(f"Composite {name} missing branch notes: {', '.join(missing_notes)}")
        biases = model.get("branch_biases", {})
        missing_biases = [branch for branch in branches if branch not in biases]
        if missing_biases:
            raise SystemExit(f"Composite {name} missing branch biases: {', '.join(missing_biases)}")
        extra_biases = [branch for branch in biases if branch not in branches]
        if extra_biases:
            raise SystemExit(f"Composite {name} has unknown branch biases: {', '.join(extra_biases)}")
        for branch, refs in biases.items():
            validate_refs(f"composite {name}.{branch}", tuple(refs), known)

    for branch, model in data["sword_branch_models"].items():
        for key in ("vulgar", "essence", "min_realm", "quality", "contexts"):
            if key not in model or model[key] in ("", ()):
                raise SystemExit(f"Sword branch model {branch} missing {key}.")

    print("Pool text is valid.")


if __name__ == "__main__":
    main()
