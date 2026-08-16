import shutil
from dataclasses import dataclass, field
from pathlib import Path

from .paths import minecraft_dir


class SyncError(Exception):
    # raised when the instance or template cannot be resolved
    pass


@dataclass
class SyncResult:
    destination: Path
    copied: list[str] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.copied)


# keeps a name from escaping its root with .. or an absolute path
# returns the resolved folder so callers work with a clean path
def resolve_inside(root: Path, name: str, label: str) -> Path:
    resolved = root.joinpath(name).resolve()

    if not resolved.is_relative_to(root.resolve()):
        raise SyncError(f"{label} name must stay inside {root}, got '{name}'")

    return resolved


def resolve_destination(instances_root: Path, instance_name: str) -> Path:
    instance_dir = resolve_inside(instances_root, instance_name, "Instance")

    if not instance_dir.is_dir():
        raise SyncError(f"Instance not found: {instance_dir}")

    game_dir = minecraft_dir(instance_dir)
    if game_dir is None:
        raise SyncError(
            f"No 'minecraft' folder inside {instance_dir}. "
            "Launch the instance once so Prism creates it."
        )
    
    return game_dir


def resolve_template(templates_root: Path, template_name: str) -> Path:
    template_dir = resolve_inside(templates_root, template_name, "Template")

    if not template_dir.is_dir():
        raise SyncError(f"Template not found: {template_dir}")
    
    return template_dir


# copies over every file in the template into the target instance dir
# only touches files that need to be overwritten
def apply_template(
    instances_root: Path,
    instance_name: str,
    templates_root: Path,
    template_name: str,
    dry_run: bool = False,
) -> SyncResult:
    destination = resolve_destination(instances_root, instance_name)
    source = resolve_template(templates_root, template_name)

    result = SyncResult(destination=destination)

    for src_file in sorted(source.rglob("*")):
        if not src_file.is_file():
            continue

        relative = src_file.relative_to(source)
        dst_file = destination.joinpath(relative)

        if not dry_run:
            dst_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_file, dst_file)

        result.copied.append(relative.as_posix())

    return result
