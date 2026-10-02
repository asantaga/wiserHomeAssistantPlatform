# Adding Wiser frontend cards and panels

Wiser cards and panels are developed and released from their own repositories. The integration keeps only their definitions in `custom_components/wiser/frontend/cards.json`; compiled JavaScript bundles must not be committed to this repository.

Adding a new definition requires an integration pull request and release. After that initial registration, new versions of the card or panel are released and updated independently through its Home Assistant update entity.

## Choose the frontend type

The registry supports three types of frontend bundle:

| Type | `component` | `panel` | `card` |
| --- | --- | --- | --- |
| Lovelace card only | Card custom element | `null` | Omit or `true` |
| Sidebar panel only | Panel custom element | Panel custom element | `false` |
| Card and sidebar panel | Card custom element | Panel custom element | Omit or `true` |

A panel-only bundle is not added to the Lovelace resources list. The integration loads it only for its Wiser sidebar tab.

## Prepare the frontend repository

The repository must publish a GitHub release containing one compiled JavaScript asset whose name exactly matches the registry `filename`. The asset must:

- Be at least 100 bytes and contain JavaScript rather than an HTML error page.
- Define the custom element named by `component`.
- Define the custom element named by `panel` when one is configured.
- Use the shared `wiser/panel/configure` API instead of a panel-specific settings endpoint.
- Begin with a version marker matching the asset filename and release version.

For `wiser-energy-card.js` version `1.0.0`, the marker is:

```js
/*! WISER-CARD-VERSION wiser-energy-card 1.0.0 */
```

Use semantic release tags such as `v1.0.0` or `v1.1.0-beta.1`. Stable update checks ignore prereleases. When the HACS **Pre-release** switch is enabled for the integration, update checks consider stable and prerelease versions.

## Add the registry definition

Add an entry to the `cards` array in `custom_components/wiser/frontend/cards.json`:

```json
{
  "id": "energy",
  "name": "Wiser Energy Card",
  "filename": "wiser-energy-card.js",
  "repository": "andyblac/wiser-energy-card",
  "component": "wiser-energy-card",
  "panel": "wiser-energy-panel"
}
```

The fields are:

| Field | Purpose |
| --- | --- |
| `id` | Stable internal identifier used for settings and the update entity. |
| `name` | Name displayed by the Home Assistant update entity. |
| `filename` | Exact JavaScript filename attached to every GitHub release. |
| `repository` | GitHub repository in `owner/repository` form. |
| `component` | Custom element defined by the JavaScript bundle. |
| `panel` | Sidebar panel custom element, or `null` for a card without a panel. |
| `card` | Set to `false` for a panel-only bundle; otherwise omit it. |
| `legacy_filenames` | Previous filenames retained only when migrating a renamed card. |

A card without a sidebar panel uses `"panel": null`. A panel-only definition uses the panel custom element for both `component` and `panel`:

```json
{
  "id": "hub",
  "name": "Wiser Hub Panel",
  "filename": "wiser-hub-panel.js",
  "repository": "andyblac/wiser-hub-panel",
  "component": "wiser-hub-panel",
  "panel": "wiser-hub-panel",
  "card": false
}
```

IDs, filenames, component names and non-null panel names must be unique. Treat them as permanent identities after release. Renaming one requires an explicit migration so existing resources, settings and entity history are preserved. The versioned registry document supports up to 100 definitions:

```json
{
  "schema_version": 1,
  "cards": []
}
```

## Test registration locally

For the normal development layout, place the frontend repository beside this integration repository and build its `dist/<filename>` output. A development integration build automatically prefers that local bundle:

```text
GitHub/
├── wiserHomeAssistantPlatform/
└── wiser-energy-card/
    └── dist/
        └── wiser-energy-card.js
```

```sh
python3 scripts/build.py --channel dev
```

To test installation through Home Assistant instead, edit the installed `custom_components/wiser/frontend/cards.json` and run **Check for updates** on any Wiser frontend update entity. The shared coordinator reloads and validates the file, creates an update entity for the new definition, and offers it as installed version `0.0.0`. This does not require an integration rebuild or Home Assistant restart.

To build a package containing the definitions but none of the JavaScript bundles, run:

```sh
python3 scripts/build.py --channel dev --without-frontend
```

This is useful for testing initial installation through all frontend update entities. The build does not contact any card or panel repository.

You can override a repository during development without changing the registry:

```sh
python3 scripts/build.py --channel dev \
  --repository energy=example/wiser-energy-card
```

## Submit the integration pull request

The pull request for a new card or panel should contain:

- Its entry in `custom_components/wiser/frontend/cards.json`.
- Any integration backend, WebSocket or shared-shell changes it requires.
- Tests for new integration behavior.
- A changelog entry when required by the integration contribution guidelines.

Publish a usable frontend release before the integration release is built. If the frontend repository or release asset is unavailable during packaging, the integration build continues and omits that bundle. Its definition remains in `cards.json`, so Home Assistant can install it later through the update entity.

After the definition has shipped, normal frontend releases require no further integration pull request. Publish the correctly named and versioned JavaScript asset in the frontend repository; Home Assistant will offer it through the existing update entity.

## Sidebar panel contract

Each registered panel receives `hass` and `panel.config`. The configuration includes `panel_id`, `hubs`, `hub_ids`, per-hub `card_configs`, and `card_url`. Use the supplied `panel_id` when saving settings.

Panel preferences use the administrator-only shared WebSocket command:

```js
await hass.callWS({
  type: "wiser/panel/configure",
  panel_id: this._config.panel_id,
  configs: {
    [hubName]: { columns: 3 }
  }
});
```

The integration stores this example under `wiser_panel_config.energy` in each selected hub's options and refreshes the panel without reloading the hub. Tab ordering and custom titles continue to use `wiser/panel/configure_tabs`.

The shared panel shell and backend APIs ship with the integration. A panel that needs new backend commands, hub data or shared-shell behavior must include those changes in its integration pull request.
