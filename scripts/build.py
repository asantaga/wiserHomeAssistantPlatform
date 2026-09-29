"""Package Wiser with local development cards or published release assets."""

import argparse
import json
from pathlib import Path
import shutil
import tempfile
from zipfile import ZIP_DEFLATED, ZipFile

from fetch_card_releases import (
    PANEL_CONFIG_REPOSITORY,
    fetch_cards,
    fetch_panel_config,
    repository_overrides,
    select_repositories,
)

ROOT = Path(__file__).resolve().parents[1]


def build(
    source,
    output,
    local_root,
    channel,
    repositories=None,
    release=False,
    panel_config_repository=PANEL_CONFIG_REPOSITORY,
):
    """Stage a fresh integration and replace the ZIP only after a successful build."""
    # Stable builds and explicit releases must never package local card builds.
    if release or channel == "stable":
        local_root = None
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output.parent) as temporary:
        staging = Path(temporary) / "wiser"
        shutil.copytree(
            source, staging,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"),
        )
        manifest, config_record = fetch_panel_config(
            channel,
            local_root=local_root,
            release=release,
            repository=panel_config_repository,
        )
        (staging / "frontend/cards.json").write_text(
            json.dumps(manifest, indent=2) + "\n"
        )
        definitions = {card["id"]: card for card in manifest}
        selected_repositories = select_repositories(definitions, repositories or {})
        report = fetch_cards(
            channel,
            staging / "frontend",
            selected_repositories,
            local_root=local_root,
            definitions=definitions,
        )
        (staging / "frontend/panel-config-release.json").write_text(
            json.dumps(config_record, indent=2) + "\n"
        )
        archive_path = Path(temporary) / "wiser.zip"
        with ZipFile(archive_path, "w", compression=ZIP_DEFLATED) as archive:
            for path in sorted(staging.rglob("*")):
                if path.is_file():
                    archive.write(path, path.relative_to(staging))
        with ZipFile(archive_path) as archive:
            if archive.testzip() is not None:
                raise ValueError("Package integrity check failed")
        archive_path.replace(output)
        shutil.copyfile(
            staging / "frontend/card-releases.json",
            output.parent / "card-releases.json",
        )
        shutil.copyfile(
            staging / "frontend/panel-config-release.json",
            output.parent / "panel-config-release.json",
        )
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--channel", choices=["dev", "stable"], default="dev")
    parser.add_argument("--release", action="store_true",
                        help="Use only GitHub release assets, including for the dev channel")
    parser.add_argument("--local-root", type=Path, default=ROOT.parent,
                        help="Directory containing sibling card repositories")
    parser.add_argument("--output", type=Path, default=ROOT / "dist/wiser.zip")
    parser.add_argument("--repository", action="append", default=[], metavar="ID=OWNER/REPO")
    parser.add_argument(
        "--panel-config-repository", default=PANEL_CONFIG_REPOSITORY
    )
    args = parser.parse_args()
    try:
        report = build(
            ROOT / "custom_components/wiser", args.output, args.local_root,
            args.channel,
            repository_overrides(args.repository),
            release=args.release,
            panel_config_repository=args.panel_config_repository,
        )
    except Exception as error:
        parser.exit(1, f"Build failed: {error}\n")
    print(json.dumps(report, indent=2))
    print(f"Built {args.output.resolve()}")


if __name__ == "__main__":
    main()
