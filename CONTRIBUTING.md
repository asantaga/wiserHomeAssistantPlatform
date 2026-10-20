# Contributing

Thanks for helping out with the Wiser Home Assistant integration. Issues, pull
requests, and bug fixes are all welcome and greatly appreciated.

## Before you start

- **Search the [issues](https://github.com/asantaga/wiserHomeAssistantPlatform/issues)
  first.** If your problem is already reported, add your details there rather
  than opening a duplicate.
- For anything larger than a bug fix, open an issue to discuss the approach
  before writing code. It saves everyone a wasted PR.
- Check the [Wiki](https://github.com/asantaga/wiserHomeAssistantPlatform/wiki)
  for setup and usage documentation.

## Reporting bugs

Please include:

- The integration version (Settings → Devices & Services → Wiser), and your
  Home Assistant version.
- Your hub model (v1 or v2) and firmware version.
- Depending on the bug we may ask for a **diagnostics download** from the integration's device page — it redacts
  secrets and captures the hub data we need.
- Relevant log output. Add this to `configuration.yaml`, restart, and reproduce:

  ```yaml
  logger:
    default: warning
    logs:
      custom_components.wiser: debug
      aioWiserHeatAPI: debug
  ```

## Where things live

| What | Where |
| --- | --- |
| Integration source | `custom_components/wiser/` |
| Hub communication | the separate `aioWiserHeatAPI` library, pinned in `manifest.json` |
| Frontend panel/card plumbing | `custom_components/wiser/frontend/` |
| Frontend cards and panels | repositories declared in `custom_components/wiser/frontend/cards.json` |
| Tests | `tests/` |
| Packaging scripts | `scripts/` |

Two things that trip people up:

- If a change is really about how we talk to the hub, it probably belongs in 
  [aioWiserHeatAPI](https://github.com/msp1974/aioWiserHeatAPI) git repo, not here.
- **Card bundles are not committed to this repository.** They are downloaded
  from the card repositories' GitHub releases at build time. Do not add built
  `.js` card assets to `custom_components/wiser/frontend/`.
- Follow [Adding Wiser frontend cards and panels](docs/frontend-registry.md) to
  register a new frontend repository and test its independent update entity.

## Branching and pull requests

- **Base every PR on `dev`.** All development happens there; `master` only
  receives `dev` when we cut a release.
- Name your branch after the issue it fixes, e.g. `issue123`.
- Keep a PR to one logical change. Unrelated fixes are much easier to review as
  separate PRs.
- Reference the issue in the PR description (`Fixes #123`).
- Add or update tests for behaviour you change, and add a `CHANGELOG.md` entry
  under the unreleased/current heading, matching the existing style (one line,
  ending with a link to the issue and/or PR).

Releases are tagged from `master` as `vX.Y.Z` (e.g. `v3.4.20`). Release
candidates are cut from `dev` and tagged `vX.Y.Z-rcN` (e.g. `v4.0.0-rc1`).

## Development setup

Run the integration against a real Home Assistant instance. The quickest route
is a development instance (container or venv) with the integration mounted or
symlinked into place:

```sh
ln -s /path/to/wiserHomeAssistantPlatform/custom_components/wiser \
      /path/to/ha-config/custom_components/wiser
```

Restart Home Assistant after each change — Home Assistant does not hot-reload
custom components.

The minimum supported Home Assistant version is declared in `hacs.json`
(currently 2025.5); don't use APIs newer than that without raising the minimum
deliberately.


## Code style

There is no enforced formatter config in this repository, so match the
surrounding code, which follows Home Assistant core conventions:

- `from __future__ import annotations` at the top, type hints on new functions.
- Docstrings on every module, class, and function.
- Import grouping and ordering as in the existing modules.
- New user-visible strings go in `strings.json` and the files under
  `translations/`; new icons go in `icons.json`.

## Versioning

The version is set in two places, and both must be changed together:

- `version` in `custom_components/wiser/manifest.json`, which HACS and Home
  Assistant read.
- `VERSION` in `custom_components/wiser/const.py`, which the integration reports
  itself, for example in the hub sensor's `integration_version` attribute.

The version must stay parseable by HACS and Home Assistant. Use `X.Y.Z` for
releases, `X.Y.Z-rcN` for release candidates, and `X.Y.ZbN` for beta builds on
`dev`. Do not invent suffixes such as `Dev` — HACS and Home Assistant reject
them, and the integration will fail to load with `does not have a valid version
key`.

## Building a package

```sh
# Local development package
python3 scripts/build.py --channel dev

# Local development package using a manually installed API
python3 scripts/build.py --channel dev --use-installed-api

# Stable release package
python3 scripts/build.py --release --channel stable

# Prerelease package
python3 scripts/build.py --release --channel dev
```

The build downloads every card and panel declared in
`custom_components/wiser/frontend/cards.json` from its own GitHub repository.
Stable builds use stable frontend releases; prerelease builds use the most
recently published stable or prerelease release. In a running installation,
each frontend update entity follows the HACS **Pre-release** switch for this
integration; without that option it offers stable releases only. See
[Adding frontend cards and panels](docs/frontend-registry.md) for the registry
format and shared panel API.

The source manifest pins the released `aioWiserHeatAPI` version. A dev-channel
build uses the newest published API prerelease that is newer than the released
pin; if none is available, or PyPI cannot be checked, it retains the released
pin. Pass `--use-installed-api` for local testing with a manually installed API;
this removes the API requirement from the packaged manifest so Home Assistant
does not replace the installed version. The option cannot be combined with
`--release`. A final release package (`--release --channel stable`) always
retains the released pin.

API artifacts are built separately in the `aioWiserHeatAPI` repository and are
never bundled in the integration package. All API requirement changes apply
only to the staged package; the source manifest is never modified by the build.

The output is `dist/wiser.zip`, with `dist/card-releases.json` recording the
frontend artifacts and checksums included. If an individual card or panel
repository is temporarily unavailable, its bundle is omitted and the
integration still builds; its Home Assistant update entity can install it
later. Invalid local development bundles and an invalid bundled registry still
fail the build.

For an integration-only test package that retains the registry but
deliberately omits every card and panel bundle:

```sh
python3 scripts/build.py --channel dev --without-frontend
```

To see which card releases would be selected without downloading card bundles
(the registry metadata is still fetched):

```sh
python3 scripts/fetch_card_releases.py --channel dev --plan
```

The **Publish** GitHub Actions workflow runs the same build and attaches
`wiser.zip` when an integration release is published. Preview runs provide a
downloadable **wiser-package** artifact without publishing a release.

## Licence

By contributing, you agree that your contributions are licensed under the
project's MIT licence (see [LICENSE](LICENSE)).

Thanks again,
Wiser Home Assistant Integration Team
