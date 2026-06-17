#!/usr/bin/env python3
"""Validate published skills for the local skill archive layout."""

import re
import sys
from math import ceil
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Set, Tuple


ROOT_DIR = Path(__file__).resolve().parent
SKILLS_DIR = ROOT_DIR / "skills"
REQUIRED_FRONTMATTER_KEYS = ("name", "description", "license")
REQUIRED_OPENAI_INTERFACE_KEYS = (
    "display_name",
    "short_description",
    "default_prompt",
)
VALID_LICENSES = {"MIT"}
NAME_PATTERN = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$|^[a-z0-9]$")
MARKDOWN_LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
DESCRIPTION_USE_PATTERN = re.compile(r"\bUse\b.*\b(when|whenever)\b", re.IGNORECASE)
BODY_MAX_LINES = 500
BODY_MAX_TOKENS = 5000

try:
    import tiktoken  # type: ignore
except ImportError:
    tiktoken = None


def iter_skill_dirs() -> Iterator[Path]:
    if not SKILLS_DIR.is_dir():
        return

    for path in sorted(SKILLS_DIR.iterdir()):
        if not path.is_dir():
            continue
        if path.name.startswith(".") or path.name == "__pycache__":
            continue
        if not (path / "SKILL.md").is_file():
            continue
        yield path


def strip_quotes(value):
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    return value


def parse_frontmatter(skill_file: Path) -> Dict[str, str]:
    text = skill_file.read_text(encoding="utf-8")
    lines = text.splitlines()

    if not lines or lines[0].strip() != "---":
        raise ValueError("SKILL.md must start with a frontmatter block delimited by ---")

    end = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            end = index
            break
    if end is None:
        raise ValueError("SKILL.md frontmatter is missing a closing --- line")

    frontmatter = {}  # type: Dict[str, str]
    for line in lines[1:end]:
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not match:
            continue
        frontmatter[match.group(1)] = strip_quotes(match.group(2))
    return frontmatter


def get_body_text(skill_file: Path) -> str:
    text = skill_file.read_text(encoding="utf-8")
    lines = text.splitlines()

    if not lines or lines[0].strip() != "---":
        raise ValueError("SKILL.md must start with a frontmatter block delimited by ---")

    end = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            end = index
            break
    if end is None:
        raise ValueError("SKILL.md frontmatter is missing a closing --- line")

    return "\n".join(lines[end + 1 :])


def estimate_token_count(text: str) -> Tuple[int, str]:
    if tiktoken is not None:
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text)), "exact"

    # Fallback approximation commonly used for GPT-style token budgets.
    return ceil(len(text) / 4), "estimated"


def parse_openai_metadata(metadata_file: Path) -> Dict[str, str]:
    interface = {}  # type: Dict[str, str]
    in_interface = False

    for raw_line in metadata_file.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue

        if raw_line.startswith("interface:"):
            in_interface = True
            continue

        if not in_interface:
            continue

        if raw_line.startswith((" ", "\t")):
            stripped = raw_line.strip()
            match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", stripped)
            if match:
                interface[match.group(1)] = strip_quotes(match.group(2))
            continue

        break

    return interface


def is_external_link(target: str) -> bool:
    return re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target) is not None


def referenced_local_paths(skill_file: Path, body_text: str) -> Iterator[Tuple[str, Path]]:
    for link_target in MARKDOWN_LINK_PATTERN.findall(body_text):
        target = link_target.strip()
        if not target or target.startswith("#") or is_external_link(target):
            continue

        relative = target.split("#", 1)[0].strip()
        if not relative:
            continue

        yield target, (skill_file.parent / relative)


def validate_relative_links(
    skill_dir: Path, skill_file: Path, body_text: str
) -> Tuple[List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []

    for target, resolved_path in referenced_local_paths(skill_file, body_text):
        if target.startswith("/"):
            warnings.append(
                f"{skill_file}: absolute filesystem link '{target}' will not be bundled with the published skill"
            )
            continue

        try:
            resolved_path.resolve().relative_to(skill_dir.resolve())
        except ValueError:
            warnings.append(
                f"{skill_file}: relative link '{target}' points outside the skill directory"
            )
            continue

        if not resolved_path.exists():
            errors.append(f"{skill_file}: relative link '{target}' does not exist")

    return errors, warnings


def list_skill_files(skill_dir: Path) -> Set[Path]:
    return {
        path.relative_to(skill_dir)
        for path in skill_dir.rglob("*")
        if path.is_file()
    }


def validate_skill(skill_dir: Path) -> List[str]:
    errors = []  # type: List[str]
    warnings = []  # type: List[str]
    skill_file = skill_dir / "SKILL.md"

    if not skill_file.is_file():
        return [f"{skill_dir}: missing SKILL.md"]

    try:
        frontmatter = parse_frontmatter(skill_file)
    except ValueError as exc:
        return [f"{skill_file}: {exc}"]

    body_text = get_body_text(skill_file)
    published_files = list_skill_files(skill_dir)

    for key in REQUIRED_FRONTMATTER_KEYS:
        if not frontmatter.get(key, "").strip():
            errors.append(f"{skill_file}: missing non-empty frontmatter key '{key}'")

    skill_name = frontmatter.get("name", "")
    if skill_name:
        if not (1 <= len(skill_name) <= 64):
            errors.append(
                f"{skill_file}: frontmatter name must be 1-64 characters long"
            )
        if not NAME_PATTERN.fullmatch(skill_name):
            errors.append(
                f"{skill_file}: frontmatter name must use lowercase letters, numbers, and single hyphens only"
            )
        if "--" in skill_name:
            errors.append(
                f"{skill_file}: frontmatter name must not contain consecutive hyphens"
            )

    if skill_name and skill_name != skill_dir.name:
        errors.append(
            f"{skill_file}: frontmatter name '{skill_name}' does not match directory '{skill_dir.name}'"
        )

    description = frontmatter.get("description", "")
    if description and not (1 <= len(description) <= 1024):
        errors.append(
            f"{skill_file}: frontmatter description must be 1-1024 characters long"
        )
    if description and not DESCRIPTION_USE_PATTERN.search(description):
        warnings.append(
            f"{skill_file}: description should explain when the skill is used"
        )

    license_name = frontmatter.get("license", "")
    if license_name and license_name not in VALID_LICENSES:
        warnings.append(
            f"{skill_file}: frontmatter license '{license_name}' is not one of {sorted(VALID_LICENSES)}"
        )

    if not body_text.strip():
        errors.append(f"{skill_file}: body must not be empty")
    else:
        first_content_line: Optional[str] = None
        for line in body_text.splitlines():
            if line.strip():
                first_content_line = line.strip()
                break
        if first_content_line and not first_content_line.startswith("#"):
            warnings.append(
                f"{skill_file}: body should begin with a Markdown heading"
            )

    body_line_count = len(body_text.splitlines())
    if body_line_count >= BODY_MAX_LINES:
        warnings.append(
            f"{skill_file}: body must be under {BODY_MAX_LINES} lines (found {body_line_count})"
        )

    body_token_count, token_count_kind = estimate_token_count(body_text)
    if body_token_count >= BODY_MAX_TOKENS:
        warnings.append(
            f"{skill_file}: body must be under {BODY_MAX_TOKENS} tokens "
            f"({token_count_kind} count {body_token_count})"
        )

    link_errors, link_warnings = validate_relative_links(skill_dir, skill_file, body_text)
    errors.extend(link_errors)
    warnings.extend(link_warnings)

    metadata_file = skill_dir / "agents" / "openai.yaml"
    if metadata_file.is_file():
        interface = parse_openai_metadata(metadata_file)
        for key in REQUIRED_OPENAI_INTERFACE_KEYS:
            if not interface.get(key, "").strip():
                errors.append(
                    f"{metadata_file}: missing non-empty interface.{key}"
                )
    elif Path("agents/openai.yaml") in published_files:
        errors.append(f"{metadata_file}: missing or unreadable OpenAI metadata file")

    return errors + [f"WARNING: {warning}" for warning in warnings]


def main():
    errors = []  # type: List[str]
    skill_dirs = list(iter_skill_dirs())

    if not SKILLS_DIR.is_dir():
        print(f"ERROR: {SKILLS_DIR}: skills directory not found", file=sys.stderr)
        return 1

    if not skill_dirs:
        print(f"ERROR: {SKILLS_DIR}: no skill directories found", file=sys.stderr)
        return 1

    for skill_dir in skill_dirs:
        errors.extend(validate_skill(skill_dir))

    if errors:
        for error in errors:
            if error.startswith("WARNING: "):
                print(error, file=sys.stderr)
            else:
                print(f"ERROR: {error}", file=sys.stderr)
        if any(not error.startswith("WARNING: ") for error in errors):
            return 1

    print("Validated {} skill directories".format(len(skill_dirs)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
