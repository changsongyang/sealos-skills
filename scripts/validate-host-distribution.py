#!/usr/bin/env python3
"""Validate Sealos host adapters against the canonical three-skill pack."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins/sealos"
SKILLS = ("use-sealos", "sealos-deploy", "k8s-kaniko-job")
REPOSITORY = "https://github.com/labring/sealos-skills"


def read_json(relative_path: str) -> dict:
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


def require_path(base: Path, relative_path: str) -> None:
    assert relative_path.startswith("./"), relative_path
    assert (base / relative_path).exists(), relative_path


def main() -> None:
    package = read_json("package.json")
    version = package["version"]
    assert package["repository"]["url"] == f"git+{REPOSITORY}.git"
    assert package["dsh"]["bundle"]["patch"] == "./cordis.patch.yml"
    require_path(ROOT, "./cordis.patch.yml")
    require_path(ROOT, "./index.js")

    for name in SKILLS:
        canonical = PLUGIN / "skills" / name
        alias = ROOT / "skills" / name
        assert (canonical / "SKILL.md").is_file(), name
        assert alias.is_symlink(), name
        assert alias.resolve() == canonical.resolve(), name
    assert {path.name for path in (PLUGIN / "skills").iterdir()} == set(SKILLS)
    assert {path.name for path in (ROOT / "skills").iterdir()} == set(SKILLS)

    codex_marketplace = read_json(".agents/plugins/marketplace.json")
    assert codex_marketplace["name"] == "sealos"
    assert codex_marketplace["interface"]["displayName"] == "Sealos"
    assert codex_marketplace["plugins"][0]["name"] == "sealos"
    assert codex_marketplace["plugins"][0]["source"] == {
        "source": "local", "path": "./plugins/sealos"
    }
    root_codex = read_json(".codex-plugin/plugin.json")
    assert root_codex == read_json("plugin.json")
    nested_codex = read_json("plugins/sealos/.codex-plugin/plugin.json")
    for manifest, base in ((root_codex, ROOT), (nested_codex, PLUGIN)):
        assert manifest["name"] == "sealos"
        assert manifest["version"] == version
        assert manifest["repository"] == REPOSITORY
        require_path(base, manifest["skills"])
        for icon in ("composerIcon", "logo"):
            require_path(base, manifest["interface"][icon])

    for marketplace_name in (".claude-plugin/marketplace.json", "marketplace.json"):
        marketplace = read_json(marketplace_name)
        assert marketplace["plugins"][0]["source"] == "./plugins/sealos"
    for manifest_name, base in (
        (".claude-plugin/plugin.json", ROOT),
        ("plugins/sealos/.claude-plugin/plugin.json", PLUGIN),
    ):
        manifest = read_json(manifest_name)
        assert manifest["version"] == version
        assert manifest["repository"] == REPOSITORY
        for command_dir in manifest["commands"]:
            require_path(base, command_dir)
            assert (base / command_dir / "sealos.md").is_file()
        for skill_dir in manifest["skills"]:
            require_path(base, skill_dir)

    cursor_marketplace = read_json(".cursor-plugin/marketplace.json")
    assert cursor_marketplace["plugins"][0]["source"] == "plugins/sealos"
    cursor = read_json("plugins/sealos/.cursor-plugin/plugin.json")
    assert cursor["version"] == version
    require_path(PLUGIN, cursor["skills"])

    for manifest_name, base in (
        (".qoder-plugin/plugin.json", ROOT),
        ("plugins/sealos/.qoder-plugin/plugin.json", PLUGIN),
    ):
        manifest = read_json(manifest_name)
        assert manifest["version"] == version
        for skill_dir in manifest["skills"] if isinstance(manifest["skills"], list) else [manifest["skills"]]:
            require_path(base, skill_dir)
        command = manifest["commands"]["sealos"]
        require_path(base, command["source"])

    codebuddy = read_json(".codebuddy-plugin/marketplace.json")
    assert codebuddy["version"] == version
    assert codebuddy["plugins"][0]["source"] == "./plugins/sealos"
    assert codebuddy["plugins"][0]["version"] == version

    openclaw = read_json("openclaw.plugin.json")
    assert openclaw["version"] == version
    assert openclaw["source"] == "plugins/sealos/.claude-plugin/plugin.json"
    assert "openclaw" in openclaw["hostTargets"]

    for extension_name in ("gemini-extension.json", "qwen-extension.json"):
        extension = read_json(extension_name)
        assert extension["version"] == version
        assert extension["contextFileName"] == "CLAUDE.md"
        assert "not claimed" in extension["description"]
    assert (ROOT / "CLAUDE.md").is_file()

    registry = read_json("distribution/platforms.json")
    assert registry["version"] == version
    assert registry["repository"] == REPOSITORY
    ids = [platform["id"] for platform in registry["platforms"]]
    assert len(ids) == len(set(ids))
    assert set(ids) == {
        "codex", "claude-code", "cursor", "qoder", "codebuddy", "openclaw",
        "gemini-cli", "qwen-code", "skills-sh", "brain",
        "deepseek-harness", "amp-kimi-generic",
    }
    for platform in registry["platforms"]:
        assert (ROOT / platform["manifest"]).exists(), platform["id"]

    print(f"Validated {len(SKILLS)} canonical skills across {len(ids)} host targets (v{version}).")


if __name__ == "__main__":
    main()
