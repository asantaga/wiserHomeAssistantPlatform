/*! WISER-CARD-VERSION wiser-climate-more-info 1.5.2 */

// The structure and behaviour in this control deliberately follow Home
// Assistant's native MoreInfoClimate and HaStateControlClimateTemperature:
// https://github.com/home-assistant/frontend/blob/dev/src/dialogs/more-info/controls/more-info-climate.ts
// https://github.com/home-assistant/frontend/blob/dev/src/state-control/climate/ha-state-control-climate-temperature.ts
// Reviewed 2026-10-27. Home Assistant frontend is licensed under Apache-2.0.
// We reuse HA's registered temperature control instead of replacing its
// temperature/service behaviour. The Wiser presentation is applied to that
// same native control in both More Info and native Thermostat cards.

const MORE_INFO_TYPE = "wiser-climate-more-info";
const NATIVE_TEMPERATURE_CONTROL = "ha-state-control-climate-temperature";
const NATIVE_THERMOSTAT_CARD = "hui-thermostat-card";
const NATIVE_THERMOSTAT_EDITOR = "hui-thermostat-card-editor";
const THERMOSTAT_FEATURE_ROW_ATTRIBUTE = "data-wiser-feature-row";
const THERMOSTAT_FEATURE_STYLE_ATTRIBUTE = "data-wiser-feature-layout";
const TARGET_TEMPERATURE = 1;
const TARGET_TEMPERATURE_RANGE = 2;
const PRESET_MODE = 16;

const MODE_ICONS = {
  auto: "mdi:calendar-clock",
  heat: "mdi:fire",
  off: "mdi:power",
};

const localize = (hass, key, fallback) => hass?.localize?.(key) || fallback;

const titleCase = (value) =>
  String(value || "")
    .replaceAll("_", " ")
    .replace(/\b\w/g, (character) => character.toUpperCase());

const cssString = (value) =>
  String(value).replaceAll("\\", "\\\\").replaceAll('"', '\\"');

const styleGenerations = new WeakMap();
const thermostatFeatureObservers = new WeakMap();

const demandForState = (stateObj) => {
  const demand = Number(stateObj?.attributes?.percentage_demand);
  return Number.isFinite(demand) ? demand : 0;
};

const extraInfoForState = (stateObj) => {
  const attributes = stateObj?.attributes;
  if (attributes?.is_passive) {
    const controlType = attributes.passive_control_type || "Modulation";
    return `${controlType} · ${demandForState(stateObj)}%`;
  }
  if (attributes?.demand_type != null) {
    return `Demand · ${demandForState(stateObj)}%`;
  }
  return undefined;
};

const wiserControlsEnabled = (stateObj) =>
  stateObj?.attributes?.custom_ui_more_info === MORE_INFO_TYPE;

const clearNativeControlStyle = (control) => {
  styleGenerations.set(control, (styleGenerations.get(control) || 0) + 1);
  for (const property of [
    "--wiser-slider-color",
    "--wiser-slider-opacity",
    "--wiser-label-color",
    "--wiser-extra-info-text",
    "--state-climate-auto-color",
    "--state-climate-heat-color",
    "--state-climate-off-color",
  ]) {
    control.style.removeProperty(property);
  }
  control.shadowRoot?.querySelector("style[data-wiser-theme]")?.remove();
  control.shadowRoot
    ?.querySelector("ha-control-circular-slider")
    ?.shadowRoot?.querySelector("style[data-wiser-theme]")
    ?.remove();
};

const styleNativeControl = async (control, stateObj) => {
  if (!control || !wiserControlsEnabled(stateObj)) {
    if (control) clearNativeControlStyle(control);
    return;
  }

  const generation = (styleGenerations.get(control) || 0) + 1;
  styleGenerations.set(control, generation);
  await control.updateComplete;
  if (generation !== styleGenerations.get(control) || !control.shadowRoot) return;

  const demand = demandForState(stateObj);
  const passive = Boolean(stateObj.attributes.is_passive);
  const state = stateObj.state;
  const passiveMode = passive && (state === "auto" || state === "heat");
  const sliderColor = passiveMode
    ? state === "auto"
      ? "var(--passive-auto-color, var(--light-green-color))"
      : "var(--passive-heat-color, var(--amber-color))"
    : "var(--slider-color, var(--disabled-color))";
  const modeColor = passiveMode
    ? sliderColor
    : state === "auto"
      ? "var(--climate-auto-color, var(--green-color))"
      : "var(--climate-heat-color, var(--deep-orange-color))";
  const sliderOpacity = passiveMode
    ? "var(--slider-passive-range-opacity, 1)"
    : "var(--slider-opacity, var(--slider-theme-opacity, .3))";
  const labelColor = demand > 0
    ? "var(--label-text-highlight-color, var(--deep-orange-color, inherit))"
    : "var(--thermostat-primary-text-color, var(--primary-text-color))";

  control.style.setProperty("--wiser-slider-color", sliderColor);
  control.style.setProperty("--wiser-slider-opacity", sliderOpacity);
  control.style.setProperty("--wiser-label-color", labelColor);
  control.style.setProperty(`--state-climate-${state}-color`, modeColor);
  const extraInfo = extraInfoForState(stateObj);
  control.style.setProperty(
    "--wiser-extra-info-text",
    extraInfo ? `"${cssString(extraInfo)}"` : "none"
  );

  let style = control.shadowRoot.querySelector("style[data-wiser-theme]");
  if (!style) {
    style = document.createElement("style");
    style.dataset.wiserTheme = "";
    control.shadowRoot.append(style);
  }
  style.textContent = `
    .buttons { visibility: var(--button-visibility, visible) !important; }
    .label, .info, .info > p {
      color: var(--thermostat-primary-text-color, var(--primary-text-color)) !important;
    }
    .info::after {
      color: var(--extra-info-text-color, var(--action-color));
      content: var(--wiser-extra-info-text);
      font-weight: var(--ha-font-weight-medium, 500);
      line-height: var(--ha-line-height-normal, 1.5);
      margin-top: var(--extra-info-margin-top, -6px);
      max-width: 90%;
      overflow: visible;
      text-align: center;
      white-space: nowrap;
    }
    .container.xs .info::after { display: none; }
    .container .label { color: var(--wiser-label-color) !important; }
    ${
      demand > 0
        ? ".container { --action-color: var(--radial-glow-color, var(--deep-orange-color)) !important; }"
        : ""
    }
    ha-control-circular-slider {
      --control-circular-slider-high-color: var(--custom-theme-control-circular-slider-high-color, var(--disabled-color)) !important;
      --control-circular-slider-low-color: var(--wiser-slider-color) !important;
      --control-circular-slider-background: var(--wiser-slider-color) !important;
      --control-circular-slider-background-opacity: var(--wiser-slider-opacity) !important;
    }
  `;

  const slider = control.shadowRoot.querySelector("ha-control-circular-slider");
  if (!slider) return;
  await slider.updateComplete;
  if (generation !== styleGenerations.get(control) || !slider.shadowRoot) return;

  let sliderStyle = slider.shadowRoot.querySelector("style[data-wiser-theme]");
  if (!sliderStyle) {
    sliderStyle = document.createElement("style");
    sliderStyle.dataset.wiserTheme = "";
    slider.shadowRoot.append(sliderStyle);
  }
  sliderStyle.textContent = `
    .arc.arc-clear {
      stroke-width: var(--custom-theme-slider-high-stroke-width, 25px);
    }
    path.arc.arc-colored.high {
      opacity: var(--custom-theme-control-circular-slider-high-color-opacity, var(--slider-theme-opacity, .3)) !important;
      stroke-width: 25px;
    }
    .current {
      stroke: color-mix(in srgb, var(--wiser-slider-color), #000 50%) !important;
    }
    .arc-current {
      opacity: .5 !important;
      stroke: var(--primary-text-color) !important;
    }
    .arc.arc-active.high { opacity: 0 !important; }
    .target-border.high, .target-border.low {
      opacity: 1 !important;
      stroke: var(--wiser-slider-color) !important;
    }
  `;
};

class WiserClimateMoreInfo extends HTMLElement {
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

  connectedCallback() {
    this._render();
  }

  async _ensureNativeTemperatureControl() {
    if (customElements.get(NATIVE_TEMPERATURE_CONTROL)) {
      return;
    }

    if (!this._nativeControlPromise) {
      this._nativeControlPromise = (async () => {
        // This is the public custom-card helper route used by HA custom cards.
        // Constructing a thermostat card asks HA to load its native climate
        // state control without relying on private chunk URLs.
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

  _formatAttribute(attribute) {
    if (this._hass?.formatEntityAttributeValue) {
      return this._hass.formatEntityAttributeValue(this._stateObj, attribute);
    }
    const value = this._stateObj?.attributes?.[attribute];
    return value == null ? "" : String(value);
  }

  _formatAttributeName(attribute, fallback) {
    return (
      this._hass?.formatEntityAttributeName?.(this._stateObj, attribute) ||
      fallback
    );
  }

  _formatState(value) {
    if (this._hass?.formatEntityState) {
      return this._hass.formatEntityState(this._stateObj, value);
    }
    return titleCase(value);
  }

  _formatPreset(value) {
    if (this._hass?.formatEntityAttributeValue) {
      return this._hass.formatEntityAttributeValue(
        this._stateObj,
        "preset_mode",
        value
      );
    }
    return titleCase(value);
  }

  _createModeIcon(mode) {
    const icon = document.createElement("ha-icon");
    icon.setAttribute("icon", MODE_ICONS[mode] || "mdi:radiator");
    return icon;
  }

  _presetIcon() {
    const icon = document.createElement("ha-icon");
    icon.setAttribute("icon", "mdi:tune-variant");
    return icon;
  }

  _showLoadError(message) {
    const error = document.createElement("p");
    error.className = "load-error";
    error.style.color = "var(--error-color)";
    error.style.textAlign = "center";
    error.textContent = message;
    this.shadowRoot.replaceChildren(error);
  }

  async _setHvacMode(event) {
    event.stopPropagation();
    const value = event.detail?.item?.value ?? event.detail?.value;
    if (!value || value === this._stateObj?.state) return;
    await this._callService("set_hvac_mode", { hvac_mode: value });
  }

  async _setPresetMode(event) {
    event.stopPropagation();
    const value = event.detail?.item?.value ?? event.detail?.value;
    if (!value || value === this._stateObj?.attributes?.preset_mode) return;
    await this._callService("set_preset_mode", { preset_mode: value });
  }

  async _callService(service, data) {
    try {
      await this._hass.callService("climate", service, {
        entity_id: this._stateObj.entity_id,
        ...data,
      });
    } catch (error) {
      this.dispatchEvent(
        new CustomEvent("hass-notification", {
          bubbles: true,
          composed: true,
          detail: {
            message: error?.message || "Unable to update the Wiser room.",
            duration: 10000,
          },
        })
      );
    }
  }

  _build() {
    const style = document.createElement("style");
    style.textContent = `
      :host {
        color: var(--primary-text-color);
        display: flex;
        flex: 1;
        flex-direction: column;
        justify-content: space-between;
      }
      .current {
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: center;
        margin-bottom: var(--ha-space-10, 40px);
        text-align: center;
      }
      .current > div {
        display: flex;
        flex: 1;
        flex-direction: column;
        align-items: center;
      }
      .current p { margin: 0; color: var(--primary-text-color); }
      .current .label {
        font-size: var(--ha-font-size-m, 14px);
        line-height: var(--ha-line-height-condensed, 1.2);
        letter-spacing: .4px;
        margin-bottom: var(--ha-space-1, 4px);
        opacity: .8;
      }
      .current .value {
        direction: ltr;
        font-size: var(--ha-font-size-xl, 24px);
        font-weight: var(--ha-font-weight-medium, 500);
        line-height: var(--ha-line-height-condensed, 1.2);
      }
      .controls {
        display: flex;
        flex: 1;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin-bottom: var(--ha-space-6, 24px);
      }
      .selects {
        display: flex;
        flex-flow: row wrap;
        gap: var(--ha-space-3, 12px);
        justify-content: center;
        margin-inline: auto;
        max-width: 450px;
        width: 100%;
      }
      .selects > * {
        flex: 0 1 160px;
        min-width: 120px;
      }
      ha-circular-progress { display: block; margin: 40px auto; }
      .load-error { color: var(--error-color); text-align: center; }
    `;

    const current = document.createElement("div");
    current.className = "current";
    const currentColumn = document.createElement("div");
    const currentLabel = document.createElement("p");
    currentLabel.className = "label";
    const currentValue = document.createElement("p");
    currentValue.className = "value";
    currentColumn.append(currentLabel, currentValue);
    const humidityColumn = document.createElement("div");
    const humidityLabel = document.createElement("p");
    humidityLabel.className = "label";
    const humidityValue = document.createElement("p");
    humidityValue.className = "value";
    humidityColumn.append(humidityLabel, humidityValue);
    current.append(currentColumn, humidityColumn);

    const controls = document.createElement("div");
    controls.className = "controls";
    const temperatureControl = document.createElement(
      NATIVE_TEMPERATURE_CONTROL
    );
    temperatureControl.preventInteractionOnScroll = true;
    controls.append(temperatureControl);

    const selects = document.createElement("div");
    selects.className = "selects";
    const modeSelect = document.createElement("ha-control-select-menu");
    const modeIcon = document.createElement("ha-icon");
    modeIcon.setAttribute("slot", "icon");
    modeSelect.append(modeIcon);
    modeSelect.addEventListener("wa-select", (event) =>
      void this._setHvacMode(event)
    );
    selects.append(modeSelect);

    const presetSelect = document.createElement("ha-control-select-menu");
    const presetIcon = document.createElement("ha-icon");
    presetIcon.setAttribute("slot", "icon");
    presetIcon.setAttribute("icon", "mdi:tune-variant");
    presetSelect.append(presetIcon);
    presetSelect.addEventListener("wa-select", (event) =>
      void this._setPresetMode(event)
    );
    selects.append(presetSelect);

    this.shadowRoot.replaceChildren(style, current, controls, selects);
    this._current = current;
    this._currentLabel = currentLabel;
    this._currentValue = currentValue;
    this._humidityColumn = humidityColumn;
    this._humidityLabel = humidityLabel;
    this._humidityValue = humidityValue;
    this._temperatureControl = temperatureControl;
    this._modeSelect = modeSelect;
    this._modeIconElement = modeIcon;
    this._presetSelect = presetSelect;
  }

  _sync() {
    const stateObj = this._stateObj;
    const currentTemperature = stateObj.attributes.current_temperature;
    this._current.hidden = currentTemperature == null;
    this._currentLabel.textContent = this._formatAttributeName(
      "current_temperature",
      "Current temperature"
    );
    this._currentValue.textContent = this._formatAttribute(
      "current_temperature"
    );
    const currentHumidity = stateObj.attributes.current_humidity;
    this._humidityColumn.hidden = currentHumidity == null;
    this._humidityLabel.textContent = this._formatAttributeName(
      "current_humidity",
      "Current humidity"
    );
    this._humidityValue.textContent = this._formatAttribute(
      "current_humidity"
    );

    this._temperatureControl.stateObj = stateObj;
    this._temperatureControl.preventInteractionOnScroll = true;

    const modes = Array.isArray(stateObj.attributes.hvac_modes)
      ? stateObj.attributes.hvac_modes
      : [];
    this._modeSelect.label = localize(
      this._hass,
      "ui.card.climate.mode",
      "Mode"
    );
    this._modeSelect.value = stateObj.state;
    this._modeSelect.disabled = stateObj.state === "unavailable";
    this._modeSelect.options = modes.map((mode) => ({
      value: mode,
      label: this._formatState(mode),
    }));
    this._modeSelect.renderIcon = (value) => this._createModeIcon(value);
    this._modeIconElement.setAttribute(
      "icon",
      MODE_ICONS[stateObj.state] || "mdi:radiator"
    );

    const presets = Array.isArray(stateObj.attributes.preset_modes)
      ? stateObj.attributes.preset_modes
      : [];
    const supportedFeatures = Number(stateObj.attributes.supported_features || 0);
    const supportsPresets =
      (supportedFeatures & PRESET_MODE) !== 0 && presets.length > 0;
    this._presetSelect.hidden = !supportsPresets;
    this._presetSelect.label = this._formatAttributeName(
      "preset_mode",
      localize(this._hass, "ui.card.climate.preset", "Preset")
    );
    this._presetSelect.value = stateObj.attributes.preset_mode;
    this._presetSelect.disabled = stateObj.state === "unavailable";
    this._presetSelect.options = presets.map((preset) => ({
      value: preset,
      label: this._formatPreset(preset),
    }));
    this._presetSelect.renderIcon = () => this._presetIcon();

    void this._styleNativeControl();
  }

  async _styleNativeControl() {
    await styleNativeControl(this._temperatureControl, this._stateObj);
  }

  _render() {
    if (!this.shadowRoot || !this._hass || !this._stateObj) return;

    const supportedFeatures = Number(
      this._stateObj.attributes.supported_features || 0
    );
    if (
      (supportedFeatures &
        (TARGET_TEMPERATURE | TARGET_TEMPERATURE_RANGE)) ===
      0
    ) {
      this._showLoadError(
        "This Wiser room does not expose a target temperature."
      );
      return;
    }

    if (!customElements.get(NATIVE_TEMPERATURE_CONTROL)) {
      const loading = document.createElement("ha-circular-progress");
      loading.setAttribute("active", "");
      this.shadowRoot.replaceChildren(loading);
      void this._ensureNativeTemperatureControl().catch((error) => {
        this._showLoadError(
          String(
            error?.message || "Unable to load the native climate control."
          )
        );
      });
      return;
    }

    if (!this._temperatureControl) this._build();
    this._sync();
  }
}

if (!customElements.get(MORE_INFO_TYPE)) {
  customElements.define(MORE_INFO_TYPE, WiserClimateMoreInfo);
}

const patchNativeTemperatureControl = async () => {
  await customElements.whenDefined(NATIVE_TEMPERATURE_CONTROL);
  const controlClass = customElements.get(NATIVE_TEMPERATURE_CONTROL);
  if (!controlClass || controlClass.prototype.__wiserControlsPatched) return;

  const originalUpdated = controlClass.prototype.updated;
  controlClass.prototype.updated = function (...args) {
    const result = originalUpdated?.apply(this, args);
    if (wiserControlsEnabled(this.stateObj)) {
      void styleNativeControl(this, this.stateObj);
    } else {
      clearNativeControlStyle(this);
    }
    return result;
  };
  controlClass.prototype.__wiserControlsPatched = true;

  const visit = (root) => {
    for (const element of root.querySelectorAll?.("*") || []) {
      if (element.localName === NATIVE_TEMPERATURE_CONTROL) {
        if (wiserControlsEnabled(element.stateObj)) {
          void styleNativeControl(element, element.stateObj);
        }
      }
      if (element.shadowRoot) visit(element.shadowRoot);
    }
  };
  visit(document);
};

void patchNativeTemperatureControl();

const thermostatState = (element) =>
  element?._config?.entity
    ? element.hass?.states?.[element._config.entity]
    : undefined;

const clearThermostatInlineFeatures = (card) => {
  const root = card.shadowRoot;
  if (!root) return;
  const observer = thermostatFeatureObservers.get(card);
  observer?.disconnect();
  thermostatFeatureObservers.delete(card);
  root
    .querySelector(`[${THERMOSTAT_FEATURE_ROW_ATTRIBUTE}]`)
    ?.remove();
  root
    .querySelector(`style[${THERMOSTAT_FEATURE_STYLE_ATTRIBUTE}]`)
    ?.remove();
  const bottom = root.querySelector("ha-card > hui-card-features");
  if (bottom) {
    bottom.style.removeProperty("display");
    bottom.columns = undefined;
    bottom.features = card._config?.features || [];
  }
};

const THERMOSTAT_MODE_FEATURES = {
  "climate-hvac-modes": "hvac_modes",
  "climate-preset-modes": "preset_modes",
  "climate-fan-modes": "fan_modes",
  "climate-swing-modes": "swing_modes",
  "climate-swing-horizontal-modes": "swing_horizontal_modes",
};

const thermostatFeatureLayout = (feature, stateObj) => {
  const attribute = THERMOSTAT_MODE_FEATURES[feature?.type];
  if (!attribute) return { units: 1, minimum: 60 };
  if (feature.style === "dropdown") return { units: 2, minimum: 120 };
  const configuredModes = feature?.[attribute];
  const entityModes = stateObj?.attributes?.[attribute];
  const visibleModes = Array.isArray(configuredModes)
    ? Array.isArray(entityModes)
      ? configuredModes.filter((mode) => entityModes.includes(mode))
      : configuredModes
    : entityModes;
  const buttons = Array.isArray(visibleModes)
    ? Math.max(visibleModes.length, 1)
    : 1;
  return { units: buttons, minimum: Math.max(buttons * 50, 60) };
};

const isCardEditorPreview = (element) => {
  if (element?.preview === true || element?.editMode === true) return true;
  let current = element;
  while (current) {
    if (
      current.localName === "hui-card-preview" ||
      (current.localName === "hui-card" && current.hasAttribute("preview"))
    ) {
      return true;
    }
    const root = current.getRootNode?.();
    current = current.parentElement || root?.host;
  }
  return false;
};

const thermostatFeatureRows = (card, features, stateObj) => {
  const renderedWidth =
    card.shadowRoot?.querySelector("ha-card")?.clientWidth ||
    card.clientWidth ||
    600;
  const width = isCardEditorPreview(card)
    ? Math.min(renderedWidth, 360)
    : renderedWidth;
  const availableWidth = Math.max(width - 24, 1);
  const gap = 12;
  let rows = 1;
  let used = 0;
  for (const feature of features) {
    const { minimum } = thermostatFeatureLayout(feature, stateObj);
    const required = used ? minimum + gap : minimum;
    if (used && used + required > availableWidth) {
      rows += 1;
      used = minimum;
    } else {
      used += required;
    }
  }
  return rows;
};

const applyThermostatInlineFeatures = (card) => {
  const config = card._config;
  const features = Array.isArray(config?.features) ? config.features : [];
  const stateObj = thermostatState(card);
  const root = card.shadowRoot;
  const bottom = root?.querySelector("ha-card > hui-card-features");
  if (
    !root ||
    !bottom ||
    !wiserControlsEnabled(stateObj) ||
    config.features_position !== "inline" ||
    features.length === 0
  ) {
    clearThermostatInlineFeatures(card);
    return;
  }

  let style = root.querySelector(
    `style[${THERMOSTAT_FEATURE_STYLE_ATTRIBUTE}]`
  );
  if (!style) {
    style = document.createElement("style");
    style.setAttribute(THERMOSTAT_FEATURE_STYLE_ATTRIBUTE, "");
    style.textContent = `
      [${THERMOSTAT_FEATURE_ROW_ATTRIBUTE}] {
        display: flex;
        flex-wrap: wrap;
        gap: var(--ha-card-feature-gap, 12px);
        width: 100%;
        padding: 0 12px 12px;
        box-sizing: border-box;
      }
      [${THERMOSTAT_FEATURE_ROW_ATTRIBUTE}][data-editor-preview] {
        max-width: 360px;
        margin-inline: auto;
      }
      [${THERMOSTAT_FEATURE_ROW_ATTRIBUTE}] > hui-card-features {
        width: auto;
        min-width: 60px;
        padding: 0;
      }
    `;
    root.append(style);
  }

  let row = root.querySelector(`[${THERMOSTAT_FEATURE_ROW_ATTRIBUTE}]`);
  if (!row) {
    row = document.createElement("div");
    row.setAttribute(THERMOSTAT_FEATURE_ROW_ATTRIBUTE, "");
    bottom.after(row);
  }
  row.toggleAttribute("data-editor-preview", isCardEditorPreview(card));

  const hosts = [...row.querySelectorAll(":scope > hui-card-features")];
  features.forEach((feature, index) => {
    const host = hosts[index] || document.createElement("hui-card-features");
    if (!hosts[index]) row.append(host);
    const layout = thermostatFeatureLayout(feature, stateObj);
    host.dataset.units = String(layout.units);
    host.style.flex = `${layout.units} 1 ${layout.minimum}px`;
    host.hass = card.hass;
    host.context = bottom.context || card._featureContext;
    host.color = bottom.color;
    host.position = bottom.position;
    host.columns = 1;
    host.features = [feature];
    const featureColor = bottom.style.getPropertyValue("--feature-color");
    if (featureColor) host.style.setProperty("--feature-color", featureColor);
  });
  hosts.slice(features.length).forEach((host) => host.remove());
  bottom.style.display = "none";

  if (!thermostatFeatureObservers.has(card) && window.ResizeObserver) {
    const observer = new window.ResizeObserver(() => {
      if (card._config?.features_position === "inline") {
        applyThermostatInlineFeatures(card);
      }
    });
    observer.observe(card);
    thermostatFeatureObservers.set(card, observer);
  }
};

const patchNativeThermostatCard = async () => {
  await customElements.whenDefined(NATIVE_THERMOSTAT_CARD);
  const cardClass = customElements.get(NATIVE_THERMOSTAT_CARD);
  if (!cardClass || cardClass.prototype.__wiserInlineFeaturesPatched) return;

  const originalUpdated = cardClass.prototype.updated;
  cardClass.prototype.updated = function (...args) {
    const result = originalUpdated?.apply(this, args);
    Promise.resolve(this.updateComplete).then(() =>
      applyThermostatInlineFeatures(this)
    );
    return result;
  };

  const originalGridOptions = cardClass.prototype.getGridOptions;
  cardClass.prototype.getGridOptions = function (...args) {
    const options = originalGridOptions.apply(this, args);
    const features = this._config?.features || [];
    if (
      wiserControlsEnabled(thermostatState(this)) &&
      this._config?.features_position === "inline" &&
      features.length
    ) {
      const nativeRows = Math.ceil((features.length * 2) / 3);
      const inlineRows = thermostatFeatureRows(
        this,
        features,
        thermostatState(this)
      );
      options.rows += inlineRows - nativeRows;
      options.min_rows += inlineRows - nativeRows;
    }
    return options;
  };
  cardClass.prototype.__wiserInlineFeaturesPatched = true;

  const visit = (root) => {
    for (const element of root.querySelectorAll?.("*") || []) {
      if (element.localName === NATIVE_THERMOSTAT_CARD) {
        applyThermostatInlineFeatures(element);
      }
      if (element.shadowRoot) visit(element.shadowRoot);
    }
  };
  visit(document);
};

const thermostatFeaturePositionSchema = (hass) => ({
  name: "features_position",
  required: true,
  label:
    hass.localize("ui.panel.lovelace.editor.card.tile.features_position") ||
    "Features position",
  selector: {
    select: {
      mode: "box",
      options: ["bottom", "inline"].map((value) => ({
        label:
          hass.localize(
            `ui.panel.lovelace.editor.card.tile.features_position_options.${value}`
          ) || titleCase(value),
        description:
          value === "inline"
            ? "Uses available width dynamically and wraps when needed"
            : hass.localize(
                `ui.panel.lovelace.editor.card.tile.features_position_options.${value}_description`
              ),
        value,
        image: {
          src: `/static/images/form/tile_features_position_${value}.svg`,
          src_dark: `/static/images/form/tile_features_position_${value}_dark.svg`,
          flip_rtl: true,
        },
      })),
    },
  },
});

const injectThermostatFeaturePositionEditor = (editor) => {
  const root = editor.shadowRoot;
  const content = root?.querySelector("ha-expansion-panel .content");
  const stateObj = thermostatState(editor);
  const hasFeatures = Boolean(editor._config?.features?.length);
  let form = root?.querySelector("ha-form[data-wiser-features-position]");
  if (!content || !hasFeatures || !wiserControlsEnabled(stateObj)) {
    form?.remove();
    return;
  }

  if (!form) {
    form = document.createElement("ha-form");
    form.dataset.wiserFeaturesPosition = "";
    form.computeLabel = (schema) => schema.label;
    form.addEventListener("value-changed", (event) => {
      event.stopPropagation();
      const featuresPosition = event.detail.value.features_position || "bottom";
      const config = {
        ...editor._config,
        features_position: featuresPosition,
      };
      editor._config = config;
      editor.dispatchEvent(
        new CustomEvent("config-changed", {
          bubbles: true,
          composed: true,
          detail: { config },
        })
      );
    });
    content.append(form);

    let style = root.querySelector("style[data-wiser-features-position]");
    if (!style) {
      style = document.createElement("style");
      style.dataset.wiserFeaturesPosition = "";
      style.textContent = `
        ha-form[data-wiser-features-position] {
          display: block;
          margin-top: var(--ha-space-6, 24px);
        }
      `;
      root.append(style);
    }
  }
  form.hass = editor.hass;
  form.data = {
    features_position: editor._config.features_position || "bottom",
  };
  form.schema = [thermostatFeaturePositionSchema(editor.hass)];
};

const patchNativeThermostatEditor = async () => {
  await customElements.whenDefined(NATIVE_THERMOSTAT_EDITOR);
  const editorClass = customElements.get(NATIVE_THERMOSTAT_EDITOR);
  if (!editorClass || editorClass.prototype.__wiserInlineFeaturesPatched) return;

  const originalSetConfig = editorClass.prototype.setConfig;
  editorClass.prototype.setConfig = function (config) {
    const featuresPosition = config.features_position;
    const nativeConfig = { ...config };
    delete nativeConfig.features_position;
    const result = originalSetConfig.call(this, nativeConfig);
    this._config = {
      ...this._config,
      ...(featuresPosition ? { features_position: featuresPosition } : {}),
    };
    return result;
  };

  const originalValueChanged = editorClass.prototype._valueChanged;
  editorClass.prototype._valueChanged = function (event) {
    if (this._config?.features_position && event.detail?.value) {
      event.detail.value = {
        ...event.detail.value,
        features_position: this._config.features_position,
      };
    }
    return originalValueChanged.call(this, event);
  };

  const originalUpdated = editorClass.prototype.updated;
  editorClass.prototype.updated = function (...args) {
    const result = originalUpdated?.apply(this, args);
    Promise.resolve(this.updateComplete).then(() =>
      injectThermostatFeaturePositionEditor(this)
    );
    return result;
  };
  editorClass.prototype.__wiserInlineFeaturesPatched = true;

  const visit = (root) => {
    for (const element of root.querySelectorAll?.("*") || []) {
      if (element.localName === NATIVE_THERMOSTAT_EDITOR) {
        injectThermostatFeaturePositionEditor(element);
      }
      if (element.shadowRoot) visit(element.shadowRoot);
    }
  };
  visit(document);
};

void patchNativeThermostatCard();
void patchNativeThermostatEditor();
