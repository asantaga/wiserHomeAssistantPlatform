# Adding frontend cards and panels

After installing an integration version with runtime registry support, adding a
card or panel that uses the existing Wiser APIs requires no integration PR.

1. Publish a release in the card repository with the JavaScript bundle attached.
2. Add its definition to `src/cards.json` in
   [WiserFrontendPanelConfig](https://github.com/andyblac/WiserFrontendPanelConfig).
3. Build and publish a registry release with `cards.json` attached.
4. Home Assistant discovers the definition on its next daily card-update check.
   To check sooner, run `homeassistant.update_entity` on an existing Wiser card
   update entity. The registry and card checks follow the integration's HACS
   prerelease switch.
5. Install the new card using its update entity, then refresh the browser. Its
   Lovelace resource and any panel tab are registered automatically. A new card
   without an installed version is offered with version `0.0.0`.

Discovery downloads registry metadata only. JavaScript is downloaded when the
user installs the card. The integration retains the last valid registry and
installed bundles under `.storage/wiser_cards` across restarts and upgrades.
A missing or invalid registry release leaves the existing definitions in use.
Omitting a card from a later registry does not uninstall it or erase its settings.
Existing IDs, filenames, repositories and component names are treated as stable
identities; changing them requires an explicit migration rather than silently
redirecting an existing installation.

## Registry definition

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

`cards.json` contains an array of these objects. The `id` is a stable registry
identifier independent of the filename. Use `null` for `panel` for a card with no
sidebar view. IDs, filenames, card components and non-null panel components must
be unique.
The runtime registry accepts up to 100 definitions and a 256 KiB registry asset.

The JavaScript release must include a matching version marker, for example:

```js
/*! WISER-CARD-VERSION wiser-energy-card 1.0.0 */
```

It must define the declared card and optional panel custom elements. The existing
card repositories demonstrate the panel contract. Each panel receives `hass` and
`panel.config`, including `panel_id`, `hubs`, `hub_ids`, per-hub `card_configs`,
and `card_url`. Always use the supplied `panel_id` when saving settings.

## Shared settings endpoint

New panels save preferences using this administrator-only WebSocket command:

```js
await hass.callWS({
  type: "wiser/panel/configure",
  panel_id: this._config.panel_id,
  configs: {
    [hubName]: { columns: 3 }
  }
});
```

The integration stores these settings under
`wiser_panel_config.energy` in each selected hub's options and refreshes the panel
without reloading the hub. All panels, including the existing ones, use this
command. The former per-panel
commands have been removed; deploy the rebuilt card bundles with this integration
bridge. There are no separate per-panel settings options or reload exclusions.
Tab ordering and custom titles continue to use
`wiser/panel/configure_tabs`.

The shared panel shell and backend APIs still ship with the integration. New
backend commands, new hub data or changes to the shared shell require an
integration release; adding a card or panel using the existing contract does not.

## Packaging and source ownership

The integration repository contains no maintained card list. Builds read the
external registry's `dist/cards.json` for local development, or its published
release asset for release builds, and generate the package's offline snapshot.
The build loops over every definition, including new IDs and repositories.
Optional local overrides use `--repository ID=OWNER/REPOSITORY`; there are no
card-specific build flags. Publish the generic-API card bundles before building
an integration release with the bridge.

Source checkouts without a generated snapshot start with an empty card list and
can discover definitions from the external registry. Normal ZIP installs include
the validated registry snapshot and card bundles for offline setup.
