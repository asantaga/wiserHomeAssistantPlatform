const assert = require("node:assert/strict");
const {readFileSync} = require("node:fs");
const {resolve} = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

const source = readFileSync(resolve(__dirname, "../../custom_components/wiser/frontend/wiser-panel.js"), "utf8");
const settle = () => new Promise(resolve => setImmediate(resolve));
const deferred = () => {
  let resolve, reject;
  const promise = new Promise((yes, no) => { resolve = yes; reject = no; });
  return {promise, resolve, reject};
};

class Element {
  constructor(tag = "element") {
    this.tagName = tag;
    this.children = [];
    this.attributes = new Map();
    this.listeners = new Map();
    this.className = "";
    this.hidden = false;
    this.dataset = {};
    this.classList = {add() {}, remove() {}};
  }
  setAttribute(key, value) { this.attributes.set(key, value); }
  getAttribute(key) { return this.attributes.get(key); }
  removeAttribute(key) { this.attributes.delete(key); }
  addEventListener(event, callback) {
    const listeners = this.listeners.get(event) || [];
    listeners.push(callback);
    this.listeners.set(event, listeners);
  }
  dispatchEvent(event) {
    for (const callback of this.listeners.get(event.type) || []) callback(event);
  }
  append(...children) {
    for (const child of children) {
      child.remove();
      child.parentNode = this;
      this.children.push(child);
    }
  }
  replaceChildren(...children) {
    for (const child of this.children) child.parentNode = null;
    this.children = [];
    this.append(...children);
  }
  remove() {
    if (this.parentNode) {
      this.parentNode.children = this.parentNode.children.filter(child => child !== this);
      this.parentNode = null;
    }
  }
  querySelector(selector) {
    for (const child of this.children) {
      if (selector === ".message" ? child.className === "message" : child.tagName === selector) return child;
      const match = child.querySelector(selector);
      if (match) return match;
    }
    return null;
  }
  click() { this.dispatchEvent({type:"click", target:this}); }
  focus() { this.focused = true; }
}

class ShadowRoot extends Element {
  set innerHTML(html) {
    this.elements = new Map([...html.matchAll(/id="([^"]+)"/g)].map(([, id]) => [id, new Element()]));
    this.main = new Element("main");
  }
  getElementById(id) { return this.elements.get(id); }
  querySelector(selector) { return selector === "main" ? this.main : super.querySelector(selector); }
}

function setup(savedTab) {
  const registry = new Map();
  const instances = [];
  const imports = [];
  const errors = [];
  const plans = new Map();
  const storage = new Map(savedTab ? [["wiser-active-panel", savedTab]] : []);
  const blobs = [];
  class Host extends Element {
    attachShadow() { return this.shadowRoot = new ShadowRoot(); }
  }
  const document = {
    createElement(tag) {
      const Constructor = registry.get(tag);
      return Constructor ? new Constructor() : new Element(tag);
    },
  };
  const context = vm.createContext({
    HTMLElement:Host, document, Blob,
    URL:{createObjectURL(blob) {blobs.push(blob); return "blob:export";}, revokeObjectURL() {}},
    window:{sessionStorage:{getItem:key => storage.get(key), setItem:(key, value) => storage.set(key, value)}},
    customElements:{
      get:name => registry.get(name),
      define:(name, value) => registry.set(name, value),
      whenDefined:name => registry.has(name) ? Promise.resolve() : Promise.reject(Error(`Undefined ${name}`)),
    },
    CustomEvent:class { constructor(type, options) {this.type = type; Object.assign(this, options);} },
    console:{error:(...args) => errors.push(args)},
  });
  vm.runInContext(source, context);
  const shell = new (registry.get("wiser-panel"))();
  const panels = ["rooms", "zigbee", "schedule"].map(id => ({
    id, title:id, component:`wiser-${id}-panel`, module_url:`/wiser/${id}.js`,
    config:{hubs:["House"], card_configs:{House:{columns:2}}},
  }));
  shell._importPanel = async url => {
    imports.push(url);
    await plans.get(url)?.();
    const panel = panels.find(panel => panel.module_url === url);
    if (!registry.has(panel.component)) {
      registry.set(panel.component, class extends Element {
        constructor() {super(panel.component); this.configurations = []; this.updates = []; instances.push(this);}
        set hass(value) {this.updates.push(value);}
        set panel(value) {this.configurations.push(value.config);}
        _openEditor() {this.editorOpened = true;}
      });
    }
  };
  shell.hass = {user:{is_admin:true}, states:{}, callWS:async () => {}};
  return {shell, panels, imports, instances, plans, errors, storage, blobs};
}

const configure = ({shell, panels}) => {shell.panel = {config:{panels}};};

test("opening the sidebar imports and creates only the selected panel", async () => {
  const state = setup();
  configure(state);
  assert.deepEqual(state.imports, ["/wiser/rooms.js"]);
  assert.equal(state.shell._tabs.length, 3);
  assert.equal(state.instances.length, 0);
  assert.equal(state.shell.shadowRoot.main.getAttribute("aria-busy"), "true");
  await settle();
  assert.equal(state.instances.length, 1);
  assert.equal(state.shell._views[1], null);
  assert.equal(state.shell._views[2], null);
  assert.equal(state.shell._views[0].getAttribute("nested"), "");
  assert.equal(state.shell._views[0].getAttribute("aria-labelledby"), state.shell._tabs[0].id);
  assert.equal(state.shell._tabs[0].getAttribute("aria-selected"), "true");
  assert.equal(state.shell.shadowRoot.main.querySelector(".message"), null);
  assert.equal(state.shell.shadowRoot.getElementById("settings").hidden, false);
});

test("restores the remembered tab without loading earlier panels", async () => {
  const state = setup("zigbee");
  configure(state);
  await settle();
  assert.deepEqual(state.imports, ["/wiser/zigbee.js"]);
  assert.equal(state.shell._views[0], null);
  assert.equal(state.instances.length, 1);
  assert.equal(state.shell._tabs[1].tabIndex, 0);
});

test("visited panels keep their instances and only the active panel receives hass", async () => {
  const state = setup(); configure(state); await settle();
  const rooms = state.shell._views[0];
  state.shell._tabs[1].click(); await settle();
  const zigbee = state.shell._views[1];
  assert.equal(rooms.hidden, true);
  const roomUpdates = rooms.updates.length;
  const latest = {user:{is_admin:false}, states:{new:true}};
  state.shell.hass = latest;
  assert.equal(rooms.updates.length, roomUpdates);
  assert.equal(zigbee.updates.at(-1), latest);
  state.shell._selectPanel("rooms"); await settle();
  assert.equal(state.shell._views[0], rooms);
  assert.equal(rooms.updates.at(-1), latest);
  assert.equal(rooms.configurations.length, 1);
  assert.equal(zigbee.hidden, true);
  assert.deepEqual(state.imports, ["/wiser/rooms.js", "/wiser/zigbee.js"]);
  assert.equal(state.instances.length, 2);
});

test("rapid tab switching discards stale completion and shares pending imports", async () => {
  const state = setup(); const slow = deferred();
  state.plans.set("/wiser/rooms.js", () => slow.promise);
  configure(state);
  state.shell._selectPanel("rooms");
  assert.deepEqual(state.imports, ["/wiser/rooms.js"]);
  state.shell._selectPanel("zigbee"); await settle();
  const zigbee = state.shell._views[1];
  slow.resolve(); await settle();
  assert.equal(state.shell._views[0], null);
  assert.equal(state.instances.length, 1);
  assert.equal(zigbee.hidden, false);
  state.shell._selectPanel("rooms"); await settle();
  assert.equal(state.instances.length, 2);
  assert.deepEqual(state.imports, ["/wiser/rooms.js", "/wiser/zigbee.js"]);
});

test("failure keeps other tabs available and Retry loads the failed tab", async () => {
  const state = setup(); let failed = true;
  state.plans.set("/wiser/rooms.js", () => {if (failed) throw Error("offline");});
  configure(state); await settle();
  assert.equal(state.errors.length, 1);
  assert.equal(state.shell._tabs.length, 3);
  assert.equal(state.shell.shadowRoot.getElementById("settings").hidden, true);
  const message = state.shell.shadowRoot.main.querySelector(".message");
  assert.equal(message.getAttribute("role"), "alert");
  failed = false;
  message.querySelector("ha-button").click(); await settle();
  assert.equal(state.instances.length, 1);
  assert.equal(state.shell.shadowRoot.main.querySelector(".message"), null);
  state.shell._selectPanel("zigbee"); await settle();
  assert.equal(state.instances.length, 2);
});

test("reordering while loading preserves the pending request and correct tab association", async () => {
  const state = setup(); const slow = deferred();
  state.plans.set("/wiser/rooms.js", () => slow.promise);
  configure(state);
  state.shell._applyPanels([state.panels[1], state.panels[0], state.panels[2]]);
  slow.resolve(); await settle();
  assert.deepEqual(state.imports, ["/wiser/rooms.js"]);
  assert.equal(state.instances.length, 1);
  assert.equal(state.shell._views[0], null);
  assert.equal(state.shell._views[1].id, "wiser-panel-view-1");
  assert.equal(state.shell._tabs[1].getAttribute("aria-selected"), "true");
  const rooms = state.shell._views[1];
  state.shell._applyPanels(state.panels);
  assert.equal(state.shell._views[0], rooms);
  assert.equal(rooms.id, "wiser-panel-view-0");
});

test("configuration updates reuse visited panels and defer hidden panel changes until selected", async () => {
  const state = setup(); configure(state); await settle();
  const rooms = state.shell._views[0];
  state.shell._selectPanel("zigbee"); await settle();
  const zigbee = state.shell._views[1];
  const updated = state.panels.map(panel => ({...panel, config:{...panel.config, updated:true}}));
  state.shell.panel = {config:{panels:updated}};
  assert.equal(state.shell._views[0], rooms);
  assert.equal(state.shell._views[1], zigbee);
  assert.equal(zigbee.configurations.at(-1).updated, true);
  assert.equal(rooms.configurations.length, 1);
  state.shell._selectPanel("rooms");
  assert.equal(rooms.configurations.at(-1).updated, true);
  assert.equal(state.instances.length, 2);
  assert.equal(state.shell._views[2], null);
});

test("removing a loading tab prevents its stale content from appearing", async () => {
  const state = setup(); const slow = deferred();
  state.plans.set("/wiser/rooms.js", () => slow.promise);
  configure(state);
  state.shell.panel = {config:{panels:state.panels.slice(1)}};
  await settle();
  slow.resolve(); await settle();
  assert.equal(state.instances.length, 1);
  assert.equal(state.shell._activePanel, "zigbee");
  assert.equal(state.shell._views[0].tagName, "wiser-zigbee-panel");
});

test("keyboard navigation opens the next tab and export includes unvisited panel settings", async () => {
  const state = setup(); configure(state); await settle();
  state.shell._tabs[0].dispatchEvent({type:"keydown", key:"ArrowRight", preventDefault() {}});
  await settle();
  assert.equal(state.shell._activePanel, "zigbee");
  assert.equal(state.shell._tabs[1].focused, true);
  state.shell._exportConfiguration();
  const exported = JSON.parse(await state.blobs[0].text());
  assert.deepEqual(Object.keys(exported.panels), ["rooms", "zigbee", "schedule"]);
  assert.equal(state.shell._views[2], null);
  assert.equal(state.imports.length, 2);
});

test("an empty registry clears busy state and exposes no panel actions", async () => {
  const state = setup(); state.shell.panel = {config:{panels:[]}};
  assert.equal(state.imports.length, 0);
  assert.equal(state.shell.shadowRoot.main.getAttribute("aria-busy"), undefined);
  assert.equal(state.shell.shadowRoot.getElementById("settings").hidden, true);
});


test("leaving the sidebar suppresses pending creation and returning resumes the selected tab", async () => {
  const state = setup(); const slow = deferred();
  state.plans.set("/wiser/rooms.js", () => slow.promise);
  configure(state);
  state.shell.disconnectedCallback();
  slow.resolve(); await settle();
  assert.equal(state.instances.length, 0);
  state.shell.connectedCallback(); await settle();
  assert.equal(state.instances.length, 1);
  assert.deepEqual(state.imports, ["/wiser/rooms.js"]);
});
