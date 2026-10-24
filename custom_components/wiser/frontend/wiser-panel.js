/*! WISER-CARD-VERSION wiser-panel 1.1.0 */

const WISER_ACTIVE_PANEL_KEY = "wiser-active-panel";

class WiserPanel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this.shadowRoot.innerHTML = `
      <style>
        :host { display:flex; flex-direction:column; height:100vh; height:100dvh;
          min-width:0; min-height:0; overflow:hidden; color:var(--primary-text-color);
          background:var(--primary-background-color); }
        header { display:flex; flex:0 0 64px; align-items:center; gap:16px; min-width:0;
          padding:0 16px; background:var(--app-header-background-color);
          color:var(--app-header-text-color); }
        .brand { display:block; flex:0 0 auto; width:96px; height:auto; }
        #menu { flex-shrink:0; color:inherit; }
        #menu ha-icon { color:var(--app-header-text-color, var(--primary-text-color)); }
        #panel-tabs { display:flex; flex:1; min-width:0; margin-inline-start:24px;
          align-self:stretch; overflow-x:auto; }
        #panel-tabs[hidden], .panel-view[hidden] { display:none; }
        #panel-actions { display:flex; flex-shrink:0; margin-inline-start:auto; }
        #panel-actions[hidden], #settings[hidden] { display:none; }
        #panel-actions ha-button { color:inherit; }
        #panel-actions ha-icon { color:var(--app-header-text-color, var(--primary-text-color)); }
        .panel-tab { flex:0 0 auto; min-height:48px; padding:0 24px; border:0;
          border-bottom:2px solid transparent; background:transparent;
          color:var(--secondary-text-color); font:inherit; cursor:pointer; }
        .panel-tab[aria-selected="true"] { color:var(--app-header-text-color, var(--primary-text-color));
          border-bottom-color:currentColor; }
        .panel-tab:focus-visible { outline:2px solid currentColor; outline-offset:-4px; }
        .panel-tab[draggable="true"] { cursor:grab; }
        .panel-tab.dragging { opacity:.45; cursor:grabbing; }
        .panel-tab.drop-before { box-shadow:inset 3px 0 var(--primary-color); }
        .panel-tab.drop-after { box-shadow:inset -3px 0 var(--primary-color); }
        .tab-name-input { box-sizing:border-box; width:120px; min-width:72px;
          padding:6px 8px; border:1px solid var(--primary-color); border-radius:4px;
          color:var(--primary-text-color); font:inherit;
          background:var(--card-background-color, var(--primary-background-color)); }
        main { display:flex; flex:1; min-width:0; min-height:0; overflow:hidden; }
        .panel-view { flex:1; min-width:0; min-height:0; }
        .message { padding:24px; }
        dialog { box-sizing:border-box; width:min(560px, calc(100vw - 32px));
          max-height:min(720px, calc(100vh - 32px)); padding:0; border:0;
          border-radius:12px; color:var(--primary-text-color);
          background:var(--card-background-color, var(--primary-background-color));
          box-shadow:var(--ha-card-box-shadow, 0 8px 32px rgba(0,0,0,.35)); }
        dialog::backdrop { background:rgba(0,0,0,.45); }
        .dialog-content { display:flex; flex-direction:column; max-height:inherit; }
        .dialog-header { padding:20px 24px 12px; font-size:22px; font-weight:500; }
        .dialog-body { overflow:auto; padding:8px 24px 16px; }
        .dialog-actions { display:flex; justify-content:flex-end; gap:8px; padding:12px 16px; }
        .selection-actions { display:flex; gap:8px; margin:12px 0; }
        #import-panels { display:grid; gap:8px; margin:12px 0; }
        .import-panel { display:flex; align-items:center; gap:10px; min-height:36px; }
        .import-panel small { color:var(--secondary-text-color); }
        .import-warning { color:var(--warning-color, #ff9800); }
        .layout-option { display:flex; align-items:center; gap:10px; margin-top:16px; }
        @media (max-width:600px) {
          header { gap:8px; padding:0 8px; }
          .brand { display:none; }
          #panel-tabs { margin-inline-start:0; }
          .panel-tab { padding:0 14px; }
        }
      </style>
      <header>
        <ha-button id="menu" appearance="plain" aria-label="Toggle sidebar" title="Toggle sidebar">
          <ha-icon icon="mdi:menu"></ha-icon>
        </ha-button>
        <img class="brand" src="/wiser/wiser-logo.png" alt="Wiser">
        <nav id="panel-tabs" role="tablist" aria-label="Wiser panels" hidden></nav>
        <div id="panel-actions" hidden>
          <ha-button id="export-config" appearance="plain" aria-label="Export panel configuration" title="Export panel configuration">
            <ha-icon icon="mdi:download"></ha-icon>
          </ha-button>
          <ha-button id="import-config" appearance="plain" aria-label="Import panel configuration" title="Import panel configuration">
            <ha-icon icon="mdi:upload"></ha-icon>
          </ha-button>
          <ha-button id="settings" appearance="plain" aria-label="Configure panel" title="Configure panel" hidden>
            <ha-icon icon="mdi:cog"></ha-icon>
          </ha-button>
        </div>
      </header>
      <main><p class="message" role="status">Loading Wiser…</p></main>
      <input id="import-file" type="file" accept="application/json,.json" hidden>
      <dialog id="import-dialog" aria-labelledby="import-title">
        <div class="dialog-content">
          <div class="dialog-header" id="import-title">Import panel configuration</div>
          <div class="dialog-body">
            <div id="import-summary"></div>
            <div class="selection-actions">
              <ha-button id="select-all" appearance="plain">Select all</ha-button>
              <ha-button id="select-none" appearance="plain">Select none</ha-button>
            </div>
            <div id="import-panels"></div>
            <label class="layout-option">
              <input id="import-layout" type="checkbox">
              Restore panel order and titles
            </label>
            <p id="import-warning" class="import-warning" hidden></p>
          </div>
          <div class="dialog-actions">
            <ha-button id="cancel-import" appearance="plain">Cancel</ha-button>
            <ha-button id="confirm-import">Import selected</ha-button>
          </div>
        </div>
      </dialog>`;
    this.shadowRoot.getElementById("menu").addEventListener("click", () => {
      this.dispatchEvent(new CustomEvent("hass-toggle-menu", { bubbles:true, composed:true }));
    });
    this.shadowRoot.getElementById("settings").addEventListener("click", () => {
      const view = this._views.find((candidate) => !candidate.hidden);
      if (typeof view?._openEditor === "function") void view._openEditor();
    });
    this.shadowRoot.getElementById("export-config").addEventListener("click", () => {
      this._exportConfiguration();
    });
    this.shadowRoot.getElementById("import-config").addEventListener("click", () => {
      this.shadowRoot.getElementById("import-file").click();
    });
    this.shadowRoot.getElementById("import-file").addEventListener("change", (event) => {
      const [file] = event.target.files || [];
      event.target.value = "";
      if (file) void this._prepareImport(file);
    });
    this.shadowRoot.getElementById("select-all").addEventListener("click", () => {
      this._selectImportPanels(true);
    });
    this.shadowRoot.getElementById("select-none").addEventListener("click", () => {
      this._selectImportPanels(false);
    });
    this.shadowRoot.getElementById("cancel-import").addEventListener("click", () => {
      this.shadowRoot.getElementById("import-dialog").close();
    });
    this.shadowRoot.getElementById("confirm-import").addEventListener("click", () => {
      void this._importConfiguration();
    });
    this._views = [];
    this._tabs = [];
    this._generation = 0;
    this._draggedPanelId = undefined;
    try {
      this._activePanel = window.sessionStorage.getItem(WISER_ACTIVE_PANEL_KEY) || undefined;
    } catch (_error) {
      this._activePanel = undefined;
    }
  }

  set hass(hass) {
    this._hass = hass;
    this._syncSettings();
    this._syncTabEditing();
    for (const view of this._views) {
      if (!view.hidden) view.hass = hass;
    }
  }

  set panel(panel) {
    if (!this._tabPreferences) {
      this._tabPreferences = panel.config.panels.map(({ id, title }) => ({
        id,
        title,
      }));
    }
    const config = this._mergeTabPreferences(panel.config);
    if (JSON.stringify(config) === JSON.stringify(this._config)) return;
    this._config = config;
    void this._loadPanels();
  }

  _mergeTabPreferences(config) {
    const preferences = new Map(
      this._tabPreferences.map((tab, index) => [tab.id, { ...tab, index }])
    );
    const discoveredOrder = new Map(
      config.panels.map((panel, index) => [panel.id, index])
    );
    const panels = config.panels
      .map((panel) => ({
        ...panel,
        title: preferences.get(panel.id)?.title || panel.title,
      }))
      .sort((left, right) => {
        const leftOrder = preferences.get(left.id)?.index;
        const rightOrder = preferences.get(right.id)?.index;
        return (
          (leftOrder ?? preferences.size + discoveredOrder.get(left.id)) -
          (rightOrder ?? preferences.size + discoveredOrder.get(right.id))
        );
      });
    return { ...config, panels };
  }

  _selectPanel(id) {
    this._activePanel = id;
    try {
      window.sessionStorage.setItem(WISER_ACTIVE_PANEL_KEY, id);
    } catch (_error) {
      // Session storage can be unavailable in restricted browser contexts.
    }
    this._views.forEach((view, index) => {
      const selected = this._config.panels[index].id === id;
      view.hidden = !selected;
      if (selected) view.hass = this._hass;
      this._tabs[index].setAttribute("aria-selected", String(selected));
      this._tabs[index].tabIndex = selected ? 0 : -1;
    });
    this._syncSettings();
  }

  _syncSettings() {
    const view = this._views.find((candidate) => !candidate.hidden);
    this.shadowRoot.getElementById("panel-actions").hidden = !(
      this._hass?.user?.is_admin && this._config?.panels?.length
    );
    this.shadowRoot.getElementById("settings").hidden = !(
      this._hass?.user?.is_admin && typeof view?._openEditor === "function"
    );
  }

  _notify(message) {
    this.dispatchEvent(
      new CustomEvent("hass-notification", {
        bubbles: true,
        composed: true,
        detail: { message },
      })
    );
  }

  _exportConfiguration() {
    if (!this._hass?.user?.is_admin || !this._config?.panels) return;
    const panels = Object.fromEntries(
      this._config.panels.map((panel) => [
        panel.id,
        {
          title: panel.title,
          configs: panel.config?.card_configs || {},
        },
      ])
    );
    const payload = {
      format: this._config.export_format || "wiser-panel-config",
      version: this._config.export_version || 1,
      exported_at: new Date().toISOString(),
      tabs: this._config.panels.map(({ id, title }) => ({ id, title })),
      panels,
    };
    const blob = new Blob([`${JSON.stringify(payload, null, 2)}\n`], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `wiser-panels-${new Date().toISOString().slice(0, 10)}.json`;
    link.click();
    URL.revokeObjectURL(url);
  }

  async _prepareImport(file) {
    try {
      if (file.size > 2 * 1024 * 1024) {
        throw new Error("The Wiser panel configuration file is too large.");
      }
      const payload = JSON.parse(await file.text());
      const format = this._config.export_format || "wiser-panel-config";
      const version = this._config.export_version || 1;
      if (
        !payload ||
        Array.isArray(payload) ||
        payload.format !== format ||
        payload.version !== version ||
        !payload.panels ||
        Array.isArray(payload.panels) ||
        typeof payload.panels !== "object"
      ) {
        throw new Error("This is not a supported Wiser panel configuration file.");
      }
      this._importPayload = payload;
      this._renderImportOptions();
      this.shadowRoot.getElementById("import-dialog").showModal();
    } catch (error) {
      this._notify(error?.message || "Unable to read the Wiser panel configuration file.");
    }
  }

  _renderImportOptions() {
    const container = this.shadowRoot.getElementById("import-panels");
    const currentPanels = new Map(
      this._config.panels.map((panel) => [panel.id, panel])
    );
    const rows = [];
    let available = 0;
    for (const [panelId, saved] of Object.entries(this._importPayload.panels)) {
      const current = currentPanels.get(panelId);
      const row = document.createElement("label");
      row.className = "import-panel";
      const checkbox = document.createElement("input");
      checkbox.type = "checkbox";
      checkbox.dataset.panelId = panelId;
      checkbox.disabled = !current;
      checkbox.checked = Boolean(current);
      const label = document.createElement("span");
      label.textContent = saved?.title || current?.title || panelId;
      row.append(checkbox, label);
      if (!current) {
        const unavailable = document.createElement("small");
        unavailable.textContent = "Not installed";
        row.append(unavailable);
      } else {
        available += 1;
      }
      rows.push(row);
    }
    container.replaceChildren(...rows);
    const total = Object.keys(this._importPayload.panels).length;
    this.shadowRoot.getElementById("import-summary").textContent =
      `${available} of ${total} saved panels are available to import.`;
    const hasLayout = Array.isArray(this._importPayload.tabs);
    const layout = this.shadowRoot.getElementById("import-layout");
    layout.checked = hasLayout;
    layout.disabled = !hasLayout;
    this.shadowRoot.getElementById("import-warning").hidden = true;
  }

  _selectImportPanels(selected) {
    for (const checkbox of this.shadowRoot.querySelectorAll(
      '#import-panels input[type="checkbox"]:not(:disabled)'
    )) {
      checkbox.checked = selected;
    }
  }

  async _importConfiguration() {
    if (!this._hass?.user?.is_admin || !this._importPayload) return;
    const button = this.shadowRoot.getElementById("confirm-import");
    const warning = this.shadowRoot.getElementById("import-warning");
    const currentPanelIds = new Set(this._config.panels.map((panel) => panel.id));
    const currentHubs = new Set(
      this._config.panels.flatMap((panel) => panel.config?.hubs || [])
    );
    const selected = [...this.shadowRoot.querySelectorAll(
      '#import-panels input[type="checkbox"]:checked:not(:disabled)'
    )].map((checkbox) => checkbox.dataset.panelId);
    const panels = {};
    const skippedHubs = new Set();
    for (const panelId of selected) {
      const saved = this._importPayload.panels[panelId];
      if (
        !saved ||
        !saved.configs ||
        typeof saved.configs !== "object" ||
        Array.isArray(saved.configs)
      ) {
        warning.textContent = `The saved ${panelId} panel configuration is invalid.`;
        warning.hidden = false;
        return;
      }
      panels[panelId] = {};
      for (const [hub, config] of Object.entries(saved.configs)) {
        if (currentHubs.has(hub)) panels[panelId][hub] = config;
        else skippedHubs.add(hub);
      }
    }

    const restoreLayout = this.shadowRoot.getElementById("import-layout").checked;
    let tabs;
    if (restoreLayout) {
      const importedTabs = this._importPayload.tabs
        .filter((tab) => currentPanelIds.has(tab?.id) && typeof tab?.title === "string")
        .map(({ id, title }) => ({ id, title }));
      const importedIds = new Set(importedTabs.map((tab) => tab.id));
      tabs = [
        ...importedTabs,
        ...this._config.panels
          .filter((panel) => !importedIds.has(panel.id))
          .map(({ id, title }) => ({ id, title })),
      ];
    }
    if (selected.length === 0 && !tabs) {
      warning.textContent = "Select at least one panel or restore the panel layout.";
      warning.hidden = false;
      return;
    }

    button.disabled = true;
    try {
      const message = { type: "wiser/panel/import", panels };
      if (tabs) message.tabs = tabs;
      await this._hass.callWS(message);
      if (tabs) this._tabPreferences = tabs;
      this.shadowRoot.getElementById("import-dialog").close();
      const skipped = skippedHubs.size
        ? ` Settings for unavailable hubs were skipped: ${[...skippedHubs].join(", ")}.`
        : "";
      this._notify(`Imported ${selected.length} Wiser panel configuration(s).${skipped}`);
    } catch (error) {
      warning.textContent = error?.message || "Unable to import panel configuration.";
      warning.hidden = false;
    } finally {
      button.disabled = false;
    }
  }

  _syncTabEditing() {
    const editable = Boolean(this._hass?.user?.is_admin);
    for (const tab of this._tabs) {
      tab.draggable = editable;
      tab.title = editable
        ? "Drag to reorder. Double-click to rename."
        : "";
    }
  }

  _clearDropIndicators() {
    for (const tab of this._tabs) {
      tab.classList.remove("drop-before", "drop-after");
    }
  }

  _applyPanels(panels) {
    const viewsById = new Map(
      this._config.panels.map((panel, index) => [panel.id, this._views[index]])
    );
    this._tabPreferences = panels.map(({ id, title }) => ({ id, title }));
    this._config = { ...this._config, panels };
    this._views = panels.map((panel) => viewsById.get(panel.id));
    this.shadowRoot.querySelector("main").replaceChildren(...this._views);
    this._renderTabs();
  }

  async _persistTabs(previousPanels) {
    try {
      await this._hass.callWS({
        type: "wiser/panel/configure_tabs",
        tabs: this._config.panels.map(({ id, title }) => ({ id, title })),
      });
    } catch (error) {
      this._applyPanels(previousPanels);
      this.dispatchEvent(
        new CustomEvent("hass-notification", {
          bubbles: true,
          composed: true,
          detail: {
            message: "Unable to save the Wiser panel tab layout.",
          },
        })
      );
      console.error("Unable to save Wiser panel tabs", error);
    }
  }

  _movePanel(panelId, targetId, after) {
    if (!this._hass?.user?.is_admin || panelId === targetId) return;
    const previousPanels = [...this._config.panels];
    const panels = [...previousPanels];
    const sourceIndex = panels.findIndex((panel) => panel.id === panelId);
    if (sourceIndex < 0) return;
    const [panel] = panels.splice(sourceIndex, 1);
    const targetIndex = panels.findIndex((candidate) => candidate.id === targetId);
    if (targetIndex < 0) return;
    panels.splice(targetIndex + (after ? 1 : 0), 0, panel);
    if (panels.every((candidate, index) => candidate === previousPanels[index])) return;
    this._applyPanels(panels);
    void this._persistTabs(previousPanels);
  }

  _startRename(panelId, tab) {
    if (!this._hass?.user?.is_admin || tab.querySelector("input")) return;
    const panel = this._config.panels.find((candidate) => candidate.id === panelId);
    if (!panel) return;

    const input = document.createElement("input");
    input.className = "tab-name-input";
    input.value = panel.title;
    input.maxLength = 64;
    input.setAttribute("aria-label", `Rename ${panel.title} tab`);
    input.addEventListener("click", (event) => event.stopPropagation());
    input.addEventListener("dblclick", (event) => event.stopPropagation());

    let finished = false;
    const finish = (save) => {
      if (finished) return;
      finished = true;
      const title = input.value.trim() || panel.default_title || panel.title;
      if (!save || title === panel.title) {
        tab.textContent = panel.title;
        this._syncTabEditing();
        return;
      }
      const previousPanels = this._config.panels.map((item) => ({ ...item }));
      const panels = this._config.panels.map((item) =>
        item.id === panelId ? { ...item, title } : item
      );
      this._applyPanels(panels);
      void this._persistTabs(previousPanels);
    };

    input.addEventListener("keydown", (event) => {
      event.stopPropagation();
      if (event.key === "Enter") {
        event.preventDefault();
        finish(true);
      } else if (event.key === "Escape") {
        event.preventDefault();
        finish(false);
      }
    });
    input.addEventListener("blur", () => finish(true));
    tab.draggable = false;
    tab.replaceChildren(input);
    input.focus();
    input.select();
  }

  _renderTabs() {
    const panels = this._config.panels;
    const container = this.shadowRoot.getElementById("panel-tabs");
    container.hidden = panels.length === 0;
    this._tabs = panels.map((panel, index) => {
      const tab = document.createElement("button");
      tab.type = "button";
      tab.className = "panel-tab";
      tab.textContent = panel.title;
      tab.id = `wiser-panel-tab-${index}`;
      tab.setAttribute("role", "tab");
      tab.setAttribute("aria-controls", `wiser-panel-view-${index}`);
      tab.addEventListener("click", () => this._selectPanel(panel.id));
      tab.addEventListener("dblclick", (event) => {
        event.preventDefault();
        this._startRename(panel.id, tab);
      });
      tab.addEventListener("dragstart", (event) => {
        if (!this._hass?.user?.is_admin) {
          event.preventDefault();
          return;
        }
        this._draggedPanelId = panel.id;
        tab.classList.add("dragging");
        event.dataTransfer.effectAllowed = "move";
        event.dataTransfer.setData("text/plain", panel.id);
      });
      tab.addEventListener("dragover", (event) => {
        if (!this._draggedPanelId || this._draggedPanelId === panel.id) return;
        event.preventDefault();
        event.dataTransfer.dropEffect = "move";
        this._clearDropIndicators();
        const bounds = tab.getBoundingClientRect();
        const after = event.clientX >= bounds.left + bounds.width / 2;
        tab.classList.add(after ? "drop-after" : "drop-before");
      });
      tab.addEventListener("drop", (event) => {
        if (!this._draggedPanelId) return;
        event.preventDefault();
        const bounds = tab.getBoundingClientRect();
        const after = event.clientX >= bounds.left + bounds.width / 2;
        const draggedPanelId = this._draggedPanelId;
        this._draggedPanelId = undefined;
        this._clearDropIndicators();
        this._movePanel(draggedPanelId, panel.id, after);
      });
      tab.addEventListener("dragend", () => {
        this._draggedPanelId = undefined;
        this._clearDropIndicators();
        tab.classList.remove("dragging");
      });
      tab.addEventListener("keydown", (event) => {
        let next;
        if (event.key === "ArrowRight") next = (index + 1) % panels.length;
        else if (event.key === "ArrowLeft") next = (index + panels.length - 1) % panels.length;
        else if (event.key === "Home") next = 0;
        else if (event.key === "End") next = panels.length - 1;
        else return;
        event.preventDefault();
        this._selectPanel(panels[next].id);
        this._tabs[next].focus();
      });
      const view = this._views[index];
      view.id = `wiser-panel-view-${index}`;
      view.setAttribute("role", "tabpanel");
      view.setAttribute("aria-labelledby", tab.id);
      return tab;
    });
    container.replaceChildren(...this._tabs);
    this._syncTabEditing();
    const selected = panels.some((panel) => panel.id === this._activePanel)
      ? this._activePanel : panels[0]?.id;
    if (selected) this._selectPanel(selected);
  }

  async _loadPanels() {
    const generation = ++this._generation;
    const main = this.shadowRoot.querySelector("main");
    try {
      for (const panel of this._config.panels) {
        if (!customElements.get(panel.component)) await import(panel.module_url);
        await customElements.whenDefined(panel.component);
      }
      if (generation !== this._generation) return;
      this._views = this._config.panels.map((panel) => {
        const view = document.createElement(panel.component);
        view.className = "panel-view";
        view.setAttribute("nested", "");
        view.hass = this._hass;
        view.panel = { config: panel.config };
        return view;
      });
      main.replaceChildren(...this._views);
      this._renderTabs();
    } catch (error) {
      if (generation !== this._generation) return;
      this._views = [];
      this.shadowRoot.getElementById("panel-tabs").hidden = true;
      const message = document.createElement("p");
      message.className = "message";
      message.setAttribute("role", "alert");
      message.textContent = error?.message || "Unable to load Wiser panels.";
      main.replaceChildren(message);
      console.error("Unable to load Wiser panels", error);
    }
  }
}

if (!customElements.get("wiser-panel")) {
  customElements.define("wiser-panel", WiserPanel);
}
