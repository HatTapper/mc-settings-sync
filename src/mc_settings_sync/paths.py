"""Filesystem discovery for Prism instances and settings templates."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

CONFIG_FILENAME = "mc-settings-sync.json"


def default_instances_root() -> Path:
    appdata = os.environ.get("APPDATA")
    if appdata:
        return Path(appdata) / "PrismLauncher" / "instances"
    return Path.home() / ".local" / "share" / "PrismLauncher" / "instances"


def default_templates_root() -> Path:
    return Path.home() / "Documents" / "MCTemplates"


def config_path() -> Path:
    appdata = os.environ.get("APPDATA")
    base = Path(appdata) if appdata else Path.home() / ".config"
    return base / "mc-settings-sync" / CONFIG_FILENAME


@dataclass
class Settings:
    instances_root: Path
    templates_root: Path

    @classmethod
    def load(cls) -> "Settings":
        path = config_path()
        data = {}
        if path.is_file():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                data = {}
        return cls(
            instances_root=Path(data.get("instances_root") or default_instances_root()),
            templates_root=Path(data.get("templates_root") or default_templates_root()),
        )

    def save(self) -> None:
        path = config_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(
                {
                    "instances_root": str(self.instances_root),
                    "templates_root": str(self.templates_root),
                },
                indent=2,
            ),
            encoding="utf-8",
        )


def list_instances(instances_root: Path) -> list[str]:
    """Instance folder names that actually contain a Minecraft game directory."""
    if not instances_root.is_dir():
        return []
    names = []
    for entry in sorted(instances_root.iterdir(), key=lambda p: p.name.lower()):
        if entry.is_dir() and minecraft_dir(entry) is not None:
            names.append(entry.name)
    return names


def minecraft_dir(instance_dir: Path) -> Path | None:
    """Prism uses `minecraft`; some older/imported instances use `.minecraft`."""
    for candidate in ("minecraft", ".minecraft"):
        path = instance_dir / candidate
        if path.is_dir():
            return path
    return None


def list_templates(templates_root: Path) -> list[str]:
    if not templates_root.is_dir():
        return []
    return [
        entry.name
        for entry in sorted(templates_root.iterdir(), key=lambda p: p.name.lower())
        if entry.is_dir()
    ]
