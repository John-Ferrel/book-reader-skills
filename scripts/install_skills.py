#!/usr/bin/env python3
"""Install Book Reader skill packages into agent-compatible skill directories."""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path


TARGETS = ("opencode-global", "opencode-project", "agents-global", "agents-project")
MODES = ("copy", "symlink")
SKILL_NAME_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


@dataclass(frozen=True)
class SkillPackage:
    name: str
    path: Path


@dataclass(frozen=True)
class InstallResult:
    installed: int
    skipped: int
    target_directory: Path
    messages: tuple[str, ...]


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[1]


def discover_skills(repo_root: Path) -> list[SkillPackage]:
    """Return skill packages discovered from skills/**/SKILL.md.

    Lens skills are intentionally flattened at install time by using the skill
    directory basename as the installed package name.
    """
    skills_root = repo_root / "skills"
    if not skills_root.is_dir():
        raise ValueError(f"skills directory not found: {skills_root}")

    packages: list[SkillPackage] = []
    seen: dict[str, Path] = {}
    for skill_file in sorted(skills_root.glob("**/SKILL.md")):
        package_path = skill_file.parent.resolve()
        name = package_path.name
        if name in seen:
            raise ValueError(f"duplicate skill name {name!r}: {seen[name]} and {package_path}")
        skill = SkillPackage(name=name, path=package_path)
        validate_skill_package(skill)
        seen[name] = package_path
        packages.append(skill)
    return packages


def parse_skill_frontmatter(skill_file: Path) -> dict[str, str]:
    if skill_file.name != "SKILL.md":
        raise ValueError(f"{skill_file}: skill file must be named SKILL.md")
    if not skill_file.is_file():
        raise ValueError(f"{skill_file}: SKILL.md not found")

    lines = skill_file.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        raise ValueError(f"{skill_file}: SKILL.md must start with YAML frontmatter")

    metadata: dict[str, str] = {}
    closing_index: int | None = None
    for index, line in enumerate(lines[1:], start=1):
        if line == "---":
            closing_index = index
            break
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"{skill_file}: invalid frontmatter line: {line!r}")
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip().strip("'\"")

    if closing_index is None:
        raise ValueError(f"{skill_file}: YAML frontmatter is not closed")
    return metadata


def validate_skill_package(skill: SkillPackage) -> None:
    skill_file = skill.path / "SKILL.md"
    metadata = parse_skill_frontmatter(skill_file)

    for field in ("name", "description"):
        if field not in metadata:
            raise ValueError(f"{skill_file}: missing required frontmatter field {field!r}")

    frontmatter_name = metadata["name"]
    description = metadata["description"]
    if not SKILL_NAME_PATTERN.fullmatch(frontmatter_name):
        raise ValueError(f"{skill_file}: invalid skill name {frontmatter_name!r}")
    if len(frontmatter_name) > 64:
        raise ValueError(f"{skill_file}: skill name must be 64 characters or fewer")
    if frontmatter_name != skill.name:
        raise ValueError(
            f"{skill_file}: frontmatter name {frontmatter_name!r} does not match install name {skill.name!r}"
        )
    if not description.strip():
        raise ValueError(f"{skill_file}: description must be non-empty")
    if len(description) > 1024:
        raise ValueError(f"{skill_file}: description must be 1024 characters or fewer")


def validate_skill_packages(skills: list[SkillPackage]) -> None:
    for skill in skills:
        validate_skill_package(skill)


def resolve_target_directory(target: str, project: Path | None = None) -> Path:
    if target == "opencode-global":
        return Path.home() / ".config" / "opencode" / "skills"
    if target == "agents-global":
        return Path.home() / ".agents" / "skills"
    if target == "opencode-project":
        if project is None:
            raise ValueError("--project is required for opencode-project")
        return project / ".opencode" / "skills"
    if target == "agents-project":
        if project is None:
            raise ValueError("--project is required for agents-project")
        return project / ".agents" / "skills"
    raise ValueError(f"unsupported target: {target}")


def install_skills(
    skills: list[SkillPackage],
    target_directory: Path,
    *,
    mode: str = "copy",
    force: bool = False,
    dry_run: bool = False,
) -> InstallResult:
    if mode not in MODES:
        raise ValueError(f"unsupported mode: {mode}")
    validate_skill_packages(skills)

    messages: list[str] = []
    installed = 0
    skipped = 0
    target_directory = target_directory.expanduser().resolve()

    if dry_run:
        messages.append(f"DRY RUN: target directory: {target_directory}")
    else:
        target_directory.mkdir(parents=True, exist_ok=True)

    for skill in skills:
        destination = target_directory / skill.name
        if destination.exists() or destination.is_symlink():
            if not force:
                skipped += 1
                messages.append(f"SKIP existing {destination} (use --force to overwrite)")
                continue
            if dry_run:
                messages.append(f"WOULD overwrite {destination}")
            else:
                remove_existing(destination)

        if dry_run:
            action = "symlink" if mode == "symlink" else "copy"
            messages.append(f"WOULD {action} {skill.path} -> {destination}")
            installed += 1
            continue

        if mode == "copy":
            shutil.copytree(skill.path, destination, ignore=copy_ignore)
        else:
            destination.symlink_to(skill.path, target_is_directory=True)
        messages.append(f"INSTALLED {skill.name}: {skill.path} -> {destination}")
        installed += 1

    return InstallResult(
        installed=installed,
        skipped=skipped,
        target_directory=target_directory,
        messages=tuple(messages),
    )


def copy_ignore(directory: str, names: list[str]) -> set[str]:
    ignored = {"__pycache__", ".pytest_cache"}
    ignored.update(name for name in names if name.endswith((".pyc", ".pyo", ".pyd")))
    return ignored


def remove_existing(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)
    else:
        raise ValueError(f"cannot remove unsupported existing path: {path}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Install Book Reader skills into agent-compatible skill directories.")
    parser.add_argument("--target", choices=TARGETS, required=True)
    parser.add_argument("--project", type=Path, help="Project path for project-local targets.")
    parser.add_argument("--mode", choices=MODES, default="copy")
    parser.add_argument("--force", action="store_true", help="Overwrite existing installed skill directories.")
    parser.add_argument("--dry-run", action="store_true", help="Print planned installation without writing.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        repo_root = repo_root_from_script()
        target_directory = resolve_target_directory(args.target, args.project)
        skills = discover_skills(repo_root)
        result = install_skills(
            skills,
            target_directory,
            mode=args.mode,
            force=args.force,
            dry_run=args.dry_run,
        )
    except Exception as error:
        print(f"install failed: {error}", file=sys.stderr)
        return 2

    for message in result.messages:
        print(message)
    print(f"skills discovered: {len(skills)}")
    print(f"installed/planned: {result.installed}")
    print(f"skipped: {result.skipped}")
    print(f"target: {result.target_directory}")
    if result.skipped and not args.force and not args.dry_run:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
