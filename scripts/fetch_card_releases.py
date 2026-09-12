"""Fetch published card assets for integration packaging (never branch source)."""

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import tempfile
from urllib.parse import urlparse
from urllib.request import Request, urlopen

CARD_REPOSITORIES = {
    "schedule": "andyblac/wiser-schedule-card",
    "zigbee": "andyblac/wiser-zigbee-card",
}


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
    published = [r for r in releases if not r.get("draft") and r.get("published_at")]
    stable = [r for r in published if not r.get("prerelease")]
    beta = [r for r in published if r.get("prerelease")]
    candidates = (beta or stable) if channel == "dev" else stable
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


def fetch_cards(channel, output_dir, repositories, plan=False):
    selections = []
    # Resolve every release before downloading or replacing any assets.
    for card, repository in repositories.items():
        release = select_release(list_releases(repository), channel)
        filename = f"wiser-{card}-card.js"
        asset = select_asset(release, filename)
        selections.append((repository, release, asset))
    report = []
    payloads = {}
    for repository, release, asset in selections:
        record = {
            "repository": repository, "tag": release["tag_name"],
            "prerelease": release["prerelease"], "asset": asset["name"],
            "asset_id": asset["id"], "url": asset["browser_download_url"],
        }
        if not plan:
            contents, digest = download_asset(repository, asset)
            # The integration's dedicated panel must have a matching card build.
            if asset["name"] == "wiser-schedule-card.js" and (output_dir / "sidebar.py").exists() and b"wiser-schedules-panel" not in contents:
                raise ValueError("Selected schedule card does not include the sidebar panel required by this integration")
            payloads[asset["name"]] = contents
            record["digest"] = digest
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--channel", choices=["dev", "stable"], required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("dist/wiser/frontend"))
    parser.add_argument("--card", choices=["schedule", "zigbee", "all"], default="all")
    parser.add_argument("--schedule-repository", default=CARD_REPOSITORIES["schedule"])
    parser.add_argument("--zigbee-repository", default=CARD_REPOSITORIES["zigbee"])
    parser.add_argument("--plan", action="store_true", help="Show selected releases without downloading or writing files")
    args = parser.parse_args()
    repositories = {"schedule": args.schedule_repository, "zigbee": args.zigbee_repository}
    if args.card != "all":
        repositories = {args.card: repositories[args.card]}
    try:
        report = fetch_cards(args.channel, args.output_dir, repositories, args.plan)
    except Exception as error:
        parser.exit(1, f"Card release fetch failed: {error}\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
