"""Fetch published card assets for integration packaging (never branch source)."""

import argparse
from hashlib import sha256
import importlib.util
import json
import os
from pathlib import Path
import re
import tempfile
from urllib.parse import urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
PANEL_CONFIG_REPOSITORY = "andyblac/WiserFrontendPanelConfig"
PANEL_CONFIG_FILENAME = "cards.json"


# Load the dependency-free schema without importing the Home Assistant package.
_SPEC = importlib.util.spec_from_file_location(
    "wiser_frontend_manifest", ROOT / "custom_components/wiser/frontend/manifest.py"
)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError("Unable to load the frontend registry schema")
_MANIFEST = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MANIFEST)
validate_card_manifest = _MANIFEST.validate_manifest


def fetch_panel_config(
    channel,
    local_root=None,
    release=False,
    repository=PANEL_CONFIG_REPOSITORY,
):
    """Load definitions exclusively from the external registry build or release."""
    local = (
        Path(local_root) / repository.rsplit("/", 1)[-1] / "dist" / PANEL_CONFIG_FILENAME
        if local_root is not None and not release
        else None
    )
    if local is not None and local.is_file():
        contents = local.read_bytes()
        record = {
            "repository": repository,
            "source": "local",
            "asset": PANEL_CONFIG_FILENAME,
            "path": str(local.resolve()),
            "digest": "sha256:" + sha256(contents).hexdigest(),
        }
    else:
        selected = select_release(list_releases(repository), channel)
        asset = select_asset(selected, PANEL_CONFIG_FILENAME)
        contents, digest = download_asset(repository, asset)
        record = {
            "repository": repository,
            "source": "release",
            "tag": selected["tag_name"],
            "prerelease": selected["prerelease"],
            "asset": PANEL_CONFIG_FILENAME,
            "asset_id": asset["id"],
            "url": asset["browser_download_url"],
            "digest": digest,
        }
    try:
        manifest = json.loads(contents)
    except (TypeError, json.JSONDecodeError) as error:
        raise ValueError("Invalid cards.json") from error
    return validate_card_manifest(manifest), record


def list_releases(repository):
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise ValueError(f"Invalid repository: {repository}")
    releases = []
    for page in range(1, 101):
        headers = {"Accept": "application/vnd.github+json", "User-Agent": "wiser-card-packager"}
        if token := os.environ.get("GITHUB_TOKEN"):
            headers["Authorization"] = f"Bearer {token}"
        request = Request(
            f"https://api.github.com/repos/{repository}/releases?per_page=100&page={page}",
            headers=headers,
        )
        with urlopen(request, timeout=30) as response:
            batch = json.load(response)
        releases.extend(batch)
        if len(batch) < 100:
            return releases
    raise ValueError(f"Too many releases in {repository}")


def select_release(releases, channel):
    """Select the most recently published release allowed by the channel."""
    published = [r for r in releases if not r.get("draft") and r.get("published_at")]
    stable = [r for r in published if not r.get("prerelease")]
    candidates = published if channel == "dev" else stable
    if not candidates:
        raise ValueError(f"No published {'prerelease or stable' if channel == 'dev' else 'stable'} release available")
    return max(candidates, key=lambda r: r["published_at"])


def select_asset(release, filename):
    assets = [a for a in release.get("assets", []) if a["name"] == filename and a.get("state") == "uploaded"]
    if len(assets) != 1:
        raise ValueError(f"Release {release['tag_name']} must have one uploaded {filename} asset")
    return assets[0]


def download_asset(repository, asset):
    url = asset["browser_download_url"]
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.netloc != "github.com" or not parsed.path.startswith(f"/{repository}/releases/download/"):
        raise ValueError("Asset URL is not a GitHub release download for the selected repository")
    # Public assets do not require forwarding the API token through redirects.
    with urlopen(Request(url, headers={"User-Agent": "wiser-card-packager"}), timeout=60) as response:
        contents = response.read()
    if len(contents) != asset["size"] or len(contents) < 100:
        raise ValueError(f"Incorrect size for {asset['name']}")
    digest = "sha256:" + sha256(contents).hexdigest()
    if asset.get("digest") and asset["digest"] != digest:
        raise ValueError(f"Digest mismatch for {asset['name']}")
    if contents.lstrip().lower().startswith((b"<!doctype html", b"<html")):
        raise ValueError("Downloaded HTML instead of JavaScript")
    return contents, digest


def fetch_cards(
    channel,
    output_dir,
    repositories,
    definitions,
    plan=False,
    local_root=None,
):
    report = []
    payloads = {}
    # Resolve and validate every source before replacing any staged assets.
    for card, repository in repositories.items():
        definition = definitions[card]
        filename = definition["filename"]
        local = (
            Path(local_root) / repository.rsplit("/", 1)[-1] / "dist" / filename
            if local_root is not None else None
        )
        if local is not None and local.is_file():
            contents = local.read_bytes()
            record = {
                "repository": repository, "source": "local", "asset": filename,
                "path": str(local.resolve()),
                "digest": "sha256:" + sha256(contents).hexdigest(),
            }
        else:
            release = select_release(list_releases(repository), channel)
            asset = select_asset(release, filename)
            record = {
                "repository": repository, "source": "release",
                "tag": release["tag_name"], "prerelease": release["prerelease"],
                "asset": filename, "asset_id": asset["id"],
                "url": asset["browser_download_url"],
            }
            if not plan:
                contents, record["digest"] = download_asset(repository, asset)
        if not plan:
            if not contents or contents.lstrip().lower().startswith((b"<!doctype html", b"<html")):
                raise ValueError(f"Invalid JavaScript bundle: {filename}")
            if re.search(rb"wiser/[a-z0-9_-]+_panel/configure", contents):
                raise ValueError("Panel bundle must use the generic settings API")
            if definition["component"].encode() not in contents:
                raise ValueError(
                    f"Selected {card} card does not include {definition['component']}"
                )
            if definition.get("panel") and definition["panel"].encode() not in contents:
                raise ValueError(f"Selected {card} card does not include the sidebar panel required by this integration")
            payloads[filename] = contents
        report.append(record)
    if not plan:
        output_dir.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=output_dir) as temporary:
            for filename, contents in payloads.items():
                staged = Path(temporary) / filename
                staged.write_bytes(contents)
            for filename in payloads:
                (Path(temporary) / filename).replace(output_dir / filename)
        (output_dir / "card-releases.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def repository_overrides(values):
    """Parse optional overrides without baking any card identities into the CLI."""
    result = {}
    for value in values:
        card_id, separator, repository = value.partition("=")
        if not separator or not re.fullmatch(r"[a-z0-9-]+", card_id) or not re.fullmatch(
            r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository
        ):
            raise ValueError("Repository overrides must be ID=OWNER/REPOSITORY")
        if card_id in result:
            raise ValueError(f"Duplicate repository override: {card_id}")
        result[card_id] = repository
    return result


def select_repositories(definitions, overrides):
    """Resolve every card from its definition and reject misspelled overrides."""
    unknown = overrides.keys() - definitions.keys()
    if unknown:
        raise ValueError(f"Unknown card repository overrides: {sorted(unknown)}")
    return {key: overrides.get(key, card["repository"]) for key, card in definitions.items()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--channel", choices=["dev", "stable"], required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("dist/wiser/frontend"))
    parser.add_argument("--card", default="all", help="Registry card ID, or all")
    parser.add_argument("--repository", action="append", default=[], metavar="ID=OWNER/REPO")
    parser.add_argument("--panel-config-repository", default=PANEL_CONFIG_REPOSITORY)
    parser.add_argument("--plan", action="store_true", help="Resolve registry and releases without downloading card bundles")
    args = parser.parse_args()
    try:
        manifest, _ = fetch_panel_config(args.channel, release=True, repository=args.panel_config_repository)
        definitions = {card["id"]: card for card in manifest}
        repositories = select_repositories(definitions, repository_overrides(args.repository))
        if args.card != "all":
            if args.card not in repositories:
                raise ValueError(f"Unknown registry card: {args.card}")
            repositories = {args.card: repositories[args.card]}
        report = fetch_cards(args.channel, args.output_dir, repositories, definitions, plan=args.plan)
    except Exception as error:
        parser.exit(1, f"Card release fetch failed: {error}\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
