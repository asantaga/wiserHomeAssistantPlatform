/*! WISER-CARD-VERSION wiser-climate-more-info 1.0.0 */

// The structure and behaviour in this control deliberately follow Home
// Assistant's native MoreInfoClimate and HaStateControlClimateTemperature:
// https://github.com/home-assistant/frontend/blob/dev/src/dialogs/more-info/controls/more-info-climate.ts
// https://github.com/home-assistant/frontend/blob/dev/src/state-control/climate/ha-state-control-climate-temperature.ts
// Reviewed 2026-10-27. Home Assistant frontend is licensed under Apache-2.0.
// We reuse HA's registered temperature control instead of replacing its
// temperature/service behaviour; this element only supplies Wiser presentation
// and the two controls supported by Wiser rooms.

const MORE_INFO_TYPE = "wiser-climate-more-info";
const NATIVE_TEMPERATURE_CONTROL = "ha-state-control-climate-temperature";
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

class WiserClimateMoreInfo extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._styleGeneration = 0;
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

  _demand() {
    const demand = Number(this._stateObj?.attributes?.percentage_demand);
    return Number.isFinite(demand) ? demand : 0;
  }

  _extraInfo() {
    const state = this._stateObj?.state;
    const mode = this._stateObj?.attributes?.is_passive
      ? "Passive"
      : state === "heat"
        ? "Manual"
        : this._formatState(state);
    return state === "off" ? mode : `${mode} · ${this._demand()}%`;
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
      ha-state-control-climate-temperature {
        box-sizing: border-box;
        width: min(100%, 450px);
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

    const content = document.createElement("div");
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

    content.append(current, controls, selects);
    this.shadowRoot.replaceChildren(style, content);
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
    const generation = ++this._styleGeneration;
    const control = this._temperatureControl;
    await control.updateComplete;
    if (generation !== this._styleGeneration || !control.shadowRoot) return;

    const demand = this._demand();
    const passive = Boolean(this._stateObj.attributes.is_passive);
    const state = this._stateObj.state;
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
    control.style.setProperty(
      `--state-climate-${state}-color`,
      modeColor
    );
    control.style.setProperty(
      "--wiser-extra-info-text",
      `"\\A ${cssString(this._extraInfo())}"`
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
      .info > p:last-of-type::after {
        color: var(--extra-info-text-color, var(--action-color));
        content: var(--wiser-extra-info-text);
        white-space: pre;
      }
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

    const slider = control.shadowRoot.querySelector(
      "ha-control-circular-slider"
    );
    if (!slider) return;
    await slider.updateComplete;
    if (generation !== this._styleGeneration || !slider.shadowRoot) return;

    let sliderStyle = slider.shadowRoot.querySelector(
      "style[data-wiser-theme]"
    );
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
