import pytest

from mc_settings_sync.paths import create_starter_template, list_instances, list_templates
from mc_settings_sync.sync import SyncError, apply_template


def make_instance(root, name, game_dir="minecraft"):
    path = root / name / game_dir
    path.mkdir(parents=True)
    return path


def make_template(root, name, files):
    base = root / name
    for relative, content in files.items():
        target = base / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    return base


def test_apply_copies_nested_files(tmp_path):
    instances, templates = tmp_path / "instances", tmp_path / "templates"
    game = make_instance(instances, "Fabric 1.21")
    make_template(
        templates,
        "base",
        {"options.txt": "fov:0.5", "config/sodium-options.json": "{}"},
    )

    result = apply_template(instances, "Fabric 1.21", templates, "base")

    assert sorted(result.copied) == ["config/sodium-options.json", "options.txt"]
    assert (game / "options.txt").read_text(encoding="utf-8") == "fov:0.5"
    assert (game / "config" / "sodium-options.json").exists()


def test_apply_overwrites_only_template_files(tmp_path):
    instances, templates = tmp_path / "instances", tmp_path / "templates"
    game = make_instance(instances, "Modded")
    (game / "saves").mkdir()
    (game / "saves" / "world.dat").write_text("keep me", encoding="utf-8")
    (game / "options.txt").write_text("old", encoding="utf-8")
    make_template(templates, "base", {"options.txt": "new"})

    apply_template(instances, "Modded", templates, "base")

    assert (game / "options.txt").read_text(encoding="utf-8") == "new"
    assert (game / "saves" / "world.dat").read_text(encoding="utf-8") == "keep me"


def test_dry_run_writes_nothing(tmp_path):
    instances, templates = tmp_path / "instances", tmp_path / "templates"
    game = make_instance(instances, "Vanilla")
    make_template(templates, "base", {"options.txt": "new"})

    result = apply_template(instances, "Vanilla", templates, "base", dry_run=True)

    assert result.copied == ["options.txt"]
    assert not (game / "options.txt").exists()


def test_missing_instance_and_template_raise(tmp_path):
    instances, templates = tmp_path / "instances", tmp_path / "templates"
    make_instance(instances, "Vanilla")
    make_template(templates, "base", {"options.txt": "x"})

    with pytest.raises(SyncError, match="Instance not found"):
        apply_template(instances, "Nope", templates, "base")
    with pytest.raises(SyncError, match="Template not found"):
        apply_template(instances, "Vanilla", templates, "nope")


def test_instance_without_game_dir_is_reported(tmp_path):
    instances, templates = tmp_path / "instances", tmp_path / "templates"
    (instances / "Fresh").mkdir(parents=True)
    make_template(templates, "base", {"options.txt": "x"})

    with pytest.raises(SyncError, match="No 'minecraft' folder"):
        apply_template(instances, "Fresh", templates, "base")


def test_listing_skips_non_instances(tmp_path):
    instances, templates = tmp_path / "instances", tmp_path / "templates"
    make_instance(instances, "Alpha")
    make_instance(instances, "Beta", game_dir=".minecraft")
    (instances / "NotAnInstance").mkdir()
    make_template(templates, "base", {"options.txt": "x"})
    (templates / "loose.txt").write_text("x", encoding="utf-8")

    assert list_instances(instances) == ["Alpha", "Beta"]
    assert list_templates(templates) == ["base"]


def test_listing_missing_roots_is_empty(tmp_path):
    assert list_instances(tmp_path / "nope") == []
    assert list_templates(tmp_path / "nope") == []


def test_create_starter_template_builds_missing_tree(tmp_path):
    root = tmp_path / "Documents" / "MCTemplates"

    starter = create_starter_template(root)

    assert starter == root / "base"
    assert starter.is_dir()
    assert (root / "README.txt").is_file()
    assert list_templates(root) == ["base"]


def test_create_starter_template_is_repeatable(tmp_path):
    root = tmp_path / "MCTemplates"
    create_starter_template(root)
    (root / "base" / "options.txt").write_text("mine", encoding="utf-8")
    (root / "README.txt").write_text("my own notes", encoding="utf-8")

    create_starter_template(root)

    assert (root / "base" / "options.txt").read_text(encoding="utf-8") == "mine"
    assert (root / "README.txt").read_text(encoding="utf-8") == "my own notes"
