const FEATURE_TYPE = "opentherm-hot-water-control-modes-feature";
const PRESETS_FEATURE_TYPE =
  "opentherm-hot-water-control-presets-feature";
const MORE_INFO_TYPE = "opentherm-hot-water-control-more-info";
const NATIVE_TEMPERATURE_CONTROL =
  "ha-state-control-water_heater-temperature";
const DEFAULT_MAX_WIDTH = 560;
const PRESETS_ATTRIBUTE = "opentherm_presets";
const PRESETS_SELECTOR_KEY = "opentherm_presets_v2";
const PRESETS_SELECTOR_TYPE = `ha-selector-${PRESETS_SELECTOR_KEY}`;
const PRESETS_DIALOG_TYPE = "opentherm-presets-dialog-v2";
const MAX_PRESETS = 10;
const MDI_ARROW_LEFT =
  "M20,11V13H8L13.5,18.5L12.08,19.92L4.16,12L12.08,4.08L13.5,5.5L8,11H20Z";

const localize = (hass, key, fallback, replacements) =>
  hass?.localize?.(key, replacements) || fallback;

const showTemperatureError = (element, error) => {
  element.dispatchEvent(new CustomEvent("hass-notification", {
    bubbles: true,
    composed: true,
    detail: { message: error?.message || "Unable to change hot-water temperature.", duration: 10000 },
  }));
};

const clonePresets = (presets) =>
  Array.isArray(presets)
    ? presets.map((preset) => ({ ...preset }))
    : [];

const presetIcon = (presets, index) => {
  const preset = presets[index];
  const configuredIcon = String(preset?.icon || "").trim();
  if (configuredIcon) {
    return configuredIcon;
  }
  return `mdi:numeric-${Math.max(1, index + 1)}`;
};

class OpenThermTemperatureSourceSelector extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._formChanged = (event) => {
      if (event.target !== this._form) return;
      const device = event.detail?.value?.device_id;
      if (device === this._device) return;
      this._device = device;
      this._value = { mode: this._isWiser() ? "wiser" : "custom", entity_id: this._customEntity };
      this._update();
      // Let the outer form finish applying its device change before our update.
      queueMicrotask(() => { if (this.isConnected) this._emit(); });
    };
  }

  set hass(value) { this._hass = value; this._update(); }
  set selector(value) {
    this._selector = value?.opentherm_temperature_source || {};
    if (this._device === undefined) this._device = this._selector.device_id;
    this._update();
  }
  set value(value) {
    this._value = value;
    if (value?.mode === "custom") this._customEntity = value.entity_id;
    this._update();
  }
  get value() { return this._value; }
  set label(value) { this._label = value; this._update(); }
  set disabled(value) { this._disabled = value; this._update(); }
  set required(value) { this._required = value; }

  connectedCallback() {
    if (!this._toggle) {
      const style = document.createElement("style");
      style.textContent = `
        :host { display: block; }
        .row { display: flex; align-items: center; gap: 16px; }
        .label { flex: 1; color: var(--primary-text-color); font-size: var(--ha-font-size-m, 14px); }
        ha-button-toggle-group { flex: none; margin-inline-start: auto; }
        ha-selector { display: block; margin-top: 12px; }
        [hidden] { display: none !important; }
      `;
      const row = document.createElement("div");
      row.className = "row";
      this._labelElement = document.createElement("div");
      this._labelElement.className = "label";
      this._toggle = document.createElement("ha-button-toggle-group");
      this._toggle.setAttribute("no-wrap", "");
      this._toggle.addEventListener("value-changed", (event) => {
        event.stopPropagation();
        if (this._disabled) return;
        this._value = { mode: event.detail.value, entity_id: this._customEntity };
        this._update();
        this._emit();
      });
      this._picker = document.createElement("ha-selector");
      this._picker.selector = { entity: { domain: "sensor", device_class: "temperature" } };
      this._picker.addEventListener("value-changed", (event) => {
        event.stopPropagation();
        if (this._disabled) return;
        this._customEntity = event.detail.value;
        this._value = { mode: "custom", entity_id: this._customEntity };
        this._emit();
      });
      row.append(this._labelElement, this._toggle);
      this.shadowRoot.append(style, row, this._picker);
    }
    // ha-form owns the control-device field in a different shadow tree.
    let parent = this.parentNode;
    while (parent) {
      if (parent.localName === "ha-form") { this._form = parent; break; }
      parent = parent.parentNode || parent.host;
    }
    this._form?.addEventListener("value-changed", this._formChanged);
    this._update();
  }

  disconnectedCallback() {
    this._form?.removeEventListener("value-changed", this._formChanged);
    this._form = undefined;
  }

  _isWiser() { return this._selector?.wiser_devices?.includes(this._device) || false; }
  _emit() {
    this.dispatchEvent(new CustomEvent("value-changed", {
      bubbles: true, composed: true, detail: { value: this._value },
    }));
  }
  reportValidity() {
    return this._value?.mode === "wiser" || !this._isWiser() || Boolean(this._customEntity);
  }
  _update() {
    if (!this._toggle) return;
    this._labelElement.textContent = this._label || "Current temperature";
    this._toggle.buttons = [
      { value: "wiser", label: "Wiser" },
      { value: "custom", label: localize(this._hass, "ui.components.entity.entity-name-picker.mode_custom", "Custom") },
    ];
    this._toggle.active = this._value?.mode;
    this._toggle.disabled = Boolean(this._disabled);
    this._toggle.hidden = !this._isWiser();
    this._picker.hidden = this._isWiser() && this._value?.mode === "wiser";
    this._picker.hass = this._hass;
    this._picker.value = this._customEntity;
    this._picker.disabled = Boolean(this._disabled);
    this._picker.required = this._isWiser() && !this._picker.hidden;
  }
}

if (!customElements.get("ha-selector-opentherm_temperature_source")) {
  customElements.define("ha-selector-opentherm_temperature_source", OpenThermTemperatureSourceSelector);
}

class OpenThermFailureNotificationsSelector extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._value = { persistent: false, mobile: false };
  }

  set hass(value) { this._hass = value; this._update(); }
  set selector(value) {
    this._selector = value?.opentherm_failure_notifications || {};
    this._update();
  }
  set value(value) {
    this._value = { persistent: false, mobile: false, ...(value || {}) };
    this._update();
  }
  get value() { return this._value; }
  set label(value) { this._label = value; this._update(); }
  set disabled(value) { this._disabled = value; this._update(); }
  set required(value) { this._required = value; }

  connectedCallback() {
    if (!this._persistentSwitch) {
      const style = document.createElement("style");
      style.textContent = `
        :host { display: block; }
        .heading { color: var(--primary-text-color); font-size: var(--ha-font-size-m, 14px); margin-bottom: 8px; }
        .row { align-items: center; display: flex; min-height: 48px; }
        .row-label { color: var(--primary-text-color); flex: 1; }
        ha-switch { flex: none; }
        ha-selector { display: block; margin: 4px 0 12px; }
        [hidden] { display: none !important; }
      `;
      this._heading = document.createElement("div");
      this._heading.className = "heading";
      const persistentRow = document.createElement("div");
      persistentRow.className = "row";
      const persistentLabel = document.createElement("div");
      persistentLabel.className = "row-label";
      persistentLabel.textContent = "Persistent notification";
      this._persistentSwitch = document.createElement("ha-switch");
      this._persistentSwitch.addEventListener("change", () => {
        if (this._disabled) return;
        this._value = { ...this._value, persistent: this._persistentSwitch.checked };
        this._emit();
      });
      persistentRow.append(persistentLabel, this._persistentSwitch);

      const mobileRow = document.createElement("div");
      mobileRow.className = "row";
      const mobileLabel = document.createElement("div");
      mobileLabel.className = "row-label";
      mobileLabel.textContent = "Mobile notification";
      this._mobileSwitch = document.createElement("ha-switch");
      this._mobileSwitch.addEventListener("change", () => {
        if (this._disabled) return;
        this._value = { ...this._value, mobile: this._mobileSwitch.checked };
        this._update();
        this._emit();
      });
      mobileRow.append(mobileLabel, this._mobileSwitch);

      this._picker = document.createElement("ha-selector");
      this._picker.addEventListener("value-changed", (event) => {
        event.stopPropagation();
        if (this._disabled) return;
        this._value = { ...this._value, mobile_service: event.detail.value };
        this._emit();
      });
      this.shadowRoot.append(style, this._heading, persistentRow, mobileRow, this._picker);
    }
    this._update();
  }

  _emit() {
    this.dispatchEvent(new CustomEvent("value-changed", {
      bubbles: true, composed: true, detail: { value: this._value },
    }));
  }

  reportValidity() {
    return !this._value?.mobile || Boolean(this._value?.mobile_service);
  }

  _update() {
    if (!this._persistentSwitch) return;
    this._heading.textContent = this._label || "Failure notifications";
    this._persistentSwitch.checked = Boolean(this._value?.persistent);
    this._mobileSwitch.checked = Boolean(this._value?.mobile);
    this._persistentSwitch.disabled = Boolean(this._disabled);
    this._mobileSwitch.disabled = Boolean(this._disabled);
    this._picker.hidden = !this._value?.mobile;
    this._picker.hass = this._hass;
    this._picker.selector = {
      select: {
        mode: "dropdown",
        options: this._selector?.mobile_services || [],
      },
    };
    this._picker.value = this._value?.mobile_service;
    this._picker.label = "Mobile device";
    this._picker.disabled = Boolean(this._disabled);
    this._picker.required = Boolean(this._value?.mobile);
  }
}

if (!customElements.get("ha-selector-opentherm_failure_notifications")) {
  customElements.define(
    "ha-selector-opentherm_failure_notifications",
    OpenThermFailureNotificationsSelector
  );
}

class OpenThermPresetsSelector extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  set selector(selector) {
    this._selector = selector?.[PRESETS_SELECTOR_KEY] || selector || {};
  }

  set value(value) {
    this._value = clonePresets(value);
    this._render();
  }

  get value() {
    return this._value;
  }

  set disabled(disabled) {
    this._disabled = disabled;
    this._render();
  }

  set label(label) {
    this._label = label;
    this._updateRenderedState();
  }

  set required(required) {
    this._required = required;
  }

  connectedCallback() {
    this._ensureRendered();
    this._updateRenderedState();
  }

  reportValidity() {
    return true;
  }

  _openPresets() {
    if (this._disabled) {
      return;
    }

    const dialogParams = {
      label: this._label || "Presets",
      presets: clonePresets(this._value),
      minimum: Number(this._selector?.minimum ?? 35),
      maximum: Number(this._selector?.maximum ?? 55),
      saveCallback: (presets) => {
        this._value = clonePresets(presets);
        this.dispatchEvent(
          new CustomEvent("value-changed", {
            bubbles: true,
            composed: true,
            detail: { value: clonePresets(this._value) },
          })
        );
        this._updateRenderedState();
      },
    };
    // The options flow is already hosted inside a Home Assistant dialog. Its
    // dialog manager does not consistently handle a second `show-dialog`
    // event from a custom selector, so mount this editor at document level.
    // Reuse the single editor element between openings to avoid duplicates.
    let dialog = document.body.querySelector(PRESETS_DIALOG_TYPE);
    if (!dialog) {
      dialog = document.createElement(PRESETS_DIALOG_TYPE);
      document.body.append(dialog);
    }
    dialog.hass = this._hass;
    dialog.showDialog(dialogParams);
  }

  _render() {
    if (!this.isConnected) {
      return;
    }

    this._ensureRendered();
    this._updateRenderedState();
  }

  _ensureRendered() {
    if (!this.shadowRoot || this._button) {
      return;
    }

    const style = document.createElement("style");
    style.textContent = `
      :host { display: block; }
      ha-button { width: 100%; }
      .summary {
        color: var(--secondary-text-color);
        font-size: var(--ha-font-size-s, 12px);
        margin-top: var(--ha-space-1, 4px);
      }
    `;

    const button = document.createElement("ha-button");
    button.setAttribute("type", "button");
    button.textContent = "Presets";
    button.addEventListener("click", (event) => {
      event.preventDefault();
      event.stopPropagation();
      this._openPresets();
    });

    const summary = document.createElement("div");
    summary.className = "summary";

    this._button = button;
    this._summary = summary;
    this.shadowRoot.replaceChildren(style, button, summary);
  }

  _updateRenderedState() {
    if (!this._button || !this._summary) {
      return;
    }
    this._button.textContent = this._label || "Presets";
    this._button.disabled = Boolean(this._disabled);
    const count = this._value?.length || 0;
    this._summary.textContent = `${count} of ${MAX_PRESETS} presets configured`;
  }
}

class OpenThermPresetsDialog extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._editingIndex = undefined;
  }

  set hass(hass) {
    this._hass = hass;
  }

  showDialog(params) {
    this._params = params;
    this._minimum = Number.isFinite(params.minimum) ? params.minimum : 35;
    this._maximum = Number.isFinite(params.maximum) ? params.maximum : 55;
    this._presets = clonePresets(params.presets).slice(0, MAX_PRESETS);
    this._editingIndex = undefined;
    this._ensureDialog();
    this._dialog.open = true;
    this._renderContent();
  }

  closeDialog() {
    if (this._dialog) {
      this._dialog.open = false;
    }
    return true;
  }

  _ensureDialog() {
    if (this._dialog) {
      return;
    }

    const style = document.createElement("style");
    style.textContent = `
      .preset-list {
        display: flex;
        flex-direction: column;
        gap: var(--ha-space-2, 8px);
        width: 100%;
      }
      .preset-section {
        display: flex;
        flex-direction: column;
        gap: var(--ha-space-2, 8px);
      }
      .preset-rows {
        display: flex;
        flex-direction: column;
        gap: var(--ha-space-2, 8px);
      }
      .preset-row {
        align-items: center;
        background: var(--secondary-background-color);
        border-radius: var(--ha-border-radius-md, 12px);
        display: grid;
        gap: var(--ha-space-3, 12px);
        grid-template-columns: auto auto minmax(0, 1fr) auto;
        padding: var(--ha-space-3, 12px);
      }
      .drag-handle {
        align-items: center;
        color: var(--secondary-text-color);
        cursor: grab;
        display: flex;
        justify-content: center;
        touch-action: none;
      }
      .drag-handle:active { cursor: grabbing; }
      .preset-row ha-icon { color: var(--primary-color); }
      .preset-name { font-weight: var(--ha-font-weight-medium, 500); }
      .preset-detail {
        color: var(--secondary-text-color);
        font-size: var(--ha-font-size-s, 12px);
        margin-top: 2px;
      }
      .empty {
        color: var(--secondary-text-color);
        padding: var(--ha-space-6, 24px);
        text-align: center;
      }
      .preset-editor-content {
        display: grid;
        gap: var(--ha-space-2, 8px);
        grid-template-columns: minmax(0, 1fr);
        width: 100%;
      }
      .preset-editor-content > * {
        box-sizing: border-box;
        min-width: 0;
        width: 100%;
      }
      .dialog-footer {
        margin-block-end: var(--ha-space-2, 8px);
        margin-inline: var(--ha-space-2, 8px);
      }
      ha-alert { display: block; margin-bottom: var(--ha-space-3, 12px); }
      ha-alert[hidden] { display: none; }
    `;

    const dialog = document.createElement("ha-dialog");
    dialog.addEventListener("closed", () => {
      if (this._editingIndex !== undefined && this._params) {
        this._editingIndex = undefined;
        this._dialog.open = false;
        this._renderContent();
        window.requestAnimationFrame(() => {
          if (this._params) {
            this._dialog.open = true;
          }
        });
        return;
      }
      this._params = undefined;
    });
    this._dialog = dialog;
    this.shadowRoot.replaceChildren(style, dialog);
  }

  _button(label, handler, { primary = false, danger = false } = {}) {
    const button = document.createElement("ha-button");
    button.setAttribute("type", "button");
    button.textContent = label;
    if (primary) {
      button.setAttribute("variant", "brand");
    }
    if (danger) {
      button.setAttribute("variant", "danger");
    }
    button.addEventListener("click", (event) => {
      event.preventDefault();
      event.stopPropagation();
      handler(event);
    });
    return button;
  }

  _movePreset(oldIndex, newIndex) {
    if (
      !Number.isInteger(oldIndex) ||
      !Number.isInteger(newIndex) ||
      oldIndex === newIndex ||
      oldIndex < 0 ||
      newIndex < 0
    ) {
      return;
    }
    const [moved] = this._presets.splice(oldIndex, 1);
    if (!moved) {
      return;
    }
    this._presets.splice(newIndex, 0, moved);
    this._renderContent();
  }

  _returnToList() {
    this._editingIndex = undefined;
    this._renderContent();
  }

  _renderContent() {
    if (!this._dialog || !this._params) {
      return;
    }

    if (this._editingIndex === undefined) {
      this._renderList();
    } else {
      this._renderEditor();
    }
  }

  _renderList() {
    this._dialog.setAttribute(
      "header-title",
      this._params.label || "Presets"
    );
    const content = document.createElement("div");
    content.className = "preset-list";

    if (!this._presets.length) {
      const empty = document.createElement("div");
      empty.className = "empty";
      empty.textContent = "No presets configured";
      content.append(empty);
    }

    let rows;
    if (this._presets.length) {
      const section = document.createElement("div");
      section.className = "preset-section";
      const sortable = document.createElement("ha-sortable");
      sortable.setAttribute("handle-selector", ".drag-handle");
      sortable.setAttribute("draggable-selector", ".preset-row");
      sortable.setAttribute("group", "opentherm-presets");
      sortable.addEventListener("item-moved", (event) => {
        event.stopPropagation();
        const { oldIndex, newIndex } = event.detail || {};
        this._movePreset(Number(oldIndex), Number(newIndex));
      });
      rows = document.createElement("div");
      rows.className = "preset-rows";
      sortable.append(rows);
      section.append(sortable);
      content.append(section);
    }

    this._presets.forEach((preset, index) => {
      const row = document.createElement("div");
      row.className = "preset-row";

      const icon = document.createElement("ha-icon");
      icon.setAttribute("icon", presetIcon(this._presets, index));

      const handle = document.createElement("div");
      handle.className = "drag-handle";
      handle.setAttribute("title", `Drag to reorder ${preset.name}`);
      handle.setAttribute("aria-label", `Drag to reorder ${preset.name}`);
      const handleIcon = document.createElement("ha-icon");
      handleIcon.setAttribute("icon", "mdi:drag-horizontal-variant");
      handle.append(handleIcon);

      const text = document.createElement("div");
      const name = document.createElement("div");
      name.className = "preset-name";
      name.textContent = preset.name;
      const detail = document.createElement("div");
      detail.className = "preset-detail";
      const duration = Number(preset.duration_minutes) || 0;
      const temperature = Number(preset.temperature);
      detail.textContent = `${
        Number.isFinite(temperature) ? temperature : preset.temperature
      } °C${duration ? ` · ${duration} min` : ""}`;
      text.append(name, detail);

      const edit = this._button(
        localize(this._hass, "ui.common.edit", "Edit"),
        () => {
          this._editingIndex = index;
          this._draft = { ...preset };
          this._renderContent();
        }
      );
      edit.setAttribute("appearance", "plain");
      row.append(handle, icon, text, edit);
      rows?.append(row);
    });

    if (this._presets.length < MAX_PRESETS) {
      const add = this._button(
        localize(this._hass, "ui.common.add", "Add"),
        () => {
          this._editingIndex = -1;
          this._draft = {
            name: "",
            icon: "mdi:water",
            temperature: Math.min(Math.max(45, this._minimum), this._maximum),
            duration_minutes: 0,
          };
          this._renderContent();
        }
      );
      content.append(add);
    }

    const cancel = this._button(
      localize(this._hass, "ui.common.cancel", "Cancel"),
      () => this.closeDialog()
    );
    cancel.setAttribute("appearance", "plain");
    const apply = this._button(
      localize(this._hass, "ui.common.apply", "Apply"),
      () => {
        this._params.saveCallback(clonePresets(this._presets));
        this.closeDialog();
      },
      { primary: true }
    );
    const footer = document.createElement("div");
    footer.className = "dialog-footer";
    footer.setAttribute("slot", "footer");
    footer.append(cancel, apply);

    this._dialog.replaceChildren(content, footer);
  }

  _renderEditor() {
    const isNew = this._editingIndex === -1;
    this._dialog.setAttribute(
      "header-title",
      isNew
        ? "Add preset"
        : String(this._draft?.name || "").trim() || "Preset"
    );

    const content = document.createElement("div");
    content.className = "preset-editor-content";
    const alert = document.createElement("ha-alert");
    alert.setAttribute("alert-type", "error");
    alert.hidden = true;
    content.append(alert);

    const form = document.createElement("ha-form");
    form.hass = this._hass;
    form.data = { ...this._draft };
    // Keep the native HA form controls, but use a compact grid row gap in
    // this small editor instead of the standard 24px form-grid spacing.
    form.style.setProperty(
      "--ha-space-6",
      "var(--ha-space-2, 8px)"
    );
    const buildSchema = () => [
      {
        name: "",
        type: "grid",
        column_min_width: "240px",
        schema: [
          { name: "name", required: true, selector: { text: {} } },
          {
            name: "icon",
            required: false,
            selector: { icon: {} },
          },
          {
            name: "temperature",
            required: true,
            selector: {
              number: {
                min: this._minimum,
                max: this._maximum,
                step: 1,
                mode: "box",
                unit_of_measurement: "°C",
              },
            },
          },
          {
            name: "duration_minutes",
            required: true,
            selector: {
              number: {
                min: 0,
                max: 999,
                step: 1,
                mode: "box",
                unit_of_measurement: "min",
              },
            },
          },
        ],
      },
    ];
    form.schema = buildSchema();
    const labels = {
      name: localize(this._hass, "ui.common.name", "Name"),
      icon: localize(
        this._hass,
        "ui.components.selectors.selector.types.icon",
        "Icon"
      ),
      temperature: localize(
        this._hass,
        "ui.dialogs.more_info_control.climate.temperature",
        "Temperature"
      ),
      duration_minutes: localize(
        this._hass,
        "ui.components.selectors.selector.types.duration",
        "Duration"
      ),
    };
    form.computeLabel = (schema) => labels[schema.name] || schema.name;
    form.addEventListener("value-changed", (event) => {
      this._draft = { ...event.detail.value };
      if (!isNew) {
        this._dialog.setAttribute(
          "header-title",
          String(this._draft.name || "").trim() || "Preset"
        );
      }
      alert.hidden = true;
    });

    this._forms = [form];
    this._alert = alert;
    content.append(form);

    const cancel = this._button(
      localize(this._hass, "ui.common.cancel", "Cancel"),
      () => this._returnToList()
    );
    cancel.setAttribute("appearance", "plain");
    const save = this._button(
      localize(this._hass, "ui.common.save", "Save"),
      () => this._saveDraft(),
      { primary: true }
    );
    const footer = document.createElement("div");
    footer.className = "dialog-footer";
    footer.setAttribute("slot", "footer");
    if (!isNew) {
      const remove = this._button(
        localize(this._hass, "ui.common.delete", "Delete"),
        () => {
          this._presets.splice(this._editingIndex, 1);
          this._editingIndex = undefined;
          this._renderContent();
        },
        { danger: true }
      );
      remove.style.marginInlineEnd = "auto";
      footer.append(remove);
    }
    footer.append(cancel, save);

    const headerBack = document.createElement("ha-icon-button");
    headerBack.path = MDI_ARROW_LEFT;
    headerBack.label = localize(this._hass, "ui.common.back", "Back");
    headerBack.setAttribute("slot", "headerNavigationIcon");
    headerBack.addEventListener("click", (event) => {
      event.preventDefault();
      event.stopPropagation();
      this._returnToList();
    });
    this._dialog.replaceChildren(content, footer, headerBack);
  }

  _saveDraft() {
    if (
      this._forms?.some(
        (form) => form.reportValidity && !form.reportValidity()
      )
    ) {
      return;
    }

    const preset = {
      name: String(this._draft.name || "").trim(),
      icon: String(this._draft.icon || "").trim(),
      temperature: Number(this._draft.temperature),
      duration_minutes: Math.max(
        0,
        Math.min(999, Number(this._draft.duration_minutes) || 0)
      ),
    };
    const duplicate = this._presets.some(
      (item, index) =>
        index !== this._editingIndex &&
        String(item.name).trim().toLocaleLowerCase() ===
          preset.name.toLocaleLowerCase()
    );
    const reserved = ["off", "manual", "auto", "custom"].includes(
      preset.name.toLowerCase()
    );
    if (
      !preset.name ||
      !Number.isFinite(preset.temperature) ||
      preset.temperature < this._minimum ||
      preset.temperature > this._maximum ||
      duplicate || reserved
    ) {
      this._alert.textContent = reserved
        ? "Off, Manual, Auto and Custom are reserved names. Choose another preset name."
        : duplicate
        ? "Preset names must be unique."
        : `Enter a name and temperature between ${this._minimum} and ${this._maximum} °C.`;
      this._alert.hidden = false;
      return;
    }

    if (this._editingIndex === -1) {
      this._presets.push(preset);
    } else {
      this._presets[this._editingIndex] = preset;
    }
    this._presets = clonePresets(this._presets);
    this._editingIndex = undefined;
    this._renderContent();
  }
}

if (!customElements.get(PRESETS_SELECTOR_TYPE)) {
  customElements.define(PRESETS_SELECTOR_TYPE, OpenThermPresetsSelector);
}

if (!customElements.get(PRESETS_DIALOG_TYPE)) {
  customElements.define(PRESETS_DIALOG_TYPE, OpenThermPresetsDialog);
}

const PRIMARY_MODES = ["off", "Manual", "Auto"];
const WATER_HEATER_OPERATION_MODE = 2;

const BOOST_MODES = [
  "Boost 15 Mins",
  "Boost 30 Mins",
  "Boost 45 Mins",
];

const MODE_ICONS = {
  off: "mdi:power",
  Manual: "mdi:water-thermometer",
  Auto: "mdi:calendar-clock",
  "Shower 1": "mdi:shower-head",
  "Shower 2": "mdi:shower",
  "Boost 15 Mins": "mdi:numeric-1",
  "Boost 30 Mins": "mdi:numeric-2",
  "Boost 45 Mins": "mdi:numeric-3",
};

const supportsWaterHeater = (hass, context) => {
  const entityId = context?.entity_id;
  const stateObj = entityId ? hass.states[entityId] : undefined;
  const supportedFeatures = Number(
    stateObj?.attributes?.supported_features || 0
  );
  return Boolean(
    entityId?.startsWith("water_heater.") &&
      stateObj &&
      ((supportedFeatures & WATER_HEATER_OPERATION_MODE) !== 0 ||
        Array.isArray(stateObj.attributes.operation_list))
  );
};

const entityOperationModes = (stateObj, presetNames) => {
  const operationList = stateObj?.attributes?.operation_list;
  if (Array.isArray(operationList) && operationList.length) {
    return operationList;
  }
  return presetNames.length
    ? [...new Set(["off", "Manual", ...presetNames])]
    : PRIMARY_MODES;
};

class OpenThermHotWaterControlModesCardFeature extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._valueChanged = this._valueChanged.bind(this);
  }

  static getStubConfig() {
    return { type: `custom:${FEATURE_TYPE}` };
  }

  setConfig(config) {
    if (!config) {
      throw new Error("Invalid configuration");
    }
    this._config = config;
    this._render();
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  get hass() {
    return this._hass;
  }

  set context(context) {
    this._context = context;
    this._render();
  }

  get context() {
    return this._context;
  }

  connectedCallback() {
    this._render();
  }

  get _stateObj() {
    const entityId = this._context?.entity_id;
    return entityId && this._hass ? this._hass.states[entityId] : undefined;
  }

  _availableModes(stateObj) {
    const entityModes = entityOperationModes(
      stateObj,
      this._presetNames(stateObj)
    );
    // Keep the main native-style control limited to the three operating
    // modes. Presets have their own dropdown feature, including when an older
    // tile configuration stored preset names in operation_modes.
    return PRIMARY_MODES.filter((mode) => entityModes.includes(mode));
  }

  _presetData(stateObj = this._stateObj) {
    const presets = stateObj?.attributes?.[PRESETS_ATTRIBUTE];
    if (!Array.isArray(presets)) {
      return [];
    }

    return presets
      .map((preset) => {
        if (!preset || typeof preset !== "object") {
          return null;
        }

        const name = typeof preset.name === "string" ? preset.name.trim() : "";
        if (!name) {
          return null;
        }

        return {
          name,
          icon:
            typeof preset.icon === "string" && preset.icon.trim()
              ? preset.icon.trim()
              : MODE_ICONS[name],
        };
      })
      .filter(Boolean);
  }

  _presetNames(stateObj = this._stateObj) {
    const presets = this._presetData(stateObj);
    if (presets.length > 0) {
      return presets.map((preset) => preset.name);
    }

    return (
      stateObj?.attributes?.preset_modes ?? []
    );
  }

  _option(mode) {
    const icon = document.createElement("ha-icon");
    const iconSrc = this._presetData().find((preset) => preset.name === mode)?.icon;
    icon.setAttribute("icon", iconSrc || MODE_ICONS[mode] || "mdi:water");
    return {
      value: mode,
      label: mode,
      ariaLabel: mode,
      icon,
    };
  }

  async _valueChanged(event) {
    event.stopPropagation();
    const stateObj = this._stateObj;
    const value = event.detail?.item?.value ?? event.detail?.value;
    if (!stateObj || !value) {
      return;
    }

    try {
      if (value === "off") {
        await this._hass.callService("water_heater", "turn_off", {
          entity_id: stateObj.entity_id,
        });
        return;
      }

      await this._hass.callService("water_heater", "set_operation_mode", {
        entity_id: stateObj.entity_id,
        operation_mode: value,
      });
    } catch (error) {
      showTemperatureError(this, error);
      this._renderSignature = undefined;
      this._render();
    }
  }

  _render() {
    if (!this.shadowRoot) {
      return;
    }

    const stateObj = this._stateObj;
    if (
      !this._config ||
      !this._hass ||
      !stateObj ||
      !supportsWaterHeater(this._hass, this._context)
    ) {
      this.shadowRoot.replaceChildren();
      return;
    }

    const availableModes = this._availableModes(stateObj);
    const selectedValue =
      stateObj.state === "Custom"
        ? "Manual"
        : availableModes.includes(stateObj.state)
          ? stateObj.state
          : undefined;
    const renderSignature = JSON.stringify([
      stateObj.state,
      stateObj.state === "unavailable",
      availableModes,
      this._config.max_width,
    ]);
    if (this._select && this._renderSignature === renderSignature) {
      void this._replaceNativeCurrentlyLabel();
      return;
    }

    if (this._select) {
      this._select.options = availableModes.map((mode) => this._option(mode));
      this._select.value = selectedValue;
      this._select.disabled = stateObj.state === "unavailable";
      this._renderSignature = renderSignature;
      void this._replaceNativeCurrentlyLabel();
      return;
    }

    const style = document.createElement("style");
    style.textContent = `
      :host {
        display: block;
        height: var(--feature-height, 42px);
      }
      ha-control-select {
        --control-select-thickness: var(--feature-height, 42px);
        --control-select-border-radius: var(--feature-border-radius, 12px);
        --control-select-color: var(
          --state-water_heater-active-color,
          var(--primary-color)
        );
      }
    `;

    const select = document.createElement("ha-control-select");
    select.options = availableModes.map((mode) => this._option(mode));
    select.value = selectedValue;
    select.label = localize(
      this._hass,
      "ui.card.water_heater.mode",
      "Mode"
    );
    select.hideOptionLabel = true;
    select.disabled = stateObj.state === "unavailable";
    const configuredMaxWidth = Number(this._config.max_width);
    select.style.maxWidth = `${
      Number.isFinite(configuredMaxWidth) && configuredMaxWidth > 0
        ? configuredMaxWidth
        : DEFAULT_MAX_WIDTH
    }px`;
    select.style.marginInline = "auto";
    select.addEventListener("value-changed", this._valueChanged);

    this._select = select;
    this._renderSignature = renderSignature;
    this.shadowRoot.replaceChildren(style, select);
    void this._replaceNativeCurrentlyLabel();
  }

  async _replaceNativeCurrentlyLabel() {
    let parent = this;
    let thermostatCard;
    while (parent) {
      const root = parent.getRootNode();
      parent = root?.host;
      if (parent?.localName === "hui-thermostat-card") {
        thermostatCard = parent;
        break;
      }
    }

    const control = thermostatCard?.shadowRoot?.querySelector(
      NATIVE_TEMPERATURE_CONTROL
    );
    if (!control?.shadowRoot) {
      return;
    }

    if (control.updateComplete) {
      await control.updateComplete;
    }

    const labels = control.shadowRoot.querySelectorAll(".info > p.label");
    const currentLabel = labels[labels.length - 1];
    const value = currentLabel?.querySelector("span");
    if (!currentLabel || !value) {
      return;
    }

    const icon = document.createElement("ha-icon");
    icon.setAttribute("icon", "mdi:thermometer");
    icon.setAttribute(
      "aria-label",
      this._hass.formatEntityAttributeName?.(
        this._stateObj,
        "current_temperature"
      ) || "Current temperature"
    );
    icon.style.setProperty("--mdc-icon-size", "18px");
    currentLabel.style.display = "flex";
    currentLabel.style.alignItems = "center";
    currentLabel.style.justifyContent = "center";
    currentLabel.style.gap = "4px";
    currentLabel.replaceChildren(icon, value);
  }
}

class OpenThermHotWaterControlPresetsCardFeature extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._valueChanged = this._valueChanged.bind(this);
  }

  static getStubConfig() {
    return { type: `custom:${PRESETS_FEATURE_TYPE}` };
  }

  setConfig(config) {
    if (!config) {
      throw new Error("Invalid configuration");
    }
    this._config = config;
    this._render();
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  get hass() {
    return this._hass;
  }

  set context(context) {
    this._context = context;
    this._render();
  }

  get context() {
    return this._context;
  }

  connectedCallback() {
    this._render();
  }

  get _stateObj() {
    const entityId = this._context?.entity_id;
    return entityId && this._hass ? this._hass.states[entityId] : undefined;
  }

  _availableModes(stateObj) {
    const presetData = this._presetData(stateObj);
    const presetNames = this._presetNames(stateObj);
    const entityModes = entityOperationModes(stateObj, presetNames);
    const configuredModes = this._config.preset_modes
      ? [...new Set([...this._config.preset_modes, ...presetNames])]
      : presetNames;

    return configuredModes.filter((mode) => {
      const inEntity = entityModes.includes(mode);
      if (!inEntity) {
        return false;
      }

      if (!presetData.length) {
        return BOOST_MODES.includes(mode);
      }

      return presetData.some((preset) => preset.name === mode);
    });
  }

  _presetData(stateObj = this._stateObj) {
    const presets = stateObj?.attributes?.[PRESETS_ATTRIBUTE];
    if (!Array.isArray(presets)) {
      return [];
    }

    return presets
      .map((preset) => {
        if (!preset || typeof preset !== "object") {
          return null;
        }

        const name = typeof preset.name === "string" ? preset.name.trim() : "";
        if (!name) {
          return null;
        }

        return {
          name,
          icon:
            typeof preset.icon === "string" && preset.icon.trim()
              ? preset.icon.trim()
              : MODE_ICONS[name],
          durationMinutes: Number(preset.duration_minutes) || 0,
        };
      })
      .filter(Boolean);
  }

  _presetNames(stateObj = this._stateObj) {
    const presets = this._presetData(stateObj);
    if (presets.length > 0) {
      return presets.map((preset) => preset.name);
    }

    return stateObj?.attributes?.preset_modes ?? [];
  }

  _presetIcon(mode, stateObj = this._stateObj) {
    return (
      this._presetData(stateObj).find((preset) => preset.name === mode)?.icon ||
      MODE_ICONS[mode]
    );
  }

  async _valueChanged(event) {
    event.stopPropagation();
    const stateObj = this._stateObj;
    const value = event.detail?.item?.value ?? event.detail?.value;
    if (!stateObj || !value) {
      return;
    }

    try {
      await this._hass.callService("water_heater", "set_operation_mode", {
        entity_id: stateObj.entity_id,
        operation_mode: value,
      });
    } catch (error) {
      showTemperatureError(this, error);
      this._renderSignature = undefined;
      this._render();
    }
  }

  _render() {
    if (!this.shadowRoot) {
      return;
    }

    const stateObj = this._stateObj;
    if (
      !this._config ||
      !this._hass ||
      !stateObj ||
      !supportsWaterHeater(this._hass, this._context)
    ) {
      this.shadowRoot.replaceChildren();
      return;
    }

    const availableModes = this._availableModes(stateObj);
    this.style.display = availableModes.length ? "" : "none";
    const renderSignature = JSON.stringify([
      stateObj.state === "unavailable",
      availableModes,
      this._presetData(stateObj),
    ]);
    if (this._select && this._renderSignature === renderSignature) {
      this._select.value = availableModes.includes(stateObj.state)
        ? stateObj.state
        : undefined;
      this._select.disabled = stateObj.state === "unavailable";
      return;
    }

    const style = document.createElement("style");
    style.textContent = `
      :host {
        display: block;
        height: auto;
      }
      .controls {
        display: flex;
        flex-direction: column;
        gap: var(--feature-button-spacing, 12px);
      }
      ha-control-select-menu {
        box-sizing: border-box;
        --control-select-menu-height: var(--feature-height, 42px);
        --control-select-menu-border-radius: var(--feature-border-radius, 12px);
        --control-select-menu-focus-color: var(--feature-color);
        display: block;
        line-height: var(--ha-line-height-condensed);
        width: 100%;
      }
    `;

    const controls = document.createElement("div");
    controls.className = "controls";
    const select = document.createElement("ha-control-select-menu");
    select.options = availableModes.map((mode) => ({
        value: mode,
        label: mode,
        icon: this._presetIcon(mode, stateObj),
    }));
    select.value = availableModes.includes(stateObj.state)
      ? stateObj.state
      : undefined;
    select.label = localize(this._hass, "ui.card.climate.preset", "Preset");
    select.showArrow = true;
    select.hideLabel = true;
    const icon = document.createElement("ha-icon");
    icon.setAttribute("slot", "icon");
    icon.setAttribute("icon", "mdi:tune-variant");
    select.append(icon);
    select.disabled = stateObj.state === "unavailable";
    select.addEventListener("wa-select", this._valueChanged);
    controls.append(select);

    this._select = select;
    this.style.gridRow = "";
    this._renderSignature = renderSignature;
    this.shadowRoot.replaceChildren(style, controls);
  }
}

class OpenThermHotWaterControlMoreInfo extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
  }
  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  get hass() {
    return this._hass;
  }

  set stateObj(stateObj) {
    this._stateObj = stateObj;
    this._render();
  }

  get stateObj() {
    return this._stateObj;
  }

  _presetNames() {
    const presets = this._stateObj?.attributes?.[PRESETS_ATTRIBUTE];
    if (Array.isArray(presets) && presets.length > 0) {
      return presets
        .map((preset) =>
          typeof preset?.name === "string" ? preset.name.trim() : ""
        )
        .filter(Boolean);
    }

    return this._stateObj?.attributes?.preset_modes ?? [];
  }

  _listPresetNames() {
    return this._presetNames();
  }

  connectedCallback() {
    this._render();
  }

  async _ensureNativeTemperatureControl() {
    if (customElements.get(NATIVE_TEMPERATURE_CONTROL)) {
      return;
    }

    if (!this._nativeControlPromise) {
      this._nativeControlPromise = (async () => {
        if (window.loadCardHelpers && this._stateObj) {
          const helpers = await window.loadCardHelpers();
          const loader = helpers.createCardElement({
            type: "thermostat",
            entity: this._stateObj.entity_id,
          });
          loader.hass = this._hass;
        }
        await customElements.whenDefined(NATIVE_TEMPERATURE_CONTROL);
      })();
    }

    await this._nativeControlPromise;
    this._render();
  }

  _formatCurrentTemperature(stateObj) {
    if (this._hass.formatEntityAttributeValue) {
      return this._hass.formatEntityAttributeValue(
        stateObj,
        "current_temperature"
      );
    }
    return `${stateObj.attributes.current_temperature} ${
      stateObj.attributes.temperature_unit || "°C"
    }`;
  }

  _formatCurrentTemperatureLabel(stateObj) {
    if (this._hass.formatEntityAttributeName) {
      return this._hass.formatEntityAttributeName(
        stateObj,
        "current_temperature"
      );
    }
    return "Current temperature";
  }

  _render() {
    if (!this.shadowRoot || !this._hass || !this._stateObj) {
      return;
    }

    if (!customElements.get(NATIVE_TEMPERATURE_CONTROL)) {
      const loading = document.createElement("ha-circular-progress");
      loading.setAttribute("active", "");
      this.shadowRoot.replaceChildren(loading);
      void this._ensureNativeTemperatureControl();
      return;
    }

    const currentTemperature = this._stateObj.attributes.current_temperature;
    if (this._temperatureControl) {
      this._temperatureControl.stateObj = this._stateObj;
      this._current.hidden = currentTemperature == null;
      if (currentTemperature != null) {
        this._currentLabel.textContent =
          this._formatCurrentTemperatureLabel(this._stateObj);
        this._currentValue.textContent = this._formatCurrentTemperature(
          this._stateObj
        );
      }
      this._modes.hass = this._hass;
      this._modes.context = { entity_id: this._stateObj.entity_id };
      if (this._presets) {
        this._presets.hass = this._hass;
        this._presets.context = { entity_id: this._stateObj.entity_id };
      }
      return;
    }

    const style = document.createElement("style");
    style.textContent = `
      :host {
        display: block;
        color: var(--primary-text-color);
      }
      .current {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin-bottom: var(--ha-space-4, 16px);
        text-align: center;
      }
      .current .label {
        color: var(--secondary-text-color);
        font-size: var(--ha-font-size-m, 14px);
        line-height: var(--ha-line-height-condensed, 1.2);
      }
      .current .value {
        margin-top: var(--ha-space-1, 4px);
        font-size: var(--ha-font-size-xl, 24px);
        font-weight: var(--ha-font-weight-medium, 500);
        line-height: var(--ha-line-height-condensed, 1.2);
      }
      .temperature {
        display: flex;
        justify-content: center;
        overflow: hidden;
        width: 100%;
      }
      ha-state-control-water_heater-temperature {
        box-sizing: border-box;
        width: min(100%, 320px);
        padding: 8px;
      }
      .features {
        align-items: center;
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        gap: var(--feature-button-spacing, 12px);
        justify-content: center;
        margin-top: var(--ha-space-4, 16px);
        margin-inline: auto;
        max-width: 520px;
        padding-inline: var(--ha-space-4, 16px);
        width: 100%;
      }
      .modes {
        width: 100%;
      }
      .presets {
        width: 100%;
      }
      ha-circular-progress {
        display: block;
        margin: 40px auto;
      }
    `;

    const content = document.createElement("div");

    const current = document.createElement("div");
    current.className = "current";
    current.hidden = currentTemperature == null;

    const label = document.createElement("div");
    label.className = "label";
    const value = document.createElement("div");
    value.className = "value";
    if (currentTemperature != null) {
      label.textContent = this._formatCurrentTemperatureLabel(this._stateObj);
      value.textContent = this._formatCurrentTemperature(this._stateObj);
    }
    current.append(label, value);
    content.append(current);

    const temperature = document.createElement("div");
    temperature.className = "temperature";
    const temperatureControl = document.createElement(
      NATIVE_TEMPERATURE_CONTROL
    );
    temperatureControl.stateObj = this._stateObj;
    temperatureControl.preventInteractionOnScroll = true;
    temperature.append(temperatureControl);
    content.append(temperature);

    const features = document.createElement("div");
    features.className = "features";

    const modesContainer = document.createElement("div");
    modesContainer.className = "modes";
    const modes = document.createElement(FEATURE_TYPE);
    modes.setConfig({
      type: `custom:${FEATURE_TYPE}`,
      max_width: 320,
    });
    modes.hass = this._hass;
    modes.context = { entity_id: this._stateObj.entity_id };
    modesContainer.append(modes);

    const presetsContainer = document.createElement("div");
    presetsContainer.className = "presets";
    const presets = document.createElement(PRESETS_FEATURE_TYPE);
    const presetModes = this._listPresetNames();
    presets.setConfig({
      type: `custom:${PRESETS_FEATURE_TYPE}`,
    });
    if (presetModes.length > 0) {
      presets.hass = this._hass;
      presets.context = { entity_id: this._stateObj.entity_id };
      presetsContainer.append(presets);
      features.append(modesContainer, presetsContainer);
      this._presets = presets;
    } else {
      features.append(modesContainer);
      this._presets = undefined;
    }

    content.append(features);

    this._temperatureControl = temperatureControl;
    this._current = current;
    this._currentLabel = label;
    this._currentValue = value;
    this._modes = modes;
    if (presetModes.length === 0) {
      this._presets = undefined;
    }
    this.shadowRoot.replaceChildren(style, content);
  }
}

if (!customElements.get(FEATURE_TYPE)) {
  customElements.define(FEATURE_TYPE, OpenThermHotWaterControlModesCardFeature);
}

if (!customElements.get(PRESETS_FEATURE_TYPE)) {
  customElements.define(
    PRESETS_FEATURE_TYPE,
    OpenThermHotWaterControlPresetsCardFeature
  );
}

if (!customElements.get(MORE_INFO_TYPE)) {
  customElements.define(MORE_INFO_TYPE, OpenThermHotWaterControlMoreInfo);
}

window.customCardFeatures = window.customCardFeatures || [];
if (!window.customCardFeatures.some((feature) => feature.type === FEATURE_TYPE)) {
  window.customCardFeatures.push({
    type: FEATURE_TYPE,
    name: "Hot-water control modes",
    isSupported: supportsWaterHeater,
  });
}

if (
  !window.customCardFeatures.some(
    (feature) => feature.type === PRESETS_FEATURE_TYPE
  )
) {
  window.customCardFeatures.push({
    type: PRESETS_FEATURE_TYPE,
    name: "Hot-water control presets",
    isSupported: supportsWaterHeater,
  });
}

const OPENTHERM_FEATURE_TYPES = new Set([
  `custom:${FEATURE_TYPE}`,
  `custom:${PRESETS_FEATURE_TYPE}`,
]);

// Home Assistant normally rebuilds a custom feature after its element is
// defined. If that notification loses the cold-load race, the feature host can
// retain its temporary error element. Ask the owning view to recreate its
// cards once now that all OpenTherm feature elements are registered.
const rebuiltOpenThermFeatureTargets = new WeakSet();

const rebuildFailedOpenThermFeature = (rebuildTarget) => {
  if (
    !OPENTHERM_FEATURE_TYPES.has(rebuildTarget?.feature?.type) ||
    !rebuildTarget.shadowRoot?.querySelector("hui-error-card")
  ) {
    return;
  }

  let owner = rebuildTarget;
  while (owner && owner.localName !== "hui-view") {
    owner = owner.parentNode || owner.getRootNode?.().host;
  }
  if (!owner || rebuiltOpenThermFeatureTargets.has(owner)) {
    return;
  }

  rebuiltOpenThermFeatureTargets.add(owner);
  rebuildTarget.dispatchEvent(
    new CustomEvent("ll-rebuild", { bubbles: true, composed: true })
  );
};

const INLINE_FEATURE_BACKPORT_ATTRIBUTE =
  "data-opentherm-inline-feature-backport";
const INLINE_LAYOUT_BACKPORT_ATTRIBUTE =
  "data-opentherm-inline-layout-backport";

const removeOpenThermInlineLayout = (tile) => {
  tile?.shadowRoot
    ?.querySelector(`style[${INLINE_LAYOUT_BACKPORT_ATTRIBUTE}]`)
    ?.remove();
  // Clean up the layout style used by versions 2.5.8 and 2.5.9.
  tile?.shadowRoot
    ?.querySelector("ha-tile-container")
    ?.shadowRoot
    ?.querySelector(`style[${INLINE_LAYOUT_BACKPORT_ATTRIBUTE}]`)
    ?.remove();
};

const installOpenThermInlineLayout = (tile) => {
  const root = tile?.shadowRoot;
  if (
    !root ||
    root.querySelector(`style[${INLINE_LAYOUT_BACKPORT_ATTRIBUTE}]`)
  ) {
    return;
  }

  const style = document.createElement("style");
  style.setAttribute(INLINE_LAYOUT_BACKPORT_ATTRIBUTE, "");
  style.textContent = `
    ha-card {
      display: flex !important;
      flex-direction: column !important;
    }
    ha-card > ha-tile-container {
      flex: 1 0 auto;
      height: auto !important;
    }
    ha-card > hui-card-features[${INLINE_FEATURE_BACKPORT_ATTRIBUTE}] {
      --feature-color: var(--tile-color);
      box-sizing: border-box;
      flex: none;
      padding: 0 var(--ha-space-3, 12px) var(--ha-space-3, 12px);
      width: 100%;
    }
  `;
  root.append(style);
};

const needsOpenThermInlineFeatureBackport = (tile) => {
  const config = tile?._config;
  if (
    !config ||
    config.vertical ||
    config.features_position !== "inline" ||
    !Array.isArray(config.features) ||
    config.features.length < 2
  ) {
    return false;
  }

  return config.features
    .slice(1)
    .some((feature) => OPENTHERM_FEATURE_TYPES.has(feature.type));
};

const restoreOpenThermInlineFeatures = (tile) => {
  if (!tile?.shadowRoot) {
    return;
  }

  const injectedSelector = `hui-card-features[${INLINE_FEATURE_BACKPORT_ATTRIBUTE}]`;
  const injected = tile.shadowRoot.querySelector(injectedSelector);
  if (!needsOpenThermInlineFeatureBackport(tile)) {
    injected?.remove();
    removeOpenThermInlineLayout(tile);
    return;
  }

  const container = tile.shadowRoot.querySelector("ha-tile-container");
  const card = tile.shadowRoot.querySelector("ha-card");
  if (!container || !card) {
    return;
  }

  // Newer Home Assistant versions render the remaining inline features
  // themselves. Never duplicate or replace that native feature container.
  const nativeBottomFeatures = container.querySelector(
    `hui-card-features[slot="features"]:not([${INLINE_FEATURE_BACKPORT_ATTRIBUTE}])`
  );
  const remainingFeatures = tile._config.features.slice(1);
  const nativeFeatures = nativeBottomFeatures?.features;
  const nativeHasRemainingFeatures =
    Array.isArray(nativeFeatures) &&
    nativeFeatures.length === remainingFeatures.length &&
    nativeFeatures.every(
      (feature, index) => feature.type === remainingFeatures[index].type
    );
  if (nativeHasRemainingFeatures) {
    injected?.remove();
    removeOpenThermInlineLayout(tile);
    return;
  }

  installOpenThermInlineLayout(tile);

  const bottomFeatures =
    injected || document.createElement("hui-card-features");
  bottomFeatures.setAttribute(INLINE_FEATURE_BACKPORT_ATTRIBUTE, "");
  bottomFeatures.removeAttribute("slot");
  // Keep the mode buttons and preset selector as separate full-width rows.
  bottomFeatures.columns = 1;
  bottomFeatures.hass = tile.hass;
  bottomFeatures.context =
    tile._featureContext || { entity_id: tile._config.entity };
  bottomFeatures.color = tile._config.color;
  bottomFeatures.features = remainingFeatures;

  if (bottomFeatures.parentElement !== card) {
    card.append(bottomFeatures);
  }
};

const installOpenThermInlineFeatureBackport = async () => {
  await customElements.whenDefined("hui-tile-card");
  const TileCard = customElements.get("hui-tile-card");
  const prototype = TileCard?.prototype;
  if (!prototype || prototype._openThermInlineFeatureBackport) {
    return;
  }

  prototype._openThermInlineFeatureBackport = true;

  const originalUpdated = prototype.updated;
  prototype.updated = function (...args) {
    const result = originalUpdated?.apply(this, args);
    queueMicrotask(() => restoreOpenThermInlineFeatures(this));
    return result;
  };

  // Older Tile cards report no bottom feature rows while Inline is selected.
  // Account for the restored rows so masonry and Sections layouts allocate the
  // same height as the visible controls. Native mixed-layout versions expose
  // _featureLayout and already include these rows in their own calculations.
  const originalGetCardSize = prototype.getCardSize;
  if (originalGetCardSize) {
    prototype.getCardSize = function (...args) {
      let size = originalGetCardSize.apply(this, args);
      if (
        typeof this._featureLayout !== "function" &&
        needsOpenThermInlineFeatureBackport(this)
      ) {
        size += this._config.features.slice(1).length;
      }
      return size;
    };
  }

  const originalGetGridOptions = prototype.getGridOptions;
  if (originalGetGridOptions) {
    prototype.getGridOptions = function (...args) {
      const nativeOptions = originalGetGridOptions.apply(this, args);
      if (
        typeof this._featureLayout === "function" ||
        !needsOpenThermInlineFeatureBackport(this)
      ) {
        return nativeOptions;
      }

      const addedRows = this._config.features.slice(1).length;
      return {
        ...nativeOptions,
        rows:
          typeof nativeOptions.rows === "number"
            ? nativeOptions.rows + addedRows
            : nativeOptions.rows,
        min_rows:
          typeof nativeOptions.min_rows === "number"
            ? nativeOptions.min_rows + addedRows
            : nativeOptions.min_rows,
      };
    };
  }

  refreshOpenThermFeatureLayout();
};

const observedOpenThermFeatureRoots = new WeakSet();
let openThermFeatureObserver;
let openThermFeatureObservationEnded = false;
let openThermFeatureObservationStopScheduled = false;

const observeOpenThermFeatureRoot = (root) => {
  if (
    !root ||
    openThermFeatureObservationEnded ||
    observedOpenThermFeatureRoots.has(root) ||
    (!(root instanceof Document) && !(root instanceof ShadowRoot))
  ) {
    return;
  }

  if (!openThermFeatureObserver) {
    openThermFeatureObserver = new MutationObserver((mutations) => {
      for (const mutation of mutations) {
        for (const node of mutation.addedNodes) {
          if (node.nodeType === Node.ELEMENT_NODE) {
            refreshOpenThermFeatureLayout(node);
          }
        }
      }
    });
  }
  observedOpenThermFeatureRoots.add(root);
  openThermFeatureObserver.observe(root, { childList: true, subtree: true });
  if (!openThermFeatureObservationStopScheduled) {
    openThermFeatureObservationStopScheduled = true;
    window.setTimeout(() => {
      openThermFeatureObservationEnded = true;
      openThermFeatureObserver?.disconnect();
    }, 60000);
  }
};

const refreshOpenThermFeatureLayout = (root = document) => {
  observeOpenThermFeatureRoot(root);
  const elements = [
    ...(root.nodeType === Node.ELEMENT_NODE ? [root] : []),
    ...(root.querySelectorAll?.("*") || []),
  ];
  for (const element of elements) {
    if (element.localName === "hui-tile-card") {
      restoreOpenThermInlineFeatures(element);
    }

    if (element.localName === "hui-card-feature") {
      rebuildFailedOpenThermFeature(element);
    }

    if (element.shadowRoot) {
      observeOpenThermFeatureRoot(element.shadowRoot);
      refreshOpenThermFeatureLayout(element.shadowRoot);
    }
  }
};


void installOpenThermInlineFeatureBackport();
