var wiserschedulecard=function(t){"use strict";var e=function(t,i){return e=Object.setPrototypeOf||{__proto__:[]}instanceof Array&&function(t,e){t.__proto__=e}||function(t,e){for(var i in e)Object.prototype.hasOwnProperty.call(e,i)&&(t[i]=e[i])},e(t,i)};function i(t,i){if("function"!=typeof i&&null!==i)throw new TypeError("Class extends value "+String(i)+" is not a constructor or null");function s(){this.constructor=t}e(t,i),t.prototype=null===i?Object.create(i):(s.prototype=i.prototype,new s)}var s=function(){return s=Object.assign||function(t){for(var e,i=1,s=arguments.length;i<s;i++)for(var n in e=arguments[i])Object.prototype.hasOwnProperty.call(e,n)&&(t[n]=e[n]);return t},s.apply(this,arguments)};function n(t,e,i,s){var n,r=arguments.length,o=r<3?e:null===s?s=Object.getOwnPropertyDescriptor(e,i):s;if("object"==typeof Reflect&&"function"==typeof Reflect.decorate)o=Reflect.decorate(t,e,i,s);else for(var a=t.length-1;a>=0;a--)(n=t[a])&&(o=(r<3?n(o):r>3?n(e,i,o):n(e,i))||o);return r>3&&o&&Object.defineProperty(e,i,o),o}function r(t){var e="function"==typeof Symbol&&Symbol.iterator,i=e&&t[e],s=0;if(i)return i.call(t);if(t&&"number"==typeof t.length)return{next:function(){return t&&s>=t.length&&(t=void 0),{value:t&&t[s++],done:!t}}};throw new TypeError(e?"Object is not iterable.":"Symbol.iterator is not defined.")}"function"==typeof SuppressedError&&SuppressedError;
/**
     * @license
     * Copyright 2019 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
const o=globalThis,a=o.ShadowRoot&&(void 0===o.ShadyCSS||o.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,l=Symbol(),d=new WeakMap;let c=class{constructor(t,e,i){if(this._$cssResult$=!0,i!==l)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o;const e=this.t;if(a&&void 0===t){const i=void 0!==e&&1===e.length;i&&(t=d.get(e)),void 0===t&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),i&&d.set(e,t))}return t}toString(){return this.cssText}};const h=(t,...e)=>{const i=1===t.length?t[0]:e.reduce((e,i,s)=>e+(t=>{if(!0===t._$cssResult$)return t.cssText;if("number"==typeof t)return t;throw Error("Value passed to 'css' function must be a 'css' function result: "+t+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+t[s+1],t[0]);return new c(i,t,l)},p=(t,e)=>{if(a)t.adoptedStyleSheets=e.map(t=>t instanceof CSSStyleSheet?t:t.styleSheet);else for(const i of e){const e=document.createElement("style"),s=o.litNonce;void 0!==s&&e.setAttribute("nonce",s),e.textContent=i.cssText,t.appendChild(e)}},u=a?t=>t:t=>t instanceof CSSStyleSheet?(t=>{let e="";for(const i of t.cssRules)e+=i.cssText;return(t=>new c("string"==typeof t?t:t+"",void 0,l))(e)})(t):t,{is:m,defineProperty:f,getOwnPropertyDescriptor:g,getOwnPropertyNames:v,getOwnPropertySymbols:_,getPrototypeOf:b}=Object,y=globalThis,x=y.trustedTypes,$=x?x.emptyScript:"",w=y.reactiveElementPolyfillSupport,A=(t,e)=>t,E={toAttribute(t,e){switch(e){case Boolean:t=t?$:null;break;case Object:case Array:t=null==t?t:JSON.stringify(t)}return t},fromAttribute(t,e){let i=t;switch(e){case Boolean:i=null!==t;break;case Number:i=null===t?null:Number(t);break;case Object:case Array:try{i=JSON.parse(t)}catch(t){i=null}}return i}},S=(t,e)=>!m(t,e),C={attribute:!0,type:String,converter:E,reflect:!1,useDefault:!1,hasChanged:S};
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */Symbol.metadata??=Symbol("metadata"),y.litPropertyMetadata??=new WeakMap;let T=class extends HTMLElement{static addInitializer(t){this._$Ei(),(this.l??=[]).push(t)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(t,e=C){if(e.state&&(e.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(t)&&((e=Object.create(e)).wrapped=!0),this.elementProperties.set(t,e),!e.noAccessor){const i=Symbol(),s=this.getPropertyDescriptor(t,i,e);void 0!==s&&f(this.prototype,t,s)}}static getPropertyDescriptor(t,e,i){const{get:s,set:n}=g(this.prototype,t)??{get(){return this[e]},set(t){this[e]=t}};return{get:s,set(e){const r=s?.call(this);n?.call(this,e),this.requestUpdate(t,r,i)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)??C}static _$Ei(){if(this.hasOwnProperty(A("elementProperties")))return;const t=b(this);t.finalize(),void 0!==t.l&&(this.l=[...t.l]),this.elementProperties=new Map(t.elementProperties)}static finalize(){if(this.hasOwnProperty(A("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(A("properties"))){const t=this.properties,e=[...v(t),..._(t)];for(const i of e)this.createProperty(i,t[i])}const t=this[Symbol.metadata];if(null!==t){const e=litPropertyMetadata.get(t);if(void 0!==e)for(const[t,i]of e)this.elementProperties.set(t,i)}this._$Eh=new Map;for(const[t,e]of this.elementProperties){const i=this._$Eu(t,e);void 0!==i&&this._$Eh.set(i,t)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(t){const e=[];if(Array.isArray(t)){const i=new Set(t.flat(1/0).reverse());for(const t of i)e.unshift(u(t))}else void 0!==t&&e.push(u(t));return e}static _$Eu(t,e){const i=e.attribute;return!1===i?void 0:"string"==typeof i?i:"string"==typeof t?t.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(t=>t(this))}addController(t){(this._$EO??=new Set).add(t),void 0!==this.renderRoot&&this.isConnected&&t.hostConnected?.()}removeController(t){this._$EO?.delete(t)}_$E_(){const t=new Map,e=this.constructor.elementProperties;for(const i of e.keys())this.hasOwnProperty(i)&&(t.set(i,this[i]),delete this[i]);t.size>0&&(this._$Ep=t)}createRenderRoot(){const t=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return p(t,this.constructor.elementStyles),t}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(t=>t.hostConnected?.())}enableUpdating(t){}disconnectedCallback(){this._$EO?.forEach(t=>t.hostDisconnected?.())}attributeChangedCallback(t,e,i){this._$AK(t,i)}_$ET(t,e){const i=this.constructor.elementProperties.get(t),s=this.constructor._$Eu(t,i);if(void 0!==s&&!0===i.reflect){const n=(void 0!==i.converter?.toAttribute?i.converter:E).toAttribute(e,i.type);this._$Em=t,null==n?this.removeAttribute(s):this.setAttribute(s,n),this._$Em=null}}_$AK(t,e){const i=this.constructor,s=i._$Eh.get(t);if(void 0!==s&&this._$Em!==s){const t=i.getPropertyOptions(s),n="function"==typeof t.converter?{fromAttribute:t.converter}:void 0!==t.converter?.fromAttribute?t.converter:E;this._$Em=s;const r=n.fromAttribute(e,t.type);this[s]=r??this._$Ej?.get(s)??r,this._$Em=null}}requestUpdate(t,e,i){if(void 0!==t){const s=this.constructor,n=this[t];if(i??=s.getPropertyOptions(t),!((i.hasChanged??S)(n,e)||i.useDefault&&i.reflect&&n===this._$Ej?.get(t)&&!this.hasAttribute(s._$Eu(t,i))))return;this.C(t,e,i)}!1===this.isUpdatePending&&(this._$ES=this._$EP())}C(t,e,{useDefault:i,reflect:s,wrapped:n},r){i&&!(this._$Ej??=new Map).has(t)&&(this._$Ej.set(t,r??e??this[t]),!0!==n||void 0!==r)||(this._$AL.has(t)||(this.hasUpdated||i||(e=void 0),this._$AL.set(t,e)),!0===s&&this._$Em!==t&&(this._$Eq??=new Set).add(t))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(t){Promise.reject(t)}const t=this.scheduleUpdate();return null!=t&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(const[t,e]of this._$Ep)this[t]=e;this._$Ep=void 0}const t=this.constructor.elementProperties;if(t.size>0)for(const[e,i]of t){const{wrapped:t}=i,s=this[e];!0!==t||this._$AL.has(e)||void 0===s||this.C(e,void 0,i,s)}}let t=!1;const e=this._$AL;try{t=this.shouldUpdate(e),t?(this.willUpdate(e),this._$EO?.forEach(t=>t.hostUpdate?.()),this.update(e)):this._$EM()}catch(e){throw t=!1,this._$EM(),e}t&&this._$AE(e)}willUpdate(t){}_$AE(t){this._$EO?.forEach(t=>t.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(t){return!0}update(t){this._$Eq&&=this._$Eq.forEach(t=>this._$ET(t,this[t])),this._$EM()}updated(t){}firstUpdated(t){}};T.elementStyles=[],T.shadowRootOptions={mode:"open"},T[A("elementProperties")]=new Map,T[A("finalized")]=new Map,w?.({ReactiveElement:T}),(y.reactiveElementVersions??=[]).push("2.1.1");
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
const I=globalThis,O=I.trustedTypes,k=O?O.createPolicy("lit-html",{createHTML:t=>t}):void 0,R="$lit$",P=`lit$${Math.random().toFixed(9).slice(2)}$`,L="?"+P,M=`<${L}>`,N=document,D=()=>N.createComment(""),H=t=>null===t||"object"!=typeof t&&"function"!=typeof t,U=Array.isArray,z="[ \t\n\f\r]",F=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,B=/-->/g,V=/>/g,j=RegExp(`>|${z}(?:([^\\s"'>=/]+)(${z}*=${z}*(?:[^ \t\n\f\r"'\`<>=]|("|')|))|$)`,"g"),W=/'/g,q=/"/g,Y=/^(?:script|style|textarea|title)$/i,X=(t=>(e,...i)=>({_$litType$:t,strings:e,values:i}))(1),G=Symbol.for("lit-noChange"),K=Symbol.for("lit-nothing"),J=new WeakMap,Z=N.createTreeWalker(N,129);function Q(t,e){if(!U(t)||!t.hasOwnProperty("raw"))throw Error("invalid template strings array");return void 0!==k?k.createHTML(e):e}let tt=class t{constructor({strings:e,_$litType$:i},s){let n;this.parts=[];let r=0,o=0;const a=e.length-1,l=this.parts,[d,c]=((t,e)=>{const i=t.length-1,s=[];let n,r=2===e?"<svg>":3===e?"<math>":"",o=F;for(let e=0;e<i;e++){const i=t[e];let a,l,d=-1,c=0;for(;c<i.length&&(o.lastIndex=c,l=o.exec(i),null!==l);)c=o.lastIndex,o===F?"!--"===l[1]?o=B:void 0!==l[1]?o=V:void 0!==l[2]?(Y.test(l[2])&&(n=RegExp("</"+l[2],"g")),o=j):void 0!==l[3]&&(o=j):o===j?">"===l[0]?(o=n??F,d=-1):void 0===l[1]?d=-2:(d=o.lastIndex-l[2].length,a=l[1],o=void 0===l[3]?j:'"'===l[3]?q:W):o===q||o===W?o=j:o===B||o===V?o=F:(o=j,n=void 0);const h=o===j&&t[e+1].startsWith("/>")?" ":"";r+=o===F?i+M:d>=0?(s.push(a),i.slice(0,d)+R+i.slice(d)+P+h):i+P+(-2===d?e:h)}return[Q(t,r+(t[i]||"<?>")+(2===e?"</svg>":3===e?"</math>":"")),s]})(e,i);if(this.el=t.createElement(d,s),Z.currentNode=this.el.content,2===i||3===i){const t=this.el.content.firstChild;t.replaceWith(...t.childNodes)}for(;null!==(n=Z.nextNode())&&l.length<a;){if(1===n.nodeType){if(n.hasAttributes())for(const t of n.getAttributeNames())if(t.endsWith(R)){const e=c[o++],i=n.getAttribute(t).split(P),s=/([.?@])?(.*)/.exec(e);l.push({type:1,index:r,name:s[2],strings:i,ctor:"."===s[1]?rt:"?"===s[1]?ot:"@"===s[1]?at:nt}),n.removeAttribute(t)}else t.startsWith(P)&&(l.push({type:6,index:r}),n.removeAttribute(t));if(Y.test(n.tagName)){const t=n.textContent.split(P),e=t.length-1;if(e>0){n.textContent=O?O.emptyScript:"";for(let i=0;i<e;i++)n.append(t[i],D()),Z.nextNode(),l.push({type:2,index:++r});n.append(t[e],D())}}}else if(8===n.nodeType)if(n.data===L)l.push({type:2,index:r});else{let t=-1;for(;-1!==(t=n.data.indexOf(P,t+1));)l.push({type:7,index:r}),t+=P.length-1}r++}}static createElement(t,e){const i=N.createElement("template");return i.innerHTML=t,i}};function et(t,e,i=t,s){if(e===G)return e;let n=void 0!==s?i._$Co?.[s]:i._$Cl;const r=H(e)?void 0:e._$litDirective$;return n?.constructor!==r&&(n?._$AO?.(!1),void 0===r?n=void 0:(n=new r(t),n._$AT(t,i,s)),void 0!==s?(i._$Co??=[])[s]=n:i._$Cl=n),void 0!==n&&(e=et(t,n._$AS(t,e.values),n,s)),e}let it=class{constructor(t,e){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){const{el:{content:e},parts:i}=this._$AD,s=(t?.creationScope??N).importNode(e,!0);Z.currentNode=s;let n=Z.nextNode(),r=0,o=0,a=i[0];for(;void 0!==a;){if(r===a.index){let e;2===a.type?e=new st(n,n.nextSibling,this,t):1===a.type?e=new a.ctor(n,a.name,a.strings,this,t):6===a.type&&(e=new lt(n,this,t)),this._$AV.push(e),a=i[++o]}r!==a?.index&&(n=Z.nextNode(),r++)}return Z.currentNode=N,s}p(t){let e=0;for(const i of this._$AV)void 0!==i&&(void 0!==i.strings?(i._$AI(t,i,e),e+=i.strings.length-2):i._$AI(t[e])),e++}},st=class t{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(t,e,i,s){this.type=2,this._$AH=K,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=i,this.options=s,this._$Cv=s?.isConnected??!0}get parentNode(){let t=this._$AA.parentNode;const e=this._$AM;return void 0!==e&&11===t?.nodeType&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=et(this,t,e),H(t)?t===K||null==t||""===t?(this._$AH!==K&&this._$AR(),this._$AH=K):t!==this._$AH&&t!==G&&this._(t):void 0!==t._$litType$?this.$(t):void 0!==t.nodeType?this.T(t):(t=>U(t)||"function"==typeof t?.[Symbol.iterator])(t)?this.k(t):this._(t)}O(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}T(t){this._$AH!==t&&(this._$AR(),this._$AH=this.O(t))}_(t){this._$AH!==K&&H(this._$AH)?this._$AA.nextSibling.data=t:this.T(N.createTextNode(t)),this._$AH=t}$(t){const{values:e,_$litType$:i}=t,s="number"==typeof i?this._$AC(t):(void 0===i.el&&(i.el=tt.createElement(Q(i.h,i.h[0]),this.options)),i);if(this._$AH?._$AD===s)this._$AH.p(e);else{const t=new it(s,this),i=t.u(this.options);t.p(e),this.T(i),this._$AH=t}}_$AC(t){let e=J.get(t.strings);return void 0===e&&J.set(t.strings,e=new tt(t)),e}k(e){U(this._$AH)||(this._$AH=[],this._$AR());const i=this._$AH;let s,n=0;for(const r of e)n===i.length?i.push(s=new t(this.O(D()),this.O(D()),this,this.options)):s=i[n],s._$AI(r),n++;n<i.length&&(this._$AR(s&&s._$AB.nextSibling,n),i.length=n)}_$AR(t=this._$AA.nextSibling,e){for(this._$AP?.(!1,!0,e);t!==this._$AB;){const e=t.nextSibling;t.remove(),t=e}}setConnected(t){void 0===this._$AM&&(this._$Cv=t,this._$AP?.(t))}},nt=class{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(t,e,i,s,n){this.type=1,this._$AH=K,this._$AN=void 0,this.element=t,this.name=e,this._$AM=s,this.options=n,i.length>2||""!==i[0]||""!==i[1]?(this._$AH=Array(i.length-1).fill(new String),this.strings=i):this._$AH=K}_$AI(t,e=this,i,s){const n=this.strings;let r=!1;if(void 0===n)t=et(this,t,e,0),r=!H(t)||t!==this._$AH&&t!==G,r&&(this._$AH=t);else{const s=t;let o,a;for(t=n[0],o=0;o<n.length-1;o++)a=et(this,s[i+o],e,o),a===G&&(a=this._$AH[o]),r||=!H(a)||a!==this._$AH[o],a===K?t=K:t!==K&&(t+=(a??"")+n[o+1]),this._$AH[o]=a}r&&!s&&this.j(t)}j(t){t===K?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,t??"")}},rt=class extends nt{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===K?void 0:t}},ot=class extends nt{constructor(){super(...arguments),this.type=4}j(t){this.element.toggleAttribute(this.name,!!t&&t!==K)}},at=class extends nt{constructor(t,e,i,s,n){super(t,e,i,s,n),this.type=5}_$AI(t,e=this){if((t=et(this,t,e,0)??K)===G)return;const i=this._$AH,s=t===K&&i!==K||t.capture!==i.capture||t.once!==i.once||t.passive!==i.passive,n=t!==K&&(i===K||s);s&&this.element.removeEventListener(this.name,this,i),n&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){"function"==typeof this._$AH?this._$AH.call(this.options?.host??this.element,t):this._$AH.handleEvent(t)}},lt=class{constructor(t,e,i){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=i}get _$AU(){return this._$AM._$AU}_$AI(t){et(this,t)}};const dt=I.litHtmlPolyfillSupport;dt?.(tt,st),(I.litHtmlVersions??=[]).push("3.3.1");const ct=globalThis;
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */let ht=class extends T{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){const t=super.createRenderRoot();return this.renderOptions.renderBefore??=t.firstChild,t}update(t){const e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=((t,e,i)=>{const s=i?.renderBefore??e;let n=s._$litPart$;if(void 0===n){const t=i?.renderBefore??null;s._$litPart$=n=new st(e.insertBefore(D(),t),t,void 0,i??{})}return n._$AI(t),n})(e,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return G}};ht._$litElement$=!0,ht.finalized=!0,ct.litElementHydrateSupport?.({LitElement:ht});const pt=ct.litElementPolyfillSupport;pt?.({LitElement:ht}),(ct.litElementVersions??=[]).push("4.2.1");
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
const ut=t=>(e,i)=>{void 0!==i?i.addInitializer(()=>{customElements.define(t,e)}):customElements.define(t,e)},mt={attribute:!0,type:String,converter:E,reflect:!1,hasChanged:S},ft=(t=mt,e,i)=>{const{kind:s,metadata:n}=i;let r=globalThis.litPropertyMetadata.get(n);if(void 0===r&&globalThis.litPropertyMetadata.set(n,r=new Map),"setter"===s&&((t=Object.create(t)).wrapped=!0),r.set(i.name,t),"accessor"===s){const{name:s}=i;return{set(i){const n=e.get.call(this);e.set.call(this,i),this.requestUpdate(s,n,t)},init(e){return void 0!==e&&this.C(s,void 0,t,e),e}}}if("setter"===s){const{name:s}=i;return function(i){const n=this[s];e.call(this,i),this.requestUpdate(s,n,t)}}throw Error("Unsupported decorator location: "+s)};
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */function gt(t){return(e,i)=>"object"==typeof i?ft(t,e,i):((t,e,i)=>{const s=e.hasOwnProperty(i);return e.constructor.createProperty(i,t),s?Object.getOwnPropertyDescriptor(e,i):void 0})(t,e,i)}
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */function vt(t){return gt({...t,state:!0,attribute:!1})}
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */var _t,bt;!function(t){t.language="language",t.system="system",t.comma_decimal="comma_decimal",t.decimal_comma="decimal_comma",t.space_comma="space_comma",t.none="none"}(_t||(_t={})),function(t){t.language="language",t.system="system",t.am_pm="12",t.twenty_four="24"}(bt||(bt={}));var yt=function(t,e,i,s){s=s||{},i=null==i?{}:i;var n=new Event(e,{bubbles:void 0===s.bubbles||s.bubbles,cancelable:Boolean(s.cancelable),composed:void 0===s.composed||s.composed});return n.detail=i,t.dispatchEvent(n),n};function xt(t,e,i){if(e.has("config")||i)return!0;if(t.config.entity){var s=e.get("hass");return!s||s.states[t.config.entity]!==t.hass.states[t.config.entity]}return!1}const $t="1.4.0",wt=86400;var At,Et,St,Ct;!function(t){t.Heating="mdi:radiator",t.OnOff="mdi:power-socket-uk",t.Shutters="mdi:blinds",t.Lighting="mdi:lightbulb-outline"}(At||(At={})),function(t){t.Overview="OVERVIEW",t.ScheduleEdit="SCHEDULE_EDIT",t.ScheduleCopy="SCHEDULE_COPY",t.ScheduleAdd="SCHEDULE_ADD",t.ScheduleRename="SCHEDULE_RENAME"}(Et||(Et={})),function(t){t.Heating="19",t.OnOff="Off",t.Lighting="0",t.Shutters="100"}(St||(St={})),function(t){t.Heating="°C",t.OnOff="",t.Lighting="%",t.Shutters="%"}(Ct||(Ct={}));const Tt=["Heating","OnOff","Lighting","Shutters"],It=["Lighting","Shutters"],Ot=["Weekdays","Weekend"],kt=["Monday","Tuesday","Wednesday","Thursday","Friday"],Rt=["Saturday","Sunday"],Pt=kt.concat(Rt),Lt=["Sunrise","Sunset"];var Mt;!function(t){t.Sunrise="3000",t.Sunset="4000"}(Mt||(Mt={}));var Nt={version:"Version",invalid_configuration:"Invalid configuration",no_schedules:"No Schedules Found",name_required:"Name is required"},Dt={actions:{copy:"Copy",files:"Files",rename:"Rename",add:"Add",view:"View",add_schedule:"Add Schedule"},labels:{setting:"Setting",name:"Name",assigns:"Assigns",start:"Start",end:"End",to:"to"},days:{monday:"Monday",tuesday:"Tuesday",wednesday:"Wednesday",thursday:"Thursday",friday:"Friday",saturday:"Saturday",sunday:"Sunday",weekdays:"Weekdays",weekend:"Weekend",all:"All",short:{monday:"Mon",tuesday:"Tue",wednesday:"Wed",thursday:"Thu",friday:"Fri",saturday:"Sat",sunday:"Sun"}},headings:{schedule_actions:"Schedule Actions",schedule_type:"Schedule Type",schedule_id:"Schedule Id",schedule_name:"Schedule Name",schedule_assignment:"Room/Device Assignment",not_assigned:"(Not Assigned)",rename_schedule:"Rename Schedule",copy_schedule:"Copy Schedule",delete_schedule:"Delete Schedule"},helpers:{enter_new_name:"Enter the new name for the Schedule",select_copy_schedule:"Select the schedule to copy to",delete_schedule_confirm:"Are you sure you wish to delete the schedule",select_a_schedule:"Select a schedule to view",add_schedule:"Select the schedule type and enter a name for the schedule to create"}},Ht={common:Nt,wiser:Dt},Ut={version:"Déclinaison",invalid_configuration:"Configuration Invalide",no_schedules:"Aucun Programme Trouvé",name_required:"Nom est obligatoire"},zt={actions:{copy:"Copie",files:"Fichier",rename:"Renommer",add:"Ajouter",view:"Voir",add_schedule:"Ajouter un Programme"},labels:{setting:"Paramètre",name:"Nom",assigns:"Attribuers",start:"Début",end:"Fin",to:"à"},days:{monday:"Lundi",tuesday:"Mardi",wednesday:"Mercredi",thursday:"Jeudi",friday:"Vendredi",saturday:"Samedi",sunday:"Dimanche",weekdays:"Lun à Ven",weekend:"Sam et Dim",all:"Toute",short:{monday:"Lun",tuesday:"Mar",wednesday:"Mer",thursday:"Jeu",friday:"Ven",saturday:"Sam",sunday:"Dim"}},headings:{schedule_actions:"Programmer des Actions",schedule_type:"Type de Programme",schedule_id:"Numéro de Programme",schedule_name:"Nom de Programme",schedule_assignment:"Attribuer de Programme",not_assigned:"(Non Attribué)",rename_schedule:"Renommer le Programme",copy_schedule:"Copier le Programme",delete_schedule:"Supprimer le Programme"},helpers:{enter_new_name:"Entrez un nom pour le Programme",select_copy_schedule:"Sélectionnez le calendrier ci-dessous pour le copier",delete_schedule_confirm:"Êtes-vous sûr de vouloir effacer ce programme",select_a_schedule:"Sélectionner un programme à afficher",add_schedule:"Sélectionnez le type de programme et entrez un nom pour la programme à créer"}},Ft={common:Ut,wiser:zt};const Bt={en:Object.freeze({__proto__:null,common:Nt,default:Ht,wiser:Dt}),fr:Object.freeze({__proto__:null,common:Ut,default:Ft,wiser:zt})};function Vt(t,e="",i=""){const s=(localStorage.getItem("selectedLanguage")||"en").replace(/['"]+/g,"").replace("-","_");let n;try{n=t.split(".").reduce((t,e)=>t[e],Bt[s]),n||(n=t.split(".").reduce((t,e)=>t[e],Bt.en))}catch(e){try{n=t.split(".").reduce((t,e)=>t[e],Bt.en)}catch(t){n=""}}return void 0===n&&(n=t.split(".").reduce((t,e)=>t[e],Bt.en)),""!==e&&""!==i&&(n=n.replace(e,i)),n}const jt=h`
  .card-header {
    display: flex;
    justify-content: space-between;
  }
  .card-header .name {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    display: flex;
  }
  .card-header ha-switch {
    padding: 5px;
  }
  .card-header ha-icon-button {
    position: absolute;
    right: 6px;
    top: 6px;
  }
  .card-content {
    flex: 1;
  }
  .card-content > *:first-child {
    margin-top: 0;
  }
  .card-content > *:last-child {
    margin-bottom: 0;
  }
  div.text-field,
  div.secondary {
    color: var(--secondary-text-color);
  }
  .disabled {
    color: var(--disabled-text-color);
  }
  div.header {
    color: var(--secondary-text-color);
    text-transform: uppercase;
    font-weight: 500;
    font-size: 12px;
    margin: 20px 0px 0px 0px;
    display: flex;
    flex-direction: row;
  }
  div.header .switch {
    text-transform: none;
    font-weight: normal;
    font-size: 14px;
    display: flex;
    flex-grow: 1;
    justify-content: flex-end;
  }
  div.header ha-switch {
    display: flex;
    align-self: center;
    margin: 0px 8px;
    line-height: 24px;
  }
  mwc-button {
    margin: 2px 0px;
  }
  mwc-button.active {
    background: var(--primary-color);
    --mdc-theme-primary: var(--text-primary-color);
    border-radius: 4px;
  }
  mwc-button ha-icon {
    margin-right: 11px;
  }
  mwc-button.warning {
    --mdc-theme-primary: var(--error-color);
  }
  div.checkbox-container {
    display: grid;
    grid-template-columns: max-content 1fr max-content;
    grid-template-rows: min-content;
    grid-template-areas: 'checkbox slider value';
    grid-gap: 0px 10px;
  }
  div.checkbox-container div.checkbox {
    grid-area: checkbox;
    display: flex;
    align-items: center;
  }
  div.checkbox-container div.slider {
    grid-area: slider;
    display: flex;
    align-items: center;
  }
  div.checkbox-container div.value {
    grid-area: value;
    min-width: 40px;
    display: flex;
    align-items: center;
  }
  a {
    color: var(--primary-color);
  }
  a:visited {
    color: var(--accent-color);
  }
`,Wt=(t,e)=>t.callWS({type:"wiser/schedules/types",hub:e}),qt=(t,e,i="")=>t.callWS({type:"wiser/schedules",hub:e,schedule_type:i}),Yt=(t,e,i,s)=>t.callWS({type:"wiser/schedule/id",hub:e,schedule_type:i,schedule_id:s});const Xt="a-f\\d",Gt=`#?[${Xt}]{3}[${Xt}]?`,Kt=`#?[${Xt}]{6}([${Xt}]{2})?`,Jt=new RegExp(`[^#${Xt}]`,"gi"),Zt=new RegExp(`^${Gt}$|^${Kt}$`,"i");const Qt=Math.trunc;function te(t){return null!=t}function ee(t){if(function(t){return 6===(t=String(t).replace("#","")).length&&!isNaN(Number("0x"+t))}(t)){const e=function(t,e={}){if("string"!=typeof t||Jt.test(t)||!Zt.test(t))throw new TypeError("Expected a valid hex string");let i=1;8===(t=t.replace(/^#/,"")).length&&(i=Number.parseInt(t.slice(6,8),16)/255,t=t.slice(0,6)),4===t.length&&(i=Number.parseInt(t.slice(3,4).repeat(2),16)/255,t=t.slice(0,3)),3===t.length&&(t=t[0]+t[0]+t[1]+t[1]+t[2]+t[2]);const s=Number.parseInt(t,16),n=s>>16,r=s>>8&255,o=255&s,a="number"==typeof e.alpha?e.alpha:i;if("array"===e.format)return[n,r,o,a];if("css"===e.format)return`rgb(${n} ${r} ${o}${1===a?"":` / ${Number((100*a).toFixed(2))}%`})`;return{red:n,green:r,blue:o,alpha:a}}(t);return String(e.red+","+e.green+","+e.blue+","+e.alpha)}return"100,100,100"}function ie(t,e){return getComputedStyle(t).getPropertyValue(e).trim()}function se(t,e,i){if("Unknown"==i)return"100,100,100";if("onoff"===e.toLowerCase())return ee(ie(t,"On"==i?"--green-color":"--red-color"));if(["lighting","shutters"].includes(e.toLowerCase()))return(0==(s=parseInt(i))?"50,50,50":Qt(50+1.85*s)+","+Qt(50+1.5*s)+",0")+",1";{if(-20==parseFloat(i))return"138, 138, 138";const t=45,e=-10,s=(parseFloat(i)-e)/(t-e);return 235+","+Math.floor(255*(1-s))+","+0+",1"}var s}function ne(t,e){return!e.display_only&&!!(e.admin_only&&t.user.is_admin||!e.admin_only)}function re(t,e){return 0==t.slots.length||t.slots.length-1==e?"23:59":t.slots[e+1].Time}function oe(t,e,i){return-1==e?function(t,e){const i=[...Pt.slice(Pt.indexOf(t.day)),...Pt.slice(0,Pt.indexOf(t.day))].reverse();let s;for(s of i){const t=e.ScheduleData.filter(t=>t.day==s)[0];if(t&&t.slots.length>0)return t.slots[t.slots.length-1].Setpoint}return"Unknown"}(t,i):t.slots[e].Setpoint}function ae(t){const[e,i]=t.split(":");return 3600*+e+60*+i}const le=t=>t.locale||{language:t.selectedLanguage,number_format:_t.system,time_format:bt.system},de=t=>{class e extends t{connectedCallback(){super.connectedCallback(),this.__checkSubscribed()}disconnectedCallback(){if(super.disconnectedCallback(),this.__unsubs){for(;this.__unsubs.length;){const t=this.__unsubs.pop();t instanceof Promise?t.then(t=>t()):te(t)&&t()}this.__unsubs=void 0}}updated(t){super.updated(t),t.has("hass")&&this.__checkSubscribed()}hassSubscribe(){return[]}__checkSubscribed(){void 0===this.__unsubs&&this.isConnected&&void 0!==this.hass&&(this.__unsubs=this.hassSubscribe())}}return n([gt({attribute:!1})],e.prototype,"hass",void 0),e};let ce=class extends(de(ht)){constructor(){super(...arguments),this.component_loaded=!1,this.connectionError=!1}async initialise(){return await this.isComponentLoaded()&&(this.component_loaded=!0,await this.loadData()),!0}async isComponentLoaded(){for(;!this.hass||!this.hass.config.components.includes("wiser");)await new Promise(t=>setTimeout(t,100));return!0}hassSubscribe(){return this.initialise(),[this.hass.connection.subscribeMessage(t=>this.handleUpdate(t),{type:"wiser_updated"})]}async handleUpdate(t){this.config.hub&&t.hub!=this.config.hub||"wiser_updated"!=t.event||await this.loadData()}async loadData(){this.error=void 0,await Wt(this.hass,this.config.hub).then(t=>{this.supported_schedule_types=t}).catch(t=>{this.error=t}),this.supported_schedule_types&&await qt(this.hass,this.config.hub).then(t=>{this.schedule_list=t}).catch(t=>{this.error=t})}shouldUpdate(t){return!!t.has("schedule_list")||!!xt(this,t,!1)&&(this.loadData(),!0)}render(){return this.hass&&this.config?this.schedule_list&&this.schedule_list.length>0?X`
        <div>
          <div class="info-text">${Vt("wiser.helpers.select_a_schedule")}</div>
          ${this.supported_schedule_types.map(t=>this.renderScheduleItemsByType(t))}
        </div>
        ${this.renderAddScheduleButton()}
      `:X` ${this._showWarning(Vt("wiser.common.no_schedules"))} `:X``}_showWarning(t){return X` <hui-warning>${t}</hui-warning> `}renderScheduleItemsByType(t){var e,i;const s=this.schedule_list.filter(e=>e.Type===t);return s.length>0?X`
        <div class="sub-heading">
          <fieldset>
            <legend>${t}</legend>
            <div class="wrapper">
              ${"list"==(null===(e=this.config)||void 0===e?void 0:e.view_type)?this.renderScheduleList(s):(null===(i=this.config)||void 0===i?void 0:i.show_schedule_id)?s.sort((t,e)=>t.Id-e.Id).map(t=>this.renderScheduleItem(t)):s.map(t=>this.renderScheduleItem(t))}
            </div>
          </fieldset>
        </div>
      `:X``}renderScheduleList(t){return t.length>0?X`
        <table class="schedule-table">
          <thead>
            <tr class="table-header">
              <td class="schedule-id" style="text-align: center;">ID</td>
              <td class="schedule-name">${Vt("wiser.labels.name")}</td>
              <td class="schedule-assigns">${Vt("wiser.labels.assigns")}</td>
              <td class="schedule-action">&nbsp;</td>
            </tr>
          </thead>
          <tbody class="table-body">
            ${t.sort((t,e)=>t.Id-e.Id).map(t=>this.renderScheduleListItem(t))}
          </tbody>
        </table>
      `:X``}renderScheduleItem(t){var e,i;const s=At[t.Type];return X`
      <ha-button
        appearance="accent"
        class="schedule-item"
        id=${"schedule"+t.Id}
        @click=${()=>this._scheduleClick(t.Type,t.Id)}
      >
        <ha-icon slot="start" .icon="${function(t){if(t)return"string"!=typeof t&&(t=String(t)),t.match(/^[a-z]+:[a-z0-9-]+$/i)?t:`hass:${t}`}(s)}"></ha-icon>
        ${(null===(e=this.config)||void 0===e?void 0:e.show_schedule_id)?t.Id+" - ":null}${t.Name}
        ${(null===(i=this.config)||void 0===i?void 0:i.show_badges)?X`<span class="badge">${t.Assignments}</span>`:null}
      </ha-button>
    `}renderScheduleListItem(t){return X`
      <tr class="table-body-item">
        <td class="schedule-id">${t.Id}</td>
        <td class="schedule-name">${t.Name}</td>
        <td class="schedule-assigns">${t.Assignments}</td>
        <td class="schedule-action">
          <ha-button
            appearance="plain"
            size="small"
            id=${"schedule"+t.Id}
            @click=${()=>this._scheduleClick(t.Type,t.Id)}
          >
            ${Vt("wiser.actions.view")}
          </ha-button>
        </td>
      </tr>
    `}renderAddScheduleButton(){if(ne(this.hass,this.config))return X`
        <div class="card-actions">
          <ha-button appearance="plain" @click=${this._addScheduleClick}
            >${Vt("wiser.actions.add_schedule")}
          </ha-button>
        </div>
      `}async _addScheduleClick(){const t=new CustomEvent("addScheduleClick");this.dispatchEvent(t)}_scheduleClick(t,e){const i=new CustomEvent("scheduleClick",{detail:{schedule_type:t,schedule_id:e}});this.dispatchEvent(i)}};ce.styles=h`
    ${jt}
    div.info-text {
      margin-bottom: 10px;
    }
    span.button-label {
      padding-left: 5px;
      text-transform: uppercase;
      font-weight: 500;
    }
    div.wrapper {
      white-space: nowrap;
      transition:
        width 0.2s cubic-bezier(0.17, 0.67, 0.83, 0.67),
        margin 0.2s cubic-bezier(0.17, 0.67, 0.83, 0.67);
      overflow: auto;
      display: flex;
      flex-wrap: wrap;
      flex-direction: row;
      justify-content: flex-start;
    }
    div.sub-heading {
      display: block;
      margin: 5px 0;
    }
    div.sub-heading fieldset {
      border: 1px solid var(--divider-color, #e8e8e8);
      border-radius: 5px;
      font-size: small;
    }
    .schedule-id {
      width: 30px;
      text-align: right;
    }
    .schedule-name {
      padding-left: 5px;
      overflow: hidden;
      white-space: nowrap;
      text-overflow: ellipsis;
    }
    .schedule-assigns {
      width: 15%;
      text-align: center;
      padding-left: 5px;
    }
    .schedule-action {
      width: 75px;
      text-align: center;
      padding-left: 5px;
    }
    div.table-header {
      display: flex;
      font-weight: 500;
    }
    div.table-body-item {
      display: flex;
      align-items: center;
    }
    .schedule-table {
      width: 100%;
      font-size: 14px;
      table-layout: fixed;
    }
    .view-button {
      line-height: 32px;
      cursor: pointer;
      white-space: nowrap;
      text-overflow: ellipsis;
      margin: 3px 10px 3px 5px;
      display: flex;
      padding: 0px 15px 0px 10px;
      color: var(--mdc-theme-primary, #6200ee);
      background: var(--primary-color);
      --mdc-theme-primary: var(--text-primary-color);
      border-radius: 4px;
      font-size: var(--material-button-font-size);
      position: relative;
    }
    .schedule-item {
      white-space: nowrap;
      text-overflow: ellipsis;
      padding: 5px 5px;
    }
    .badge {
      font-size: 13px;
      font-weight: 400;
      position: absolute;
      min-width: 20px;
      box-sizing: border-box;
      top: 0px;
      right: 0px;
      background-color: var(--accent-color);
      border-radius: 50%;
      line-height: 20px;
      text-align: center;
      padding: 0px 6px;
      color: var(--text-accent-color, var(--text-primary-color));
    }
  `,n([gt({attribute:!1})],ce.prototype,"config",void 0),n([gt({attribute:!1})],ce.prototype,"schedule_list",void 0),n([gt({attribute:!1})],ce.prototype,"component_loaded",void 0),ce=n([ut("wiser-schedule-list-card")],ce);let he=class extends ht{async showDialog(t){this._params=t,await this.updateComplete}async closeDialog(){this._params&&this._params.cancel(),this._params=void 0}render(){return this._params?X`
      <ha-dialog
        open
        .heading=${Vt("wiser.headings.delete_schedule")}
        @closed=${this.closeDialog}
        @close-dialog=${this.closeDialog}
      >
        <div class="wrapper">${Vt("wiser.helpers.delete_schedule_confirm")+" "+this._params.name+"?"}</div>
        <ha-button
          variant="danger"
          slot="primaryAction"
          style="float: left"
          @click=${this.confirmClick}
          dialogAction="close"
        >
          ${this.hass.localize("ui.common.delete")}
        </ha-button>
        <ha-button slot="secondaryAction" @click=${this.cancelClick} dialogAction="close">
          ${this.hass.localize("ui.common.cancel")}
        </ha-button>
      </ha-dialog>
    `:X``}confirmClick(){this._params.confirm()}cancelClick(){this._params.cancel()}static get styles(){return h`
      div.wrapper {
        color: var(--primary-text-color);
      }
    `}};n([gt({attribute:!1})],he.prototype,"hass",void 0),n([vt()],he.prototype,"_params",void 0),he=n([ut("wiser-dialog-delete-confirm")],he);var pe=Object.freeze({__proto__:null,get DialogDeleteConfirm(){return he}});function ue(t){if(t.match(/^([0-9:]+)$/)){const e=t.split(":").map(Number);return 3600*e[0]+60*e[1]+(e[2]||0)}const e=new Date(t);return 3600*e.getHours()+60*e.getMinutes()+e.getSeconds()}function me(t){const e=Math.floor(t/3600);t-=3600*e;const i=Math.floor(t/60);t-=60*i;const s=Math.round(t);return String(e%24).padStart(2,"0")+":"+String(i).padStart(2,"0")+":"+String(s).padStart(2,"0")}function fe(t){const e=Math.floor(t/3600);t-=3600*e;const i=Math.floor(t/60);return String(e%24).padStart(2,"0")+":"+String(i).padStart(2,"0")}function ge(t,e,i={wrapAround:!0}){let s=t>=0?Math.floor(t/3600):Math.ceil(t/3600),n=Math.floor((t-3600*s)/60);n%e!=0&&(n=Math.round(n/e)*e),n>=60?(s++,n-=60):n<0&&(s--,n+=60),i.wrapAround&&(s>=24?s-=24:s<0&&(s+=24));const r=3600*s+60*n;if(i.maxHours){if(r>3600*i.maxHours)return 3600*i.maxHours;if(r<3600*-i.maxHours)return 3600*-i.maxHours}return r}var ve=/d{1,4}|M{1,4}|YY(?:YY)?|S{1,3}|Do|ZZ|Z|([HhMsDm])\1?|[aA]|"[^"]*"|'[^']*'/g,_e=/\[([^]*?)\]/gm;function be(t,e){for(var i=[],s=0,n=t.length;s<n;s++)i.push(t[s].substr(0,e));return i}function ye(t){for(var e=[],i=1;i<arguments.length;i++)e[i-1]=arguments[i];for(var s=0,n=e;s<n.length;s++){var r=n[s];for(var o in r)t[o]=r[o]}return t}var xe=["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"],$e=["January","February","March","April","May","June","July","August","September","October","November","December"],we=be($e,3),Ae=ye({},{dayNamesShort:be(xe,3),dayNames:xe,monthNamesShort:we,monthNames:$e,amPm:["am","pm"],DoFn:function(t){return t+["th","st","nd","rd"][t%10>3?0:(t-t%10!=10?1:0)*t%10]}}),Ee=function(t,e){for(void 0===e&&(e=2),t=String(t);t.length<e;)t="0"+t;return t},Se={D:function(t){return String(t.getDate())},DD:function(t){return Ee(t.getDate())},Do:function(t,e){return e.DoFn(t.getDate())},d:function(t){return String(t.getDay())},dd:function(t){return Ee(t.getDay())},ddd:function(t,e){return e.dayNamesShort[t.getDay()]},dddd:function(t,e){return e.dayNames[t.getDay()]},M:function(t){return String(t.getMonth()+1)},MM:function(t){return Ee(t.getMonth()+1)},MMM:function(t,e){return e.monthNamesShort[t.getMonth()]},MMMM:function(t,e){return e.monthNames[t.getMonth()]},YY:function(t){return Ee(String(t.getFullYear()),4).substr(2)},YYYY:function(t){return Ee(t.getFullYear(),4)},h:function(t){return String(t.getHours()%12||12)},hh:function(t){return Ee(t.getHours()%12||12)},H:function(t){return String(t.getHours())},HH:function(t){return Ee(t.getHours())},m:function(t){return String(t.getMinutes())},mm:function(t){return Ee(t.getMinutes())},s:function(t){return String(t.getSeconds())},ss:function(t){return Ee(t.getSeconds())},S:function(t){return String(Math.round(t.getMilliseconds()/100))},SS:function(t){return Ee(Math.round(t.getMilliseconds()/10),2)},SSS:function(t){return Ee(t.getMilliseconds(),3)},a:function(t,e){return t.getHours()<12?e.amPm[0]:e.amPm[1]},A:function(t,e){return t.getHours()<12?e.amPm[0].toUpperCase():e.amPm[1].toUpperCase()},ZZ:function(t){var e=t.getTimezoneOffset();return(e>0?"-":"+")+Ee(100*Math.floor(Math.abs(e)/60)+Math.abs(e)%60,4)},Z:function(t){var e=t.getTimezoneOffset();return(e>0?"-":"+")+Ee(Math.floor(Math.abs(e)/60),2)+":"+Ee(Math.abs(e)%60,2)}},Ce={default:"ddd MMM DD YYYY HH:mm:ss",shortDate:"M/D/YY",mediumDate:"MMM D, YYYY",longDate:"MMMM D, YYYY",fullDate:"dddd, MMMM D, YYYY",isoDate:"YYYY-MM-DD",isoDateTime:"YYYY-MM-DDTHH:mm:ssZ",shortTime:"HH:mm",mediumTime:"HH:mm:ss",longTime:"HH:mm:ss.SSS"},Te=function(t,e,i){if(void 0===e&&(e=Ce.default),void 0===i&&(i={}),"number"==typeof t&&(t=new Date(t)),"[object Date]"!==Object.prototype.toString.call(t)||isNaN(t.getTime()))throw new Error("Invalid Date pass to format");var s=[];e=(e=Ce[e]||e).replace(_e,function(t,e){return s.push(e),"@@@"});var n=ye(ye({},Ae),i);return(e=e.replace(ve,function(e){return Se[e](t,n)})).replace(/@@@/g,function(){return s.shift()})};const Ie=t=>{if(t.time_format===bt.language||t.time_format===bt.system){const e=t.time_format===bt.language?t.language:void 0,i=(new Date).toLocaleString(e);return i.includes("AM")||i.includes("PM")}return t.time_format===bt.am_pm};function Oe(t,e,i){return i===bt.am_pm||!i&&e.time_format===bt.am_pm?Te(t,"h:mm A"):i===bt.twenty_four||!i&&e.time_format===bt.twenty_four?Te(t,"shortTime"):(()=>{try{(new Date).toLocaleTimeString("i")}catch(t){return"RangeError"===t.name}return!1})()?t.toLocaleTimeString(e.language,{hour:"numeric",minute:"2-digit",hour12:Ie(e)}):Ie(e)?Oe(t,e,bt.am_pm):Oe(t,e,bt.twenty_four)}function ke(t){const e=new Date,i=(t||"").match(/^([0-9]{4})-([0-9]{2})-([0-9]{2})/);null!==i&&e.setFullYear(Number(i[1]),Number(i[2])-1,Number(i[3]));const s=(t||"").match(/([0-9]{2}):([0-9]{2})(:([0-9]{2}))?$/);return null!==s&&e.setHours(Number(s[1]),Number(s[2]),s.length>4?Number(s[4]):e.getSeconds()),e}let Re=class extends ht{constructor(){super(...arguments),this.min=0,this.max=255,this.step=1,this.scaleFactor=1,this.unit="",this.optional=!1,this.disabled=!1,this._displayedValue=0}set value(t){t=isNaN(t)?this.min:this._roundedValue(t/this.scaleFactor),this._displayedValue=t}render(){return X`
      <div class="checkbox-container">
        <div class="checkbox">${this.getCheckbox()}</div>
        <div class="slider">${this.getSlider()}</div>
        <div class="value${this.disabled?" disabled":""}">${this._displayedValue}${this.unit}</div>
      </div>
    `}getSlider(){return this.disabled?X`
        <ha-slider
          pin
          min=${this.min}
          max=${this.max}
          step=${this.step}
          value=${this._displayedValue}
          disabled
        ></ha-slider>
      `:X`
        <ha-slider
          pin
          min=${this.min}
          max=${this.max}
          step=${this.step}
          value=${this._displayedValue}
          @change=${this._updateValue}
        ></ha-slider>
      `}getCheckbox(){return this.optional?X` <ha-checkbox @change=${this._toggleChecked} ?checked=${!this.disabled}></ha-checkbox> `:X``}_toggleChecked(t){const e=t.target.checked;this.disabled=!e;const i=this.disabled?null:this._scaledValue(this._displayedValue);yt(this,"value-changed",{value:i})}_updateValue(t){let e=Number(t.target.value);this._displayedValue=e,e=this._scaledValue(this._displayedValue),yt(this,"value-changed",{value:e})}_roundedValue(t){return t=Math.round(t/this.step)*this.step,(t=parseFloat(t.toPrecision(12)))>this.max?t=this.max:t<this.min&&(t=this.min),t}_scaledValue(t){return t=this._roundedValue(t),t*=this.scaleFactor,t=parseFloat(t.toFixed(2))}};Re.styles=h`
    ${jt} :host {
      width: 100%;
    }
    ha-slider {
      width: 100%;
    }
  `,n([gt({type:Number})],Re.prototype,"min",void 0),n([gt({type:Number})],Re.prototype,"max",void 0),n([gt({type:Number})],Re.prototype,"step",void 0),n([gt({type:Number})],Re.prototype,"value",null),n([gt({type:Number})],Re.prototype,"scaleFactor",void 0),n([gt({type:String})],Re.prototype,"unit",void 0),n([gt({type:Boolean})],Re.prototype,"optional",void 0),n([gt({type:Boolean})],Re.prototype,"disabled",void 0),n([gt({type:Number})],Re.prototype,"_displayedValue",void 0),Re=n([ut("wiser-variable-slider")],Re);let Pe=class extends ht{render(){return X` <div id="time-bar" class="time-wrapper">${this.renderTimes()}</div> `}renderTimes(){if(this.hass){const t=parseFloat(getComputedStyle(this).getPropertyValue("width"))||460,e=[1,2,3,4,6,8,12],i=Ie(le(this.hass))?55:40;let s=Math.ceil(24/(t/i));for(;!e.includes(s);)s++;const n=[0,...Array.from(Array(24/s-1).keys()).map(t=>(t+1)*s),24];return n.map(t=>{const e=0==t||24==t,i=e?s/48*100:s/24*100;return X`
          <div style="width: ${Math.floor(100*i)/100}%" class="${e?"":"time"}">
            ${e?"":Oe(ke(me(3600*t)),le(this.hass))}
          </div>
        `})}return X``}static get styles(){return h`
      :host {
        display: block;
        max-width: 100%;
        overflow: hidden;
      }
      div.outer {
        width: 100%;
        overflow-x: hidden;
        overflow-y: hidden;
        border-radius: 5px;
      }
      div.time-wrapper {
        white-space: nowrap;
        transition:
          width 0.2s cubic-bezier(0.17, 0.67, 0.83, 0.67),
          margin 0.2s cubic-bezier(0.17, 0.67, 0.83, 0.67);
        overflow: auto;
      }
      div.time-wrapper div {
        float: left;
        display: flex;
        position: relative;
        height: 25px;
        line-height: 25px;
        font-size: 12px;
        text-align: center;
        align-content: center;
        align-items: center;
        justify-content: center;
      }
      div.time-wrapper div.time:before {
        content: ' ';
        background: var(--disabled-text-color);
        position: absolute;
        left: 0px;
        top: 0px;
        width: 1px;
        height: 5px;
        margin-left: 50%;
        margin-top: 0px;
      }
      @keyframes fadeIn {
        99% {
          visibility: hidden;
        }
        100% {
          visibility: visible;
        }
      }
    `}};n([gt({attribute:!1})],Pe.prototype,"hass",void 0),Pe=n([ut("wiser-time-bar")],Pe);let Le=class extends ht{constructor(){super(),this.editMode=!1,this._activeSlot=-99,this._activeDay="",this._show_short_days=!1,this.schedule_type=Tt[0],this.activeMarker=0,this.isDragging=!1,this.currentTime=0,this.timer=0,this.timeout=0,this.zoomFactor=1,this.rangeMin=0,this.rangeMax=wt,this.stepSize=5,this.initialise()}async initialise(){return this.schedule&&(this.schedule_type=this.schedule.Type),!0}shouldUpdate(){return this.editMode||(this._activeSlot=-99,this._activeDay=""),!0}render(){const t=parseFloat(getComputedStyle(this).getPropertyValue("width"));return this._show_short_days=t<500,this.hass&&this.config&&this.suntimes&&this.schedule?X`
            <div class = "slots-wrapper">
                ${Pt.map(t=>this.renderDay(this.schedule.ScheduleData.filter(e=>e.day==t)[0]?this.schedule.ScheduleData.filter(e=>e.day==t)[0]:{day:t,slots:[]}))}
                <div class="wrapper" style="display:flex; height:28px;">
                    <div class="day  ${this._show_short_days?"short":""}">&nbsp;</div>
                        <wiser-time-bar style="width:100%"
                            .hass=${this.hass}
                            ></wiser-time-bar>
                    </div>
                </div>
            </div>
            ${this.editMode&&It.includes(this.schedule_type)?this.renderSpecialTimeButtons():null}
            ${this.editMode?this.renderAddDeleteButtons():null}
            ${this.editMode?this.renderSetPointControl():null}
            ${this.editMode?this.renderCopyDay():null}
        `:X``}renderDay(t){return X`
      <div class="wrapper">
        ${this.computeDayLabel(t.day)}
        <div class="outer" id="${t.day}">
          <div class="wrapper selectable">
            ${t.slots.length>0?t.slots.map((e,i)=>this.renderSlot(e,i,t)):this.renderEmptySlot({Time:"23:59",Setpoint:"0",SpecialTime:""},-1,t,!0)}
          </div>
        </div>
      </div>
    `}renderEmptySlot(t,e,i,s=!1){const n="00:00",r=t.Time,o=oe(i,e,this.schedule),a=parseFloat(getComputedStyle(this).getPropertyValue("width")),l=this.config.theme_colors?"rgba(var(--rgb-primary-color), 0.7)":"rgba("+se(this,this.schedule_type,o)+")",d=(ae(r)-ae(n))/wt*100,c=Vt("wiser.labels.start")+" - "+n+"\n"+Vt("wiser.labels.end")+" - "+r+"\n"+Vt("wiser.labels.setting")+" - "+this.computeSetpointLabel(o),h=d/100*a<35?"setpoint rotate":"setpoint";return X`
      <div
        id=${i.day+"|-1"}
        class="slot previous ${this.editMode&&s?"selectable":null} ${this._activeSlot==e&&this._activeDay==i.day?"selected":null} ${this.config.theme_colors?"theme-colors":null}"
        style="width:${Math.floor(1e3*d)/1e3}%; background:${l};"
        title="${c}"
        @click=${s?this._slotClick:null}
        slot="${-1}"
      >
        <div class="slotoverlay previous">
          <span class="${h}">${this.computeSetpointLabel(o)}</span>
        </div>
      </div>
    `}renderSlot(t,e,i){const s=t.Time,n=re(i,e),r=t.Setpoint,o=(ae(n)-ae(s))/wt*100,a=this.config.theme_colors?"rgba(var(--rgb-primary-color), 0.7)":"rgba("+se(this,this.schedule_type,r)+")",l=o/100*parseFloat(getComputedStyle(this).getPropertyValue("width"))<35?"setpoint rotate":"setpoint",d=Vt("wiser.labels.start")+" - "+(t.SpecialTime?t.SpecialTime+" ("+s+")":s)+"\n"+Vt("wiser.labels.end")+" - "+n+"\n"+Vt("wiser.labels.setting")+" - "+this.computeSetpointLabel(r);return X`
      ${0==e&&"00:00"!=s&&"0:00"!=s?this.renderEmptySlot(t,-1,i,!1):""}
      <div
        id=${i.day+"|"+e}
        class="slot ${this.editMode?"selectable":null} ${this._activeSlot==e&&this._activeDay==i.day?"selected":null}"
        style="width:${Math.floor(1e3*o)/1e3}%; background:${a};"
        title="${d}"
        @click=${this._slotClick}
        slot="${e}"
      >
        <div class="slotoverlay ${this.editMode?"selectable":null}">
          <span class="${l}">${this.computeSetpointLabel(r)}</span>
        </div>
        ${this._activeSlot==e&&this._activeDay==i.day?X`
              <div class="handle">
                <div class="button-holder">
                  <ha-icon-button
                    .path=${"M18.17,12L15,8.83L16.41,7.41L21,12L16.41,16.58L15,15.17L18.17,12M5.83,12L9,15.17L7.59,16.59L3,12L7.59,7.42L9,8.83L5.83,12Z"}
                    @mousedown=${this._handleTouchStart}
                    @touchstart=${this._handleTouchStart}
                  >
                  </ha-icon-button>
                </div>
              </div>
            `:""}
        ${this._activeSlot==e&&this._activeDay==i.day?this.renderTooltip(i,e):""}
      </div>
    `}renderSpecialTimeButtons(){const t=this._activeDay?this.schedule.ScheduleData.filter(t=>t.day==this._activeDay)[0].slots[this._activeSlot]:null;return X`
      <div class="wrapper special-times" style="white-space: normal;">
        <div class="day  ${this._show_short_days?"short":""}">&nbsp;</div>
        <div class="sub-section">
          <div class="sub-heading">Set Special Time</div>
          <ha-button id=${"sunrise"} @click=${this._setSpecialTime} ?disabled=${!t}>
            <ha-icon id=${"sunrise"} icon="hass:weather-sunny" class="padded-right"></ha-icon>
            Sunrise
          </ha-button>
          <ha-button id=${"sunset"} @click=${this._setSpecialTime} ?disabled=${!t}>
            <ha-icon id=${"sunset"} icon="hass:weather-night" class="padded-right"></ha-icon>
            Sunset
          </ha-button>
        </div>
      </div>
    `}renderAddDeleteButtons(){let t=0;return this.schedule.ScheduleData.filter(t=>t.day==this._activeDay).length>0&&(t=this._activeDay?this.schedule.ScheduleData.filter(t=>t.day==this._activeDay)[0].slots.length:0),X`
      <div class="wrapper" style="white-space: normal;">
        <div class="day  ${this._show_short_days?"short":""}">&nbsp;</div>
        <div class="sub-section">
          <ha-button
            size="small"
            style="padding: 0 2px"
            @click=${this._addSlot}
            .disabled=${this._activeSlot<-1||t>=24}
          >
            <ha-icon slot="start" icon="hass:plus-circle-outline" class="padded-right"></ha-icon>
            ${Vt("wiser.actions.add")}
          </ha-button>
          <ha-button
            size="small"
            style="padding: 0 2px"
            @click=${this._removeSlot}
            .disabled=${this._activeSlot<0||t<1}
          >
            <ha-icon slot="start" icon="hass:minus-circle-outline" class="padded-right"></ha-icon>
            ${this.hass.localize("ui.common.delete")}
          </ha-button>
        </div>
      </div>
    `}renderSetPointControl(){let t={};return this.editMode?(this.schedule.ScheduleData.filter(t=>t.day==this._activeDay).length>0&&(t=this._activeDay?this.schedule.ScheduleData.filter(t=>t.day==this._activeDay)[0].slots:{}),"Heating"==this.schedule_type?X`
          <div class="wrapper" style="white-space: normal; padding-top: 10px;">
            <div class="day  ${this._show_short_days?"short":""}">&nbsp;</div>
            <div class="sub-section">
              <div class="section-header">${this._show_short_days?"Temp":"Temperature"}</div>
              <br />
              <div style="display: flex; line-height: 32px; width: 100%; max-width: 400px;">
                <ha-icon-button
                  class="set-off-button"
                  .path=${"M3.28,2L2,3.27L4.77,6.04L5.64,7.39L4.22,9.6L5.95,10.5L7.23,8.5L10.73,12H4A2,2 0 0,0 2,14V22H4V20H18.73L20,21.27V22H22V20.73L22,20.72V20.72L3.28,2M7,17A1,1 0 0,1 6,18A1,1 0 0,1 5,17V15A1,1 0 0,1 6,14A1,1 0 0,1 7,15V17M11,17A1,1 0 0,1 10,18A1,1 0 0,1 9,17V15A1,1 0 0,1 10,14A1,1 0 0,1 11,15V17M15,17A1,1 0 0,1 14,18A1,1 0 0,1 13,17V15C13,14.79 13.08,14.61 13.18,14.45L15,16.27V17M16.25,9.5L17.67,7.3L16.25,5.1L18.25,2L20,2.89L18.56,5.1L20,7.3V7.31L18,10.4L16.25,9.5M22,14V18.18L19,15.18V15A1,1 0 0,0 18,14C17.95,14 17.9,14 17.85,14.03L15.82,12H20C21.11,12 22,12.9 22,14M11.64,7.3L10.22,5.1L12.22,2L13.95,2.89L12.53,5.1L13.95,7.3L13.94,7.31L12.84,9L11.44,7.62L11.64,7.3M7.5,3.69L6.1,2.28L6.22,2.09L7.95,3L7.5,3.69Z"}
                  .disabled=${this._activeSlot<0}
                  @click=${()=>this._updateSetPoint("-20")}
                >
                </ha-icon-button>
                <wiser-variable-slider
                  min="5"
                  max="30"
                  step="0.5"
                  value=${this._activeSlot>=0?parseFloat(t[this._activeSlot].Setpoint):0}
                  unit="°C"
                  .optional=${!1}
                  .disabled=${this._activeSlot<0}
                  @value-changed=${t=>{this._updateSetPoint(Number(t.detail.value))}}
                >
                </wiser-variable-slider>
              </div>
            </div>
          </div>
        `:"OnOff"==this.schedule_type?X`
          <div class="wrapper" style="height: 36px;">
            <div class="day  ${this._show_short_days?"short":""}">&nbsp;</div>
            <div class="sub-section">
              <div style="display: flex; justify-content: center;">
                <div class="section-header" style="padding-right: 30%">State</div>
                <div style="display: flex; line-height: 32px;">
                  <span>Off</span>
                  <ha-switch
                    style="margin: 8px 10px;"
                    ?checked=${this._activeSlot>=0&&"On"==t[this._activeSlot].Setpoint}
                    .disabled=${this._activeSlot<0}
                    @change=${()=>"On"==t[this._activeSlot].Setpoint?this._updateSetPoint("Off"):this._updateSetPoint("On")}
                  >
                  </ha-switch>
                  <span>On</span>
                </div>
              </div>
            </div>
          </div>
        `:["Lighting","Shutters"].includes(this.schedule_type)?X`
          <div class="wrapper" style="white-space: normal;">
            <div class="day  ${this._show_short_days?"short":""}">&nbsp;</div>
            <div class="sub-section">
              <div class="section-header">Level</div>
              <div style="display: flex; line-height: 32px; width: 100%; max-width: 400px;">
                <wiser-variable-slider
                  min="0"
                  max="100"
                  step="1"
                  value=${this._activeSlot>=0?parseFloat(t[this._activeSlot].Setpoint):0}
                  unit="%"
                  .optional=${!1}
                  .disabled=${this._activeSlot<0}
                  @value-changed=${t=>{this._updateSetPoint(Number(t.detail.value))}}
                >
                </wiser-variable-slider>
              </div>
            </div>
          </div>
        `:X``):X``}renderCopyDay(){return X`
      <div class="wrapper" style="white-space: normal; padding-top: 10px;">
        <div class="day  ${this._show_short_days?"short":""}">&nbsp;</div>
        <div>
          <div class="section-header">
            ${this._activeDay?Vt("wiser.actions.copy")+" "+Vt("wiser.days."+this._activeDay.toLowerCase())+" "+Vt("wiser.labels.to"):Vt("wiser.actions.copy")+" "+Vt("wiser.labels.to")}
          </div>
          <div>
            ${Pt.concat(Ot).concat("All").map(t=>this.renderCopyToButton(t))}
          </div>
        </div>
      </div>
    `}renderCopyToButton(t){return X`
      <ha-button
        id=${t}
        appearance="plain"
        size="small"
        @click=${this._copyDay}
        ?disabled=${this._activeDay==t||!this._activeDay}
      >
        ${Pt.includes(t)&&this._show_short_days?Vt("wiser.days.short."+t.toLowerCase()):Vt("wiser.days."+t.toLowerCase())}
      </ha-button>
    `}renderTooltip(t,e){const i=t.slots,s=Lt.includes(i[e].SpecialTime);return X`
      <div class="tooltip-container center">
        <div class="tooltip ${this._activeSlot===e?"active":""}">
          ${s?X`
                <ha-icon
                  icon="hass:${i[e].SpecialTime==Lt[0]?"weather-sunny":"weather-night"}"
                ></ha-icon>
                ${i[e].SpecialTime}
              `:Oe(ke(me(ue(i[e].Time))),le(this.hass))}
        </div>
      </div>
    `}_slotClick(t){const e=t.target.parentElement.parentElement;if(e.id){const t=e.id.split("|")[0],i=e.id.split("|")[1];i!=this._activeSlot||t!=this._activeDay?(this._activeSlot=parseInt(i),this._activeDay=t):(this._activeSlot=-99,this._activeDay="");const s=new CustomEvent("slotClicked",{detail:{day:this._activeDay,slot:this._activeSlot}});this.dispatchEvent(s)}}_copyDay(t){const e=t.target,i=JSON.stringify(this.schedule.ScheduleData[Pt.indexOf(this._activeDay)].slots);Pt.includes(e.id)?this.schedule.ScheduleData[Pt.indexOf(e.id)].slots=JSON.parse(i):e.id==Ot[0]?kt.map(t=>{this.schedule.ScheduleData[Pt.indexOf(t)].slots=JSON.parse(i)}):e.id==Ot[1]?Rt.map(t=>{this.schedule.ScheduleData[Pt.indexOf(t)].slots=JSON.parse(i)}):"All"==e.id&&Pt.map(t=>{this.schedule.ScheduleData[Pt.indexOf(t)].slots=JSON.parse(i)}),this.requestUpdate()}_updateSetPoint(t){this.schedule.ScheduleData[Pt.indexOf(this._activeDay)].slots=Object.assign(this.schedule.ScheduleData[Pt.indexOf(this._activeDay)].slots,{[this._activeSlot]:Object.assign(Object.assign({},this.schedule.ScheduleData[Pt.indexOf(this._activeDay)].slots[this._activeSlot]),{Setpoint:t})});const e=new CustomEvent("scheduleChanged",{detail:{schedule:this.schedule}});this.dispatchEvent(e),this.requestUpdate()}getSunTime(t,e){return e==Lt[0]?this.suntimes.Sunrises[Pt.indexOf(t)].time:this.suntimes.Sunsets[Pt.indexOf(t)].time}convertScheduleDay(t){const e=t.slots.map(e=>Lt.includes(e.SpecialTime)?{Time:this.getSunTime(t.day,e.SpecialTime),Setpoint:e.Setpoint,SpecialTime:e.SpecialTime}:{Time:e.Time,Setpoint:e.Setpoint,SpecialTime:e.SpecialTime}).sort((t,e)=>parseInt(t.Time.replace(":",""))<parseInt(e.Time.replace(":",""))?0:1),i=new Set(e.map(t=>JSON.stringify(t))),s=Array.from(i).map(t=>JSON.parse(t));return{day:t.day,slots:s}}_setSpecialTime(t){const e=t.target.id.replace(/\w\S*/g,t=>t.charAt(0).toUpperCase()+t.substr(1).toLowerCase());this._activeDay&&this._activeSlot>=0&&(this.schedule.ScheduleData[Pt.indexOf(this._activeDay)].slots[this._activeSlot].SpecialTime!=e&&(this.schedule.ScheduleData[Pt.indexOf(this._activeDay)].slots=Object.assign(this.schedule.ScheduleData[Pt.indexOf(this._activeDay)].slots,{[this._activeSlot]:Object.assign(Object.assign({},this.schedule.ScheduleData[Pt.indexOf(this._activeDay)].slots[this._activeSlot]),{SpecialTime:e,Time:this.getSunTime(this._activeDay,e)})})),this.schedule.ScheduleData[Pt.indexOf(this._activeDay)]=this.convertScheduleDay(this.schedule.ScheduleData[Pt.indexOf(this._activeDay)]),this.schedule.ScheduleData[Pt.indexOf(this._activeDay)].slots.forEach((t,i)=>{t.SpecialTime==e&&(this._activeSlot=i)}),this.requestUpdate())}_addSlot(){if(this._activeSlot<-1)return;const t=Pt.indexOf(this._activeDay);if(this._activeSlot<0)this.schedule.ScheduleData[t].slots=[{Time:fe(ue("06:00")),Setpoint:St[this.schedule_type],SpecialTime:""}],this._activeSlot=0;else{const e=this.schedule.ScheduleData[t].slots[this._activeSlot];let i=ue(e.Time),s=ue(re(this.schedule.ScheduleData[t],this._activeSlot));s<i&&(s+=wt);const n=ge(i+(s-i)/2,this.stepSize);e.SpecialTime?(i=ge(i-ue("01:00"),this.stepSize),this.schedule.ScheduleData[t].slots=[...this.schedule.ScheduleData[t].slots.slice(0,this._activeSlot),{Time:fe(i),Setpoint:e.Setpoint,SpecialTime:""},...this.schedule.ScheduleData[t].slots.slice(this._activeSlot)]):this.schedule.ScheduleData[t].slots=[...this.schedule.ScheduleData[t].slots.slice(0,this._activeSlot),{Time:fe(i),Setpoint:e.Setpoint,SpecialTime:""},Object.assign(Object.assign({},this.schedule.ScheduleData[t].slots[this._activeSlot]),{Time:fe(n)}),...this.schedule.ScheduleData[t].slots.slice(this._activeSlot+1)],this._activeSlot++}const e=new CustomEvent("scheduleChanged",{detail:{schedule:this.schedule}});this.dispatchEvent(e),this.requestUpdate()}_removeSlot(){if(this._activeSlot<0)return;const t=Pt.indexOf(this._activeDay),e=this._activeSlot;this.schedule.ScheduleData[t].slots=0==e?[...this.schedule.ScheduleData[t].slots.slice(e+1)]:[...this.schedule.ScheduleData[t].slots.slice(0,e),...this.schedule.ScheduleData[t].slots.slice(e+1)],this._activeSlot==this.schedule.ScheduleData[t].slots.length&&this._activeSlot--;const i=new CustomEvent("scheduleChanged",{detail:{schedule:this.schedule}});this.dispatchEvent(i),this.requestUpdate()}_handleTouchStart(t){const e=Pt.indexOf(this._activeDay);let i=this.schedule.ScheduleData.filter(t=>t.day==this._activeDay)[0].slots;const s=t.target;let n=s;for(;!n.classList.contains("outer");)n=n.parentElement;const r=parseFloat(getComputedStyle(n).getPropertyValue("width")),o=wt/(this.rangeMax-this.rangeMin)*r,a=-(-this.rangeMin/(this.rangeMax-this.rangeMin)*r)/o*wt;let l=s;for(;!l.classList.contains("slot");)l=l.parentElement;const d=l,c=Number(d.getAttribute("slot")),h=c>0?ue(i[c-1].Time)+60*this.stepSize:0,p=c<i.length-1?(ue(re(this.schedule.ScheduleData[e],c))||wt)-60*this.stepSize:wt-60*this.stepSize;this.isDragging=!0;const u=d.parentElement.parentElement.getBoundingClientRect();let m=t=>{let s;s="undefined"!=typeof TouchEvent&&t instanceof TouchEvent?t.changedTouches[0].pageX:t.pageX;let n=s-u.left;n>r-1&&(n=r-1),n<-18&&(n=-18);let l=Math.round(n/o*wt+a);l<h&&(l=h),l>p&&(l=p),this.currentTime=l,l=Math.round(l)>=wt?wt:ge(l,this.stepSize);const d=fe(l);d!=re(this.schedule.ScheduleData[e],c)&&(i=Object.assign(i,{[c]:Object.assign(Object.assign({},i[c]),{Time:d,SpecialTime:""})}),this.requestUpdate())};const f=()=>{window.removeEventListener("mousemove",m),window.removeEventListener("touchmove",m),window.removeEventListener("mouseup",f),window.removeEventListener("touchend",f),window.removeEventListener("blur",f),m=()=>{},setTimeout(()=>{this.isDragging=!1},100),s.blur();const t=new CustomEvent("scheduleChanged",{detail:{schedule:this.schedule}});this.dispatchEvent(t)};window.addEventListener("mouseup",f),window.addEventListener("touchend",f),window.addEventListener("blur",f),window.addEventListener("mousemove",m),window.addEventListener("touchmove",m)}computeDayLabel(t){return X`
      <div class="day  ${this._show_short_days?"short":""}">
        ${this._show_short_days?Vt("wiser.days.short."+t.toLowerCase()):Vt("wiser.days."+t.toLowerCase())}
      </div>
    `}computeSetpointLabel(t){return"Unknown"==t?t:"Heating"==this.schedule_type&&-20==t?"Off":t+Ct[this.schedule_type]}static get styles(){return h`
      :host {
        display: block;
        max-width: 100%;
      }
      div.outer {
        width: 100%;
        overflow: visible;
      }
      div.wrapper,
      div.time-wrapper {
        white-space: nowrap;
        transition:
          width 0.2s cubic-bezier(0.17, 0.67, 0.83, 0.67),
          margin 0.2s cubic-bezier(0.17, 0.67, 0.83, 0.67);
        display: flex;
      }
      div.sub-section {
        display: flex;
        justify-content: center;
        width: 100%;
      }
      .special-times {
        justify-content: flex-end;
        line-height: 40px;
        padding: 0 5px;
        text-transform: uppercase;
        font-size: small;
      }
      .section-header {
        color: var(--material-body-text-color, #000);
        text-transform: uppercase;
        font-weight: 500;
        font-size: var(--material-small-font-size);
        padding: 5px 10px;
      }
      .slot {
        float: left;
        background: rgba(var(--rgb-primary-color), 0.7);
        height: 60px;
        box-sizing: border-box;
        transition: background 0.1s cubic-bezier(0.17, 0.67, 0.83, 0.67);
        position: relative;
        height: 40px;
        line-height: 40px;
        font-size: 10px;
        text-align: center;
      }
      .slot:first-child {
        border-radius: 5px 0 0 5px;
      }
      .slot:last-child {
        border-radius: 0 5px 5px 0;
      }
      .slot:only-child {
        border-radius: 5px;
      }
      .slot.previous {
        cursor: default;
      }
      .slot.selected {
        background: rgba(52, 143, 255, 1);
      }
      .setpoint {
        z-index: 3;
        position: relative;
        text-align: center;
      }
      .slotoverlay {
        position: absolute;
        display: hidden;
        width: 100%;
        height: 100%;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        /*background-color: rgba(0,0,0,0.5);*/
        z-index: 2;
      }
      div.slot.selectable {
        cursor: pointer;
      }

      .previous {
        display: block;
        background: repeating-linear-gradient(
          135deg,
          rgba(0, 0, 0, 0),
          rgba(0, 0, 0, 0) 5px,
          rgba(255, 255, 255, 0.2) 5px,
          rgba(255, 255, 255, 0.2) 10px
        );
        border-radius: 5px 0 0 5px;
      }
      .previous.selected {
        border: 2px solid var(--primary-color);
      }
      .previous.selected.theme-colors {
        border: 2px solid var(--warning-color);
      }
      .wrapper.selectable .slot:hover {
        background: rgba(var(--rgb-primary-color), 0.85);
      }
      .slot:not(:first-child) {
        border-left: 1px solid var(--card-background-color);
      }
      .slot.active {
        background: rgba(var(--rgb-accent-color), 0.7);
      }
      .slot.noborder {
        border: none;
      }
      .wrapper.selectable .slot.active:hover {
        background: rgba(var(--rgb-accent-color), 0.85);
      }
      .wrapper .day.short {
        max-width: 50px;
      }
      .wrapper .day {
        line-height: 42px;
        float: left;
        width: 20%;
        max-width: 100px;
      }
      .wrapper .schedule {
        position: relative;
        width: 100%;
        height: 40px;
        border-radius: 5px;
        overflow: auto;
        margin-bottom: 2px;
        display: flex;
      }
      .setpoint.rotate {
        z-index: 3;
        transform: rotate(-90deg);
        position: absolute;
        top: 20px;
        height: 0px !important;
        width: 100%;
        overflow: visible !important;
      }
      div.time-wrapper div {
        float: left;
        display: flex;
        position: relative;
        height: 25px;
        line-height: 25px;
        font-size: 12px;
        text-align: center;
        align-content: center;
        align-items: center;
        justify-content: center;
      }
      div.time-wrapper div.time:before {
        content: ' ';
        background: var(--disabled-text-color);
        position: absolute;
        left: 0px;
        top: 0px;
        width: 1px;
        height: 5px;
        margin-left: 50%;
        margin-top: 0px;
      }
      .slot span {
        font-size: 10px;
        color: var(--text-primary-color);
        height: 100%;
        display: flex;
        align-content: center;
        align-items: center;
        justify-content: center;
        transition: margin 0.2s cubic-bezier(0.17, 0.67, 0.83, 0.67);
        word-break: nowrap;
        white-space: normal;
        overflow: hidden;
        line-height: 1em;
      }
      div.handle {
        display: flex;
        height: 100%;
        width: 36px;
        margin-left: -19px;
        margin-bottom: -60px;
        align-content: center;
        align-items: center;
        justify-content: center;
      }
      div.button-holder {
        background: var(--card-background-color);
        border-radius: 50%;
        width: 24px;
        height: 24px;
        display: flex;
        visibility: hidden;
        animation: 0.2s fadeIn;
        animation-fill-mode: forwards;
        z-index: 5;
      }
      div.tooltip-container {
        position: absolute;
        margin-top: -12px;
        margin-left: -22px;
        width: 40px;
        height: 0px;
        text-align: center;
        line-height: 35px;
        z-index: 3;
        top: -26px;
      }

      div.tooltip-container.visible {
        display: block;
      }
      div.tooltip-container.left {
        margin-left: -80px;
        text-align: right;
      }
      div.tooltip-container.right {
        margin-left: 0px;
        text-align: left;
      }
      div.tooltip {
        display: inline-flex;
        margin: 0px auto;
        border-radius: 5px;
        color: var(--text-primary-color);
        font-size: 1em;
        padding: 0px 5px;
        text-align: center;
        line-height: 20px;
        z-index: 5;
        transition: all 0.1s ease-in;
        transform-origin: center bottom;
        --tooltip-color: var(--primary-color);
        background: var(--primary-color);
      }
      div.tooltip.active {
        --tooltip-color: rgba(var(--rgb-accent-color), 0.7);
      }
      div.tooltip-container.left div.tooltip {
        transform-origin: right bottom;
      }
      div.tooltip-container.right div.tooltip {
        transform-origin: left bottom;
      }
      div.tooltip-container.center div.tooltip:before {
        content: ' ';
        width: 0px;
        height: 0px;
        border-left: 6px solid transparent;
        border-right: 6px solid transparent;
        border-top: 10px solid var(--primary-color);
        position: absolute;
        margin-top: 25px;
        margin-left: calc(50% - 6px);
        top: 0px;
        left: 0px;
      }
      div.tooltip-container.left div.tooltip:before {
        content: ' ';
        border-top: 10px solid transparent;
        border-bottom: 10px solid transparent;
        border-right: 8px solid var(--tooltip-color);
        opacity: 1;
        position: absolute;
        margin-top: 15px;
        margin-left: calc(100% - 8px);
        left: 0px;
        top: 0px;
        width: 0px;
        height: 0px;
      }
      div.tooltip-container.right div.tooltip:before {
        content: ' ';
        border-top: 10px solid transparent;
        border-bottom: 10px solid transparent;
        border-left: 8px solid var(--tooltip-color);
        opacity: 1;
        position: absolute;
        margin-top: 15px;
        margin-left: 0px;
        left: 0px;
        top: 0px;
        width: 0px;
        height: 0px;
      }
      div.tooltip ha-icon {
        --mdc-icon-size: 18px;
      }

      mwc-button.state-button {
        padding: 0px 10px;
        margin: 0 2px;
        max-width: 100px;
      }

      mwc-button.warning {
        --mdc-theme-primary: var(--error-color);
      }
      mwc-button.warning .mdc-button .mdc-button__label {
        color: var(--primary-text-color);
      }
      mwc-button.right {
        float: right;
      }
      ha-icon-button {
        --mdc-icon-button-size: 36px;
        margin-top: -6px;
        margin-left: -6px;
      }
      @keyframes fadeIn {
        99% {
          visibility: hidden;
        }
        100% {
          visibility: visible;
        }
      }

      mwc-button ha-icon {
        margin-right: 2px;
      }
      mwc-button.active {
        background: var(--primary-color);
        --mdc-theme-primary: var(--text-primary-color);
        border-radius: 4px;
      }
      ha-icon-button.set-off-button {
        margin-left: 0px;
      }
      .sub-heading {
        padding: 0px 10px 0px 10px;
        font-weight: 500;
      }
    `}};n([gt({attribute:!1})],Le.prototype,"hass",void 0),n([gt({attribute:!1})],Le.prototype,"config",void 0),n([gt({attribute:!1})],Le.prototype,"schedule",void 0),n([gt({attribute:!1})],Le.prototype,"suntimes",void 0),n([gt({attribute:!1})],Le.prototype,"editMode",void 0),n([vt()],Le.prototype,"_activeSlot",void 0),n([vt()],Le.prototype,"_activeDay",void 0),n([vt()],Le.prototype,"_show_short_days",void 0),n([vt()],Le.prototype,"rangeMin",void 0),n([vt()],Le.prototype,"rangeMax",void 0),n([vt()],Le.prototype,"stepSize",void 0),n([function(t){return(e,i)=>{const s="function"==typeof e?e:e[i];Object.assign(s,t)}}({passive:!0})],Le.prototype,"_handleTouchStart",null),Le=n([ut("wiser-schedule-slot-editor")],Le);let Me=class extends ht{async showDialog(t){this._params=t,await this.updateComplete}async closeDialog(){this._params=void 0}render(){return this._params?X`
      <ha-dialog
        open
        .heading=${this._params.title||this.hass.localize("state_badge.default.error")}
        @closed=${this.closeDialog}
        @close-dialog=${this.closeDialog}
      >
        <div class="wrapper">${this._params.error||""}</div>
        <ha-button slot="primaryAction" style="float: left" @click=${this.closeDialog} dialogAction="close">
          ${this.hass.localize("ui.dialogs.generic.ok")}
        </ha-button>
      </ha-dialog>
    `:X``}static get styles(){return h`
      div.wrapper {
        color: var(--primary-text-color);
      }
    `}};n([gt({attribute:!1})],Me.prototype,"hass",void 0),n([vt()],Me.prototype,"_params",void 0),Me=n([ut("wiser-dialog-error")],Me);var Ne=Object.freeze({__proto__:null,get DialogError(){return Me}});let De=class extends(de(ht)){constructor(){var t;super(...arguments),this.schedule_id=0,this.use_heat_colors=!0,this.rooms=[],this.entities=[],this._activeSlot=null,this._activeDay=null,this.editMode=!1,this._current_user=null===(t=this.hass)||void 0===t?void 0:t.user,this._assigning_in_progress=0,this._save_in_progress=!1,this.stepSize=5}async initialise(){return await this._isComponentLoaded()&&(this.component_loaded=!0,await this.loadData()),!0}hassSubscribe(){return this.initialise(),[this.hass.connection.subscribeMessage(t=>this.handleUpdate(t),{type:"wiser_updated"})]}async handleUpdate(t){this.config.hub&&t.hub!=this.config.hub||"wiser_updated"!=t.event||await this.loadData()}async _isComponentLoaded(){for(;!this.hass&&!this.config&&!this.hass.config.components.includes("wiser");)await new Promise(t=>setTimeout(t,100));return!0}getSunTime(t,e){return e==Lt[0]?this.suntimes.Sunrises[Pt.indexOf(t)].time:this.suntimes.Sunsets[Pt.indexOf(t)].time}convertLoadedSchedule(t){const e=t.ScheduleData.map(t=>this.convertLoadedScheduleDay(t));return t.ScheduleData=e,t}convertLoadedScheduleDay(t){const e=t.slots.map(e=>Lt.includes(e.Time)?{Time:this.getSunTime(t.day,e.Time),Setpoint:e.Setpoint,SpecialTime:e.Time}:{Time:e.Time,Setpoint:e.Setpoint,SpecialTime:""}).sort((t,e)=>parseInt(t.Time.replace(":",""))<parseInt(e.Time.replace(":",""))?0:1),i=new Set(e.map(t=>JSON.stringify(t))),s=Array.from(i).map(t=>JSON.parse(t));return{day:t.day,slots:s}}convertScheduleForSaving(t){const e=t.ScheduleData.map(t=>this.convertScheduleDayForSaving(t));return t.ScheduleData=e,t}convertScheduleDayForSaving(t){const e=t.slots.map(t=>Lt.includes(t.SpecialTime)?{Time:t.SpecialTime,Setpoint:t.Setpoint,SpecialTime:t.SpecialTime}:{Time:t.Time,Setpoint:t.Setpoint,SpecialTime:""}).sort((t,e)=>t.Time.replace(":","")<e.Time.replace(":","")?0:1),i=new Set(e.map(t=>JSON.stringify(t))),s=Array.from(i).map(t=>JSON.parse(t));return{day:t.day,slots:s}}async loadData(){var t,e;this.error=void 0,this.schedule_type&&this.schedule_id&&!this.editMode&&(await(t=this.hass,e=this.config.hub,t.callWS({type:"wiser/suntimes",hub:e})).then(t=>{this.suntimes=t}).catch(t=>{this.error=t}),await Yt(this.hass,this.config.hub,this.schedule_type,this.schedule_id).then(t=>{this.schedule=this.convertLoadedSchedule(t)}).catch(t=>{this.schedule=void 0,this.error=t}),this.schedule&&await this.get_entity_list(this.hass,this.config.hub).then(t=>{this.entities=t}).catch(t=>{this.error=t}))}async get_entity_list(t,e){return"heating"==this.schedule.Type.toLowerCase()?await((t,e)=>t.callWS({type:"wiser/rooms",hub:e}))(t,e):await((t,e,i)=>t.callWS({type:"wiser/devices",device_type:i,hub:e}))(t,e,this.schedule.SubType)}shouldUpdate(t){return t.has("schedule_id")||t.has("editMode")?(this.loadData(),!0):!!(t.has("schedule")||t.has("entities")||t.has("editMode")||t.has("_assigning_in_progress")||t.has("_save_in_progress")||t.has("error")&&te(this.error))}render(){return this.hass&&this.config&&this.component_loaded?te(this.error)?X` <hui-warning> ${this.error.message} </hui-warning> `:this.schedule&&this.entities&&this.suntimes?X`
          <div>
            <div class="schedule-info">
              <span class="sub-heading">${Vt("wiser.headings.schedule_type")}: </span> ${this.schedule.SubType}
            </div>
            <div class="schedule-info">
              <span class="sub-heading">${Vt("wiser.headings.schedule_id")}: </span> ${this.schedule.Id}
            </div>
            <div class="schedule-info">
              <span class="sub-heading">${Vt("wiser.headings.schedule_name")}: </span> ${this.schedule.Name}
            </div>
            <div class=${this.editMode?"mode":""}>${this.editMode?"Edit Mode":null}</div>
            <div class="wrapper">
              <div class="schedules">
                <div class="slots-wrapper">
                  <wiser-schedule-slot-editor
                    .hass=${this.hass}
                    .config=${this.config}
                    .schedule=${this.editMode?this._tempSchedule:this.schedule}
                    .schedule_type=${this.schedule_type}
                    .suntimes=${this.suntimes}
                    .editMode=${this.editMode}
                    @scheduleChanged=${this.scheduleChanged}
                  ></wiser-schedule-slot-editor>
                </div>
              </div>
            </div>
            ${this.renderScheduleAssignment(this.entities,this.schedule.Assignments)}
            ${this.renderScheduleActionButtonSection()}
          </div>
          ${this.renderCardActions()}
        </ha-card>
      `:X``:X``}renderScheduleAssignment(t,e){if(this.schedule&&!this.editMode)return ne(this.hass,this.config)?X`
          <div class="assignment-wrapper">
            <div class="sub-heading">${Vt("wiser.headings.schedule_assignment")}</div>
            ${t.length>0?t.map(t=>this.renderEntityButton(t,e.map(function(t){return t.name}).includes(t.Name))):X`<div class="schedule-info">(No Assignable Devices)</div>`}
          </div>
        `:X`
          <div class="assignment-wrapper">
            <div class="sub-heading">${Vt("wiser.headings.schedule_assignment")}</div>
            ${e.length>0?t.filter(t=>e.map(function(t){return t.name}).includes(t.Name)).map(t=>this.renderEntityLabel(t)):X`<span class="assignment-label">${Vt("wiser.headings.not_assigned")}</span>`}
          </div>
        `}renderEntityButton(t,e){return X`
      <ha-button
        id=${t.Id}
        class=${e?"active":""}
        appearance=${e?"accent":"plain"}
        size="small"
        @click=${this.entityAssignmentClick}
      >
        ${this._assigning_in_progress==t.Id?X`<span class="waiting"><ha-circular-progress active size="small"></ha-circular-progress></span>`:null}
        ${t.Name}
      </ha-button>
    `}renderScheduleActionButtonSection(){if(this.schedule&&!this.editMode&&ne(this.hass,this.config))return X`
          <div class="actions-wrapper">
            <div class="sub-heading">${Vt("wiser.headings.schedule_actions")}</div>
            <div class="wrapper schedule-action-wrapper">
              ${this.renderScheduleRenameButton()} ${this.renderEditScheduleButton()} ${this.renderCopyScheduleButton()}
              ${this.renderDeleteScheduleButton()}
            </div>
          </div>
        `}renderEntityLabel(t){return X` <span class="assignment-label"> ${t.Name} </span> `}renderCardActions(){if(!this.config.selected_schedule||this.editMode)return X`
        <div class="card-actions">
          <div class="action-buttons">
            ${this.editMode?null:this.renderBackButton()} ${this.editMode?this.renderCancelButton():null}
            ${this.editMode?this.renderSaveScheduleButton():null}
          </div>
        </div>
      `}renderBackButton(){return X`
      <ha-button appearance="plain" @click=${this.backClick}>${this.hass.localize("ui.common.back")} </ha-button>
    `}renderCancelButton(){return X`
      <ha-button appearance="plain" @click=${this.cancelClick}>${this.hass.localize("ui.common.cancel")} </ha-button>
    `}renderScheduleRenameButton(){return X`
      <ha-button class="schedule-action-button" @click=${this.renameScheduleClick}>
        ${Vt("wiser.actions.rename")}
      </ha-button>
    `}renderDeleteScheduleButton(){return X`
      <ha-button
        class="schedule-action-button"
        variant="danger"
        .disabled=${1e3==this.schedule_id}
        @click=${this.deleteClick}
      >
        ${this.hass.localize("ui.common.delete")}
      </ha-button>
    `}renderCopyScheduleButton(){return X`
      <ha-button class="schedule-action-button" .disabled=${1e3==this.schedule_id} @click=${this.copyClick}>
        ${Vt("wiser.actions.copy")}
      </ha-button>
    `}renderEditScheduleButton(){return X`
      <ha-button class="schedule-action-button" @click=${this.editClick}>
        ${this.hass.localize("ui.common.edit")}
      </ha-button>
    `}renderFilesScheduleButton(){return X`
      <ha-button class="schedule-action-button" @click=${this.filesClick}>
        ${Vt("wiser.actions.files")}
      </ha-button>
    `}renderSaveScheduleButton(){if(ne(this.hass,this.config))return X`
        <ha-button appearance="plain" style="float: right" @click=${this.saveClick}>
          ${this._save_in_progress?X`<ha-circular-progress active size="small"></ha-circular-progress>`:this.hass.localize("ui.common.save")}
        </ha-button>
      `}async entityAssignmentClick(t){const e=t.target;this._assigning_in_progress=parseInt(e.id),ne(this.hass,this.config)&&await((t,e,i,s,n,r=!1)=>t.callWS({type:"wiser/schedule/assign",hub:e,schedule_type:i,schedule_id:s,entity_id:n,remove:r}))(this.hass,this.config.hub,this.schedule_type,this.schedule_id,e.id,e.classList.contains("active")),this._assigning_in_progress=0}backClick(){const t=new CustomEvent("backClick");this.dispatchEvent(t)}editClick(){this._tempSchedule=this.schedule,this.editMode=!this.editMode}copyClick(){const t=new CustomEvent("copyClick");this.dispatchEvent(t)}filesClick(){const t=new CustomEvent("filesClick");this.dispatchEvent(t)}async renameScheduleClick(){const t=new CustomEvent("renameClick");this.dispatchEvent(t)}async deleteClick(t){const e=t.target;if(await new Promise(t=>{yt(e,"show-dialog",{dialogTag:"wiser-dialog-delete-confirm",dialogImport:()=>Promise.resolve().then(function(){return pe}),dialogParams:{cancel:()=>{t(!1)},confirm:()=>{t(!0)},name:this.schedule.Name}})})){this.schedule_id=0,await(i=this.hass,s=this.config.hub,n=this.schedule.Type,r=this.schedule.Id,i.callWS({type:"wiser/schedule/delete",hub:s,schedule_type:n,schedule_id:r}));const t=new CustomEvent("scheduleDeleted");this.dispatchEvent(t)}var i,s,n,r}cancelClick(){this.editMode=!1}validateSchedule(t){return t.ScheduleData.map(t=>t.slots).map(t=>t.length>0).includes(!0)}async saveClick(){if(this._save_in_progress=!0,this.validateSchedule(this._tempSchedule))It.includes(this.schedule_type)&&(this._tempSchedule=await this.convertScheduleForSaving(this._tempSchedule)),await(t=this.hass,e=this.config.hub,i=this.schedule_type,s=this.schedule_id,n=this._tempSchedule,t.callWS({type:"wiser/schedule/save",hub:e,schedule_type:i,schedule_id:s,schedule:n})),this.editMode=!1;else{const t=X`The schedule you are trying to save has no time slots.`;yt(this,"show-dialog",{dialogTag:"wiser-dialog-error",dialogImport:()=>Promise.resolve().then(function(){return Ne}),dialogParams:{title:"Error Saving Schedule",error:t}})}var t,e,i,s,n;this._save_in_progress=!1}scheduleChanged(t){this._tempSchedule=t.detail.schedule,this.render()}static get styles(){return h`
      :host {
        display: block;
        max-width: 100%;
      }
      div.outer {
        width: 100%;
        overflow-x: hidden;
        overflow-y: hidden;
        border-radius: 5px;
      }
      div.wrapper,
      div.time-wrapper {
        white-space: nowrap;
        transition:
          width 0.2s cubic-bezier(0.17, 0.67, 0.83, 0.67),
          margin 0.2s cubic-bezier(0.17, 0.67, 0.83, 0.67);
      }
      div.assignment-wrapper,
      div.actions-wrapper {
        border-top: 1px solid var(--divider-color, #e8e8e8);
        padding: 5px 0px;
        min-height: 40px;
      }
      div.mode {
        position: absolute;
        right: 10px;
        top: 64px;
        background: var(--primary-color);
        padding: 2px 10px;
        border-radius: 20px;
        font-size: smaller;
        color: var(--app-header-text-color);
      }
      div.action-buttons {
        display: flow-root;
      }
      span.assignment-label {
        color: var(--primary-color);
        text-transform: uppercase;
        font-weight: 500;
        font-size: var(--material-small-font-size);
        padding: 5px 10px;
      }
      .slot {
        float: left;
        background: rgba(var(--rgb-primary-color), 0.7);
        height: 60px;
        cursor: pointer;
        box-sizing: border-box;
        transition: background 0.1s cubic-bezier(0.17, 0.67, 0.83, 0.67);
        position: relative;
        height: 40px;
        line-height: 40px;
        font-size: 10px;
        text-align: center;
        overflow: hidden;
      }
      .slot.previous {
        cursor: default;
      }
      .slot.selected {
        background: rgba(52, 143, 255, 1);
      }
      .setpoint {
        z-index: 3;
        position: relative;
        text-align: center;
      }
      .slotoverlay {
        position: absolute;
        display: hidden;
        width: 100%;
        height: 100%;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        /*background-color: rgba(0,0,0,0.5);*/
        z-index: 2;
        cursor: pointer;
      }
      .previous {
        display: block;
        background: repeating-linear-gradient(
          135deg,
          rgba(0, 0, 0, 0),
          rgba(0, 0, 0, 0) 5px,
          rgba(255, 255, 255, 0.2) 5px,
          rgba(255, 255, 255, 0.2) 10px
        );
      }
      .wrapper.selectable .slot:hover {
        background: rgba(var(--rgb-primary-color), 0.85);
      }
      .slot:not(:first-child) {
        border-left: 1px solid var(--card-background-color);
      }
      .slot:not(:last-child) {
        border-right: 1px solid var(--card-background-color);
      }
      .slot.active {
        background: rgba(var(--rgb-accent-color), 0.7);
      }
      .slot.noborder {
        border: none;
      }
      .wrapper.selectable .slot.active:hover {
        background: rgba(var(--rgb-accent-color), 0.85);
      }
      .wrapper .days .day {
        line-height: 42px;
        float: left;
        width: 100%;
      }
      .wrapper .schedules {
        position: relative;
        padding-top: 30px;
        width: 100%;
      }
      .wrapper .schedules .slots {
        height: 40px;
        border-radius: 5px;
        overflow: auto;
        margin-bottom: 2px;
        display: flex;
      }

      .setpoint.rotate {
        z-index: 3;
        transform: rotate(-90deg);
        position: absolute;
        top: 20px;
        height: 0px !important;
        width: 100%;
        overflow: visible !important;
      }
      div.schedule-action-wrapper {
        display: flex;
        justify-content: center;
      }
      div.time-wrapper div {
        float: left;
        display: flex;
        position: relative;
        height: 25px;
        line-height: 25px;
        font-size: 12px;
        text-align: center;
        align-content: center;
        align-items: center;
        justify-content: center;
      }
      div.time-wrapper div.time:before {
        content: ' ';
        background: var(--disabled-text-color);
        position: absolute;
        left: 0px;
        top: 0px;
        width: 1px;
        height: 5px;
        margin-left: 50%;
        margin-top: 0px;
      }
      .slot span {
        font-size: 10px;
        color: var(--text-primary-color);
        height: 100%;
        display: flex;
        align-content: center;
        align-items: center;
        justify-content: center;
        transition: margin 0.2s cubic-bezier(0.17, 0.67, 0.83, 0.67);
        word-break: nowrap;
        white-space: normal;
        overflow: hidden;
        line-height: 1em;
      }
      div.handle {
        display: flex;
        height: 100%;
        width: 36px;
        margin-left: -19px;
        margin-bottom: -60px;
        align-content: center;
        align-items: center;
        justify-content: center;
      }
      div.button-holder {
        background: var(--card-background-color);
        border-radius: 50%;
        width: 24px;
        height: 24px;
        display: flex;
        visibility: hidden;
        animation: 0.2s fadeIn;
        animation-fill-mode: forwards;
      }
      .schedule-action-button {
        width: 20%;
        padding: 0 5px;
      }
      ha-icon-button {
        --mdc-icon-button-size: 36px;
        margin-top: -6px;
        margin-left: -6px;
      }
      @keyframes fadeIn {
        99% {
          visibility: hidden;
        }
        100% {
          visibility: visible;
        }
      }
      .card-header ha-icon-button {
        position: absolute;
        right: 6px;
        top: 6px;
      }
      .sub-heading {
        padding-bottom: 10px;
        font-weight: 500;
      }
      span.waiting {
        position: absolute;
        height: 28px;
        width: 100%;
        margin: 4px;
      }
      div.schedule-info {
        margin: 3px 0;
      }
    `}};n([gt({attribute:!1})],De.prototype,"config",void 0),n([gt({attribute:!1})],De.prototype,"schedule_id",void 0),n([gt({attribute:!1})],De.prototype,"schedule_type",void 0),n([gt({attribute:!1})],De.prototype,"use_heat_colors",void 0),n([vt()],De.prototype,"schedule",void 0),n([vt()],De.prototype,"rooms",void 0),n([vt()],De.prototype,"entities",void 0),n([vt()],De.prototype,"suntimes",void 0),n([vt()],De.prototype,"component_loaded",void 0),n([vt()],De.prototype,"_activeSlot",void 0),n([vt()],De.prototype,"_activeDay",void 0),n([vt()],De.prototype,"editMode",void 0),n([vt()],De.prototype,"_current_user",void 0),n([vt()],De.prototype,"_assigning_in_progress",void 0),n([vt()],De.prototype,"_save_in_progress",void 0),n([vt()],De.prototype,"error",void 0),De=n([ut("wiser-schedule-edit-card")],De);let He=class extends ht{constructor(){super(),this.component_loaded=!1,this._schedule_types=[],this._schedule_info={Name:"",Type:"Heating"},this.initialise()}async initialise(){return await this.isComponentLoaded()&&(this.component_loaded=!0,await this.loadData()),!0}async isComponentLoaded(){for(;!this.hass||!this.hass.config.components.includes("wiser");)await new Promise(t=>setTimeout(t,100));return!0}async loadData(){this._schedule_types=await Wt(this.hass,this.config.hub)}render(){return this.hass&&this.config?X`
      <div>
        <div>${Vt("wiser.actions.add_schedule")}</div>
        <div class="wrapper" style="white-space: normal">${Vt("wiser.helpers.add_schedule")}</div>
        <div class="wrapper">${this._schedule_types.map((t,e)=>this.renderScheduleTypeButtons(t,e))}</div>
        <ha-textfield
          class="schedule-name"
          auto-validate
          required
          label=${Vt("wiser.headings.schedule_name")}
          error-message=${Vt("wiser.common.name_required")}
          .configValue=${"Name"}
          @input=${this._valueChanged}
        >
        </ha-textfield>
      </div>
      <div class="card-actions">
        <ha-button
          appearance="plain"
          style="float: right"
          .disabled=${!this._schedule_info||!this._schedule_info.Name}
          @click=${this.confirmClick}
          dialogAction="close"
        >
          ${this.hass.localize("ui.common.save")}
        </ha-button>
        <ha-button appearance="plain" @click=${this.cancelClick}> ${this.hass.localize("ui.common.cancel")} </ha-button>
      </div>
    `:X``}renderScheduleTypeButtons(t,e){return X`
      <ha-button
        id=${e}
        size="small"
        appearance=${this._schedule_info&&this._schedule_info.Type==t?"filled":"plain"}
        @click=${this._valueChanged}
        .configValue=${"Type"}
        .value=${t}
      >
        ${t}
      </ha-button>
    `}async confirmClick(){await this.createSchedule()}async createSchedule(){var t,e,i,s;await(t=this.hass,e=this.config.hub,i=this._schedule_info.Type,s=this._schedule_info.Name,t.callWS({type:"wiser/schedule/create",hub:e,schedule_type:i,name:s}));const n=new CustomEvent("scheduleAdded");this.dispatchEvent(n)}cancelClick(){const t=new CustomEvent("backClick");this.dispatchEvent(t)}_valueChanged(t){const e=t.target;e.configValue&&(this._schedule_info=Object.assign(Object.assign({},this._schedule_info),{[e.configValue]:void 0!==e.checked?e.checked:e.value}))}static get styles(){return h`
      div.wrapper {
        white-space: nowrap;
        transition:
          width 0.2s cubic-bezier(0.17, 0.67, 0.83, 0.67),
          margin 0.2s cubic-bezier(0.17, 0.67, 0.83, 0.67);
        overflow: auto;
      }
      div.wrapper {
        color: var(--primary-text-color);
        padding: 5px 0;
      }
      .schedule-type-select {
        margin: 20px 0 0 0;
      }
      .schedule-name {
        margin: 20px 0 0 0;
        width: 100%;
      }
      ha-icon-button {
        --mdc-icon-button-size: 36px;
        margin-top: -6px;
        margin-left: -6px;
      }
      .card-header ha-icon-button {
        position: absolute;
        right: 6px;
        top: 6px;
      }
      mwc-button.active {
        background: var(--primary-color);
        --mdc-theme-primary: var(--text-primary-color);
        border-radius: 4px;
      }
    `}};n([gt({attribute:!1})],He.prototype,"hass",void 0),n([gt({attribute:!1})],He.prototype,"config",void 0),n([gt({attribute:!1})],He.prototype,"component_loaded",void 0),n([vt()],He.prototype,"_schedule_types",void 0),n([vt()],He.prototype,"_schedule_info",void 0),He=n([ut("wiser-schedule-add-card")],He);let Ue=class extends ht{constructor(){super(),this.schedule_id=0,this.component_loaded=!1,this._copy_in_progress=0,this._schedule_list=[],this.initialise()}async initialise(){return await this.isComponentLoaded()&&(this.component_loaded=!0,await this.loadData()),!0}async isComponentLoaded(){for(;!this.hass||!this.hass.config.components.includes("wiser");)await new Promise(t=>setTimeout(t,100));return!0}async loadData(){this.schedule=await Yt(this.hass,this.config.hub,this.schedule_type,this.schedule_id),this._schedule_list=await qt(this.hass,this.config.hub,this.schedule_type)}render(){return this.hass&&this.config&&this.schedule?X`
       <div>
          <div>${Vt("wiser.headings.copy_schedule")}</div>
          <div class="schedule-info">
            <span class="sub-heading">${Vt("wiser.headings.schedule_type")}:</span> ${this.schedule.Type}
          </div>
          <div class="schedule-info">
            <span class="sub-heading">${Vt("wiser.headings.schedule_id")}:</span> ${this.schedule.Id}
          </div>
          <div class="schedule-info">
            <span class="sub-heading">${Vt("wiser.headings.schedule_name")}:</span> ${this.schedule.Name}
          </div>
          <div class="wrapper" style="margin: 20px 0 0 0;">${Vt("wiser.helpers.select_copy_schedule")}</div>
          <div class="assignment-wrapper">
            ${this._schedule_list.filter(t=>{var e;return t.Id!=(null===(e=this.schedule)||void 0===e?void 0:e.Id)}).map(t=>this.renderScheduleButtons(t))}
          </div>
        </div>
        <div class="card-actions">
          <ha-button
            appearance="plain"
            @click=${this.cancelClick}
          > 
            ${this.hass.localize("ui.common.cancel")}
          </ha-button>
        </div>
      </ha-card>
    `:X``}renderScheduleButtons(t){return X`
      <ha-button
        class="schedule-button"
        id=${t.Id}
        size="small"
        @click=${this._copySchedule}
        .value=${t.Name}
      >
        ${this._copy_in_progress==t.Id?X`<span class="waiting"><ha-circular-progress active size="small"></ha-circular-progress></span>`:null}
        ${t.Name}
      </ha-button>
    `}cancelClick(){const t=new CustomEvent("backClick",{detail:Et.ScheduleEdit});this.dispatchEvent(t)}async _copySchedule(t){const e=t.target;if(e.id){this._copy_in_progress=parseInt(e.id),await(i=this.hass,s=this.config.hub,n=this.schedule_type,r=this.schedule_id,o=parseInt(e.id),i.callWS({type:"wiser/schedule/copy",hub:s,schedule_type:n,schedule_id:r,to_schedule_id:o})),this._copy_in_progress=0;const t=new CustomEvent("scheduleCopied");this.dispatchEvent(t)}var i,s,n,r,o}static get styles(){return h`
      div.wrapper {
        white-space: nowrap;
        transition:
          width 0.2s cubic-bezier(0.17, 0.67, 0.83, 0.67),
          margin 0.2s cubic-bezier(0.17, 0.67, 0.83, 0.67);
        overflow: auto;
      }
      div.card-actions {
        border-top: 1px solid var(--divider-color, #e8e8e8);
        padding: 5px 0px;
        min-height: 40px;
      }
      div.wrapper {
        color: var(--primary-text-color);
        padding: 5px 0;
      }
      .schedule-type-select {
        margin: 20px 0 0 0;
      }
      .schedule-name {
        margin: 20px 0 0 0;
        width: 100%;
      }
      .sub-heading {
        padding-bottom: 10px;
        font-weight: 500;
      }
      .schedule-button {
        padding: 5px;
      }
      span.waiting {
        position: absolute;
        height: 28px;
        width: 100%;
        margin: 4px;
      }
      div.schedule-info {
        margin: 3px 0;
      }
    `}};n([gt({attribute:!1})],Ue.prototype,"hass",void 0),n([gt({attribute:!1})],Ue.prototype,"config",void 0),n([gt({attribute:!1})],Ue.prototype,"schedule_id",void 0),n([gt({attribute:!1})],Ue.prototype,"schedule_type",void 0),n([vt()],Ue.prototype,"schedule",void 0),n([vt()],Ue.prototype,"component_loaded",void 0),n([vt()],Ue.prototype,"_copy_in_progress",void 0),n([vt()],Ue.prototype,"_schedule_list",void 0),Ue=n([ut("wiser-schedule-copy-card")],Ue);let ze=class extends ht{constructor(){super(),this.component_loaded=!1,this._newScheduleName="",this._rename_in_progress=!1,this.initialise()}async initialise(){return await this.isComponentLoaded()&&(this.component_loaded=!0,await this.loadData()),!0}async isComponentLoaded(){for(;!this.hass||!this.hass.config.components.includes("wiser");)await new Promise(t=>setTimeout(t,100));return!0}async loadData(){this._schedule=await Yt(this.hass,this.config.hub,this.schedule_type,this.schedule_id)}render(){return this.hass&&this.config?X`
      <div>
        <div>${Vt("wiser.headings.rename_schedule")}</div>
        <div class="wrapper">${Vt("wiser.helpers.enter_new_name")}</div>
        <ha-textfield
          class="schedule-name"
          auto-validate
          required
          label=${Vt("wiser.headings.schedule_name")}
          value=${this._schedule.Name}
          error-message="Name is required"
          .configValue=${"Name"}
          @input=${this._valueChanged}
        >
        </ha-textfield>
      </div>
      <div class="card-actions">
        <ha-button
          appearance="plain"
          style="float: right"
          .disabled=${!this._newScheduleName}
          @click=${this.confirmClick}
        >
          ${this._rename_in_progress?X`<span class="waiting"><ha-circular-progress active size="small"></ha-circular-progress></span>`:this.hass.localize("ui.common.save")}
        </ha-button>
        <ha-button appearance="plain" @click=${this.cancelClick}>
          ${this.hass.localize("ui.common.cancel")}
        </ha-button>
      </div>
    `:X``}async confirmClick(){await this.renameSchedule()}async renameSchedule(){var t,e,i,s,n;this._rename_in_progress=!0,await(t=this.hass,e=this.config.hub,i=this.schedule_type,s=this.schedule_id,n=this._newScheduleName,t.callWS({type:"wiser/schedule/rename",hub:e,schedule_type:i,schedule_id:s,schedule_name:n}));const r=new CustomEvent("scheduleRenamed");this.dispatchEvent(r),this._rename_in_progress=!1}cancelClick(){const t=new CustomEvent("backClick",{detail:Et.ScheduleEdit});this.dispatchEvent(t)}_valueChanged(t){const e=t.target;e.configValue&&(this._newScheduleName=e.value)}static get styles(){return h`
      div.wrapper {
        white-space: nowrap;
        transition:
          width 0.2s cubic-bezier(0.17, 0.67, 0.83, 0.67),
          margin 0.2s cubic-bezier(0.17, 0.67, 0.83, 0.67);
        overflow: auto;
      }
      div.wrapper {
        color: var(--primary-text-color);
        padding: 5px 0;
      }
      .card-actions {
        padding-top: 8px;
      }
      .schedule-type-select {
        margin: 20px 0 0 0;
      }
      .schedule-name {
        margin: 20px 0 0 0;
        width: 100%;
      }
      ha-icon-button {
        --mdc-icon-button-size: 36px;
        margin-top: -6px;
        margin-left: -6px;
      }
      .card-header ha-icon-button {
        position: absolute;
        right: 6px;
        top: 6px;
      }
      mwc-button.active {
        background: var(--primary-color);
        --mdc-theme-primary: var(--text-primary-color);
        border-radius: 4px;
      }
    `}};n([gt({attribute:!1})],ze.prototype,"hass",void 0),n([gt({attribute:!1})],ze.prototype,"config",void 0),n([gt({attribute:!1})],ze.prototype,"component_loaded",void 0),n([gt({attribute:!1})],ze.prototype,"schedule_type",void 0),n([gt({attribute:!1})],ze.prototype,"schedule_id",void 0),n([vt()],ze.prototype,"_newScheduleName",void 0),n([vt()],ze.prototype,"_schedule",void 0),n([vt()],ze.prototype,"_rename_in_progress",void 0),ze=n([ut("wiser-schedule-rename-card")],ze);
/**
     * @license
     * Copyright 2016 Google Inc.
     *
     * Permission is hereby granted, free of charge, to any person obtaining a copy
     * of this software and associated documentation files (the "Software"), to deal
     * in the Software without restriction, including without limitation the rights
     * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
     * copies of the Software, and to permit persons to whom the Software is
     * furnished to do so, subject to the following conditions:
     *
     * The above copyright notice and this permission notice shall be included in
     * all copies or substantial portions of the Software.
     *
     * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
     * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
     * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
     * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
     * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
     * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
     * THE SOFTWARE.
     */
var Fe=function(){function t(t){void 0===t&&(t={}),this.adapter=t}return Object.defineProperty(t,"cssClasses",{get:function(){return{}},enumerable:!1,configurable:!0}),Object.defineProperty(t,"strings",{get:function(){return{}},enumerable:!1,configurable:!0}),Object.defineProperty(t,"numbers",{get:function(){return{}},enumerable:!1,configurable:!0}),Object.defineProperty(t,"defaultAdapter",{get:function(){return{}},enumerable:!1,configurable:!0}),t.prototype.init=function(){},t.prototype.destroy=function(){},t}(),Be={ROOT:"mdc-form-field"},Ve={LABEL_SELECTOR:".mdc-form-field > label"},je=function(t){function e(i){var n=t.call(this,s(s({},e.defaultAdapter),i))||this;return n.click=function(){n.handleClick()},n}return i(e,t),Object.defineProperty(e,"cssClasses",{get:function(){return Be},enumerable:!1,configurable:!0}),Object.defineProperty(e,"strings",{get:function(){return Ve},enumerable:!1,configurable:!0}),Object.defineProperty(e,"defaultAdapter",{get:function(){return{activateInputRipple:function(){},deactivateInputRipple:function(){},deregisterInteractionHandler:function(){},registerInteractionHandler:function(){}}},enumerable:!1,configurable:!0}),e.prototype.init=function(){this.adapter.registerInteractionHandler("click",this.click)},e.prototype.destroy=function(){this.adapter.deregisterInteractionHandler("click",this.click)},e.prototype.handleClick=function(){var t=this;this.adapter.activateInputRipple(),requestAnimationFrame(function(){t.adapter.deactivateInputRipple()})},e}(Fe);
/**
     * @license
     * Copyright 2017 Google Inc.
     *
     * Permission is hereby granted, free of charge, to any person obtaining a copy
     * of this software and associated documentation files (the "Software"), to deal
     * in the Software without restriction, including without limitation the rights
     * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
     * copies of the Software, and to permit persons to whom the Software is
     * furnished to do so, subject to the following conditions:
     *
     * The above copyright notice and this permission notice shall be included in
     * all copies or substantial portions of the Software.
     *
     * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
     * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
     * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
     * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
     * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
     * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
     * THE SOFTWARE.
     */
/**
     * @license
     * Copyright 2019 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
const We=window,qe=We.ShadowRoot&&(void 0===We.ShadyCSS||We.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,Ye=Symbol(),Xe=new WeakMap;let Ge=class{constructor(t,e,i){if(this._$cssResult$=!0,i!==Ye)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o;const e=this.t;if(qe&&void 0===t){const i=void 0!==e&&1===e.length;i&&(t=Xe.get(e)),void 0===t&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),i&&Xe.set(e,t))}return t}toString(){return this.cssText}};const Ke=qe?t=>t:t=>t instanceof CSSStyleSheet?(t=>{let e="";for(const i of t.cssRules)e+=i.cssText;return(t=>new Ge("string"==typeof t?t:t+"",void 0,Ye))(e)})(t):t;
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */var Je;const Ze=window,Qe=Ze.trustedTypes,ti=Qe?Qe.emptyScript:"",ei=Ze.reactiveElementPolyfillSupport,ii={toAttribute(t,e){switch(e){case Boolean:t=t?ti:null;break;case Object:case Array:t=null==t?t:JSON.stringify(t)}return t},fromAttribute(t,e){let i=t;switch(e){case Boolean:i=null!==t;break;case Number:i=null===t?null:Number(t);break;case Object:case Array:try{i=JSON.parse(t)}catch(t){i=null}}return i}},si=(t,e)=>e!==t&&(e==e||t==t),ni={attribute:!0,type:String,converter:ii,reflect:!1,hasChanged:si},ri="finalized";let oi=class extends HTMLElement{constructor(){super(),this._$Ei=new Map,this.isUpdatePending=!1,this.hasUpdated=!1,this._$El=null,this._$Eu()}static addInitializer(t){var e;this.finalize(),(null!==(e=this.h)&&void 0!==e?e:this.h=[]).push(t)}static get observedAttributes(){this.finalize();const t=[];return this.elementProperties.forEach((e,i)=>{const s=this._$Ep(i,e);void 0!==s&&(this._$Ev.set(s,i),t.push(s))}),t}static createProperty(t,e=ni){if(e.state&&(e.attribute=!1),this.finalize(),this.elementProperties.set(t,e),!e.noAccessor&&!this.prototype.hasOwnProperty(t)){const i="symbol"==typeof t?Symbol():"__"+t,s=this.getPropertyDescriptor(t,i,e);void 0!==s&&Object.defineProperty(this.prototype,t,s)}}static getPropertyDescriptor(t,e,i){return{get(){return this[e]},set(s){const n=this[t];this[e]=s,this.requestUpdate(t,n,i)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)||ni}static finalize(){if(this.hasOwnProperty(ri))return!1;this[ri]=!0;const t=Object.getPrototypeOf(this);if(t.finalize(),void 0!==t.h&&(this.h=[...t.h]),this.elementProperties=new Map(t.elementProperties),this._$Ev=new Map,this.hasOwnProperty("properties")){const t=this.properties,e=[...Object.getOwnPropertyNames(t),...Object.getOwnPropertySymbols(t)];for(const i of e)this.createProperty(i,t[i])}return this.elementStyles=this.finalizeStyles(this.styles),!0}static finalizeStyles(t){const e=[];if(Array.isArray(t)){const i=new Set(t.flat(1/0).reverse());for(const t of i)e.unshift(Ke(t))}else void 0!==t&&e.push(Ke(t));return e}static _$Ep(t,e){const i=e.attribute;return!1===i?void 0:"string"==typeof i?i:"string"==typeof t?t.toLowerCase():void 0}_$Eu(){var t;this._$E_=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$Eg(),this.requestUpdate(),null===(t=this.constructor.h)||void 0===t||t.forEach(t=>t(this))}addController(t){var e,i;(null!==(e=this._$ES)&&void 0!==e?e:this._$ES=[]).push(t),void 0!==this.renderRoot&&this.isConnected&&(null===(i=t.hostConnected)||void 0===i||i.call(t))}removeController(t){var e;null===(e=this._$ES)||void 0===e||e.splice(this._$ES.indexOf(t)>>>0,1)}_$Eg(){this.constructor.elementProperties.forEach((t,e)=>{this.hasOwnProperty(e)&&(this._$Ei.set(e,this[e]),delete this[e])})}createRenderRoot(){var t;const e=null!==(t=this.shadowRoot)&&void 0!==t?t:this.attachShadow(this.constructor.shadowRootOptions);return((t,e)=>{qe?t.adoptedStyleSheets=e.map(t=>t instanceof CSSStyleSheet?t:t.styleSheet):e.forEach(e=>{const i=document.createElement("style"),s=We.litNonce;void 0!==s&&i.setAttribute("nonce",s),i.textContent=e.cssText,t.appendChild(i)})})(e,this.constructor.elementStyles),e}connectedCallback(){var t;void 0===this.renderRoot&&(this.renderRoot=this.createRenderRoot()),this.enableUpdating(!0),null===(t=this._$ES)||void 0===t||t.forEach(t=>{var e;return null===(e=t.hostConnected)||void 0===e?void 0:e.call(t)})}enableUpdating(t){}disconnectedCallback(){var t;null===(t=this._$ES)||void 0===t||t.forEach(t=>{var e;return null===(e=t.hostDisconnected)||void 0===e?void 0:e.call(t)})}attributeChangedCallback(t,e,i){this._$AK(t,i)}_$EO(t,e,i=ni){var s;const n=this.constructor._$Ep(t,i);if(void 0!==n&&!0===i.reflect){const r=(void 0!==(null===(s=i.converter)||void 0===s?void 0:s.toAttribute)?i.converter:ii).toAttribute(e,i.type);this._$El=t,null==r?this.removeAttribute(n):this.setAttribute(n,r),this._$El=null}}_$AK(t,e){var i;const s=this.constructor,n=s._$Ev.get(t);if(void 0!==n&&this._$El!==n){const t=s.getPropertyOptions(n),r="function"==typeof t.converter?{fromAttribute:t.converter}:void 0!==(null===(i=t.converter)||void 0===i?void 0:i.fromAttribute)?t.converter:ii;this._$El=n,this[n]=r.fromAttribute(e,t.type),this._$El=null}}requestUpdate(t,e,i){let s=!0;void 0!==t&&(((i=i||this.constructor.getPropertyOptions(t)).hasChanged||si)(this[t],e)?(this._$AL.has(t)||this._$AL.set(t,e),!0===i.reflect&&this._$El!==t&&(void 0===this._$EC&&(this._$EC=new Map),this._$EC.set(t,i))):s=!1),!this.isUpdatePending&&s&&(this._$E_=this._$Ej())}async _$Ej(){this.isUpdatePending=!0;try{await this._$E_}catch(t){Promise.reject(t)}const t=this.scheduleUpdate();return null!=t&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){var t;if(!this.isUpdatePending)return;this.hasUpdated,this._$Ei&&(this._$Ei.forEach((t,e)=>this[e]=t),this._$Ei=void 0);let e=!1;const i=this._$AL;try{e=this.shouldUpdate(i),e?(this.willUpdate(i),null===(t=this._$ES)||void 0===t||t.forEach(t=>{var e;return null===(e=t.hostUpdate)||void 0===e?void 0:e.call(t)}),this.update(i)):this._$Ek()}catch(t){throw e=!1,this._$Ek(),t}e&&this._$AE(i)}willUpdate(t){}_$AE(t){var e;null===(e=this._$ES)||void 0===e||e.forEach(t=>{var e;return null===(e=t.hostUpdated)||void 0===e?void 0:e.call(t)}),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$Ek(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$E_}shouldUpdate(t){return!0}update(t){void 0!==this._$EC&&(this._$EC.forEach((t,e)=>this._$EO(e,this[e],t)),this._$EC=void 0),this._$Ek()}updated(t){}firstUpdated(t){}};
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
var ai;oi[ri]=!0,oi.elementProperties=new Map,oi.elementStyles=[],oi.shadowRootOptions={mode:"open"},null==ei||ei({ReactiveElement:oi}),(null!==(Je=Ze.reactiveElementVersions)&&void 0!==Je?Je:Ze.reactiveElementVersions=[]).push("1.6.3");const li=window,di=li.trustedTypes,ci=di?di.createPolicy("lit-html",{createHTML:t=>t}):void 0,hi="$lit$",pi=`lit$${(Math.random()+"").slice(9)}$`,ui="?"+pi,mi=`<${ui}>`,fi=document,gi=()=>fi.createComment(""),vi=t=>null===t||"object"!=typeof t&&"function"!=typeof t,_i=Array.isArray,bi="[ \t\n\f\r]",yi=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,xi=/-->/g,$i=/>/g,wi=RegExp(`>|${bi}(?:([^\\s"'>=/]+)(${bi}*=${bi}*(?:[^ \t\n\f\r"'\`<>=]|("|')|))|$)`,"g"),Ai=/'/g,Ei=/"/g,Si=/^(?:script|style|textarea|title)$/i,Ci=Symbol.for("lit-noChange"),Ti=Symbol.for("lit-nothing"),Ii=new WeakMap,Oi=fi.createTreeWalker(fi,129,null,!1);function ki(t,e){if(!Array.isArray(t)||!t.hasOwnProperty("raw"))throw Error("invalid template strings array");return void 0!==ci?ci.createHTML(e):e}let Ri=class t{constructor({strings:e,_$litType$:i},s){let n;this.parts=[];let r=0,o=0;const a=e.length-1,l=this.parts,[d,c]=((t,e)=>{const i=t.length-1,s=[];let n,r=2===e?"<svg>":"",o=yi;for(let e=0;e<i;e++){const i=t[e];let a,l,d=-1,c=0;for(;c<i.length&&(o.lastIndex=c,l=o.exec(i),null!==l);)c=o.lastIndex,o===yi?"!--"===l[1]?o=xi:void 0!==l[1]?o=$i:void 0!==l[2]?(Si.test(l[2])&&(n=RegExp("</"+l[2],"g")),o=wi):void 0!==l[3]&&(o=wi):o===wi?">"===l[0]?(o=null!=n?n:yi,d=-1):void 0===l[1]?d=-2:(d=o.lastIndex-l[2].length,a=l[1],o=void 0===l[3]?wi:'"'===l[3]?Ei:Ai):o===Ei||o===Ai?o=wi:o===xi||o===$i?o=yi:(o=wi,n=void 0);const h=o===wi&&t[e+1].startsWith("/>")?" ":"";r+=o===yi?i+mi:d>=0?(s.push(a),i.slice(0,d)+hi+i.slice(d)+pi+h):i+pi+(-2===d?(s.push(void 0),e):h)}return[ki(t,r+(t[i]||"<?>")+(2===e?"</svg>":"")),s]})(e,i);if(this.el=t.createElement(d,s),Oi.currentNode=this.el.content,2===i){const t=this.el.content,e=t.firstChild;e.remove(),t.append(...e.childNodes)}for(;null!==(n=Oi.nextNode())&&l.length<a;){if(1===n.nodeType){if(n.hasAttributes()){const t=[];for(const e of n.getAttributeNames())if(e.endsWith(hi)||e.startsWith(pi)){const i=c[o++];if(t.push(e),void 0!==i){const t=n.getAttribute(i.toLowerCase()+hi).split(pi),e=/([.?@])?(.*)/.exec(i);l.push({type:1,index:r,name:e[2],strings:t,ctor:"."===e[1]?Di:"?"===e[1]?Ui:"@"===e[1]?zi:Ni})}else l.push({type:6,index:r})}for(const e of t)n.removeAttribute(e)}if(Si.test(n.tagName)){const t=n.textContent.split(pi),e=t.length-1;if(e>0){n.textContent=di?di.emptyScript:"";for(let i=0;i<e;i++)n.append(t[i],gi()),Oi.nextNode(),l.push({type:2,index:++r});n.append(t[e],gi())}}}else if(8===n.nodeType)if(n.data===ui)l.push({type:2,index:r});else{let t=-1;for(;-1!==(t=n.data.indexOf(pi,t+1));)l.push({type:7,index:r}),t+=pi.length-1}r++}}static createElement(t,e){const i=fi.createElement("template");return i.innerHTML=t,i}};function Pi(t,e,i=t,s){var n,r,o,a;if(e===Ci)return e;let l=void 0!==s?null===(n=i._$Co)||void 0===n?void 0:n[s]:i._$Cl;const d=vi(e)?void 0:e._$litDirective$;return(null==l?void 0:l.constructor)!==d&&(null===(r=null==l?void 0:l._$AO)||void 0===r||r.call(l,!1),void 0===d?l=void 0:(l=new d(t),l._$AT(t,i,s)),void 0!==s?(null!==(o=(a=i)._$Co)&&void 0!==o?o:a._$Co=[])[s]=l:i._$Cl=l),void 0!==l&&(e=Pi(t,l._$AS(t,e.values),l,s)),e}let Li=class{constructor(t,e){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){var e;const{el:{content:i},parts:s}=this._$AD,n=(null!==(e=null==t?void 0:t.creationScope)&&void 0!==e?e:fi).importNode(i,!0);Oi.currentNode=n;let r=Oi.nextNode(),o=0,a=0,l=s[0];for(;void 0!==l;){if(o===l.index){let e;2===l.type?e=new Mi(r,r.nextSibling,this,t):1===l.type?e=new l.ctor(r,l.name,l.strings,this,t):6===l.type&&(e=new Fi(r,this,t)),this._$AV.push(e),l=s[++a]}o!==(null==l?void 0:l.index)&&(r=Oi.nextNode(),o++)}return Oi.currentNode=fi,n}v(t){let e=0;for(const i of this._$AV)void 0!==i&&(void 0!==i.strings?(i._$AI(t,i,e),e+=i.strings.length-2):i._$AI(t[e])),e++}},Mi=class t{constructor(t,e,i,s){var n;this.type=2,this._$AH=Ti,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=i,this.options=s,this._$Cp=null===(n=null==s?void 0:s.isConnected)||void 0===n||n}get _$AU(){var t,e;return null!==(e=null===(t=this._$AM)||void 0===t?void 0:t._$AU)&&void 0!==e?e:this._$Cp}get parentNode(){let t=this._$AA.parentNode;const e=this._$AM;return void 0!==e&&11===(null==t?void 0:t.nodeType)&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=Pi(this,t,e),vi(t)?t===Ti||null==t||""===t?(this._$AH!==Ti&&this._$AR(),this._$AH=Ti):t!==this._$AH&&t!==Ci&&this._(t):void 0!==t._$litType$?this.g(t):void 0!==t.nodeType?this.$(t):(t=>_i(t)||"function"==typeof(null==t?void 0:t[Symbol.iterator]))(t)?this.T(t):this._(t)}k(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}$(t){this._$AH!==t&&(this._$AR(),this._$AH=this.k(t))}_(t){this._$AH!==Ti&&vi(this._$AH)?this._$AA.nextSibling.data=t:this.$(fi.createTextNode(t)),this._$AH=t}g(t){var e;const{values:i,_$litType$:s}=t,n="number"==typeof s?this._$AC(t):(void 0===s.el&&(s.el=Ri.createElement(ki(s.h,s.h[0]),this.options)),s);if((null===(e=this._$AH)||void 0===e?void 0:e._$AD)===n)this._$AH.v(i);else{const t=new Li(n,this),e=t.u(this.options);t.v(i),this.$(e),this._$AH=t}}_$AC(t){let e=Ii.get(t.strings);return void 0===e&&Ii.set(t.strings,e=new Ri(t)),e}T(e){_i(this._$AH)||(this._$AH=[],this._$AR());const i=this._$AH;let s,n=0;for(const r of e)n===i.length?i.push(s=new t(this.k(gi()),this.k(gi()),this,this.options)):s=i[n],s._$AI(r),n++;n<i.length&&(this._$AR(s&&s._$AB.nextSibling,n),i.length=n)}_$AR(t=this._$AA.nextSibling,e){var i;for(null===(i=this._$AP)||void 0===i||i.call(this,!1,!0,e);t&&t!==this._$AB;){const e=t.nextSibling;t.remove(),t=e}}setConnected(t){var e;void 0===this._$AM&&(this._$Cp=t,null===(e=this._$AP)||void 0===e||e.call(this,t))}},Ni=class{constructor(t,e,i,s,n){this.type=1,this._$AH=Ti,this._$AN=void 0,this.element=t,this.name=e,this._$AM=s,this.options=n,i.length>2||""!==i[0]||""!==i[1]?(this._$AH=Array(i.length-1).fill(new String),this.strings=i):this._$AH=Ti}get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}_$AI(t,e=this,i,s){const n=this.strings;let r=!1;if(void 0===n)t=Pi(this,t,e,0),r=!vi(t)||t!==this._$AH&&t!==Ci,r&&(this._$AH=t);else{const s=t;let o,a;for(t=n[0],o=0;o<n.length-1;o++)a=Pi(this,s[i+o],e,o),a===Ci&&(a=this._$AH[o]),r||(r=!vi(a)||a!==this._$AH[o]),a===Ti?t=Ti:t!==Ti&&(t+=(null!=a?a:"")+n[o+1]),this._$AH[o]=a}r&&!s&&this.j(t)}j(t){t===Ti?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,null!=t?t:"")}},Di=class extends Ni{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===Ti?void 0:t}};const Hi=di?di.emptyScript:"";let Ui=class extends Ni{constructor(){super(...arguments),this.type=4}j(t){t&&t!==Ti?this.element.setAttribute(this.name,Hi):this.element.removeAttribute(this.name)}},zi=class extends Ni{constructor(t,e,i,s,n){super(t,e,i,s,n),this.type=5}_$AI(t,e=this){var i;if((t=null!==(i=Pi(this,t,e,0))&&void 0!==i?i:Ti)===Ci)return;const s=this._$AH,n=t===Ti&&s!==Ti||t.capture!==s.capture||t.once!==s.once||t.passive!==s.passive,r=t!==Ti&&(s===Ti||n);n&&this.element.removeEventListener(this.name,this,s),r&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){var e,i;"function"==typeof this._$AH?this._$AH.call(null!==(i=null===(e=this.options)||void 0===e?void 0:e.host)&&void 0!==i?i:this.element,t):this._$AH.handleEvent(t)}},Fi=class{constructor(t,e,i){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=i}get _$AU(){return this._$AM._$AU}_$AI(t){Pi(this,t)}};const Bi=li.litHtmlPolyfillSupport;null==Bi||Bi(Ri,Mi),(null!==(ai=li.litHtmlVersions)&&void 0!==ai?ai:li.litHtmlVersions=[]).push("2.8.0");
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
var Vi,ji;let Wi=class extends oi{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){var t,e;const i=super.createRenderRoot();return null!==(t=(e=this.renderOptions).renderBefore)&&void 0!==t||(e.renderBefore=i.firstChild),i}update(t){const e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=((t,e,i)=>{var s,n;const r=null!==(s=null==i?void 0:i.renderBefore)&&void 0!==s?s:e;let o=r._$litPart$;if(void 0===o){const t=null!==(n=null==i?void 0:i.renderBefore)&&void 0!==n?n:null;r._$litPart$=o=new Mi(e.insertBefore(gi(),t),t,void 0,null!=i?i:{})}return o._$AI(t),o})(e,this.renderRoot,this.renderOptions)}connectedCallback(){var t;super.connectedCallback(),null===(t=this._$Do)||void 0===t||t.setConnected(!0)}disconnectedCallback(){var t;super.disconnectedCallback(),null===(t=this._$Do)||void 0===t||t.setConnected(!1)}render(){return Ci}};Wi.finalized=!0,Wi._$litElement$=!0,null===(Vi=globalThis.litElementHydrateSupport)||void 0===Vi||Vi.call(globalThis,{LitElement:Wi});const qi=globalThis.litElementPolyfillSupport;null==qi||qi({LitElement:Wi}),(null!==(ji=globalThis.litElementVersions)&&void 0!==ji?ji:globalThis.litElementVersions=[]).push("3.3.3");
/**
     * @license
     * Copyright 2018 Google LLC
     * SPDX-License-Identifier: Apache-2.0
     */
const Yi=t=>t.nodeType===Node.ELEMENT_NODE;function Xi(t){return{addClass:e=>{t.classList.add(e)},removeClass:e=>{t.classList.remove(e)},hasClass:e=>t.classList.contains(e)}}const Gi=()=>{},Ki={get passive(){return!1}};document.addEventListener("x",Gi,Ki),document.removeEventListener("x",Gi);const Ji=(t=window.document)=>{let e=t.activeElement;const i=[];if(!e)return i;for(;e&&(i.push(e),e.shadowRoot);)e=e.shadowRoot.activeElement;return i},Zi=t=>{const e=Ji();if(!e.length)return!1;const i=e[e.length-1],s=new Event("check-if-focused",{bubbles:!0,composed:!0});let n=[];const r=t=>{n=t.composedPath()};return document.body.addEventListener("check-if-focused",r),i.dispatchEvent(s),document.body.removeEventListener("check-if-focused",r),-1!==n.indexOf(t)};
/**
     * @license
     * Copyright 2018 Google LLC
     * SPDX-License-Identifier: Apache-2.0
     */
class Qi extends Wi{click(){if(this.mdcRoot)return this.mdcRoot.focus(),void this.mdcRoot.click();super.click()}createFoundation(){void 0!==this.mdcFoundation&&this.mdcFoundation.destroy(),this.mdcFoundationClass&&(this.mdcFoundation=new this.mdcFoundationClass(this.createAdapter()),this.mdcFoundation.init())}firstUpdated(){this.createFoundation()}}
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */const ts=(t,e)=>"method"===e.kind&&e.descriptor&&!("value"in e.descriptor)?{...e,finisher(i){i.createProperty(e.key,t)}}:{kind:"field",key:Symbol(),placement:"own",descriptor:{},originalKey:e.key,initializer(){"function"==typeof e.initializer&&(this[e.key]=e.initializer.call(this))},finisher(i){i.createProperty(e.key,t)}};
/**
     * @license
     * Copyright 2021 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
var es,is,ss;null===(es=window.HTMLSlotElement)||void 0===es||es.prototype.assignedElements;const ns=null!==(ss=null===(is=window.ShadyDOM)||void 0===is?void 0:is.inUse)&&void 0!==ss&&ss;class rs extends Qi{constructor(){super(...arguments),this.disabled=!1,this.containingForm=null,this.formDataListener=t=>{this.disabled||this.setFormData(t.formData)}}findFormElement(){if(!this.shadowRoot||ns)return null;const t=this.getRootNode().querySelectorAll("form");for(const e of Array.from(t))if(e.contains(this))return e;return null}connectedCallback(){var t;super.connectedCallback(),this.containingForm=this.findFormElement(),null===(t=this.containingForm)||void 0===t||t.addEventListener("formdata",this.formDataListener)}disconnectedCallback(){var t;super.disconnectedCallback(),null===(t=this.containingForm)||void 0===t||t.removeEventListener("formdata",this.formDataListener),this.containingForm=null}click(){this.formElement&&!this.disabled&&(this.formElement.focus(),this.formElement.click())}firstUpdated(){super.firstUpdated(),this.shadowRoot&&this.mdcRoot.addEventListener("change",t=>{this.dispatchEvent(new Event("change",t))})}}rs.shadowRootOptions={mode:"open",delegatesFocus:!0},n([function(t){return(e,i)=>void 0!==i?((t,e,i)=>{e.constructor.createProperty(i,t)})(t,e,i):ts(t,e)}({type:Boolean})],rs.prototype,"disabled",void 0);
/**
     * @license
     * Copyright 2018 Google LLC
     * SPDX-License-Identifier: Apache-2.0
     */
const os=t=>(e,i)=>{if(e.constructor._observers){if(!e.constructor.hasOwnProperty("_observers")){const t=e.constructor._observers;e.constructor._observers=new Map,t.forEach((t,i)=>e.constructor._observers.set(i,t))}}else{e.constructor._observers=new Map;const t=e.updated;e.updated=function(e){t.call(this,e),e.forEach((t,e)=>{const i=this.constructor._observers.get(e);void 0!==i&&i.call(this,this[e],t)})}}e.constructor._observers.set(i,t)},as=window,ls=as.ShadowRoot&&(void 0===as.ShadyCSS||as.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,ds=Symbol(),cs=new WeakMap;
/**
     * @license
     * Copyright 2019 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */let hs=class{constructor(t,e,i){if(this._$cssResult$=!0,i!==ds)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o;const e=this.t;if(ls&&void 0===t){const i=void 0!==e&&1===e.length;i&&(t=cs.get(e)),void 0===t&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),i&&cs.set(e,t))}return t}toString(){return this.cssText}};const ps=ls?t=>t:t=>t instanceof CSSStyleSheet?(t=>{let e="";for(const i of t.cssRules)e+=i.cssText;return(t=>new hs("string"==typeof t?t:t+"",void 0,ds))(e)})(t):t;
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */var us;const ms=window,fs=ms.trustedTypes,gs=fs?fs.emptyScript:"",vs=ms.reactiveElementPolyfillSupport,_s={toAttribute(t,e){switch(e){case Boolean:t=t?gs:null;break;case Object:case Array:t=null==t?t:JSON.stringify(t)}return t},fromAttribute(t,e){let i=t;switch(e){case Boolean:i=null!==t;break;case Number:i=null===t?null:Number(t);break;case Object:case Array:try{i=JSON.parse(t)}catch(t){i=null}}return i}},bs=(t,e)=>e!==t&&(e==e||t==t),ys={attribute:!0,type:String,converter:_s,reflect:!1,hasChanged:bs},xs="finalized";let $s=class extends HTMLElement{constructor(){super(),this._$Ei=new Map,this.isUpdatePending=!1,this.hasUpdated=!1,this._$El=null,this._$Eu()}static addInitializer(t){var e;this.finalize(),(null!==(e=this.h)&&void 0!==e?e:this.h=[]).push(t)}static get observedAttributes(){this.finalize();const t=[];return this.elementProperties.forEach((e,i)=>{const s=this._$Ep(i,e);void 0!==s&&(this._$Ev.set(s,i),t.push(s))}),t}static createProperty(t,e=ys){if(e.state&&(e.attribute=!1),this.finalize(),this.elementProperties.set(t,e),!e.noAccessor&&!this.prototype.hasOwnProperty(t)){const i="symbol"==typeof t?Symbol():"__"+t,s=this.getPropertyDescriptor(t,i,e);void 0!==s&&Object.defineProperty(this.prototype,t,s)}}static getPropertyDescriptor(t,e,i){return{get(){return this[e]},set(s){const n=this[t];this[e]=s,this.requestUpdate(t,n,i)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)||ys}static finalize(){if(this.hasOwnProperty(xs))return!1;this[xs]=!0;const t=Object.getPrototypeOf(this);if(t.finalize(),void 0!==t.h&&(this.h=[...t.h]),this.elementProperties=new Map(t.elementProperties),this._$Ev=new Map,this.hasOwnProperty("properties")){const t=this.properties,e=[...Object.getOwnPropertyNames(t),...Object.getOwnPropertySymbols(t)];for(const i of e)this.createProperty(i,t[i])}return this.elementStyles=this.finalizeStyles(this.styles),!0}static finalizeStyles(t){const e=[];if(Array.isArray(t)){const i=new Set(t.flat(1/0).reverse());for(const t of i)e.unshift(ps(t))}else void 0!==t&&e.push(ps(t));return e}static _$Ep(t,e){const i=e.attribute;return!1===i?void 0:"string"==typeof i?i:"string"==typeof t?t.toLowerCase():void 0}_$Eu(){var t;this._$E_=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$Eg(),this.requestUpdate(),null===(t=this.constructor.h)||void 0===t||t.forEach(t=>t(this))}addController(t){var e,i;(null!==(e=this._$ES)&&void 0!==e?e:this._$ES=[]).push(t),void 0!==this.renderRoot&&this.isConnected&&(null===(i=t.hostConnected)||void 0===i||i.call(t))}removeController(t){var e;null===(e=this._$ES)||void 0===e||e.splice(this._$ES.indexOf(t)>>>0,1)}_$Eg(){this.constructor.elementProperties.forEach((t,e)=>{this.hasOwnProperty(e)&&(this._$Ei.set(e,this[e]),delete this[e])})}createRenderRoot(){var t;const e=null!==(t=this.shadowRoot)&&void 0!==t?t:this.attachShadow(this.constructor.shadowRootOptions);return((t,e)=>{ls?t.adoptedStyleSheets=e.map(t=>t instanceof CSSStyleSheet?t:t.styleSheet):e.forEach(e=>{const i=document.createElement("style"),s=as.litNonce;void 0!==s&&i.setAttribute("nonce",s),i.textContent=e.cssText,t.appendChild(i)})})(e,this.constructor.elementStyles),e}connectedCallback(){var t;void 0===this.renderRoot&&(this.renderRoot=this.createRenderRoot()),this.enableUpdating(!0),null===(t=this._$ES)||void 0===t||t.forEach(t=>{var e;return null===(e=t.hostConnected)||void 0===e?void 0:e.call(t)})}enableUpdating(t){}disconnectedCallback(){var t;null===(t=this._$ES)||void 0===t||t.forEach(t=>{var e;return null===(e=t.hostDisconnected)||void 0===e?void 0:e.call(t)})}attributeChangedCallback(t,e,i){this._$AK(t,i)}_$EO(t,e,i=ys){var s;const n=this.constructor._$Ep(t,i);if(void 0!==n&&!0===i.reflect){const r=(void 0!==(null===(s=i.converter)||void 0===s?void 0:s.toAttribute)?i.converter:_s).toAttribute(e,i.type);this._$El=t,null==r?this.removeAttribute(n):this.setAttribute(n,r),this._$El=null}}_$AK(t,e){var i;const s=this.constructor,n=s._$Ev.get(t);if(void 0!==n&&this._$El!==n){const t=s.getPropertyOptions(n),r="function"==typeof t.converter?{fromAttribute:t.converter}:void 0!==(null===(i=t.converter)||void 0===i?void 0:i.fromAttribute)?t.converter:_s;this._$El=n,this[n]=r.fromAttribute(e,t.type),this._$El=null}}requestUpdate(t,e,i){let s=!0;void 0!==t&&(((i=i||this.constructor.getPropertyOptions(t)).hasChanged||bs)(this[t],e)?(this._$AL.has(t)||this._$AL.set(t,e),!0===i.reflect&&this._$El!==t&&(void 0===this._$EC&&(this._$EC=new Map),this._$EC.set(t,i))):s=!1),!this.isUpdatePending&&s&&(this._$E_=this._$Ej())}async _$Ej(){this.isUpdatePending=!0;try{await this._$E_}catch(t){Promise.reject(t)}const t=this.scheduleUpdate();return null!=t&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){var t;if(!this.isUpdatePending)return;this.hasUpdated,this._$Ei&&(this._$Ei.forEach((t,e)=>this[e]=t),this._$Ei=void 0);let e=!1;const i=this._$AL;try{e=this.shouldUpdate(i),e?(this.willUpdate(i),null===(t=this._$ES)||void 0===t||t.forEach(t=>{var e;return null===(e=t.hostUpdate)||void 0===e?void 0:e.call(t)}),this.update(i)):this._$Ek()}catch(t){throw e=!1,this._$Ek(),t}e&&this._$AE(i)}willUpdate(t){}_$AE(t){var e;null===(e=this._$ES)||void 0===e||e.forEach(t=>{var e;return null===(e=t.hostUpdated)||void 0===e?void 0:e.call(t)}),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$Ek(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$E_}shouldUpdate(t){return!0}update(t){void 0!==this._$EC&&(this._$EC.forEach((t,e)=>this._$EO(e,this[e],t)),this._$EC=void 0),this._$Ek()}updated(t){}firstUpdated(t){}};
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
var ws;$s[xs]=!0,$s.elementProperties=new Map,$s.elementStyles=[],$s.shadowRootOptions={mode:"open"},null==vs||vs({ReactiveElement:$s}),(null!==(us=ms.reactiveElementVersions)&&void 0!==us?us:ms.reactiveElementVersions=[]).push("1.6.3");const As=window,Es=As.trustedTypes,Ss=Es?Es.createPolicy("lit-html",{createHTML:t=>t}):void 0,Cs="$lit$",Ts=`lit$${(Math.random()+"").slice(9)}$`,Is="?"+Ts,Os=`<${Is}>`,ks=document,Rs=()=>ks.createComment(""),Ps=t=>null===t||"object"!=typeof t&&"function"!=typeof t,Ls=Array.isArray,Ms="[ \t\n\f\r]",Ns=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,Ds=/-->/g,Hs=/>/g,Us=RegExp(`>|${Ms}(?:([^\\s"'>=/]+)(${Ms}*=${Ms}*(?:[^ \t\n\f\r"'\`<>=]|("|')|))|$)`,"g"),zs=/'/g,Fs=/"/g,Bs=/^(?:script|style|textarea|title)$/i,Vs=(t=>(e,...i)=>({_$litType$:t,strings:e,values:i}))(1),js=Symbol.for("lit-noChange"),Ws=Symbol.for("lit-nothing"),qs=new WeakMap,Ys=ks.createTreeWalker(ks,129,null,!1);function Xs(t,e){if(!Array.isArray(t)||!t.hasOwnProperty("raw"))throw Error("invalid template strings array");return void 0!==Ss?Ss.createHTML(e):e}let Gs=class t{constructor({strings:e,_$litType$:i},s){let n;this.parts=[];let r=0,o=0;const a=e.length-1,l=this.parts,[d,c]=((t,e)=>{const i=t.length-1,s=[];let n,r=2===e?"<svg>":"",o=Ns;for(let e=0;e<i;e++){const i=t[e];let a,l,d=-1,c=0;for(;c<i.length&&(o.lastIndex=c,l=o.exec(i),null!==l);)c=o.lastIndex,o===Ns?"!--"===l[1]?o=Ds:void 0!==l[1]?o=Hs:void 0!==l[2]?(Bs.test(l[2])&&(n=RegExp("</"+l[2],"g")),o=Us):void 0!==l[3]&&(o=Us):o===Us?">"===l[0]?(o=null!=n?n:Ns,d=-1):void 0===l[1]?d=-2:(d=o.lastIndex-l[2].length,a=l[1],o=void 0===l[3]?Us:'"'===l[3]?Fs:zs):o===Fs||o===zs?o=Us:o===Ds||o===Hs?o=Ns:(o=Us,n=void 0);const h=o===Us&&t[e+1].startsWith("/>")?" ":"";r+=o===Ns?i+Os:d>=0?(s.push(a),i.slice(0,d)+Cs+i.slice(d)+Ts+h):i+Ts+(-2===d?(s.push(void 0),e):h)}return[Xs(t,r+(t[i]||"<?>")+(2===e?"</svg>":"")),s]})(e,i);if(this.el=t.createElement(d,s),Ys.currentNode=this.el.content,2===i){const t=this.el.content,e=t.firstChild;e.remove(),t.append(...e.childNodes)}for(;null!==(n=Ys.nextNode())&&l.length<a;){if(1===n.nodeType){if(n.hasAttributes()){const t=[];for(const e of n.getAttributeNames())if(e.endsWith(Cs)||e.startsWith(Ts)){const i=c[o++];if(t.push(e),void 0!==i){const t=n.getAttribute(i.toLowerCase()+Cs).split(Ts),e=/([.?@])?(.*)/.exec(i);l.push({type:1,index:r,name:e[2],strings:t,ctor:"."===e[1]?tn:"?"===e[1]?sn:"@"===e[1]?nn:Qs})}else l.push({type:6,index:r})}for(const e of t)n.removeAttribute(e)}if(Bs.test(n.tagName)){const t=n.textContent.split(Ts),e=t.length-1;if(e>0){n.textContent=Es?Es.emptyScript:"";for(let i=0;i<e;i++)n.append(t[i],Rs()),Ys.nextNode(),l.push({type:2,index:++r});n.append(t[e],Rs())}}}else if(8===n.nodeType)if(n.data===Is)l.push({type:2,index:r});else{let t=-1;for(;-1!==(t=n.data.indexOf(Ts,t+1));)l.push({type:7,index:r}),t+=Ts.length-1}r++}}static createElement(t,e){const i=ks.createElement("template");return i.innerHTML=t,i}};function Ks(t,e,i=t,s){var n,r,o,a;if(e===js)return e;let l=void 0!==s?null===(n=i._$Co)||void 0===n?void 0:n[s]:i._$Cl;const d=Ps(e)?void 0:e._$litDirective$;return(null==l?void 0:l.constructor)!==d&&(null===(r=null==l?void 0:l._$AO)||void 0===r||r.call(l,!1),void 0===d?l=void 0:(l=new d(t),l._$AT(t,i,s)),void 0!==s?(null!==(o=(a=i)._$Co)&&void 0!==o?o:a._$Co=[])[s]=l:i._$Cl=l),void 0!==l&&(e=Ks(t,l._$AS(t,e.values),l,s)),e}let Js=class{constructor(t,e){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){var e;const{el:{content:i},parts:s}=this._$AD,n=(null!==(e=null==t?void 0:t.creationScope)&&void 0!==e?e:ks).importNode(i,!0);Ys.currentNode=n;let r=Ys.nextNode(),o=0,a=0,l=s[0];for(;void 0!==l;){if(o===l.index){let e;2===l.type?e=new Zs(r,r.nextSibling,this,t):1===l.type?e=new l.ctor(r,l.name,l.strings,this,t):6===l.type&&(e=new rn(r,this,t)),this._$AV.push(e),l=s[++a]}o!==(null==l?void 0:l.index)&&(r=Ys.nextNode(),o++)}return Ys.currentNode=ks,n}v(t){let e=0;for(const i of this._$AV)void 0!==i&&(void 0!==i.strings?(i._$AI(t,i,e),e+=i.strings.length-2):i._$AI(t[e])),e++}},Zs=class t{constructor(t,e,i,s){var n;this.type=2,this._$AH=Ws,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=i,this.options=s,this._$Cp=null===(n=null==s?void 0:s.isConnected)||void 0===n||n}get _$AU(){var t,e;return null!==(e=null===(t=this._$AM)||void 0===t?void 0:t._$AU)&&void 0!==e?e:this._$Cp}get parentNode(){let t=this._$AA.parentNode;const e=this._$AM;return void 0!==e&&11===(null==t?void 0:t.nodeType)&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=Ks(this,t,e),Ps(t)?t===Ws||null==t||""===t?(this._$AH!==Ws&&this._$AR(),this._$AH=Ws):t!==this._$AH&&t!==js&&this._(t):void 0!==t._$litType$?this.g(t):void 0!==t.nodeType?this.$(t):(t=>Ls(t)||"function"==typeof(null==t?void 0:t[Symbol.iterator]))(t)?this.T(t):this._(t)}k(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}$(t){this._$AH!==t&&(this._$AR(),this._$AH=this.k(t))}_(t){this._$AH!==Ws&&Ps(this._$AH)?this._$AA.nextSibling.data=t:this.$(ks.createTextNode(t)),this._$AH=t}g(t){var e;const{values:i,_$litType$:s}=t,n="number"==typeof s?this._$AC(t):(void 0===s.el&&(s.el=Gs.createElement(Xs(s.h,s.h[0]),this.options)),s);if((null===(e=this._$AH)||void 0===e?void 0:e._$AD)===n)this._$AH.v(i);else{const t=new Js(n,this),e=t.u(this.options);t.v(i),this.$(e),this._$AH=t}}_$AC(t){let e=qs.get(t.strings);return void 0===e&&qs.set(t.strings,e=new Gs(t)),e}T(e){Ls(this._$AH)||(this._$AH=[],this._$AR());const i=this._$AH;let s,n=0;for(const r of e)n===i.length?i.push(s=new t(this.k(Rs()),this.k(Rs()),this,this.options)):s=i[n],s._$AI(r),n++;n<i.length&&(this._$AR(s&&s._$AB.nextSibling,n),i.length=n)}_$AR(t=this._$AA.nextSibling,e){var i;for(null===(i=this._$AP)||void 0===i||i.call(this,!1,!0,e);t&&t!==this._$AB;){const e=t.nextSibling;t.remove(),t=e}}setConnected(t){var e;void 0===this._$AM&&(this._$Cp=t,null===(e=this._$AP)||void 0===e||e.call(this,t))}},Qs=class{constructor(t,e,i,s,n){this.type=1,this._$AH=Ws,this._$AN=void 0,this.element=t,this.name=e,this._$AM=s,this.options=n,i.length>2||""!==i[0]||""!==i[1]?(this._$AH=Array(i.length-1).fill(new String),this.strings=i):this._$AH=Ws}get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}_$AI(t,e=this,i,s){const n=this.strings;let r=!1;if(void 0===n)t=Ks(this,t,e,0),r=!Ps(t)||t!==this._$AH&&t!==js,r&&(this._$AH=t);else{const s=t;let o,a;for(t=n[0],o=0;o<n.length-1;o++)a=Ks(this,s[i+o],e,o),a===js&&(a=this._$AH[o]),r||(r=!Ps(a)||a!==this._$AH[o]),a===Ws?t=Ws:t!==Ws&&(t+=(null!=a?a:"")+n[o+1]),this._$AH[o]=a}r&&!s&&this.j(t)}j(t){t===Ws?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,null!=t?t:"")}},tn=class extends Qs{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===Ws?void 0:t}};const en=Es?Es.emptyScript:"";let sn=class extends Qs{constructor(){super(...arguments),this.type=4}j(t){t&&t!==Ws?this.element.setAttribute(this.name,en):this.element.removeAttribute(this.name)}},nn=class extends Qs{constructor(t,e,i,s,n){super(t,e,i,s,n),this.type=5}_$AI(t,e=this){var i;if((t=null!==(i=Ks(this,t,e,0))&&void 0!==i?i:Ws)===js)return;const s=this._$AH,n=t===Ws&&s!==Ws||t.capture!==s.capture||t.once!==s.once||t.passive!==s.passive,r=t!==Ws&&(s===Ws||n);n&&this.element.removeEventListener(this.name,this,s),r&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){var e,i;"function"==typeof this._$AH?this._$AH.call(null!==(i=null===(e=this.options)||void 0===e?void 0:e.host)&&void 0!==i?i:this.element,t):this._$AH.handleEvent(t)}},rn=class{constructor(t,e,i){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=i}get _$AU(){return this._$AM._$AU}_$AI(t){Ks(this,t)}};const on=As.litHtmlPolyfillSupport;null==on||on(Gs,Zs),(null!==(ws=As.litHtmlVersions)&&void 0!==ws?ws:As.litHtmlVersions=[]).push("2.8.0");
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
var an,ln;let dn=class extends $s{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){var t,e;const i=super.createRenderRoot();return null!==(t=(e=this.renderOptions).renderBefore)&&void 0!==t||(e.renderBefore=i.firstChild),i}update(t){const e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=((t,e,i)=>{var s,n;const r=null!==(s=null==i?void 0:i.renderBefore)&&void 0!==s?s:e;let o=r._$litPart$;if(void 0===o){const t=null!==(n=null==i?void 0:i.renderBefore)&&void 0!==n?n:null;r._$litPart$=o=new Zs(e.insertBefore(Rs(),t),t,void 0,null!=i?i:{})}return o._$AI(t),o})(e,this.renderRoot,this.renderOptions)}connectedCallback(){var t;super.connectedCallback(),null===(t=this._$Do)||void 0===t||t.setConnected(!0)}disconnectedCallback(){var t;super.disconnectedCallback(),null===(t=this._$Do)||void 0===t||t.setConnected(!1)}render(){return js}};dn.finalized=!0,dn._$litElement$=!0,null===(an=globalThis.litElementHydrateSupport)||void 0===an||an.call(globalThis,{LitElement:dn});const cn=globalThis.litElementPolyfillSupport;null==cn||cn({LitElement:dn}),(null!==(ln=globalThis.litElementVersions)&&void 0!==ln?ln:globalThis.litElementVersions=[]).push("3.3.3");
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
const hn=(t,e)=>"method"===e.kind&&e.descriptor&&!("value"in e.descriptor)?{...e,finisher(i){i.createProperty(e.key,t)}}:{kind:"field",key:Symbol(),placement:"own",descriptor:{},originalKey:e.key,initializer(){"function"==typeof e.initializer&&(this[e.key]=e.initializer.call(this))},finisher(i){i.createProperty(e.key,t)}};function pn(t){return(e,i)=>void 0!==i?((t,e,i)=>{e.constructor.createProperty(i,t)})(t,e,i):hn(t,e)}
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */const un=({finisher:t,descriptor:e})=>(i,s)=>{var n;if(void 0===s){const s=null!==(n=i.originalKey)&&void 0!==n?n:i.key,r=null!=e?{kind:"method",placement:"prototype",key:s,descriptor:e(i.key)}:{...i,key:s};return null!=t&&(r.finisher=function(e){t(e,s)}),r}{const n=i.constructor;void 0!==e&&Object.defineProperty(i,s,e(s)),null==t||t(n,s)}};
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */function mn(t,e){return un({descriptor:e=>{const i={get(){var e,i;return null!==(i=null===(e=this.renderRoot)||void 0===e?void 0:e.querySelector(t))&&void 0!==i?i:null},enumerable:!0,configurable:!0};return i}})}
/**
     * @license
     * Copyright 2021 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */var fn;const gn=null!=(null===(fn=window.HTMLSlotElement)||void 0===fn?void 0:fn.prototype.assignedElements)?(t,e)=>t.assignedElements(e):(t,e)=>t.assignedNodes(e).filter(t=>t.nodeType===Node.ELEMENT_NODE);
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
const vn=1;let _n=class{constructor(t){}get _$AU(){return this._$AM._$AU}_$AT(t,e,i){this._$Ct=t,this._$AM=e,this._$Ci=i}_$AS(t,e){return this.update(t,e)}update(t,e){return this.render(...e)}};
/**
     * @license
     * Copyright 2018 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */const bn=(t=>(...e)=>({_$litDirective$:t,values:e}))(class extends _n{constructor(t){var e;if(super(t),t.type!==vn||"class"!==t.name||(null===(e=t.strings)||void 0===e?void 0:e.length)>2)throw Error("`classMap()` can only be used in the `class` attribute and must be the only part in the attribute.")}render(t){return" "+Object.keys(t).filter(e=>t[e]).join(" ")+" "}update(t,[e]){var i,s;if(void 0===this.it){this.it=new Set,void 0!==t.strings&&(this.nt=new Set(t.strings.join(" ").split(/\s/).filter(t=>""!==t)));for(const t in e)e[t]&&!(null===(i=this.nt)||void 0===i?void 0:i.has(t))&&this.it.add(t);return this.render(e)}const n=t.element.classList;this.it.forEach(t=>{t in e||(n.remove(t),this.it.delete(t))});for(const t in e){const i=!!e[t];i===this.it.has(t)||(null===(s=this.nt)||void 0===s?void 0:s.has(t))||(i?(n.add(t),this.it.add(t)):(n.remove(t),this.it.delete(t)))}return js}});
/**
     * @license
     * Copyright 2018 Google LLC
     * SPDX-License-Identifier: Apache-2.0
     */class yn extends Qi{constructor(){super(...arguments),this.alignEnd=!1,this.spaceBetween=!1,this.nowrap=!1,this.label="",this.mdcFoundationClass=je}createAdapter(){return{registerInteractionHandler:(t,e)=>{this.labelEl.addEventListener(t,e)},deregisterInteractionHandler:(t,e)=>{this.labelEl.removeEventListener(t,e)},activateInputRipple:async()=>{const t=this.input;if(t instanceof rs){const e=await t.ripple;e&&e.startPress()}},deactivateInputRipple:async()=>{const t=this.input;if(t instanceof rs){const e=await t.ripple;e&&e.endPress()}}}}get input(){var t,e;return null!==(e=null===(t=this.slottedInputs)||void 0===t?void 0:t[0])&&void 0!==e?e:null}render(){const t={"mdc-form-field--align-end":this.alignEnd,"mdc-form-field--space-between":this.spaceBetween,"mdc-form-field--nowrap":this.nowrap};return Vs`
      <div class="mdc-form-field ${bn(t)}">
        <slot></slot>
        <label class="mdc-label"
               @click="${this._labelClick}">${this.label}</label>
      </div>`}click(){this._labelClick()}_labelClick(){const t=this.input;t&&(t.focus(),t.click())}}n([pn({type:Boolean})],yn.prototype,"alignEnd",void 0),n([pn({type:Boolean})],yn.prototype,"spaceBetween",void 0),n([pn({type:Boolean})],yn.prototype,"nowrap",void 0),n([pn({type:String}),os(async function(t){var e;null===(e=this.input)||void 0===e||e.setAttribute("aria-label",t)})],yn.prototype,"label",void 0),n([mn(".mdc-form-field")],yn.prototype,"mdcRoot",void 0),n([
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
function(t,e,i){let s;return s={flatten:e},i?function(t){const{slot:e,selector:i}=null!=t?t:{};return un({descriptor:s=>({get(){var s;const n="slot"+(e?`[name=${e}]`:":not([name])"),r=null===(s=this.renderRoot)||void 0===s?void 0:s.querySelector(n),o=null!=r?gn(r,t):[];return i?o.filter(t=>t.matches(i)):o},enumerable:!0,configurable:!0})})}({slot:t,flatten:e,selector:i}):un({descriptor:t=>({get(){var t,e;const i=null===(t=this.renderRoot)||void 0===t?void 0:t.querySelector("slot:not([name])");return null!==(e=null==i?void 0:i.assignedNodes(s))&&void 0!==e?e:[]},enumerable:!0,configurable:!0})})}("",!0,"*")],yn.prototype,"slottedInputs",void 0),n([mn("label")],yn.prototype,"labelEl",void 0);
/**
     * @license
     * Copyright 2021 Google LLC
     * SPDX-LIcense-Identifier: Apache-2.0
     */
const xn=((t,...e)=>{const i=1===t.length?t[0]:e.reduce((e,i,s)=>e+(t=>{if(!0===t._$cssResult$)return t.cssText;if("number"==typeof t)return t;throw Error("Value passed to 'css' function must be a 'css' function result: "+t+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+t[s+1],t[0]);return new hs(i,t,ds)})`.mdc-form-field{-moz-osx-font-smoothing:grayscale;-webkit-font-smoothing:antialiased;font-family:Roboto, sans-serif;font-family:var(--mdc-typography-body2-font-family, var(--mdc-typography-font-family, Roboto, sans-serif));font-size:0.875rem;font-size:var(--mdc-typography-body2-font-size, 0.875rem);line-height:1.25rem;line-height:var(--mdc-typography-body2-line-height, 1.25rem);font-weight:400;font-weight:var(--mdc-typography-body2-font-weight, 400);letter-spacing:0.0178571429em;letter-spacing:var(--mdc-typography-body2-letter-spacing, 0.0178571429em);text-decoration:inherit;text-decoration:var(--mdc-typography-body2-text-decoration, inherit);text-transform:inherit;text-transform:var(--mdc-typography-body2-text-transform, inherit);color:rgba(0, 0, 0, 0.87);color:var(--mdc-theme-text-primary-on-background, rgba(0, 0, 0, 0.87));display:inline-flex;align-items:center;vertical-align:middle}.mdc-form-field>label{margin-left:0;margin-right:auto;padding-left:4px;padding-right:0;order:0}[dir=rtl] .mdc-form-field>label,.mdc-form-field>label[dir=rtl]{margin-left:auto;margin-right:0}[dir=rtl] .mdc-form-field>label,.mdc-form-field>label[dir=rtl]{padding-left:0;padding-right:4px}.mdc-form-field--nowrap>label{text-overflow:ellipsis;overflow:hidden;white-space:nowrap}.mdc-form-field--align-end>label{margin-left:auto;margin-right:0;padding-left:0;padding-right:4px;order:-1}[dir=rtl] .mdc-form-field--align-end>label,.mdc-form-field--align-end>label[dir=rtl]{margin-left:0;margin-right:auto}[dir=rtl] .mdc-form-field--align-end>label,.mdc-form-field--align-end>label[dir=rtl]{padding-left:4px;padding-right:0}.mdc-form-field--space-between{justify-content:space-between}.mdc-form-field--space-between>label{margin:0}[dir=rtl] .mdc-form-field--space-between>label,.mdc-form-field--space-between>label[dir=rtl]{margin:0}:host{display:inline-flex}.mdc-form-field{width:100%}::slotted(*){-moz-osx-font-smoothing:grayscale;-webkit-font-smoothing:antialiased;font-family:Roboto, sans-serif;font-family:var(--mdc-typography-body2-font-family, var(--mdc-typography-font-family, Roboto, sans-serif));font-size:0.875rem;font-size:var(--mdc-typography-body2-font-size, 0.875rem);line-height:1.25rem;line-height:var(--mdc-typography-body2-line-height, 1.25rem);font-weight:400;font-weight:var(--mdc-typography-body2-font-weight, 400);letter-spacing:0.0178571429em;letter-spacing:var(--mdc-typography-body2-letter-spacing, 0.0178571429em);text-decoration:inherit;text-decoration:var(--mdc-typography-body2-text-decoration, inherit);text-transform:inherit;text-transform:var(--mdc-typography-body2-text-transform, inherit);color:rgba(0, 0, 0, 0.87);color:var(--mdc-theme-text-primary-on-background, rgba(0, 0, 0, 0.87))}::slotted(mwc-switch){margin-right:10px}[dir=rtl] ::slotted(mwc-switch),::slotted(mwc-switch[dir=rtl]){margin-left:10px}`,$n={"mwc-formfield":class extends yn{static get styles(){return xn}}};
/**
     * @license
     * Copyright 2020 Google Inc.
     *
     * Permission is hereby granted, free of charge, to any person obtaining a copy
     * of this software and associated documentation files (the "Software"), to deal
     * in the Software without restriction, including without limitation the rights
     * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
     * copies of the Software, and to permit persons to whom the Software is
     * furnished to do so, subject to the following conditions:
     *
     * The above copyright notice and this permission notice shall be included in
     * all copies or substantial portions of the Software.
     *
     * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
     * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
     * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
     * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
     * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
     * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
     * THE SOFTWARE.
     */
var wn="Unknown",An="Backspace",En="Enter",Sn="Spacebar",Cn="PageUp",Tn="PageDown",In="End",On="Home",kn="ArrowLeft",Rn="ArrowUp",Pn="ArrowRight",Ln="ArrowDown",Mn="Delete",Nn="Escape",Dn="Tab",Hn=new Set;Hn.add(An),Hn.add(En),Hn.add(Sn),Hn.add(Cn),Hn.add(Tn),Hn.add(In),Hn.add(On),Hn.add(kn),Hn.add(Rn),Hn.add(Pn),Hn.add(Ln),Hn.add(Mn),Hn.add(Nn),Hn.add(Dn);var Un=8,zn=13,Fn=32,Bn=33,Vn=34,jn=35,Wn=36,qn=37,Yn=38,Xn=39,Gn=40,Kn=46,Jn=27,Zn=9,Qn=new Map;Qn.set(Un,An),Qn.set(zn,En),Qn.set(Fn,Sn),Qn.set(Bn,Cn),Qn.set(Vn,Tn),Qn.set(jn,In),Qn.set(Wn,On),Qn.set(qn,kn),Qn.set(Yn,Rn),Qn.set(Xn,Pn),Qn.set(Gn,Ln),Qn.set(Kn,Mn),Qn.set(Jn,Nn),Qn.set(Zn,Dn);var tr=new Set;function er(t){var e=t.key;if(Hn.has(e))return e;var i=Qn.get(t.keyCode);return i||wn}
/**
     * @license
     * Copyright 2020 Google Inc.
     *
     * Permission is hereby granted, free of charge, to any person obtaining a copy
     * of this software and associated documentation files (the "Software"), to deal
     * in the Software without restriction, including without limitation the rights
     * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
     * copies of the Software, and to permit persons to whom the Software is
     * furnished to do so, subject to the following conditions:
     *
     * The above copyright notice and this permission notice shall be included in
     * all copies or substantial portions of the Software.
     *
     * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
     * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
     * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
     * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
     * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
     * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
     * THE SOFTWARE.
     */tr.add(Cn),tr.add(Tn),tr.add(In),tr.add(On),tr.add(kn),tr.add(Rn),tr.add(Pn),tr.add(Ln);var ir="Unknown",sr="Backspace",nr="Enter",rr="Spacebar",or="PageUp",ar="PageDown",lr="End",dr="Home",cr="ArrowLeft",hr="ArrowUp",pr="ArrowRight",ur="ArrowDown",mr="Delete",fr="Escape",gr="Tab",vr=new Set;vr.add(sr),vr.add(nr),vr.add(rr),vr.add(or),vr.add(ar),vr.add(lr),vr.add(dr),vr.add(cr),vr.add(hr),vr.add(pr),vr.add(ur),vr.add(mr),vr.add(fr),vr.add(gr);var _r=8,br=13,yr=32,xr=33,$r=34,wr=35,Ar=36,Er=37,Sr=38,Cr=39,Tr=40,Ir=46,Or=27,kr=9,Rr=new Map;Rr.set(_r,sr),Rr.set(br,nr),Rr.set(yr,rr),Rr.set(xr,or),Rr.set($r,ar),Rr.set(wr,lr),Rr.set(Ar,dr),Rr.set(Er,cr),Rr.set(Sr,hr),Rr.set(Cr,pr),Rr.set(Tr,ur),Rr.set(Ir,mr),Rr.set(Or,fr),Rr.set(kr,gr);var Pr,Lr,Mr=new Set;function Nr(t){var e=t.key;if(vr.has(e))return e;var i=Rr.get(t.keyCode);return i||ir}
/**
     * @license
     * Copyright 2018 Google Inc.
     *
     * Permission is hereby granted, free of charge, to any person obtaining a copy
     * of this software and associated documentation files (the "Software"), to deal
     * in the Software without restriction, including without limitation the rights
     * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
     * copies of the Software, and to permit persons to whom the Software is
     * furnished to do so, subject to the following conditions:
     *
     * The above copyright notice and this permission notice shall be included in
     * all copies or substantial portions of the Software.
     *
     * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
     * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
     * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
     * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
     * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
     * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
     * THE SOFTWARE.
     */Mr.add(or),Mr.add(ar),Mr.add(lr),Mr.add(dr),Mr.add(cr),Mr.add(hr),Mr.add(pr),Mr.add(ur);var Dr="mdc-list-item--activated",Hr="mdc-list-item",Ur="mdc-list-item--disabled",zr="mdc-list-item--selected",Fr="mdc-list-item__text",Br="mdc-list-item__primary-text",Vr="mdc-list";(Pr={})[""+Dr]="mdc-list-item--activated",Pr[""+Hr]="mdc-list-item",Pr[""+Ur]="mdc-list-item--disabled",Pr[""+zr]="mdc-list-item--selected",Pr[""+Br]="mdc-list-item__primary-text",Pr[""+Vr]="mdc-list";var jr=((Lr={})[""+Dr]="mdc-deprecated-list-item--activated",Lr[""+Hr]="mdc-deprecated-list-item",Lr[""+Ur]="mdc-deprecated-list-item--disabled",Lr[""+zr]="mdc-deprecated-list-item--selected",Lr[""+Fr]="mdc-deprecated-list-item__text",Lr[""+Br]="mdc-deprecated-list-item__primary-text",Lr[""+Vr]="mdc-deprecated-list",Lr),Wr={ACTION_EVENT:"MDCList:action",SELECTION_CHANGE_EVENT:"MDCList:selectionChange",ARIA_CHECKED:"aria-checked",ARIA_CHECKED_CHECKBOX_SELECTOR:'[role="checkbox"][aria-checked="true"]',ARIA_CHECKED_RADIO_SELECTOR:'[role="radio"][aria-checked="true"]',ARIA_CURRENT:"aria-current",ARIA_DISABLED:"aria-disabled",ARIA_ORIENTATION:"aria-orientation",ARIA_ORIENTATION_HORIZONTAL:"horizontal",ARIA_ROLE_CHECKBOX_SELECTOR:'[role="checkbox"]',ARIA_SELECTED:"aria-selected",ARIA_INTERACTIVE_ROLES_SELECTOR:'[role="listbox"], [role="menu"]',ARIA_MULTI_SELECTABLE_SELECTOR:'[aria-multiselectable="true"]',CHECKBOX_RADIO_SELECTOR:'input[type="checkbox"], input[type="radio"]',CHECKBOX_SELECTOR:'input[type="checkbox"]',CHILD_ELEMENTS_TO_TOGGLE_TABINDEX:"\n    ."+Hr+" button:not(:disabled),\n    ."+Hr+" a,\n    ."+jr[Hr]+" button:not(:disabled),\n    ."+jr[Hr]+" a\n  ",DEPRECATED_SELECTOR:".mdc-deprecated-list",FOCUSABLE_CHILD_ELEMENTS:"\n    ."+Hr+" button:not(:disabled),\n    ."+Hr+" a,\n    ."+Hr+' input[type="radio"]:not(:disabled),\n    .'+Hr+' input[type="checkbox"]:not(:disabled),\n    .'+jr[Hr]+" button:not(:disabled),\n    ."+jr[Hr]+" a,\n    ."+jr[Hr]+' input[type="radio"]:not(:disabled),\n    .'+jr[Hr]+' input[type="checkbox"]:not(:disabled)\n  ',RADIO_SELECTOR:'input[type="radio"]',SELECTED_ITEM_SELECTOR:'[aria-selected="true"], [aria-current="true"]'},qr={UNSET_INDEX:-1,TYPEAHEAD_BUFFER_CLEAR_TIMEOUT_MS:300},Yr=["input","button","textarea","select"],Xr=function(t){var e=t.target;if(e){var i=(""+e.tagName).toLowerCase();-1===Yr.indexOf(i)&&t.preventDefault()}};function Gr(t,e){for(var i=new Map,s=0;s<t;s++){var n=e(s).trim();if(n){var r=n[0].toLowerCase();i.has(r)||i.set(r,[]),i.get(r).push({text:n.toLowerCase(),index:s})}}return i.forEach(function(t){t.sort(function(t,e){return t.index-e.index})}),i}function Kr(t,e){var i,s=t.nextChar,n=t.focusItemAtIndex,r=t.sortedIndexByFirstChar,o=t.focusedItemIndex,a=t.skipFocus,l=t.isItemAtIndexDisabled;return clearTimeout(e.bufferClearTimeout),e.bufferClearTimeout=setTimeout(function(){!function(t){t.typeaheadBuffer=""}(e)},qr.TYPEAHEAD_BUFFER_CLEAR_TIMEOUT_MS),e.typeaheadBuffer=e.typeaheadBuffer+s,i=1===e.typeaheadBuffer.length?function(t,e,i,s){var n=s.typeaheadBuffer[0],r=t.get(n);if(!r)return-1;if(n===s.currentFirstChar&&r[s.sortedIndexCursor].index===e){s.sortedIndexCursor=(s.sortedIndexCursor+1)%r.length;var o=r[s.sortedIndexCursor].index;if(!i(o))return o}s.currentFirstChar=n;var a,l=-1;for(a=0;a<r.length;a++)if(!i(r[a].index)){l=a;break}for(;a<r.length;a++)if(r[a].index>e&&!i(r[a].index)){l=a;break}if(-1!==l)return s.sortedIndexCursor=l,r[s.sortedIndexCursor].index;return-1}(r,o,l,e):function(t,e,i){var s=i.typeaheadBuffer[0],n=t.get(s);if(!n)return-1;var r=n[i.sortedIndexCursor];if(0===r.text.lastIndexOf(i.typeaheadBuffer,0)&&!e(r.index))return r.index;var o=(i.sortedIndexCursor+1)%n.length,a=-1;for(;o!==i.sortedIndexCursor;){var l=n[o],d=0===l.text.lastIndexOf(i.typeaheadBuffer,0),c=!e(l.index);if(d&&c){a=o;break}o=(o+1)%n.length}if(-1!==a)return i.sortedIndexCursor=a,n[i.sortedIndexCursor].index;return-1}(r,l,e),-1===i||a||n(i),i}function Jr(t){return t.typeaheadBuffer.length>0}
/**
     * @license
     * Copyright 2016 Google Inc.
     *
     * Permission is hereby granted, free of charge, to any person obtaining a copy
     * of this software and associated documentation files (the "Software"), to deal
     * in the Software without restriction, including without limitation the rights
     * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
     * copies of the Software, and to permit persons to whom the Software is
     * furnished to do so, subject to the following conditions:
     *
     * The above copyright notice and this permission notice shall be included in
     * all copies or substantial portions of the Software.
     *
     * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
     * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
     * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
     * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
     * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
     * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
     * THE SOFTWARE.
     */
var Zr=function(){function t(t){void 0===t&&(t={}),this.adapter=t}return Object.defineProperty(t,"cssClasses",{get:function(){return{}},enumerable:!1,configurable:!0}),Object.defineProperty(t,"strings",{get:function(){return{}},enumerable:!1,configurable:!0}),Object.defineProperty(t,"numbers",{get:function(){return{}},enumerable:!1,configurable:!0}),Object.defineProperty(t,"defaultAdapter",{get:function(){return{}},enumerable:!1,configurable:!0}),t.prototype.init=function(){},t.prototype.destroy=function(){},t}(),Qr={LABEL_FLOAT_ABOVE:"mdc-floating-label--float-above",LABEL_REQUIRED:"mdc-floating-label--required",LABEL_SHAKE:"mdc-floating-label--shake",ROOT:"mdc-floating-label"},to=function(t){function e(i){var n=t.call(this,s(s({},e.defaultAdapter),i))||this;return n.shakeAnimationEndHandler=function(){n.handleShakeAnimationEnd()},n}return i(e,t),Object.defineProperty(e,"cssClasses",{get:function(){return Qr},enumerable:!1,configurable:!0}),Object.defineProperty(e,"defaultAdapter",{get:function(){return{addClass:function(){},removeClass:function(){},getWidth:function(){return 0},registerInteractionHandler:function(){},deregisterInteractionHandler:function(){}}},enumerable:!1,configurable:!0}),e.prototype.init=function(){this.adapter.registerInteractionHandler("animationend",this.shakeAnimationEndHandler)},e.prototype.destroy=function(){this.adapter.deregisterInteractionHandler("animationend",this.shakeAnimationEndHandler)},e.prototype.getWidth=function(){return this.adapter.getWidth()},e.prototype.shake=function(t){var i=e.cssClasses.LABEL_SHAKE;t?this.adapter.addClass(i):this.adapter.removeClass(i)},e.prototype.float=function(t){var i=e.cssClasses,s=i.LABEL_FLOAT_ABOVE,n=i.LABEL_SHAKE;t?this.adapter.addClass(s):(this.adapter.removeClass(s),this.adapter.removeClass(n))},e.prototype.setRequired=function(t){var i=e.cssClasses.LABEL_REQUIRED;t?this.adapter.addClass(i):this.adapter.removeClass(i)},e.prototype.handleShakeAnimationEnd=function(){var t=e.cssClasses.LABEL_SHAKE;this.adapter.removeClass(t)},e}(Zr);
/**
     * @license
     * Copyright 2016 Google Inc.
     *
     * Permission is hereby granted, free of charge, to any person obtaining a copy
     * of this software and associated documentation files (the "Software"), to deal
     * in the Software without restriction, including without limitation the rights
     * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
     * copies of the Software, and to permit persons to whom the Software is
     * furnished to do so, subject to the following conditions:
     *
     * The above copyright notice and this permission notice shall be included in
     * all copies or substantial portions of the Software.
     *
     * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
     * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
     * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
     * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
     * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
     * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
     * THE SOFTWARE.
     */
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
const eo=1,io=3;let so=class{constructor(t){}get _$AU(){return this._$AM._$AU}_$AT(t,e,i){this._$Ct=t,this._$AM=e,this._$Ci=i}_$AS(t,e){return this.update(t,e)}update(t,e){return this.render(...e)}};
/**
     * @license
     * Copyright 2018 Google LLC
     * SPDX-License-Identifier: Apache-2.0
     */const no=(t=>(...e)=>({_$litDirective$:t,values:e}))(class extends so{constructor(t){switch(super(t),this.foundation=null,this.previousPart=null,t.type){case eo:case io:break;default:throw new Error("FloatingLabel directive only support attribute and property parts")}}update(t,[e]){if(t!==this.previousPart){this.foundation&&this.foundation.destroy(),this.previousPart=t;const e=t.element;e.classList.add("mdc-floating-label");const i=(t=>({addClass:e=>t.classList.add(e),removeClass:e=>t.classList.remove(e),getWidth:()=>t.scrollWidth,registerInteractionHandler:(e,i)=>{t.addEventListener(e,i)},deregisterInteractionHandler:(e,i)=>{t.removeEventListener(e,i)}}))(e);this.foundation=new to(i),this.foundation.init()}return this.render(e)}render(t){return this.foundation}});
/**
     * @license
     * Copyright 2016 Google Inc.
     *
     * Permission is hereby granted, free of charge, to any person obtaining a copy
     * of this software and associated documentation files (the "Software"), to deal
     * in the Software without restriction, including without limitation the rights
     * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
     * copies of the Software, and to permit persons to whom the Software is
     * furnished to do so, subject to the following conditions:
     *
     * The above copyright notice and this permission notice shall be included in
     * all copies or substantial portions of the Software.
     *
     * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
     * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
     * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
     * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
     * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
     * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
     * THE SOFTWARE.
     */var ro=function(){function t(t){void 0===t&&(t={}),this.adapter=t}return Object.defineProperty(t,"cssClasses",{get:function(){return{}},enumerable:!1,configurable:!0}),Object.defineProperty(t,"strings",{get:function(){return{}},enumerable:!1,configurable:!0}),Object.defineProperty(t,"numbers",{get:function(){return{}},enumerable:!1,configurable:!0}),Object.defineProperty(t,"defaultAdapter",{get:function(){return{}},enumerable:!1,configurable:!0}),t.prototype.init=function(){},t.prototype.destroy=function(){},t}(),oo={LINE_RIPPLE_ACTIVE:"mdc-line-ripple--active",LINE_RIPPLE_DEACTIVATING:"mdc-line-ripple--deactivating"},ao=function(t){function e(i){var n=t.call(this,s(s({},e.defaultAdapter),i))||this;return n.transitionEndHandler=function(t){n.handleTransitionEnd(t)},n}return i(e,t),Object.defineProperty(e,"cssClasses",{get:function(){return oo},enumerable:!1,configurable:!0}),Object.defineProperty(e,"defaultAdapter",{get:function(){return{addClass:function(){},removeClass:function(){},hasClass:function(){return!1},setStyle:function(){},registerEventHandler:function(){},deregisterEventHandler:function(){}}},enumerable:!1,configurable:!0}),e.prototype.init=function(){this.adapter.registerEventHandler("transitionend",this.transitionEndHandler)},e.prototype.destroy=function(){this.adapter.deregisterEventHandler("transitionend",this.transitionEndHandler)},e.prototype.activate=function(){this.adapter.removeClass(oo.LINE_RIPPLE_DEACTIVATING),this.adapter.addClass(oo.LINE_RIPPLE_ACTIVE)},e.prototype.setRippleCenter=function(t){this.adapter.setStyle("transform-origin",t+"px center")},e.prototype.deactivate=function(){this.adapter.addClass(oo.LINE_RIPPLE_DEACTIVATING)},e.prototype.handleTransitionEnd=function(t){var e=this.adapter.hasClass(oo.LINE_RIPPLE_DEACTIVATING);"opacity"===t.propertyName&&e&&(this.adapter.removeClass(oo.LINE_RIPPLE_ACTIVE),this.adapter.removeClass(oo.LINE_RIPPLE_DEACTIVATING))},e}(ro);
/**
     * @license
     * Copyright 2018 Google Inc.
     *
     * Permission is hereby granted, free of charge, to any person obtaining a copy
     * of this software and associated documentation files (the "Software"), to deal
     * in the Software without restriction, including without limitation the rights
     * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
     * copies of the Software, and to permit persons to whom the Software is
     * furnished to do so, subject to the following conditions:
     *
     * The above copyright notice and this permission notice shall be included in
     * all copies or substantial portions of the Software.
     *
     * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
     * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
     * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
     * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
     * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
     * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
     * THE SOFTWARE.
     */
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
const lo=1,co=3;let ho=class{constructor(t){}get _$AU(){return this._$AM._$AU}_$AT(t,e,i){this._$Ct=t,this._$AM=e,this._$Ci=i}_$AS(t,e){return this.update(t,e)}update(t,e){return this.render(...e)}};
/**
     * @license
     * Copyright 2019 Google LLC
     * SPDX-License-Identifier: Apache-2.0
     */const po=(t=>(...e)=>({_$litDirective$:t,values:e}))(class extends ho{constructor(t){switch(super(t),this.previousPart=null,this.foundation=null,t.type){case lo:case co:return;default:throw new Error("LineRipple only support attribute and property parts.")}}update(t,e){if(this.previousPart!==t){this.foundation&&this.foundation.destroy(),this.previousPart=t;const e=t.element;e.classList.add("mdc-line-ripple");const i=(t=>({addClass:e=>t.classList.add(e),removeClass:e=>t.classList.remove(e),hasClass:e=>t.classList.contains(e),setStyle:(e,i)=>t.style.setProperty(e,i),registerEventHandler:(e,i)=>{t.addEventListener(e,i)},deregisterEventHandler:(e,i)=>{t.removeEventListener(e,i)}}))(e);this.foundation=new ao(i),this.foundation.init()}return this.render()}render(){return this.foundation}});
/**
     * @license
     * Copyright 2016 Google Inc.
     *
     * Permission is hereby granted, free of charge, to any person obtaining a copy
     * of this software and associated documentation files (the "Software"), to deal
     * in the Software without restriction, including without limitation the rights
     * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
     * copies of the Software, and to permit persons to whom the Software is
     * furnished to do so, subject to the following conditions:
     *
     * The above copyright notice and this permission notice shall be included in
     * all copies or substantial portions of the Software.
     *
     * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
     * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
     * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
     * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
     * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
     * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
     * THE SOFTWARE.
     */var uo=function(){function t(t){void 0===t&&(t={}),this.adapter=t}return Object.defineProperty(t,"cssClasses",{get:function(){return{}},enumerable:!1,configurable:!0}),Object.defineProperty(t,"strings",{get:function(){return{}},enumerable:!1,configurable:!0}),Object.defineProperty(t,"numbers",{get:function(){return{}},enumerable:!1,configurable:!0}),Object.defineProperty(t,"defaultAdapter",{get:function(){return{}},enumerable:!1,configurable:!0}),t.prototype.init=function(){},t.prototype.destroy=function(){},t}(),mo="Unknown",fo="Backspace",go="Enter",vo="Spacebar",_o="PageUp",bo="PageDown",yo="End",xo="Home",$o="ArrowLeft",wo="ArrowUp",Ao="ArrowRight",Eo="ArrowDown",So="Delete",Co="Escape",To="Tab",Io=new Set;
/**
     * @license
     * Copyright 2020 Google Inc.
     *
     * Permission is hereby granted, free of charge, to any person obtaining a copy
     * of this software and associated documentation files (the "Software"), to deal
     * in the Software without restriction, including without limitation the rights
     * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
     * copies of the Software, and to permit persons to whom the Software is
     * furnished to do so, subject to the following conditions:
     *
     * The above copyright notice and this permission notice shall be included in
     * all copies or substantial portions of the Software.
     *
     * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
     * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
     * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
     * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
     * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
     * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
     * THE SOFTWARE.
     */Io.add(fo),Io.add(go),Io.add(vo),Io.add(_o),Io.add(bo),Io.add(yo),Io.add(xo),Io.add($o),Io.add(wo),Io.add(Ao),Io.add(Eo),Io.add(So),Io.add(Co),Io.add(To);var Oo=8,ko=13,Ro=32,Po=33,Lo=34,Mo=35,No=36,Do=37,Ho=38,Uo=39,zo=40,Fo=46,Bo=27,Vo=9,jo=new Map;jo.set(Oo,fo),jo.set(ko,go),jo.set(Ro,vo),jo.set(Po,_o),jo.set(Lo,bo),jo.set(Mo,yo),jo.set(No,xo),jo.set(Do,$o),jo.set(Ho,wo),jo.set(Uo,Ao),jo.set(zo,Eo),jo.set(Fo,So),jo.set(Bo,Co),jo.set(Vo,To);var Wo=new Set;function qo(t){var e=t.key;if(Io.has(e))return e;var i=jo.get(t.keyCode);return i||mo}
/**
     * @license
     * Copyright 2018 Google Inc.
     *
     * Permission is hereby granted, free of charge, to any person obtaining a copy
     * of this software and associated documentation files (the "Software"), to deal
     * in the Software without restriction, including without limitation the rights
     * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
     * copies of the Software, and to permit persons to whom the Software is
     * furnished to do so, subject to the following conditions:
     *
     * The above copyright notice and this permission notice shall be included in
     * all copies or substantial portions of the Software.
     *
     * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
     * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
     * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
     * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
     * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
     * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
     * THE SOFTWARE.
     */Wo.add(_o),Wo.add(bo),Wo.add(yo),Wo.add(xo),Wo.add($o),Wo.add(wo),Wo.add(Ao),Wo.add(Eo);var Yo,Xo,Go={ANCHOR:"mdc-menu-surface--anchor",ANIMATING_CLOSED:"mdc-menu-surface--animating-closed",ANIMATING_OPEN:"mdc-menu-surface--animating-open",FIXED:"mdc-menu-surface--fixed",IS_OPEN_BELOW:"mdc-menu-surface--is-open-below",OPEN:"mdc-menu-surface--open",ROOT:"mdc-menu-surface"},Ko={CLOSED_EVENT:"MDCMenuSurface:closed",CLOSING_EVENT:"MDCMenuSurface:closing",OPENED_EVENT:"MDCMenuSurface:opened",OPENING_EVENT:"MDCMenuSurface:opening",FOCUSABLE_ELEMENTS:["button:not(:disabled)",'[href]:not([aria-disabled="true"])',"input:not(:disabled)","select:not(:disabled)","textarea:not(:disabled)",'[tabindex]:not([tabindex="-1"]):not([aria-disabled="true"])'].join(", ")},Jo={TRANSITION_OPEN_DURATION:120,TRANSITION_CLOSE_DURATION:75,MARGIN_TO_EDGE:32,ANCHOR_TO_MENU_SURFACE_WIDTH_RATIO:.67,TOUCH_EVENT_WAIT_MS:30};!function(t){t[t.BOTTOM=1]="BOTTOM",t[t.CENTER=2]="CENTER",t[t.RIGHT=4]="RIGHT",t[t.FLIP_RTL=8]="FLIP_RTL"}(Yo||(Yo={})),function(t){t[t.TOP_LEFT=0]="TOP_LEFT",t[t.TOP_RIGHT=4]="TOP_RIGHT",t[t.BOTTOM_LEFT=1]="BOTTOM_LEFT",t[t.BOTTOM_RIGHT=5]="BOTTOM_RIGHT",t[t.TOP_START=8]="TOP_START",t[t.TOP_END=12]="TOP_END",t[t.BOTTOM_START=9]="BOTTOM_START",t[t.BOTTOM_END=13]="BOTTOM_END"}(Xo||(Xo={}));
/**
     * @license
     * Copyright 2016 Google Inc.
     *
     * Permission is hereby granted, free of charge, to any person obtaining a copy
     * of this software and associated documentation files (the "Software"), to deal
     * in the Software without restriction, including without limitation the rights
     * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
     * copies of the Software, and to permit persons to whom the Software is
     * furnished to do so, subject to the following conditions:
     *
     * The above copyright notice and this permission notice shall be included in
     * all copies or substantial portions of the Software.
     *
     * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
     * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
     * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
     * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
     * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
     * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
     * THE SOFTWARE.
     */
var Zo={ACTIVATED:"mdc-select--activated",DISABLED:"mdc-select--disabled",FOCUSED:"mdc-select--focused",INVALID:"mdc-select--invalid",MENU_INVALID:"mdc-select__menu--invalid",OUTLINED:"mdc-select--outlined",REQUIRED:"mdc-select--required",ROOT:"mdc-select",WITH_LEADING_ICON:"mdc-select--with-leading-icon"},Qo={ARIA_CONTROLS:"aria-controls",ARIA_DESCRIBEDBY:"aria-describedby",ARIA_SELECTED_ATTR:"aria-selected",CHANGE_EVENT:"MDCSelect:change",HIDDEN_INPUT_SELECTOR:'input[type="hidden"]',LABEL_SELECTOR:".mdc-floating-label",LEADING_ICON_SELECTOR:".mdc-select__icon",LINE_RIPPLE_SELECTOR:".mdc-line-ripple",MENU_SELECTOR:".mdc-select__menu",OUTLINE_SELECTOR:".mdc-notched-outline",SELECTED_TEXT_SELECTOR:".mdc-select__selected-text",SELECT_ANCHOR_SELECTOR:".mdc-select__anchor",VALUE_ATTR:"data-value"},ta={LABEL_SCALE:.75,UNSET_INDEX:-1,CLICK_DEBOUNCE_TIMEOUT_MS:330},ea=function(t){function e(i,n){void 0===n&&(n={});var r=t.call(this,s(s({},e.defaultAdapter),i))||this;return r.disabled=!1,r.isMenuOpen=!1,r.useDefaultValidation=!0,r.customValidity=!0,r.lastSelectedIndex=ta.UNSET_INDEX,r.clickDebounceTimeout=0,r.recentlyClicked=!1,r.leadingIcon=n.leadingIcon,r.helperText=n.helperText,r}return i(e,t),Object.defineProperty(e,"cssClasses",{get:function(){return Zo},enumerable:!1,configurable:!0}),Object.defineProperty(e,"numbers",{get:function(){return ta},enumerable:!1,configurable:!0}),Object.defineProperty(e,"strings",{get:function(){return Qo},enumerable:!1,configurable:!0}),Object.defineProperty(e,"defaultAdapter",{get:function(){return{addClass:function(){},removeClass:function(){},hasClass:function(){return!1},activateBottomLine:function(){},deactivateBottomLine:function(){},getSelectedIndex:function(){return-1},setSelectedIndex:function(){},hasLabel:function(){return!1},floatLabel:function(){},getLabelWidth:function(){return 0},setLabelRequired:function(){},hasOutline:function(){return!1},notchOutline:function(){},closeOutline:function(){},setRippleCenter:function(){},notifyChange:function(){},setSelectedText:function(){},isSelectAnchorFocused:function(){return!1},getSelectAnchorAttr:function(){return""},setSelectAnchorAttr:function(){},removeSelectAnchorAttr:function(){},addMenuClass:function(){},removeMenuClass:function(){},openMenu:function(){},closeMenu:function(){},getAnchorElement:function(){return null},setMenuAnchorElement:function(){},setMenuAnchorCorner:function(){},setMenuWrapFocus:function(){},focusMenuItemAtIndex:function(){},getMenuItemCount:function(){return 0},getMenuItemValues:function(){return[]},getMenuItemTextAtIndex:function(){return""},isTypeaheadInProgress:function(){return!1},typeaheadMatchItem:function(){return-1}}},enumerable:!1,configurable:!0}),e.prototype.getSelectedIndex=function(){return this.adapter.getSelectedIndex()},e.prototype.setSelectedIndex=function(t,e,i){void 0===e&&(e=!1),void 0===i&&(i=!1),t>=this.adapter.getMenuItemCount()||(t===ta.UNSET_INDEX?this.adapter.setSelectedText(""):this.adapter.setSelectedText(this.adapter.getMenuItemTextAtIndex(t).trim()),this.adapter.setSelectedIndex(t),e&&this.adapter.closeMenu(),i||this.lastSelectedIndex===t||this.handleChange(),this.lastSelectedIndex=t)},e.prototype.setValue=function(t,e){void 0===e&&(e=!1);var i=this.adapter.getMenuItemValues().indexOf(t);this.setSelectedIndex(i,!1,e)},e.prototype.getValue=function(){var t=this.adapter.getSelectedIndex(),e=this.adapter.getMenuItemValues();return t!==ta.UNSET_INDEX?e[t]:""},e.prototype.getDisabled=function(){return this.disabled},e.prototype.setDisabled=function(t){this.disabled=t,this.disabled?(this.adapter.addClass(Zo.DISABLED),this.adapter.closeMenu()):this.adapter.removeClass(Zo.DISABLED),this.leadingIcon&&this.leadingIcon.setDisabled(this.disabled),this.disabled?this.adapter.removeSelectAnchorAttr("tabindex"):this.adapter.setSelectAnchorAttr("tabindex","0"),this.adapter.setSelectAnchorAttr("aria-disabled",this.disabled.toString())},e.prototype.openMenu=function(){this.adapter.addClass(Zo.ACTIVATED),this.adapter.openMenu(),this.isMenuOpen=!0,this.adapter.setSelectAnchorAttr("aria-expanded","true")},e.prototype.setHelperTextContent=function(t){this.helperText&&this.helperText.setContent(t)},e.prototype.layout=function(){if(this.adapter.hasLabel()){var t=this.getValue().length>0,e=this.adapter.hasClass(Zo.FOCUSED),i=t||e,s=this.adapter.hasClass(Zo.REQUIRED);this.notchOutline(i),this.adapter.floatLabel(i),this.adapter.setLabelRequired(s)}},e.prototype.layoutOptions=function(){var t=this.adapter.getMenuItemValues().indexOf(this.getValue());this.setSelectedIndex(t,!1,!0)},e.prototype.handleMenuOpened=function(){if(0!==this.adapter.getMenuItemValues().length){var t=this.getSelectedIndex(),e=t>=0?t:0;this.adapter.focusMenuItemAtIndex(e)}},e.prototype.handleMenuClosing=function(){this.adapter.setSelectAnchorAttr("aria-expanded","false")},e.prototype.handleMenuClosed=function(){this.adapter.removeClass(Zo.ACTIVATED),this.isMenuOpen=!1,this.adapter.isSelectAnchorFocused()||this.blur()},e.prototype.handleChange=function(){this.layout(),this.adapter.notifyChange(this.getValue()),this.adapter.hasClass(Zo.REQUIRED)&&this.useDefaultValidation&&this.setValid(this.isValid())},e.prototype.handleMenuItemAction=function(t){this.setSelectedIndex(t,!0)},e.prototype.handleFocus=function(){this.adapter.addClass(Zo.FOCUSED),this.layout(),this.adapter.activateBottomLine()},e.prototype.handleBlur=function(){this.isMenuOpen||this.blur()},e.prototype.handleClick=function(t){this.disabled||this.recentlyClicked||(this.setClickDebounceTimeout(),this.isMenuOpen?this.adapter.closeMenu():(this.adapter.setRippleCenter(t),this.openMenu()))},e.prototype.handleKeydown=function(t){if(!this.isMenuOpen&&this.adapter.hasClass(Zo.FOCUSED)){var e=qo(t)===go,i=qo(t)===vo,s=qo(t)===wo,n=qo(t)===Eo;if(!(t.ctrlKey||t.metaKey)&&(!i&&t.key&&1===t.key.length||i&&this.adapter.isTypeaheadInProgress())){var r=i?" ":t.key,o=this.adapter.typeaheadMatchItem(r,this.getSelectedIndex());return o>=0&&this.setSelectedIndex(o),void t.preventDefault()}(e||i||s||n)&&(this.openMenu(),t.preventDefault())}},e.prototype.notchOutline=function(t){if(this.adapter.hasOutline()){var e=this.adapter.hasClass(Zo.FOCUSED);if(t){var i=ta.LABEL_SCALE,s=this.adapter.getLabelWidth()*i;this.adapter.notchOutline(s)}else e||this.adapter.closeOutline()}},e.prototype.setLeadingIconAriaLabel=function(t){this.leadingIcon&&this.leadingIcon.setAriaLabel(t)},e.prototype.setLeadingIconContent=function(t){this.leadingIcon&&this.leadingIcon.setContent(t)},e.prototype.getUseDefaultValidation=function(){return this.useDefaultValidation},e.prototype.setUseDefaultValidation=function(t){this.useDefaultValidation=t},e.prototype.setValid=function(t){this.useDefaultValidation||(this.customValidity=t),this.adapter.setSelectAnchorAttr("aria-invalid",(!t).toString()),t?(this.adapter.removeClass(Zo.INVALID),this.adapter.removeMenuClass(Zo.MENU_INVALID)):(this.adapter.addClass(Zo.INVALID),this.adapter.addMenuClass(Zo.MENU_INVALID)),this.syncHelperTextValidity(t)},e.prototype.isValid=function(){return this.useDefaultValidation&&this.adapter.hasClass(Zo.REQUIRED)&&!this.adapter.hasClass(Zo.DISABLED)?this.getSelectedIndex()!==ta.UNSET_INDEX&&(0!==this.getSelectedIndex()||Boolean(this.getValue())):this.customValidity},e.prototype.setRequired=function(t){t?this.adapter.addClass(Zo.REQUIRED):this.adapter.removeClass(Zo.REQUIRED),this.adapter.setSelectAnchorAttr("aria-required",t.toString()),this.adapter.setLabelRequired(t)},e.prototype.getRequired=function(){return"true"===this.adapter.getSelectAnchorAttr("aria-required")},e.prototype.init=function(){var t=this.adapter.getAnchorElement();t&&(this.adapter.setMenuAnchorElement(t),this.adapter.setMenuAnchorCorner(Xo.BOTTOM_START)),this.adapter.setMenuWrapFocus(!1),this.setDisabled(this.adapter.hasClass(Zo.DISABLED)),this.syncHelperTextValidity(!this.adapter.hasClass(Zo.INVALID)),this.layout(),this.layoutOptions()},e.prototype.blur=function(){this.adapter.removeClass(Zo.FOCUSED),this.layout(),this.adapter.deactivateBottomLine(),this.adapter.hasClass(Zo.REQUIRED)&&this.useDefaultValidation&&this.setValid(this.isValid())},e.prototype.syncHelperTextValidity=function(t){if(this.helperText){this.helperText.setValidity(t);var e=this.helperText.isVisible(),i=this.helperText.getId();e&&i?this.adapter.setSelectAnchorAttr(Qo.ARIA_DESCRIBEDBY,i):this.adapter.removeSelectAnchorAttr(Qo.ARIA_DESCRIBEDBY)}},e.prototype.setClickDebounceTimeout=function(){var t=this;clearTimeout(this.clickDebounceTimeout),this.clickDebounceTimeout=setTimeout(function(){t.recentlyClicked=!1},ta.CLICK_DEBOUNCE_TIMEOUT_MS),this.recentlyClicked=!0},e}(uo);
/**
     * @license
     * Copyright 2019 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
const ia=window,sa=ia.ShadowRoot&&(void 0===ia.ShadyCSS||ia.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,na=Symbol(),ra=new WeakMap;let oa=class{constructor(t,e,i){if(this._$cssResult$=!0,i!==na)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o;const e=this.t;if(sa&&void 0===t){const i=void 0!==e&&1===e.length;i&&(t=ra.get(e)),void 0===t&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),i&&ra.set(e,t))}return t}toString(){return this.cssText}};const aa=sa?t=>t:t=>t instanceof CSSStyleSheet?(t=>{let e="";for(const i of t.cssRules)e+=i.cssText;return(t=>new oa("string"==typeof t?t:t+"",void 0,na))(e)})(t):t;
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */var la;const da=window,ca=da.trustedTypes,ha=ca?ca.emptyScript:"",pa=da.reactiveElementPolyfillSupport,ua={toAttribute(t,e){switch(e){case Boolean:t=t?ha:null;break;case Object:case Array:t=null==t?t:JSON.stringify(t)}return t},fromAttribute(t,e){let i=t;switch(e){case Boolean:i=null!==t;break;case Number:i=null===t?null:Number(t);break;case Object:case Array:try{i=JSON.parse(t)}catch(t){i=null}}return i}},ma=(t,e)=>e!==t&&(e==e||t==t),fa={attribute:!0,type:String,converter:ua,reflect:!1,hasChanged:ma},ga="finalized";let va=class extends HTMLElement{constructor(){super(),this._$Ei=new Map,this.isUpdatePending=!1,this.hasUpdated=!1,this._$El=null,this._$Eu()}static addInitializer(t){var e;this.finalize(),(null!==(e=this.h)&&void 0!==e?e:this.h=[]).push(t)}static get observedAttributes(){this.finalize();const t=[];return this.elementProperties.forEach((e,i)=>{const s=this._$Ep(i,e);void 0!==s&&(this._$Ev.set(s,i),t.push(s))}),t}static createProperty(t,e=fa){if(e.state&&(e.attribute=!1),this.finalize(),this.elementProperties.set(t,e),!e.noAccessor&&!this.prototype.hasOwnProperty(t)){const i="symbol"==typeof t?Symbol():"__"+t,s=this.getPropertyDescriptor(t,i,e);void 0!==s&&Object.defineProperty(this.prototype,t,s)}}static getPropertyDescriptor(t,e,i){return{get(){return this[e]},set(s){const n=this[t];this[e]=s,this.requestUpdate(t,n,i)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)||fa}static finalize(){if(this.hasOwnProperty(ga))return!1;this[ga]=!0;const t=Object.getPrototypeOf(this);if(t.finalize(),void 0!==t.h&&(this.h=[...t.h]),this.elementProperties=new Map(t.elementProperties),this._$Ev=new Map,this.hasOwnProperty("properties")){const t=this.properties,e=[...Object.getOwnPropertyNames(t),...Object.getOwnPropertySymbols(t)];for(const i of e)this.createProperty(i,t[i])}return this.elementStyles=this.finalizeStyles(this.styles),!0}static finalizeStyles(t){const e=[];if(Array.isArray(t)){const i=new Set(t.flat(1/0).reverse());for(const t of i)e.unshift(aa(t))}else void 0!==t&&e.push(aa(t));return e}static _$Ep(t,e){const i=e.attribute;return!1===i?void 0:"string"==typeof i?i:"string"==typeof t?t.toLowerCase():void 0}_$Eu(){var t;this._$E_=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$Eg(),this.requestUpdate(),null===(t=this.constructor.h)||void 0===t||t.forEach(t=>t(this))}addController(t){var e,i;(null!==(e=this._$ES)&&void 0!==e?e:this._$ES=[]).push(t),void 0!==this.renderRoot&&this.isConnected&&(null===(i=t.hostConnected)||void 0===i||i.call(t))}removeController(t){var e;null===(e=this._$ES)||void 0===e||e.splice(this._$ES.indexOf(t)>>>0,1)}_$Eg(){this.constructor.elementProperties.forEach((t,e)=>{this.hasOwnProperty(e)&&(this._$Ei.set(e,this[e]),delete this[e])})}createRenderRoot(){var t;const e=null!==(t=this.shadowRoot)&&void 0!==t?t:this.attachShadow(this.constructor.shadowRootOptions);return((t,e)=>{sa?t.adoptedStyleSheets=e.map(t=>t instanceof CSSStyleSheet?t:t.styleSheet):e.forEach(e=>{const i=document.createElement("style"),s=ia.litNonce;void 0!==s&&i.setAttribute("nonce",s),i.textContent=e.cssText,t.appendChild(i)})})(e,this.constructor.elementStyles),e}connectedCallback(){var t;void 0===this.renderRoot&&(this.renderRoot=this.createRenderRoot()),this.enableUpdating(!0),null===(t=this._$ES)||void 0===t||t.forEach(t=>{var e;return null===(e=t.hostConnected)||void 0===e?void 0:e.call(t)})}enableUpdating(t){}disconnectedCallback(){var t;null===(t=this._$ES)||void 0===t||t.forEach(t=>{var e;return null===(e=t.hostDisconnected)||void 0===e?void 0:e.call(t)})}attributeChangedCallback(t,e,i){this._$AK(t,i)}_$EO(t,e,i=fa){var s;const n=this.constructor._$Ep(t,i);if(void 0!==n&&!0===i.reflect){const r=(void 0!==(null===(s=i.converter)||void 0===s?void 0:s.toAttribute)?i.converter:ua).toAttribute(e,i.type);this._$El=t,null==r?this.removeAttribute(n):this.setAttribute(n,r),this._$El=null}}_$AK(t,e){var i;const s=this.constructor,n=s._$Ev.get(t);if(void 0!==n&&this._$El!==n){const t=s.getPropertyOptions(n),r="function"==typeof t.converter?{fromAttribute:t.converter}:void 0!==(null===(i=t.converter)||void 0===i?void 0:i.fromAttribute)?t.converter:ua;this._$El=n,this[n]=r.fromAttribute(e,t.type),this._$El=null}}requestUpdate(t,e,i){let s=!0;void 0!==t&&(((i=i||this.constructor.getPropertyOptions(t)).hasChanged||ma)(this[t],e)?(this._$AL.has(t)||this._$AL.set(t,e),!0===i.reflect&&this._$El!==t&&(void 0===this._$EC&&(this._$EC=new Map),this._$EC.set(t,i))):s=!1),!this.isUpdatePending&&s&&(this._$E_=this._$Ej())}async _$Ej(){this.isUpdatePending=!0;try{await this._$E_}catch(t){Promise.reject(t)}const t=this.scheduleUpdate();return null!=t&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){var t;if(!this.isUpdatePending)return;this.hasUpdated,this._$Ei&&(this._$Ei.forEach((t,e)=>this[e]=t),this._$Ei=void 0);let e=!1;const i=this._$AL;try{e=this.shouldUpdate(i),e?(this.willUpdate(i),null===(t=this._$ES)||void 0===t||t.forEach(t=>{var e;return null===(e=t.hostUpdate)||void 0===e?void 0:e.call(t)}),this.update(i)):this._$Ek()}catch(t){throw e=!1,this._$Ek(),t}e&&this._$AE(i)}willUpdate(t){}_$AE(t){var e;null===(e=this._$ES)||void 0===e||e.forEach(t=>{var e;return null===(e=t.hostUpdated)||void 0===e?void 0:e.call(t)}),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$Ek(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$E_}shouldUpdate(t){return!0}update(t){void 0!==this._$EC&&(this._$EC.forEach((t,e)=>this._$EO(e,this[e],t)),this._$EC=void 0),this._$Ek()}updated(t){}firstUpdated(t){}};
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
var _a;va[ga]=!0,va.elementProperties=new Map,va.elementStyles=[],va.shadowRootOptions={mode:"open"},null==pa||pa({ReactiveElement:va}),(null!==(la=da.reactiveElementVersions)&&void 0!==la?la:da.reactiveElementVersions=[]).push("1.6.3");const ba=window,ya=ba.trustedTypes,xa=ya?ya.createPolicy("lit-html",{createHTML:t=>t}):void 0,$a="$lit$",wa=`lit$${(Math.random()+"").slice(9)}$`,Aa="?"+wa,Ea=`<${Aa}>`,Sa=document,Ca=()=>Sa.createComment(""),Ta=t=>null===t||"object"!=typeof t&&"function"!=typeof t,Ia=Array.isArray,Oa="[ \t\n\f\r]",ka=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,Ra=/-->/g,Pa=/>/g,La=RegExp(`>|${Oa}(?:([^\\s"'>=/]+)(${Oa}*=${Oa}*(?:[^ \t\n\f\r"'\`<>=]|("|')|))|$)`,"g"),Ma=/'/g,Na=/"/g,Da=/^(?:script|style|textarea|title)$/i,Ha=(t=>(e,...i)=>({_$litType$:t,strings:e,values:i}))(1),Ua=Symbol.for("lit-noChange"),za=Symbol.for("lit-nothing"),Fa=new WeakMap,Ba=Sa.createTreeWalker(Sa,129,null,!1);function Va(t,e){if(!Array.isArray(t)||!t.hasOwnProperty("raw"))throw Error("invalid template strings array");return void 0!==xa?xa.createHTML(e):e}let ja=class t{constructor({strings:e,_$litType$:i},s){let n;this.parts=[];let r=0,o=0;const a=e.length-1,l=this.parts,[d,c]=((t,e)=>{const i=t.length-1,s=[];let n,r=2===e?"<svg>":"",o=ka;for(let e=0;e<i;e++){const i=t[e];let a,l,d=-1,c=0;for(;c<i.length&&(o.lastIndex=c,l=o.exec(i),null!==l);)c=o.lastIndex,o===ka?"!--"===l[1]?o=Ra:void 0!==l[1]?o=Pa:void 0!==l[2]?(Da.test(l[2])&&(n=RegExp("</"+l[2],"g")),o=La):void 0!==l[3]&&(o=La):o===La?">"===l[0]?(o=null!=n?n:ka,d=-1):void 0===l[1]?d=-2:(d=o.lastIndex-l[2].length,a=l[1],o=void 0===l[3]?La:'"'===l[3]?Na:Ma):o===Na||o===Ma?o=La:o===Ra||o===Pa?o=ka:(o=La,n=void 0);const h=o===La&&t[e+1].startsWith("/>")?" ":"";r+=o===ka?i+Ea:d>=0?(s.push(a),i.slice(0,d)+$a+i.slice(d)+wa+h):i+wa+(-2===d?(s.push(void 0),e):h)}return[Va(t,r+(t[i]||"<?>")+(2===e?"</svg>":"")),s]})(e,i);if(this.el=t.createElement(d,s),Ba.currentNode=this.el.content,2===i){const t=this.el.content,e=t.firstChild;e.remove(),t.append(...e.childNodes)}for(;null!==(n=Ba.nextNode())&&l.length<a;){if(1===n.nodeType){if(n.hasAttributes()){const t=[];for(const e of n.getAttributeNames())if(e.endsWith($a)||e.startsWith(wa)){const i=c[o++];if(t.push(e),void 0!==i){const t=n.getAttribute(i.toLowerCase()+$a).split(wa),e=/([.?@])?(.*)/.exec(i);l.push({type:1,index:r,name:e[2],strings:t,ctor:"."===e[1]?Ga:"?"===e[1]?Ja:"@"===e[1]?Za:Xa})}else l.push({type:6,index:r})}for(const e of t)n.removeAttribute(e)}if(Da.test(n.tagName)){const t=n.textContent.split(wa),e=t.length-1;if(e>0){n.textContent=ya?ya.emptyScript:"";for(let i=0;i<e;i++)n.append(t[i],Ca()),Ba.nextNode(),l.push({type:2,index:++r});n.append(t[e],Ca())}}}else if(8===n.nodeType)if(n.data===Aa)l.push({type:2,index:r});else{let t=-1;for(;-1!==(t=n.data.indexOf(wa,t+1));)l.push({type:7,index:r}),t+=wa.length-1}r++}}static createElement(t,e){const i=Sa.createElement("template");return i.innerHTML=t,i}};function Wa(t,e,i=t,s){var n,r,o,a;if(e===Ua)return e;let l=void 0!==s?null===(n=i._$Co)||void 0===n?void 0:n[s]:i._$Cl;const d=Ta(e)?void 0:e._$litDirective$;return(null==l?void 0:l.constructor)!==d&&(null===(r=null==l?void 0:l._$AO)||void 0===r||r.call(l,!1),void 0===d?l=void 0:(l=new d(t),l._$AT(t,i,s)),void 0!==s?(null!==(o=(a=i)._$Co)&&void 0!==o?o:a._$Co=[])[s]=l:i._$Cl=l),void 0!==l&&(e=Wa(t,l._$AS(t,e.values),l,s)),e}let qa=class{constructor(t,e){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){var e;const{el:{content:i},parts:s}=this._$AD,n=(null!==(e=null==t?void 0:t.creationScope)&&void 0!==e?e:Sa).importNode(i,!0);Ba.currentNode=n;let r=Ba.nextNode(),o=0,a=0,l=s[0];for(;void 0!==l;){if(o===l.index){let e;2===l.type?e=new Ya(r,r.nextSibling,this,t):1===l.type?e=new l.ctor(r,l.name,l.strings,this,t):6===l.type&&(e=new Qa(r,this,t)),this._$AV.push(e),l=s[++a]}o!==(null==l?void 0:l.index)&&(r=Ba.nextNode(),o++)}return Ba.currentNode=Sa,n}v(t){let e=0;for(const i of this._$AV)void 0!==i&&(void 0!==i.strings?(i._$AI(t,i,e),e+=i.strings.length-2):i._$AI(t[e])),e++}},Ya=class t{constructor(t,e,i,s){var n;this.type=2,this._$AH=za,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=i,this.options=s,this._$Cp=null===(n=null==s?void 0:s.isConnected)||void 0===n||n}get _$AU(){var t,e;return null!==(e=null===(t=this._$AM)||void 0===t?void 0:t._$AU)&&void 0!==e?e:this._$Cp}get parentNode(){let t=this._$AA.parentNode;const e=this._$AM;return void 0!==e&&11===(null==t?void 0:t.nodeType)&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=Wa(this,t,e),Ta(t)?t===za||null==t||""===t?(this._$AH!==za&&this._$AR(),this._$AH=za):t!==this._$AH&&t!==Ua&&this._(t):void 0!==t._$litType$?this.g(t):void 0!==t.nodeType?this.$(t):(t=>Ia(t)||"function"==typeof(null==t?void 0:t[Symbol.iterator]))(t)?this.T(t):this._(t)}k(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}$(t){this._$AH!==t&&(this._$AR(),this._$AH=this.k(t))}_(t){this._$AH!==za&&Ta(this._$AH)?this._$AA.nextSibling.data=t:this.$(Sa.createTextNode(t)),this._$AH=t}g(t){var e;const{values:i,_$litType$:s}=t,n="number"==typeof s?this._$AC(t):(void 0===s.el&&(s.el=ja.createElement(Va(s.h,s.h[0]),this.options)),s);if((null===(e=this._$AH)||void 0===e?void 0:e._$AD)===n)this._$AH.v(i);else{const t=new qa(n,this),e=t.u(this.options);t.v(i),this.$(e),this._$AH=t}}_$AC(t){let e=Fa.get(t.strings);return void 0===e&&Fa.set(t.strings,e=new ja(t)),e}T(e){Ia(this._$AH)||(this._$AH=[],this._$AR());const i=this._$AH;let s,n=0;for(const r of e)n===i.length?i.push(s=new t(this.k(Ca()),this.k(Ca()),this,this.options)):s=i[n],s._$AI(r),n++;n<i.length&&(this._$AR(s&&s._$AB.nextSibling,n),i.length=n)}_$AR(t=this._$AA.nextSibling,e){var i;for(null===(i=this._$AP)||void 0===i||i.call(this,!1,!0,e);t&&t!==this._$AB;){const e=t.nextSibling;t.remove(),t=e}}setConnected(t){var e;void 0===this._$AM&&(this._$Cp=t,null===(e=this._$AP)||void 0===e||e.call(this,t))}},Xa=class{constructor(t,e,i,s,n){this.type=1,this._$AH=za,this._$AN=void 0,this.element=t,this.name=e,this._$AM=s,this.options=n,i.length>2||""!==i[0]||""!==i[1]?(this._$AH=Array(i.length-1).fill(new String),this.strings=i):this._$AH=za}get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}_$AI(t,e=this,i,s){const n=this.strings;let r=!1;if(void 0===n)t=Wa(this,t,e,0),r=!Ta(t)||t!==this._$AH&&t!==Ua,r&&(this._$AH=t);else{const s=t;let o,a;for(t=n[0],o=0;o<n.length-1;o++)a=Wa(this,s[i+o],e,o),a===Ua&&(a=this._$AH[o]),r||(r=!Ta(a)||a!==this._$AH[o]),a===za?t=za:t!==za&&(t+=(null!=a?a:"")+n[o+1]),this._$AH[o]=a}r&&!s&&this.j(t)}j(t){t===za?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,null!=t?t:"")}},Ga=class extends Xa{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===za?void 0:t}};const Ka=ya?ya.emptyScript:"";let Ja=class extends Xa{constructor(){super(...arguments),this.type=4}j(t){t&&t!==za?this.element.setAttribute(this.name,Ka):this.element.removeAttribute(this.name)}},Za=class extends Xa{constructor(t,e,i,s,n){super(t,e,i,s,n),this.type=5}_$AI(t,e=this){var i;if((t=null!==(i=Wa(this,t,e,0))&&void 0!==i?i:za)===Ua)return;const s=this._$AH,n=t===za&&s!==za||t.capture!==s.capture||t.once!==s.once||t.passive!==s.passive,r=t!==za&&(s===za||n);n&&this.element.removeEventListener(this.name,this,s),r&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){var e,i;"function"==typeof this._$AH?this._$AH.call(null!==(i=null===(e=this.options)||void 0===e?void 0:e.host)&&void 0!==i?i:this.element,t):this._$AH.handleEvent(t)}},Qa=class{constructor(t,e,i){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=i}get _$AU(){return this._$AM._$AU}_$AI(t){Wa(this,t)}};const tl=ba.litHtmlPolyfillSupport;null==tl||tl(ja,Ya),(null!==(_a=ba.litHtmlVersions)&&void 0!==_a?_a:ba.litHtmlVersions=[]).push("2.8.0");
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
var el,il;let sl=class extends va{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){var t,e;const i=super.createRenderRoot();return null!==(t=(e=this.renderOptions).renderBefore)&&void 0!==t||(e.renderBefore=i.firstChild),i}update(t){const e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=((t,e,i)=>{var s,n;const r=null!==(s=null==i?void 0:i.renderBefore)&&void 0!==s?s:e;let o=r._$litPart$;if(void 0===o){const t=null!==(n=null==i?void 0:i.renderBefore)&&void 0!==n?n:null;r._$litPart$=o=new Ya(e.insertBefore(Ca(),t),t,void 0,null!=i?i:{})}return o._$AI(t),o})(e,this.renderRoot,this.renderOptions)}connectedCallback(){var t;super.connectedCallback(),null===(t=this._$Do)||void 0===t||t.setConnected(!0)}disconnectedCallback(){var t;super.disconnectedCallback(),null===(t=this._$Do)||void 0===t||t.setConnected(!1)}render(){return Ua}};sl.finalized=!0,sl._$litElement$=!0,null===(el=globalThis.litElementHydrateSupport)||void 0===el||el.call(globalThis,{LitElement:sl});const nl=globalThis.litElementPolyfillSupport;null==nl||nl({LitElement:sl}),(null!==(il=globalThis.litElementVersions)&&void 0!==il?il:globalThis.litElementVersions=[]).push("3.3.3");
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
const rl=(t,e)=>"method"===e.kind&&e.descriptor&&!("value"in e.descriptor)?{...e,finisher(i){i.createProperty(e.key,t)}}:{kind:"field",key:Symbol(),placement:"own",descriptor:{},originalKey:e.key,initializer(){"function"==typeof e.initializer&&(this[e.key]=e.initializer.call(this))},finisher(i){i.createProperty(e.key,t)}};function ol(t){return(e,i)=>void 0!==i?((t,e,i)=>{e.constructor.createProperty(i,t)})(t,e,i):rl(t,e)}
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */function al(t){return ol({...t,state:!0})}
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */const ll=({finisher:t,descriptor:e})=>(i,s)=>{var n;if(void 0===s){const s=null!==(n=i.originalKey)&&void 0!==n?n:i.key,r=null!=e?{kind:"method",placement:"prototype",key:s,descriptor:e(i.key)}:{...i,key:s};return null!=t&&(r.finisher=function(e){t(e,s)}),r}{const n=i.constructor;void 0!==e&&Object.defineProperty(i,s,e(s)),null==t||t(n,s)}};
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
function dl(t,e){return ll({descriptor:e=>{const i={get(){var e,i;return null!==(i=null===(e=this.renderRoot)||void 0===e?void 0:e.querySelector(t))&&void 0!==i?i:null},enumerable:!0,configurable:!0};return i}})}
/**
     * @license
     * Copyright 2021 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */var cl;null===(cl=window.HTMLSlotElement)||void 0===cl||cl.prototype.assignedElements;
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
const hl=1;let pl=class{constructor(t){}get _$AU(){return this._$AM._$AU}_$AT(t,e,i){this._$Ct=t,this._$AM=e,this._$Ci=i}_$AS(t,e){return this.update(t,e)}update(t,e){return this.render(...e)}};
/**
     * @license
     * Copyright 2018 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */const ul=(t=>(...e)=>({_$litDirective$:t,values:e}))(class extends pl{constructor(t){var e;if(super(t),t.type!==hl||"class"!==t.name||(null===(e=t.strings)||void 0===e?void 0:e.length)>2)throw Error("`classMap()` can only be used in the `class` attribute and must be the only part in the attribute.")}render(t){return" "+Object.keys(t).filter(e=>t[e]).join(" ")+" "}update(t,[e]){var i,s;if(void 0===this.it){this.it=new Set,void 0!==t.strings&&(this.nt=new Set(t.strings.join(" ").split(/\s/).filter(t=>""!==t)));for(const t in e)e[t]&&!(null===(i=this.nt)||void 0===i?void 0:i.has(t))&&this.it.add(t);return this.render(e)}const n=t.element.classList;this.it.forEach(t=>{t in e||(n.remove(t),this.it.delete(t))});for(const t in e){const i=!!e[t];i===this.it.has(t)||(null===(s=this.nt)||void 0===s?void 0:s.has(t))||(i?(n.add(t),this.it.add(t)):(n.remove(t),this.it.delete(t)))}return Ua}}),ml=t=>null!=t?t:za,fl=(t={})=>{const e={};for(const i in t)e[i]=t[i];return Object.assign({badInput:!1,customError:!1,patternMismatch:!1,rangeOverflow:!1,rangeUnderflow:!1,stepMismatch:!1,tooLong:!1,tooShort:!1,typeMismatch:!1,valid:!0,valueMissing:!1},e)};
/**
     * @license
     * Copyright 2018 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */class gl extends rs{constructor(){super(...arguments),this.mdcFoundationClass=ea,this.disabled=!1,this.outlined=!1,this.label="",this.outlineOpen=!1,this.outlineWidth=0,this.value="",this.name="",this.selectedText="",this.icon="",this.menuOpen=!1,this.helper="",this.validateOnInitialRender=!1,this.validationMessage="",this.required=!1,this.naturalMenuWidth=!1,this.isUiValid=!0,this.fixedMenuPosition=!1,this.typeaheadState={bufferClearTimeout:0,currentFirstChar:"",sortedIndexCursor:0,typeaheadBuffer:""},this.sortedIndexByFirstChar=new Map,this.menuElement_=null,this.listeners=[],this.onBodyClickBound=()=>{},this._menuUpdateComplete=null,this.valueSetDirectly=!1,this.validityTransform=null,this._validity=fl()}get items(){return this.menuElement_||(this.menuElement_=this.menuElement),this.menuElement_?this.menuElement_.items:[]}get selected(){const t=this.menuElement;return t?t.selected:null}get index(){const t=this.menuElement;return t?t.index:-1}get shouldRenderHelperText(){return!!this.helper||!!this.validationMessage}get validity(){return this._checkValidity(this.value),this._validity}render(){const t={"mdc-select--disabled":this.disabled,"mdc-select--no-label":!this.label,"mdc-select--filled":!this.outlined,"mdc-select--outlined":this.outlined,"mdc-select--with-leading-icon":!!this.icon,"mdc-select--required":this.required,"mdc-select--invalid":!this.isUiValid},e=this.label?"label":void 0,i=this.shouldRenderHelperText?"helper-text":void 0;return Ha`
      <div
          class="mdc-select ${ul(t)}">
        <input
            class="formElement"
            name="${this.name}"
            .value="${this.value}"
            hidden
            ?disabled="${this.disabled}"
            ?required=${this.required}>
        <!-- @ts-ignore -->
        <div class="mdc-select__anchor"
            aria-autocomplete="none"
            role="combobox"
            aria-expanded=${this.menuOpen}
            aria-invalid=${!this.isUiValid}
            aria-haspopup="listbox"
            aria-labelledby=${ml(e)}
            aria-required=${this.required}
            aria-describedby=${ml(i)}
            @click=${this.onClick}
            @focus=${this.onFocus}
            @blur=${this.onBlur}
            @keydown=${this.onKeydown}>
          ${this.renderRipple()}
          ${this.outlined?this.renderOutline():this.renderLabel()}
          ${this.renderLeadingIcon()}
          <span class="mdc-select__selected-text-container">
            <span class="mdc-select__selected-text">${this.selectedText}</span>
          </span>
          <span class="mdc-select__dropdown-icon">
            <svg
                class="mdc-select__dropdown-icon-graphic"
                viewBox="7 10 10 5"
                focusable="false">
              <polygon
                  class="mdc-select__dropdown-icon-inactive"
                  stroke="none"
                  fill-rule="evenodd"
                  points="7 10 12 15 17 10">
              </polygon>
              <polygon
                  class="mdc-select__dropdown-icon-active"
                  stroke="none"
                  fill-rule="evenodd"
                  points="7 15 12 10 17 15">
              </polygon>
            </svg>
          </span>
          ${this.renderLineRipple()}
        </div>
        ${this.renderMenu()}
      </div>
      ${this.renderHelperText()}`}renderMenu(){const t=this.getMenuClasses();return Ha`
      <mwc-menu
        innerRole="listbox"
        wrapFocus
        class=" ${ul(t)}"
        activatable
        .fullwidth=${!this.fixedMenuPosition&&!this.naturalMenuWidth}
        .open=${this.menuOpen}
        .anchor=${this.anchorElement}
        .fixed=${this.fixedMenuPosition}
        @selected=${this.onSelected}
        @opened=${this.onOpened}
        @closed=${this.onClosed}
        @items-updated=${this.onItemsUpdated}
        @keydown=${this.handleTypeahead}>
      ${this.renderMenuContent()}
    </mwc-menu>`}getMenuClasses(){return{"mdc-select__menu":!0,"mdc-menu":!0,"mdc-menu-surface":!0,"mdc-select__menu--invalid":!this.isUiValid}}renderMenuContent(){return Ha`<slot></slot>`}renderRipple(){return this.outlined?za:Ha`
      <span class="mdc-select__ripple"></span>
    `}renderOutline(){return this.outlined?Ha`
      <mwc-notched-outline
          .width=${this.outlineWidth}
          .open=${this.outlineOpen}
          class="mdc-notched-outline">
        ${this.renderLabel()}
      </mwc-notched-outline>`:za}renderLabel(){return this.label?Ha`
      <span
          .floatingLabelFoundation=${no(this.label)}
          id="label">${this.label}</span>
    `:za}renderLeadingIcon(){return this.icon?Ha`<mwc-icon class="mdc-select__icon"><div>${this.icon}</div></mwc-icon>`:za}renderLineRipple(){return this.outlined?za:Ha`
      <span .lineRippleFoundation=${po()}></span>
    `}renderHelperText(){if(!this.shouldRenderHelperText)return za;const t=this.validationMessage&&!this.isUiValid;return Ha`
        <p
          class="mdc-select-helper-text ${ul({"mdc-select-helper-text--validation-msg":t})}"
          id="helper-text">${t?this.validationMessage:this.helper}</p>`}createAdapter(){return Object.assign(Object.assign({},Xi(this.mdcRoot)),{activateBottomLine:()=>{this.lineRippleElement&&this.lineRippleElement.lineRippleFoundation.activate()},deactivateBottomLine:()=>{this.lineRippleElement&&this.lineRippleElement.lineRippleFoundation.deactivate()},hasLabel:()=>!!this.label,floatLabel:t=>{this.labelElement&&this.labelElement.floatingLabelFoundation.float(t)},getLabelWidth:()=>this.labelElement?this.labelElement.floatingLabelFoundation.getWidth():0,setLabelRequired:t=>{this.labelElement&&this.labelElement.floatingLabelFoundation.setRequired(t)},hasOutline:()=>this.outlined,notchOutline:t=>{this.outlineElement&&!this.outlineOpen&&(this.outlineWidth=t,this.outlineOpen=!0)},closeOutline:()=>{this.outlineElement&&(this.outlineOpen=!1)},setRippleCenter:t=>{if(this.lineRippleElement){this.lineRippleElement.lineRippleFoundation.setRippleCenter(t)}},notifyChange:async t=>{if(!this.valueSetDirectly&&t===this.value)return;this.valueSetDirectly=!1,this.value=t,await this.updateComplete;const e=new Event("change",{bubbles:!0});this.dispatchEvent(e)},setSelectedText:t=>this.selectedText=t,isSelectAnchorFocused:()=>{const t=this.anchorElement;if(!t)return!1;return t.getRootNode().activeElement===t},getSelectAnchorAttr:t=>{const e=this.anchorElement;return e?e.getAttribute(t):null},setSelectAnchorAttr:(t,e)=>{const i=this.anchorElement;i&&i.setAttribute(t,e)},removeSelectAnchorAttr:t=>{const e=this.anchorElement;e&&e.removeAttribute(t)},openMenu:()=>{this.menuOpen=!0},closeMenu:()=>{this.menuOpen=!1},addMenuClass:()=>{},removeMenuClass:()=>{},getAnchorElement:()=>this.anchorElement,setMenuAnchorElement:()=>{},setMenuAnchorCorner:()=>{const t=this.menuElement;t&&(t.corner="BOTTOM_START")},setMenuWrapFocus:t=>{const e=this.menuElement;e&&(e.wrapFocus=t)},focusMenuItemAtIndex:t=>{const e=this.menuElement;if(!e)return;const i=e.items[t];i&&i.focus()},getMenuItemCount:()=>{const t=this.menuElement;return t?t.items.length:0},getMenuItemValues:()=>{const t=this.menuElement;if(!t)return[];return t.items.map(t=>t.value)},getMenuItemTextAtIndex:t=>{const e=this.menuElement;if(!e)return"";const i=e.items[t];return i?i.text:""},getSelectedIndex:()=>this.index,setSelectedIndex:()=>{},isTypeaheadInProgress:()=>Jr(this.typeaheadState),typeaheadMatchItem:(t,e)=>{if(!this.menuElement)return-1;const i={focusItemAtIndex:t=>{this.menuElement.focusItemAtIndex(t)},focusedItemIndex:e||this.menuElement.getFocusedItemIndex(),nextChar:t,sortedIndexByFirstChar:this.sortedIndexByFirstChar,skipFocus:!1,isItemAtIndexDisabled:t=>this.items[t].disabled},s=Kr(i,this.typeaheadState);return-1!==s&&this.select(s),s}})}checkValidity(){const t=this._checkValidity(this.value);if(!t){const t=new Event("invalid",{bubbles:!1,cancelable:!0});this.dispatchEvent(t)}return t}reportValidity(){const t=this.checkValidity();return this.isUiValid=t,t}_checkValidity(t){const e=this.formElement.validity;let i=fl(e);if(this.validityTransform){const e=this.validityTransform(t,i);i=Object.assign(Object.assign({},i),e)}return this._validity=i,this._validity.valid}setCustomValidity(t){this.validationMessage=t,this.formElement.setCustomValidity(t)}async getUpdateComplete(){await this._menuUpdateComplete;return await super.getUpdateComplete()}async firstUpdated(){const t=this.menuElement;if(t&&(this._menuUpdateComplete=t.updateComplete,await this._menuUpdateComplete),super.firstUpdated(),this.mdcFoundation.isValid=()=>!0,this.mdcFoundation.setValid=()=>{},this.mdcFoundation.setDisabled(this.disabled),this.validateOnInitialRender&&this.reportValidity(),!this.selected){!this.items.length&&this.slotElement&&this.slotElement.assignedNodes({flatten:!0}).length&&(await new Promise(t=>requestAnimationFrame(t)),await this.layout());const t=this.items.length&&""===this.items[0].value;if(!this.value&&t)return void this.select(0);this.selectByValue(this.value)}this.sortedIndexByFirstChar=Gr(this.items.length,t=>this.items[t].text)}onItemsUpdated(){this.sortedIndexByFirstChar=Gr(this.items.length,t=>this.items[t].text)}select(t){const e=this.menuElement;e&&e.select(t)}selectByValue(t){let e=-1;for(let i=0;i<this.items.length;i++){if(this.items[i].value===t){e=i;break}}this.valueSetDirectly=!0,this.select(e),this.mdcFoundation.handleChange()}disconnectedCallback(){super.disconnectedCallback();for(const t of this.listeners)t.target.removeEventListener(t.name,t.cb)}focus(){const t=new CustomEvent("focus"),e=this.anchorElement;e&&(e.dispatchEvent(t),e.focus())}blur(){const t=new CustomEvent("blur"),e=this.anchorElement;e&&(e.dispatchEvent(t),e.blur())}onFocus(){this.mdcFoundation&&this.mdcFoundation.handleFocus()}onBlur(){this.mdcFoundation&&this.mdcFoundation.handleBlur();const t=this.menuElement;t&&!t.open&&this.reportValidity()}onClick(t){if(this.mdcFoundation){this.focus();const e=t.target.getBoundingClientRect();let i=0;i="touches"in t?t.touches[0].clientX:t.clientX;const s=i-e.left;this.mdcFoundation.handleClick(s)}}onKeydown(t){const e=er(t)===Rn,i=er(t)===Ln;if(i||e){const s=e&&this.index>0,n=i&&this.index<this.items.length-1;return s?this.select(this.index-1):n&&this.select(this.index+1),t.preventDefault(),void this.mdcFoundation.openMenu()}this.mdcFoundation.handleKeydown(t)}handleTypeahead(t){if(!this.menuElement)return;const e=this.menuElement.getFocusedItemIndex(),i=Yi(t.target)?t.target:null;!function(t,e){var i=t.event,s=t.isTargetListItem,n=t.focusedItemIndex,r=t.focusItemAtIndex,o=t.sortedIndexByFirstChar,a=t.isItemAtIndexDisabled,l="ArrowLeft"===Nr(i),d="ArrowUp"===Nr(i),c="ArrowRight"===Nr(i),h="ArrowDown"===Nr(i),p="Home"===Nr(i),u="End"===Nr(i),m="Enter"===Nr(i),f="Spacebar"===Nr(i);i.altKey||i.ctrlKey||i.metaKey||l||d||c||h||p||u||m||(f||1!==i.key.length?f&&(s&&Xr(i),s&&Jr(e)&&Kr({focusItemAtIndex:r,focusedItemIndex:n,nextChar:" ",sortedIndexByFirstChar:o,skipFocus:!1,isItemAtIndexDisabled:a},e)):(Xr(i),Kr({focusItemAtIndex:r,focusedItemIndex:n,nextChar:i.key.toLowerCase(),sortedIndexByFirstChar:o,skipFocus:!1,isItemAtIndexDisabled:a},e)))}({event:t,focusItemAtIndex:t=>{this.menuElement.focusItemAtIndex(t)},focusedItemIndex:e,isTargetListItem:!!i&&i.hasAttribute("mwc-list-item"),sortedIndexByFirstChar:this.sortedIndexByFirstChar,isItemAtIndexDisabled:t=>this.items[t].disabled},this.typeaheadState)}async onSelected(t){this.mdcFoundation||await this.updateComplete,this.mdcFoundation.handleMenuItemAction(t.detail.index);const e=this.items[t.detail.index];e&&(this.value=e.value)}onOpened(){this.mdcFoundation&&(this.menuOpen=!0,this.mdcFoundation.handleMenuOpened())}onClosed(){this.mdcFoundation&&(this.menuOpen=!1,this.mdcFoundation.handleMenuClosed())}setFormData(t){this.name&&null!==this.selected&&t.append(this.name,this.value)}async layout(t=!0){this.mdcFoundation&&this.mdcFoundation.layout(),await this.updateComplete;const e=this.menuElement;e&&e.layout(t);const i=this.labelElement;if(!i)return void(this.outlineOpen=!1);const s=!!this.label&&!!this.value;if(i.floatingLabelFoundation.float(s),!this.outlined)return;this.outlineOpen=s,await this.updateComplete;const n=i.floatingLabelFoundation.getWidth();this.outlineOpen&&(this.outlineWidth=n)}async layoutOptions(){this.mdcFoundation&&this.mdcFoundation.layoutOptions()}}n([dl(".mdc-select")],gl.prototype,"mdcRoot",void 0),n([dl(".formElement")],gl.prototype,"formElement",void 0),n([dl("slot")],gl.prototype,"slotElement",void 0),n([dl("select")],gl.prototype,"nativeSelectElement",void 0),n([dl("input")],gl.prototype,"nativeInputElement",void 0),n([dl(".mdc-line-ripple")],gl.prototype,"lineRippleElement",void 0),n([dl(".mdc-floating-label")],gl.prototype,"labelElement",void 0),n([dl("mwc-notched-outline")],gl.prototype,"outlineElement",void 0),n([dl(".mdc-menu")],gl.prototype,"menuElement",void 0),n([dl(".mdc-select__anchor")],gl.prototype,"anchorElement",void 0),n([ol({type:Boolean,attribute:"disabled",reflect:!0}),os(function(t){this.mdcFoundation&&this.mdcFoundation.setDisabled(t)})],gl.prototype,"disabled",void 0),n([ol({type:Boolean}),os(function(t,e){void 0!==e&&this.outlined!==e&&this.layout(!1)})],gl.prototype,"outlined",void 0),n([ol({type:String}),os(function(t,e){void 0!==e&&this.label!==e&&this.layout(!1)})],gl.prototype,"label",void 0),n([al()],gl.prototype,"outlineOpen",void 0),n([al()],gl.prototype,"outlineWidth",void 0),n([ol({type:String}),os(function(t){if(this.mdcFoundation){const e=null===this.selected&&!!t,i=this.selected&&this.selected.value!==t;(e||i)&&this.selectByValue(t),this.reportValidity()}})],gl.prototype,"value",void 0),n([ol()],gl.prototype,"name",void 0),n([al()],gl.prototype,"selectedText",void 0),n([ol({type:String})],gl.prototype,"icon",void 0),n([al()],gl.prototype,"menuOpen",void 0),n([ol({type:String})],gl.prototype,"helper",void 0),n([ol({type:Boolean})],gl.prototype,"validateOnInitialRender",void 0),n([ol({type:String})],gl.prototype,"validationMessage",void 0),n([ol({type:Boolean})],gl.prototype,"required",void 0),n([ol({type:Boolean})],gl.prototype,"naturalMenuWidth",void 0),n([al()],gl.prototype,"isUiValid",void 0),n([ol({type:Boolean})],gl.prototype,"fixedMenuPosition",void 0),n([function(t){return ll({finisher:(e,i)=>{Object.assign(e.prototype[i],t)}})}({capture:!0})],gl.prototype,"handleTypeahead",null);
/**
     * @license
     * Copyright 2019 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
const vl=window,_l=vl.ShadowRoot&&(void 0===vl.ShadyCSS||vl.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,bl=Symbol(),yl=new WeakMap;let xl=class{constructor(t,e,i){if(this._$cssResult$=!0,i!==bl)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o;const e=this.t;if(_l&&void 0===t){const i=void 0!==e&&1===e.length;i&&(t=yl.get(e)),void 0===t&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),i&&yl.set(e,t))}return t}toString(){return this.cssText}};const $l=(t,...e)=>{const i=1===t.length?t[0]:e.reduce((e,i,s)=>e+(t=>{if(!0===t._$cssResult$)return t.cssText;if("number"==typeof t)return t;throw Error("Value passed to 'css' function must be a 'css' function result: "+t+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+t[s+1],t[0]);return new xl(i,t,bl)},wl=_l?t=>t:t=>t instanceof CSSStyleSheet?(t=>{let e="";for(const i of t.cssRules)e+=i.cssText;return(t=>new xl("string"==typeof t?t:t+"",void 0,bl))(e)})(t):t;
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */var Al;const El=window,Sl=El.trustedTypes,Cl=Sl?Sl.emptyScript:"",Tl=El.reactiveElementPolyfillSupport,Il={toAttribute(t,e){switch(e){case Boolean:t=t?Cl:null;break;case Object:case Array:t=null==t?t:JSON.stringify(t)}return t},fromAttribute(t,e){let i=t;switch(e){case Boolean:i=null!==t;break;case Number:i=null===t?null:Number(t);break;case Object:case Array:try{i=JSON.parse(t)}catch(t){i=null}}return i}},Ol=(t,e)=>e!==t&&(e==e||t==t),kl={attribute:!0,type:String,converter:Il,reflect:!1,hasChanged:Ol},Rl="finalized";let Pl=class extends HTMLElement{constructor(){super(),this._$Ei=new Map,this.isUpdatePending=!1,this.hasUpdated=!1,this._$El=null,this._$Eu()}static addInitializer(t){var e;this.finalize(),(null!==(e=this.h)&&void 0!==e?e:this.h=[]).push(t)}static get observedAttributes(){this.finalize();const t=[];return this.elementProperties.forEach((e,i)=>{const s=this._$Ep(i,e);void 0!==s&&(this._$Ev.set(s,i),t.push(s))}),t}static createProperty(t,e=kl){if(e.state&&(e.attribute=!1),this.finalize(),this.elementProperties.set(t,e),!e.noAccessor&&!this.prototype.hasOwnProperty(t)){const i="symbol"==typeof t?Symbol():"__"+t,s=this.getPropertyDescriptor(t,i,e);void 0!==s&&Object.defineProperty(this.prototype,t,s)}}static getPropertyDescriptor(t,e,i){return{get(){return this[e]},set(s){const n=this[t];this[e]=s,this.requestUpdate(t,n,i)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)||kl}static finalize(){if(this.hasOwnProperty(Rl))return!1;this[Rl]=!0;const t=Object.getPrototypeOf(this);if(t.finalize(),void 0!==t.h&&(this.h=[...t.h]),this.elementProperties=new Map(t.elementProperties),this._$Ev=new Map,this.hasOwnProperty("properties")){const t=this.properties,e=[...Object.getOwnPropertyNames(t),...Object.getOwnPropertySymbols(t)];for(const i of e)this.createProperty(i,t[i])}return this.elementStyles=this.finalizeStyles(this.styles),!0}static finalizeStyles(t){const e=[];if(Array.isArray(t)){const i=new Set(t.flat(1/0).reverse());for(const t of i)e.unshift(wl(t))}else void 0!==t&&e.push(wl(t));return e}static _$Ep(t,e){const i=e.attribute;return!1===i?void 0:"string"==typeof i?i:"string"==typeof t?t.toLowerCase():void 0}_$Eu(){var t;this._$E_=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$Eg(),this.requestUpdate(),null===(t=this.constructor.h)||void 0===t||t.forEach(t=>t(this))}addController(t){var e,i;(null!==(e=this._$ES)&&void 0!==e?e:this._$ES=[]).push(t),void 0!==this.renderRoot&&this.isConnected&&(null===(i=t.hostConnected)||void 0===i||i.call(t))}removeController(t){var e;null===(e=this._$ES)||void 0===e||e.splice(this._$ES.indexOf(t)>>>0,1)}_$Eg(){this.constructor.elementProperties.forEach((t,e)=>{this.hasOwnProperty(e)&&(this._$Ei.set(e,this[e]),delete this[e])})}createRenderRoot(){var t;const e=null!==(t=this.shadowRoot)&&void 0!==t?t:this.attachShadow(this.constructor.shadowRootOptions);return((t,e)=>{_l?t.adoptedStyleSheets=e.map(t=>t instanceof CSSStyleSheet?t:t.styleSheet):e.forEach(e=>{const i=document.createElement("style"),s=vl.litNonce;void 0!==s&&i.setAttribute("nonce",s),i.textContent=e.cssText,t.appendChild(i)})})(e,this.constructor.elementStyles),e}connectedCallback(){var t;void 0===this.renderRoot&&(this.renderRoot=this.createRenderRoot()),this.enableUpdating(!0),null===(t=this._$ES)||void 0===t||t.forEach(t=>{var e;return null===(e=t.hostConnected)||void 0===e?void 0:e.call(t)})}enableUpdating(t){}disconnectedCallback(){var t;null===(t=this._$ES)||void 0===t||t.forEach(t=>{var e;return null===(e=t.hostDisconnected)||void 0===e?void 0:e.call(t)})}attributeChangedCallback(t,e,i){this._$AK(t,i)}_$EO(t,e,i=kl){var s;const n=this.constructor._$Ep(t,i);if(void 0!==n&&!0===i.reflect){const r=(void 0!==(null===(s=i.converter)||void 0===s?void 0:s.toAttribute)?i.converter:Il).toAttribute(e,i.type);this._$El=t,null==r?this.removeAttribute(n):this.setAttribute(n,r),this._$El=null}}_$AK(t,e){var i;const s=this.constructor,n=s._$Ev.get(t);if(void 0!==n&&this._$El!==n){const t=s.getPropertyOptions(n),r="function"==typeof t.converter?{fromAttribute:t.converter}:void 0!==(null===(i=t.converter)||void 0===i?void 0:i.fromAttribute)?t.converter:Il;this._$El=n,this[n]=r.fromAttribute(e,t.type),this._$El=null}}requestUpdate(t,e,i){let s=!0;void 0!==t&&(((i=i||this.constructor.getPropertyOptions(t)).hasChanged||Ol)(this[t],e)?(this._$AL.has(t)||this._$AL.set(t,e),!0===i.reflect&&this._$El!==t&&(void 0===this._$EC&&(this._$EC=new Map),this._$EC.set(t,i))):s=!1),!this.isUpdatePending&&s&&(this._$E_=this._$Ej())}async _$Ej(){this.isUpdatePending=!0;try{await this._$E_}catch(t){Promise.reject(t)}const t=this.scheduleUpdate();return null!=t&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){var t;if(!this.isUpdatePending)return;this.hasUpdated,this._$Ei&&(this._$Ei.forEach((t,e)=>this[e]=t),this._$Ei=void 0);let e=!1;const i=this._$AL;try{e=this.shouldUpdate(i),e?(this.willUpdate(i),null===(t=this._$ES)||void 0===t||t.forEach(t=>{var e;return null===(e=t.hostUpdate)||void 0===e?void 0:e.call(t)}),this.update(i)):this._$Ek()}catch(t){throw e=!1,this._$Ek(),t}e&&this._$AE(i)}willUpdate(t){}_$AE(t){var e;null===(e=this._$ES)||void 0===e||e.forEach(t=>{var e;return null===(e=t.hostUpdated)||void 0===e?void 0:e.call(t)}),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$Ek(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$E_}shouldUpdate(t){return!0}update(t){void 0!==this._$EC&&(this._$EC.forEach((t,e)=>this._$EO(e,this[e],t)),this._$EC=void 0),this._$Ek()}updated(t){}firstUpdated(t){}};
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
var Ll;Pl[Rl]=!0,Pl.elementProperties=new Map,Pl.elementStyles=[],Pl.shadowRootOptions={mode:"open"},null==Tl||Tl({ReactiveElement:Pl}),(null!==(Al=El.reactiveElementVersions)&&void 0!==Al?Al:El.reactiveElementVersions=[]).push("1.6.3");const Ml=window,Nl=Ml.trustedTypes,Dl=Nl?Nl.createPolicy("lit-html",{createHTML:t=>t}):void 0,Hl="$lit$",Ul=`lit$${(Math.random()+"").slice(9)}$`,zl="?"+Ul,Fl=`<${zl}>`,Bl=document,Vl=()=>Bl.createComment(""),jl=t=>null===t||"object"!=typeof t&&"function"!=typeof t,Wl=Array.isArray,ql="[ \t\n\f\r]",Yl=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,Xl=/-->/g,Gl=/>/g,Kl=RegExp(`>|${ql}(?:([^\\s"'>=/]+)(${ql}*=${ql}*(?:[^ \t\n\f\r"'\`<>=]|("|')|))|$)`,"g"),Jl=/'/g,Zl=/"/g,Ql=/^(?:script|style|textarea|title)$/i,td=(t=>(e,...i)=>({_$litType$:t,strings:e,values:i}))(1),ed=Symbol.for("lit-noChange"),id=Symbol.for("lit-nothing"),sd=new WeakMap,nd=Bl.createTreeWalker(Bl,129,null,!1);function rd(t,e){if(!Array.isArray(t)||!t.hasOwnProperty("raw"))throw Error("invalid template strings array");return void 0!==Dl?Dl.createHTML(e):e}let od=class t{constructor({strings:e,_$litType$:i},s){let n;this.parts=[];let r=0,o=0;const a=e.length-1,l=this.parts,[d,c]=((t,e)=>{const i=t.length-1,s=[];let n,r=2===e?"<svg>":"",o=Yl;for(let e=0;e<i;e++){const i=t[e];let a,l,d=-1,c=0;for(;c<i.length&&(o.lastIndex=c,l=o.exec(i),null!==l);)c=o.lastIndex,o===Yl?"!--"===l[1]?o=Xl:void 0!==l[1]?o=Gl:void 0!==l[2]?(Ql.test(l[2])&&(n=RegExp("</"+l[2],"g")),o=Kl):void 0!==l[3]&&(o=Kl):o===Kl?">"===l[0]?(o=null!=n?n:Yl,d=-1):void 0===l[1]?d=-2:(d=o.lastIndex-l[2].length,a=l[1],o=void 0===l[3]?Kl:'"'===l[3]?Zl:Jl):o===Zl||o===Jl?o=Kl:o===Xl||o===Gl?o=Yl:(o=Kl,n=void 0);const h=o===Kl&&t[e+1].startsWith("/>")?" ":"";r+=o===Yl?i+Fl:d>=0?(s.push(a),i.slice(0,d)+Hl+i.slice(d)+Ul+h):i+Ul+(-2===d?(s.push(void 0),e):h)}return[rd(t,r+(t[i]||"<?>")+(2===e?"</svg>":"")),s]})(e,i);if(this.el=t.createElement(d,s),nd.currentNode=this.el.content,2===i){const t=this.el.content,e=t.firstChild;e.remove(),t.append(...e.childNodes)}for(;null!==(n=nd.nextNode())&&l.length<a;){if(1===n.nodeType){if(n.hasAttributes()){const t=[];for(const e of n.getAttributeNames())if(e.endsWith(Hl)||e.startsWith(Ul)){const i=c[o++];if(t.push(e),void 0!==i){const t=n.getAttribute(i.toLowerCase()+Hl).split(Ul),e=/([.?@])?(.*)/.exec(i);l.push({type:1,index:r,name:e[2],strings:t,ctor:"."===e[1]?hd:"?"===e[1]?ud:"@"===e[1]?md:cd})}else l.push({type:6,index:r})}for(const e of t)n.removeAttribute(e)}if(Ql.test(n.tagName)){const t=n.textContent.split(Ul),e=t.length-1;if(e>0){n.textContent=Nl?Nl.emptyScript:"";for(let i=0;i<e;i++)n.append(t[i],Vl()),nd.nextNode(),l.push({type:2,index:++r});n.append(t[e],Vl())}}}else if(8===n.nodeType)if(n.data===zl)l.push({type:2,index:r});else{let t=-1;for(;-1!==(t=n.data.indexOf(Ul,t+1));)l.push({type:7,index:r}),t+=Ul.length-1}r++}}static createElement(t,e){const i=Bl.createElement("template");return i.innerHTML=t,i}};function ad(t,e,i=t,s){var n,r,o,a;if(e===ed)return e;let l=void 0!==s?null===(n=i._$Co)||void 0===n?void 0:n[s]:i._$Cl;const d=jl(e)?void 0:e._$litDirective$;return(null==l?void 0:l.constructor)!==d&&(null===(r=null==l?void 0:l._$AO)||void 0===r||r.call(l,!1),void 0===d?l=void 0:(l=new d(t),l._$AT(t,i,s)),void 0!==s?(null!==(o=(a=i)._$Co)&&void 0!==o?o:a._$Co=[])[s]=l:i._$Cl=l),void 0!==l&&(e=ad(t,l._$AS(t,e.values),l,s)),e}let ld=class{constructor(t,e){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){var e;const{el:{content:i},parts:s}=this._$AD,n=(null!==(e=null==t?void 0:t.creationScope)&&void 0!==e?e:Bl).importNode(i,!0);nd.currentNode=n;let r=nd.nextNode(),o=0,a=0,l=s[0];for(;void 0!==l;){if(o===l.index){let e;2===l.type?e=new dd(r,r.nextSibling,this,t):1===l.type?e=new l.ctor(r,l.name,l.strings,this,t):6===l.type&&(e=new fd(r,this,t)),this._$AV.push(e),l=s[++a]}o!==(null==l?void 0:l.index)&&(r=nd.nextNode(),o++)}return nd.currentNode=Bl,n}v(t){let e=0;for(const i of this._$AV)void 0!==i&&(void 0!==i.strings?(i._$AI(t,i,e),e+=i.strings.length-2):i._$AI(t[e])),e++}},dd=class t{constructor(t,e,i,s){var n;this.type=2,this._$AH=id,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=i,this.options=s,this._$Cp=null===(n=null==s?void 0:s.isConnected)||void 0===n||n}get _$AU(){var t,e;return null!==(e=null===(t=this._$AM)||void 0===t?void 0:t._$AU)&&void 0!==e?e:this._$Cp}get parentNode(){let t=this._$AA.parentNode;const e=this._$AM;return void 0!==e&&11===(null==t?void 0:t.nodeType)&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=ad(this,t,e),jl(t)?t===id||null==t||""===t?(this._$AH!==id&&this._$AR(),this._$AH=id):t!==this._$AH&&t!==ed&&this._(t):void 0!==t._$litType$?this.g(t):void 0!==t.nodeType?this.$(t):(t=>Wl(t)||"function"==typeof(null==t?void 0:t[Symbol.iterator]))(t)?this.T(t):this._(t)}k(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}$(t){this._$AH!==t&&(this._$AR(),this._$AH=this.k(t))}_(t){this._$AH!==id&&jl(this._$AH)?this._$AA.nextSibling.data=t:this.$(Bl.createTextNode(t)),this._$AH=t}g(t){var e;const{values:i,_$litType$:s}=t,n="number"==typeof s?this._$AC(t):(void 0===s.el&&(s.el=od.createElement(rd(s.h,s.h[0]),this.options)),s);if((null===(e=this._$AH)||void 0===e?void 0:e._$AD)===n)this._$AH.v(i);else{const t=new ld(n,this),e=t.u(this.options);t.v(i),this.$(e),this._$AH=t}}_$AC(t){let e=sd.get(t.strings);return void 0===e&&sd.set(t.strings,e=new od(t)),e}T(e){Wl(this._$AH)||(this._$AH=[],this._$AR());const i=this._$AH;let s,n=0;for(const r of e)n===i.length?i.push(s=new t(this.k(Vl()),this.k(Vl()),this,this.options)):s=i[n],s._$AI(r),n++;n<i.length&&(this._$AR(s&&s._$AB.nextSibling,n),i.length=n)}_$AR(t=this._$AA.nextSibling,e){var i;for(null===(i=this._$AP)||void 0===i||i.call(this,!1,!0,e);t&&t!==this._$AB;){const e=t.nextSibling;t.remove(),t=e}}setConnected(t){var e;void 0===this._$AM&&(this._$Cp=t,null===(e=this._$AP)||void 0===e||e.call(this,t))}},cd=class{constructor(t,e,i,s,n){this.type=1,this._$AH=id,this._$AN=void 0,this.element=t,this.name=e,this._$AM=s,this.options=n,i.length>2||""!==i[0]||""!==i[1]?(this._$AH=Array(i.length-1).fill(new String),this.strings=i):this._$AH=id}get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}_$AI(t,e=this,i,s){const n=this.strings;let r=!1;if(void 0===n)t=ad(this,t,e,0),r=!jl(t)||t!==this._$AH&&t!==ed,r&&(this._$AH=t);else{const s=t;let o,a;for(t=n[0],o=0;o<n.length-1;o++)a=ad(this,s[i+o],e,o),a===ed&&(a=this._$AH[o]),r||(r=!jl(a)||a!==this._$AH[o]),a===id?t=id:t!==id&&(t+=(null!=a?a:"")+n[o+1]),this._$AH[o]=a}r&&!s&&this.j(t)}j(t){t===id?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,null!=t?t:"")}},hd=class extends cd{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===id?void 0:t}};const pd=Nl?Nl.emptyScript:"";let ud=class extends cd{constructor(){super(...arguments),this.type=4}j(t){t&&t!==id?this.element.setAttribute(this.name,pd):this.element.removeAttribute(this.name)}},md=class extends cd{constructor(t,e,i,s,n){super(t,e,i,s,n),this.type=5}_$AI(t,e=this){var i;if((t=null!==(i=ad(this,t,e,0))&&void 0!==i?i:id)===ed)return;const s=this._$AH,n=t===id&&s!==id||t.capture!==s.capture||t.once!==s.once||t.passive!==s.passive,r=t!==id&&(s===id||n);n&&this.element.removeEventListener(this.name,this,s),r&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){var e,i;"function"==typeof this._$AH?this._$AH.call(null!==(i=null===(e=this.options)||void 0===e?void 0:e.host)&&void 0!==i?i:this.element,t):this._$AH.handleEvent(t)}},fd=class{constructor(t,e,i){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=i}get _$AU(){return this._$AM._$AU}_$AI(t){ad(this,t)}};const gd=Ml.litHtmlPolyfillSupport;null==gd||gd(od,dd),(null!==(Ll=Ml.litHtmlVersions)&&void 0!==Ll?Ll:Ml.litHtmlVersions=[]).push("2.8.0");
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
var vd,_d;let bd=class extends Pl{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){var t,e;const i=super.createRenderRoot();return null!==(t=(e=this.renderOptions).renderBefore)&&void 0!==t||(e.renderBefore=i.firstChild),i}update(t){const e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=((t,e,i)=>{var s,n;const r=null!==(s=null==i?void 0:i.renderBefore)&&void 0!==s?s:e;let o=r._$litPart$;if(void 0===o){const t=null!==(n=null==i?void 0:i.renderBefore)&&void 0!==n?n:null;r._$litPart$=o=new dd(e.insertBefore(Vl(),t),t,void 0,null!=i?i:{})}return o._$AI(t),o})(e,this.renderRoot,this.renderOptions)}connectedCallback(){var t;super.connectedCallback(),null===(t=this._$Do)||void 0===t||t.setConnected(!0)}disconnectedCallback(){var t;super.disconnectedCallback(),null===(t=this._$Do)||void 0===t||t.setConnected(!1)}render(){return ed}};bd.finalized=!0,bd._$litElement$=!0,null===(vd=globalThis.litElementHydrateSupport)||void 0===vd||vd.call(globalThis,{LitElement:bd});const yd=globalThis.litElementPolyfillSupport;null==yd||yd({LitElement:bd}),(null!==(_d=globalThis.litElementVersions)&&void 0!==_d?_d:globalThis.litElementVersions=[]).push("3.3.3");
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
const xd=(t,e)=>"method"===e.kind&&e.descriptor&&!("value"in e.descriptor)?{...e,finisher(i){i.createProperty(e.key,t)}}:{kind:"field",key:Symbol(),placement:"own",descriptor:{},originalKey:e.key,initializer(){"function"==typeof e.initializer&&(this[e.key]=e.initializer.call(this))},finisher(i){i.createProperty(e.key,t)}};function $d(t){return(e,i)=>void 0!==i?((t,e,i)=>{e.constructor.createProperty(i,t)})(t,e,i):xd(t,e)}
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */function wd(t){return $d({...t,state:!0})}
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */const Ad=({finisher:t,descriptor:e})=>(i,s)=>{var n;if(void 0===s){const s=null!==(n=i.originalKey)&&void 0!==n?n:i.key,r=null!=e?{kind:"method",placement:"prototype",key:s,descriptor:e(i.key)}:{...i,key:s};return null!=t&&(r.finisher=function(e){t(e,s)}),r}{const n=i.constructor;void 0!==e&&Object.defineProperty(i,s,e(s)),null==t||t(n,s)}};
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */function Ed(t,e){return Ad({descriptor:e=>{const i={get(){var e,i;return null!==(i=null===(e=this.renderRoot)||void 0===e?void 0:e.querySelector(t))&&void 0!==i?i:null},enumerable:!0,configurable:!0};return i}})}
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
/**
     * @license
     * Copyright 2021 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
var Sd;const Cd=null!=(null===(Sd=window.HTMLSlotElement)||void 0===Sd?void 0:Sd.prototype.assignedElements)?(t,e)=>t.assignedElements(e):(t,e)=>t.assignedNodes(e).filter(t=>t.nodeType===Node.ELEMENT_NODE);
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
function Td(t,e,i){let s;return s={flatten:e},i?function(t){const{slot:e,selector:i}=null!=t?t:{};return Ad({descriptor:s=>({get(){var s;const n="slot"+(e?`[name=${e}]`:":not([name])"),r=null===(s=this.renderRoot)||void 0===s?void 0:s.querySelector(n),o=null!=r?Cd(r,t):[];return i?o.filter(t=>t.matches(i)):o},enumerable:!0,configurable:!0})})}({slot:t,flatten:e,selector:i}):Ad({descriptor:t=>({get(){var t,e;const i=null===(t=this.renderRoot)||void 0===t?void 0:t.querySelector("slot:not([name])");return null!==(e=null==i?void 0:i.assignedNodes(s))&&void 0!==e?e:[]},enumerable:!0,configurable:!0})})}
/**
     * @license
     * Copyright 2018 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */const Id=t=>null!=t?t:id;
/**
     * @license
     * Copyright 2016 Google Inc.
     *
     * Permission is hereby granted, free of charge, to any person obtaining a copy
     * of this software and associated documentation files (the "Software"), to deal
     * in the Software without restriction, including without limitation the rights
     * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
     * copies of the Software, and to permit persons to whom the Software is
     * furnished to do so, subject to the following conditions:
     *
     * The above copyright notice and this permission notice shall be included in
     * all copies or substantial portions of the Software.
     *
     * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
     * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
     * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
     * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
     * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
     * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
     * THE SOFTWARE.
     */var Od=function(){function t(t){void 0===t&&(t={}),this.adapter=t}return Object.defineProperty(t,"cssClasses",{get:function(){return{}},enumerable:!1,configurable:!0}),Object.defineProperty(t,"strings",{get:function(){return{}},enumerable:!1,configurable:!0}),Object.defineProperty(t,"numbers",{get:function(){return{}},enumerable:!1,configurable:!0}),Object.defineProperty(t,"defaultAdapter",{get:function(){return{}},enumerable:!1,configurable:!0}),t.prototype.init=function(){},t.prototype.destroy=function(){},t}(),kd="Unknown",Rd="Backspace",Pd="Enter",Ld="Spacebar",Md="PageUp",Nd="PageDown",Dd="End",Hd="Home",Ud="ArrowLeft",zd="ArrowUp",Fd="ArrowRight",Bd="ArrowDown",Vd="Delete",jd="Escape",Wd="Tab",qd=new Set;
/**
     * @license
     * Copyright 2020 Google Inc.
     *
     * Permission is hereby granted, free of charge, to any person obtaining a copy
     * of this software and associated documentation files (the "Software"), to deal
     * in the Software without restriction, including without limitation the rights
     * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
     * copies of the Software, and to permit persons to whom the Software is
     * furnished to do so, subject to the following conditions:
     *
     * The above copyright notice and this permission notice shall be included in
     * all copies or substantial portions of the Software.
     *
     * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
     * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
     * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
     * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
     * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
     * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
     * THE SOFTWARE.
     */qd.add(Rd),qd.add(Pd),qd.add(Ld),qd.add(Md),qd.add(Nd),qd.add(Dd),qd.add(Hd),qd.add(Ud),qd.add(zd),qd.add(Fd),qd.add(Bd),qd.add(Vd),qd.add(jd),qd.add(Wd);var Yd=8,Xd=13,Gd=32,Kd=33,Jd=34,Zd=35,Qd=36,tc=37,ec=38,ic=39,sc=40,nc=46,rc=27,oc=9,ac=new Map;ac.set(Yd,Rd),ac.set(Xd,Pd),ac.set(Gd,Ld),ac.set(Kd,Md),ac.set(Jd,Nd),ac.set(Zd,Dd),ac.set(Qd,Hd),ac.set(tc,Ud),ac.set(ec,zd),ac.set(ic,Fd),ac.set(sc,Bd),ac.set(nc,Vd),ac.set(rc,jd),ac.set(oc,Wd);var lc=new Set;function dc(t){var e=t.key;if(qd.has(e))return e;var i=ac.get(t.keyCode);return i||kd}
/**
     * @license
     * Copyright 2020 Google LLC
     * SPDX-License-Identifier: Apache-2.0
     */lc.add(Md),lc.add(Nd),lc.add(Dd),lc.add(Hd),lc.add(Ud),lc.add(zd),lc.add(Fd),lc.add(Bd);const cc=(t,e)=>t-e,hc=["input","button","textarea","select"];function pc(t){return t instanceof Set}const uc=t=>{const e=t===qr.UNSET_INDEX?new Set:t;return pc(e)?new Set(e):new Set([e])};class mc extends Od{constructor(t){super(Object.assign(Object.assign({},mc.defaultAdapter),t)),this.isMulti_=!1,this.wrapFocus_=!1,this.isVertical_=!0,this.selectedIndex_=qr.UNSET_INDEX,this.focusedItemIndex_=qr.UNSET_INDEX,this.useActivatedClass_=!1,this.ariaCurrentAttrValue_=null}static get strings(){return Wr}static get numbers(){return qr}static get defaultAdapter(){return{focusItemAtIndex:()=>{},getFocusedElementIndex:()=>0,getListItemCount:()=>0,isFocusInsideList:()=>!1,isRootFocused:()=>!1,notifyAction:()=>{},notifySelected:()=>{},getSelectedStateForElementIndex:()=>!1,setDisabledStateForElementIndex:()=>{},getDisabledStateForElementIndex:()=>!1,setSelectedStateForElementIndex:()=>{},setActivatedStateForElementIndex:()=>{},setTabIndexForElementIndex:()=>{},setAttributeForElementIndex:()=>{},getAttributeForElementIndex:()=>null}}setWrapFocus(t){this.wrapFocus_=t}setMulti(t){this.isMulti_=t;const e=this.selectedIndex_;if(t){if(!pc(e)){const t=e===qr.UNSET_INDEX;this.selectedIndex_=t?new Set:new Set([e])}}else if(pc(e))if(e.size){const t=Array.from(e).sort(cc);this.selectedIndex_=t[0]}else this.selectedIndex_=qr.UNSET_INDEX}setVerticalOrientation(t){this.isVertical_=t}setUseActivatedClass(t){this.useActivatedClass_=t}getSelectedIndex(){return this.selectedIndex_}setSelectedIndex(t){this.isIndexValid_(t)&&(this.isMulti_?this.setMultiSelectionAtIndex_(uc(t)):this.setSingleSelectionAtIndex_(t))}handleFocusIn(t,e){e>=0&&this.adapter.setTabIndexForElementIndex(e,0)}handleFocusOut(t,e){e>=0&&this.adapter.setTabIndexForElementIndex(e,-1),setTimeout(()=>{this.adapter.isFocusInsideList()||this.setTabindexToFirstSelectedItem_()},0)}handleKeydown(t,e,i){const s="ArrowLeft"===dc(t),n="ArrowUp"===dc(t),r="ArrowRight"===dc(t),o="ArrowDown"===dc(t),a="Home"===dc(t),l="End"===dc(t),d="Enter"===dc(t),c="Spacebar"===dc(t);if(this.adapter.isRootFocused())return void(n||l?(t.preventDefault(),this.focusLastElement()):(o||a)&&(t.preventDefault(),this.focusFirstElement()));let h,p=this.adapter.getFocusedElementIndex();if(!(-1===p&&(p=i,p<0))){if(this.isVertical_&&o||!this.isVertical_&&r)this.preventDefaultEvent(t),h=this.focusNextElement(p);else if(this.isVertical_&&n||!this.isVertical_&&s)this.preventDefaultEvent(t),h=this.focusPrevElement(p);else if(a)this.preventDefaultEvent(t),h=this.focusFirstElement();else if(l)this.preventDefaultEvent(t),h=this.focusLastElement();else if((d||c)&&e){const e=t.target;if(e&&"A"===e.tagName&&d)return;this.preventDefaultEvent(t),this.setSelectedIndexOnAction_(p,!0)}this.focusedItemIndex_=p,void 0!==h&&(this.setTabindexAtIndex_(h),this.focusedItemIndex_=h)}}handleSingleSelection(t,e,i){t!==qr.UNSET_INDEX&&(this.setSelectedIndexOnAction_(t,e,i),this.setTabindexAtIndex_(t),this.focusedItemIndex_=t)}focusNextElement(t){let e=t+1;if(e>=this.adapter.getListItemCount()){if(!this.wrapFocus_)return t;e=0}return this.adapter.focusItemAtIndex(e),e}focusPrevElement(t){let e=t-1;if(e<0){if(!this.wrapFocus_)return t;e=this.adapter.getListItemCount()-1}return this.adapter.focusItemAtIndex(e),e}focusFirstElement(){return this.adapter.focusItemAtIndex(0),0}focusLastElement(){const t=this.adapter.getListItemCount()-1;return this.adapter.focusItemAtIndex(t),t}setEnabled(t,e){this.isIndexValid_(t)&&this.adapter.setDisabledStateForElementIndex(t,!e)}preventDefaultEvent(t){const e=`${t.target.tagName}`.toLowerCase();-1===hc.indexOf(e)&&t.preventDefault()}setSingleSelectionAtIndex_(t,e=!0){this.selectedIndex_!==t&&(this.selectedIndex_!==qr.UNSET_INDEX&&(this.adapter.setSelectedStateForElementIndex(this.selectedIndex_,!1),this.useActivatedClass_&&this.adapter.setActivatedStateForElementIndex(this.selectedIndex_,!1)),e&&this.adapter.setSelectedStateForElementIndex(t,!0),this.useActivatedClass_&&this.adapter.setActivatedStateForElementIndex(t,!0),this.setAriaForSingleSelectionAtIndex_(t),this.selectedIndex_=t,this.adapter.notifySelected(t))}setMultiSelectionAtIndex_(t,e=!0){const i=((t,e)=>{const i=Array.from(t),s=Array.from(e),n={added:[],removed:[]},r=i.sort(cc),o=s.sort(cc);let a=0,l=0;for(;a<r.length||l<o.length;){const t=r[a],e=o[l];t!==e?void 0!==t&&(void 0===e||t<e)?(n.removed.push(t),a++):void 0!==e&&(void 0===t||e<t)&&(n.added.push(e),l++):(a++,l++)}return n})(uc(this.selectedIndex_),t);if(i.removed.length||i.added.length){for(const t of i.removed)e&&this.adapter.setSelectedStateForElementIndex(t,!1),this.useActivatedClass_&&this.adapter.setActivatedStateForElementIndex(t,!1);for(const t of i.added)e&&this.adapter.setSelectedStateForElementIndex(t,!0),this.useActivatedClass_&&this.adapter.setActivatedStateForElementIndex(t,!0);this.selectedIndex_=t,this.adapter.notifySelected(t,i)}}setAriaForSingleSelectionAtIndex_(t){this.selectedIndex_===qr.UNSET_INDEX&&(this.ariaCurrentAttrValue_=this.adapter.getAttributeForElementIndex(t,Wr.ARIA_CURRENT));const e=null!==this.ariaCurrentAttrValue_,i=e?Wr.ARIA_CURRENT:Wr.ARIA_SELECTED;this.selectedIndex_!==qr.UNSET_INDEX&&this.adapter.setAttributeForElementIndex(this.selectedIndex_,i,"false");const s=e?this.ariaCurrentAttrValue_:"true";this.adapter.setAttributeForElementIndex(t,i,s)}setTabindexAtIndex_(t){this.focusedItemIndex_===qr.UNSET_INDEX&&0!==t?this.adapter.setTabIndexForElementIndex(0,-1):this.focusedItemIndex_>=0&&this.focusedItemIndex_!==t&&this.adapter.setTabIndexForElementIndex(this.focusedItemIndex_,-1),this.adapter.setTabIndexForElementIndex(t,0)}setTabindexToFirstSelectedItem_(){let t=0;"number"==typeof this.selectedIndex_&&this.selectedIndex_!==qr.UNSET_INDEX?t=this.selectedIndex_:pc(this.selectedIndex_)&&this.selectedIndex_.size>0&&(t=Math.min(...this.selectedIndex_)),this.setTabindexAtIndex_(t)}isIndexValid_(t){if(t instanceof Set){if(!this.isMulti_)throw new Error("MDCListFoundation: Array of index is only supported for checkbox based list");if(0===t.size)return!0;{let e=!1;for(const i of t)if(e=this.isIndexInRange_(i),e)break;return e}}if("number"==typeof t){if(this.isMulti_)throw new Error("MDCListFoundation: Expected array of index for checkbox based list but got number: "+t);return t===qr.UNSET_INDEX||this.isIndexInRange_(t)}return!1}isIndexInRange_(t){const e=this.adapter.getListItemCount();return t>=0&&t<e}setSelectedIndexOnAction_(t,e,i){if(this.adapter.getDisabledStateForElementIndex(t))return;let s=t;if(this.isMulti_&&(s=new Set([t])),this.isIndexValid_(s)){if(this.isMulti_)this.toggleMultiAtIndex(t,i,e);else if(e||i)this.setSingleSelectionAtIndex_(t,e);else{this.selectedIndex_===t&&this.setSingleSelectionAtIndex_(qr.UNSET_INDEX)}e&&this.adapter.notifyAction(t)}}toggleMultiAtIndex(t,e,i=!0){let s=!1;s=void 0===e?!this.adapter.getSelectedStateForElementIndex(t):e;const n=uc(this.selectedIndex_);s?n.add(t):n.delete(t),this.setMultiSelectionAtIndex_(n,i)}}
/**
     * @license
     * Copyright 2020 Google LLC
     * SPDX-License-Identifier: Apache-2.0
     */const fc=t=>t.hasAttribute("mwc-list-item");function gc(){const t=this.itemsReadyResolver;this.itemsReady=new Promise(t=>this.itemsReadyResolver=t),t()}class vc extends Qi{constructor(){super(),this.mdcAdapter=null,this.mdcFoundationClass=mc,this.activatable=!1,this.multi=!1,this.wrapFocus=!1,this.itemRoles=null,this.innerRole=null,this.innerAriaLabel=null,this.rootTabbable=!1,this.previousTabindex=null,this.noninteractive=!1,this.itemsReadyResolver=()=>{},this.itemsReady=Promise.resolve([]),this.items_=[];const t=function(t,e=50){let i;return function(s=!0){clearTimeout(i),i=setTimeout(()=>{t(s)},e)}}(this.layout.bind(this));this.debouncedLayout=(e=!0)=>{gc.call(this),t(e)}}async getUpdateComplete(){const t=await super.getUpdateComplete();return await this.itemsReady,t}get items(){return this.items_}updateItems(){var t;const e=null!==(t=this.assignedElements)&&void 0!==t?t:[],i=[];for(const t of e)fc(t)&&(i.push(t),t._managingList=this),t.hasAttribute("divider")&&!t.hasAttribute("role")&&t.setAttribute("role","separator");this.items_=i;const s=new Set;if(this.items_.forEach((t,e)=>{this.itemRoles?t.setAttribute("role",this.itemRoles):t.removeAttribute("role"),t.selected&&s.add(e)}),this.multi)this.select(s);else{const t=s.size?s.entries().next().value[1]:-1;this.select(t)}const n=new Event("items-updated",{bubbles:!0,composed:!0});this.dispatchEvent(n)}get selected(){const t=this.index;if(!pc(t))return-1===t?null:this.items[t];const e=[];for(const i of t)e.push(this.items[i]);return e}get index(){return this.mdcFoundation?this.mdcFoundation.getSelectedIndex():-1}render(){const t=null===this.innerRole?void 0:this.innerRole,e=null===this.innerAriaLabel?void 0:this.innerAriaLabel,i=this.rootTabbable?"0":"-1";return td`
      <!-- @ts-ignore -->
      <ul
          tabindex=${i}
          role="${Id(t)}"
          aria-label="${Id(e)}"
          class="mdc-deprecated-list"
          @keydown=${this.onKeydown}
          @focusin=${this.onFocusIn}
          @focusout=${this.onFocusOut}
          @request-selected=${this.onRequestSelected}
          @list-item-rendered=${this.onListItemConnected}>
        <slot></slot>
        ${this.renderPlaceholder()}
      </ul>
    `}renderPlaceholder(){var t;const e=null!==(t=this.assignedElements)&&void 0!==t?t:[];return void 0!==this.emptyMessage&&0===e.length?td`
        <mwc-list-item noninteractive>${this.emptyMessage}</mwc-list-item>
      `:null}firstUpdated(){super.firstUpdated(),this.items.length||(this.mdcFoundation.setMulti(this.multi),this.layout())}onFocusIn(t){if(this.mdcFoundation&&this.mdcRoot){const e=this.getIndexOfTarget(t);this.mdcFoundation.handleFocusIn(t,e)}}onFocusOut(t){if(this.mdcFoundation&&this.mdcRoot){const e=this.getIndexOfTarget(t);this.mdcFoundation.handleFocusOut(t,e)}}onKeydown(t){if(this.mdcFoundation&&this.mdcRoot){const e=this.getIndexOfTarget(t),i=t.target,s=fc(i);this.mdcFoundation.handleKeydown(t,s,e)}}onRequestSelected(t){if(this.mdcFoundation){let e=this.getIndexOfTarget(t);if(-1===e&&(this.layout(),e=this.getIndexOfTarget(t),-1===e))return;if(this.items[e].disabled)return;const i=t.detail.selected,s=t.detail.source;this.mdcFoundation.handleSingleSelection(e,"interaction"===s,i),t.stopPropagation()}}getIndexOfTarget(t){const e=this.items,i=t.composedPath();for(const t of i){let i=-1;if(Yi(t)&&fc(t)&&(i=e.indexOf(t)),-1!==i)return i}return-1}createAdapter(){return this.mdcAdapter={getListItemCount:()=>this.mdcRoot?this.items.length:0,getFocusedElementIndex:this.getFocusedItemIndex,getAttributeForElementIndex:(t,e)=>{if(!this.mdcRoot)return"";const i=this.items[t];return i?i.getAttribute(e):""},setAttributeForElementIndex:(t,e,i)=>{if(!this.mdcRoot)return;const s=this.items[t];s&&s.setAttribute(e,i)},focusItemAtIndex:t=>{const e=this.items[t];e&&e.focus()},setTabIndexForElementIndex:(t,e)=>{const i=this.items[t];i&&(i.tabindex=e)},notifyAction:t=>{const e={bubbles:!0,composed:!0};e.detail={index:t};const i=new CustomEvent("action",e);this.dispatchEvent(i)},notifySelected:(t,e)=>{const i={bubbles:!0,composed:!0};i.detail={index:t,diff:e};const s=new CustomEvent("selected",i);this.dispatchEvent(s)},isFocusInsideList:()=>Zi(this),isRootFocused:()=>{const t=this.mdcRoot;return t.getRootNode().activeElement===t},setDisabledStateForElementIndex:(t,e)=>{const i=this.items[t];i&&(i.disabled=e)},getDisabledStateForElementIndex:t=>{const e=this.items[t];return!!e&&e.disabled},setSelectedStateForElementIndex:(t,e)=>{const i=this.items[t];i&&(i.selected=e)},getSelectedStateForElementIndex:t=>{const e=this.items[t];return!!e&&e.selected},setActivatedStateForElementIndex:(t,e)=>{const i=this.items[t];i&&(i.activated=e)}},this.mdcAdapter}selectUi(t,e=!1){const i=this.items[t];i&&(i.selected=!0,i.activated=e)}deselectUi(t){const e=this.items[t];e&&(e.selected=!1,e.activated=!1)}select(t){this.mdcFoundation&&this.mdcFoundation.setSelectedIndex(t)}toggle(t,e){this.multi&&this.mdcFoundation.toggleMultiAtIndex(t,e)}onListItemConnected(t){const e=t.target;this.layout(-1===this.items.indexOf(e))}layout(t=!0){t&&this.updateItems();const e=this.items[0];for(const t of this.items)t.tabindex=-1;e&&(this.noninteractive?this.previousTabindex||(this.previousTabindex=e):e.tabindex=0),this.itemsReadyResolver()}getFocusedItemIndex(){if(!this.mdcRoot)return-1;if(!this.items.length)return-1;const t=Ji();if(!t.length)return-1;for(let e=t.length-1;e>=0;e--){const i=t[e];if(fc(i))return this.items.indexOf(i)}return-1}focusItemAtIndex(t){for(const t of this.items)if(0===t.tabindex){t.tabindex=-1;break}this.items[t].tabindex=0,this.items[t].focus()}focus(){const t=this.mdcRoot;t&&t.focus()}blur(){const t=this.mdcRoot;t&&t.blur()}}n([$d({type:String})],vc.prototype,"emptyMessage",void 0),n([Ed(".mdc-deprecated-list")],vc.prototype,"mdcRoot",void 0),n([Td("",!0,"*")],vc.prototype,"assignedElements",void 0),n([Td("",!0,'[tabindex="0"]')],vc.prototype,"tabbableElements",void 0),n([$d({type:Boolean}),os(function(t){this.mdcFoundation&&this.mdcFoundation.setUseActivatedClass(t)})],vc.prototype,"activatable",void 0),n([$d({type:Boolean}),os(function(t,e){this.mdcFoundation&&this.mdcFoundation.setMulti(t),void 0!==e&&this.layout()})],vc.prototype,"multi",void 0),n([$d({type:Boolean}),os(function(t){this.mdcFoundation&&this.mdcFoundation.setWrapFocus(t)})],vc.prototype,"wrapFocus",void 0),n([$d({type:String}),os(function(t,e){void 0!==e&&this.updateItems()})],vc.prototype,"itemRoles",void 0),n([$d({type:String})],vc.prototype,"innerRole",void 0),n([$d({type:String})],vc.prototype,"innerAriaLabel",void 0),n([$d({type:Boolean})],vc.prototype,"rootTabbable",void 0),n([$d({type:Boolean,reflect:!0}),os(function(t){var e,i;if(t){const t=null!==(i=null===(e=this.tabbableElements)||void 0===e?void 0:e[0])&&void 0!==i?i:null;this.previousTabindex=t,t&&t.setAttribute("tabindex","-1")}else!t&&this.previousTabindex&&(this.previousTabindex.setAttribute("tabindex","0"),this.previousTabindex=null)})],vc.prototype,"noninteractive",void 0);
/**
     * @license
     * Copyright 2020 Google LLC
     * SPDX-License-Identifier: Apache-2.0
     */
class _c{constructor(t){this.startPress=e=>{t().then(t=>{t&&t.startPress(e)})},this.endPress=()=>{t().then(t=>{t&&t.endPress()})},this.startFocus=()=>{t().then(t=>{t&&t.startFocus()})},this.endFocus=()=>{t().then(t=>{t&&t.endFocus()})},this.startHover=()=>{t().then(t=>{t&&t.startHover()})},this.endHover=()=>{t().then(t=>{t&&t.endHover()})}}}
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */const bc=1;let yc=class{constructor(t){}get _$AU(){return this._$AM._$AU}_$AT(t,e,i){this._$Ct=t,this._$AM=e,this._$Ci=i}_$AS(t,e){return this.update(t,e)}update(t,e){return this.render(...e)}};
/**
     * @license
     * Copyright 2018 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */const xc=(t=>(...e)=>({_$litDirective$:t,values:e}))(class extends yc{constructor(t){var e;if(super(t),t.type!==bc||"class"!==t.name||(null===(e=t.strings)||void 0===e?void 0:e.length)>2)throw Error("`classMap()` can only be used in the `class` attribute and must be the only part in the attribute.")}render(t){return" "+Object.keys(t).filter(e=>t[e]).join(" ")+" "}update(t,[e]){var i,s;if(void 0===this.it){this.it=new Set,void 0!==t.strings&&(this.nt=new Set(t.strings.join(" ").split(/\s/).filter(t=>""!==t)));for(const t in e)e[t]&&!(null===(i=this.nt)||void 0===i?void 0:i.has(t))&&this.it.add(t);return this.render(e)}const n=t.element.classList;this.it.forEach(t=>{t in e||(n.remove(t),this.it.delete(t))});for(const t in e){const i=!!e[t];i===this.it.has(t)||(null===(s=this.nt)||void 0===s?void 0:s.has(t))||(i?(n.add(t),this.it.add(t)):(n.remove(t),this.it.delete(t)))}return ed}});
/**
     * @license
     * Copyright 2020 Google LLC
     * SPDX-License-Identifier: Apache-2.0
     */class $c extends bd{constructor(){super(...arguments),this.value="",this.group=null,this.tabindex=-1,this.disabled=!1,this.twoline=!1,this.activated=!1,this.graphic=null,this.multipleGraphics=!1,this.hasMeta=!1,this.noninteractive=!1,this.selected=!1,this.shouldRenderRipple=!1,this._managingList=null,this.boundOnClick=this.onClick.bind(this),this._firstChanged=!0,this._skipPropRequest=!1,this.rippleHandlers=new _c(()=>(this.shouldRenderRipple=!0,this.ripple)),this.listeners=[{target:this,eventNames:["click"],cb:()=>{this.onClick()}},{target:this,eventNames:["mouseenter"],cb:this.rippleHandlers.startHover},{target:this,eventNames:["mouseleave"],cb:this.rippleHandlers.endHover},{target:this,eventNames:["focus"],cb:this.rippleHandlers.startFocus},{target:this,eventNames:["blur"],cb:this.rippleHandlers.endFocus},{target:this,eventNames:["mousedown","touchstart"],cb:t=>{const e=t.type;this.onDown("mousedown"===e?"mouseup":"touchend",t)}}]}get text(){const t=this.textContent;return t?t.trim():""}render(){const t=this.renderText(),e=this.graphic?this.renderGraphic():td``,i=this.hasMeta?this.renderMeta():td``;return td`
      ${this.renderRipple()}
      ${e}
      ${t}
      ${i}`}renderRipple(){return this.shouldRenderRipple?td`
      <mwc-ripple
        .activated=${this.activated}>
      </mwc-ripple>`:this.activated?td`<div class="fake-activated-ripple"></div>`:""}renderGraphic(){const t={multi:this.multipleGraphics};return td`
      <span class="mdc-deprecated-list-item__graphic material-icons ${xc(t)}">
        <slot name="graphic"></slot>
      </span>`}renderMeta(){return td`
      <span class="mdc-deprecated-list-item__meta material-icons">
        <slot name="meta"></slot>
      </span>`}renderText(){const t=this.twoline?this.renderTwoline():this.renderSingleLine();return td`
      <span class="mdc-deprecated-list-item__text">
        ${t}
      </span>`}renderSingleLine(){return td`<slot></slot>`}renderTwoline(){return td`
      <span class="mdc-deprecated-list-item__primary-text">
        <slot></slot>
      </span>
      <span class="mdc-deprecated-list-item__secondary-text">
        <slot name="secondary"></slot>
      </span>
    `}onClick(){this.fireRequestSelected(!this.selected,"interaction")}onDown(t,e){const i=()=>{window.removeEventListener(t,i),this.rippleHandlers.endPress()};window.addEventListener(t,i),this.rippleHandlers.startPress(e)}fireRequestSelected(t,e){if(this.noninteractive)return;const i=new CustomEvent("request-selected",{bubbles:!0,composed:!0,detail:{source:e,selected:t}});this.dispatchEvent(i)}connectedCallback(){super.connectedCallback(),this.noninteractive||this.setAttribute("mwc-list-item","");for(const t of this.listeners)for(const e of t.eventNames)t.target.addEventListener(e,t.cb,{passive:!0})}disconnectedCallback(){super.disconnectedCallback();for(const t of this.listeners)for(const e of t.eventNames)t.target.removeEventListener(e,t.cb);this._managingList&&(this._managingList.debouncedLayout?this._managingList.debouncedLayout(!0):this._managingList.layout(!0))}firstUpdated(){const t=new Event("list-item-rendered",{bubbles:!0,composed:!0});this.dispatchEvent(t)}}n([Ed("slot")],$c.prototype,"slotElement",void 0),n([function(t){return Ad({descriptor:e=>({async get(){var e;return await this.updateComplete,null===(e=this.renderRoot)||void 0===e?void 0:e.querySelector(t)},enumerable:!0,configurable:!0})})}("mwc-ripple")],$c.prototype,"ripple",void 0),n([$d({type:String})],$c.prototype,"value",void 0),n([$d({type:String,reflect:!0})],$c.prototype,"group",void 0),n([$d({type:Number,reflect:!0})],$c.prototype,"tabindex",void 0),n([$d({type:Boolean,reflect:!0}),os(function(t){t?this.setAttribute("aria-disabled","true"):this.setAttribute("aria-disabled","false")})],$c.prototype,"disabled",void 0),n([$d({type:Boolean,reflect:!0})],$c.prototype,"twoline",void 0),n([$d({type:Boolean,reflect:!0})],$c.prototype,"activated",void 0),n([$d({type:String,reflect:!0})],$c.prototype,"graphic",void 0),n([$d({type:Boolean})],$c.prototype,"multipleGraphics",void 0),n([$d({type:Boolean})],$c.prototype,"hasMeta",void 0),n([$d({type:Boolean,reflect:!0}),os(function(t){t?(this.removeAttribute("aria-checked"),this.removeAttribute("mwc-list-item"),this.selected=!1,this.activated=!1,this.tabIndex=-1):this.setAttribute("mwc-list-item","")})],$c.prototype,"noninteractive",void 0),n([$d({type:Boolean,reflect:!0}),os(function(t){const e=this.getAttribute("role"),i="gridcell"===e||"option"===e||"row"===e||"tab"===e;i&&t?this.setAttribute("aria-selected","true"):i&&this.setAttribute("aria-selected","false"),this._firstChanged?this._firstChanged=!1:this._skipPropRequest||this.fireRequestSelected(t,"property")})],$c.prototype,"selected",void 0),n([wd()],$c.prototype,"shouldRenderRipple",void 0),n([wd()],$c.prototype,"_managingList",void 0);
/**
     * @license
     * Copyright 2018 Google Inc.
     *
     * Permission is hereby granted, free of charge, to any person obtaining a copy
     * of this software and associated documentation files (the "Software"), to deal
     * in the Software without restriction, including without limitation the rights
     * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
     * copies of the Software, and to permit persons to whom the Software is
     * furnished to do so, subject to the following conditions:
     *
     * The above copyright notice and this permission notice shall be included in
     * all copies or substantial portions of the Software.
     *
     * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
     * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
     * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
     * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
     * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
     * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
     * THE SOFTWARE.
     */
var wc,Ac={MENU_SELECTED_LIST_ITEM:"mdc-menu-item--selected",MENU_SELECTION_GROUP:"mdc-menu__selection-group",ROOT:"mdc-menu"},Ec={ARIA_CHECKED_ATTR:"aria-checked",ARIA_DISABLED_ATTR:"aria-disabled",CHECKBOX_SELECTOR:'input[type="checkbox"]',LIST_SELECTOR:".mdc-list,.mdc-deprecated-list",SELECTED_EVENT:"MDCMenu:selected",SKIP_RESTORE_FOCUS:"data-menu-item-skip-restore-focus"},Sc={FOCUS_ROOT_INDEX:-1};!function(t){t[t.NONE=0]="NONE",t[t.LIST_ROOT=1]="LIST_ROOT",t[t.FIRST_ITEM=2]="FIRST_ITEM",t[t.LAST_ITEM=3]="LAST_ITEM"}(wc||(wc={}));
/**
     * @license
     * Copyright 2016 Google Inc.
     *
     * Permission is hereby granted, free of charge, to any person obtaining a copy
     * of this software and associated documentation files (the "Software"), to deal
     * in the Software without restriction, including without limitation the rights
     * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
     * copies of the Software, and to permit persons to whom the Software is
     * furnished to do so, subject to the following conditions:
     *
     * The above copyright notice and this permission notice shall be included in
     * all copies or substantial portions of the Software.
     *
     * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
     * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
     * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
     * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
     * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
     * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
     * THE SOFTWARE.
     */
var Cc=function(){function t(t){void 0===t&&(t={}),this.adapter=t}return Object.defineProperty(t,"cssClasses",{get:function(){return{}},enumerable:!1,configurable:!0}),Object.defineProperty(t,"strings",{get:function(){return{}},enumerable:!1,configurable:!0}),Object.defineProperty(t,"numbers",{get:function(){return{}},enumerable:!1,configurable:!0}),Object.defineProperty(t,"defaultAdapter",{get:function(){return{}},enumerable:!1,configurable:!0}),t.prototype.init=function(){},t.prototype.destroy=function(){},t}(),Tc=function(){function t(t){void 0===t&&(t={}),this.adapter=t}return Object.defineProperty(t,"cssClasses",{get:function(){return{}},enumerable:!1,configurable:!0}),Object.defineProperty(t,"strings",{get:function(){return{}},enumerable:!1,configurable:!0}),Object.defineProperty(t,"numbers",{get:function(){return{}},enumerable:!1,configurable:!0}),Object.defineProperty(t,"defaultAdapter",{get:function(){return{}},enumerable:!1,configurable:!0}),t.prototype.init=function(){},t.prototype.destroy=function(){},t}(),Ic=function(t){function e(i){var n=t.call(this,s(s({},e.defaultAdapter),i))||this;return n.isSurfaceOpen=!1,n.isQuickOpen=!1,n.isHoistedElement=!1,n.isFixedPosition=!1,n.isHorizontallyCenteredOnViewport=!1,n.maxHeight=0,n.openBottomBias=0,n.openAnimationEndTimerId=0,n.closeAnimationEndTimerId=0,n.animationRequestId=0,n.anchorCorner=Xo.TOP_START,n.originCorner=Xo.TOP_START,n.anchorMargin={top:0,right:0,bottom:0,left:0},n.position={x:0,y:0},n}return i(e,t),Object.defineProperty(e,"cssClasses",{get:function(){return Go},enumerable:!1,configurable:!0}),Object.defineProperty(e,"strings",{get:function(){return Ko},enumerable:!1,configurable:!0}),Object.defineProperty(e,"numbers",{get:function(){return Jo},enumerable:!1,configurable:!0}),Object.defineProperty(e,"Corner",{get:function(){return Xo},enumerable:!1,configurable:!0}),Object.defineProperty(e,"defaultAdapter",{get:function(){return{addClass:function(){},removeClass:function(){},hasClass:function(){return!1},hasAnchor:function(){return!1},isElementInContainer:function(){return!1},isFocused:function(){return!1},isRtl:function(){return!1},getInnerDimensions:function(){return{height:0,width:0}},getAnchorDimensions:function(){return null},getWindowDimensions:function(){return{height:0,width:0}},getBodyDimensions:function(){return{height:0,width:0}},getWindowScroll:function(){return{x:0,y:0}},setPosition:function(){},setMaxHeight:function(){},setTransformOrigin:function(){},saveFocus:function(){},restoreFocus:function(){},notifyClose:function(){},notifyClosing:function(){},notifyOpen:function(){},notifyOpening:function(){}}},enumerable:!1,configurable:!0}),e.prototype.init=function(){var t=e.cssClasses,i=t.ROOT,s=t.OPEN;if(!this.adapter.hasClass(i))throw new Error(i+" class required in root element.");this.adapter.hasClass(s)&&(this.isSurfaceOpen=!0)},e.prototype.destroy=function(){clearTimeout(this.openAnimationEndTimerId),clearTimeout(this.closeAnimationEndTimerId),cancelAnimationFrame(this.animationRequestId)},e.prototype.setAnchorCorner=function(t){this.anchorCorner=t},e.prototype.flipCornerHorizontally=function(){this.originCorner=this.originCorner^Yo.RIGHT},e.prototype.setAnchorMargin=function(t){this.anchorMargin.top=t.top||0,this.anchorMargin.right=t.right||0,this.anchorMargin.bottom=t.bottom||0,this.anchorMargin.left=t.left||0},e.prototype.setIsHoisted=function(t){this.isHoistedElement=t},e.prototype.setFixedPosition=function(t){this.isFixedPosition=t},e.prototype.isFixed=function(){return this.isFixedPosition},e.prototype.setAbsolutePosition=function(t,e){this.position.x=this.isFinite(t)?t:0,this.position.y=this.isFinite(e)?e:0},e.prototype.setIsHorizontallyCenteredOnViewport=function(t){this.isHorizontallyCenteredOnViewport=t},e.prototype.setQuickOpen=function(t){this.isQuickOpen=t},e.prototype.setMaxHeight=function(t){this.maxHeight=t},e.prototype.setOpenBottomBias=function(t){this.openBottomBias=t},e.prototype.isOpen=function(){return this.isSurfaceOpen},e.prototype.open=function(){var t=this;this.isSurfaceOpen||(this.adapter.notifyOpening(),this.adapter.saveFocus(),this.isQuickOpen?(this.isSurfaceOpen=!0,this.adapter.addClass(e.cssClasses.OPEN),this.dimensions=this.adapter.getInnerDimensions(),this.autoposition(),this.adapter.notifyOpen()):(this.adapter.addClass(e.cssClasses.ANIMATING_OPEN),this.animationRequestId=requestAnimationFrame(function(){t.dimensions=t.adapter.getInnerDimensions(),t.autoposition(),t.adapter.addClass(e.cssClasses.OPEN),t.openAnimationEndTimerId=setTimeout(function(){t.openAnimationEndTimerId=0,t.adapter.removeClass(e.cssClasses.ANIMATING_OPEN),t.adapter.notifyOpen()},Jo.TRANSITION_OPEN_DURATION)}),this.isSurfaceOpen=!0))},e.prototype.close=function(t){var i=this;if(void 0===t&&(t=!1),this.isSurfaceOpen){if(this.adapter.notifyClosing(),this.isQuickOpen)return this.isSurfaceOpen=!1,t||this.maybeRestoreFocus(),this.adapter.removeClass(e.cssClasses.OPEN),this.adapter.removeClass(e.cssClasses.IS_OPEN_BELOW),void this.adapter.notifyClose();this.adapter.addClass(e.cssClasses.ANIMATING_CLOSED),requestAnimationFrame(function(){i.adapter.removeClass(e.cssClasses.OPEN),i.adapter.removeClass(e.cssClasses.IS_OPEN_BELOW),i.closeAnimationEndTimerId=setTimeout(function(){i.closeAnimationEndTimerId=0,i.adapter.removeClass(e.cssClasses.ANIMATING_CLOSED),i.adapter.notifyClose()},Jo.TRANSITION_CLOSE_DURATION)}),this.isSurfaceOpen=!1,t||this.maybeRestoreFocus()}},e.prototype.handleBodyClick=function(t){var e=t.target;this.adapter.isElementInContainer(e)||this.close()},e.prototype.handleKeydown=function(t){var e=t.keyCode;("Escape"===t.key||27===e)&&this.close()},e.prototype.autoposition=function(){var t;this.measurements=this.getAutoLayoutmeasurements();var i=this.getoriginCorner(),s=this.getMenuSurfaceMaxHeight(i),n=this.hasBit(i,Yo.BOTTOM)?"bottom":"top",r=this.hasBit(i,Yo.RIGHT)?"right":"left",o=this.getHorizontalOriginOffset(i),a=this.getVerticalOriginOffset(i),l=this.measurements,d=l.anchorSize,c=l.surfaceSize,h=((t={})[r]=o,t[n]=a,t);d.width/c.width>Jo.ANCHOR_TO_MENU_SURFACE_WIDTH_RATIO&&(r="center"),(this.isHoistedElement||this.isFixedPosition)&&this.adjustPositionForHoistedElement(h),this.adapter.setTransformOrigin(r+" "+n),this.adapter.setPosition(h),this.adapter.setMaxHeight(s?s+"px":""),this.hasBit(i,Yo.BOTTOM)||this.adapter.addClass(e.cssClasses.IS_OPEN_BELOW)},e.prototype.getAutoLayoutmeasurements=function(){var t=this.adapter.getAnchorDimensions(),e=this.adapter.getBodyDimensions(),i=this.adapter.getWindowDimensions(),s=this.adapter.getWindowScroll();return t||(t={top:this.position.y,right:this.position.x,bottom:this.position.y,left:this.position.x,width:0,height:0}),{anchorSize:t,bodySize:e,surfaceSize:this.dimensions,viewportDistance:{top:t.top,right:i.width-t.right,bottom:i.height-t.bottom,left:t.left},viewportSize:i,windowScroll:s}},e.prototype.getoriginCorner=function(){var t,i,s=this.originCorner,n=this.measurements,r=n.viewportDistance,o=n.anchorSize,a=n.surfaceSize,l=e.numbers.MARGIN_TO_EDGE;this.hasBit(this.anchorCorner,Yo.BOTTOM)?(t=r.top-l+this.anchorMargin.bottom,i=r.bottom-l-this.anchorMargin.bottom):(t=r.top-l+this.anchorMargin.top,i=r.bottom-l+o.height-this.anchorMargin.top),!(i-a.height>0)&&t>i+this.openBottomBias&&(s=this.setBit(s,Yo.BOTTOM));var d,c,h=this.adapter.isRtl(),p=this.hasBit(this.anchorCorner,Yo.FLIP_RTL),u=this.hasBit(this.anchorCorner,Yo.RIGHT)||this.hasBit(s,Yo.RIGHT),m=!1;(m=h&&p?!u:u)?(d=r.left+o.width+this.anchorMargin.right,c=r.right-this.anchorMargin.right):(d=r.left+this.anchorMargin.left,c=r.right+o.width-this.anchorMargin.left);var f=d-a.width>0,g=c-a.width>0,v=this.hasBit(s,Yo.FLIP_RTL)&&this.hasBit(s,Yo.RIGHT);return g&&v&&h||!f&&v?s=this.unsetBit(s,Yo.RIGHT):(f&&m&&h||f&&!m&&u||!g&&d>=c)&&(s=this.setBit(s,Yo.RIGHT)),s},e.prototype.getMenuSurfaceMaxHeight=function(t){if(this.maxHeight>0)return this.maxHeight;var i=this.measurements.viewportDistance,s=0,n=this.hasBit(t,Yo.BOTTOM),r=this.hasBit(this.anchorCorner,Yo.BOTTOM),o=e.numbers.MARGIN_TO_EDGE;return n?(s=i.top+this.anchorMargin.top-o,r||(s+=this.measurements.anchorSize.height)):(s=i.bottom-this.anchorMargin.bottom+this.measurements.anchorSize.height-o,r&&(s-=this.measurements.anchorSize.height)),s},e.prototype.getHorizontalOriginOffset=function(t){var e=this.measurements.anchorSize,i=this.hasBit(t,Yo.RIGHT),s=this.hasBit(this.anchorCorner,Yo.RIGHT);if(i){var n=s?e.width-this.anchorMargin.left:this.anchorMargin.right;return this.isHoistedElement||this.isFixedPosition?n-(this.measurements.viewportSize.width-this.measurements.bodySize.width):n}return s?e.width-this.anchorMargin.right:this.anchorMargin.left},e.prototype.getVerticalOriginOffset=function(t){var e=this.measurements.anchorSize,i=this.hasBit(t,Yo.BOTTOM),s=this.hasBit(this.anchorCorner,Yo.BOTTOM);return i?s?e.height-this.anchorMargin.top:-this.anchorMargin.bottom:s?e.height+this.anchorMargin.bottom:this.anchorMargin.top},e.prototype.adjustPositionForHoistedElement=function(t){var e,i,s=this.measurements,n=s.windowScroll,o=s.viewportDistance,a=s.surfaceSize,l=s.viewportSize,d=Object.keys(t);try{for(var c=r(d),h=c.next();!h.done;h=c.next()){var p=h.value,u=t[p]||0;!this.isHorizontallyCenteredOnViewport||"left"!==p&&"right"!==p?(u+=o[p],this.isFixedPosition||("top"===p?u+=n.y:"bottom"===p?u-=n.y:"left"===p?u+=n.x:u-=n.x),t[p]=u):t[p]=(l.width-a.width)/2}}catch(t){e={error:t}}finally{try{h&&!h.done&&(i=c.return)&&i.call(c)}finally{if(e)throw e.error}}},e.prototype.maybeRestoreFocus=function(){var t=this,e=this.adapter.isFocused(),i=this.adapter.getOwnerDocument?this.adapter.getOwnerDocument():document,s=i.activeElement&&this.adapter.isElementInContainer(i.activeElement);(e||s)&&setTimeout(function(){t.adapter.restoreFocus()},Jo.TOUCH_EVENT_WAIT_MS)},e.prototype.hasBit=function(t,e){return Boolean(t&e)},e.prototype.setBit=function(t,e){return t|e},e.prototype.unsetBit=function(t,e){return t^e},e.prototype.isFinite=function(t){return"number"==typeof t&&isFinite(t)},e}(Tc),Oc=function(t){function e(i){var n=t.call(this,s(s({},e.defaultAdapter),i))||this;return n.closeAnimationEndTimerId=0,n.defaultFocusState=wc.LIST_ROOT,n.selectedIndex=-1,n}return i(e,t),Object.defineProperty(e,"cssClasses",{get:function(){return Ac},enumerable:!1,configurable:!0}),Object.defineProperty(e,"strings",{get:function(){return Ec},enumerable:!1,configurable:!0}),Object.defineProperty(e,"numbers",{get:function(){return Sc},enumerable:!1,configurable:!0}),Object.defineProperty(e,"defaultAdapter",{get:function(){return{addClassToElementAtIndex:function(){},removeClassFromElementAtIndex:function(){},addAttributeToElementAtIndex:function(){},removeAttributeFromElementAtIndex:function(){},getAttributeFromElementAtIndex:function(){return null},elementContainsClass:function(){return!1},closeSurface:function(){},getElementIndex:function(){return-1},notifySelected:function(){},getMenuItemCount:function(){return 0},focusItemAtIndex:function(){},focusListRoot:function(){},getSelectedSiblingOfItemAtIndex:function(){return-1},isSelectableItemAtIndex:function(){return!1}}},enumerable:!1,configurable:!0}),e.prototype.destroy=function(){this.closeAnimationEndTimerId&&clearTimeout(this.closeAnimationEndTimerId),this.adapter.closeSurface()},e.prototype.handleKeydown=function(t){var e=t.key,i=t.keyCode;("Tab"===e||9===i)&&this.adapter.closeSurface(!0)},e.prototype.handleItemAction=function(t){var e=this,i=this.adapter.getElementIndex(t);if(!(i<0)){this.adapter.notifySelected({index:i});var s="true"===this.adapter.getAttributeFromElementAtIndex(i,Ec.SKIP_RESTORE_FOCUS);this.adapter.closeSurface(s),this.closeAnimationEndTimerId=setTimeout(function(){var i=e.adapter.getElementIndex(t);i>=0&&e.adapter.isSelectableItemAtIndex(i)&&e.setSelectedIndex(i)},Ic.numbers.TRANSITION_CLOSE_DURATION)}},e.prototype.handleMenuSurfaceOpened=function(){switch(this.defaultFocusState){case wc.FIRST_ITEM:this.adapter.focusItemAtIndex(0);break;case wc.LAST_ITEM:this.adapter.focusItemAtIndex(this.adapter.getMenuItemCount()-1);break;case wc.NONE:break;default:this.adapter.focusListRoot()}},e.prototype.setDefaultFocusState=function(t){this.defaultFocusState=t},e.prototype.getSelectedIndex=function(){return this.selectedIndex},e.prototype.setSelectedIndex=function(t){if(this.validatedIndex(t),!this.adapter.isSelectableItemAtIndex(t))throw new Error("MDCMenuFoundation: No selection group at specified index.");var e=this.adapter.getSelectedSiblingOfItemAtIndex(t);e>=0&&(this.adapter.removeAttributeFromElementAtIndex(e,Ec.ARIA_CHECKED_ATTR),this.adapter.removeClassFromElementAtIndex(e,Ac.MENU_SELECTED_LIST_ITEM)),this.adapter.addClassToElementAtIndex(t,Ac.MENU_SELECTED_LIST_ITEM),this.adapter.addAttributeToElementAtIndex(t,Ec.ARIA_CHECKED_ATTR,"true"),this.selectedIndex=t},e.prototype.setEnabled=function(t,e){this.validatedIndex(t),e?(this.adapter.removeClassFromElementAtIndex(t,Ur),this.adapter.addAttributeToElementAtIndex(t,Ec.ARIA_DISABLED_ATTR,"false")):(this.adapter.addClassToElementAtIndex(t,Ur),this.adapter.addAttributeToElementAtIndex(t,Ec.ARIA_DISABLED_ATTR,"true"))},e.prototype.validatedIndex=function(t){var e=this.adapter.getMenuItemCount();if(!(t>=0&&t<e))throw new Error("MDCMenuFoundation: No list item at specified index.")},e}(Cc);
/**
     * @license
     * Copyright 2016 Google Inc.
     *
     * Permission is hereby granted, free of charge, to any person obtaining a copy
     * of this software and associated documentation files (the "Software"), to deal
     * in the Software without restriction, including without limitation the rights
     * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
     * copies of the Software, and to permit persons to whom the Software is
     * furnished to do so, subject to the following conditions:
     *
     * The above copyright notice and this permission notice shall be included in
     * all copies or substantial portions of the Software.
     *
     * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
     * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
     * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
     * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
     * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
     * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
     * THE SOFTWARE.
     */
/**
     * @license
     * Copyright 2019 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
const kc=window,Rc=kc.ShadowRoot&&(void 0===kc.ShadyCSS||kc.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,Pc=Symbol(),Lc=new WeakMap;let Mc=class{constructor(t,e,i){if(this._$cssResult$=!0,i!==Pc)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o;const e=this.t;if(Rc&&void 0===t){const i=void 0!==e&&1===e.length;i&&(t=Lc.get(e)),void 0===t&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),i&&Lc.set(e,t))}return t}toString(){return this.cssText}};const Nc=(t,...e)=>{const i=1===t.length?t[0]:e.reduce((e,i,s)=>e+(t=>{if(!0===t._$cssResult$)return t.cssText;if("number"==typeof t)return t;throw Error("Value passed to 'css' function must be a 'css' function result: "+t+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+t[s+1],t[0]);return new Mc(i,t,Pc)},Dc=Rc?t=>t:t=>t instanceof CSSStyleSheet?(t=>{let e="";for(const i of t.cssRules)e+=i.cssText;return(t=>new Mc("string"==typeof t?t:t+"",void 0,Pc))(e)})(t):t;
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */var Hc;const Uc=window,zc=Uc.trustedTypes,Fc=zc?zc.emptyScript:"",Bc=Uc.reactiveElementPolyfillSupport,Vc={toAttribute(t,e){switch(e){case Boolean:t=t?Fc:null;break;case Object:case Array:t=null==t?t:JSON.stringify(t)}return t},fromAttribute(t,e){let i=t;switch(e){case Boolean:i=null!==t;break;case Number:i=null===t?null:Number(t);break;case Object:case Array:try{i=JSON.parse(t)}catch(t){i=null}}return i}},jc=(t,e)=>e!==t&&(e==e||t==t),Wc={attribute:!0,type:String,converter:Vc,reflect:!1,hasChanged:jc},qc="finalized";let Yc=class extends HTMLElement{constructor(){super(),this._$Ei=new Map,this.isUpdatePending=!1,this.hasUpdated=!1,this._$El=null,this._$Eu()}static addInitializer(t){var e;this.finalize(),(null!==(e=this.h)&&void 0!==e?e:this.h=[]).push(t)}static get observedAttributes(){this.finalize();const t=[];return this.elementProperties.forEach((e,i)=>{const s=this._$Ep(i,e);void 0!==s&&(this._$Ev.set(s,i),t.push(s))}),t}static createProperty(t,e=Wc){if(e.state&&(e.attribute=!1),this.finalize(),this.elementProperties.set(t,e),!e.noAccessor&&!this.prototype.hasOwnProperty(t)){const i="symbol"==typeof t?Symbol():"__"+t,s=this.getPropertyDescriptor(t,i,e);void 0!==s&&Object.defineProperty(this.prototype,t,s)}}static getPropertyDescriptor(t,e,i){return{get(){return this[e]},set(s){const n=this[t];this[e]=s,this.requestUpdate(t,n,i)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)||Wc}static finalize(){if(this.hasOwnProperty(qc))return!1;this[qc]=!0;const t=Object.getPrototypeOf(this);if(t.finalize(),void 0!==t.h&&(this.h=[...t.h]),this.elementProperties=new Map(t.elementProperties),this._$Ev=new Map,this.hasOwnProperty("properties")){const t=this.properties,e=[...Object.getOwnPropertyNames(t),...Object.getOwnPropertySymbols(t)];for(const i of e)this.createProperty(i,t[i])}return this.elementStyles=this.finalizeStyles(this.styles),!0}static finalizeStyles(t){const e=[];if(Array.isArray(t)){const i=new Set(t.flat(1/0).reverse());for(const t of i)e.unshift(Dc(t))}else void 0!==t&&e.push(Dc(t));return e}static _$Ep(t,e){const i=e.attribute;return!1===i?void 0:"string"==typeof i?i:"string"==typeof t?t.toLowerCase():void 0}_$Eu(){var t;this._$E_=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$Eg(),this.requestUpdate(),null===(t=this.constructor.h)||void 0===t||t.forEach(t=>t(this))}addController(t){var e,i;(null!==(e=this._$ES)&&void 0!==e?e:this._$ES=[]).push(t),void 0!==this.renderRoot&&this.isConnected&&(null===(i=t.hostConnected)||void 0===i||i.call(t))}removeController(t){var e;null===(e=this._$ES)||void 0===e||e.splice(this._$ES.indexOf(t)>>>0,1)}_$Eg(){this.constructor.elementProperties.forEach((t,e)=>{this.hasOwnProperty(e)&&(this._$Ei.set(e,this[e]),delete this[e])})}createRenderRoot(){var t;const e=null!==(t=this.shadowRoot)&&void 0!==t?t:this.attachShadow(this.constructor.shadowRootOptions);return((t,e)=>{Rc?t.adoptedStyleSheets=e.map(t=>t instanceof CSSStyleSheet?t:t.styleSheet):e.forEach(e=>{const i=document.createElement("style"),s=kc.litNonce;void 0!==s&&i.setAttribute("nonce",s),i.textContent=e.cssText,t.appendChild(i)})})(e,this.constructor.elementStyles),e}connectedCallback(){var t;void 0===this.renderRoot&&(this.renderRoot=this.createRenderRoot()),this.enableUpdating(!0),null===(t=this._$ES)||void 0===t||t.forEach(t=>{var e;return null===(e=t.hostConnected)||void 0===e?void 0:e.call(t)})}enableUpdating(t){}disconnectedCallback(){var t;null===(t=this._$ES)||void 0===t||t.forEach(t=>{var e;return null===(e=t.hostDisconnected)||void 0===e?void 0:e.call(t)})}attributeChangedCallback(t,e,i){this._$AK(t,i)}_$EO(t,e,i=Wc){var s;const n=this.constructor._$Ep(t,i);if(void 0!==n&&!0===i.reflect){const r=(void 0!==(null===(s=i.converter)||void 0===s?void 0:s.toAttribute)?i.converter:Vc).toAttribute(e,i.type);this._$El=t,null==r?this.removeAttribute(n):this.setAttribute(n,r),this._$El=null}}_$AK(t,e){var i;const s=this.constructor,n=s._$Ev.get(t);if(void 0!==n&&this._$El!==n){const t=s.getPropertyOptions(n),r="function"==typeof t.converter?{fromAttribute:t.converter}:void 0!==(null===(i=t.converter)||void 0===i?void 0:i.fromAttribute)?t.converter:Vc;this._$El=n,this[n]=r.fromAttribute(e,t.type),this._$El=null}}requestUpdate(t,e,i){let s=!0;void 0!==t&&(((i=i||this.constructor.getPropertyOptions(t)).hasChanged||jc)(this[t],e)?(this._$AL.has(t)||this._$AL.set(t,e),!0===i.reflect&&this._$El!==t&&(void 0===this._$EC&&(this._$EC=new Map),this._$EC.set(t,i))):s=!1),!this.isUpdatePending&&s&&(this._$E_=this._$Ej())}async _$Ej(){this.isUpdatePending=!0;try{await this._$E_}catch(t){Promise.reject(t)}const t=this.scheduleUpdate();return null!=t&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){var t;if(!this.isUpdatePending)return;this.hasUpdated,this._$Ei&&(this._$Ei.forEach((t,e)=>this[e]=t),this._$Ei=void 0);let e=!1;const i=this._$AL;try{e=this.shouldUpdate(i),e?(this.willUpdate(i),null===(t=this._$ES)||void 0===t||t.forEach(t=>{var e;return null===(e=t.hostUpdate)||void 0===e?void 0:e.call(t)}),this.update(i)):this._$Ek()}catch(t){throw e=!1,this._$Ek(),t}e&&this._$AE(i)}willUpdate(t){}_$AE(t){var e;null===(e=this._$ES)||void 0===e||e.forEach(t=>{var e;return null===(e=t.hostUpdated)||void 0===e?void 0:e.call(t)}),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$Ek(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$E_}shouldUpdate(t){return!0}update(t){void 0!==this._$EC&&(this._$EC.forEach((t,e)=>this._$EO(e,this[e],t)),this._$EC=void 0),this._$Ek()}updated(t){}firstUpdated(t){}};
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
var Xc;Yc[qc]=!0,Yc.elementProperties=new Map,Yc.elementStyles=[],Yc.shadowRootOptions={mode:"open"},null==Bc||Bc({ReactiveElement:Yc}),(null!==(Hc=Uc.reactiveElementVersions)&&void 0!==Hc?Hc:Uc.reactiveElementVersions=[]).push("1.6.3");const Gc=window,Kc=Gc.trustedTypes,Jc=Kc?Kc.createPolicy("lit-html",{createHTML:t=>t}):void 0,Zc="$lit$",Qc=`lit$${(Math.random()+"").slice(9)}$`,th="?"+Qc,eh=`<${th}>`,ih=document,sh=()=>ih.createComment(""),nh=t=>null===t||"object"!=typeof t&&"function"!=typeof t,rh=Array.isArray,oh="[ \t\n\f\r]",ah=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,lh=/-->/g,dh=/>/g,ch=RegExp(`>|${oh}(?:([^\\s"'>=/]+)(${oh}*=${oh}*(?:[^ \t\n\f\r"'\`<>=]|("|')|))|$)`,"g"),hh=/'/g,ph=/"/g,uh=/^(?:script|style|textarea|title)$/i,mh=(t=>(e,...i)=>({_$litType$:t,strings:e,values:i}))(1),fh=Symbol.for("lit-noChange"),gh=Symbol.for("lit-nothing"),vh=new WeakMap,_h=ih.createTreeWalker(ih,129,null,!1);function bh(t,e){if(!Array.isArray(t)||!t.hasOwnProperty("raw"))throw Error("invalid template strings array");return void 0!==Jc?Jc.createHTML(e):e}let yh=class t{constructor({strings:e,_$litType$:i},s){let n;this.parts=[];let r=0,o=0;const a=e.length-1,l=this.parts,[d,c]=((t,e)=>{const i=t.length-1,s=[];let n,r=2===e?"<svg>":"",o=ah;for(let e=0;e<i;e++){const i=t[e];let a,l,d=-1,c=0;for(;c<i.length&&(o.lastIndex=c,l=o.exec(i),null!==l);)c=o.lastIndex,o===ah?"!--"===l[1]?o=lh:void 0!==l[1]?o=dh:void 0!==l[2]?(uh.test(l[2])&&(n=RegExp("</"+l[2],"g")),o=ch):void 0!==l[3]&&(o=ch):o===ch?">"===l[0]?(o=null!=n?n:ah,d=-1):void 0===l[1]?d=-2:(d=o.lastIndex-l[2].length,a=l[1],o=void 0===l[3]?ch:'"'===l[3]?ph:hh):o===ph||o===hh?o=ch:o===lh||o===dh?o=ah:(o=ch,n=void 0);const h=o===ch&&t[e+1].startsWith("/>")?" ":"";r+=o===ah?i+eh:d>=0?(s.push(a),i.slice(0,d)+Zc+i.slice(d)+Qc+h):i+Qc+(-2===d?(s.push(void 0),e):h)}return[bh(t,r+(t[i]||"<?>")+(2===e?"</svg>":"")),s]})(e,i);if(this.el=t.createElement(d,s),_h.currentNode=this.el.content,2===i){const t=this.el.content,e=t.firstChild;e.remove(),t.append(...e.childNodes)}for(;null!==(n=_h.nextNode())&&l.length<a;){if(1===n.nodeType){if(n.hasAttributes()){const t=[];for(const e of n.getAttributeNames())if(e.endsWith(Zc)||e.startsWith(Qc)){const i=c[o++];if(t.push(e),void 0!==i){const t=n.getAttribute(i.toLowerCase()+Zc).split(Qc),e=/([.?@])?(.*)/.exec(i);l.push({type:1,index:r,name:e[2],strings:t,ctor:"."===e[1]?Eh:"?"===e[1]?Ch:"@"===e[1]?Th:Ah})}else l.push({type:6,index:r})}for(const e of t)n.removeAttribute(e)}if(uh.test(n.tagName)){const t=n.textContent.split(Qc),e=t.length-1;if(e>0){n.textContent=Kc?Kc.emptyScript:"";for(let i=0;i<e;i++)n.append(t[i],sh()),_h.nextNode(),l.push({type:2,index:++r});n.append(t[e],sh())}}}else if(8===n.nodeType)if(n.data===th)l.push({type:2,index:r});else{let t=-1;for(;-1!==(t=n.data.indexOf(Qc,t+1));)l.push({type:7,index:r}),t+=Qc.length-1}r++}}static createElement(t,e){const i=ih.createElement("template");return i.innerHTML=t,i}};function xh(t,e,i=t,s){var n,r,o,a;if(e===fh)return e;let l=void 0!==s?null===(n=i._$Co)||void 0===n?void 0:n[s]:i._$Cl;const d=nh(e)?void 0:e._$litDirective$;return(null==l?void 0:l.constructor)!==d&&(null===(r=null==l?void 0:l._$AO)||void 0===r||r.call(l,!1),void 0===d?l=void 0:(l=new d(t),l._$AT(t,i,s)),void 0!==s?(null!==(o=(a=i)._$Co)&&void 0!==o?o:a._$Co=[])[s]=l:i._$Cl=l),void 0!==l&&(e=xh(t,l._$AS(t,e.values),l,s)),e}let $h=class{constructor(t,e){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){var e;const{el:{content:i},parts:s}=this._$AD,n=(null!==(e=null==t?void 0:t.creationScope)&&void 0!==e?e:ih).importNode(i,!0);_h.currentNode=n;let r=_h.nextNode(),o=0,a=0,l=s[0];for(;void 0!==l;){if(o===l.index){let e;2===l.type?e=new wh(r,r.nextSibling,this,t):1===l.type?e=new l.ctor(r,l.name,l.strings,this,t):6===l.type&&(e=new Ih(r,this,t)),this._$AV.push(e),l=s[++a]}o!==(null==l?void 0:l.index)&&(r=_h.nextNode(),o++)}return _h.currentNode=ih,n}v(t){let e=0;for(const i of this._$AV)void 0!==i&&(void 0!==i.strings?(i._$AI(t,i,e),e+=i.strings.length-2):i._$AI(t[e])),e++}},wh=class t{constructor(t,e,i,s){var n;this.type=2,this._$AH=gh,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=i,this.options=s,this._$Cp=null===(n=null==s?void 0:s.isConnected)||void 0===n||n}get _$AU(){var t,e;return null!==(e=null===(t=this._$AM)||void 0===t?void 0:t._$AU)&&void 0!==e?e:this._$Cp}get parentNode(){let t=this._$AA.parentNode;const e=this._$AM;return void 0!==e&&11===(null==t?void 0:t.nodeType)&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=xh(this,t,e),nh(t)?t===gh||null==t||""===t?(this._$AH!==gh&&this._$AR(),this._$AH=gh):t!==this._$AH&&t!==fh&&this._(t):void 0!==t._$litType$?this.g(t):void 0!==t.nodeType?this.$(t):(t=>rh(t)||"function"==typeof(null==t?void 0:t[Symbol.iterator]))(t)?this.T(t):this._(t)}k(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}$(t){this._$AH!==t&&(this._$AR(),this._$AH=this.k(t))}_(t){this._$AH!==gh&&nh(this._$AH)?this._$AA.nextSibling.data=t:this.$(ih.createTextNode(t)),this._$AH=t}g(t){var e;const{values:i,_$litType$:s}=t,n="number"==typeof s?this._$AC(t):(void 0===s.el&&(s.el=yh.createElement(bh(s.h,s.h[0]),this.options)),s);if((null===(e=this._$AH)||void 0===e?void 0:e._$AD)===n)this._$AH.v(i);else{const t=new $h(n,this),e=t.u(this.options);t.v(i),this.$(e),this._$AH=t}}_$AC(t){let e=vh.get(t.strings);return void 0===e&&vh.set(t.strings,e=new yh(t)),e}T(e){rh(this._$AH)||(this._$AH=[],this._$AR());const i=this._$AH;let s,n=0;for(const r of e)n===i.length?i.push(s=new t(this.k(sh()),this.k(sh()),this,this.options)):s=i[n],s._$AI(r),n++;n<i.length&&(this._$AR(s&&s._$AB.nextSibling,n),i.length=n)}_$AR(t=this._$AA.nextSibling,e){var i;for(null===(i=this._$AP)||void 0===i||i.call(this,!1,!0,e);t&&t!==this._$AB;){const e=t.nextSibling;t.remove(),t=e}}setConnected(t){var e;void 0===this._$AM&&(this._$Cp=t,null===(e=this._$AP)||void 0===e||e.call(this,t))}},Ah=class{constructor(t,e,i,s,n){this.type=1,this._$AH=gh,this._$AN=void 0,this.element=t,this.name=e,this._$AM=s,this.options=n,i.length>2||""!==i[0]||""!==i[1]?(this._$AH=Array(i.length-1).fill(new String),this.strings=i):this._$AH=gh}get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}_$AI(t,e=this,i,s){const n=this.strings;let r=!1;if(void 0===n)t=xh(this,t,e,0),r=!nh(t)||t!==this._$AH&&t!==fh,r&&(this._$AH=t);else{const s=t;let o,a;for(t=n[0],o=0;o<n.length-1;o++)a=xh(this,s[i+o],e,o),a===fh&&(a=this._$AH[o]),r||(r=!nh(a)||a!==this._$AH[o]),a===gh?t=gh:t!==gh&&(t+=(null!=a?a:"")+n[o+1]),this._$AH[o]=a}r&&!s&&this.j(t)}j(t){t===gh?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,null!=t?t:"")}},Eh=class extends Ah{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===gh?void 0:t}};const Sh=Kc?Kc.emptyScript:"";let Ch=class extends Ah{constructor(){super(...arguments),this.type=4}j(t){t&&t!==gh?this.element.setAttribute(this.name,Sh):this.element.removeAttribute(this.name)}},Th=class extends Ah{constructor(t,e,i,s,n){super(t,e,i,s,n),this.type=5}_$AI(t,e=this){var i;if((t=null!==(i=xh(this,t,e,0))&&void 0!==i?i:gh)===fh)return;const s=this._$AH,n=t===gh&&s!==gh||t.capture!==s.capture||t.once!==s.once||t.passive!==s.passive,r=t!==gh&&(s===gh||n);n&&this.element.removeEventListener(this.name,this,s),r&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){var e,i;"function"==typeof this._$AH?this._$AH.call(null!==(i=null===(e=this.options)||void 0===e?void 0:e.host)&&void 0!==i?i:this.element,t):this._$AH.handleEvent(t)}},Ih=class{constructor(t,e,i){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=i}get _$AU(){return this._$AM._$AU}_$AI(t){xh(this,t)}};const Oh=Gc.litHtmlPolyfillSupport;null==Oh||Oh(yh,wh),(null!==(Xc=Gc.litHtmlVersions)&&void 0!==Xc?Xc:Gc.litHtmlVersions=[]).push("2.8.0");
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
var kh,Rh;let Ph=class extends Yc{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){var t,e;const i=super.createRenderRoot();return null!==(t=(e=this.renderOptions).renderBefore)&&void 0!==t||(e.renderBefore=i.firstChild),i}update(t){const e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=((t,e,i)=>{var s,n;const r=null!==(s=null==i?void 0:i.renderBefore)&&void 0!==s?s:e;let o=r._$litPart$;if(void 0===o){const t=null!==(n=null==i?void 0:i.renderBefore)&&void 0!==n?n:null;r._$litPart$=o=new wh(e.insertBefore(sh(),t),t,void 0,null!=i?i:{})}return o._$AI(t),o})(e,this.renderRoot,this.renderOptions)}connectedCallback(){var t;super.connectedCallback(),null===(t=this._$Do)||void 0===t||t.setConnected(!0)}disconnectedCallback(){var t;super.disconnectedCallback(),null===(t=this._$Do)||void 0===t||t.setConnected(!1)}render(){return fh}};Ph.finalized=!0,Ph._$litElement$=!0,null===(kh=globalThis.litElementHydrateSupport)||void 0===kh||kh.call(globalThis,{LitElement:Ph});const Lh=globalThis.litElementPolyfillSupport;null==Lh||Lh({LitElement:Ph}),(null!==(Rh=globalThis.litElementVersions)&&void 0!==Rh?Rh:globalThis.litElementVersions=[]).push("3.3.3");
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
const Mh=(t,e)=>"method"===e.kind&&e.descriptor&&!("value"in e.descriptor)?{...e,finisher(i){i.createProperty(e.key,t)}}:{kind:"field",key:Symbol(),placement:"own",descriptor:{},originalKey:e.key,initializer(){"function"==typeof e.initializer&&(this[e.key]=e.initializer.call(this))},finisher(i){i.createProperty(e.key,t)}};function Nh(t){return(e,i)=>void 0!==i?((t,e,i)=>{e.constructor.createProperty(i,t)})(t,e,i):Mh(t,e)}
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */function Dh(t){return Nh({...t,state:!0})}
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
function Hh(t,e){return(({finisher:t,descriptor:e})=>(i,s)=>{var n;if(void 0===s){const s=null!==(n=i.originalKey)&&void 0!==n?n:i.key,r=null!=e?{kind:"method",placement:"prototype",key:s,descriptor:e(i.key)}:{...i,key:s};return null!=t&&(r.finisher=function(e){t(e,s)}),r}{const n=i.constructor;void 0!==e&&Object.defineProperty(i,s,e(s)),null==t||t(n,s)}})({descriptor:e=>{const i={get(){var e,i;return null!==(i=null===(e=this.renderRoot)||void 0===e?void 0:e.querySelector(t))&&void 0!==i?i:null},enumerable:!0,configurable:!0};return i}})}
/**
     * @license
     * Copyright 2021 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */var Uh;null===(Uh=window.HTMLSlotElement)||void 0===Uh||Uh.prototype.assignedElements;
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
const zh=1,Fh=t=>(...e)=>({_$litDirective$:t,values:e});let Bh=class{constructor(t){}get _$AU(){return this._$AM._$AU}_$AT(t,e,i){this._$Ct=t,this._$AM=e,this._$Ci=i}_$AS(t,e){return this.update(t,e)}update(t,e){return this.render(...e)}};
/**
     * @license
     * Copyright 2018 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */const Vh=Fh(class extends Bh{constructor(t){var e;if(super(t),t.type!==zh||"class"!==t.name||(null===(e=t.strings)||void 0===e?void 0:e.length)>2)throw Error("`classMap()` can only be used in the `class` attribute and must be the only part in the attribute.")}render(t){return" "+Object.keys(t).filter(e=>t[e]).join(" ")+" "}update(t,[e]){var i,s;if(void 0===this.it){this.it=new Set,void 0!==t.strings&&(this.nt=new Set(t.strings.join(" ").split(/\s/).filter(t=>""!==t)));for(const t in e)e[t]&&!(null===(i=this.nt)||void 0===i?void 0:i.has(t))&&this.it.add(t);return this.render(e)}const n=t.element.classList;this.it.forEach(t=>{t in e||(n.remove(t),this.it.delete(t))});for(const t in e){const i=!!e[t];i===this.it.has(t)||(null===(s=this.nt)||void 0===s?void 0:s.has(t))||(i?(n.add(t),this.it.add(t)):(n.remove(t),this.it.delete(t)))}return fh}});
/**
     * @license
     * Copyright 2020 Google LLC
     * SPDX-License-Identifier: Apache-2.0
     */class jh extends Qi{constructor(){super(...arguments),this.mdcFoundationClass=Oc,this.listElement_=null,this.anchor=null,this.open=!1,this.quick=!1,this.wrapFocus=!1,this.innerRole="menu",this.innerAriaLabel=null,this.corner="TOP_START",this.x=null,this.y=null,this.absolute=!1,this.multi=!1,this.activatable=!1,this.fixed=!1,this.forceGroupSelection=!1,this.fullwidth=!1,this.menuCorner="START",this.stayOpenOnBodyClick=!1,this.defaultFocus="LIST_ROOT",this._listUpdateComplete=null}get listElement(){return this.listElement_||(this.listElement_=this.renderRoot.querySelector("mwc-list")),this.listElement_}get items(){const t=this.listElement;return t?t.items:[]}get index(){const t=this.listElement;return t?t.index:-1}get selected(){const t=this.listElement;return t?t.selected:null}render(){return this.renderSurface()}renderSurface(){const t=this.getSurfaceClasses();return mh`
      <mwc-menu-surface
        ?hidden=${!this.open}
        .anchor=${this.anchor}
        .open=${this.open}
        .quick=${this.quick}
        .corner=${this.corner}
        .x=${this.x}
        .y=${this.y}
        .absolute=${this.absolute}
        .fixed=${this.fixed}
        .fullwidth=${this.fullwidth}
        .menuCorner=${this.menuCorner}
        ?stayOpenOnBodyClick=${this.stayOpenOnBodyClick}
        class=${Vh(t)}
        @closed=${this.onClosed}
        @opened=${this.onOpened}
        @keydown=${this.onKeydown}>
      ${this.renderList()}
    </mwc-menu-surface>`}getSurfaceClasses(){return{"mdc-menu":!0,"mdc-menu-surface":!0}}renderList(){const t="menu"===this.innerRole?"menuitem":"option",e=this.renderListClasses();return mh`
      <mwc-list
          rootTabbable
          .innerAriaLabel=${this.innerAriaLabel}
          .innerRole=${this.innerRole}
          .multi=${this.multi}
          class=${Vh(e)}
          .itemRoles=${t}
          .wrapFocus=${this.wrapFocus}
          .activatable=${this.activatable}
          @action=${this.onAction}>
        <slot></slot>
      </mwc-list>`}renderListClasses(){return{"mdc-deprecated-list":!0}}createAdapter(){return{addClassToElementAtIndex:(t,e)=>{const i=this.listElement;if(!i)return;const s=i.items[t];s&&("mdc-menu-item--selected"===e?this.forceGroupSelection&&!s.selected&&i.toggle(t,!0):s.classList.add(e))},removeClassFromElementAtIndex:(t,e)=>{const i=this.listElement;if(!i)return;const s=i.items[t];s&&("mdc-menu-item--selected"===e?s.selected&&i.toggle(t,!1):s.classList.remove(e))},addAttributeToElementAtIndex:(t,e,i)=>{const s=this.listElement;if(!s)return;const n=s.items[t];n&&n.setAttribute(e,i)},removeAttributeFromElementAtIndex:(t,e)=>{const i=this.listElement;if(!i)return;const s=i.items[t];s&&s.removeAttribute(e)},getAttributeFromElementAtIndex:(t,e)=>{const i=this.listElement;if(!i)return null;const s=i.items[t];return s?s.getAttribute(e):null},elementContainsClass:(t,e)=>t.classList.contains(e),closeSurface:()=>{this.open=!1},getElementIndex:t=>{const e=this.listElement;return e?e.items.indexOf(t):-1},notifySelected:()=>{},getMenuItemCount:()=>{const t=this.listElement;return t?t.items.length:0},focusItemAtIndex:t=>{const e=this.listElement;if(!e)return;const i=e.items[t];i&&i.focus()},focusListRoot:()=>{this.listElement&&this.listElement.focus()},getSelectedSiblingOfItemAtIndex:t=>{const e=this.listElement;if(!e)return-1;const i=e.items[t];if(!i||!i.group)return-1;for(let s=0;s<e.items.length;s++){if(s===t)continue;const n=e.items[s];if(n.selected&&n.group===i.group)return s}return-1},isSelectableItemAtIndex:t=>{const e=this.listElement;if(!e)return!1;const i=e.items[t];return!!i&&i.hasAttribute("group")}}}onKeydown(t){this.mdcFoundation&&this.mdcFoundation.handleKeydown(t)}onAction(t){const e=this.listElement;if(this.mdcFoundation&&e){const i=t.detail.index,s=e.items[i];s&&this.mdcFoundation.handleItemAction(s)}}onOpened(){this.open=!0,this.mdcFoundation&&this.mdcFoundation.handleMenuSurfaceOpened()}onClosed(){this.open=!1}async getUpdateComplete(){await this._listUpdateComplete;return await super.getUpdateComplete()}async firstUpdated(){super.firstUpdated();const t=this.listElement;t&&(this._listUpdateComplete=t.updateComplete,await this._listUpdateComplete)}select(t){const e=this.listElement;e&&e.select(t)}close(){this.open=!1}show(){this.open=!0}getFocusedItemIndex(){const t=this.listElement;return t?t.getFocusedItemIndex():-1}focusItemAtIndex(t){const e=this.listElement;e&&e.focusItemAtIndex(t)}layout(t=!0){const e=this.listElement;e&&e.layout(t)}}n([Hh(".mdc-menu")],jh.prototype,"mdcRoot",void 0),n([Hh("slot")],jh.prototype,"slotElement",void 0),n([Nh({type:Object})],jh.prototype,"anchor",void 0),n([Nh({type:Boolean,reflect:!0})],jh.prototype,"open",void 0),n([Nh({type:Boolean})],jh.prototype,"quick",void 0),n([Nh({type:Boolean})],jh.prototype,"wrapFocus",void 0),n([Nh({type:String})],jh.prototype,"innerRole",void 0),n([Nh({type:String})],jh.prototype,"innerAriaLabel",void 0),n([Nh({type:String})],jh.prototype,"corner",void 0),n([Nh({type:Number})],jh.prototype,"x",void 0),n([Nh({type:Number})],jh.prototype,"y",void 0),n([Nh({type:Boolean})],jh.prototype,"absolute",void 0),n([Nh({type:Boolean})],jh.prototype,"multi",void 0),n([Nh({type:Boolean})],jh.prototype,"activatable",void 0),n([Nh({type:Boolean})],jh.prototype,"fixed",void 0),n([Nh({type:Boolean})],jh.prototype,"forceGroupSelection",void 0),n([Nh({type:Boolean})],jh.prototype,"fullwidth",void 0),n([Nh({type:String})],jh.prototype,"menuCorner",void 0),n([Nh({type:Boolean})],jh.prototype,"stayOpenOnBodyClick",void 0),n([Nh({type:String}),os(function(t){this.mdcFoundation&&this.mdcFoundation.setDefaultFocusState(wc[t])})],jh.prototype,"defaultFocus",void 0);
/**
     * @license
     * Copyright 2018 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
const Wh="important",qh=" !"+Wh,Yh=Fh(class extends Bh{constructor(t){var e;if(super(t),t.type!==zh||"style"!==t.name||(null===(e=t.strings)||void 0===e?void 0:e.length)>2)throw Error("The `styleMap` directive must be used in the `style` attribute and must be the only part in the attribute.")}render(t){return Object.keys(t).reduce((e,i)=>{const s=t[i];return null==s?e:e+`${i=i.includes("-")?i:i.replace(/(?:^(webkit|moz|ms|o)|)(?=[A-Z])/g,"-$&").toLowerCase()}:${s};`},"")}update(t,[e]){const{style:i}=t.element;if(void 0===this.ht){this.ht=new Set;for(const t in e)this.ht.add(t);return this.render(e)}this.ht.forEach(t=>{null==e[t]&&(this.ht.delete(t),t.includes("-")?i.removeProperty(t):i[t]="")});for(const t in e){const s=e[t];if(null!=s){this.ht.add(t);const e="string"==typeof s&&s.endsWith(qh);t.includes("-")||e?i.setProperty(t,e?s.slice(0,-11):s,e?Wh:""):i[t]=s}}return fh}}),Xh={TOP_LEFT:Xo.TOP_LEFT,TOP_RIGHT:Xo.TOP_RIGHT,BOTTOM_LEFT:Xo.BOTTOM_LEFT,BOTTOM_RIGHT:Xo.BOTTOM_RIGHT,TOP_START:Xo.TOP_START,TOP_END:Xo.TOP_END,BOTTOM_START:Xo.BOTTOM_START,BOTTOM_END:Xo.BOTTOM_END};
/**
     * @license
     * Copyright 2020 Google LLC
     * SPDX-License-Identifier: Apache-2.0
     */class Gh extends Qi{constructor(){super(...arguments),this.mdcFoundationClass=Ic,this.absolute=!1,this.fullwidth=!1,this.fixed=!1,this.x=null,this.y=null,this.quick=!1,this.open=!1,this.stayOpenOnBodyClick=!1,this.bitwiseCorner=Xo.TOP_START,this.previousMenuCorner=null,this.menuCorner="START",this.corner="TOP_START",this.styleTop="",this.styleLeft="",this.styleRight="",this.styleBottom="",this.styleMaxHeight="",this.styleTransformOrigin="",this.anchor=null,this.previouslyFocused=null,this.previousAnchor=null,this.onBodyClickBound=()=>{}}render(){return this.renderSurface()}renderSurface(){const t=this.getRootClasses(),e=this.getRootStyles();return mh`
      <div
          class=${Vh(t)}
          style="${Yh(e)}"
          @keydown=${this.onKeydown}
          @opened=${this.registerBodyClick}
          @closed=${this.deregisterBodyClick}>
        ${this.renderContent()}
      </div>`}getRootClasses(){return{"mdc-menu-surface":!0,"mdc-menu-surface--fixed":this.fixed,"mdc-menu-surface--fullwidth":this.fullwidth}}getRootStyles(){return{top:this.styleTop,left:this.styleLeft,right:this.styleRight,bottom:this.styleBottom,"max-height":this.styleMaxHeight,"transform-origin":this.styleTransformOrigin}}renderContent(){return mh`<slot></slot>`}createAdapter(){return Object.assign(Object.assign({},Xi(this.mdcRoot)),{hasAnchor:()=>!!this.anchor,notifyClose:()=>{const t=new CustomEvent("closed",{bubbles:!0,composed:!0});this.open=!1,this.mdcRoot.dispatchEvent(t)},notifyClosing:()=>{const t=new CustomEvent("closing",{bubbles:!0,composed:!0});this.mdcRoot.dispatchEvent(t)},notifyOpen:()=>{const t=new CustomEvent("opened",{bubbles:!0,composed:!0});this.open=!0,this.mdcRoot.dispatchEvent(t)},notifyOpening:()=>{const t=new CustomEvent("opening",{bubbles:!0,composed:!0});this.mdcRoot.dispatchEvent(t)},isElementInContainer:()=>!1,isRtl:()=>!!this.mdcRoot&&"rtl"===getComputedStyle(this.mdcRoot).direction,setTransformOrigin:t=>{this.mdcRoot&&(this.styleTransformOrigin=t)},isFocused:()=>Zi(this),saveFocus:()=>{const t=Ji(),e=t.length;e||(this.previouslyFocused=null),this.previouslyFocused=t[e-1]},restoreFocus:()=>{this.previouslyFocused&&"focus"in this.previouslyFocused&&this.previouslyFocused.focus()},getInnerDimensions:()=>{const t=this.mdcRoot;return t?{width:t.offsetWidth,height:t.offsetHeight}:{width:0,height:0}},getAnchorDimensions:()=>{const t=this.anchor;return t?t.getBoundingClientRect():null},getBodyDimensions:()=>({width:document.body.clientWidth,height:document.body.clientHeight}),getWindowDimensions:()=>({width:window.innerWidth,height:window.innerHeight}),getWindowScroll:()=>({x:window.pageXOffset,y:window.pageYOffset}),setPosition:t=>{this.mdcRoot&&(this.styleLeft="left"in t?`${t.left}px`:"",this.styleRight="right"in t?`${t.right}px`:"",this.styleTop="top"in t?`${t.top}px`:"",this.styleBottom="bottom"in t?`${t.bottom}px`:"")},setMaxHeight:async t=>{this.mdcRoot&&(this.styleMaxHeight=t,await this.updateComplete,this.styleMaxHeight=`var(--mdc-menu-max-height, ${t})`)}})}onKeydown(t){this.mdcFoundation&&this.mdcFoundation.handleKeydown(t)}onBodyClick(t){if(this.stayOpenOnBodyClick)return;-1===t.composedPath().indexOf(this)&&this.close()}registerBodyClick(){this.onBodyClickBound=this.onBodyClick.bind(this),document.body.addEventListener("click",this.onBodyClickBound,{passive:!0,capture:!0})}deregisterBodyClick(){document.body.removeEventListener("click",this.onBodyClickBound,{capture:!0})}onOpenChanged(t,e){this.mdcFoundation&&(t?this.mdcFoundation.open():void 0!==e&&this.mdcFoundation.close())}close(){this.open=!1}show(){this.open=!0}}n([Hh(".mdc-menu-surface")],Gh.prototype,"mdcRoot",void 0),n([Hh("slot")],Gh.prototype,"slotElement",void 0),n([Nh({type:Boolean}),os(function(t){this.mdcFoundation&&!this.fixed&&this.mdcFoundation.setIsHoisted(t)})],Gh.prototype,"absolute",void 0),n([Nh({type:Boolean})],Gh.prototype,"fullwidth",void 0),n([Nh({type:Boolean}),os(function(t){this.mdcFoundation&&!this.absolute&&this.mdcFoundation.setFixedPosition(t)})],Gh.prototype,"fixed",void 0),n([Nh({type:Number}),os(function(t){this.mdcFoundation&&null!==this.y&&null!==t&&(this.mdcFoundation.setAbsolutePosition(t,this.y),this.mdcFoundation.setAnchorMargin({left:t,top:this.y,right:-t,bottom:this.y}))})],Gh.prototype,"x",void 0),n([Nh({type:Number}),os(function(t){this.mdcFoundation&&null!==this.x&&null!==t&&(this.mdcFoundation.setAbsolutePosition(this.x,t),this.mdcFoundation.setAnchorMargin({left:this.x,top:t,right:-this.x,bottom:t}))})],Gh.prototype,"y",void 0),n([Nh({type:Boolean}),os(function(t){this.mdcFoundation&&this.mdcFoundation.setQuickOpen(t)})],Gh.prototype,"quick",void 0),n([Nh({type:Boolean,reflect:!0}),os(function(t,e){this.onOpenChanged(t,e)})],Gh.prototype,"open",void 0),n([Nh({type:Boolean})],Gh.prototype,"stayOpenOnBodyClick",void 0),n([Dh(),os(function(t){this.mdcFoundation&&this.mdcFoundation.setAnchorCorner(t)})],Gh.prototype,"bitwiseCorner",void 0),n([Nh({type:String}),os(function(t){if(this.mdcFoundation){const e="START"===t||"END"===t,i=null===this.previousMenuCorner,s=!i&&t!==this.previousMenuCorner;e&&(s||i&&"END"===t)&&(this.bitwiseCorner=this.bitwiseCorner^Yo.RIGHT,this.mdcFoundation.flipCornerHorizontally(),this.previousMenuCorner=t)}})],Gh.prototype,"menuCorner",void 0),n([Nh({type:String}),os(function(t){if(this.mdcFoundation&&t){let e=Xh[t];"END"===this.menuCorner&&(e^=Yo.RIGHT),this.bitwiseCorner=e}})],Gh.prototype,"corner",void 0),n([Dh()],Gh.prototype,"styleTop",void 0),n([Dh()],Gh.prototype,"styleLeft",void 0),n([Dh()],Gh.prototype,"styleRight",void 0),n([Dh()],Gh.prototype,"styleBottom",void 0),n([Dh()],Gh.prototype,"styleMaxHeight",void 0),n([Dh()],Gh.prototype,"styleTransformOrigin",void 0);
/**
     * @license
     * Copyright 2016 Google Inc.
     *
     * Permission is hereby granted, free of charge, to any person obtaining a copy
     * of this software and associated documentation files (the "Software"), to deal
     * in the Software without restriction, including without limitation the rights
     * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
     * copies of the Software, and to permit persons to whom the Software is
     * furnished to do so, subject to the following conditions:
     *
     * The above copyright notice and this permission notice shall be included in
     * all copies or substantial portions of the Software.
     *
     * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
     * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
     * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
     * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
     * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
     * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
     * THE SOFTWARE.
     */
var Kh=function(){function t(t){void 0===t&&(t={}),this.adapter=t}return Object.defineProperty(t,"cssClasses",{get:function(){return{}},enumerable:!1,configurable:!0}),Object.defineProperty(t,"strings",{get:function(){return{}},enumerable:!1,configurable:!0}),Object.defineProperty(t,"numbers",{get:function(){return{}},enumerable:!1,configurable:!0}),Object.defineProperty(t,"defaultAdapter",{get:function(){return{}},enumerable:!1,configurable:!0}),t.prototype.init=function(){},t.prototype.destroy=function(){},t}(),Jh={BG_FOCUSED:"mdc-ripple-upgraded--background-focused",FG_ACTIVATION:"mdc-ripple-upgraded--foreground-activation",FG_DEACTIVATION:"mdc-ripple-upgraded--foreground-deactivation",ROOT:"mdc-ripple-upgraded",UNBOUNDED:"mdc-ripple-upgraded--unbounded"},Zh={VAR_FG_SCALE:"--mdc-ripple-fg-scale",VAR_FG_SIZE:"--mdc-ripple-fg-size",VAR_FG_TRANSLATE_END:"--mdc-ripple-fg-translate-end",VAR_FG_TRANSLATE_START:"--mdc-ripple-fg-translate-start",VAR_LEFT:"--mdc-ripple-left",VAR_TOP:"--mdc-ripple-top"},Qh={DEACTIVATION_TIMEOUT_MS:225,FG_DEACTIVATION_MS:150,INITIAL_ORIGIN_SCALE:.6,PADDING:10,TAP_DELAY_MS:300};
/**
     * @license
     * Copyright 2016 Google Inc.
     *
     * Permission is hereby granted, free of charge, to any person obtaining a copy
     * of this software and associated documentation files (the "Software"), to deal
     * in the Software without restriction, including without limitation the rights
     * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
     * copies of the Software, and to permit persons to whom the Software is
     * furnished to do so, subject to the following conditions:
     *
     * The above copyright notice and this permission notice shall be included in
     * all copies or substantial portions of the Software.
     *
     * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
     * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
     * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
     * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
     * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
     * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
     * THE SOFTWARE.
     */
/**
     * @license
     * Copyright 2016 Google Inc.
     *
     * Permission is hereby granted, free of charge, to any person obtaining a copy
     * of this software and associated documentation files (the "Software"), to deal
     * in the Software without restriction, including without limitation the rights
     * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
     * copies of the Software, and to permit persons to whom the Software is
     * furnished to do so, subject to the following conditions:
     *
     * The above copyright notice and this permission notice shall be included in
     * all copies or substantial portions of the Software.
     *
     * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
     * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
     * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
     * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
     * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
     * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
     * THE SOFTWARE.
     */
var tp=["touchstart","pointerdown","mousedown","keydown"],ep=["touchend","pointerup","mouseup","contextmenu"],ip=[],sp=function(t){function e(i){var n=t.call(this,s(s({},e.defaultAdapter),i))||this;return n.activationAnimationHasEnded=!1,n.activationTimer=0,n.fgDeactivationRemovalTimer=0,n.fgScale="0",n.frame={width:0,height:0},n.initialSize=0,n.layoutFrame=0,n.maxRadius=0,n.unboundedCoords={left:0,top:0},n.activationState=n.defaultActivationState(),n.activationTimerCallback=function(){n.activationAnimationHasEnded=!0,n.runDeactivationUXLogicIfReady()},n.activateHandler=function(t){n.activateImpl(t)},n.deactivateHandler=function(){n.deactivateImpl()},n.focusHandler=function(){n.handleFocus()},n.blurHandler=function(){n.handleBlur()},n.resizeHandler=function(){n.layout()},n}return i(e,t),Object.defineProperty(e,"cssClasses",{get:function(){return Jh},enumerable:!1,configurable:!0}),Object.defineProperty(e,"strings",{get:function(){return Zh},enumerable:!1,configurable:!0}),Object.defineProperty(e,"numbers",{get:function(){return Qh},enumerable:!1,configurable:!0}),Object.defineProperty(e,"defaultAdapter",{get:function(){return{addClass:function(){},browserSupportsCssVars:function(){return!0},computeBoundingRect:function(){return{top:0,right:0,bottom:0,left:0,width:0,height:0}},containsEventTarget:function(){return!0},deregisterDocumentInteractionHandler:function(){},deregisterInteractionHandler:function(){},deregisterResizeHandler:function(){},getWindowPageOffset:function(){return{x:0,y:0}},isSurfaceActive:function(){return!0},isSurfaceDisabled:function(){return!0},isUnbounded:function(){return!0},registerDocumentInteractionHandler:function(){},registerInteractionHandler:function(){},registerResizeHandler:function(){},removeClass:function(){},updateCssVariable:function(){}}},enumerable:!1,configurable:!0}),e.prototype.init=function(){var t=this,i=this.supportsPressRipple();if(this.registerRootHandlers(i),i){var s=e.cssClasses,n=s.ROOT,r=s.UNBOUNDED;requestAnimationFrame(function(){t.adapter.addClass(n),t.adapter.isUnbounded()&&(t.adapter.addClass(r),t.layoutInternal())})}},e.prototype.destroy=function(){var t=this;if(this.supportsPressRipple()){this.activationTimer&&(clearTimeout(this.activationTimer),this.activationTimer=0,this.adapter.removeClass(e.cssClasses.FG_ACTIVATION)),this.fgDeactivationRemovalTimer&&(clearTimeout(this.fgDeactivationRemovalTimer),this.fgDeactivationRemovalTimer=0,this.adapter.removeClass(e.cssClasses.FG_DEACTIVATION));var i=e.cssClasses,s=i.ROOT,n=i.UNBOUNDED;requestAnimationFrame(function(){t.adapter.removeClass(s),t.adapter.removeClass(n),t.removeCssVars()})}this.deregisterRootHandlers(),this.deregisterDeactivationHandlers()},e.prototype.activate=function(t){this.activateImpl(t)},e.prototype.deactivate=function(){this.deactivateImpl()},e.prototype.layout=function(){var t=this;this.layoutFrame&&cancelAnimationFrame(this.layoutFrame),this.layoutFrame=requestAnimationFrame(function(){t.layoutInternal(),t.layoutFrame=0})},e.prototype.setUnbounded=function(t){var i=e.cssClasses.UNBOUNDED;t?this.adapter.addClass(i):this.adapter.removeClass(i)},e.prototype.handleFocus=function(){var t=this;requestAnimationFrame(function(){return t.adapter.addClass(e.cssClasses.BG_FOCUSED)})},e.prototype.handleBlur=function(){var t=this;requestAnimationFrame(function(){return t.adapter.removeClass(e.cssClasses.BG_FOCUSED)})},e.prototype.supportsPressRipple=function(){return this.adapter.browserSupportsCssVars()},e.prototype.defaultActivationState=function(){return{activationEvent:void 0,hasDeactivationUXRun:!1,isActivated:!1,isProgrammatic:!1,wasActivatedByPointer:!1,wasElementMadeActive:!1}},e.prototype.registerRootHandlers=function(t){var e,i;if(t){try{for(var s=r(tp),n=s.next();!n.done;n=s.next()){var o=n.value;this.adapter.registerInteractionHandler(o,this.activateHandler)}}catch(t){e={error:t}}finally{try{n&&!n.done&&(i=s.return)&&i.call(s)}finally{if(e)throw e.error}}this.adapter.isUnbounded()&&this.adapter.registerResizeHandler(this.resizeHandler)}this.adapter.registerInteractionHandler("focus",this.focusHandler),this.adapter.registerInteractionHandler("blur",this.blurHandler)},e.prototype.registerDeactivationHandlers=function(t){var e,i;if("keydown"===t.type)this.adapter.registerInteractionHandler("keyup",this.deactivateHandler);else try{for(var s=r(ep),n=s.next();!n.done;n=s.next()){var o=n.value;this.adapter.registerDocumentInteractionHandler(o,this.deactivateHandler)}}catch(t){e={error:t}}finally{try{n&&!n.done&&(i=s.return)&&i.call(s)}finally{if(e)throw e.error}}},e.prototype.deregisterRootHandlers=function(){var t,e;try{for(var i=r(tp),s=i.next();!s.done;s=i.next()){var n=s.value;this.adapter.deregisterInteractionHandler(n,this.activateHandler)}}catch(e){t={error:e}}finally{try{s&&!s.done&&(e=i.return)&&e.call(i)}finally{if(t)throw t.error}}this.adapter.deregisterInteractionHandler("focus",this.focusHandler),this.adapter.deregisterInteractionHandler("blur",this.blurHandler),this.adapter.isUnbounded()&&this.adapter.deregisterResizeHandler(this.resizeHandler)},e.prototype.deregisterDeactivationHandlers=function(){var t,e;this.adapter.deregisterInteractionHandler("keyup",this.deactivateHandler);try{for(var i=r(ep),s=i.next();!s.done;s=i.next()){var n=s.value;this.adapter.deregisterDocumentInteractionHandler(n,this.deactivateHandler)}}catch(e){t={error:e}}finally{try{s&&!s.done&&(e=i.return)&&e.call(i)}finally{if(t)throw t.error}}},e.prototype.removeCssVars=function(){var t=this,i=e.strings;Object.keys(i).forEach(function(e){0===e.indexOf("VAR_")&&t.adapter.updateCssVariable(i[e],null)})},e.prototype.activateImpl=function(t){var e=this;if(!this.adapter.isSurfaceDisabled()){var i=this.activationState;if(!i.isActivated){var s=this.previousActivationEvent;if(!(s&&void 0!==t&&s.type!==t.type))i.isActivated=!0,i.isProgrammatic=void 0===t,i.activationEvent=t,i.wasActivatedByPointer=!i.isProgrammatic&&(void 0!==t&&("mousedown"===t.type||"touchstart"===t.type||"pointerdown"===t.type)),void 0!==t&&ip.length>0&&ip.some(function(t){return e.adapter.containsEventTarget(t)})?this.resetActivationState():(void 0!==t&&(ip.push(t.target),this.registerDeactivationHandlers(t)),i.wasElementMadeActive=this.checkElementMadeActive(t),i.wasElementMadeActive&&this.animateActivation(),requestAnimationFrame(function(){ip=[],i.wasElementMadeActive||void 0===t||" "!==t.key&&32!==t.keyCode||(i.wasElementMadeActive=e.checkElementMadeActive(t),i.wasElementMadeActive&&e.animateActivation()),i.wasElementMadeActive||(e.activationState=e.defaultActivationState())}))}}},e.prototype.checkElementMadeActive=function(t){return void 0===t||"keydown"!==t.type||this.adapter.isSurfaceActive()},e.prototype.animateActivation=function(){var t=this,i=e.strings,s=i.VAR_FG_TRANSLATE_START,n=i.VAR_FG_TRANSLATE_END,r=e.cssClasses,o=r.FG_DEACTIVATION,a=r.FG_ACTIVATION,l=e.numbers.DEACTIVATION_TIMEOUT_MS;this.layoutInternal();var d="",c="";if(!this.adapter.isUnbounded()){var h=this.getFgTranslationCoordinates(),p=h.startPoint,u=h.endPoint;d=p.x+"px, "+p.y+"px",c=u.x+"px, "+u.y+"px"}this.adapter.updateCssVariable(s,d),this.adapter.updateCssVariable(n,c),clearTimeout(this.activationTimer),clearTimeout(this.fgDeactivationRemovalTimer),this.rmBoundedActivationClasses(),this.adapter.removeClass(o),this.adapter.computeBoundingRect(),this.adapter.addClass(a),this.activationTimer=setTimeout(function(){t.activationTimerCallback()},l)},e.prototype.getFgTranslationCoordinates=function(){var t,e=this.activationState,i=e.activationEvent;return t=e.wasActivatedByPointer?function(t,e,i){if(!t)return{x:0,y:0};var s,n,r=e.x,o=e.y,a=r+i.left,l=o+i.top;if("touchstart"===t.type){var d=t;s=d.changedTouches[0].pageX-a,n=d.changedTouches[0].pageY-l}else{var c=t;s=c.pageX-a,n=c.pageY-l}return{x:s,y:n}}(i,this.adapter.getWindowPageOffset(),this.adapter.computeBoundingRect()):{x:this.frame.width/2,y:this.frame.height/2},{startPoint:t={x:t.x-this.initialSize/2,y:t.y-this.initialSize/2},endPoint:{x:this.frame.width/2-this.initialSize/2,y:this.frame.height/2-this.initialSize/2}}},e.prototype.runDeactivationUXLogicIfReady=function(){var t=this,i=e.cssClasses.FG_DEACTIVATION,s=this.activationState,n=s.hasDeactivationUXRun,r=s.isActivated;(n||!r)&&this.activationAnimationHasEnded&&(this.rmBoundedActivationClasses(),this.adapter.addClass(i),this.fgDeactivationRemovalTimer=setTimeout(function(){t.adapter.removeClass(i)},Qh.FG_DEACTIVATION_MS))},e.prototype.rmBoundedActivationClasses=function(){var t=e.cssClasses.FG_ACTIVATION;this.adapter.removeClass(t),this.activationAnimationHasEnded=!1,this.adapter.computeBoundingRect()},e.prototype.resetActivationState=function(){var t=this;this.previousActivationEvent=this.activationState.activationEvent,this.activationState=this.defaultActivationState(),setTimeout(function(){return t.previousActivationEvent=void 0},e.numbers.TAP_DELAY_MS)},e.prototype.deactivateImpl=function(){var t=this,e=this.activationState;if(e.isActivated){var i=s({},e);e.isProgrammatic?(requestAnimationFrame(function(){t.animateDeactivation(i)}),this.resetActivationState()):(this.deregisterDeactivationHandlers(),requestAnimationFrame(function(){t.activationState.hasDeactivationUXRun=!0,t.animateDeactivation(i),t.resetActivationState()}))}},e.prototype.animateDeactivation=function(t){var e=t.wasActivatedByPointer,i=t.wasElementMadeActive;(e||i)&&this.runDeactivationUXLogicIfReady()},e.prototype.layoutInternal=function(){var t=this;this.frame=this.adapter.computeBoundingRect();var i=Math.max(this.frame.height,this.frame.width);this.maxRadius=this.adapter.isUnbounded()?i:Math.sqrt(Math.pow(t.frame.width,2)+Math.pow(t.frame.height,2))+e.numbers.PADDING;var s=Math.floor(i*e.numbers.INITIAL_ORIGIN_SCALE);this.adapter.isUnbounded()&&s%2!=0?this.initialSize=s-1:this.initialSize=s,this.fgScale=""+this.maxRadius/this.initialSize,this.updateLayoutCssVars()},e.prototype.updateLayoutCssVars=function(){var t=e.strings,i=t.VAR_FG_SIZE,s=t.VAR_LEFT,n=t.VAR_TOP,r=t.VAR_FG_SCALE;this.adapter.updateCssVariable(i,this.initialSize+"px"),this.adapter.updateCssVariable(r,this.fgScale),this.adapter.isUnbounded()&&(this.unboundedCoords={left:Math.round(this.frame.width/2-this.initialSize/2),top:Math.round(this.frame.height/2-this.initialSize/2)},this.adapter.updateCssVariable(s,this.unboundedCoords.left+"px"),this.adapter.updateCssVariable(n,this.unboundedCoords.top+"px"))},e}(Kh);
/**
     * @license
     * Copyright 2019 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
const np=window,rp=np.ShadowRoot&&(void 0===np.ShadyCSS||np.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,op=Symbol(),ap=new WeakMap;let lp=class{constructor(t,e,i){if(this._$cssResult$=!0,i!==op)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o;const e=this.t;if(rp&&void 0===t){const i=void 0!==e&&1===e.length;i&&(t=ap.get(e)),void 0===t&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),i&&ap.set(e,t))}return t}toString(){return this.cssText}};const dp=rp?t=>t:t=>t instanceof CSSStyleSheet?(t=>{let e="";for(const i of t.cssRules)e+=i.cssText;return(t=>new lp("string"==typeof t?t:t+"",void 0,op))(e)})(t):t;
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */var cp;const hp=window,pp=hp.trustedTypes,up=pp?pp.emptyScript:"",mp=hp.reactiveElementPolyfillSupport,fp={toAttribute(t,e){switch(e){case Boolean:t=t?up:null;break;case Object:case Array:t=null==t?t:JSON.stringify(t)}return t},fromAttribute(t,e){let i=t;switch(e){case Boolean:i=null!==t;break;case Number:i=null===t?null:Number(t);break;case Object:case Array:try{i=JSON.parse(t)}catch(t){i=null}}return i}},gp=(t,e)=>e!==t&&(e==e||t==t),vp={attribute:!0,type:String,converter:fp,reflect:!1,hasChanged:gp},_p="finalized";let bp=class extends HTMLElement{constructor(){super(),this._$Ei=new Map,this.isUpdatePending=!1,this.hasUpdated=!1,this._$El=null,this._$Eu()}static addInitializer(t){var e;this.finalize(),(null!==(e=this.h)&&void 0!==e?e:this.h=[]).push(t)}static get observedAttributes(){this.finalize();const t=[];return this.elementProperties.forEach((e,i)=>{const s=this._$Ep(i,e);void 0!==s&&(this._$Ev.set(s,i),t.push(s))}),t}static createProperty(t,e=vp){if(e.state&&(e.attribute=!1),this.finalize(),this.elementProperties.set(t,e),!e.noAccessor&&!this.prototype.hasOwnProperty(t)){const i="symbol"==typeof t?Symbol():"__"+t,s=this.getPropertyDescriptor(t,i,e);void 0!==s&&Object.defineProperty(this.prototype,t,s)}}static getPropertyDescriptor(t,e,i){return{get(){return this[e]},set(s){const n=this[t];this[e]=s,this.requestUpdate(t,n,i)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)||vp}static finalize(){if(this.hasOwnProperty(_p))return!1;this[_p]=!0;const t=Object.getPrototypeOf(this);if(t.finalize(),void 0!==t.h&&(this.h=[...t.h]),this.elementProperties=new Map(t.elementProperties),this._$Ev=new Map,this.hasOwnProperty("properties")){const t=this.properties,e=[...Object.getOwnPropertyNames(t),...Object.getOwnPropertySymbols(t)];for(const i of e)this.createProperty(i,t[i])}return this.elementStyles=this.finalizeStyles(this.styles),!0}static finalizeStyles(t){const e=[];if(Array.isArray(t)){const i=new Set(t.flat(1/0).reverse());for(const t of i)e.unshift(dp(t))}else void 0!==t&&e.push(dp(t));return e}static _$Ep(t,e){const i=e.attribute;return!1===i?void 0:"string"==typeof i?i:"string"==typeof t?t.toLowerCase():void 0}_$Eu(){var t;this._$E_=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$Eg(),this.requestUpdate(),null===(t=this.constructor.h)||void 0===t||t.forEach(t=>t(this))}addController(t){var e,i;(null!==(e=this._$ES)&&void 0!==e?e:this._$ES=[]).push(t),void 0!==this.renderRoot&&this.isConnected&&(null===(i=t.hostConnected)||void 0===i||i.call(t))}removeController(t){var e;null===(e=this._$ES)||void 0===e||e.splice(this._$ES.indexOf(t)>>>0,1)}_$Eg(){this.constructor.elementProperties.forEach((t,e)=>{this.hasOwnProperty(e)&&(this._$Ei.set(e,this[e]),delete this[e])})}createRenderRoot(){var t;const e=null!==(t=this.shadowRoot)&&void 0!==t?t:this.attachShadow(this.constructor.shadowRootOptions);return((t,e)=>{rp?t.adoptedStyleSheets=e.map(t=>t instanceof CSSStyleSheet?t:t.styleSheet):e.forEach(e=>{const i=document.createElement("style"),s=np.litNonce;void 0!==s&&i.setAttribute("nonce",s),i.textContent=e.cssText,t.appendChild(i)})})(e,this.constructor.elementStyles),e}connectedCallback(){var t;void 0===this.renderRoot&&(this.renderRoot=this.createRenderRoot()),this.enableUpdating(!0),null===(t=this._$ES)||void 0===t||t.forEach(t=>{var e;return null===(e=t.hostConnected)||void 0===e?void 0:e.call(t)})}enableUpdating(t){}disconnectedCallback(){var t;null===(t=this._$ES)||void 0===t||t.forEach(t=>{var e;return null===(e=t.hostDisconnected)||void 0===e?void 0:e.call(t)})}attributeChangedCallback(t,e,i){this._$AK(t,i)}_$EO(t,e,i=vp){var s;const n=this.constructor._$Ep(t,i);if(void 0!==n&&!0===i.reflect){const r=(void 0!==(null===(s=i.converter)||void 0===s?void 0:s.toAttribute)?i.converter:fp).toAttribute(e,i.type);this._$El=t,null==r?this.removeAttribute(n):this.setAttribute(n,r),this._$El=null}}_$AK(t,e){var i;const s=this.constructor,n=s._$Ev.get(t);if(void 0!==n&&this._$El!==n){const t=s.getPropertyOptions(n),r="function"==typeof t.converter?{fromAttribute:t.converter}:void 0!==(null===(i=t.converter)||void 0===i?void 0:i.fromAttribute)?t.converter:fp;this._$El=n,this[n]=r.fromAttribute(e,t.type),this._$El=null}}requestUpdate(t,e,i){let s=!0;void 0!==t&&(((i=i||this.constructor.getPropertyOptions(t)).hasChanged||gp)(this[t],e)?(this._$AL.has(t)||this._$AL.set(t,e),!0===i.reflect&&this._$El!==t&&(void 0===this._$EC&&(this._$EC=new Map),this._$EC.set(t,i))):s=!1),!this.isUpdatePending&&s&&(this._$E_=this._$Ej())}async _$Ej(){this.isUpdatePending=!0;try{await this._$E_}catch(t){Promise.reject(t)}const t=this.scheduleUpdate();return null!=t&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){var t;if(!this.isUpdatePending)return;this.hasUpdated,this._$Ei&&(this._$Ei.forEach((t,e)=>this[e]=t),this._$Ei=void 0);let e=!1;const i=this._$AL;try{e=this.shouldUpdate(i),e?(this.willUpdate(i),null===(t=this._$ES)||void 0===t||t.forEach(t=>{var e;return null===(e=t.hostUpdate)||void 0===e?void 0:e.call(t)}),this.update(i)):this._$Ek()}catch(t){throw e=!1,this._$Ek(),t}e&&this._$AE(i)}willUpdate(t){}_$AE(t){var e;null===(e=this._$ES)||void 0===e||e.forEach(t=>{var e;return null===(e=t.hostUpdated)||void 0===e?void 0:e.call(t)}),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$Ek(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$E_}shouldUpdate(t){return!0}update(t){void 0!==this._$EC&&(this._$EC.forEach((t,e)=>this._$EO(e,this[e],t)),this._$EC=void 0),this._$Ek()}updated(t){}firstUpdated(t){}};
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
var yp;bp[_p]=!0,bp.elementProperties=new Map,bp.elementStyles=[],bp.shadowRootOptions={mode:"open"},null==mp||mp({ReactiveElement:bp}),(null!==(cp=hp.reactiveElementVersions)&&void 0!==cp?cp:hp.reactiveElementVersions=[]).push("1.6.3");const xp=window,$p=xp.trustedTypes,wp=$p?$p.createPolicy("lit-html",{createHTML:t=>t}):void 0,Ap="$lit$",Ep=`lit$${(Math.random()+"").slice(9)}$`,Sp="?"+Ep,Cp=`<${Sp}>`,Tp=document,Ip=()=>Tp.createComment(""),Op=t=>null===t||"object"!=typeof t&&"function"!=typeof t,kp=Array.isArray,Rp="[ \t\n\f\r]",Pp=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,Lp=/-->/g,Mp=/>/g,Np=RegExp(`>|${Rp}(?:([^\\s"'>=/]+)(${Rp}*=${Rp}*(?:[^ \t\n\f\r"'\`<>=]|("|')|))|$)`,"g"),Dp=/'/g,Hp=/"/g,Up=/^(?:script|style|textarea|title)$/i,zp=(t=>(e,...i)=>({_$litType$:t,strings:e,values:i}))(1),Fp=Symbol.for("lit-noChange"),Bp=Symbol.for("lit-nothing"),Vp=new WeakMap,jp=Tp.createTreeWalker(Tp,129,null,!1);function Wp(t,e){if(!Array.isArray(t)||!t.hasOwnProperty("raw"))throw Error("invalid template strings array");return void 0!==wp?wp.createHTML(e):e}let qp=class t{constructor({strings:e,_$litType$:i},s){let n;this.parts=[];let r=0,o=0;const a=e.length-1,l=this.parts,[d,c]=((t,e)=>{const i=t.length-1,s=[];let n,r=2===e?"<svg>":"",o=Pp;for(let e=0;e<i;e++){const i=t[e];let a,l,d=-1,c=0;for(;c<i.length&&(o.lastIndex=c,l=o.exec(i),null!==l);)c=o.lastIndex,o===Pp?"!--"===l[1]?o=Lp:void 0!==l[1]?o=Mp:void 0!==l[2]?(Up.test(l[2])&&(n=RegExp("</"+l[2],"g")),o=Np):void 0!==l[3]&&(o=Np):o===Np?">"===l[0]?(o=null!=n?n:Pp,d=-1):void 0===l[1]?d=-2:(d=o.lastIndex-l[2].length,a=l[1],o=void 0===l[3]?Np:'"'===l[3]?Hp:Dp):o===Hp||o===Dp?o=Np:o===Lp||o===Mp?o=Pp:(o=Np,n=void 0);const h=o===Np&&t[e+1].startsWith("/>")?" ":"";r+=o===Pp?i+Cp:d>=0?(s.push(a),i.slice(0,d)+Ap+i.slice(d)+Ep+h):i+Ep+(-2===d?(s.push(void 0),e):h)}return[Wp(t,r+(t[i]||"<?>")+(2===e?"</svg>":"")),s]})(e,i);if(this.el=t.createElement(d,s),jp.currentNode=this.el.content,2===i){const t=this.el.content,e=t.firstChild;e.remove(),t.append(...e.childNodes)}for(;null!==(n=jp.nextNode())&&l.length<a;){if(1===n.nodeType){if(n.hasAttributes()){const t=[];for(const e of n.getAttributeNames())if(e.endsWith(Ap)||e.startsWith(Ep)){const i=c[o++];if(t.push(e),void 0!==i){const t=n.getAttribute(i.toLowerCase()+Ap).split(Ep),e=/([.?@])?(.*)/.exec(i);l.push({type:1,index:r,name:e[2],strings:t,ctor:"."===e[1]?Jp:"?"===e[1]?Qp:"@"===e[1]?tu:Kp})}else l.push({type:6,index:r})}for(const e of t)n.removeAttribute(e)}if(Up.test(n.tagName)){const t=n.textContent.split(Ep),e=t.length-1;if(e>0){n.textContent=$p?$p.emptyScript:"";for(let i=0;i<e;i++)n.append(t[i],Ip()),jp.nextNode(),l.push({type:2,index:++r});n.append(t[e],Ip())}}}else if(8===n.nodeType)if(n.data===Sp)l.push({type:2,index:r});else{let t=-1;for(;-1!==(t=n.data.indexOf(Ep,t+1));)l.push({type:7,index:r}),t+=Ep.length-1}r++}}static createElement(t,e){const i=Tp.createElement("template");return i.innerHTML=t,i}};function Yp(t,e,i=t,s){var n,r,o,a;if(e===Fp)return e;let l=void 0!==s?null===(n=i._$Co)||void 0===n?void 0:n[s]:i._$Cl;const d=Op(e)?void 0:e._$litDirective$;return(null==l?void 0:l.constructor)!==d&&(null===(r=null==l?void 0:l._$AO)||void 0===r||r.call(l,!1),void 0===d?l=void 0:(l=new d(t),l._$AT(t,i,s)),void 0!==s?(null!==(o=(a=i)._$Co)&&void 0!==o?o:a._$Co=[])[s]=l:i._$Cl=l),void 0!==l&&(e=Yp(t,l._$AS(t,e.values),l,s)),e}let Xp=class{constructor(t,e){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){var e;const{el:{content:i},parts:s}=this._$AD,n=(null!==(e=null==t?void 0:t.creationScope)&&void 0!==e?e:Tp).importNode(i,!0);jp.currentNode=n;let r=jp.nextNode(),o=0,a=0,l=s[0];for(;void 0!==l;){if(o===l.index){let e;2===l.type?e=new Gp(r,r.nextSibling,this,t):1===l.type?e=new l.ctor(r,l.name,l.strings,this,t):6===l.type&&(e=new eu(r,this,t)),this._$AV.push(e),l=s[++a]}o!==(null==l?void 0:l.index)&&(r=jp.nextNode(),o++)}return jp.currentNode=Tp,n}v(t){let e=0;for(const i of this._$AV)void 0!==i&&(void 0!==i.strings?(i._$AI(t,i,e),e+=i.strings.length-2):i._$AI(t[e])),e++}},Gp=class t{constructor(t,e,i,s){var n;this.type=2,this._$AH=Bp,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=i,this.options=s,this._$Cp=null===(n=null==s?void 0:s.isConnected)||void 0===n||n}get _$AU(){var t,e;return null!==(e=null===(t=this._$AM)||void 0===t?void 0:t._$AU)&&void 0!==e?e:this._$Cp}get parentNode(){let t=this._$AA.parentNode;const e=this._$AM;return void 0!==e&&11===(null==t?void 0:t.nodeType)&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=Yp(this,t,e),Op(t)?t===Bp||null==t||""===t?(this._$AH!==Bp&&this._$AR(),this._$AH=Bp):t!==this._$AH&&t!==Fp&&this._(t):void 0!==t._$litType$?this.g(t):void 0!==t.nodeType?this.$(t):(t=>kp(t)||"function"==typeof(null==t?void 0:t[Symbol.iterator]))(t)?this.T(t):this._(t)}k(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}$(t){this._$AH!==t&&(this._$AR(),this._$AH=this.k(t))}_(t){this._$AH!==Bp&&Op(this._$AH)?this._$AA.nextSibling.data=t:this.$(Tp.createTextNode(t)),this._$AH=t}g(t){var e;const{values:i,_$litType$:s}=t,n="number"==typeof s?this._$AC(t):(void 0===s.el&&(s.el=qp.createElement(Wp(s.h,s.h[0]),this.options)),s);if((null===(e=this._$AH)||void 0===e?void 0:e._$AD)===n)this._$AH.v(i);else{const t=new Xp(n,this),e=t.u(this.options);t.v(i),this.$(e),this._$AH=t}}_$AC(t){let e=Vp.get(t.strings);return void 0===e&&Vp.set(t.strings,e=new qp(t)),e}T(e){kp(this._$AH)||(this._$AH=[],this._$AR());const i=this._$AH;let s,n=0;for(const r of e)n===i.length?i.push(s=new t(this.k(Ip()),this.k(Ip()),this,this.options)):s=i[n],s._$AI(r),n++;n<i.length&&(this._$AR(s&&s._$AB.nextSibling,n),i.length=n)}_$AR(t=this._$AA.nextSibling,e){var i;for(null===(i=this._$AP)||void 0===i||i.call(this,!1,!0,e);t&&t!==this._$AB;){const e=t.nextSibling;t.remove(),t=e}}setConnected(t){var e;void 0===this._$AM&&(this._$Cp=t,null===(e=this._$AP)||void 0===e||e.call(this,t))}},Kp=class{constructor(t,e,i,s,n){this.type=1,this._$AH=Bp,this._$AN=void 0,this.element=t,this.name=e,this._$AM=s,this.options=n,i.length>2||""!==i[0]||""!==i[1]?(this._$AH=Array(i.length-1).fill(new String),this.strings=i):this._$AH=Bp}get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}_$AI(t,e=this,i,s){const n=this.strings;let r=!1;if(void 0===n)t=Yp(this,t,e,0),r=!Op(t)||t!==this._$AH&&t!==Fp,r&&(this._$AH=t);else{const s=t;let o,a;for(t=n[0],o=0;o<n.length-1;o++)a=Yp(this,s[i+o],e,o),a===Fp&&(a=this._$AH[o]),r||(r=!Op(a)||a!==this._$AH[o]),a===Bp?t=Bp:t!==Bp&&(t+=(null!=a?a:"")+n[o+1]),this._$AH[o]=a}r&&!s&&this.j(t)}j(t){t===Bp?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,null!=t?t:"")}},Jp=class extends Kp{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===Bp?void 0:t}};const Zp=$p?$p.emptyScript:"";let Qp=class extends Kp{constructor(){super(...arguments),this.type=4}j(t){t&&t!==Bp?this.element.setAttribute(this.name,Zp):this.element.removeAttribute(this.name)}},tu=class extends Kp{constructor(t,e,i,s,n){super(t,e,i,s,n),this.type=5}_$AI(t,e=this){var i;if((t=null!==(i=Yp(this,t,e,0))&&void 0!==i?i:Bp)===Fp)return;const s=this._$AH,n=t===Bp&&s!==Bp||t.capture!==s.capture||t.once!==s.once||t.passive!==s.passive,r=t!==Bp&&(s===Bp||n);n&&this.element.removeEventListener(this.name,this,s),r&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){var e,i;"function"==typeof this._$AH?this._$AH.call(null!==(i=null===(e=this.options)||void 0===e?void 0:e.host)&&void 0!==i?i:this.element,t):this._$AH.handleEvent(t)}},eu=class{constructor(t,e,i){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=i}get _$AU(){return this._$AM._$AU}_$AI(t){Yp(this,t)}};const iu=xp.litHtmlPolyfillSupport;null==iu||iu(qp,Gp),(null!==(yp=xp.litHtmlVersions)&&void 0!==yp?yp:xp.litHtmlVersions=[]).push("2.8.0");
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
var su,nu;let ru=class extends bp{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){var t,e;const i=super.createRenderRoot();return null!==(t=(e=this.renderOptions).renderBefore)&&void 0!==t||(e.renderBefore=i.firstChild),i}update(t){const e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=((t,e,i)=>{var s,n;const r=null!==(s=null==i?void 0:i.renderBefore)&&void 0!==s?s:e;let o=r._$litPart$;if(void 0===o){const t=null!==(n=null==i?void 0:i.renderBefore)&&void 0!==n?n:null;r._$litPart$=o=new Gp(e.insertBefore(Ip(),t),t,void 0,null!=i?i:{})}return o._$AI(t),o})(e,this.renderRoot,this.renderOptions)}connectedCallback(){var t;super.connectedCallback(),null===(t=this._$Do)||void 0===t||t.setConnected(!0)}disconnectedCallback(){var t;super.disconnectedCallback(),null===(t=this._$Do)||void 0===t||t.setConnected(!1)}render(){return Fp}};ru.finalized=!0,ru._$litElement$=!0,null===(su=globalThis.litElementHydrateSupport)||void 0===su||su.call(globalThis,{LitElement:ru});const ou=globalThis.litElementPolyfillSupport;null==ou||ou({LitElement:ru}),(null!==(nu=globalThis.litElementVersions)&&void 0!==nu?nu:globalThis.litElementVersions=[]).push("3.3.3");
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
const au=(t,e)=>"method"===e.kind&&e.descriptor&&!("value"in e.descriptor)?{...e,finisher(i){i.createProperty(e.key,t)}}:{kind:"field",key:Symbol(),placement:"own",descriptor:{},originalKey:e.key,initializer(){"function"==typeof e.initializer&&(this[e.key]=e.initializer.call(this))},finisher(i){i.createProperty(e.key,t)}};function lu(t){return(e,i)=>void 0!==i?((t,e,i)=>{e.constructor.createProperty(i,t)})(t,e,i):au(t,e)}
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */function du(t){return lu({...t,state:!0})}
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
/**
     * @license
     * Copyright 2021 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
var cu;null===(cu=window.HTMLSlotElement)||void 0===cu||cu.prototype.assignedElements;
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
const hu=1,pu=t=>(...e)=>({_$litDirective$:t,values:e});let uu=class{constructor(t){}get _$AU(){return this._$AM._$AU}_$AT(t,e,i){this._$Ct=t,this._$AM=e,this._$Ci=i}_$AS(t,e){return this.update(t,e)}update(t,e){return this.render(...e)}};
/**
     * @license
     * Copyright 2018 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */const mu=pu(class extends uu{constructor(t){var e;if(super(t),t.type!==hu||"class"!==t.name||(null===(e=t.strings)||void 0===e?void 0:e.length)>2)throw Error("`classMap()` can only be used in the `class` attribute and must be the only part in the attribute.")}render(t){return" "+Object.keys(t).filter(e=>t[e]).join(" ")+" "}update(t,[e]){var i,s;if(void 0===this.it){this.it=new Set,void 0!==t.strings&&(this.nt=new Set(t.strings.join(" ").split(/\s/).filter(t=>""!==t)));for(const t in e)e[t]&&!(null===(i=this.nt)||void 0===i?void 0:i.has(t))&&this.it.add(t);return this.render(e)}const n=t.element.classList;this.it.forEach(t=>{t in e||(n.remove(t),this.it.delete(t))});for(const t in e){const i=!!e[t];i===this.it.has(t)||(null===(s=this.nt)||void 0===s?void 0:s.has(t))||(i?(n.add(t),this.it.add(t)):(n.remove(t),this.it.delete(t)))}return Fp}}),fu="important",gu=" !"+fu,vu=pu(class extends uu{constructor(t){var e;if(super(t),t.type!==hu||"style"!==t.name||(null===(e=t.strings)||void 0===e?void 0:e.length)>2)throw Error("The `styleMap` directive must be used in the `style` attribute and must be the only part in the attribute.")}render(t){return Object.keys(t).reduce((e,i)=>{const s=t[i];return null==s?e:e+`${i=i.includes("-")?i:i.replace(/(?:^(webkit|moz|ms|o)|)(?=[A-Z])/g,"-$&").toLowerCase()}:${s};`},"")}update(t,[e]){const{style:i}=t.element;if(void 0===this.ht){this.ht=new Set;for(const t in e)this.ht.add(t);return this.render(e)}this.ht.forEach(t=>{null==e[t]&&(this.ht.delete(t),t.includes("-")?i.removeProperty(t):i[t]="")});for(const t in e){const s=e[t];if(null!=s){this.ht.add(t);const e="string"==typeof s&&s.endsWith(gu);t.includes("-")||e?i.setProperty(t,e?s.slice(0,-11):s,e?fu:""):i[t]=s}}return Fp}});
/**
     * @license
     * Copyright 2018 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
/**
     * @license
     * Copyright 2018 Google LLC
     * SPDX-License-Identifier: Apache-2.0
     */
class _u extends Qi{constructor(){super(...arguments),this.primary=!1,this.accent=!1,this.unbounded=!1,this.disabled=!1,this.activated=!1,this.selected=!1,this.internalUseStateLayerCustomProperties=!1,this.hovering=!1,this.bgFocused=!1,this.fgActivation=!1,this.fgDeactivation=!1,this.fgScale="",this.fgSize="",this.translateStart="",this.translateEnd="",this.leftPos="",this.topPos="",this.mdcFoundationClass=sp}get isActive(){return t=this.parentElement||this,e=":active",(t.matches||t.webkitMatchesSelector||t.msMatchesSelector).call(t,e);
/**
     * @license
     * Copyright 2018 Google Inc.
     *
     * Permission is hereby granted, free of charge, to any person obtaining a copy
     * of this software and associated documentation files (the "Software"), to deal
     * in the Software without restriction, including without limitation the rights
     * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
     * copies of the Software, and to permit persons to whom the Software is
     * furnished to do so, subject to the following conditions:
     *
     * The above copyright notice and this permission notice shall be included in
     * all copies or substantial portions of the Software.
     *
     * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
     * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
     * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
     * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
     * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
     * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
     * THE SOFTWARE.
     */
var t,e}createAdapter(){return{browserSupportsCssVars:()=>!0,isUnbounded:()=>this.unbounded,isSurfaceActive:()=>this.isActive,isSurfaceDisabled:()=>this.disabled,addClass:t=>{switch(t){case"mdc-ripple-upgraded--background-focused":this.bgFocused=!0;break;case"mdc-ripple-upgraded--foreground-activation":this.fgActivation=!0;break;case"mdc-ripple-upgraded--foreground-deactivation":this.fgDeactivation=!0}},removeClass:t=>{switch(t){case"mdc-ripple-upgraded--background-focused":this.bgFocused=!1;break;case"mdc-ripple-upgraded--foreground-activation":this.fgActivation=!1;break;case"mdc-ripple-upgraded--foreground-deactivation":this.fgDeactivation=!1}},containsEventTarget:()=>!0,registerInteractionHandler:()=>{},deregisterInteractionHandler:()=>{},registerDocumentInteractionHandler:()=>{},deregisterDocumentInteractionHandler:()=>{},registerResizeHandler:()=>{},deregisterResizeHandler:()=>{},updateCssVariable:(t,e)=>{switch(t){case"--mdc-ripple-fg-scale":this.fgScale=e;break;case"--mdc-ripple-fg-size":this.fgSize=e;break;case"--mdc-ripple-fg-translate-end":this.translateEnd=e;break;case"--mdc-ripple-fg-translate-start":this.translateStart=e;break;case"--mdc-ripple-left":this.leftPos=e;break;case"--mdc-ripple-top":this.topPos=e}},computeBoundingRect:()=>(this.parentElement||this).getBoundingClientRect(),getWindowPageOffset:()=>({x:window.pageXOffset,y:window.pageYOffset})}}startPress(t){this.waitForFoundation(()=>{this.mdcFoundation.activate(t)})}endPress(){this.waitForFoundation(()=>{this.mdcFoundation.deactivate()})}startFocus(){this.waitForFoundation(()=>{this.mdcFoundation.handleFocus()})}endFocus(){this.waitForFoundation(()=>{this.mdcFoundation.handleBlur()})}startHover(){this.hovering=!0}endHover(){this.hovering=!1}waitForFoundation(t){this.mdcFoundation?t():this.updateComplete.then(t)}update(t){t.has("disabled")&&this.disabled&&this.endHover(),super.update(t)}render(){const t=this.activated&&(this.primary||!this.accent),e=this.selected&&(this.primary||!this.accent),i={"mdc-ripple-surface--accent":this.accent,"mdc-ripple-surface--primary--activated":t,"mdc-ripple-surface--accent--activated":this.accent&&this.activated,"mdc-ripple-surface--primary--selected":e,"mdc-ripple-surface--accent--selected":this.accent&&this.selected,"mdc-ripple-surface--disabled":this.disabled,"mdc-ripple-surface--hover":this.hovering,"mdc-ripple-surface--primary":this.primary,"mdc-ripple-surface--selected":this.selected,"mdc-ripple-upgraded--background-focused":this.bgFocused,"mdc-ripple-upgraded--foreground-activation":this.fgActivation,"mdc-ripple-upgraded--foreground-deactivation":this.fgDeactivation,"mdc-ripple-upgraded--unbounded":this.unbounded,"mdc-ripple-surface--internal-use-state-layer-custom-properties":this.internalUseStateLayerCustomProperties};return zp`
        <div class="mdc-ripple-surface mdc-ripple-upgraded ${mu(i)}"
          style="${vu({"--mdc-ripple-fg-scale":this.fgScale,"--mdc-ripple-fg-size":this.fgSize,"--mdc-ripple-fg-translate-end":this.translateEnd,"--mdc-ripple-fg-translate-start":this.translateStart,"--mdc-ripple-left":this.leftPos,"--mdc-ripple-top":this.topPos})}"></div>`}}n([
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
function(t){return(({finisher:t,descriptor:e})=>(i,s)=>{var n;if(void 0===s){const s=null!==(n=i.originalKey)&&void 0!==n?n:i.key,r=null!=e?{kind:"method",placement:"prototype",key:s,descriptor:e(i.key)}:{...i,key:s};return null!=t&&(r.finisher=function(e){t(e,s)}),r}{const n=i.constructor;void 0!==e&&Object.defineProperty(i,s,e(s)),null==t||t(n,s)}})({descriptor:e=>{const i={get(){var e,i;return null!==(i=null===(e=this.renderRoot)||void 0===e?void 0:e.querySelector(t))&&void 0!==i?i:null},enumerable:!0,configurable:!0};return i}})}(".mdc-ripple-surface")],_u.prototype,"mdcRoot",void 0),n([lu({type:Boolean})],_u.prototype,"primary",void 0),n([lu({type:Boolean})],_u.prototype,"accent",void 0),n([lu({type:Boolean})],_u.prototype,"unbounded",void 0),n([lu({type:Boolean})],_u.prototype,"disabled",void 0),n([lu({type:Boolean})],_u.prototype,"activated",void 0),n([lu({type:Boolean})],_u.prototype,"selected",void 0),n([lu({type:Boolean})],_u.prototype,"internalUseStateLayerCustomProperties",void 0),n([du()],_u.prototype,"hovering",void 0),n([du()],_u.prototype,"bgFocused",void 0),n([du()],_u.prototype,"fgActivation",void 0),n([du()],_u.prototype,"fgDeactivation",void 0),n([du()],_u.prototype,"fgScale",void 0),n([du()],_u.prototype,"fgSize",void 0),n([du()],_u.prototype,"translateStart",void 0),n([du()],_u.prototype,"translateEnd",void 0),n([du()],_u.prototype,"leftPos",void 0),n([du()],_u.prototype,"topPos",void 0);
/**
     * @license
     * Copyright 2016 Google Inc.
     *
     * Permission is hereby granted, free of charge, to any person obtaining a copy
     * of this software and associated documentation files (the "Software"), to deal
     * in the Software without restriction, including without limitation the rights
     * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
     * copies of the Software, and to permit persons to whom the Software is
     * furnished to do so, subject to the following conditions:
     *
     * The above copyright notice and this permission notice shall be included in
     * all copies or substantial portions of the Software.
     *
     * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
     * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
     * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
     * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
     * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
     * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
     * THE SOFTWARE.
     */
var bu=function(){function t(t){void 0===t&&(t={}),this.adapter=t}return Object.defineProperty(t,"cssClasses",{get:function(){return{}},enumerable:!1,configurable:!0}),Object.defineProperty(t,"strings",{get:function(){return{}},enumerable:!1,configurable:!0}),Object.defineProperty(t,"numbers",{get:function(){return{}},enumerable:!1,configurable:!0}),Object.defineProperty(t,"defaultAdapter",{get:function(){return{}},enumerable:!1,configurable:!0}),t.prototype.init=function(){},t.prototype.destroy=function(){},t}(),yu={NOTCH_ELEMENT_SELECTOR:".mdc-notched-outline__notch"},xu={NOTCH_ELEMENT_PADDING:8},$u={NO_LABEL:"mdc-notched-outline--no-label",OUTLINE_NOTCHED:"mdc-notched-outline--notched",OUTLINE_UPGRADED:"mdc-notched-outline--upgraded"},wu=function(t){function e(i){return t.call(this,s(s({},e.defaultAdapter),i))||this}return i(e,t),Object.defineProperty(e,"strings",{get:function(){return yu},enumerable:!1,configurable:!0}),Object.defineProperty(e,"cssClasses",{get:function(){return $u},enumerable:!1,configurable:!0}),Object.defineProperty(e,"numbers",{get:function(){return xu},enumerable:!1,configurable:!0}),Object.defineProperty(e,"defaultAdapter",{get:function(){return{addClass:function(){},removeClass:function(){},setNotchWidthProperty:function(){},removeNotchWidthProperty:function(){}}},enumerable:!1,configurable:!0}),e.prototype.notch=function(t){var i=e.cssClasses.OUTLINE_NOTCHED;t>0&&(t+=xu.NOTCH_ELEMENT_PADDING),this.adapter.setNotchWidthProperty(t),this.adapter.addClass(i)},e.prototype.closeNotch=function(){var t=e.cssClasses.OUTLINE_NOTCHED;this.adapter.removeClass(t),this.adapter.removeNotchWidthProperty()},e}(bu);
/**
     * @license
     * Copyright 2018 Google Inc.
     *
     * Permission is hereby granted, free of charge, to any person obtaining a copy
     * of this software and associated documentation files (the "Software"), to deal
     * in the Software without restriction, including without limitation the rights
     * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
     * copies of the Software, and to permit persons to whom the Software is
     * furnished to do so, subject to the following conditions:
     *
     * The above copyright notice and this permission notice shall be included in
     * all copies or substantial portions of the Software.
     *
     * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
     * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
     * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
     * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
     * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
     * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
     * THE SOFTWARE.
     */
/**
     * @license
     * Copyright 2019 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
const Au=window,Eu=Au.ShadowRoot&&(void 0===Au.ShadyCSS||Au.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,Su=Symbol(),Cu=new WeakMap;let Tu=class{constructor(t,e,i){if(this._$cssResult$=!0,i!==Su)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o;const e=this.t;if(Eu&&void 0===t){const i=void 0!==e&&1===e.length;i&&(t=Cu.get(e)),void 0===t&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),i&&Cu.set(e,t))}return t}toString(){return this.cssText}};const Iu=Eu?t=>t:t=>t instanceof CSSStyleSheet?(t=>{let e="";for(const i of t.cssRules)e+=i.cssText;return(t=>new Tu("string"==typeof t?t:t+"",void 0,Su))(e)})(t):t;
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */var Ou;const ku=window,Ru=ku.trustedTypes,Pu=Ru?Ru.emptyScript:"",Lu=ku.reactiveElementPolyfillSupport,Mu={toAttribute(t,e){switch(e){case Boolean:t=t?Pu:null;break;case Object:case Array:t=null==t?t:JSON.stringify(t)}return t},fromAttribute(t,e){let i=t;switch(e){case Boolean:i=null!==t;break;case Number:i=null===t?null:Number(t);break;case Object:case Array:try{i=JSON.parse(t)}catch(t){i=null}}return i}},Nu=(t,e)=>e!==t&&(e==e||t==t),Du={attribute:!0,type:String,converter:Mu,reflect:!1,hasChanged:Nu},Hu="finalized";let Uu=class extends HTMLElement{constructor(){super(),this._$Ei=new Map,this.isUpdatePending=!1,this.hasUpdated=!1,this._$El=null,this._$Eu()}static addInitializer(t){var e;this.finalize(),(null!==(e=this.h)&&void 0!==e?e:this.h=[]).push(t)}static get observedAttributes(){this.finalize();const t=[];return this.elementProperties.forEach((e,i)=>{const s=this._$Ep(i,e);void 0!==s&&(this._$Ev.set(s,i),t.push(s))}),t}static createProperty(t,e=Du){if(e.state&&(e.attribute=!1),this.finalize(),this.elementProperties.set(t,e),!e.noAccessor&&!this.prototype.hasOwnProperty(t)){const i="symbol"==typeof t?Symbol():"__"+t,s=this.getPropertyDescriptor(t,i,e);void 0!==s&&Object.defineProperty(this.prototype,t,s)}}static getPropertyDescriptor(t,e,i){return{get(){return this[e]},set(s){const n=this[t];this[e]=s,this.requestUpdate(t,n,i)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)||Du}static finalize(){if(this.hasOwnProperty(Hu))return!1;this[Hu]=!0;const t=Object.getPrototypeOf(this);if(t.finalize(),void 0!==t.h&&(this.h=[...t.h]),this.elementProperties=new Map(t.elementProperties),this._$Ev=new Map,this.hasOwnProperty("properties")){const t=this.properties,e=[...Object.getOwnPropertyNames(t),...Object.getOwnPropertySymbols(t)];for(const i of e)this.createProperty(i,t[i])}return this.elementStyles=this.finalizeStyles(this.styles),!0}static finalizeStyles(t){const e=[];if(Array.isArray(t)){const i=new Set(t.flat(1/0).reverse());for(const t of i)e.unshift(Iu(t))}else void 0!==t&&e.push(Iu(t));return e}static _$Ep(t,e){const i=e.attribute;return!1===i?void 0:"string"==typeof i?i:"string"==typeof t?t.toLowerCase():void 0}_$Eu(){var t;this._$E_=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$Eg(),this.requestUpdate(),null===(t=this.constructor.h)||void 0===t||t.forEach(t=>t(this))}addController(t){var e,i;(null!==(e=this._$ES)&&void 0!==e?e:this._$ES=[]).push(t),void 0!==this.renderRoot&&this.isConnected&&(null===(i=t.hostConnected)||void 0===i||i.call(t))}removeController(t){var e;null===(e=this._$ES)||void 0===e||e.splice(this._$ES.indexOf(t)>>>0,1)}_$Eg(){this.constructor.elementProperties.forEach((t,e)=>{this.hasOwnProperty(e)&&(this._$Ei.set(e,this[e]),delete this[e])})}createRenderRoot(){var t;const e=null!==(t=this.shadowRoot)&&void 0!==t?t:this.attachShadow(this.constructor.shadowRootOptions);return((t,e)=>{Eu?t.adoptedStyleSheets=e.map(t=>t instanceof CSSStyleSheet?t:t.styleSheet):e.forEach(e=>{const i=document.createElement("style"),s=Au.litNonce;void 0!==s&&i.setAttribute("nonce",s),i.textContent=e.cssText,t.appendChild(i)})})(e,this.constructor.elementStyles),e}connectedCallback(){var t;void 0===this.renderRoot&&(this.renderRoot=this.createRenderRoot()),this.enableUpdating(!0),null===(t=this._$ES)||void 0===t||t.forEach(t=>{var e;return null===(e=t.hostConnected)||void 0===e?void 0:e.call(t)})}enableUpdating(t){}disconnectedCallback(){var t;null===(t=this._$ES)||void 0===t||t.forEach(t=>{var e;return null===(e=t.hostDisconnected)||void 0===e?void 0:e.call(t)})}attributeChangedCallback(t,e,i){this._$AK(t,i)}_$EO(t,e,i=Du){var s;const n=this.constructor._$Ep(t,i);if(void 0!==n&&!0===i.reflect){const r=(void 0!==(null===(s=i.converter)||void 0===s?void 0:s.toAttribute)?i.converter:Mu).toAttribute(e,i.type);this._$El=t,null==r?this.removeAttribute(n):this.setAttribute(n,r),this._$El=null}}_$AK(t,e){var i;const s=this.constructor,n=s._$Ev.get(t);if(void 0!==n&&this._$El!==n){const t=s.getPropertyOptions(n),r="function"==typeof t.converter?{fromAttribute:t.converter}:void 0!==(null===(i=t.converter)||void 0===i?void 0:i.fromAttribute)?t.converter:Mu;this._$El=n,this[n]=r.fromAttribute(e,t.type),this._$El=null}}requestUpdate(t,e,i){let s=!0;void 0!==t&&(((i=i||this.constructor.getPropertyOptions(t)).hasChanged||Nu)(this[t],e)?(this._$AL.has(t)||this._$AL.set(t,e),!0===i.reflect&&this._$El!==t&&(void 0===this._$EC&&(this._$EC=new Map),this._$EC.set(t,i))):s=!1),!this.isUpdatePending&&s&&(this._$E_=this._$Ej())}async _$Ej(){this.isUpdatePending=!0;try{await this._$E_}catch(t){Promise.reject(t)}const t=this.scheduleUpdate();return null!=t&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){var t;if(!this.isUpdatePending)return;this.hasUpdated,this._$Ei&&(this._$Ei.forEach((t,e)=>this[e]=t),this._$Ei=void 0);let e=!1;const i=this._$AL;try{e=this.shouldUpdate(i),e?(this.willUpdate(i),null===(t=this._$ES)||void 0===t||t.forEach(t=>{var e;return null===(e=t.hostUpdate)||void 0===e?void 0:e.call(t)}),this.update(i)):this._$Ek()}catch(t){throw e=!1,this._$Ek(),t}e&&this._$AE(i)}willUpdate(t){}_$AE(t){var e;null===(e=this._$ES)||void 0===e||e.forEach(t=>{var e;return null===(e=t.hostUpdated)||void 0===e?void 0:e.call(t)}),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$Ek(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$E_}shouldUpdate(t){return!0}update(t){void 0!==this._$EC&&(this._$EC.forEach((t,e)=>this._$EO(e,this[e],t)),this._$EC=void 0),this._$Ek()}updated(t){}firstUpdated(t){}};
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
var zu;Uu[Hu]=!0,Uu.elementProperties=new Map,Uu.elementStyles=[],Uu.shadowRootOptions={mode:"open"},null==Lu||Lu({ReactiveElement:Uu}),(null!==(Ou=ku.reactiveElementVersions)&&void 0!==Ou?Ou:ku.reactiveElementVersions=[]).push("1.6.3");const Fu=window,Bu=Fu.trustedTypes,Vu=Bu?Bu.createPolicy("lit-html",{createHTML:t=>t}):void 0,ju="$lit$",Wu=`lit$${(Math.random()+"").slice(9)}$`,qu="?"+Wu,Yu=`<${qu}>`,Xu=document,Gu=()=>Xu.createComment(""),Ku=t=>null===t||"object"!=typeof t&&"function"!=typeof t,Ju=Array.isArray,Zu="[ \t\n\f\r]",Qu=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,tm=/-->/g,em=/>/g,im=RegExp(`>|${Zu}(?:([^\\s"'>=/]+)(${Zu}*=${Zu}*(?:[^ \t\n\f\r"'\`<>=]|("|')|))|$)`,"g"),sm=/'/g,nm=/"/g,rm=/^(?:script|style|textarea|title)$/i,om=(t=>(e,...i)=>({_$litType$:t,strings:e,values:i}))(1),am=Symbol.for("lit-noChange"),lm=Symbol.for("lit-nothing"),dm=new WeakMap,cm=Xu.createTreeWalker(Xu,129,null,!1);function hm(t,e){if(!Array.isArray(t)||!t.hasOwnProperty("raw"))throw Error("invalid template strings array");return void 0!==Vu?Vu.createHTML(e):e}let pm=class t{constructor({strings:e,_$litType$:i},s){let n;this.parts=[];let r=0,o=0;const a=e.length-1,l=this.parts,[d,c]=((t,e)=>{const i=t.length-1,s=[];let n,r=2===e?"<svg>":"",o=Qu;for(let e=0;e<i;e++){const i=t[e];let a,l,d=-1,c=0;for(;c<i.length&&(o.lastIndex=c,l=o.exec(i),null!==l);)c=o.lastIndex,o===Qu?"!--"===l[1]?o=tm:void 0!==l[1]?o=em:void 0!==l[2]?(rm.test(l[2])&&(n=RegExp("</"+l[2],"g")),o=im):void 0!==l[3]&&(o=im):o===im?">"===l[0]?(o=null!=n?n:Qu,d=-1):void 0===l[1]?d=-2:(d=o.lastIndex-l[2].length,a=l[1],o=void 0===l[3]?im:'"'===l[3]?nm:sm):o===nm||o===sm?o=im:o===tm||o===em?o=Qu:(o=im,n=void 0);const h=o===im&&t[e+1].startsWith("/>")?" ":"";r+=o===Qu?i+Yu:d>=0?(s.push(a),i.slice(0,d)+ju+i.slice(d)+Wu+h):i+Wu+(-2===d?(s.push(void 0),e):h)}return[hm(t,r+(t[i]||"<?>")+(2===e?"</svg>":"")),s]})(e,i);if(this.el=t.createElement(d,s),cm.currentNode=this.el.content,2===i){const t=this.el.content,e=t.firstChild;e.remove(),t.append(...e.childNodes)}for(;null!==(n=cm.nextNode())&&l.length<a;){if(1===n.nodeType){if(n.hasAttributes()){const t=[];for(const e of n.getAttributeNames())if(e.endsWith(ju)||e.startsWith(Wu)){const i=c[o++];if(t.push(e),void 0!==i){const t=n.getAttribute(i.toLowerCase()+ju).split(Wu),e=/([.?@])?(.*)/.exec(i);l.push({type:1,index:r,name:e[2],strings:t,ctor:"."===e[1]?vm:"?"===e[1]?bm:"@"===e[1]?ym:gm})}else l.push({type:6,index:r})}for(const e of t)n.removeAttribute(e)}if(rm.test(n.tagName)){const t=n.textContent.split(Wu),e=t.length-1;if(e>0){n.textContent=Bu?Bu.emptyScript:"";for(let i=0;i<e;i++)n.append(t[i],Gu()),cm.nextNode(),l.push({type:2,index:++r});n.append(t[e],Gu())}}}else if(8===n.nodeType)if(n.data===qu)l.push({type:2,index:r});else{let t=-1;for(;-1!==(t=n.data.indexOf(Wu,t+1));)l.push({type:7,index:r}),t+=Wu.length-1}r++}}static createElement(t,e){const i=Xu.createElement("template");return i.innerHTML=t,i}};function um(t,e,i=t,s){var n,r,o,a;if(e===am)return e;let l=void 0!==s?null===(n=i._$Co)||void 0===n?void 0:n[s]:i._$Cl;const d=Ku(e)?void 0:e._$litDirective$;return(null==l?void 0:l.constructor)!==d&&(null===(r=null==l?void 0:l._$AO)||void 0===r||r.call(l,!1),void 0===d?l=void 0:(l=new d(t),l._$AT(t,i,s)),void 0!==s?(null!==(o=(a=i)._$Co)&&void 0!==o?o:a._$Co=[])[s]=l:i._$Cl=l),void 0!==l&&(e=um(t,l._$AS(t,e.values),l,s)),e}let mm=class{constructor(t,e){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){var e;const{el:{content:i},parts:s}=this._$AD,n=(null!==(e=null==t?void 0:t.creationScope)&&void 0!==e?e:Xu).importNode(i,!0);cm.currentNode=n;let r=cm.nextNode(),o=0,a=0,l=s[0];for(;void 0!==l;){if(o===l.index){let e;2===l.type?e=new fm(r,r.nextSibling,this,t):1===l.type?e=new l.ctor(r,l.name,l.strings,this,t):6===l.type&&(e=new xm(r,this,t)),this._$AV.push(e),l=s[++a]}o!==(null==l?void 0:l.index)&&(r=cm.nextNode(),o++)}return cm.currentNode=Xu,n}v(t){let e=0;for(const i of this._$AV)void 0!==i&&(void 0!==i.strings?(i._$AI(t,i,e),e+=i.strings.length-2):i._$AI(t[e])),e++}},fm=class t{constructor(t,e,i,s){var n;this.type=2,this._$AH=lm,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=i,this.options=s,this._$Cp=null===(n=null==s?void 0:s.isConnected)||void 0===n||n}get _$AU(){var t,e;return null!==(e=null===(t=this._$AM)||void 0===t?void 0:t._$AU)&&void 0!==e?e:this._$Cp}get parentNode(){let t=this._$AA.parentNode;const e=this._$AM;return void 0!==e&&11===(null==t?void 0:t.nodeType)&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=um(this,t,e),Ku(t)?t===lm||null==t||""===t?(this._$AH!==lm&&this._$AR(),this._$AH=lm):t!==this._$AH&&t!==am&&this._(t):void 0!==t._$litType$?this.g(t):void 0!==t.nodeType?this.$(t):(t=>Ju(t)||"function"==typeof(null==t?void 0:t[Symbol.iterator]))(t)?this.T(t):this._(t)}k(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}$(t){this._$AH!==t&&(this._$AR(),this._$AH=this.k(t))}_(t){this._$AH!==lm&&Ku(this._$AH)?this._$AA.nextSibling.data=t:this.$(Xu.createTextNode(t)),this._$AH=t}g(t){var e;const{values:i,_$litType$:s}=t,n="number"==typeof s?this._$AC(t):(void 0===s.el&&(s.el=pm.createElement(hm(s.h,s.h[0]),this.options)),s);if((null===(e=this._$AH)||void 0===e?void 0:e._$AD)===n)this._$AH.v(i);else{const t=new mm(n,this),e=t.u(this.options);t.v(i),this.$(e),this._$AH=t}}_$AC(t){let e=dm.get(t.strings);return void 0===e&&dm.set(t.strings,e=new pm(t)),e}T(e){Ju(this._$AH)||(this._$AH=[],this._$AR());const i=this._$AH;let s,n=0;for(const r of e)n===i.length?i.push(s=new t(this.k(Gu()),this.k(Gu()),this,this.options)):s=i[n],s._$AI(r),n++;n<i.length&&(this._$AR(s&&s._$AB.nextSibling,n),i.length=n)}_$AR(t=this._$AA.nextSibling,e){var i;for(null===(i=this._$AP)||void 0===i||i.call(this,!1,!0,e);t&&t!==this._$AB;){const e=t.nextSibling;t.remove(),t=e}}setConnected(t){var e;void 0===this._$AM&&(this._$Cp=t,null===(e=this._$AP)||void 0===e||e.call(this,t))}},gm=class{constructor(t,e,i,s,n){this.type=1,this._$AH=lm,this._$AN=void 0,this.element=t,this.name=e,this._$AM=s,this.options=n,i.length>2||""!==i[0]||""!==i[1]?(this._$AH=Array(i.length-1).fill(new String),this.strings=i):this._$AH=lm}get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}_$AI(t,e=this,i,s){const n=this.strings;let r=!1;if(void 0===n)t=um(this,t,e,0),r=!Ku(t)||t!==this._$AH&&t!==am,r&&(this._$AH=t);else{const s=t;let o,a;for(t=n[0],o=0;o<n.length-1;o++)a=um(this,s[i+o],e,o),a===am&&(a=this._$AH[o]),r||(r=!Ku(a)||a!==this._$AH[o]),a===lm?t=lm:t!==lm&&(t+=(null!=a?a:"")+n[o+1]),this._$AH[o]=a}r&&!s&&this.j(t)}j(t){t===lm?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,null!=t?t:"")}},vm=class extends gm{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===lm?void 0:t}};const _m=Bu?Bu.emptyScript:"";let bm=class extends gm{constructor(){super(...arguments),this.type=4}j(t){t&&t!==lm?this.element.setAttribute(this.name,_m):this.element.removeAttribute(this.name)}},ym=class extends gm{constructor(t,e,i,s,n){super(t,e,i,s,n),this.type=5}_$AI(t,e=this){var i;if((t=null!==(i=um(this,t,e,0))&&void 0!==i?i:lm)===am)return;const s=this._$AH,n=t===lm&&s!==lm||t.capture!==s.capture||t.once!==s.once||t.passive!==s.passive,r=t!==lm&&(s===lm||n);n&&this.element.removeEventListener(this.name,this,s),r&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){var e,i;"function"==typeof this._$AH?this._$AH.call(null!==(i=null===(e=this.options)||void 0===e?void 0:e.host)&&void 0!==i?i:this.element,t):this._$AH.handleEvent(t)}},xm=class{constructor(t,e,i){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=i}get _$AU(){return this._$AM._$AU}_$AI(t){um(this,t)}};const $m=Fu.litHtmlPolyfillSupport;null==$m||$m(pm,fm),(null!==(zu=Fu.litHtmlVersions)&&void 0!==zu?zu:Fu.litHtmlVersions=[]).push("2.8.0");
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
var wm,Am;let Em=class extends Uu{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){var t,e;const i=super.createRenderRoot();return null!==(t=(e=this.renderOptions).renderBefore)&&void 0!==t||(e.renderBefore=i.firstChild),i}update(t){const e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=((t,e,i)=>{var s,n;const r=null!==(s=null==i?void 0:i.renderBefore)&&void 0!==s?s:e;let o=r._$litPart$;if(void 0===o){const t=null!==(n=null==i?void 0:i.renderBefore)&&void 0!==n?n:null;r._$litPart$=o=new fm(e.insertBefore(Gu(),t),t,void 0,null!=i?i:{})}return o._$AI(t),o})(e,this.renderRoot,this.renderOptions)}connectedCallback(){var t;super.connectedCallback(),null===(t=this._$Do)||void 0===t||t.setConnected(!0)}disconnectedCallback(){var t;super.disconnectedCallback(),null===(t=this._$Do)||void 0===t||t.setConnected(!1)}render(){return am}};Em.finalized=!0,Em._$litElement$=!0,null===(wm=globalThis.litElementHydrateSupport)||void 0===wm||wm.call(globalThis,{LitElement:Em});const Sm=globalThis.litElementPolyfillSupport;null==Sm||Sm({LitElement:Em}),(null!==(Am=globalThis.litElementVersions)&&void 0!==Am?Am:globalThis.litElementVersions=[]).push("3.3.3");
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
const Cm=(t,e)=>"method"===e.kind&&e.descriptor&&!("value"in e.descriptor)?{...e,finisher(i){i.createProperty(e.key,t)}}:{kind:"field",key:Symbol(),placement:"own",descriptor:{},originalKey:e.key,initializer(){"function"==typeof e.initializer&&(this[e.key]=e.initializer.call(this))},finisher(i){i.createProperty(e.key,t)}};function Tm(t){return(e,i)=>void 0!==i?((t,e,i)=>{e.constructor.createProperty(i,t)})(t,e,i):Cm(t,e)}
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
function Im(t,e){return(({finisher:t,descriptor:e})=>(i,s)=>{var n;if(void 0===s){const s=null!==(n=i.originalKey)&&void 0!==n?n:i.key,r=null!=e?{kind:"method",placement:"prototype",key:s,descriptor:e(i.key)}:{...i,key:s};return null!=t&&(r.finisher=function(e){t(e,s)}),r}{const n=i.constructor;void 0!==e&&Object.defineProperty(i,s,e(s)),null==t||t(n,s)}})({descriptor:e=>{const i={get(){var e,i;return null!==(i=null===(e=this.renderRoot)||void 0===e?void 0:e.querySelector(t))&&void 0!==i?i:null},enumerable:!0,configurable:!0};return i}})}
/**
     * @license
     * Copyright 2021 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */var Om;null===(Om=window.HTMLSlotElement)||void 0===Om||Om.prototype.assignedElements;
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
const km=1;let Rm=class{constructor(t){}get _$AU(){return this._$AM._$AU}_$AT(t,e,i){this._$Ct=t,this._$AM=e,this._$Ci=i}_$AS(t,e){return this.update(t,e)}update(t,e){return this.render(...e)}};
/**
     * @license
     * Copyright 2018 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */const Pm=(t=>(...e)=>({_$litDirective$:t,values:e}))(class extends Rm{constructor(t){var e;if(super(t),t.type!==km||"class"!==t.name||(null===(e=t.strings)||void 0===e?void 0:e.length)>2)throw Error("`classMap()` can only be used in the `class` attribute and must be the only part in the attribute.")}render(t){return" "+Object.keys(t).filter(e=>t[e]).join(" ")+" "}update(t,[e]){var i,s;if(void 0===this.it){this.it=new Set,void 0!==t.strings&&(this.nt=new Set(t.strings.join(" ").split(/\s/).filter(t=>""!==t)));for(const t in e)e[t]&&!(null===(i=this.nt)||void 0===i?void 0:i.has(t))&&this.it.add(t);return this.render(e)}const n=t.element.classList;this.it.forEach(t=>{t in e||(n.remove(t),this.it.delete(t))});for(const t in e){const i=!!e[t];i===this.it.has(t)||(null===(s=this.nt)||void 0===s?void 0:s.has(t))||(i?(n.add(t),this.it.add(t)):(n.remove(t),this.it.delete(t)))}return am}});
/**
     * @license
     * Copyright 2019 Google LLC
     * SPDX-License-Identifier: Apache-2.0
     */class Lm extends Qi{constructor(){super(...arguments),this.mdcFoundationClass=wu,this.width=0,this.open=!1,this.lastOpen=this.open}createAdapter(){return{addClass:t=>this.mdcRoot.classList.add(t),removeClass:t=>this.mdcRoot.classList.remove(t),setNotchWidthProperty:t=>this.notchElement.style.setProperty("width",`${t}px`),removeNotchWidthProperty:()=>this.notchElement.style.removeProperty("width")}}openOrClose(t,e){this.mdcFoundation&&(t&&void 0!==e?this.mdcFoundation.notch(e):this.mdcFoundation.closeNotch())}render(){this.openOrClose(this.open,this.width);const t=Pm({"mdc-notched-outline--notched":this.open});return om`
      <span class="mdc-notched-outline ${t}">
        <span class="mdc-notched-outline__leading"></span>
        <span class="mdc-notched-outline__notch">
          <slot></slot>
        </span>
        <span class="mdc-notched-outline__trailing"></span>
      </span>`}}n([Im(".mdc-notched-outline")],Lm.prototype,"mdcRoot",void 0),n([Tm({type:Number})],Lm.prototype,"width",void 0),n([Tm({type:Boolean,reflect:!0})],Lm.prototype,"open",void 0),n([Im(".mdc-notched-outline__notch")],Lm.prototype,"notchElement",void 0);
/**
     * @license
     * Copyright 2021 Google LLC
     * SPDX-LIcense-Identifier: Apache-2.0
     */
const Mm=((t,...e)=>{const i=1===t.length?t[0]:e.reduce((e,i,s)=>e+(t=>{if(!0===t._$cssResult$)return t.cssText;if("number"==typeof t)return t;throw Error("Value passed to 'css' function must be a 'css' function result: "+t+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+t[s+1],t[0]);return new oa(i,t,na)})`.mdc-floating-label{-moz-osx-font-smoothing:grayscale;-webkit-font-smoothing:antialiased;font-family:Roboto, sans-serif;font-family:var(--mdc-typography-subtitle1-font-family, var(--mdc-typography-font-family, Roboto, sans-serif));font-size:1rem;font-size:var(--mdc-typography-subtitle1-font-size, 1rem);font-weight:400;font-weight:var(--mdc-typography-subtitle1-font-weight, 400);letter-spacing:0.009375em;letter-spacing:var(--mdc-typography-subtitle1-letter-spacing, 0.009375em);text-decoration:inherit;text-decoration:var(--mdc-typography-subtitle1-text-decoration, inherit);text-transform:inherit;text-transform:var(--mdc-typography-subtitle1-text-transform, inherit);position:absolute;left:0;-webkit-transform-origin:left top;transform-origin:left top;line-height:1.15rem;text-align:left;text-overflow:ellipsis;white-space:nowrap;cursor:text;overflow:hidden;will-change:transform;transition:transform 150ms cubic-bezier(0.4, 0, 0.2, 1),color 150ms cubic-bezier(0.4, 0, 0.2, 1)}[dir=rtl] .mdc-floating-label,.mdc-floating-label[dir=rtl]{right:0;left:auto;-webkit-transform-origin:right top;transform-origin:right top;text-align:right}.mdc-floating-label--float-above{cursor:auto}.mdc-floating-label--required::after{margin-left:1px;margin-right:0px;content:"*"}[dir=rtl] .mdc-floating-label--required::after,.mdc-floating-label--required[dir=rtl]::after{margin-left:0;margin-right:1px}.mdc-floating-label--float-above{transform:translateY(-106%) scale(0.75)}.mdc-floating-label--shake{animation:mdc-floating-label-shake-float-above-standard 250ms 1}@keyframes mdc-floating-label-shake-float-above-standard{0%{transform:translateX(calc(0 - 0%)) translateY(-106%) scale(0.75)}33%{animation-timing-function:cubic-bezier(0.5, 0, 0.701732, 0.495819);transform:translateX(calc(4% - 0%)) translateY(-106%) scale(0.75)}66%{animation-timing-function:cubic-bezier(0.302435, 0.381352, 0.55, 0.956352);transform:translateX(calc(-4% - 0%)) translateY(-106%) scale(0.75)}100%{transform:translateX(calc(0 - 0%)) translateY(-106%) scale(0.75)}}@keyframes mdc-ripple-fg-radius-in{from{animation-timing-function:cubic-bezier(0.4, 0, 0.2, 1);transform:translate(var(--mdc-ripple-fg-translate-start, 0)) scale(1)}to{transform:translate(var(--mdc-ripple-fg-translate-end, 0)) scale(var(--mdc-ripple-fg-scale, 1))}}@keyframes mdc-ripple-fg-opacity-in{from{animation-timing-function:linear;opacity:0}to{opacity:var(--mdc-ripple-fg-opacity, 0)}}@keyframes mdc-ripple-fg-opacity-out{from{animation-timing-function:linear;opacity:var(--mdc-ripple-fg-opacity, 0)}to{opacity:0}}.mdc-line-ripple::before,.mdc-line-ripple::after{position:absolute;bottom:0;left:0;width:100%;border-bottom-style:solid;content:""}.mdc-line-ripple::before{border-bottom-width:1px}.mdc-line-ripple::before{z-index:1}.mdc-line-ripple::after{transform:scaleX(0);border-bottom-width:2px;opacity:0;z-index:2}.mdc-line-ripple::after{transition:transform 180ms cubic-bezier(0.4, 0, 0.2, 1),opacity 180ms cubic-bezier(0.4, 0, 0.2, 1)}.mdc-line-ripple--active::after{transform:scaleX(1);opacity:1}.mdc-line-ripple--deactivating::after{opacity:0}.mdc-notched-outline{display:flex;position:absolute;top:0;right:0;left:0;box-sizing:border-box;width:100%;max-width:100%;height:100%;text-align:left;pointer-events:none}[dir=rtl] .mdc-notched-outline,.mdc-notched-outline[dir=rtl]{text-align:right}.mdc-notched-outline__leading,.mdc-notched-outline__notch,.mdc-notched-outline__trailing{box-sizing:border-box;height:100%;border-top:1px solid;border-bottom:1px solid;pointer-events:none}.mdc-notched-outline__leading{border-left:1px solid;border-right:none;width:12px}[dir=rtl] .mdc-notched-outline__leading,.mdc-notched-outline__leading[dir=rtl]{border-left:none;border-right:1px solid}.mdc-notched-outline__trailing{border-left:none;border-right:1px solid;flex-grow:1}[dir=rtl] .mdc-notched-outline__trailing,.mdc-notched-outline__trailing[dir=rtl]{border-left:1px solid;border-right:none}.mdc-notched-outline__notch{flex:0 0 auto;width:auto;max-width:calc(100% - 12px * 2)}.mdc-notched-outline .mdc-floating-label{display:inline-block;position:relative;max-width:100%}.mdc-notched-outline .mdc-floating-label--float-above{text-overflow:clip}.mdc-notched-outline--upgraded .mdc-floating-label--float-above{max-width:calc(100% / 0.75)}.mdc-notched-outline--notched .mdc-notched-outline__notch{padding-left:0;padding-right:8px;border-top:none}[dir=rtl] .mdc-notched-outline--notched .mdc-notched-outline__notch,.mdc-notched-outline--notched .mdc-notched-outline__notch[dir=rtl]{padding-left:8px;padding-right:0}.mdc-notched-outline--no-label .mdc-notched-outline__notch{display:none}.mdc-select{display:inline-flex;position:relative}.mdc-select:not(.mdc-select--disabled) .mdc-select__selected-text{color:rgba(0, 0, 0, 0.87)}.mdc-select.mdc-select--disabled .mdc-select__selected-text{color:rgba(0, 0, 0, 0.38)}.mdc-select:not(.mdc-select--disabled) .mdc-floating-label{color:rgba(0, 0, 0, 0.6)}.mdc-select:not(.mdc-select--disabled).mdc-select--focused .mdc-floating-label{color:rgba(98, 0, 238, 0.87)}.mdc-select.mdc-select--disabled .mdc-floating-label{color:rgba(0, 0, 0, 0.38)}.mdc-select:not(.mdc-select--disabled) .mdc-select__dropdown-icon{fill:rgba(0, 0, 0, 0.54)}.mdc-select:not(.mdc-select--disabled).mdc-select--focused .mdc-select__dropdown-icon{fill:#6200ee;fill:var(--mdc-theme-primary, #6200ee)}.mdc-select.mdc-select--disabled .mdc-select__dropdown-icon{fill:rgba(0, 0, 0, 0.38)}.mdc-select:not(.mdc-select--disabled)+.mdc-select-helper-text{color:rgba(0, 0, 0, 0.6)}.mdc-select.mdc-select--disabled+.mdc-select-helper-text{color:rgba(0, 0, 0, 0.38)}.mdc-select:not(.mdc-select--disabled) .mdc-select__icon{color:rgba(0, 0, 0, 0.54)}.mdc-select.mdc-select--disabled .mdc-select__icon{color:rgba(0, 0, 0, 0.38)}@media screen and (forced-colors: active),(-ms-high-contrast: active){.mdc-select.mdc-select--disabled .mdc-select__selected-text{color:GrayText}.mdc-select.mdc-select--disabled .mdc-select__dropdown-icon{fill:red}.mdc-select.mdc-select--disabled .mdc-floating-label{color:GrayText}.mdc-select.mdc-select--disabled .mdc-line-ripple::before{border-bottom-color:GrayText}.mdc-select.mdc-select--disabled .mdc-notched-outline__leading,.mdc-select.mdc-select--disabled .mdc-notched-outline__notch,.mdc-select.mdc-select--disabled .mdc-notched-outline__trailing{border-color:GrayText}.mdc-select.mdc-select--disabled .mdc-select__icon{color:GrayText}.mdc-select.mdc-select--disabled+.mdc-select-helper-text{color:GrayText}}.mdc-select .mdc-floating-label{top:50%;transform:translateY(-50%);pointer-events:none}.mdc-select .mdc-select__anchor{padding-left:16px;padding-right:0}[dir=rtl] .mdc-select .mdc-select__anchor,.mdc-select .mdc-select__anchor[dir=rtl]{padding-left:0;padding-right:16px}.mdc-select.mdc-select--with-leading-icon .mdc-select__anchor{padding-left:0;padding-right:0}[dir=rtl] .mdc-select.mdc-select--with-leading-icon .mdc-select__anchor,.mdc-select.mdc-select--with-leading-icon .mdc-select__anchor[dir=rtl]{padding-left:0;padding-right:0}.mdc-select .mdc-select__icon{width:24px;height:24px;font-size:24px}.mdc-select .mdc-select__dropdown-icon{width:24px;height:24px}.mdc-select .mdc-select__menu .mdc-deprecated-list-item{padding-left:16px;padding-right:16px}[dir=rtl] .mdc-select .mdc-select__menu .mdc-deprecated-list-item,.mdc-select .mdc-select__menu .mdc-deprecated-list-item[dir=rtl]{padding-left:16px;padding-right:16px}.mdc-select .mdc-select__menu .mdc-deprecated-list-item__graphic{margin-left:0;margin-right:12px}[dir=rtl] .mdc-select .mdc-select__menu .mdc-deprecated-list-item__graphic,.mdc-select .mdc-select__menu .mdc-deprecated-list-item__graphic[dir=rtl]{margin-left:12px;margin-right:0}.mdc-select__dropdown-icon{margin-left:12px;margin-right:12px;display:inline-flex;position:relative;align-self:center;align-items:center;justify-content:center;flex-shrink:0;pointer-events:none}.mdc-select__dropdown-icon .mdc-select__dropdown-icon-active,.mdc-select__dropdown-icon .mdc-select__dropdown-icon-inactive{position:absolute;top:0;left:0}.mdc-select__dropdown-icon .mdc-select__dropdown-icon-graphic{width:41.6666666667%;height:20.8333333333%}.mdc-select__dropdown-icon .mdc-select__dropdown-icon-inactive{opacity:1;transition:opacity 75ms linear 75ms}.mdc-select__dropdown-icon .mdc-select__dropdown-icon-active{opacity:0;transition:opacity 75ms linear}[dir=rtl] .mdc-select__dropdown-icon,.mdc-select__dropdown-icon[dir=rtl]{margin-left:12px;margin-right:12px}.mdc-select--activated .mdc-select__dropdown-icon .mdc-select__dropdown-icon-inactive{opacity:0;transition:opacity 49.5ms linear}.mdc-select--activated .mdc-select__dropdown-icon .mdc-select__dropdown-icon-active{opacity:1;transition:opacity 100.5ms linear 49.5ms}.mdc-select__anchor{width:200px;min-width:0;flex:1 1 auto;position:relative;box-sizing:border-box;overflow:hidden;outline:none;cursor:pointer}.mdc-select__anchor .mdc-floating-label--float-above{transform:translateY(-106%) scale(0.75)}.mdc-select__selected-text-container{display:flex;appearance:none;pointer-events:none;box-sizing:border-box;width:auto;min-width:0;flex-grow:1;height:28px;border:none;outline:none;padding:0;background-color:transparent;color:inherit}.mdc-select__selected-text{-moz-osx-font-smoothing:grayscale;-webkit-font-smoothing:antialiased;font-family:Roboto, sans-serif;font-family:var(--mdc-typography-subtitle1-font-family, var(--mdc-typography-font-family, Roboto, sans-serif));font-size:1rem;font-size:var(--mdc-typography-subtitle1-font-size, 1rem);line-height:1.75rem;line-height:var(--mdc-typography-subtitle1-line-height, 1.75rem);font-weight:400;font-weight:var(--mdc-typography-subtitle1-font-weight, 400);letter-spacing:0.009375em;letter-spacing:var(--mdc-typography-subtitle1-letter-spacing, 0.009375em);text-decoration:inherit;text-decoration:var(--mdc-typography-subtitle1-text-decoration, inherit);text-transform:inherit;text-transform:var(--mdc-typography-subtitle1-text-transform, inherit);text-overflow:ellipsis;white-space:nowrap;overflow:hidden;display:block;width:100%;text-align:left}[dir=rtl] .mdc-select__selected-text,.mdc-select__selected-text[dir=rtl]{text-align:right}.mdc-select--invalid:not(.mdc-select--disabled) .mdc-floating-label{color:#b00020;color:var(--mdc-theme-error, #b00020)}.mdc-select--invalid:not(.mdc-select--disabled).mdc-select--focused .mdc-floating-label{color:#b00020;color:var(--mdc-theme-error, #b00020)}.mdc-select--invalid:not(.mdc-select--disabled).mdc-select--invalid+.mdc-select-helper-text--validation-msg{color:#b00020;color:var(--mdc-theme-error, #b00020)}.mdc-select--invalid:not(.mdc-select--disabled) .mdc-select__dropdown-icon{fill:#b00020;fill:var(--mdc-theme-error, #b00020)}.mdc-select--invalid:not(.mdc-select--disabled).mdc-select--focused .mdc-select__dropdown-icon{fill:#b00020;fill:var(--mdc-theme-error, #b00020)}.mdc-select--disabled{cursor:default;pointer-events:none}.mdc-select--with-leading-icon .mdc-select__menu .mdc-deprecated-list-item{padding-left:12px;padding-right:12px}[dir=rtl] .mdc-select--with-leading-icon .mdc-select__menu .mdc-deprecated-list-item,.mdc-select--with-leading-icon .mdc-select__menu .mdc-deprecated-list-item[dir=rtl]{padding-left:12px;padding-right:12px}@media screen and (forced-colors: active),(-ms-high-contrast: active){.mdc-select__menu::before{position:absolute;box-sizing:border-box;width:100%;height:100%;top:0;left:0;border:1px solid transparent;border-radius:inherit;content:"";pointer-events:none}}@media screen and (forced-colors: active)and (forced-colors: active),screen and (-ms-high-contrast: active)and (forced-colors: active){.mdc-select__menu::before{border-color:CanvasText}}.mdc-select__menu .mdc-deprecated-list .mdc-select__icon,.mdc-select__menu .mdc-list .mdc-select__icon{margin-left:0;margin-right:0}[dir=rtl] .mdc-select__menu .mdc-deprecated-list .mdc-select__icon,[dir=rtl] .mdc-select__menu .mdc-list .mdc-select__icon,.mdc-select__menu .mdc-deprecated-list .mdc-select__icon[dir=rtl],.mdc-select__menu .mdc-list .mdc-select__icon[dir=rtl]{margin-left:0;margin-right:0}.mdc-select__menu .mdc-deprecated-list .mdc-deprecated-list-item--selected,.mdc-select__menu .mdc-deprecated-list .mdc-deprecated-list-item--activated,.mdc-select__menu .mdc-list .mdc-deprecated-list-item--selected,.mdc-select__menu .mdc-list .mdc-deprecated-list-item--activated{color:#000;color:var(--mdc-theme-on-surface, #000)}.mdc-select__menu .mdc-deprecated-list .mdc-deprecated-list-item--selected .mdc-deprecated-list-item__graphic,.mdc-select__menu .mdc-deprecated-list .mdc-deprecated-list-item--activated .mdc-deprecated-list-item__graphic,.mdc-select__menu .mdc-list .mdc-deprecated-list-item--selected .mdc-deprecated-list-item__graphic,.mdc-select__menu .mdc-list .mdc-deprecated-list-item--activated .mdc-deprecated-list-item__graphic{color:#000;color:var(--mdc-theme-on-surface, #000)}.mdc-select__menu .mdc-list-item__start{display:inline-flex;align-items:center}.mdc-select__option{padding-left:16px;padding-right:16px}[dir=rtl] .mdc-select__option,.mdc-select__option[dir=rtl]{padding-left:16px;padding-right:16px}.mdc-select__one-line-option.mdc-list-item--with-one-line{height:48px}.mdc-select__two-line-option.mdc-list-item--with-two-lines{height:64px}.mdc-select__two-line-option.mdc-list-item--with-two-lines .mdc-list-item__start{margin-top:20px}.mdc-select__two-line-option.mdc-list-item--with-two-lines .mdc-list-item__primary-text{display:block;margin-top:0;line-height:normal;margin-bottom:-20px}.mdc-select__two-line-option.mdc-list-item--with-two-lines .mdc-list-item__primary-text::before{display:inline-block;width:0;height:28px;content:"";vertical-align:0}.mdc-select__two-line-option.mdc-list-item--with-two-lines .mdc-list-item__primary-text::after{display:inline-block;width:0;height:20px;content:"";vertical-align:-20px}.mdc-select__two-line-option.mdc-list-item--with-two-lines.mdc-list-item--with-trailing-meta .mdc-list-item__end{display:block;margin-top:0;line-height:normal}.mdc-select__two-line-option.mdc-list-item--with-two-lines.mdc-list-item--with-trailing-meta .mdc-list-item__end::before{display:inline-block;width:0;height:36px;content:"";vertical-align:0}.mdc-select__option-with-leading-content{padding-left:0;padding-right:12px}.mdc-select__option-with-leading-content.mdc-list-item{padding-left:0;padding-right:auto}[dir=rtl] .mdc-select__option-with-leading-content.mdc-list-item,.mdc-select__option-with-leading-content.mdc-list-item[dir=rtl]{padding-left:auto;padding-right:0}.mdc-select__option-with-leading-content .mdc-list-item__start{margin-left:12px;margin-right:0}[dir=rtl] .mdc-select__option-with-leading-content .mdc-list-item__start,.mdc-select__option-with-leading-content .mdc-list-item__start[dir=rtl]{margin-left:0;margin-right:12px}.mdc-select__option-with-leading-content .mdc-list-item__start{width:36px;height:24px}[dir=rtl] .mdc-select__option-with-leading-content,.mdc-select__option-with-leading-content[dir=rtl]{padding-left:12px;padding-right:0}.mdc-select__option-with-meta.mdc-list-item{padding-left:auto;padding-right:0}[dir=rtl] .mdc-select__option-with-meta.mdc-list-item,.mdc-select__option-with-meta.mdc-list-item[dir=rtl]{padding-left:0;padding-right:auto}.mdc-select__option-with-meta .mdc-list-item__end{margin-left:12px;margin-right:12px}[dir=rtl] .mdc-select__option-with-meta .mdc-list-item__end,.mdc-select__option-with-meta .mdc-list-item__end[dir=rtl]{margin-left:12px;margin-right:12px}.mdc-select--filled .mdc-select__anchor{height:56px;display:flex;align-items:baseline}.mdc-select--filled .mdc-select__anchor::before{display:inline-block;width:0;height:40px;content:"";vertical-align:0}.mdc-select--filled.mdc-select--no-label .mdc-select__anchor .mdc-select__selected-text::before{content:"​"}.mdc-select--filled.mdc-select--no-label .mdc-select__anchor .mdc-select__selected-text-container{height:100%;display:inline-flex;align-items:center}.mdc-select--filled.mdc-select--no-label .mdc-select__anchor::before{display:none}.mdc-select--filled .mdc-select__anchor{border-top-left-radius:4px;border-top-left-radius:var(--mdc-shape-small, 4px);border-top-right-radius:4px;border-top-right-radius:var(--mdc-shape-small, 4px);border-bottom-right-radius:0;border-bottom-left-radius:0}.mdc-select--filled:not(.mdc-select--disabled) .mdc-select__anchor{background-color:whitesmoke}.mdc-select--filled.mdc-select--disabled .mdc-select__anchor{background-color:#fafafa}.mdc-select--filled:not(.mdc-select--disabled) .mdc-line-ripple::before{border-bottom-color:rgba(0, 0, 0, 0.42)}.mdc-select--filled:not(.mdc-select--disabled):hover .mdc-line-ripple::before{border-bottom-color:rgba(0, 0, 0, 0.87)}.mdc-select--filled:not(.mdc-select--disabled) .mdc-line-ripple::after{border-bottom-color:#6200ee;border-bottom-color:var(--mdc-theme-primary, #6200ee)}.mdc-select--filled.mdc-select--disabled .mdc-line-ripple::before{border-bottom-color:rgba(0, 0, 0, 0.06)}.mdc-select--filled .mdc-floating-label{max-width:calc(100% - 64px)}.mdc-select--filled .mdc-floating-label--float-above{max-width:calc(100% / 0.75 - 64px / 0.75)}.mdc-select--filled .mdc-menu-surface--is-open-below{border-top-left-radius:0px;border-top-right-radius:0px}.mdc-select--filled.mdc-select--focused.mdc-line-ripple::after{transform:scale(1, 2);opacity:1}.mdc-select--filled .mdc-floating-label{left:16px;right:initial}[dir=rtl] .mdc-select--filled .mdc-floating-label,.mdc-select--filled .mdc-floating-label[dir=rtl]{left:initial;right:16px}.mdc-select--filled.mdc-select--with-leading-icon .mdc-floating-label{left:48px;right:initial}[dir=rtl] .mdc-select--filled.mdc-select--with-leading-icon .mdc-floating-label,.mdc-select--filled.mdc-select--with-leading-icon .mdc-floating-label[dir=rtl]{left:initial;right:48px}.mdc-select--filled.mdc-select--with-leading-icon .mdc-floating-label{max-width:calc(100% - 96px)}.mdc-select--filled.mdc-select--with-leading-icon .mdc-floating-label--float-above{max-width:calc(100% / 0.75 - 96px / 0.75)}.mdc-select--invalid:not(.mdc-select--disabled) .mdc-line-ripple::before{border-bottom-color:#b00020;border-bottom-color:var(--mdc-theme-error, #b00020)}.mdc-select--invalid:not(.mdc-select--disabled):hover .mdc-line-ripple::before{border-bottom-color:#b00020;border-bottom-color:var(--mdc-theme-error, #b00020)}.mdc-select--invalid:not(.mdc-select--disabled) .mdc-line-ripple::after{border-bottom-color:#b00020;border-bottom-color:var(--mdc-theme-error, #b00020)}.mdc-select--outlined{border:none}.mdc-select--outlined .mdc-select__anchor{height:56px}.mdc-select--outlined .mdc-select__anchor .mdc-floating-label--float-above{transform:translateY(-37.25px) scale(1)}.mdc-select--outlined .mdc-select__anchor .mdc-floating-label--float-above{font-size:.75rem}.mdc-select--outlined .mdc-select__anchor.mdc-notched-outline--upgraded .mdc-floating-label--float-above,.mdc-select--outlined .mdc-select__anchor .mdc-notched-outline--upgraded .mdc-floating-label--float-above{transform:translateY(-34.75px) scale(0.75)}.mdc-select--outlined .mdc-select__anchor.mdc-notched-outline--upgraded .mdc-floating-label--float-above,.mdc-select--outlined .mdc-select__anchor .mdc-notched-outline--upgraded .mdc-floating-label--float-above{font-size:1rem}.mdc-select--outlined .mdc-select__anchor .mdc-floating-label--shake{animation:mdc-floating-label-shake-float-above-select-outlined-56px 250ms 1}@keyframes mdc-floating-label-shake-float-above-select-outlined-56px{0%{transform:translateX(calc(0 - 0%)) translateY(-34.75px) scale(0.75)}33%{animation-timing-function:cubic-bezier(0.5, 0, 0.701732, 0.495819);transform:translateX(calc(4% - 0%)) translateY(-34.75px) scale(0.75)}66%{animation-timing-function:cubic-bezier(0.302435, 0.381352, 0.55, 0.956352);transform:translateX(calc(-4% - 0%)) translateY(-34.75px) scale(0.75)}100%{transform:translateX(calc(0 - 0%)) translateY(-34.75px) scale(0.75)}}.mdc-select--outlined .mdc-notched-outline .mdc-notched-outline__leading{border-top-left-radius:4px;border-top-left-radius:var(--mdc-shape-small, 4px);border-top-right-radius:0;border-bottom-right-radius:0;border-bottom-left-radius:4px;border-bottom-left-radius:var(--mdc-shape-small, 4px)}[dir=rtl] .mdc-select--outlined .mdc-notched-outline .mdc-notched-outline__leading,.mdc-select--outlined .mdc-notched-outline .mdc-notched-outline__leading[dir=rtl]{border-top-left-radius:0;border-top-right-radius:4px;border-top-right-radius:var(--mdc-shape-small, 4px);border-bottom-right-radius:4px;border-bottom-right-radius:var(--mdc-shape-small, 4px);border-bottom-left-radius:0}@supports(top: max(0%)){.mdc-select--outlined .mdc-notched-outline .mdc-notched-outline__leading{width:max(12px, var(--mdc-shape-small, 4px))}}@supports(top: max(0%)){.mdc-select--outlined .mdc-notched-outline .mdc-notched-outline__notch{max-width:calc(100% - max(12px, var(--mdc-shape-small, 4px)) * 2)}}.mdc-select--outlined .mdc-notched-outline .mdc-notched-outline__trailing{border-top-left-radius:0;border-top-right-radius:4px;border-top-right-radius:var(--mdc-shape-small, 4px);border-bottom-right-radius:4px;border-bottom-right-radius:var(--mdc-shape-small, 4px);border-bottom-left-radius:0}[dir=rtl] .mdc-select--outlined .mdc-notched-outline .mdc-notched-outline__trailing,.mdc-select--outlined .mdc-notched-outline .mdc-notched-outline__trailing[dir=rtl]{border-top-left-radius:4px;border-top-left-radius:var(--mdc-shape-small, 4px);border-top-right-radius:0;border-bottom-right-radius:0;border-bottom-left-radius:4px;border-bottom-left-radius:var(--mdc-shape-small, 4px)}@supports(top: max(0%)){.mdc-select--outlined .mdc-select__anchor{padding-left:max(16px, calc(var(--mdc-shape-small, 4px) + 4px))}}[dir=rtl] .mdc-select--outlined .mdc-select__anchor,.mdc-select--outlined .mdc-select__anchor[dir=rtl]{padding-left:0}@supports(top: max(0%)){[dir=rtl] .mdc-select--outlined .mdc-select__anchor,.mdc-select--outlined .mdc-select__anchor[dir=rtl]{padding-right:max(16px, calc(var(--mdc-shape-small, 4px) + 4px))}}@supports(top: max(0%)){.mdc-select--outlined+.mdc-select-helper-text{margin-left:max(16px, calc(var(--mdc-shape-small, 4px) + 4px))}}[dir=rtl] .mdc-select--outlined+.mdc-select-helper-text,.mdc-select--outlined+.mdc-select-helper-text[dir=rtl]{margin-left:0}@supports(top: max(0%)){[dir=rtl] .mdc-select--outlined+.mdc-select-helper-text,.mdc-select--outlined+.mdc-select-helper-text[dir=rtl]{margin-right:max(16px, calc(var(--mdc-shape-small, 4px) + 4px))}}.mdc-select--outlined:not(.mdc-select--disabled) .mdc-select__anchor{background-color:transparent}.mdc-select--outlined.mdc-select--disabled .mdc-select__anchor{background-color:transparent}.mdc-select--outlined:not(.mdc-select--disabled) .mdc-notched-outline__leading,.mdc-select--outlined:not(.mdc-select--disabled) .mdc-notched-outline__notch,.mdc-select--outlined:not(.mdc-select--disabled) .mdc-notched-outline__trailing{border-color:rgba(0, 0, 0, 0.38)}.mdc-select--outlined:not(.mdc-select--disabled):not(.mdc-select--focused) .mdc-select__anchor:hover .mdc-notched-outline .mdc-notched-outline__leading,.mdc-select--outlined:not(.mdc-select--disabled):not(.mdc-select--focused) .mdc-select__anchor:hover .mdc-notched-outline .mdc-notched-outline__notch,.mdc-select--outlined:not(.mdc-select--disabled):not(.mdc-select--focused) .mdc-select__anchor:hover .mdc-notched-outline .mdc-notched-outline__trailing{border-color:rgba(0, 0, 0, 0.87)}.mdc-select--outlined:not(.mdc-select--disabled).mdc-select--focused .mdc-notched-outline .mdc-notched-outline__leading,.mdc-select--outlined:not(.mdc-select--disabled).mdc-select--focused .mdc-notched-outline .mdc-notched-outline__notch,.mdc-select--outlined:not(.mdc-select--disabled).mdc-select--focused .mdc-notched-outline .mdc-notched-outline__trailing{border-width:2px}.mdc-select--outlined:not(.mdc-select--disabled).mdc-select--focused .mdc-notched-outline .mdc-notched-outline__leading,.mdc-select--outlined:not(.mdc-select--disabled).mdc-select--focused .mdc-notched-outline .mdc-notched-outline__notch,.mdc-select--outlined:not(.mdc-select--disabled).mdc-select--focused .mdc-notched-outline .mdc-notched-outline__trailing{border-color:#6200ee;border-color:var(--mdc-theme-primary, #6200ee)}.mdc-select--outlined.mdc-select--disabled .mdc-notched-outline__leading,.mdc-select--outlined.mdc-select--disabled .mdc-notched-outline__notch,.mdc-select--outlined.mdc-select--disabled .mdc-notched-outline__trailing{border-color:rgba(0, 0, 0, 0.06)}.mdc-select--outlined .mdc-select__anchor :not(.mdc-notched-outline--notched) .mdc-notched-outline__notch{max-width:calc(100% - 60px)}.mdc-select--outlined .mdc-select__anchor{display:flex;align-items:baseline;overflow:visible}.mdc-select--outlined .mdc-select__anchor .mdc-floating-label--shake{animation:mdc-floating-label-shake-float-above-select-outlined 250ms 1}.mdc-select--outlined .mdc-select__anchor .mdc-floating-label--float-above{transform:translateY(-37.25px) scale(1)}.mdc-select--outlined .mdc-select__anchor .mdc-floating-label--float-above{font-size:.75rem}.mdc-select--outlined .mdc-select__anchor.mdc-notched-outline--upgraded .mdc-floating-label--float-above,.mdc-select--outlined .mdc-select__anchor .mdc-notched-outline--upgraded .mdc-floating-label--float-above{transform:translateY(-34.75px) scale(0.75)}.mdc-select--outlined .mdc-select__anchor.mdc-notched-outline--upgraded .mdc-floating-label--float-above,.mdc-select--outlined .mdc-select__anchor .mdc-notched-outline--upgraded .mdc-floating-label--float-above{font-size:1rem}.mdc-select--outlined .mdc-select__anchor .mdc-notched-outline--notched .mdc-notched-outline__notch{padding-top:1px}.mdc-select--outlined .mdc-select__anchor .mdc-select__selected-text::before{content:"​"}.mdc-select--outlined .mdc-select__anchor .mdc-select__selected-text-container{height:100%;display:inline-flex;align-items:center}.mdc-select--outlined .mdc-select__anchor::before{display:none}.mdc-select--outlined .mdc-select__selected-text-container{display:flex;border:none;z-index:1;background-color:transparent}.mdc-select--outlined .mdc-select__icon{z-index:2}.mdc-select--outlined .mdc-floating-label{line-height:1.15rem;left:4px;right:initial}[dir=rtl] .mdc-select--outlined .mdc-floating-label,.mdc-select--outlined .mdc-floating-label[dir=rtl]{left:initial;right:4px}.mdc-select--outlined.mdc-select--focused .mdc-notched-outline--notched .mdc-notched-outline__notch{padding-top:2px}.mdc-select--outlined.mdc-select--invalid:not(.mdc-select--disabled) .mdc-notched-outline__leading,.mdc-select--outlined.mdc-select--invalid:not(.mdc-select--disabled) .mdc-notched-outline__notch,.mdc-select--outlined.mdc-select--invalid:not(.mdc-select--disabled) .mdc-notched-outline__trailing{border-color:#b00020;border-color:var(--mdc-theme-error, #b00020)}.mdc-select--outlined.mdc-select--invalid:not(.mdc-select--disabled):not(.mdc-select--focused) .mdc-select__anchor:hover .mdc-notched-outline .mdc-notched-outline__leading,.mdc-select--outlined.mdc-select--invalid:not(.mdc-select--disabled):not(.mdc-select--focused) .mdc-select__anchor:hover .mdc-notched-outline .mdc-notched-outline__notch,.mdc-select--outlined.mdc-select--invalid:not(.mdc-select--disabled):not(.mdc-select--focused) .mdc-select__anchor:hover .mdc-notched-outline .mdc-notched-outline__trailing{border-color:#b00020;border-color:var(--mdc-theme-error, #b00020)}.mdc-select--outlined.mdc-select--invalid:not(.mdc-select--disabled).mdc-select--focused .mdc-notched-outline .mdc-notched-outline__leading,.mdc-select--outlined.mdc-select--invalid:not(.mdc-select--disabled).mdc-select--focused .mdc-notched-outline .mdc-notched-outline__notch,.mdc-select--outlined.mdc-select--invalid:not(.mdc-select--disabled).mdc-select--focused .mdc-notched-outline .mdc-notched-outline__trailing{border-width:2px}.mdc-select--outlined.mdc-select--invalid:not(.mdc-select--disabled).mdc-select--focused .mdc-notched-outline .mdc-notched-outline__leading,.mdc-select--outlined.mdc-select--invalid:not(.mdc-select--disabled).mdc-select--focused .mdc-notched-outline .mdc-notched-outline__notch,.mdc-select--outlined.mdc-select--invalid:not(.mdc-select--disabled).mdc-select--focused .mdc-notched-outline .mdc-notched-outline__trailing{border-color:#b00020;border-color:var(--mdc-theme-error, #b00020)}.mdc-select--outlined.mdc-select--with-leading-icon .mdc-floating-label{left:36px;right:initial}[dir=rtl] .mdc-select--outlined.mdc-select--with-leading-icon .mdc-floating-label,.mdc-select--outlined.mdc-select--with-leading-icon .mdc-floating-label[dir=rtl]{left:initial;right:36px}.mdc-select--outlined.mdc-select--with-leading-icon .mdc-floating-label--float-above{transform:translateY(-37.25px) translateX(-32px) scale(1)}[dir=rtl] .mdc-select--outlined.mdc-select--with-leading-icon .mdc-floating-label--float-above,.mdc-select--outlined.mdc-select--with-leading-icon .mdc-floating-label--float-above[dir=rtl]{transform:translateY(-37.25px) translateX(32px) scale(1)}.mdc-select--outlined.mdc-select--with-leading-icon .mdc-floating-label--float-above{font-size:.75rem}.mdc-select--outlined.mdc-select--with-leading-icon.mdc-notched-outline--upgraded .mdc-floating-label--float-above,.mdc-select--outlined.mdc-select--with-leading-icon .mdc-notched-outline--upgraded .mdc-floating-label--float-above{transform:translateY(-34.75px) translateX(-32px) scale(0.75)}[dir=rtl] .mdc-select--outlined.mdc-select--with-leading-icon.mdc-notched-outline--upgraded .mdc-floating-label--float-above,[dir=rtl] .mdc-select--outlined.mdc-select--with-leading-icon .mdc-notched-outline--upgraded .mdc-floating-label--float-above,.mdc-select--outlined.mdc-select--with-leading-icon.mdc-notched-outline--upgraded .mdc-floating-label--float-above[dir=rtl],.mdc-select--outlined.mdc-select--with-leading-icon .mdc-notched-outline--upgraded .mdc-floating-label--float-above[dir=rtl]{transform:translateY(-34.75px) translateX(32px) scale(0.75)}.mdc-select--outlined.mdc-select--with-leading-icon.mdc-notched-outline--upgraded .mdc-floating-label--float-above,.mdc-select--outlined.mdc-select--with-leading-icon .mdc-notched-outline--upgraded .mdc-floating-label--float-above{font-size:1rem}.mdc-select--outlined.mdc-select--with-leading-icon .mdc-floating-label--shake{animation:mdc-floating-label-shake-float-above-select-outlined-leading-icon-56px 250ms 1}@keyframes mdc-floating-label-shake-float-above-select-outlined-leading-icon-56px{0%{transform:translateX(calc(0 - 32px)) translateY(-34.75px) scale(0.75)}33%{animation-timing-function:cubic-bezier(0.5, 0, 0.701732, 0.495819);transform:translateX(calc(4% - 32px)) translateY(-34.75px) scale(0.75)}66%{animation-timing-function:cubic-bezier(0.302435, 0.381352, 0.55, 0.956352);transform:translateX(calc(-4% - 32px)) translateY(-34.75px) scale(0.75)}100%{transform:translateX(calc(0 - 32px)) translateY(-34.75px) scale(0.75)}}[dir=rtl] .mdc-select--outlined.mdc-select--with-leading-icon .mdc-floating-label--shake,.mdc-select--outlined.mdc-select--with-leading-icon[dir=rtl] .mdc-floating-label--shake{animation:mdc-floating-label-shake-float-above-select-outlined-leading-icon-56px 250ms 1}@keyframes mdc-floating-label-shake-float-above-select-outlined-leading-icon-56px-rtl{0%{transform:translateX(calc(0 - -32px)) translateY(-34.75px) scale(0.75)}33%{animation-timing-function:cubic-bezier(0.5, 0, 0.701732, 0.495819);transform:translateX(calc(4% - -32px)) translateY(-34.75px) scale(0.75)}66%{animation-timing-function:cubic-bezier(0.302435, 0.381352, 0.55, 0.956352);transform:translateX(calc(-4% - -32px)) translateY(-34.75px) scale(0.75)}100%{transform:translateX(calc(0 - -32px)) translateY(-34.75px) scale(0.75)}}.mdc-select--outlined.mdc-select--with-leading-icon .mdc-select__anchor :not(.mdc-notched-outline--notched) .mdc-notched-outline__notch{max-width:calc(100% - 96px)}.mdc-select--outlined .mdc-menu-surface{margin-bottom:8px}.mdc-select--outlined.mdc-select--no-label .mdc-menu-surface,.mdc-select--outlined .mdc-menu-surface--is-open-below{margin-bottom:0}.mdc-select__anchor{--mdc-ripple-fg-size: 0;--mdc-ripple-left: 0;--mdc-ripple-top: 0;--mdc-ripple-fg-scale: 1;--mdc-ripple-fg-translate-end: 0;--mdc-ripple-fg-translate-start: 0;-webkit-tap-highlight-color:rgba(0,0,0,0);will-change:transform,opacity}.mdc-select__anchor .mdc-select__ripple::before,.mdc-select__anchor .mdc-select__ripple::after{position:absolute;border-radius:50%;opacity:0;pointer-events:none;content:""}.mdc-select__anchor .mdc-select__ripple::before{transition:opacity 15ms linear,background-color 15ms linear;z-index:1;z-index:var(--mdc-ripple-z-index, 1)}.mdc-select__anchor .mdc-select__ripple::after{z-index:0;z-index:var(--mdc-ripple-z-index, 0)}.mdc-select__anchor.mdc-ripple-upgraded .mdc-select__ripple::before{transform:scale(var(--mdc-ripple-fg-scale, 1))}.mdc-select__anchor.mdc-ripple-upgraded .mdc-select__ripple::after{top:0;left:0;transform:scale(0);transform-origin:center center}.mdc-select__anchor.mdc-ripple-upgraded--unbounded .mdc-select__ripple::after{top:var(--mdc-ripple-top, 0);left:var(--mdc-ripple-left, 0)}.mdc-select__anchor.mdc-ripple-upgraded--foreground-activation .mdc-select__ripple::after{animation:mdc-ripple-fg-radius-in 225ms forwards,mdc-ripple-fg-opacity-in 75ms forwards}.mdc-select__anchor.mdc-ripple-upgraded--foreground-deactivation .mdc-select__ripple::after{animation:mdc-ripple-fg-opacity-out 150ms;transform:translate(var(--mdc-ripple-fg-translate-end, 0)) scale(var(--mdc-ripple-fg-scale, 1))}.mdc-select__anchor .mdc-select__ripple::before,.mdc-select__anchor .mdc-select__ripple::after{top:calc(50% - 100%);left:calc(50% - 100%);width:200%;height:200%}.mdc-select__anchor.mdc-ripple-upgraded .mdc-select__ripple::after{width:var(--mdc-ripple-fg-size, 100%);height:var(--mdc-ripple-fg-size, 100%)}.mdc-select__anchor .mdc-select__ripple::before,.mdc-select__anchor .mdc-select__ripple::after{background-color:rgba(0, 0, 0, 0.87);background-color:var(--mdc-ripple-color, rgba(0, 0, 0, 0.87))}.mdc-select__anchor:hover .mdc-select__ripple::before,.mdc-select__anchor.mdc-ripple-surface--hover .mdc-select__ripple::before{opacity:0.04;opacity:var(--mdc-ripple-hover-opacity, 0.04)}.mdc-select__anchor.mdc-ripple-upgraded--background-focused .mdc-select__ripple::before,.mdc-select__anchor:not(.mdc-ripple-upgraded):focus .mdc-select__ripple::before{transition-duration:75ms;opacity:0.12;opacity:var(--mdc-ripple-focus-opacity, 0.12)}.mdc-select__anchor .mdc-select__ripple{position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none}.mdc-select__menu .mdc-deprecated-list .mdc-deprecated-list-item--selected .mdc-deprecated-list-item__ripple::before,.mdc-select__menu .mdc-deprecated-list .mdc-deprecated-list-item--selected .mdc-deprecated-list-item__ripple::after{background-color:#000;background-color:var(--mdc-ripple-color, var(--mdc-theme-on-surface, #000))}.mdc-select__menu .mdc-deprecated-list .mdc-deprecated-list-item--selected:hover .mdc-deprecated-list-item__ripple::before,.mdc-select__menu .mdc-deprecated-list .mdc-deprecated-list-item--selected.mdc-ripple-surface--hover .mdc-deprecated-list-item__ripple::before{opacity:0.04;opacity:var(--mdc-ripple-hover-opacity, 0.04)}.mdc-select__menu .mdc-deprecated-list .mdc-deprecated-list-item--selected.mdc-ripple-upgraded--background-focused .mdc-deprecated-list-item__ripple::before,.mdc-select__menu .mdc-deprecated-list .mdc-deprecated-list-item--selected:not(.mdc-ripple-upgraded):focus .mdc-deprecated-list-item__ripple::before{transition-duration:75ms;opacity:0.12;opacity:var(--mdc-ripple-focus-opacity, 0.12)}.mdc-select__menu .mdc-deprecated-list .mdc-deprecated-list-item--selected:not(.mdc-ripple-upgraded) .mdc-deprecated-list-item__ripple::after{transition:opacity 150ms linear}.mdc-select__menu .mdc-deprecated-list .mdc-deprecated-list-item--selected:not(.mdc-ripple-upgraded):active .mdc-deprecated-list-item__ripple::after{transition-duration:75ms;opacity:0.12;opacity:var(--mdc-ripple-press-opacity, 0.12)}.mdc-select__menu .mdc-deprecated-list .mdc-deprecated-list-item--selected.mdc-ripple-upgraded{--mdc-ripple-fg-opacity:var(--mdc-ripple-press-opacity, 0.12)}.mdc-select__menu .mdc-deprecated-list .mdc-deprecated-list-item--selected .mdc-list-item__ripple::before,.mdc-select__menu .mdc-deprecated-list .mdc-deprecated-list-item--selected .mdc-list-item__ripple::after{background-color:#000;background-color:var(--mdc-ripple-color, var(--mdc-theme-on-surface, #000))}.mdc-select__menu .mdc-deprecated-list .mdc-deprecated-list-item--selected:hover .mdc-list-item__ripple::before,.mdc-select__menu .mdc-deprecated-list .mdc-deprecated-list-item--selected.mdc-ripple-surface--hover .mdc-list-item__ripple::before{opacity:0.04;opacity:var(--mdc-ripple-hover-opacity, 0.04)}.mdc-select__menu .mdc-deprecated-list .mdc-deprecated-list-item--selected.mdc-ripple-upgraded--background-focused .mdc-list-item__ripple::before,.mdc-select__menu .mdc-deprecated-list .mdc-deprecated-list-item--selected:not(.mdc-ripple-upgraded):focus .mdc-list-item__ripple::before{transition-duration:75ms;opacity:0.12;opacity:var(--mdc-ripple-focus-opacity, 0.12)}.mdc-select__menu .mdc-deprecated-list .mdc-deprecated-list-item--selected:not(.mdc-ripple-upgraded) .mdc-list-item__ripple::after{transition:opacity 150ms linear}.mdc-select__menu .mdc-deprecated-list .mdc-deprecated-list-item--selected:not(.mdc-ripple-upgraded):active .mdc-list-item__ripple::after{transition-duration:75ms;opacity:0.12;opacity:var(--mdc-ripple-press-opacity, 0.12)}.mdc-select__menu .mdc-deprecated-list .mdc-deprecated-list-item--selected.mdc-ripple-upgraded{--mdc-ripple-fg-opacity:var(--mdc-ripple-press-opacity, 0.12)}.mdc-select-helper-text{margin:0;margin-left:16px;margin-right:16px;-moz-osx-font-smoothing:grayscale;-webkit-font-smoothing:antialiased;font-family:Roboto, sans-serif;font-family:var(--mdc-typography-caption-font-family, var(--mdc-typography-font-family, Roboto, sans-serif));font-size:0.75rem;font-size:var(--mdc-typography-caption-font-size, 0.75rem);line-height:1.25rem;line-height:var(--mdc-typography-caption-line-height, 1.25rem);font-weight:400;font-weight:var(--mdc-typography-caption-font-weight, 400);letter-spacing:0.0333333333em;letter-spacing:var(--mdc-typography-caption-letter-spacing, 0.0333333333em);text-decoration:inherit;text-decoration:var(--mdc-typography-caption-text-decoration, inherit);text-transform:inherit;text-transform:var(--mdc-typography-caption-text-transform, inherit);display:block;margin-top:0;line-height:normal}[dir=rtl] .mdc-select-helper-text,.mdc-select-helper-text[dir=rtl]{margin-left:16px;margin-right:16px}.mdc-select-helper-text::before{display:inline-block;width:0;height:16px;content:"";vertical-align:0}.mdc-select-helper-text--validation-msg{opacity:0;transition:opacity 180ms cubic-bezier(0.4, 0, 0.2, 1)}.mdc-select--invalid+.mdc-select-helper-text--validation-msg,.mdc-select-helper-text--validation-msg-persistent{opacity:1}.mdc-select--with-leading-icon .mdc-select__icon{display:inline-block;box-sizing:border-box;border:none;text-decoration:none;cursor:pointer;user-select:none;flex-shrink:0;align-self:center;background-color:transparent;fill:currentColor}.mdc-select--with-leading-icon .mdc-select__icon{margin-left:12px;margin-right:12px}[dir=rtl] .mdc-select--with-leading-icon .mdc-select__icon,.mdc-select--with-leading-icon .mdc-select__icon[dir=rtl]{margin-left:12px;margin-right:12px}.mdc-select__icon:not([tabindex]),.mdc-select__icon[tabindex="-1"]{cursor:default;pointer-events:none}.material-icons{font-family:var(--mdc-icon-font, "Material Icons");font-weight:normal;font-style:normal;font-size:var(--mdc-icon-size, 24px);line-height:1;letter-spacing:normal;text-transform:none;display:inline-block;white-space:nowrap;word-wrap:normal;direction:ltr;-webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility;-moz-osx-font-smoothing:grayscale;font-feature-settings:"liga"}:host{display:inline-block;vertical-align:top;outline:none}.mdc-select{width:100%}[hidden]{display:none}.mdc-select__icon{z-index:2}.mdc-select--with-leading-icon{--mdc-list-item-graphic-margin: calc( 48px - var(--mdc-list-item-graphic-size, 24px) - var(--mdc-list-side-padding, 16px) )}.mdc-select .mdc-select__anchor .mdc-select__selected-text{overflow:hidden}.mdc-select .mdc-select__anchor *{display:inline-flex}.mdc-select .mdc-select__anchor .mdc-floating-label{display:inline-block}mwc-notched-outline{--mdc-notched-outline-border-color: var( --mdc-select-outlined-idle-border-color, rgba(0, 0, 0, 0.38) );--mdc-notched-outline-notch-offset: 1px}:host(:not([disabled]):hover) .mdc-select:not(.mdc-select--invalid):not(.mdc-select--focused) mwc-notched-outline{--mdc-notched-outline-border-color: var( --mdc-select-outlined-hover-border-color, rgba(0, 0, 0, 0.87) )}:host(:not([disabled])) .mdc-select:not(.mdc-select--disabled) .mdc-select__selected-text{color:rgba(0, 0, 0, 0.87);color:var(--mdc-select-ink-color, rgba(0, 0, 0, 0.87))}:host(:not([disabled])) .mdc-select:not(.mdc-select--disabled) .mdc-line-ripple::before{border-bottom-color:rgba(0, 0, 0, 0.42);border-bottom-color:var(--mdc-select-idle-line-color, rgba(0, 0, 0, 0.42))}:host(:not([disabled])) .mdc-select:not(.mdc-select--disabled):hover .mdc-line-ripple::before{border-bottom-color:rgba(0, 0, 0, 0.87);border-bottom-color:var(--mdc-select-hover-line-color, rgba(0, 0, 0, 0.87))}:host(:not([disabled])) .mdc-select:not(.mdc-select--outlined):not(.mdc-select--disabled) .mdc-select__anchor{background-color:whitesmoke;background-color:var(--mdc-select-fill-color, whitesmoke)}:host(:not([disabled])) .mdc-select.mdc-select--invalid .mdc-select__dropdown-icon{fill:var(--mdc-select-error-dropdown-icon-color, var(--mdc-select-error-color, var(--mdc-theme-error, #b00020)))}:host(:not([disabled])) .mdc-select.mdc-select--invalid .mdc-floating-label,:host(:not([disabled])) .mdc-select.mdc-select--invalid .mdc-floating-label::after{color:var(--mdc-select-error-color, var(--mdc-theme-error, #b00020))}:host(:not([disabled])) .mdc-select.mdc-select--invalid mwc-notched-outline{--mdc-notched-outline-border-color: var(--mdc-select-error-color, var(--mdc-theme-error, #b00020))}.mdc-select__menu--invalid{--mdc-theme-primary: var(--mdc-select-error-color, var(--mdc-theme-error, #b00020))}:host(:not([disabled])) .mdc-select:not(.mdc-select--invalid):not(.mdc-select--focused) .mdc-floating-label,:host(:not([disabled])) .mdc-select:not(.mdc-select--invalid):not(.mdc-select--focused) .mdc-floating-label::after{color:rgba(0, 0, 0, 0.6);color:var(--mdc-select-label-ink-color, rgba(0, 0, 0, 0.6))}:host(:not([disabled])) .mdc-select:not(.mdc-select--invalid):not(.mdc-select--focused) .mdc-select__dropdown-icon{fill:rgba(0, 0, 0, 0.54);fill:var(--mdc-select-dropdown-icon-color, rgba(0, 0, 0, 0.54))}:host(:not([disabled])) .mdc-select.mdc-select--focused mwc-notched-outline{--mdc-notched-outline-stroke-width: 2px;--mdc-notched-outline-notch-offset: 2px}:host(:not([disabled])) .mdc-select.mdc-select--focused:not(.mdc-select--invalid) mwc-notched-outline{--mdc-notched-outline-border-color: var( --mdc-select-focused-label-color, var(--mdc-theme-primary, rgba(98, 0, 238, 0.87)) )}:host(:not([disabled])) .mdc-select.mdc-select--focused:not(.mdc-select--invalid) .mdc-select__dropdown-icon{fill:rgba(98,0,238,.87);fill:var(--mdc-select-focused-dropdown-icon-color, var(--mdc-theme-primary, rgba(98, 0, 238, 0.87)))}:host(:not([disabled])) .mdc-select.mdc-select--focused:not(.mdc-select--invalid) .mdc-floating-label{color:#6200ee;color:var(--mdc-theme-primary, #6200ee)}:host(:not([disabled])) .mdc-select.mdc-select--focused:not(.mdc-select--invalid) .mdc-floating-label::after{color:#6200ee;color:var(--mdc-theme-primary, #6200ee)}:host(:not([disabled])) .mdc-select-helper-text:not(.mdc-select-helper-text--validation-msg){color:var(--mdc-select-label-ink-color, rgba(0, 0, 0, 0.6))}:host([disabled]){pointer-events:none}:host([disabled]) .mdc-select:not(.mdc-select--outlined).mdc-select--disabled .mdc-select__anchor{background-color:#fafafa;background-color:var(--mdc-select-disabled-fill-color, #fafafa)}:host([disabled]) .mdc-select.mdc-select--outlined mwc-notched-outline{--mdc-notched-outline-border-color: var( --mdc-select-outlined-disabled-border-color, rgba(0, 0, 0, 0.06) )}:host([disabled]) .mdc-select .mdc-select__dropdown-icon{fill:rgba(0, 0, 0, 0.38);fill:var(--mdc-select-disabled-dropdown-icon-color, rgba(0, 0, 0, 0.38))}:host([disabled]) .mdc-select:not(.mdc-select--invalid):not(.mdc-select--focused) .mdc-floating-label,:host([disabled]) .mdc-select:not(.mdc-select--invalid):not(.mdc-select--focused) .mdc-floating-label::after{color:rgba(0, 0, 0, 0.38);color:var(--mdc-select-disabled-ink-color, rgba(0, 0, 0, 0.38))}:host([disabled]) .mdc-select-helper-text{color:rgba(0, 0, 0, 0.38);color:var(--mdc-select-disabled-ink-color, rgba(0, 0, 0, 0.38))}:host([disabled]) .mdc-select__selected-text{color:rgba(0, 0, 0, 0.38);color:var(--mdc-select-disabled-ink-color, rgba(0, 0, 0, 0.38))}`
/**
     * @license
     * Copyright 2021 Google LLC
     * SPDX-LIcense-Identifier: Apache-2.0
     */,Nm=$l`@keyframes mdc-ripple-fg-radius-in{from{animation-timing-function:cubic-bezier(0.4, 0, 0.2, 1);transform:translate(var(--mdc-ripple-fg-translate-start, 0)) scale(1)}to{transform:translate(var(--mdc-ripple-fg-translate-end, 0)) scale(var(--mdc-ripple-fg-scale, 1))}}@keyframes mdc-ripple-fg-opacity-in{from{animation-timing-function:linear;opacity:0}to{opacity:var(--mdc-ripple-fg-opacity, 0)}}@keyframes mdc-ripple-fg-opacity-out{from{animation-timing-function:linear;opacity:var(--mdc-ripple-fg-opacity, 0)}to{opacity:0}}:host{display:block}.mdc-deprecated-list{-moz-osx-font-smoothing:grayscale;-webkit-font-smoothing:antialiased;font-family:Roboto, sans-serif;font-family:var(--mdc-typography-subtitle1-font-family, var(--mdc-typography-font-family, Roboto, sans-serif));font-size:1rem;font-size:var(--mdc-typography-subtitle1-font-size, 1rem);line-height:1.75rem;line-height:var(--mdc-typography-subtitle1-line-height, 1.75rem);font-weight:400;font-weight:var(--mdc-typography-subtitle1-font-weight, 400);letter-spacing:0.009375em;letter-spacing:var(--mdc-typography-subtitle1-letter-spacing, 0.009375em);text-decoration:inherit;text-decoration:var(--mdc-typography-subtitle1-text-decoration, inherit);text-transform:inherit;text-transform:var(--mdc-typography-subtitle1-text-transform, inherit);line-height:1.5rem;margin:0;padding:8px 0;list-style-type:none;color:rgba(0, 0, 0, 0.87);color:var(--mdc-theme-text-primary-on-background, rgba(0, 0, 0, 0.87));padding:var(--mdc-list-vertical-padding, 8px) 0}.mdc-deprecated-list:focus{outline:none}.mdc-deprecated-list-item{height:48px}.mdc-deprecated-list--dense{padding-top:4px;padding-bottom:4px;font-size:.812rem}.mdc-deprecated-list ::slotted([divider]){height:0;margin:0;border:none;border-bottom-width:1px;border-bottom-style:solid;border-bottom-color:rgba(0, 0, 0, 0.12)}.mdc-deprecated-list ::slotted([divider][padded]){margin:0 var(--mdc-list-side-padding, 16px)}.mdc-deprecated-list ::slotted([divider][inset]){margin-left:var(--mdc-list-inset-margin, 72px);margin-right:0;width:calc( 100% - var(--mdc-list-inset-margin, 72px) )}[dir=rtl] .mdc-deprecated-list ::slotted([divider][inset]),.mdc-deprecated-list ::slotted([divider][inset][dir=rtl]){margin-left:0;margin-right:var(--mdc-list-inset-margin, 72px)}.mdc-deprecated-list ::slotted([divider][inset][padded]){width:calc( 100% - var(--mdc-list-inset-margin, 72px) - var(--mdc-list-side-padding, 16px) )}.mdc-deprecated-list--dense ::slotted([mwc-list-item]){height:40px}.mdc-deprecated-list--dense ::slotted([mwc-list]){--mdc-list-item-graphic-size: 20px}.mdc-deprecated-list--two-line.mdc-deprecated-list--dense ::slotted([mwc-list-item]),.mdc-deprecated-list--avatar-list.mdc-deprecated-list--dense ::slotted([mwc-list-item]){height:60px}.mdc-deprecated-list--avatar-list.mdc-deprecated-list--dense ::slotted([mwc-list]){--mdc-list-item-graphic-size: 36px}:host([noninteractive]){pointer-events:none;cursor:default}.mdc-deprecated-list--dense ::slotted(.mdc-deprecated-list-item__primary-text){display:block;margin-top:0;line-height:normal;margin-bottom:-20px}.mdc-deprecated-list--dense ::slotted(.mdc-deprecated-list-item__primary-text)::before{display:inline-block;width:0;height:24px;content:"";vertical-align:0}.mdc-deprecated-list--dense ::slotted(.mdc-deprecated-list-item__primary-text)::after{display:inline-block;width:0;height:20px;content:"";vertical-align:-20px}`
/**
     * @license
     * Copyright 2021 Google LLC
     * SPDX-LIcense-Identifier: Apache-2.0
     */,Dm=$l`:host{cursor:pointer;user-select:none;-webkit-tap-highlight-color:transparent;height:48px;display:flex;position:relative;align-items:center;justify-content:flex-start;overflow:hidden;padding:0;padding-left:var(--mdc-list-side-padding, 16px);padding-right:var(--mdc-list-side-padding, 16px);outline:none;height:48px;color:rgba(0,0,0,.87);color:var(--mdc-theme-text-primary-on-background, rgba(0, 0, 0, 0.87))}:host:focus{outline:none}:host([activated]){color:#6200ee;color:var(--mdc-theme-primary, #6200ee);--mdc-ripple-color: var( --mdc-theme-primary, #6200ee )}:host([activated]) .mdc-deprecated-list-item__graphic{color:#6200ee;color:var(--mdc-theme-primary, #6200ee)}:host([activated]) .fake-activated-ripple::before{position:absolute;display:block;top:0;bottom:0;left:0;right:0;width:100%;height:100%;pointer-events:none;z-index:1;content:"";opacity:0.12;opacity:var(--mdc-ripple-activated-opacity, 0.12);background-color:#6200ee;background-color:var(--mdc-ripple-color, var(--mdc-theme-primary, #6200ee))}.mdc-deprecated-list-item__graphic{flex-shrink:0;align-items:center;justify-content:center;fill:currentColor;display:inline-flex}.mdc-deprecated-list-item__graphic ::slotted(*){flex-shrink:0;align-items:center;justify-content:center;fill:currentColor;width:100%;height:100%;text-align:center}.mdc-deprecated-list-item__meta{width:var(--mdc-list-item-meta-size, 24px);height:var(--mdc-list-item-meta-size, 24px);margin-left:auto;margin-right:0;color:rgba(0, 0, 0, 0.38);color:var(--mdc-theme-text-hint-on-background, rgba(0, 0, 0, 0.38))}.mdc-deprecated-list-item__meta.multi{width:auto}.mdc-deprecated-list-item__meta ::slotted(*){width:var(--mdc-list-item-meta-size, 24px);line-height:var(--mdc-list-item-meta-size, 24px)}.mdc-deprecated-list-item__meta ::slotted(.material-icons),.mdc-deprecated-list-item__meta ::slotted(mwc-icon){line-height:var(--mdc-list-item-meta-size, 24px) !important}.mdc-deprecated-list-item__meta ::slotted(:not(.material-icons):not(mwc-icon)){-moz-osx-font-smoothing:grayscale;-webkit-font-smoothing:antialiased;font-family:Roboto, sans-serif;font-family:var(--mdc-typography-caption-font-family, var(--mdc-typography-font-family, Roboto, sans-serif));font-size:0.75rem;font-size:var(--mdc-typography-caption-font-size, 0.75rem);line-height:1.25rem;line-height:var(--mdc-typography-caption-line-height, 1.25rem);font-weight:400;font-weight:var(--mdc-typography-caption-font-weight, 400);letter-spacing:0.0333333333em;letter-spacing:var(--mdc-typography-caption-letter-spacing, 0.0333333333em);text-decoration:inherit;text-decoration:var(--mdc-typography-caption-text-decoration, inherit);text-transform:inherit;text-transform:var(--mdc-typography-caption-text-transform, inherit)}[dir=rtl] .mdc-deprecated-list-item__meta,.mdc-deprecated-list-item__meta[dir=rtl]{margin-left:0;margin-right:auto}.mdc-deprecated-list-item__meta ::slotted(*){width:100%;height:100%}.mdc-deprecated-list-item__text{text-overflow:ellipsis;white-space:nowrap;overflow:hidden}.mdc-deprecated-list-item__text ::slotted([for]),.mdc-deprecated-list-item__text[for]{pointer-events:none}.mdc-deprecated-list-item__primary-text{text-overflow:ellipsis;white-space:nowrap;overflow:hidden;display:block;margin-top:0;line-height:normal;margin-bottom:-20px;display:block}.mdc-deprecated-list-item__primary-text::before{display:inline-block;width:0;height:32px;content:"";vertical-align:0}.mdc-deprecated-list-item__primary-text::after{display:inline-block;width:0;height:20px;content:"";vertical-align:-20px}.mdc-deprecated-list-item__secondary-text{-moz-osx-font-smoothing:grayscale;-webkit-font-smoothing:antialiased;font-family:Roboto, sans-serif;font-family:var(--mdc-typography-body2-font-family, var(--mdc-typography-font-family, Roboto, sans-serif));font-size:0.875rem;font-size:var(--mdc-typography-body2-font-size, 0.875rem);line-height:1.25rem;line-height:var(--mdc-typography-body2-line-height, 1.25rem);font-weight:400;font-weight:var(--mdc-typography-body2-font-weight, 400);letter-spacing:0.0178571429em;letter-spacing:var(--mdc-typography-body2-letter-spacing, 0.0178571429em);text-decoration:inherit;text-decoration:var(--mdc-typography-body2-text-decoration, inherit);text-transform:inherit;text-transform:var(--mdc-typography-body2-text-transform, inherit);text-overflow:ellipsis;white-space:nowrap;overflow:hidden;display:block;margin-top:0;line-height:normal;display:block}.mdc-deprecated-list-item__secondary-text::before{display:inline-block;width:0;height:20px;content:"";vertical-align:0}.mdc-deprecated-list--dense .mdc-deprecated-list-item__secondary-text{font-size:inherit}* ::slotted(a),a{color:inherit;text-decoration:none}:host([twoline]){height:72px}:host([twoline]) .mdc-deprecated-list-item__text{align-self:flex-start}:host([disabled]),:host([noninteractive]){cursor:default;pointer-events:none}:host([disabled]) .mdc-deprecated-list-item__text ::slotted(*){opacity:.38}:host([disabled]) .mdc-deprecated-list-item__text ::slotted(*),:host([disabled]) .mdc-deprecated-list-item__primary-text ::slotted(*),:host([disabled]) .mdc-deprecated-list-item__secondary-text ::slotted(*){color:#000;color:var(--mdc-theme-on-surface, #000)}.mdc-deprecated-list-item__secondary-text ::slotted(*){color:rgba(0, 0, 0, 0.54);color:var(--mdc-theme-text-secondary-on-background, rgba(0, 0, 0, 0.54))}.mdc-deprecated-list-item__graphic ::slotted(*){background-color:transparent;color:rgba(0, 0, 0, 0.38);color:var(--mdc-theme-text-icon-on-background, rgba(0, 0, 0, 0.38))}.mdc-deprecated-list-group__subheader ::slotted(*){color:rgba(0, 0, 0, 0.87);color:var(--mdc-theme-text-primary-on-background, rgba(0, 0, 0, 0.87))}:host([graphic=avatar]) .mdc-deprecated-list-item__graphic{width:var(--mdc-list-item-graphic-size, 40px);height:var(--mdc-list-item-graphic-size, 40px)}:host([graphic=avatar]) .mdc-deprecated-list-item__graphic.multi{width:auto}:host([graphic=avatar]) .mdc-deprecated-list-item__graphic ::slotted(*){width:var(--mdc-list-item-graphic-size, 40px);line-height:var(--mdc-list-item-graphic-size, 40px)}:host([graphic=avatar]) .mdc-deprecated-list-item__graphic ::slotted(.material-icons),:host([graphic=avatar]) .mdc-deprecated-list-item__graphic ::slotted(mwc-icon){line-height:var(--mdc-list-item-graphic-size, 40px) !important}:host([graphic=avatar]) .mdc-deprecated-list-item__graphic ::slotted(*){border-radius:50%}:host([graphic=avatar]) .mdc-deprecated-list-item__graphic,:host([graphic=medium]) .mdc-deprecated-list-item__graphic,:host([graphic=large]) .mdc-deprecated-list-item__graphic,:host([graphic=control]) .mdc-deprecated-list-item__graphic{margin-left:0;margin-right:var(--mdc-list-item-graphic-margin, 16px)}[dir=rtl] :host([graphic=avatar]) .mdc-deprecated-list-item__graphic,[dir=rtl] :host([graphic=medium]) .mdc-deprecated-list-item__graphic,[dir=rtl] :host([graphic=large]) .mdc-deprecated-list-item__graphic,[dir=rtl] :host([graphic=control]) .mdc-deprecated-list-item__graphic,:host([graphic=avatar]) .mdc-deprecated-list-item__graphic[dir=rtl],:host([graphic=medium]) .mdc-deprecated-list-item__graphic[dir=rtl],:host([graphic=large]) .mdc-deprecated-list-item__graphic[dir=rtl],:host([graphic=control]) .mdc-deprecated-list-item__graphic[dir=rtl]{margin-left:var(--mdc-list-item-graphic-margin, 16px);margin-right:0}:host([graphic=icon]) .mdc-deprecated-list-item__graphic{width:var(--mdc-list-item-graphic-size, 24px);height:var(--mdc-list-item-graphic-size, 24px);margin-left:0;margin-right:var(--mdc-list-item-graphic-margin, 32px)}:host([graphic=icon]) .mdc-deprecated-list-item__graphic.multi{width:auto}:host([graphic=icon]) .mdc-deprecated-list-item__graphic ::slotted(*){width:var(--mdc-list-item-graphic-size, 24px);line-height:var(--mdc-list-item-graphic-size, 24px)}:host([graphic=icon]) .mdc-deprecated-list-item__graphic ::slotted(.material-icons),:host([graphic=icon]) .mdc-deprecated-list-item__graphic ::slotted(mwc-icon){line-height:var(--mdc-list-item-graphic-size, 24px) !important}[dir=rtl] :host([graphic=icon]) .mdc-deprecated-list-item__graphic,:host([graphic=icon]) .mdc-deprecated-list-item__graphic[dir=rtl]{margin-left:var(--mdc-list-item-graphic-margin, 32px);margin-right:0}:host([graphic=avatar]:not([twoLine])),:host([graphic=icon]:not([twoLine])){height:56px}:host([graphic=medium]:not([twoLine])),:host([graphic=large]:not([twoLine])){height:72px}:host([graphic=medium]) .mdc-deprecated-list-item__graphic,:host([graphic=large]) .mdc-deprecated-list-item__graphic{width:var(--mdc-list-item-graphic-size, 56px);height:var(--mdc-list-item-graphic-size, 56px)}:host([graphic=medium]) .mdc-deprecated-list-item__graphic.multi,:host([graphic=large]) .mdc-deprecated-list-item__graphic.multi{width:auto}:host([graphic=medium]) .mdc-deprecated-list-item__graphic ::slotted(*),:host([graphic=large]) .mdc-deprecated-list-item__graphic ::slotted(*){width:var(--mdc-list-item-graphic-size, 56px);line-height:var(--mdc-list-item-graphic-size, 56px)}:host([graphic=medium]) .mdc-deprecated-list-item__graphic ::slotted(.material-icons),:host([graphic=medium]) .mdc-deprecated-list-item__graphic ::slotted(mwc-icon),:host([graphic=large]) .mdc-deprecated-list-item__graphic ::slotted(.material-icons),:host([graphic=large]) .mdc-deprecated-list-item__graphic ::slotted(mwc-icon){line-height:var(--mdc-list-item-graphic-size, 56px) !important}:host([graphic=large]){padding-left:0px}`
/**
     * @license
     * Copyright 2021 Google LLC
     * SPDX-LIcense-Identifier: Apache-2.0
     */,Hm=((t,...e)=>{const i=1===t.length?t[0]:e.reduce((e,i,s)=>e+(t=>{if(!0===t._$cssResult$)return t.cssText;if("number"==typeof t)return t;throw Error("Value passed to 'css' function must be a 'css' function result: "+t+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+t[s+1],t[0]);return new lp(i,t,op)})`.mdc-ripple-surface{--mdc-ripple-fg-size: 0;--mdc-ripple-left: 0;--mdc-ripple-top: 0;--mdc-ripple-fg-scale: 1;--mdc-ripple-fg-translate-end: 0;--mdc-ripple-fg-translate-start: 0;-webkit-tap-highlight-color:rgba(0,0,0,0);will-change:transform,opacity;position:relative;outline:none;overflow:hidden}.mdc-ripple-surface::before,.mdc-ripple-surface::after{position:absolute;border-radius:50%;opacity:0;pointer-events:none;content:""}.mdc-ripple-surface::before{transition:opacity 15ms linear,background-color 15ms linear;z-index:1;z-index:var(--mdc-ripple-z-index, 1)}.mdc-ripple-surface::after{z-index:0;z-index:var(--mdc-ripple-z-index, 0)}.mdc-ripple-surface.mdc-ripple-upgraded::before{transform:scale(var(--mdc-ripple-fg-scale, 1))}.mdc-ripple-surface.mdc-ripple-upgraded::after{top:0;left:0;transform:scale(0);transform-origin:center center}.mdc-ripple-surface.mdc-ripple-upgraded--unbounded::after{top:var(--mdc-ripple-top, 0);left:var(--mdc-ripple-left, 0)}.mdc-ripple-surface.mdc-ripple-upgraded--foreground-activation::after{animation:mdc-ripple-fg-radius-in 225ms forwards,mdc-ripple-fg-opacity-in 75ms forwards}.mdc-ripple-surface.mdc-ripple-upgraded--foreground-deactivation::after{animation:mdc-ripple-fg-opacity-out 150ms;transform:translate(var(--mdc-ripple-fg-translate-end, 0)) scale(var(--mdc-ripple-fg-scale, 1))}.mdc-ripple-surface::before,.mdc-ripple-surface::after{top:calc(50% - 100%);left:calc(50% - 100%);width:200%;height:200%}.mdc-ripple-surface.mdc-ripple-upgraded::after{width:var(--mdc-ripple-fg-size, 100%);height:var(--mdc-ripple-fg-size, 100%)}.mdc-ripple-surface[data-mdc-ripple-is-unbounded],.mdc-ripple-upgraded--unbounded{overflow:visible}.mdc-ripple-surface[data-mdc-ripple-is-unbounded]::before,.mdc-ripple-surface[data-mdc-ripple-is-unbounded]::after,.mdc-ripple-upgraded--unbounded::before,.mdc-ripple-upgraded--unbounded::after{top:calc(50% - 50%);left:calc(50% - 50%);width:100%;height:100%}.mdc-ripple-surface[data-mdc-ripple-is-unbounded].mdc-ripple-upgraded::before,.mdc-ripple-surface[data-mdc-ripple-is-unbounded].mdc-ripple-upgraded::after,.mdc-ripple-upgraded--unbounded.mdc-ripple-upgraded::before,.mdc-ripple-upgraded--unbounded.mdc-ripple-upgraded::after{top:var(--mdc-ripple-top, calc(50% - 50%));left:var(--mdc-ripple-left, calc(50% - 50%));width:var(--mdc-ripple-fg-size, 100%);height:var(--mdc-ripple-fg-size, 100%)}.mdc-ripple-surface[data-mdc-ripple-is-unbounded].mdc-ripple-upgraded::after,.mdc-ripple-upgraded--unbounded.mdc-ripple-upgraded::after{width:var(--mdc-ripple-fg-size, 100%);height:var(--mdc-ripple-fg-size, 100%)}.mdc-ripple-surface::before,.mdc-ripple-surface::after{background-color:#000;background-color:var(--mdc-ripple-color, #000)}.mdc-ripple-surface:hover::before,.mdc-ripple-surface.mdc-ripple-surface--hover::before{opacity:0.04;opacity:var(--mdc-ripple-hover-opacity, 0.04)}.mdc-ripple-surface.mdc-ripple-upgraded--background-focused::before,.mdc-ripple-surface:not(.mdc-ripple-upgraded):focus::before{transition-duration:75ms;opacity:0.12;opacity:var(--mdc-ripple-focus-opacity, 0.12)}.mdc-ripple-surface:not(.mdc-ripple-upgraded)::after{transition:opacity 150ms linear}.mdc-ripple-surface:not(.mdc-ripple-upgraded):active::after{transition-duration:75ms;opacity:0.12;opacity:var(--mdc-ripple-press-opacity, 0.12)}.mdc-ripple-surface.mdc-ripple-upgraded{--mdc-ripple-fg-opacity:var(--mdc-ripple-press-opacity, 0.12)}@keyframes mdc-ripple-fg-radius-in{from{animation-timing-function:cubic-bezier(0.4, 0, 0.2, 1);transform:translate(var(--mdc-ripple-fg-translate-start, 0)) scale(1)}to{transform:translate(var(--mdc-ripple-fg-translate-end, 0)) scale(var(--mdc-ripple-fg-scale, 1))}}@keyframes mdc-ripple-fg-opacity-in{from{animation-timing-function:linear;opacity:0}to{opacity:var(--mdc-ripple-fg-opacity, 0)}}@keyframes mdc-ripple-fg-opacity-out{from{animation-timing-function:linear;opacity:var(--mdc-ripple-fg-opacity, 0)}to{opacity:0}}:host{position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;display:block}:host .mdc-ripple-surface{position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;will-change:unset}.mdc-ripple-surface--primary::before,.mdc-ripple-surface--primary::after{background-color:#6200ee;background-color:var(--mdc-ripple-color, var(--mdc-theme-primary, #6200ee))}.mdc-ripple-surface--primary:hover::before,.mdc-ripple-surface--primary.mdc-ripple-surface--hover::before{opacity:0.04;opacity:var(--mdc-ripple-hover-opacity, 0.04)}.mdc-ripple-surface--primary.mdc-ripple-upgraded--background-focused::before,.mdc-ripple-surface--primary:not(.mdc-ripple-upgraded):focus::before{transition-duration:75ms;opacity:0.12;opacity:var(--mdc-ripple-focus-opacity, 0.12)}.mdc-ripple-surface--primary:not(.mdc-ripple-upgraded)::after{transition:opacity 150ms linear}.mdc-ripple-surface--primary:not(.mdc-ripple-upgraded):active::after{transition-duration:75ms;opacity:0.12;opacity:var(--mdc-ripple-press-opacity, 0.12)}.mdc-ripple-surface--primary.mdc-ripple-upgraded{--mdc-ripple-fg-opacity:var(--mdc-ripple-press-opacity, 0.12)}.mdc-ripple-surface--primary--activated::before{opacity:0.12;opacity:var(--mdc-ripple-activated-opacity, 0.12)}.mdc-ripple-surface--primary--activated::before,.mdc-ripple-surface--primary--activated::after{background-color:#6200ee;background-color:var(--mdc-ripple-color, var(--mdc-theme-primary, #6200ee))}.mdc-ripple-surface--primary--activated:hover::before,.mdc-ripple-surface--primary--activated.mdc-ripple-surface--hover::before{opacity:0.16;opacity:var(--mdc-ripple-hover-opacity, 0.16)}.mdc-ripple-surface--primary--activated.mdc-ripple-upgraded--background-focused::before,.mdc-ripple-surface--primary--activated:not(.mdc-ripple-upgraded):focus::before{transition-duration:75ms;opacity:0.24;opacity:var(--mdc-ripple-focus-opacity, 0.24)}.mdc-ripple-surface--primary--activated:not(.mdc-ripple-upgraded)::after{transition:opacity 150ms linear}.mdc-ripple-surface--primary--activated:not(.mdc-ripple-upgraded):active::after{transition-duration:75ms;opacity:0.24;opacity:var(--mdc-ripple-press-opacity, 0.24)}.mdc-ripple-surface--primary--activated.mdc-ripple-upgraded{--mdc-ripple-fg-opacity:var(--mdc-ripple-press-opacity, 0.24)}.mdc-ripple-surface--primary--selected::before{opacity:0.08;opacity:var(--mdc-ripple-selected-opacity, 0.08)}.mdc-ripple-surface--primary--selected::before,.mdc-ripple-surface--primary--selected::after{background-color:#6200ee;background-color:var(--mdc-ripple-color, var(--mdc-theme-primary, #6200ee))}.mdc-ripple-surface--primary--selected:hover::before,.mdc-ripple-surface--primary--selected.mdc-ripple-surface--hover::before{opacity:0.12;opacity:var(--mdc-ripple-hover-opacity, 0.12)}.mdc-ripple-surface--primary--selected.mdc-ripple-upgraded--background-focused::before,.mdc-ripple-surface--primary--selected:not(.mdc-ripple-upgraded):focus::before{transition-duration:75ms;opacity:0.2;opacity:var(--mdc-ripple-focus-opacity, 0.2)}.mdc-ripple-surface--primary--selected:not(.mdc-ripple-upgraded)::after{transition:opacity 150ms linear}.mdc-ripple-surface--primary--selected:not(.mdc-ripple-upgraded):active::after{transition-duration:75ms;opacity:0.2;opacity:var(--mdc-ripple-press-opacity, 0.2)}.mdc-ripple-surface--primary--selected.mdc-ripple-upgraded{--mdc-ripple-fg-opacity:var(--mdc-ripple-press-opacity, 0.2)}.mdc-ripple-surface--accent::before,.mdc-ripple-surface--accent::after{background-color:#018786;background-color:var(--mdc-ripple-color, var(--mdc-theme-secondary, #018786))}.mdc-ripple-surface--accent:hover::before,.mdc-ripple-surface--accent.mdc-ripple-surface--hover::before{opacity:0.04;opacity:var(--mdc-ripple-hover-opacity, 0.04)}.mdc-ripple-surface--accent.mdc-ripple-upgraded--background-focused::before,.mdc-ripple-surface--accent:not(.mdc-ripple-upgraded):focus::before{transition-duration:75ms;opacity:0.12;opacity:var(--mdc-ripple-focus-opacity, 0.12)}.mdc-ripple-surface--accent:not(.mdc-ripple-upgraded)::after{transition:opacity 150ms linear}.mdc-ripple-surface--accent:not(.mdc-ripple-upgraded):active::after{transition-duration:75ms;opacity:0.12;opacity:var(--mdc-ripple-press-opacity, 0.12)}.mdc-ripple-surface--accent.mdc-ripple-upgraded{--mdc-ripple-fg-opacity:var(--mdc-ripple-press-opacity, 0.12)}.mdc-ripple-surface--accent--activated::before{opacity:0.12;opacity:var(--mdc-ripple-activated-opacity, 0.12)}.mdc-ripple-surface--accent--activated::before,.mdc-ripple-surface--accent--activated::after{background-color:#018786;background-color:var(--mdc-ripple-color, var(--mdc-theme-secondary, #018786))}.mdc-ripple-surface--accent--activated:hover::before,.mdc-ripple-surface--accent--activated.mdc-ripple-surface--hover::before{opacity:0.16;opacity:var(--mdc-ripple-hover-opacity, 0.16)}.mdc-ripple-surface--accent--activated.mdc-ripple-upgraded--background-focused::before,.mdc-ripple-surface--accent--activated:not(.mdc-ripple-upgraded):focus::before{transition-duration:75ms;opacity:0.24;opacity:var(--mdc-ripple-focus-opacity, 0.24)}.mdc-ripple-surface--accent--activated:not(.mdc-ripple-upgraded)::after{transition:opacity 150ms linear}.mdc-ripple-surface--accent--activated:not(.mdc-ripple-upgraded):active::after{transition-duration:75ms;opacity:0.24;opacity:var(--mdc-ripple-press-opacity, 0.24)}.mdc-ripple-surface--accent--activated.mdc-ripple-upgraded{--mdc-ripple-fg-opacity:var(--mdc-ripple-press-opacity, 0.24)}.mdc-ripple-surface--accent--selected::before{opacity:0.08;opacity:var(--mdc-ripple-selected-opacity, 0.08)}.mdc-ripple-surface--accent--selected::before,.mdc-ripple-surface--accent--selected::after{background-color:#018786;background-color:var(--mdc-ripple-color, var(--mdc-theme-secondary, #018786))}.mdc-ripple-surface--accent--selected:hover::before,.mdc-ripple-surface--accent--selected.mdc-ripple-surface--hover::before{opacity:0.12;opacity:var(--mdc-ripple-hover-opacity, 0.12)}.mdc-ripple-surface--accent--selected.mdc-ripple-upgraded--background-focused::before,.mdc-ripple-surface--accent--selected:not(.mdc-ripple-upgraded):focus::before{transition-duration:75ms;opacity:0.2;opacity:var(--mdc-ripple-focus-opacity, 0.2)}.mdc-ripple-surface--accent--selected:not(.mdc-ripple-upgraded)::after{transition:opacity 150ms linear}.mdc-ripple-surface--accent--selected:not(.mdc-ripple-upgraded):active::after{transition-duration:75ms;opacity:0.2;opacity:var(--mdc-ripple-press-opacity, 0.2)}.mdc-ripple-surface--accent--selected.mdc-ripple-upgraded{--mdc-ripple-fg-opacity:var(--mdc-ripple-press-opacity, 0.2)}.mdc-ripple-surface--disabled{opacity:0}.mdc-ripple-surface--internal-use-state-layer-custom-properties::before,.mdc-ripple-surface--internal-use-state-layer-custom-properties::after{background-color:#000;background-color:var(--mdc-ripple-hover-state-layer-color, #000)}.mdc-ripple-surface--internal-use-state-layer-custom-properties:hover::before,.mdc-ripple-surface--internal-use-state-layer-custom-properties.mdc-ripple-surface--hover::before{opacity:0.04;opacity:var(--mdc-ripple-hover-state-layer-opacity, 0.04)}.mdc-ripple-surface--internal-use-state-layer-custom-properties.mdc-ripple-upgraded--background-focused::before,.mdc-ripple-surface--internal-use-state-layer-custom-properties:not(.mdc-ripple-upgraded):focus::before{transition-duration:75ms;opacity:0.12;opacity:var(--mdc-ripple-focus-state-layer-opacity, 0.12)}.mdc-ripple-surface--internal-use-state-layer-custom-properties:not(.mdc-ripple-upgraded)::after{transition:opacity 150ms linear}.mdc-ripple-surface--internal-use-state-layer-custom-properties:not(.mdc-ripple-upgraded):active::after{transition-duration:75ms;opacity:0.12;opacity:var(--mdc-ripple-pressed-state-layer-opacity, 0.12)}.mdc-ripple-surface--internal-use-state-layer-custom-properties.mdc-ripple-upgraded{--mdc-ripple-fg-opacity:var(--mdc-ripple-pressed-state-layer-opacity, 0.12)}`
/**
     * @license
     * Copyright 2021 Google LLC
     * SPDX-LIcense-Identifier: Apache-2.0
     */,Um=Nc`mwc-list ::slotted([mwc-list-item]:not([twoline])),mwc-list ::slotted([noninteractive]:not([twoline])){height:var(--mdc-menu-item-height, 48px)}`
/**
     * @license
     * Copyright 2021 Google LLC
     * SPDX-LIcense-Identifier: Apache-2.0
     */,zm=Nc`.mdc-menu-surface{display:none;position:absolute;box-sizing:border-box;max-width:calc(100vw - 32px);max-width:var(--mdc-menu-max-width, calc(100vw - 32px));max-height:calc(100vh - 32px);max-height:var(--mdc-menu-max-height, calc(100vh - 32px));margin:0;padding:0;transform:scale(1);transform-origin:top left;opacity:0;overflow:auto;will-change:transform,opacity;z-index:8;transition:opacity .03s linear,transform .12s cubic-bezier(0, 0, 0.2, 1),height 250ms cubic-bezier(0, 0, 0.2, 1);box-shadow:0px 5px 5px -3px rgba(0, 0, 0, 0.2),0px 8px 10px 1px rgba(0, 0, 0, 0.14),0px 3px 14px 2px rgba(0,0,0,.12);background-color:#fff;background-color:var(--mdc-theme-surface, #fff);color:#000;color:var(--mdc-theme-on-surface, #000);border-radius:4px;border-radius:var(--mdc-shape-medium, 4px);transform-origin-left:top left;transform-origin-right:top right}.mdc-menu-surface:focus{outline:none}.mdc-menu-surface--animating-open{display:inline-block;transform:scale(0.8);opacity:0}.mdc-menu-surface--open{display:inline-block;transform:scale(1);opacity:1}.mdc-menu-surface--animating-closed{display:inline-block;opacity:0;transition:opacity .075s linear}[dir=rtl] .mdc-menu-surface,.mdc-menu-surface[dir=rtl]{transform-origin-left:top right;transform-origin-right:top left}.mdc-menu-surface--anchor{position:relative;overflow:visible}.mdc-menu-surface--fixed{position:fixed}.mdc-menu-surface--fullwidth{width:100%}:host(:not([open])){display:none}.mdc-menu-surface{z-index:8;z-index:var(--mdc-menu-z-index, 8);min-width:112px;min-width:var(--mdc-menu-min-width, 112px)}`
/**
     * @license
     * Copyright 2021 Google LLC
     * SPDX-LIcense-Identifier: Apache-2.0
     */,Fm=((t,...e)=>{const i=1===t.length?t[0]:e.reduce((e,i,s)=>e+(t=>{if(!0===t._$cssResult$)return t.cssText;if("number"==typeof t)return t;throw Error("Value passed to 'css' function must be a 'css' function result: "+t+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+t[s+1],t[0]);return new Tu(i,t,Su)})`.mdc-notched-outline{display:flex;position:absolute;top:0;right:0;left:0;box-sizing:border-box;width:100%;max-width:100%;height:100%;text-align:left;pointer-events:none}[dir=rtl] .mdc-notched-outline,.mdc-notched-outline[dir=rtl]{text-align:right}.mdc-notched-outline__leading,.mdc-notched-outline__notch,.mdc-notched-outline__trailing{box-sizing:border-box;height:100%;border-top:1px solid;border-bottom:1px solid;pointer-events:none}.mdc-notched-outline__leading{border-left:1px solid;border-right:none;width:12px}[dir=rtl] .mdc-notched-outline__leading,.mdc-notched-outline__leading[dir=rtl]{border-left:none;border-right:1px solid}.mdc-notched-outline__trailing{border-left:none;border-right:1px solid;flex-grow:1}[dir=rtl] .mdc-notched-outline__trailing,.mdc-notched-outline__trailing[dir=rtl]{border-left:1px solid;border-right:none}.mdc-notched-outline__notch{flex:0 0 auto;width:auto;max-width:calc(100% - 12px * 2)}.mdc-notched-outline .mdc-floating-label{display:inline-block;position:relative;max-width:100%}.mdc-notched-outline .mdc-floating-label--float-above{text-overflow:clip}.mdc-notched-outline--upgraded .mdc-floating-label--float-above{max-width:calc(100% / 0.75)}.mdc-notched-outline--notched .mdc-notched-outline__notch{padding-left:0;padding-right:8px;border-top:none}[dir=rtl] .mdc-notched-outline--notched .mdc-notched-outline__notch,.mdc-notched-outline--notched .mdc-notched-outline__notch[dir=rtl]{padding-left:8px;padding-right:0}.mdc-notched-outline--no-label .mdc-notched-outline__notch{display:none}:host{display:block;position:absolute;right:0;left:0;box-sizing:border-box;width:100%;max-width:100%;height:100%;text-align:left;pointer-events:none}[dir=rtl] :host,:host([dir=rtl]){text-align:right}::slotted(.mdc-floating-label){display:inline-block;position:relative;top:17px;bottom:auto;max-width:100%}::slotted(.mdc-floating-label--float-above){text-overflow:clip}.mdc-notched-outline--upgraded ::slotted(.mdc-floating-label--float-above){max-width:calc(100% / 0.75)}.mdc-notched-outline .mdc-notched-outline__leading{border-top-left-radius:4px;border-top-left-radius:var(--mdc-shape-small, 4px);border-top-right-radius:0;border-bottom-right-radius:0;border-bottom-left-radius:4px;border-bottom-left-radius:var(--mdc-shape-small, 4px)}[dir=rtl] .mdc-notched-outline .mdc-notched-outline__leading,.mdc-notched-outline .mdc-notched-outline__leading[dir=rtl]{border-top-left-radius:0;border-top-right-radius:4px;border-top-right-radius:var(--mdc-shape-small, 4px);border-bottom-right-radius:4px;border-bottom-right-radius:var(--mdc-shape-small, 4px);border-bottom-left-radius:0}@supports(top: max(0%)){.mdc-notched-outline .mdc-notched-outline__leading{width:max(12px, var(--mdc-shape-small, 4px))}}@supports(top: max(0%)){.mdc-notched-outline .mdc-notched-outline__notch{max-width:calc(100% - max(12px, var(--mdc-shape-small, 4px)) * 2)}}.mdc-notched-outline .mdc-notched-outline__trailing{border-top-left-radius:0;border-top-right-radius:4px;border-top-right-radius:var(--mdc-shape-small, 4px);border-bottom-right-radius:4px;border-bottom-right-radius:var(--mdc-shape-small, 4px);border-bottom-left-radius:0}[dir=rtl] .mdc-notched-outline .mdc-notched-outline__trailing,.mdc-notched-outline .mdc-notched-outline__trailing[dir=rtl]{border-top-left-radius:4px;border-top-left-radius:var(--mdc-shape-small, 4px);border-top-right-radius:0;border-bottom-right-radius:0;border-bottom-left-radius:4px;border-bottom-left-radius:var(--mdc-shape-small, 4px)}.mdc-notched-outline__leading,.mdc-notched-outline__notch,.mdc-notched-outline__trailing{border-color:var(--mdc-notched-outline-border-color, var(--mdc-theme-primary, #6200ee));border-width:1px;border-width:var(--mdc-notched-outline-stroke-width, 1px)}.mdc-notched-outline--notched .mdc-notched-outline__notch{padding-top:0;padding-top:var(--mdc-notched-outline-notch-offset, 0)}`,Bm={"mwc-select":class extends gl{static get styles(){return Mm}},"mwc-list":class extends vc{static get styles(){return Nm}},"mwc-list-item":class extends $c{static get styles(){return Dm}},"mwc-ripple":class extends _u{static get styles(){return Hm}},"mwc-menu":class extends jh{static get styles(){return Um}},"mwc-menu-surface":class extends Gh{static get styles(){return zm}},"mwc-notched-outline":class extends Lm{static get styles(){return Fm}}};function Vm(t,e,i){if(void 0!==e)
/**
     * @license
     * Copyright 2021 Google LLC
     * SPDX-License-Identifier: Apache-2.0
     */
return function(t,e,i){const s=t.constructor;if(!i){const t=`__${e}`;if(!(i=s.getPropertyDescriptor(e,t)))throw new Error("@ariaProperty must be used after a @property decorator")}const n=i;let r="";if(!n.set)throw new Error(`@ariaProperty requires a setter for ${e}`);if(t.dispatchWizEvent)return i;const o={configurable:!0,enumerable:!0,set(t){if(""===r){const t=s.getPropertyOptions(e);r="string"==typeof t.attribute?t.attribute:e}this.hasAttribute(r)&&this.removeAttribute(r),n.set.call(this,t)}};return n.get&&(o.get=function(){return n.get.call(this)}),o}(t,e,i);throw new Error("@ariaProperty only supports TypeScript Decorators")}
/**
     * @license
     * Copyright 2016 Google Inc.
     *
     * Permission is hereby granted, free of charge, to any person obtaining a copy
     * of this software and associated documentation files (the "Software"), to deal
     * in the Software without restriction, including without limitation the rights
     * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
     * copies of the Software, and to permit persons to whom the Software is
     * furnished to do so, subject to the following conditions:
     *
     * The above copyright notice and this permission notice shall be included in
     * all copies or substantial portions of the Software.
     *
     * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
     * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
     * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
     * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
     * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
     * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
     * THE SOFTWARE.
     */var jm=function(){function t(t){void 0===t&&(t={}),this.adapter=t}return Object.defineProperty(t,"cssClasses",{get:function(){return{}},enumerable:!1,configurable:!0}),Object.defineProperty(t,"strings",{get:function(){return{}},enumerable:!1,configurable:!0}),Object.defineProperty(t,"numbers",{get:function(){return{}},enumerable:!1,configurable:!0}),Object.defineProperty(t,"defaultAdapter",{get:function(){return{}},enumerable:!1,configurable:!0}),t.prototype.init=function(){},t.prototype.destroy=function(){},t}(),Wm={CHECKED:"mdc-switch--checked",DISABLED:"mdc-switch--disabled"},qm={ARIA_CHECKED_ATTR:"aria-checked",NATIVE_CONTROL_SELECTOR:".mdc-switch__native-control",RIPPLE_SURFACE_SELECTOR:".mdc-switch__thumb-underlay"},Ym=function(t){function e(i){return t.call(this,s(s({},e.defaultAdapter),i))||this}return i(e,t),Object.defineProperty(e,"strings",{get:function(){return qm},enumerable:!1,configurable:!0}),Object.defineProperty(e,"cssClasses",{get:function(){return Wm},enumerable:!1,configurable:!0}),Object.defineProperty(e,"defaultAdapter",{get:function(){return{addClass:function(){},removeClass:function(){},setNativeControlChecked:function(){},setNativeControlDisabled:function(){},setNativeControlAttr:function(){}}},enumerable:!1,configurable:!0}),e.prototype.setChecked=function(t){this.adapter.setNativeControlChecked(t),this.updateAriaChecked(t),this.updateCheckedStyling(t)},e.prototype.setDisabled=function(t){this.adapter.setNativeControlDisabled(t),t?this.adapter.addClass(Wm.DISABLED):this.adapter.removeClass(Wm.DISABLED)},e.prototype.handleChange=function(t){var e=t.target;this.updateAriaChecked(e.checked),this.updateCheckedStyling(e.checked)},e.prototype.updateCheckedStyling=function(t){t?this.adapter.addClass(Wm.CHECKED):this.adapter.removeClass(Wm.CHECKED)},e.prototype.updateAriaChecked=function(t){this.adapter.setNativeControlAttr(qm.ARIA_CHECKED_ATTR,""+!!t)},e}(jm);
/**
     * @license
     * Copyright 2018 Google Inc.
     *
     * Permission is hereby granted, free of charge, to any person obtaining a copy
     * of this software and associated documentation files (the "Software"), to deal
     * in the Software without restriction, including without limitation the rights
     * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
     * copies of the Software, and to permit persons to whom the Software is
     * furnished to do so, subject to the following conditions:
     *
     * The above copyright notice and this permission notice shall be included in
     * all copies or substantial portions of the Software.
     *
     * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
     * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
     * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
     * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
     * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
     * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
     * THE SOFTWARE.
     */
/**
     * @license
     * Copyright 2019 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
const Xm=window,Gm=Xm.ShadowRoot&&(void 0===Xm.ShadyCSS||Xm.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,Km=Symbol(),Jm=new WeakMap;let Zm=class{constructor(t,e,i){if(this._$cssResult$=!0,i!==Km)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o;const e=this.t;if(Gm&&void 0===t){const i=void 0!==e&&1===e.length;i&&(t=Jm.get(e)),void 0===t&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),i&&Jm.set(e,t))}return t}toString(){return this.cssText}};const Qm=Gm?t=>t:t=>t instanceof CSSStyleSheet?(t=>{let e="";for(const i of t.cssRules)e+=i.cssText;return(t=>new Zm("string"==typeof t?t:t+"",void 0,Km))(e)})(t):t;
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */var tf;const ef=window,sf=ef.trustedTypes,nf=sf?sf.emptyScript:"",rf=ef.reactiveElementPolyfillSupport,of={toAttribute(t,e){switch(e){case Boolean:t=t?nf:null;break;case Object:case Array:t=null==t?t:JSON.stringify(t)}return t},fromAttribute(t,e){let i=t;switch(e){case Boolean:i=null!==t;break;case Number:i=null===t?null:Number(t);break;case Object:case Array:try{i=JSON.parse(t)}catch(t){i=null}}return i}},af=(t,e)=>e!==t&&(e==e||t==t),lf={attribute:!0,type:String,converter:of,reflect:!1,hasChanged:af},df="finalized";let cf=class extends HTMLElement{constructor(){super(),this._$Ei=new Map,this.isUpdatePending=!1,this.hasUpdated=!1,this._$El=null,this._$Eu()}static addInitializer(t){var e;this.finalize(),(null!==(e=this.h)&&void 0!==e?e:this.h=[]).push(t)}static get observedAttributes(){this.finalize();const t=[];return this.elementProperties.forEach((e,i)=>{const s=this._$Ep(i,e);void 0!==s&&(this._$Ev.set(s,i),t.push(s))}),t}static createProperty(t,e=lf){if(e.state&&(e.attribute=!1),this.finalize(),this.elementProperties.set(t,e),!e.noAccessor&&!this.prototype.hasOwnProperty(t)){const i="symbol"==typeof t?Symbol():"__"+t,s=this.getPropertyDescriptor(t,i,e);void 0!==s&&Object.defineProperty(this.prototype,t,s)}}static getPropertyDescriptor(t,e,i){return{get(){return this[e]},set(s){const n=this[t];this[e]=s,this.requestUpdate(t,n,i)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)||lf}static finalize(){if(this.hasOwnProperty(df))return!1;this[df]=!0;const t=Object.getPrototypeOf(this);if(t.finalize(),void 0!==t.h&&(this.h=[...t.h]),this.elementProperties=new Map(t.elementProperties),this._$Ev=new Map,this.hasOwnProperty("properties")){const t=this.properties,e=[...Object.getOwnPropertyNames(t),...Object.getOwnPropertySymbols(t)];for(const i of e)this.createProperty(i,t[i])}return this.elementStyles=this.finalizeStyles(this.styles),!0}static finalizeStyles(t){const e=[];if(Array.isArray(t)){const i=new Set(t.flat(1/0).reverse());for(const t of i)e.unshift(Qm(t))}else void 0!==t&&e.push(Qm(t));return e}static _$Ep(t,e){const i=e.attribute;return!1===i?void 0:"string"==typeof i?i:"string"==typeof t?t.toLowerCase():void 0}_$Eu(){var t;this._$E_=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$Eg(),this.requestUpdate(),null===(t=this.constructor.h)||void 0===t||t.forEach(t=>t(this))}addController(t){var e,i;(null!==(e=this._$ES)&&void 0!==e?e:this._$ES=[]).push(t),void 0!==this.renderRoot&&this.isConnected&&(null===(i=t.hostConnected)||void 0===i||i.call(t))}removeController(t){var e;null===(e=this._$ES)||void 0===e||e.splice(this._$ES.indexOf(t)>>>0,1)}_$Eg(){this.constructor.elementProperties.forEach((t,e)=>{this.hasOwnProperty(e)&&(this._$Ei.set(e,this[e]),delete this[e])})}createRenderRoot(){var t;const e=null!==(t=this.shadowRoot)&&void 0!==t?t:this.attachShadow(this.constructor.shadowRootOptions);return((t,e)=>{Gm?t.adoptedStyleSheets=e.map(t=>t instanceof CSSStyleSheet?t:t.styleSheet):e.forEach(e=>{const i=document.createElement("style"),s=Xm.litNonce;void 0!==s&&i.setAttribute("nonce",s),i.textContent=e.cssText,t.appendChild(i)})})(e,this.constructor.elementStyles),e}connectedCallback(){var t;void 0===this.renderRoot&&(this.renderRoot=this.createRenderRoot()),this.enableUpdating(!0),null===(t=this._$ES)||void 0===t||t.forEach(t=>{var e;return null===(e=t.hostConnected)||void 0===e?void 0:e.call(t)})}enableUpdating(t){}disconnectedCallback(){var t;null===(t=this._$ES)||void 0===t||t.forEach(t=>{var e;return null===(e=t.hostDisconnected)||void 0===e?void 0:e.call(t)})}attributeChangedCallback(t,e,i){this._$AK(t,i)}_$EO(t,e,i=lf){var s;const n=this.constructor._$Ep(t,i);if(void 0!==n&&!0===i.reflect){const r=(void 0!==(null===(s=i.converter)||void 0===s?void 0:s.toAttribute)?i.converter:of).toAttribute(e,i.type);this._$El=t,null==r?this.removeAttribute(n):this.setAttribute(n,r),this._$El=null}}_$AK(t,e){var i;const s=this.constructor,n=s._$Ev.get(t);if(void 0!==n&&this._$El!==n){const t=s.getPropertyOptions(n),r="function"==typeof t.converter?{fromAttribute:t.converter}:void 0!==(null===(i=t.converter)||void 0===i?void 0:i.fromAttribute)?t.converter:of;this._$El=n,this[n]=r.fromAttribute(e,t.type),this._$El=null}}requestUpdate(t,e,i){let s=!0;void 0!==t&&(((i=i||this.constructor.getPropertyOptions(t)).hasChanged||af)(this[t],e)?(this._$AL.has(t)||this._$AL.set(t,e),!0===i.reflect&&this._$El!==t&&(void 0===this._$EC&&(this._$EC=new Map),this._$EC.set(t,i))):s=!1),!this.isUpdatePending&&s&&(this._$E_=this._$Ej())}async _$Ej(){this.isUpdatePending=!0;try{await this._$E_}catch(t){Promise.reject(t)}const t=this.scheduleUpdate();return null!=t&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){var t;if(!this.isUpdatePending)return;this.hasUpdated,this._$Ei&&(this._$Ei.forEach((t,e)=>this[e]=t),this._$Ei=void 0);let e=!1;const i=this._$AL;try{e=this.shouldUpdate(i),e?(this.willUpdate(i),null===(t=this._$ES)||void 0===t||t.forEach(t=>{var e;return null===(e=t.hostUpdate)||void 0===e?void 0:e.call(t)}),this.update(i)):this._$Ek()}catch(t){throw e=!1,this._$Ek(),t}e&&this._$AE(i)}willUpdate(t){}_$AE(t){var e;null===(e=this._$ES)||void 0===e||e.forEach(t=>{var e;return null===(e=t.hostUpdated)||void 0===e?void 0:e.call(t)}),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$Ek(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$E_}shouldUpdate(t){return!0}update(t){void 0!==this._$EC&&(this._$EC.forEach((t,e)=>this._$EO(e,this[e],t)),this._$EC=void 0),this._$Ek()}updated(t){}firstUpdated(t){}};
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
var hf;cf[df]=!0,cf.elementProperties=new Map,cf.elementStyles=[],cf.shadowRootOptions={mode:"open"},null==rf||rf({ReactiveElement:cf}),(null!==(tf=ef.reactiveElementVersions)&&void 0!==tf?tf:ef.reactiveElementVersions=[]).push("1.6.3");const pf=window,uf=pf.trustedTypes,mf=uf?uf.createPolicy("lit-html",{createHTML:t=>t}):void 0,ff="$lit$",gf=`lit$${(Math.random()+"").slice(9)}$`,vf="?"+gf,_f=`<${vf}>`,bf=document,yf=()=>bf.createComment(""),xf=t=>null===t||"object"!=typeof t&&"function"!=typeof t,$f=Array.isArray,wf="[ \t\n\f\r]",Af=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,Ef=/-->/g,Sf=/>/g,Cf=RegExp(`>|${wf}(?:([^\\s"'>=/]+)(${wf}*=${wf}*(?:[^ \t\n\f\r"'\`<>=]|("|')|))|$)`,"g"),Tf=/'/g,If=/"/g,Of=/^(?:script|style|textarea|title)$/i,kf=(t=>(e,...i)=>({_$litType$:t,strings:e,values:i}))(1),Rf=Symbol.for("lit-noChange"),Pf=Symbol.for("lit-nothing"),Lf=new WeakMap,Mf=bf.createTreeWalker(bf,129,null,!1);function Nf(t,e){if(!Array.isArray(t)||!t.hasOwnProperty("raw"))throw Error("invalid template strings array");return void 0!==mf?mf.createHTML(e):e}let Df=class t{constructor({strings:e,_$litType$:i},s){let n;this.parts=[];let r=0,o=0;const a=e.length-1,l=this.parts,[d,c]=((t,e)=>{const i=t.length-1,s=[];let n,r=2===e?"<svg>":"",o=Af;for(let e=0;e<i;e++){const i=t[e];let a,l,d=-1,c=0;for(;c<i.length&&(o.lastIndex=c,l=o.exec(i),null!==l);)c=o.lastIndex,o===Af?"!--"===l[1]?o=Ef:void 0!==l[1]?o=Sf:void 0!==l[2]?(Of.test(l[2])&&(n=RegExp("</"+l[2],"g")),o=Cf):void 0!==l[3]&&(o=Cf):o===Cf?">"===l[0]?(o=null!=n?n:Af,d=-1):void 0===l[1]?d=-2:(d=o.lastIndex-l[2].length,a=l[1],o=void 0===l[3]?Cf:'"'===l[3]?If:Tf):o===If||o===Tf?o=Cf:o===Ef||o===Sf?o=Af:(o=Cf,n=void 0);const h=o===Cf&&t[e+1].startsWith("/>")?" ":"";r+=o===Af?i+_f:d>=0?(s.push(a),i.slice(0,d)+ff+i.slice(d)+gf+h):i+gf+(-2===d?(s.push(void 0),e):h)}return[Nf(t,r+(t[i]||"<?>")+(2===e?"</svg>":"")),s]})(e,i);if(this.el=t.createElement(d,s),Mf.currentNode=this.el.content,2===i){const t=this.el.content,e=t.firstChild;e.remove(),t.append(...e.childNodes)}for(;null!==(n=Mf.nextNode())&&l.length<a;){if(1===n.nodeType){if(n.hasAttributes()){const t=[];for(const e of n.getAttributeNames())if(e.endsWith(ff)||e.startsWith(gf)){const i=c[o++];if(t.push(e),void 0!==i){const t=n.getAttribute(i.toLowerCase()+ff).split(gf),e=/([.?@])?(.*)/.exec(i);l.push({type:1,index:r,name:e[2],strings:t,ctor:"."===e[1]?Bf:"?"===e[1]?jf:"@"===e[1]?Wf:Ff})}else l.push({type:6,index:r})}for(const e of t)n.removeAttribute(e)}if(Of.test(n.tagName)){const t=n.textContent.split(gf),e=t.length-1;if(e>0){n.textContent=uf?uf.emptyScript:"";for(let i=0;i<e;i++)n.append(t[i],yf()),Mf.nextNode(),l.push({type:2,index:++r});n.append(t[e],yf())}}}else if(8===n.nodeType)if(n.data===vf)l.push({type:2,index:r});else{let t=-1;for(;-1!==(t=n.data.indexOf(gf,t+1));)l.push({type:7,index:r}),t+=gf.length-1}r++}}static createElement(t,e){const i=bf.createElement("template");return i.innerHTML=t,i}};function Hf(t,e,i=t,s){var n,r,o,a;if(e===Rf)return e;let l=void 0!==s?null===(n=i._$Co)||void 0===n?void 0:n[s]:i._$Cl;const d=xf(e)?void 0:e._$litDirective$;return(null==l?void 0:l.constructor)!==d&&(null===(r=null==l?void 0:l._$AO)||void 0===r||r.call(l,!1),void 0===d?l=void 0:(l=new d(t),l._$AT(t,i,s)),void 0!==s?(null!==(o=(a=i)._$Co)&&void 0!==o?o:a._$Co=[])[s]=l:i._$Cl=l),void 0!==l&&(e=Hf(t,l._$AS(t,e.values),l,s)),e}let Uf=class{constructor(t,e){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){var e;const{el:{content:i},parts:s}=this._$AD,n=(null!==(e=null==t?void 0:t.creationScope)&&void 0!==e?e:bf).importNode(i,!0);Mf.currentNode=n;let r=Mf.nextNode(),o=0,a=0,l=s[0];for(;void 0!==l;){if(o===l.index){let e;2===l.type?e=new zf(r,r.nextSibling,this,t):1===l.type?e=new l.ctor(r,l.name,l.strings,this,t):6===l.type&&(e=new qf(r,this,t)),this._$AV.push(e),l=s[++a]}o!==(null==l?void 0:l.index)&&(r=Mf.nextNode(),o++)}return Mf.currentNode=bf,n}v(t){let e=0;for(const i of this._$AV)void 0!==i&&(void 0!==i.strings?(i._$AI(t,i,e),e+=i.strings.length-2):i._$AI(t[e])),e++}},zf=class t{constructor(t,e,i,s){var n;this.type=2,this._$AH=Pf,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=i,this.options=s,this._$Cp=null===(n=null==s?void 0:s.isConnected)||void 0===n||n}get _$AU(){var t,e;return null!==(e=null===(t=this._$AM)||void 0===t?void 0:t._$AU)&&void 0!==e?e:this._$Cp}get parentNode(){let t=this._$AA.parentNode;const e=this._$AM;return void 0!==e&&11===(null==t?void 0:t.nodeType)&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=Hf(this,t,e),xf(t)?t===Pf||null==t||""===t?(this._$AH!==Pf&&this._$AR(),this._$AH=Pf):t!==this._$AH&&t!==Rf&&this._(t):void 0!==t._$litType$?this.g(t):void 0!==t.nodeType?this.$(t):(t=>$f(t)||"function"==typeof(null==t?void 0:t[Symbol.iterator]))(t)?this.T(t):this._(t)}k(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}$(t){this._$AH!==t&&(this._$AR(),this._$AH=this.k(t))}_(t){this._$AH!==Pf&&xf(this._$AH)?this._$AA.nextSibling.data=t:this.$(bf.createTextNode(t)),this._$AH=t}g(t){var e;const{values:i,_$litType$:s}=t,n="number"==typeof s?this._$AC(t):(void 0===s.el&&(s.el=Df.createElement(Nf(s.h,s.h[0]),this.options)),s);if((null===(e=this._$AH)||void 0===e?void 0:e._$AD)===n)this._$AH.v(i);else{const t=new Uf(n,this),e=t.u(this.options);t.v(i),this.$(e),this._$AH=t}}_$AC(t){let e=Lf.get(t.strings);return void 0===e&&Lf.set(t.strings,e=new Df(t)),e}T(e){$f(this._$AH)||(this._$AH=[],this._$AR());const i=this._$AH;let s,n=0;for(const r of e)n===i.length?i.push(s=new t(this.k(yf()),this.k(yf()),this,this.options)):s=i[n],s._$AI(r),n++;n<i.length&&(this._$AR(s&&s._$AB.nextSibling,n),i.length=n)}_$AR(t=this._$AA.nextSibling,e){var i;for(null===(i=this._$AP)||void 0===i||i.call(this,!1,!0,e);t&&t!==this._$AB;){const e=t.nextSibling;t.remove(),t=e}}setConnected(t){var e;void 0===this._$AM&&(this._$Cp=t,null===(e=this._$AP)||void 0===e||e.call(this,t))}},Ff=class{constructor(t,e,i,s,n){this.type=1,this._$AH=Pf,this._$AN=void 0,this.element=t,this.name=e,this._$AM=s,this.options=n,i.length>2||""!==i[0]||""!==i[1]?(this._$AH=Array(i.length-1).fill(new String),this.strings=i):this._$AH=Pf}get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}_$AI(t,e=this,i,s){const n=this.strings;let r=!1;if(void 0===n)t=Hf(this,t,e,0),r=!xf(t)||t!==this._$AH&&t!==Rf,r&&(this._$AH=t);else{const s=t;let o,a;for(t=n[0],o=0;o<n.length-1;o++)a=Hf(this,s[i+o],e,o),a===Rf&&(a=this._$AH[o]),r||(r=!xf(a)||a!==this._$AH[o]),a===Pf?t=Pf:t!==Pf&&(t+=(null!=a?a:"")+n[o+1]),this._$AH[o]=a}r&&!s&&this.j(t)}j(t){t===Pf?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,null!=t?t:"")}},Bf=class extends Ff{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===Pf?void 0:t}};const Vf=uf?uf.emptyScript:"";let jf=class extends Ff{constructor(){super(...arguments),this.type=4}j(t){t&&t!==Pf?this.element.setAttribute(this.name,Vf):this.element.removeAttribute(this.name)}},Wf=class extends Ff{constructor(t,e,i,s,n){super(t,e,i,s,n),this.type=5}_$AI(t,e=this){var i;if((t=null!==(i=Hf(this,t,e,0))&&void 0!==i?i:Pf)===Rf)return;const s=this._$AH,n=t===Pf&&s!==Pf||t.capture!==s.capture||t.once!==s.once||t.passive!==s.passive,r=t!==Pf&&(s===Pf||n);n&&this.element.removeEventListener(this.name,this,s),r&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){var e,i;"function"==typeof this._$AH?this._$AH.call(null!==(i=null===(e=this.options)||void 0===e?void 0:e.host)&&void 0!==i?i:this.element,t):this._$AH.handleEvent(t)}},qf=class{constructor(t,e,i){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=i}get _$AU(){return this._$AM._$AU}_$AI(t){Hf(this,t)}};const Yf=pf.litHtmlPolyfillSupport;null==Yf||Yf(Df,zf),(null!==(hf=pf.litHtmlVersions)&&void 0!==hf?hf:pf.litHtmlVersions=[]).push("2.8.0");
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
var Xf,Gf;let Kf=class extends cf{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){var t,e;const i=super.createRenderRoot();return null!==(t=(e=this.renderOptions).renderBefore)&&void 0!==t||(e.renderBefore=i.firstChild),i}update(t){const e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=((t,e,i)=>{var s,n;const r=null!==(s=null==i?void 0:i.renderBefore)&&void 0!==s?s:e;let o=r._$litPart$;if(void 0===o){const t=null!==(n=null==i?void 0:i.renderBefore)&&void 0!==n?n:null;r._$litPart$=o=new zf(e.insertBefore(yf(),t),t,void 0,null!=i?i:{})}return o._$AI(t),o})(e,this.renderRoot,this.renderOptions)}connectedCallback(){var t;super.connectedCallback(),null===(t=this._$Do)||void 0===t||t.setConnected(!0)}disconnectedCallback(){var t;super.disconnectedCallback(),null===(t=this._$Do)||void 0===t||t.setConnected(!1)}render(){return Rf}};Kf.finalized=!0,Kf._$litElement$=!0,null===(Xf=globalThis.litElementHydrateSupport)||void 0===Xf||Xf.call(globalThis,{LitElement:Kf});const Jf=globalThis.litElementPolyfillSupport;null==Jf||Jf({LitElement:Kf}),(null!==(Gf=globalThis.litElementVersions)&&void 0!==Gf?Gf:globalThis.litElementVersions=[]).push("3.3.3");
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
const Zf=(t,e)=>"method"===e.kind&&e.descriptor&&!("value"in e.descriptor)?{...e,finisher(i){i.createProperty(e.key,t)}}:{kind:"field",key:Symbol(),placement:"own",descriptor:{},originalKey:e.key,initializer(){"function"==typeof e.initializer&&(this[e.key]=e.initializer.call(this))},finisher(i){i.createProperty(e.key,t)}};function Qf(t){return(e,i)=>void 0!==i?((t,e,i)=>{e.constructor.createProperty(i,t)})(t,e,i):Zf(t,e)}
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
const tg=({finisher:t,descriptor:e})=>(i,s)=>{var n;if(void 0===s){const s=null!==(n=i.originalKey)&&void 0!==n?n:i.key,r=null!=e?{kind:"method",placement:"prototype",key:s,descriptor:e(i.key)}:{...i,key:s};return null!=t&&(r.finisher=function(e){t(e,s)}),r}{const n=i.constructor;void 0!==e&&Object.defineProperty(i,s,e(s)),null==t||t(n,s)}};
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */function eg(t){return tg({finisher:(e,i)=>{Object.assign(e.prototype[i],t)}})}
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */function ig(t,e){return tg({descriptor:e=>{const i={get(){var e,i;return null!==(i=null===(e=this.renderRoot)||void 0===e?void 0:e.querySelector(t))&&void 0!==i?i:null},enumerable:!0,configurable:!0};return i}})}
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
/**
     * @license
     * Copyright 2021 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
var sg;null===(sg=window.HTMLSlotElement)||void 0===sg||sg.prototype.assignedElements;
/**
     * @license
     * Copyright 2018 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
const ng=t=>null!=t?t:Pf;
/**
     * @license
     * Copyright 2018 Google LLC
     * SPDX-License-Identifier: Apache-2.0
     */class rg extends Qi{constructor(){super(...arguments),this.checked=!1,this.disabled=!1,this.shouldRenderRipple=!1,this.mdcFoundationClass=Ym,this.rippleHandlers=new _c(()=>(this.shouldRenderRipple=!0,this.ripple))}changeHandler(t){this.mdcFoundation.handleChange(t),this.checked=this.formElement.checked}createAdapter(){return Object.assign(Object.assign({},Xi(this.mdcRoot)),{setNativeControlChecked:t=>{this.formElement.checked=t},setNativeControlDisabled:t=>{this.formElement.disabled=t},setNativeControlAttr:(t,e)=>{this.formElement.setAttribute(t,e)}})}renderRipple(){return this.shouldRenderRipple?kf`
        <mwc-ripple
          .accent="${this.checked}"
          .disabled="${this.disabled}"
          unbounded>
        </mwc-ripple>`:""}focus(){const t=this.formElement;t&&(this.rippleHandlers.startFocus(),t.focus())}blur(){const t=this.formElement;t&&(this.rippleHandlers.endFocus(),t.blur())}click(){this.formElement&&!this.disabled&&(this.formElement.focus(),this.formElement.click())}firstUpdated(){super.firstUpdated(),this.shadowRoot&&this.mdcRoot.addEventListener("change",t=>{this.dispatchEvent(new Event("change",t))})}render(){return kf`
      <div class="mdc-switch">
        <div class="mdc-switch__track"></div>
        <div class="mdc-switch__thumb-underlay">
          ${this.renderRipple()}
          <div class="mdc-switch__thumb">
            <input
              type="checkbox"
              id="basic-switch"
              class="mdc-switch__native-control"
              role="switch"
              aria-label="${ng(this.ariaLabel)}"
              aria-labelledby="${ng(this.ariaLabelledBy)}"
              @change="${this.changeHandler}"
              @focus="${this.handleRippleFocus}"
              @blur="${this.handleRippleBlur}"
              @mousedown="${this.handleRippleMouseDown}"
              @mouseenter="${this.handleRippleMouseEnter}"
              @mouseleave="${this.handleRippleMouseLeave}"
              @touchstart="${this.handleRippleTouchStart}"
              @touchend="${this.handleRippleDeactivate}"
              @touchcancel="${this.handleRippleDeactivate}">
          </div>
        </div>
      </div>`}handleRippleMouseDown(t){const e=()=>{window.removeEventListener("mouseup",e),this.handleRippleDeactivate()};window.addEventListener("mouseup",e),this.rippleHandlers.startPress(t)}handleRippleTouchStart(t){this.rippleHandlers.startPress(t)}handleRippleDeactivate(){this.rippleHandlers.endPress()}handleRippleMouseEnter(){this.rippleHandlers.startHover()}handleRippleMouseLeave(){this.rippleHandlers.endHover()}handleRippleFocus(){this.rippleHandlers.startFocus()}handleRippleBlur(){this.rippleHandlers.endFocus()}}n([Qf({type:Boolean}),os(function(t){this.mdcFoundation.setChecked(t)})],rg.prototype,"checked",void 0),n([Qf({type:Boolean}),os(function(t){this.mdcFoundation.setDisabled(t)})],rg.prototype,"disabled",void 0),n([Vm,Qf({attribute:"aria-label"})],rg.prototype,"ariaLabel",void 0),n([Vm,Qf({attribute:"aria-labelledby"})],rg.prototype,"ariaLabelledBy",void 0),n([ig(".mdc-switch")],rg.prototype,"mdcRoot",void 0),n([ig("input")],rg.prototype,"formElement",void 0),n([function(t){return tg({descriptor:e=>({async get(){var e;return await this.updateComplete,null===(e=this.renderRoot)||void 0===e?void 0:e.querySelector(t)},enumerable:!0,configurable:!0})})}("mwc-ripple")],rg.prototype,"ripple",void 0),n([function(t){return Qf({...t,state:!0})}()],rg.prototype,"shouldRenderRipple",void 0),n([eg({passive:!0})],rg.prototype,"handleRippleMouseDown",null),n([eg({passive:!0})],rg.prototype,"handleRippleTouchStart",null);
/**
     * @license
     * Copyright 2021 Google LLC
     * SPDX-LIcense-Identifier: Apache-2.0
     */
const og=((t,...e)=>{const i=1===t.length?t[0]:e.reduce((e,i,s)=>e+(t=>{if(!0===t._$cssResult$)return t.cssText;if("number"==typeof t)return t;throw Error("Value passed to 'css' function must be a 'css' function result: "+t+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+t[s+1],t[0]);return new Zm(i,t,Km)})`.mdc-switch__thumb-underlay{left:-14px;right:initial;top:-17px;width:48px;height:48px}[dir=rtl] .mdc-switch__thumb-underlay,.mdc-switch__thumb-underlay[dir=rtl]{left:initial;right:-14px}.mdc-switch__native-control{width:64px;height:48px}.mdc-switch{display:inline-block;position:relative;outline:none;user-select:none}.mdc-switch.mdc-switch--checked .mdc-switch__track{background-color:#018786;background-color:var(--mdc-theme-secondary, #018786)}.mdc-switch.mdc-switch--checked .mdc-switch__thumb{background-color:#018786;background-color:var(--mdc-theme-secondary, #018786);border-color:#018786;border-color:var(--mdc-theme-secondary, #018786)}.mdc-switch:not(.mdc-switch--checked) .mdc-switch__track{background-color:#000;background-color:var(--mdc-theme-on-surface, #000)}.mdc-switch:not(.mdc-switch--checked) .mdc-switch__thumb{background-color:#fff;background-color:var(--mdc-theme-surface, #fff);border-color:#fff;border-color:var(--mdc-theme-surface, #fff)}.mdc-switch__native-control{left:0;right:initial;position:absolute;top:0;margin:0;opacity:0;cursor:pointer;pointer-events:auto;transition:transform 90ms cubic-bezier(0.4, 0, 0.2, 1)}[dir=rtl] .mdc-switch__native-control,.mdc-switch__native-control[dir=rtl]{left:initial;right:0}.mdc-switch__track{box-sizing:border-box;width:36px;height:14px;border:1px solid transparent;border-radius:7px;opacity:.38;transition:opacity 90ms cubic-bezier(0.4, 0, 0.2, 1),background-color 90ms cubic-bezier(0.4, 0, 0.2, 1),border-color 90ms cubic-bezier(0.4, 0, 0.2, 1)}.mdc-switch__thumb-underlay{display:flex;position:absolute;align-items:center;justify-content:center;transform:translateX(0);transition:transform 90ms cubic-bezier(0.4, 0, 0.2, 1),background-color 90ms cubic-bezier(0.4, 0, 0.2, 1),border-color 90ms cubic-bezier(0.4, 0, 0.2, 1)}.mdc-switch__thumb{box-shadow:0px 3px 1px -2px rgba(0, 0, 0, 0.2),0px 2px 2px 0px rgba(0, 0, 0, 0.14),0px 1px 5px 0px rgba(0,0,0,.12);box-sizing:border-box;width:20px;height:20px;border:10px solid;border-radius:50%;pointer-events:none;z-index:1}.mdc-switch--checked .mdc-switch__track{opacity:.54}.mdc-switch--checked .mdc-switch__thumb-underlay{transform:translateX(16px)}[dir=rtl] .mdc-switch--checked .mdc-switch__thumb-underlay,.mdc-switch--checked .mdc-switch__thumb-underlay[dir=rtl]{transform:translateX(-16px)}.mdc-switch--checked .mdc-switch__native-control{transform:translateX(-16px)}[dir=rtl] .mdc-switch--checked .mdc-switch__native-control,.mdc-switch--checked .mdc-switch__native-control[dir=rtl]{transform:translateX(16px)}.mdc-switch--disabled{opacity:.38;pointer-events:none}.mdc-switch--disabled .mdc-switch__thumb{border-width:1px}.mdc-switch--disabled .mdc-switch__native-control{cursor:default;pointer-events:none}:host{display:inline-flex;outline:none;-webkit-tap-highlight-color:transparent}`,ag={"mwc-switch":class extends rg{static get styles(){return og}},"mwc-ripple":class extends _u{static get styles(){return Hm}}};
/**
     * @license
     * Copyright 2016 Google Inc.
     *
     * Permission is hereby granted, free of charge, to any person obtaining a copy
     * of this software and associated documentation files (the "Software"), to deal
     * in the Software without restriction, including without limitation the rights
     * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
     * copies of the Software, and to permit persons to whom the Software is
     * furnished to do so, subject to the following conditions:
     *
     * The above copyright notice and this permission notice shall be included in
     * all copies or substantial portions of the Software.
     *
     * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
     * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
     * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
     * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
     * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
     * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
     * THE SOFTWARE.
     */
var lg=function(){function t(t){void 0===t&&(t={}),this.adapter=t}return Object.defineProperty(t,"cssClasses",{get:function(){return{}},enumerable:!1,configurable:!0}),Object.defineProperty(t,"strings",{get:function(){return{}},enumerable:!1,configurable:!0}),Object.defineProperty(t,"numbers",{get:function(){return{}},enumerable:!1,configurable:!0}),Object.defineProperty(t,"defaultAdapter",{get:function(){return{}},enumerable:!1,configurable:!0}),t.prototype.init=function(){},t.prototype.destroy=function(){},t}(),dg={ARIA_CONTROLS:"aria-controls",ARIA_DESCRIBEDBY:"aria-describedby",INPUT_SELECTOR:".mdc-text-field__input",LABEL_SELECTOR:".mdc-floating-label",LEADING_ICON_SELECTOR:".mdc-text-field__icon--leading",LINE_RIPPLE_SELECTOR:".mdc-line-ripple",OUTLINE_SELECTOR:".mdc-notched-outline",PREFIX_SELECTOR:".mdc-text-field__affix--prefix",SUFFIX_SELECTOR:".mdc-text-field__affix--suffix",TRAILING_ICON_SELECTOR:".mdc-text-field__icon--trailing"},cg={DISABLED:"mdc-text-field--disabled",FOCUSED:"mdc-text-field--focused",HELPER_LINE:"mdc-text-field-helper-line",INVALID:"mdc-text-field--invalid",LABEL_FLOATING:"mdc-text-field--label-floating",NO_LABEL:"mdc-text-field--no-label",OUTLINED:"mdc-text-field--outlined",ROOT:"mdc-text-field",TEXTAREA:"mdc-text-field--textarea",WITH_LEADING_ICON:"mdc-text-field--with-leading-icon",WITH_TRAILING_ICON:"mdc-text-field--with-trailing-icon",WITH_INTERNAL_COUNTER:"mdc-text-field--with-internal-counter"},hg={LABEL_SCALE:.75},pg=["pattern","min","max","required","step","minlength","maxlength"],ug=["color","date","datetime-local","month","range","time","week"],mg=["mousedown","touchstart"],fg=["click","keydown"],gg=function(t){function e(i,n){void 0===n&&(n={});var r=t.call(this,s(s({},e.defaultAdapter),i))||this;return r.isFocused=!1,r.receivedUserInput=!1,r.valid=!0,r.useNativeValidation=!0,r.validateOnValueChange=!0,r.helperText=n.helperText,r.characterCounter=n.characterCounter,r.leadingIcon=n.leadingIcon,r.trailingIcon=n.trailingIcon,r.inputFocusHandler=function(){r.activateFocus()},r.inputBlurHandler=function(){r.deactivateFocus()},r.inputInputHandler=function(){r.handleInput()},r.setPointerXOffset=function(t){r.setTransformOrigin(t)},r.textFieldInteractionHandler=function(){r.handleTextFieldInteraction()},r.validationAttributeChangeHandler=function(t){r.handleValidationAttributeChange(t)},r}return i(e,t),Object.defineProperty(e,"cssClasses",{get:function(){return cg},enumerable:!1,configurable:!0}),Object.defineProperty(e,"strings",{get:function(){return dg},enumerable:!1,configurable:!0}),Object.defineProperty(e,"numbers",{get:function(){return hg},enumerable:!1,configurable:!0}),Object.defineProperty(e.prototype,"shouldAlwaysFloat",{get:function(){var t=this.getNativeInput().type;return ug.indexOf(t)>=0},enumerable:!1,configurable:!0}),Object.defineProperty(e.prototype,"shouldFloat",{get:function(){return this.shouldAlwaysFloat||this.isFocused||!!this.getValue()||this.isBadInput()},enumerable:!1,configurable:!0}),Object.defineProperty(e.prototype,"shouldShake",{get:function(){return!this.isFocused&&!this.isValid()&&!!this.getValue()},enumerable:!1,configurable:!0}),Object.defineProperty(e,"defaultAdapter",{get:function(){return{addClass:function(){},removeClass:function(){},hasClass:function(){return!0},setInputAttr:function(){},removeInputAttr:function(){},registerTextFieldInteractionHandler:function(){},deregisterTextFieldInteractionHandler:function(){},registerInputInteractionHandler:function(){},deregisterInputInteractionHandler:function(){},registerValidationAttributeChangeHandler:function(){return new MutationObserver(function(){})},deregisterValidationAttributeChangeHandler:function(){},getNativeInput:function(){return null},isFocused:function(){return!1},activateLineRipple:function(){},deactivateLineRipple:function(){},setLineRippleTransformOrigin:function(){},shakeLabel:function(){},floatLabel:function(){},setLabelRequired:function(){},hasLabel:function(){return!1},getLabelWidth:function(){return 0},hasOutline:function(){return!1},notchOutline:function(){},closeOutline:function(){}}},enumerable:!1,configurable:!0}),e.prototype.init=function(){var t,e,i,s;this.adapter.hasLabel()&&this.getNativeInput().required&&this.adapter.setLabelRequired(!0),this.adapter.isFocused()?this.inputFocusHandler():this.adapter.hasLabel()&&this.shouldFloat&&(this.notchOutline(!0),this.adapter.floatLabel(!0),this.styleFloating(!0)),this.adapter.registerInputInteractionHandler("focus",this.inputFocusHandler),this.adapter.registerInputInteractionHandler("blur",this.inputBlurHandler),this.adapter.registerInputInteractionHandler("input",this.inputInputHandler);try{for(var n=r(mg),o=n.next();!o.done;o=n.next()){var a=o.value;this.adapter.registerInputInteractionHandler(a,this.setPointerXOffset)}}catch(e){t={error:e}}finally{try{o&&!o.done&&(e=n.return)&&e.call(n)}finally{if(t)throw t.error}}try{for(var l=r(fg),d=l.next();!d.done;d=l.next()){a=d.value;this.adapter.registerTextFieldInteractionHandler(a,this.textFieldInteractionHandler)}}catch(t){i={error:t}}finally{try{d&&!d.done&&(s=l.return)&&s.call(l)}finally{if(i)throw i.error}}this.validationObserver=this.adapter.registerValidationAttributeChangeHandler(this.validationAttributeChangeHandler),this.setcharacterCounter(this.getValue().length)},e.prototype.destroy=function(){var t,e,i,s;this.adapter.deregisterInputInteractionHandler("focus",this.inputFocusHandler),this.adapter.deregisterInputInteractionHandler("blur",this.inputBlurHandler),this.adapter.deregisterInputInteractionHandler("input",this.inputInputHandler);try{for(var n=r(mg),o=n.next();!o.done;o=n.next()){var a=o.value;this.adapter.deregisterInputInteractionHandler(a,this.setPointerXOffset)}}catch(e){t={error:e}}finally{try{o&&!o.done&&(e=n.return)&&e.call(n)}finally{if(t)throw t.error}}try{for(var l=r(fg),d=l.next();!d.done;d=l.next()){a=d.value;this.adapter.deregisterTextFieldInteractionHandler(a,this.textFieldInteractionHandler)}}catch(t){i={error:t}}finally{try{d&&!d.done&&(s=l.return)&&s.call(l)}finally{if(i)throw i.error}}this.adapter.deregisterValidationAttributeChangeHandler(this.validationObserver)},e.prototype.handleTextFieldInteraction=function(){var t=this.adapter.getNativeInput();t&&t.disabled||(this.receivedUserInput=!0)},e.prototype.handleValidationAttributeChange=function(t){var e=this;t.some(function(t){return pg.indexOf(t)>-1&&(e.styleValidity(!0),e.adapter.setLabelRequired(e.getNativeInput().required),!0)}),t.indexOf("maxlength")>-1&&this.setcharacterCounter(this.getValue().length)},e.prototype.notchOutline=function(t){if(this.adapter.hasOutline()&&this.adapter.hasLabel())if(t){var e=this.adapter.getLabelWidth()*hg.LABEL_SCALE;this.adapter.notchOutline(e)}else this.adapter.closeOutline()},e.prototype.activateFocus=function(){this.isFocused=!0,this.styleFocused(this.isFocused),this.adapter.activateLineRipple(),this.adapter.hasLabel()&&(this.notchOutline(this.shouldFloat),this.adapter.floatLabel(this.shouldFloat),this.styleFloating(this.shouldFloat),this.adapter.shakeLabel(this.shouldShake)),!this.helperText||!this.helperText.isPersistent()&&this.helperText.isValidation()&&this.valid||this.helperText.showToScreenReader()},e.prototype.setTransformOrigin=function(t){if(!this.isDisabled()&&!this.adapter.hasOutline()){var e=t.touches,i=e?e[0]:t,s=i.target.getBoundingClientRect(),n=i.clientX-s.left;this.adapter.setLineRippleTransformOrigin(n)}},e.prototype.handleInput=function(){this.autoCompleteFocus(),this.setcharacterCounter(this.getValue().length)},e.prototype.autoCompleteFocus=function(){this.receivedUserInput||this.activateFocus()},e.prototype.deactivateFocus=function(){this.isFocused=!1,this.adapter.deactivateLineRipple();var t=this.isValid();this.styleValidity(t),this.styleFocused(this.isFocused),this.adapter.hasLabel()&&(this.notchOutline(this.shouldFloat),this.adapter.floatLabel(this.shouldFloat),this.styleFloating(this.shouldFloat),this.adapter.shakeLabel(this.shouldShake)),this.shouldFloat||(this.receivedUserInput=!1)},e.prototype.getValue=function(){return this.getNativeInput().value},e.prototype.setValue=function(t){if(this.getValue()!==t&&(this.getNativeInput().value=t),this.setcharacterCounter(t.length),this.validateOnValueChange){var e=this.isValid();this.styleValidity(e)}this.adapter.hasLabel()&&(this.notchOutline(this.shouldFloat),this.adapter.floatLabel(this.shouldFloat),this.styleFloating(this.shouldFloat),this.validateOnValueChange&&this.adapter.shakeLabel(this.shouldShake))},e.prototype.isValid=function(){return this.useNativeValidation?this.isNativeInputValid():this.valid},e.prototype.setValid=function(t){this.valid=t,this.styleValidity(t);var e=!t&&!this.isFocused&&!!this.getValue();this.adapter.hasLabel()&&this.adapter.shakeLabel(e)},e.prototype.setValidateOnValueChange=function(t){this.validateOnValueChange=t},e.prototype.getValidateOnValueChange=function(){return this.validateOnValueChange},e.prototype.setUseNativeValidation=function(t){this.useNativeValidation=t},e.prototype.isDisabled=function(){return this.getNativeInput().disabled},e.prototype.setDisabled=function(t){this.getNativeInput().disabled=t,this.styleDisabled(t)},e.prototype.setHelperTextContent=function(t){this.helperText&&this.helperText.setContent(t)},e.prototype.setLeadingIconAriaLabel=function(t){this.leadingIcon&&this.leadingIcon.setAriaLabel(t)},e.prototype.setLeadingIconContent=function(t){this.leadingIcon&&this.leadingIcon.setContent(t)},e.prototype.setTrailingIconAriaLabel=function(t){this.trailingIcon&&this.trailingIcon.setAriaLabel(t)},e.prototype.setTrailingIconContent=function(t){this.trailingIcon&&this.trailingIcon.setContent(t)},e.prototype.setcharacterCounter=function(t){if(this.characterCounter){var e=this.getNativeInput().maxLength;if(-1===e)throw new Error("MDCTextFieldFoundation: Expected maxlength html property on text input or textarea.");this.characterCounter.setCounterValue(t,e)}},e.prototype.isBadInput=function(){return this.getNativeInput().validity.badInput||!1},e.prototype.isNativeInputValid=function(){return this.getNativeInput().validity.valid},e.prototype.styleValidity=function(t){var i=e.cssClasses.INVALID;if(t?this.adapter.removeClass(i):this.adapter.addClass(i),this.helperText){if(this.helperText.setValidity(t),!this.helperText.isValidation())return;var s=this.helperText.isVisible(),n=this.helperText.getId();s&&n?this.adapter.setInputAttr(dg.ARIA_DESCRIBEDBY,n):this.adapter.removeInputAttr(dg.ARIA_DESCRIBEDBY)}},e.prototype.styleFocused=function(t){var i=e.cssClasses.FOCUSED;t?this.adapter.addClass(i):this.adapter.removeClass(i)},e.prototype.styleDisabled=function(t){var i=e.cssClasses,s=i.DISABLED,n=i.INVALID;t?(this.adapter.addClass(s),this.adapter.removeClass(n)):this.adapter.removeClass(s),this.leadingIcon&&this.leadingIcon.setDisabled(t),this.trailingIcon&&this.trailingIcon.setDisabled(t)},e.prototype.styleFloating=function(t){var i=e.cssClasses.LABEL_FLOATING;t?this.adapter.addClass(i):this.adapter.removeClass(i)},e.prototype.getNativeInput=function(){return(this.adapter?this.adapter.getNativeInput():null)||{disabled:!1,maxLength:-1,required:!1,type:"input",validity:{badInput:!1,valid:!0},value:""}},e}(lg);
/**
     * @license
     * Copyright 2016 Google Inc.
     *
     * Permission is hereby granted, free of charge, to any person obtaining a copy
     * of this software and associated documentation files (the "Software"), to deal
     * in the Software without restriction, including without limitation the rights
     * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
     * copies of the Software, and to permit persons to whom the Software is
     * furnished to do so, subject to the following conditions:
     *
     * The above copyright notice and this permission notice shall be included in
     * all copies or substantial portions of the Software.
     *
     * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
     * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
     * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
     * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
     * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
     * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
     * THE SOFTWARE.
     */
/**
     * @license
     * Copyright 2019 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
const vg=window,_g=vg.ShadowRoot&&(void 0===vg.ShadyCSS||vg.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,bg=Symbol(),yg=new WeakMap;let xg=class{constructor(t,e,i){if(this._$cssResult$=!0,i!==bg)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o;const e=this.t;if(_g&&void 0===t){const i=void 0!==e&&1===e.length;i&&(t=yg.get(e)),void 0===t&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),i&&yg.set(e,t))}return t}toString(){return this.cssText}};const $g=_g?t=>t:t=>t instanceof CSSStyleSheet?(t=>{let e="";for(const i of t.cssRules)e+=i.cssText;return(t=>new xg("string"==typeof t?t:t+"",void 0,bg))(e)})(t):t;
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */var wg;const Ag=window,Eg=Ag.trustedTypes,Sg=Eg?Eg.emptyScript:"",Cg=Ag.reactiveElementPolyfillSupport,Tg={toAttribute(t,e){switch(e){case Boolean:t=t?Sg:null;break;case Object:case Array:t=null==t?t:JSON.stringify(t)}return t},fromAttribute(t,e){let i=t;switch(e){case Boolean:i=null!==t;break;case Number:i=null===t?null:Number(t);break;case Object:case Array:try{i=JSON.parse(t)}catch(t){i=null}}return i}},Ig=(t,e)=>e!==t&&(e==e||t==t),Og={attribute:!0,type:String,converter:Tg,reflect:!1,hasChanged:Ig},kg="finalized";let Rg=class extends HTMLElement{constructor(){super(),this._$Ei=new Map,this.isUpdatePending=!1,this.hasUpdated=!1,this._$El=null,this._$Eu()}static addInitializer(t){var e;this.finalize(),(null!==(e=this.h)&&void 0!==e?e:this.h=[]).push(t)}static get observedAttributes(){this.finalize();const t=[];return this.elementProperties.forEach((e,i)=>{const s=this._$Ep(i,e);void 0!==s&&(this._$Ev.set(s,i),t.push(s))}),t}static createProperty(t,e=Og){if(e.state&&(e.attribute=!1),this.finalize(),this.elementProperties.set(t,e),!e.noAccessor&&!this.prototype.hasOwnProperty(t)){const i="symbol"==typeof t?Symbol():"__"+t,s=this.getPropertyDescriptor(t,i,e);void 0!==s&&Object.defineProperty(this.prototype,t,s)}}static getPropertyDescriptor(t,e,i){return{get(){return this[e]},set(s){const n=this[t];this[e]=s,this.requestUpdate(t,n,i)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)||Og}static finalize(){if(this.hasOwnProperty(kg))return!1;this[kg]=!0;const t=Object.getPrototypeOf(this);if(t.finalize(),void 0!==t.h&&(this.h=[...t.h]),this.elementProperties=new Map(t.elementProperties),this._$Ev=new Map,this.hasOwnProperty("properties")){const t=this.properties,e=[...Object.getOwnPropertyNames(t),...Object.getOwnPropertySymbols(t)];for(const i of e)this.createProperty(i,t[i])}return this.elementStyles=this.finalizeStyles(this.styles),!0}static finalizeStyles(t){const e=[];if(Array.isArray(t)){const i=new Set(t.flat(1/0).reverse());for(const t of i)e.unshift($g(t))}else void 0!==t&&e.push($g(t));return e}static _$Ep(t,e){const i=e.attribute;return!1===i?void 0:"string"==typeof i?i:"string"==typeof t?t.toLowerCase():void 0}_$Eu(){var t;this._$E_=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$Eg(),this.requestUpdate(),null===(t=this.constructor.h)||void 0===t||t.forEach(t=>t(this))}addController(t){var e,i;(null!==(e=this._$ES)&&void 0!==e?e:this._$ES=[]).push(t),void 0!==this.renderRoot&&this.isConnected&&(null===(i=t.hostConnected)||void 0===i||i.call(t))}removeController(t){var e;null===(e=this._$ES)||void 0===e||e.splice(this._$ES.indexOf(t)>>>0,1)}_$Eg(){this.constructor.elementProperties.forEach((t,e)=>{this.hasOwnProperty(e)&&(this._$Ei.set(e,this[e]),delete this[e])})}createRenderRoot(){var t;const e=null!==(t=this.shadowRoot)&&void 0!==t?t:this.attachShadow(this.constructor.shadowRootOptions);return((t,e)=>{_g?t.adoptedStyleSheets=e.map(t=>t instanceof CSSStyleSheet?t:t.styleSheet):e.forEach(e=>{const i=document.createElement("style"),s=vg.litNonce;void 0!==s&&i.setAttribute("nonce",s),i.textContent=e.cssText,t.appendChild(i)})})(e,this.constructor.elementStyles),e}connectedCallback(){var t;void 0===this.renderRoot&&(this.renderRoot=this.createRenderRoot()),this.enableUpdating(!0),null===(t=this._$ES)||void 0===t||t.forEach(t=>{var e;return null===(e=t.hostConnected)||void 0===e?void 0:e.call(t)})}enableUpdating(t){}disconnectedCallback(){var t;null===(t=this._$ES)||void 0===t||t.forEach(t=>{var e;return null===(e=t.hostDisconnected)||void 0===e?void 0:e.call(t)})}attributeChangedCallback(t,e,i){this._$AK(t,i)}_$EO(t,e,i=Og){var s;const n=this.constructor._$Ep(t,i);if(void 0!==n&&!0===i.reflect){const r=(void 0!==(null===(s=i.converter)||void 0===s?void 0:s.toAttribute)?i.converter:Tg).toAttribute(e,i.type);this._$El=t,null==r?this.removeAttribute(n):this.setAttribute(n,r),this._$El=null}}_$AK(t,e){var i;const s=this.constructor,n=s._$Ev.get(t);if(void 0!==n&&this._$El!==n){const t=s.getPropertyOptions(n),r="function"==typeof t.converter?{fromAttribute:t.converter}:void 0!==(null===(i=t.converter)||void 0===i?void 0:i.fromAttribute)?t.converter:Tg;this._$El=n,this[n]=r.fromAttribute(e,t.type),this._$El=null}}requestUpdate(t,e,i){let s=!0;void 0!==t&&(((i=i||this.constructor.getPropertyOptions(t)).hasChanged||Ig)(this[t],e)?(this._$AL.has(t)||this._$AL.set(t,e),!0===i.reflect&&this._$El!==t&&(void 0===this._$EC&&(this._$EC=new Map),this._$EC.set(t,i))):s=!1),!this.isUpdatePending&&s&&(this._$E_=this._$Ej())}async _$Ej(){this.isUpdatePending=!0;try{await this._$E_}catch(t){Promise.reject(t)}const t=this.scheduleUpdate();return null!=t&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){var t;if(!this.isUpdatePending)return;this.hasUpdated,this._$Ei&&(this._$Ei.forEach((t,e)=>this[e]=t),this._$Ei=void 0);let e=!1;const i=this._$AL;try{e=this.shouldUpdate(i),e?(this.willUpdate(i),null===(t=this._$ES)||void 0===t||t.forEach(t=>{var e;return null===(e=t.hostUpdate)||void 0===e?void 0:e.call(t)}),this.update(i)):this._$Ek()}catch(t){throw e=!1,this._$Ek(),t}e&&this._$AE(i)}willUpdate(t){}_$AE(t){var e;null===(e=this._$ES)||void 0===e||e.forEach(t=>{var e;return null===(e=t.hostUpdated)||void 0===e?void 0:e.call(t)}),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$Ek(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$E_}shouldUpdate(t){return!0}update(t){void 0!==this._$EC&&(this._$EC.forEach((t,e)=>this._$EO(e,this[e],t)),this._$EC=void 0),this._$Ek()}updated(t){}firstUpdated(t){}};
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
var Pg;Rg[kg]=!0,Rg.elementProperties=new Map,Rg.elementStyles=[],Rg.shadowRootOptions={mode:"open"},null==Cg||Cg({ReactiveElement:Rg}),(null!==(wg=Ag.reactiveElementVersions)&&void 0!==wg?wg:Ag.reactiveElementVersions=[]).push("1.6.3");const Lg=window,Mg=Lg.trustedTypes,Ng=Mg?Mg.createPolicy("lit-html",{createHTML:t=>t}):void 0,Dg="$lit$",Hg=`lit$${(Math.random()+"").slice(9)}$`,Ug="?"+Hg,zg=`<${Ug}>`,Fg=document,Bg=()=>Fg.createComment(""),Vg=t=>null===t||"object"!=typeof t&&"function"!=typeof t,jg=Array.isArray,Wg="[ \t\n\f\r]",qg=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,Yg=/-->/g,Xg=/>/g,Gg=RegExp(`>|${Wg}(?:([^\\s"'>=/]+)(${Wg}*=${Wg}*(?:[^ \t\n\f\r"'\`<>=]|("|')|))|$)`,"g"),Kg=/'/g,Jg=/"/g,Zg=/^(?:script|style|textarea|title)$/i,Qg=(t=>(e,...i)=>({_$litType$:t,strings:e,values:i}))(1),tv=Symbol.for("lit-noChange"),ev=Symbol.for("lit-nothing"),iv=new WeakMap,sv=Fg.createTreeWalker(Fg,129,null,!1);function nv(t,e){if(!Array.isArray(t)||!t.hasOwnProperty("raw"))throw Error("invalid template strings array");return void 0!==Ng?Ng.createHTML(e):e}const rv=(t,e)=>{const i=t.length-1,s=[];let n,r=2===e?"<svg>":"",o=qg;for(let e=0;e<i;e++){const i=t[e];let a,l,d=-1,c=0;for(;c<i.length&&(o.lastIndex=c,l=o.exec(i),null!==l);)c=o.lastIndex,o===qg?"!--"===l[1]?o=Yg:void 0!==l[1]?o=Xg:void 0!==l[2]?(Zg.test(l[2])&&(n=RegExp("</"+l[2],"g")),o=Gg):void 0!==l[3]&&(o=Gg):o===Gg?">"===l[0]?(o=null!=n?n:qg,d=-1):void 0===l[1]?d=-2:(d=o.lastIndex-l[2].length,a=l[1],o=void 0===l[3]?Gg:'"'===l[3]?Jg:Kg):o===Jg||o===Kg?o=Gg:o===Yg||o===Xg?o=qg:(o=Gg,n=void 0);const h=o===Gg&&t[e+1].startsWith("/>")?" ":"";r+=o===qg?i+zg:d>=0?(s.push(a),i.slice(0,d)+Dg+i.slice(d)+Hg+h):i+Hg+(-2===d?(s.push(void 0),e):h)}return[nv(t,r+(t[i]||"<?>")+(2===e?"</svg>":"")),s]};class ov{constructor({strings:t,_$litType$:e},i){let s;this.parts=[];let n=0,r=0;const o=t.length-1,a=this.parts,[l,d]=rv(t,e);if(this.el=ov.createElement(l,i),sv.currentNode=this.el.content,2===e){const t=this.el.content,e=t.firstChild;e.remove(),t.append(...e.childNodes)}for(;null!==(s=sv.nextNode())&&a.length<o;){if(1===s.nodeType){if(s.hasAttributes()){const t=[];for(const e of s.getAttributeNames())if(e.endsWith(Dg)||e.startsWith(Hg)){const i=d[r++];if(t.push(e),void 0!==i){const t=s.getAttribute(i.toLowerCase()+Dg).split(Hg),e=/([.?@])?(.*)/.exec(i);a.push({type:1,index:n,name:e[2],strings:t,ctor:"."===e[1]?hv:"?"===e[1]?uv:"@"===e[1]?mv:cv})}else a.push({type:6,index:n})}for(const e of t)s.removeAttribute(e)}if(Zg.test(s.tagName)){const t=s.textContent.split(Hg),e=t.length-1;if(e>0){s.textContent=Mg?Mg.emptyScript:"";for(let i=0;i<e;i++)s.append(t[i],Bg()),sv.nextNode(),a.push({type:2,index:++n});s.append(t[e],Bg())}}}else if(8===s.nodeType)if(s.data===Ug)a.push({type:2,index:n});else{let t=-1;for(;-1!==(t=s.data.indexOf(Hg,t+1));)a.push({type:7,index:n}),t+=Hg.length-1}n++}}static createElement(t,e){const i=Fg.createElement("template");return i.innerHTML=t,i}}function av(t,e,i=t,s){var n,r,o,a;if(e===tv)return e;let l=void 0!==s?null===(n=i._$Co)||void 0===n?void 0:n[s]:i._$Cl;const d=Vg(e)?void 0:e._$litDirective$;return(null==l?void 0:l.constructor)!==d&&(null===(r=null==l?void 0:l._$AO)||void 0===r||r.call(l,!1),void 0===d?l=void 0:(l=new d(t),l._$AT(t,i,s)),void 0!==s?(null!==(o=(a=i)._$Co)&&void 0!==o?o:a._$Co=[])[s]=l:i._$Cl=l),void 0!==l&&(e=av(t,l._$AS(t,e.values),l,s)),e}class lv{constructor(t,e){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){var e;const{el:{content:i},parts:s}=this._$AD,n=(null!==(e=null==t?void 0:t.creationScope)&&void 0!==e?e:Fg).importNode(i,!0);sv.currentNode=n;let r=sv.nextNode(),o=0,a=0,l=s[0];for(;void 0!==l;){if(o===l.index){let e;2===l.type?e=new dv(r,r.nextSibling,this,t):1===l.type?e=new l.ctor(r,l.name,l.strings,this,t):6===l.type&&(e=new fv(r,this,t)),this._$AV.push(e),l=s[++a]}o!==(null==l?void 0:l.index)&&(r=sv.nextNode(),o++)}return sv.currentNode=Fg,n}v(t){let e=0;for(const i of this._$AV)void 0!==i&&(void 0!==i.strings?(i._$AI(t,i,e),e+=i.strings.length-2):i._$AI(t[e])),e++}}class dv{constructor(t,e,i,s){var n;this.type=2,this._$AH=ev,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=i,this.options=s,this._$Cp=null===(n=null==s?void 0:s.isConnected)||void 0===n||n}get _$AU(){var t,e;return null!==(e=null===(t=this._$AM)||void 0===t?void 0:t._$AU)&&void 0!==e?e:this._$Cp}get parentNode(){let t=this._$AA.parentNode;const e=this._$AM;return void 0!==e&&11===(null==t?void 0:t.nodeType)&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=av(this,t,e),Vg(t)?t===ev||null==t||""===t?(this._$AH!==ev&&this._$AR(),this._$AH=ev):t!==this._$AH&&t!==tv&&this._(t):void 0!==t._$litType$?this.g(t):void 0!==t.nodeType?this.$(t):(t=>jg(t)||"function"==typeof(null==t?void 0:t[Symbol.iterator]))(t)?this.T(t):this._(t)}k(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}$(t){this._$AH!==t&&(this._$AR(),this._$AH=this.k(t))}_(t){this._$AH!==ev&&Vg(this._$AH)?this._$AA.nextSibling.data=t:this.$(Fg.createTextNode(t)),this._$AH=t}g(t){var e;const{values:i,_$litType$:s}=t,n="number"==typeof s?this._$AC(t):(void 0===s.el&&(s.el=ov.createElement(nv(s.h,s.h[0]),this.options)),s);if((null===(e=this._$AH)||void 0===e?void 0:e._$AD)===n)this._$AH.v(i);else{const t=new lv(n,this),e=t.u(this.options);t.v(i),this.$(e),this._$AH=t}}_$AC(t){let e=iv.get(t.strings);return void 0===e&&iv.set(t.strings,e=new ov(t)),e}T(t){jg(this._$AH)||(this._$AH=[],this._$AR());const e=this._$AH;let i,s=0;for(const n of t)s===e.length?e.push(i=new dv(this.k(Bg()),this.k(Bg()),this,this.options)):i=e[s],i._$AI(n),s++;s<e.length&&(this._$AR(i&&i._$AB.nextSibling,s),e.length=s)}_$AR(t=this._$AA.nextSibling,e){var i;for(null===(i=this._$AP)||void 0===i||i.call(this,!1,!0,e);t&&t!==this._$AB;){const e=t.nextSibling;t.remove(),t=e}}setConnected(t){var e;void 0===this._$AM&&(this._$Cp=t,null===(e=this._$AP)||void 0===e||e.call(this,t))}}class cv{constructor(t,e,i,s,n){this.type=1,this._$AH=ev,this._$AN=void 0,this.element=t,this.name=e,this._$AM=s,this.options=n,i.length>2||""!==i[0]||""!==i[1]?(this._$AH=Array(i.length-1).fill(new String),this.strings=i):this._$AH=ev}get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}_$AI(t,e=this,i,s){const n=this.strings;let r=!1;if(void 0===n)t=av(this,t,e,0),r=!Vg(t)||t!==this._$AH&&t!==tv,r&&(this._$AH=t);else{const s=t;let o,a;for(t=n[0],o=0;o<n.length-1;o++)a=av(this,s[i+o],e,o),a===tv&&(a=this._$AH[o]),r||(r=!Vg(a)||a!==this._$AH[o]),a===ev?t=ev:t!==ev&&(t+=(null!=a?a:"")+n[o+1]),this._$AH[o]=a}r&&!s&&this.j(t)}j(t){t===ev?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,null!=t?t:"")}}class hv extends cv{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===ev?void 0:t}}const pv=Mg?Mg.emptyScript:"";class uv extends cv{constructor(){super(...arguments),this.type=4}j(t){t&&t!==ev?this.element.setAttribute(this.name,pv):this.element.removeAttribute(this.name)}}class mv extends cv{constructor(t,e,i,s,n){super(t,e,i,s,n),this.type=5}_$AI(t,e=this){var i;if((t=null!==(i=av(this,t,e,0))&&void 0!==i?i:ev)===tv)return;const s=this._$AH,n=t===ev&&s!==ev||t.capture!==s.capture||t.once!==s.once||t.passive!==s.passive,r=t!==ev&&(s===ev||n);n&&this.element.removeEventListener(this.name,this,s),r&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){var e,i;"function"==typeof this._$AH?this._$AH.call(null!==(i=null===(e=this.options)||void 0===e?void 0:e.host)&&void 0!==i?i:this.element,t):this._$AH.handleEvent(t)}}class fv{constructor(t,e,i){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=i}get _$AU(){return this._$AM._$AU}_$AI(t){av(this,t)}}const gv=Lg.litHtmlPolyfillSupport;null==gv||gv(ov,dv),(null!==(Pg=Lg.litHtmlVersions)&&void 0!==Pg?Pg:Lg.litHtmlVersions=[]).push("2.8.0");
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
var vv,_v;let bv=class extends Rg{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){var t,e;const i=super.createRenderRoot();return null!==(t=(e=this.renderOptions).renderBefore)&&void 0!==t||(e.renderBefore=i.firstChild),i}update(t){const e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=((t,e,i)=>{var s,n;const r=null!==(s=null==i?void 0:i.renderBefore)&&void 0!==s?s:e;let o=r._$litPart$;if(void 0===o){const t=null!==(n=null==i?void 0:i.renderBefore)&&void 0!==n?n:null;r._$litPart$=o=new dv(e.insertBefore(Bg(),t),t,void 0,null!=i?i:{})}return o._$AI(t),o})(e,this.renderRoot,this.renderOptions)}connectedCallback(){var t;super.connectedCallback(),null===(t=this._$Do)||void 0===t||t.setConnected(!0)}disconnectedCallback(){var t;super.disconnectedCallback(),null===(t=this._$Do)||void 0===t||t.setConnected(!1)}render(){return tv}};bv.finalized=!0,bv._$litElement$=!0,null===(vv=globalThis.litElementHydrateSupport)||void 0===vv||vv.call(globalThis,{LitElement:bv});const yv=globalThis.litElementPolyfillSupport;null==yv||yv({LitElement:bv}),(null!==(_v=globalThis.litElementVersions)&&void 0!==_v?_v:globalThis.litElementVersions=[]).push("3.3.3");
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
const xv=(t,e)=>"method"===e.kind&&e.descriptor&&!("value"in e.descriptor)?{...e,finisher(i){i.createProperty(e.key,t)}}:{kind:"field",key:Symbol(),placement:"own",descriptor:{},originalKey:e.key,initializer(){"function"==typeof e.initializer&&(this[e.key]=e.initializer.call(this))},finisher(i){i.createProperty(e.key,t)}};function $v(t){return(e,i)=>void 0!==i?((t,e,i)=>{e.constructor.createProperty(i,t)})(t,e,i):xv(t,e)}
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */function wv(t){return $v({...t,state:!0})}
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */const Av=({finisher:t,descriptor:e})=>(i,s)=>{var n;if(void 0===s){const s=null!==(n=i.originalKey)&&void 0!==n?n:i.key,r=null!=e?{kind:"method",placement:"prototype",key:s,descriptor:e(i.key)}:{...i,key:s};return null!=t&&(r.finisher=function(e){t(e,s)}),r}{const n=i.constructor;void 0!==e&&Object.defineProperty(i,s,e(s)),null==t||t(n,s)}};
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
function Ev(t,e){return Av({descriptor:e=>{const i={get(){var e,i;return null!==(i=null===(e=this.renderRoot)||void 0===e?void 0:e.querySelector(t))&&void 0!==i?i:null},enumerable:!0,configurable:!0};return i}})}
/**
     * @license
     * Copyright 2021 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */var Sv;null===(Sv=window.HTMLSlotElement)||void 0===Sv||Sv.prototype.assignedElements;
/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
const Cv=1,Tv=3,Iv=4,Ov=t=>(...e)=>({_$litDirective$:t,values:e});class kv{constructor(t){}get _$AU(){return this._$AM._$AU}_$AT(t,e,i){this._$Ct=t,this._$AM=e,this._$Ci=i}_$AS(t,e){return this.update(t,e)}update(t,e){return this.render(...e)}}
/**
     * @license
     * Copyright 2018 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */const Rv=Ov(class extends kv{constructor(t){var e;if(super(t),t.type!==Cv||"class"!==t.name||(null===(e=t.strings)||void 0===e?void 0:e.length)>2)throw Error("`classMap()` can only be used in the `class` attribute and must be the only part in the attribute.")}render(t){return" "+Object.keys(t).filter(e=>t[e]).join(" ")+" "}update(t,[e]){var i,s;if(void 0===this.it){this.it=new Set,void 0!==t.strings&&(this.nt=new Set(t.strings.join(" ").split(/\s/).filter(t=>""!==t)));for(const t in e)e[t]&&!(null===(i=this.nt)||void 0===i?void 0:i.has(t))&&this.it.add(t);return this.render(e)}const n=t.element.classList;this.it.forEach(t=>{t in e||(n.remove(t),this.it.delete(t))});for(const t in e){const i=!!e[t];i===this.it.has(t)||(null===(s=this.nt)||void 0===s?void 0:s.has(t))||(i?(n.add(t),this.it.add(t)):(n.remove(t),this.it.delete(t)))}return tv}}),Pv=t=>null!=t?t:ev,Lv={},Mv=Ov(class extends kv{constructor(t){if(super(t),t.type!==Tv&&t.type!==Cv&&t.type!==Iv)throw Error("The `live` directive is not allowed on child or event bindings");if(!(t=>void 0===t.strings)(t))throw Error("`live` bindings can only contain a single expression")}render(t){return t}update(t,[e]){if(e===tv||e===ev)return e;const i=t.element,s=t.name;if(t.type===Tv){if(e===i[s])return tv}else if(t.type===Iv){if(!!e===i.hasAttribute(s))return tv}else if(t.type===Cv&&i.getAttribute(s)===e+"")return tv;return((t,e=Lv)=>{t._$AH=e;
/**
     * @license
     * Copyright 2020 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */})(t),e}}),Nv=["touchstart","touchmove","scroll","mousewheel"],Dv=(t={})=>{const e={};for(const i in t)e[i]=t[i];return Object.assign({badInput:!1,customError:!1,patternMismatch:!1,rangeOverflow:!1,rangeUnderflow:!1,stepMismatch:!1,tooLong:!1,tooShort:!1,typeMismatch:!1,valid:!0,valueMissing:!1},e)};
/**
     * @license
     * Copyright 2018 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */class Hv extends rs{constructor(){super(...arguments),this.mdcFoundationClass=gg,this.value="",this.type="text",this.placeholder="",this.label="",this.icon="",this.iconTrailing="",this.disabled=!1,this.required=!1,this.minLength=-1,this.maxLength=-1,this.outlined=!1,this.helper="",this.validateOnInitialRender=!1,this.validationMessage="",this.autoValidate=!1,this.pattern="",this.min="",this.max="",this.step=null,this.size=null,this.helperPersistent=!1,this.charCounter=!1,this.endAligned=!1,this.prefix="",this.suffix="",this.name="",this.readOnly=!1,this.autocapitalize="",this.outlineOpen=!1,this.outlineWidth=0,this.isUiValid=!0,this.focused=!1,this._validity=Dv(),this.validityTransform=null}get validity(){return this._checkValidity(this.value),this._validity}get willValidate(){return this.formElement.willValidate}get selectionStart(){return this.formElement.selectionStart}get selectionEnd(){return this.formElement.selectionEnd}focus(){const t=new CustomEvent("focus");this.formElement.dispatchEvent(t),this.formElement.focus()}blur(){const t=new CustomEvent("blur");this.formElement.dispatchEvent(t),this.formElement.blur()}select(){this.formElement.select()}setSelectionRange(t,e,i){this.formElement.setSelectionRange(t,e,i)}update(t){t.has("autoValidate")&&this.mdcFoundation&&this.mdcFoundation.setValidateOnValueChange(this.autoValidate),t.has("value")&&"string"!=typeof this.value&&(this.value=`${this.value}`),super.update(t)}setFormData(t){this.name&&t.append(this.name,this.value)}render(){const t=this.charCounter&&-1!==this.maxLength,e=!!this.helper||!!this.validationMessage||t,i={"mdc-text-field--disabled":this.disabled,"mdc-text-field--no-label":!this.label,"mdc-text-field--filled":!this.outlined,"mdc-text-field--outlined":this.outlined,"mdc-text-field--with-leading-icon":this.icon,"mdc-text-field--with-trailing-icon":this.iconTrailing,"mdc-text-field--end-aligned":this.endAligned};return Qg`
      <label class="mdc-text-field ${Rv(i)}">
        ${this.renderRipple()}
        ${this.outlined?this.renderOutline():this.renderLabel()}
        ${this.renderLeadingIcon()}
        ${this.renderPrefix()}
        ${this.renderInput(e)}
        ${this.renderSuffix()}
        ${this.renderTrailingIcon()}
        ${this.renderLineRipple()}
      </label>
      ${this.renderHelperText(e,t)}
    `}updated(t){t.has("value")&&void 0!==t.get("value")&&(this.mdcFoundation.setValue(this.value),this.autoValidate&&this.reportValidity())}renderRipple(){return this.outlined?"":Qg`
      <span class="mdc-text-field__ripple"></span>
    `}renderOutline(){return this.outlined?Qg`
      <mwc-notched-outline
          .width=${this.outlineWidth}
          .open=${this.outlineOpen}
          class="mdc-notched-outline">
        ${this.renderLabel()}
      </mwc-notched-outline>`:""}renderLabel(){return this.label?Qg`
      <span
          .floatingLabelFoundation=${no(this.label)}
          id="label">${this.label}</span>
    `:""}renderLeadingIcon(){return this.icon?this.renderIcon(this.icon):""}renderTrailingIcon(){return this.iconTrailing?this.renderIcon(this.iconTrailing,!0):""}renderIcon(t,e=!1){return Qg`<i class="material-icons mdc-text-field__icon ${Rv({"mdc-text-field__icon--leading":!e,"mdc-text-field__icon--trailing":e})}">${t}</i>`}renderPrefix(){return this.prefix?this.renderAffix(this.prefix):""}renderSuffix(){return this.suffix?this.renderAffix(this.suffix,!0):""}renderAffix(t,e=!1){return Qg`<span class="mdc-text-field__affix ${Rv({"mdc-text-field__affix--prefix":!e,"mdc-text-field__affix--suffix":e})}">
        ${t}</span>`}renderInput(t){const e=-1===this.minLength?void 0:this.minLength,i=-1===this.maxLength?void 0:this.maxLength,s=this.autocapitalize?this.autocapitalize:void 0,n=this.validationMessage&&!this.isUiValid,r=this.label?"label":void 0,o=t?"helper-text":void 0,a=this.focused||this.helperPersistent||n?"helper-text":void 0;return Qg`
      <input
          aria-labelledby=${Pv(r)}
          aria-controls="${Pv(o)}"
          aria-describedby="${Pv(a)}"
          class="mdc-text-field__input"
          type="${this.type}"
          .value="${Mv(this.value)}"
          ?disabled="${this.disabled}"
          placeholder="${this.placeholder}"
          ?required="${this.required}"
          ?readonly="${this.readOnly}"
          minlength="${Pv(e)}"
          maxlength="${Pv(i)}"
          pattern="${Pv(this.pattern?this.pattern:void 0)}"
          min="${Pv(""===this.min?void 0:this.min)}"
          max="${Pv(""===this.max?void 0:this.max)}"
          step="${Pv(null===this.step?void 0:this.step)}"
          size="${Pv(null===this.size?void 0:this.size)}"
          name="${Pv(""===this.name?void 0:this.name)}"
          inputmode="${Pv(this.inputMode)}"
          autocapitalize="${Pv(s)}"
          @input="${this.handleInputChange}"
          @focus="${this.onInputFocus}"
          @blur="${this.onInputBlur}">`}renderLineRipple(){return this.outlined?"":Qg`
      <span .lineRippleFoundation=${po()}></span>
    `}renderHelperText(t,e){const i=this.validationMessage&&!this.isUiValid,s={"mdc-text-field-helper-text--persistent":this.helperPersistent,"mdc-text-field-helper-text--validation-msg":i},n=this.focused||this.helperPersistent||i?void 0:"true",r=i?this.validationMessage:this.helper;return t?Qg`
      <div class="mdc-text-field-helper-line">
        <div id="helper-text"
             aria-hidden="${Pv(n)}"
             class="mdc-text-field-helper-text ${Rv(s)}"
             >${r}</div>
        ${this.renderCharCounter(e)}
      </div>`:""}renderCharCounter(t){const e=Math.min(this.value.length,this.maxLength);return t?Qg`
      <span class="mdc-text-field-character-counter"
            >${e} / ${this.maxLength}</span>`:""}onInputFocus(){this.focused=!0}onInputBlur(){this.focused=!1,this.reportValidity()}checkValidity(){const t=this._checkValidity(this.value);if(!t){const t=new Event("invalid",{bubbles:!1,cancelable:!0});this.dispatchEvent(t)}return t}reportValidity(){const t=this.checkValidity();return this.mdcFoundation.setValid(t),this.isUiValid=t,t}_checkValidity(t){const e=this.formElement.validity;let i=Dv(e);if(this.validityTransform){const e=this.validityTransform(t,i);i=Object.assign(Object.assign({},i),e),this.mdcFoundation.setUseNativeValidation(!1)}else this.mdcFoundation.setUseNativeValidation(!0);return this._validity=i,this._validity.valid}setCustomValidity(t){this.validationMessage=t,this.formElement.setCustomValidity(t)}handleInputChange(){this.value=this.formElement.value}createAdapter(){return Object.assign(Object.assign(Object.assign(Object.assign(Object.assign({},this.getRootAdapterMethods()),this.getInputAdapterMethods()),this.getLabelAdapterMethods()),this.getLineRippleAdapterMethods()),this.getOutlineAdapterMethods())}getRootAdapterMethods(){return Object.assign({registerTextFieldInteractionHandler:(t,e)=>this.addEventListener(t,e),deregisterTextFieldInteractionHandler:(t,e)=>this.removeEventListener(t,e),registerValidationAttributeChangeHandler:t=>{const e=new MutationObserver(e=>{t((t=>t.map(t=>t.attributeName).filter(t=>t))(e))});return e.observe(this.formElement,{attributes:!0}),e},deregisterValidationAttributeChangeHandler:t=>t.disconnect()},Xi(this.mdcRoot))}getInputAdapterMethods(){return{getNativeInput:()=>this.formElement,setInputAttr:()=>{},removeInputAttr:()=>{},isFocused:()=>!!this.shadowRoot&&this.shadowRoot.activeElement===this.formElement,registerInputInteractionHandler:(t,e)=>this.formElement.addEventListener(t,e,{passive:t in Nv}),deregisterInputInteractionHandler:(t,e)=>this.formElement.removeEventListener(t,e)}}getLabelAdapterMethods(){return{floatLabel:t=>this.labelElement&&this.labelElement.floatingLabelFoundation.float(t),getLabelWidth:()=>this.labelElement?this.labelElement.floatingLabelFoundation.getWidth():0,hasLabel:()=>Boolean(this.labelElement),shakeLabel:t=>this.labelElement&&this.labelElement.floatingLabelFoundation.shake(t),setLabelRequired:t=>{this.labelElement&&this.labelElement.floatingLabelFoundation.setRequired(t)}}}getLineRippleAdapterMethods(){return{activateLineRipple:()=>{this.lineRippleElement&&this.lineRippleElement.lineRippleFoundation.activate()},deactivateLineRipple:()=>{this.lineRippleElement&&this.lineRippleElement.lineRippleFoundation.deactivate()},setLineRippleTransformOrigin:t=>{this.lineRippleElement&&this.lineRippleElement.lineRippleFoundation.setRippleCenter(t)}}}async getUpdateComplete(){var t;const e=await super.getUpdateComplete();return await(null===(t=this.outlineElement)||void 0===t?void 0:t.updateComplete),e}firstUpdated(){var t;super.firstUpdated(),this.mdcFoundation.setValidateOnValueChange(this.autoValidate),this.validateOnInitialRender&&this.reportValidity(),null===(t=this.outlineElement)||void 0===t||t.updateComplete.then(()=>{var t;this.outlineWidth=(null===(t=this.labelElement)||void 0===t?void 0:t.floatingLabelFoundation.getWidth())||0})}getOutlineAdapterMethods(){return{closeOutline:()=>this.outlineElement&&(this.outlineOpen=!1),hasOutline:()=>Boolean(this.outlineElement),notchOutline:t=>{this.outlineElement&&!this.outlineOpen&&(this.outlineWidth=t,this.outlineOpen=!0)}}}async layout(){await this.updateComplete;const t=this.labelElement;if(!t)return void(this.outlineOpen=!1);const e=!!this.label&&!!this.value;if(t.floatingLabelFoundation.float(e),!this.outlined)return;this.outlineOpen=e,await this.updateComplete;const i=t.floatingLabelFoundation.getWidth();this.outlineOpen&&(this.outlineWidth=i,await this.updateComplete)}}n([Ev(".mdc-text-field")],Hv.prototype,"mdcRoot",void 0),n([Ev("input")],Hv.prototype,"formElement",void 0),n([Ev(".mdc-floating-label")],Hv.prototype,"labelElement",void 0),n([Ev(".mdc-line-ripple")],Hv.prototype,"lineRippleElement",void 0),n([Ev("mwc-notched-outline")],Hv.prototype,"outlineElement",void 0),n([Ev(".mdc-notched-outline__notch")],Hv.prototype,"notchElement",void 0),n([$v({type:String})],Hv.prototype,"value",void 0),n([$v({type:String})],Hv.prototype,"type",void 0),n([$v({type:String})],Hv.prototype,"placeholder",void 0),n([$v({type:String}),os(function(t,e){void 0!==e&&this.label!==e&&this.layout()})],Hv.prototype,"label",void 0),n([$v({type:String})],Hv.prototype,"icon",void 0),n([$v({type:String})],Hv.prototype,"iconTrailing",void 0),n([$v({type:Boolean,reflect:!0})],Hv.prototype,"disabled",void 0),n([$v({type:Boolean})],Hv.prototype,"required",void 0),n([$v({type:Number})],Hv.prototype,"minLength",void 0),n([$v({type:Number})],Hv.prototype,"maxLength",void 0),n([$v({type:Boolean,reflect:!0}),os(function(t,e){void 0!==e&&this.outlined!==e&&this.layout()})],Hv.prototype,"outlined",void 0),n([$v({type:String})],Hv.prototype,"helper",void 0),n([$v({type:Boolean})],Hv.prototype,"validateOnInitialRender",void 0),n([$v({type:String})],Hv.prototype,"validationMessage",void 0),n([$v({type:Boolean})],Hv.prototype,"autoValidate",void 0),n([$v({type:String})],Hv.prototype,"pattern",void 0),n([$v({type:String})],Hv.prototype,"min",void 0),n([$v({type:String})],Hv.prototype,"max",void 0),n([$v({type:String})],Hv.prototype,"step",void 0),n([$v({type:Number})],Hv.prototype,"size",void 0),n([$v({type:Boolean})],Hv.prototype,"helperPersistent",void 0),n([$v({type:Boolean})],Hv.prototype,"charCounter",void 0),n([$v({type:Boolean})],Hv.prototype,"endAligned",void 0),n([$v({type:String})],Hv.prototype,"prefix",void 0),n([$v({type:String})],Hv.prototype,"suffix",void 0),n([$v({type:String})],Hv.prototype,"name",void 0),n([$v({type:String})],Hv.prototype,"inputMode",void 0),n([$v({type:Boolean})],Hv.prototype,"readOnly",void 0),n([$v({type:String})],Hv.prototype,"autocapitalize",void 0),n([wv()],Hv.prototype,"outlineOpen",void 0),n([wv()],Hv.prototype,"outlineWidth",void 0),n([wv()],Hv.prototype,"isUiValid",void 0),n([wv()],Hv.prototype,"focused",void 0),n([function(t){return Av({finisher:(e,i)=>{Object.assign(e.prototype[i],t)}})}({passive:!0})],Hv.prototype,"handleInputChange",null);
/**
     * @license
     * Copyright 2021 Google LLC
     * SPDX-LIcense-Identifier: Apache-2.0
     */
const Uv=((t,...e)=>{const i=1===t.length?t[0]:e.reduce((e,i,s)=>e+(t=>{if(!0===t._$cssResult$)return t.cssText;if("number"==typeof t)return t;throw Error("Value passed to 'css' function must be a 'css' function result: "+t+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+t[s+1],t[0]);return new xg(i,t,bg)})`.mdc-floating-label{-moz-osx-font-smoothing:grayscale;-webkit-font-smoothing:antialiased;font-family:Roboto, sans-serif;font-family:var(--mdc-typography-subtitle1-font-family, var(--mdc-typography-font-family, Roboto, sans-serif));font-size:1rem;font-size:var(--mdc-typography-subtitle1-font-size, 1rem);font-weight:400;font-weight:var(--mdc-typography-subtitle1-font-weight, 400);letter-spacing:0.009375em;letter-spacing:var(--mdc-typography-subtitle1-letter-spacing, 0.009375em);text-decoration:inherit;text-decoration:var(--mdc-typography-subtitle1-text-decoration, inherit);text-transform:inherit;text-transform:var(--mdc-typography-subtitle1-text-transform, inherit);position:absolute;left:0;-webkit-transform-origin:left top;transform-origin:left top;line-height:1.15rem;text-align:left;text-overflow:ellipsis;white-space:nowrap;cursor:text;overflow:hidden;will-change:transform;transition:transform 150ms cubic-bezier(0.4, 0, 0.2, 1),color 150ms cubic-bezier(0.4, 0, 0.2, 1)}[dir=rtl] .mdc-floating-label,.mdc-floating-label[dir=rtl]{right:0;left:auto;-webkit-transform-origin:right top;transform-origin:right top;text-align:right}.mdc-floating-label--float-above{cursor:auto}.mdc-floating-label--required::after{margin-left:1px;margin-right:0px;content:"*"}[dir=rtl] .mdc-floating-label--required::after,.mdc-floating-label--required[dir=rtl]::after{margin-left:0;margin-right:1px}.mdc-floating-label--float-above{transform:translateY(-106%) scale(0.75)}.mdc-floating-label--shake{animation:mdc-floating-label-shake-float-above-standard 250ms 1}@keyframes mdc-floating-label-shake-float-above-standard{0%{transform:translateX(calc(0 - 0%)) translateY(-106%) scale(0.75)}33%{animation-timing-function:cubic-bezier(0.5, 0, 0.701732, 0.495819);transform:translateX(calc(4% - 0%)) translateY(-106%) scale(0.75)}66%{animation-timing-function:cubic-bezier(0.302435, 0.381352, 0.55, 0.956352);transform:translateX(calc(-4% - 0%)) translateY(-106%) scale(0.75)}100%{transform:translateX(calc(0 - 0%)) translateY(-106%) scale(0.75)}}.mdc-line-ripple::before,.mdc-line-ripple::after{position:absolute;bottom:0;left:0;width:100%;border-bottom-style:solid;content:""}.mdc-line-ripple::before{border-bottom-width:1px}.mdc-line-ripple::before{z-index:1}.mdc-line-ripple::after{transform:scaleX(0);border-bottom-width:2px;opacity:0;z-index:2}.mdc-line-ripple::after{transition:transform 180ms cubic-bezier(0.4, 0, 0.2, 1),opacity 180ms cubic-bezier(0.4, 0, 0.2, 1)}.mdc-line-ripple--active::after{transform:scaleX(1);opacity:1}.mdc-line-ripple--deactivating::after{opacity:0}.mdc-notched-outline{display:flex;position:absolute;top:0;right:0;left:0;box-sizing:border-box;width:100%;max-width:100%;height:100%;text-align:left;pointer-events:none}[dir=rtl] .mdc-notched-outline,.mdc-notched-outline[dir=rtl]{text-align:right}.mdc-notched-outline__leading,.mdc-notched-outline__notch,.mdc-notched-outline__trailing{box-sizing:border-box;height:100%;border-top:1px solid;border-bottom:1px solid;pointer-events:none}.mdc-notched-outline__leading{border-left:1px solid;border-right:none;width:12px}[dir=rtl] .mdc-notched-outline__leading,.mdc-notched-outline__leading[dir=rtl]{border-left:none;border-right:1px solid}.mdc-notched-outline__trailing{border-left:none;border-right:1px solid;flex-grow:1}[dir=rtl] .mdc-notched-outline__trailing,.mdc-notched-outline__trailing[dir=rtl]{border-left:1px solid;border-right:none}.mdc-notched-outline__notch{flex:0 0 auto;width:auto;max-width:calc(100% - 12px * 2)}.mdc-notched-outline .mdc-floating-label{display:inline-block;position:relative;max-width:100%}.mdc-notched-outline .mdc-floating-label--float-above{text-overflow:clip}.mdc-notched-outline--upgraded .mdc-floating-label--float-above{max-width:calc(100% / 0.75)}.mdc-notched-outline--notched .mdc-notched-outline__notch{padding-left:0;padding-right:8px;border-top:none}[dir=rtl] .mdc-notched-outline--notched .mdc-notched-outline__notch,.mdc-notched-outline--notched .mdc-notched-outline__notch[dir=rtl]{padding-left:8px;padding-right:0}.mdc-notched-outline--no-label .mdc-notched-outline__notch{display:none}@keyframes mdc-ripple-fg-radius-in{from{animation-timing-function:cubic-bezier(0.4, 0, 0.2, 1);transform:translate(var(--mdc-ripple-fg-translate-start, 0)) scale(1)}to{transform:translate(var(--mdc-ripple-fg-translate-end, 0)) scale(var(--mdc-ripple-fg-scale, 1))}}@keyframes mdc-ripple-fg-opacity-in{from{animation-timing-function:linear;opacity:0}to{opacity:var(--mdc-ripple-fg-opacity, 0)}}@keyframes mdc-ripple-fg-opacity-out{from{animation-timing-function:linear;opacity:var(--mdc-ripple-fg-opacity, 0)}to{opacity:0}}.mdc-text-field--filled{--mdc-ripple-fg-size: 0;--mdc-ripple-left: 0;--mdc-ripple-top: 0;--mdc-ripple-fg-scale: 1;--mdc-ripple-fg-translate-end: 0;--mdc-ripple-fg-translate-start: 0;-webkit-tap-highlight-color:rgba(0,0,0,0);will-change:transform,opacity}.mdc-text-field--filled .mdc-text-field__ripple::before,.mdc-text-field--filled .mdc-text-field__ripple::after{position:absolute;border-radius:50%;opacity:0;pointer-events:none;content:""}.mdc-text-field--filled .mdc-text-field__ripple::before{transition:opacity 15ms linear,background-color 15ms linear;z-index:1;z-index:var(--mdc-ripple-z-index, 1)}.mdc-text-field--filled .mdc-text-field__ripple::after{z-index:0;z-index:var(--mdc-ripple-z-index, 0)}.mdc-text-field--filled.mdc-ripple-upgraded .mdc-text-field__ripple::before{transform:scale(var(--mdc-ripple-fg-scale, 1))}.mdc-text-field--filled.mdc-ripple-upgraded .mdc-text-field__ripple::after{top:0;left:0;transform:scale(0);transform-origin:center center}.mdc-text-field--filled.mdc-ripple-upgraded--unbounded .mdc-text-field__ripple::after{top:var(--mdc-ripple-top, 0);left:var(--mdc-ripple-left, 0)}.mdc-text-field--filled.mdc-ripple-upgraded--foreground-activation .mdc-text-field__ripple::after{animation:mdc-ripple-fg-radius-in 225ms forwards,mdc-ripple-fg-opacity-in 75ms forwards}.mdc-text-field--filled.mdc-ripple-upgraded--foreground-deactivation .mdc-text-field__ripple::after{animation:mdc-ripple-fg-opacity-out 150ms;transform:translate(var(--mdc-ripple-fg-translate-end, 0)) scale(var(--mdc-ripple-fg-scale, 1))}.mdc-text-field--filled .mdc-text-field__ripple::before,.mdc-text-field--filled .mdc-text-field__ripple::after{top:calc(50% - 100%);left:calc(50% - 100%);width:200%;height:200%}.mdc-text-field--filled.mdc-ripple-upgraded .mdc-text-field__ripple::after{width:var(--mdc-ripple-fg-size, 100%);height:var(--mdc-ripple-fg-size, 100%)}.mdc-text-field__ripple{position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none}.mdc-text-field{border-top-left-radius:4px;border-top-left-radius:var(--mdc-shape-small, 4px);border-top-right-radius:4px;border-top-right-radius:var(--mdc-shape-small, 4px);border-bottom-right-radius:0;border-bottom-left-radius:0;display:inline-flex;align-items:baseline;padding:0 16px;position:relative;box-sizing:border-box;overflow:hidden;will-change:opacity,transform,color}.mdc-text-field:not(.mdc-text-field--disabled) .mdc-floating-label{color:rgba(0, 0, 0, 0.6)}.mdc-text-field:not(.mdc-text-field--disabled) .mdc-text-field__input{color:rgba(0, 0, 0, 0.87)}@media all{.mdc-text-field:not(.mdc-text-field--disabled) .mdc-text-field__input::placeholder{color:rgba(0, 0, 0, 0.54)}}@media all{.mdc-text-field:not(.mdc-text-field--disabled) .mdc-text-field__input:-ms-input-placeholder{color:rgba(0, 0, 0, 0.54)}}.mdc-text-field .mdc-text-field__input{caret-color:#6200ee;caret-color:var(--mdc-theme-primary, #6200ee)}.mdc-text-field:not(.mdc-text-field--disabled)+.mdc-text-field-helper-line .mdc-text-field-helper-text{color:rgba(0, 0, 0, 0.6)}.mdc-text-field:not(.mdc-text-field--disabled) .mdc-text-field-character-counter,.mdc-text-field:not(.mdc-text-field--disabled)+.mdc-text-field-helper-line .mdc-text-field-character-counter{color:rgba(0, 0, 0, 0.6)}.mdc-text-field:not(.mdc-text-field--disabled) .mdc-text-field__icon--leading{color:rgba(0, 0, 0, 0.54)}.mdc-text-field:not(.mdc-text-field--disabled) .mdc-text-field__icon--trailing{color:rgba(0, 0, 0, 0.54)}.mdc-text-field:not(.mdc-text-field--disabled) .mdc-text-field__affix--prefix{color:rgba(0, 0, 0, 0.6)}.mdc-text-field:not(.mdc-text-field--disabled) .mdc-text-field__affix--suffix{color:rgba(0, 0, 0, 0.6)}.mdc-text-field .mdc-floating-label{top:50%;transform:translateY(-50%);pointer-events:none}.mdc-text-field__input{-moz-osx-font-smoothing:grayscale;-webkit-font-smoothing:antialiased;font-family:Roboto, sans-serif;font-family:var(--mdc-typography-subtitle1-font-family, var(--mdc-typography-font-family, Roboto, sans-serif));font-size:1rem;font-size:var(--mdc-typography-subtitle1-font-size, 1rem);font-weight:400;font-weight:var(--mdc-typography-subtitle1-font-weight, 400);letter-spacing:0.009375em;letter-spacing:var(--mdc-typography-subtitle1-letter-spacing, 0.009375em);text-decoration:inherit;text-decoration:var(--mdc-typography-subtitle1-text-decoration, inherit);text-transform:inherit;text-transform:var(--mdc-typography-subtitle1-text-transform, inherit);height:28px;transition:opacity 150ms 0ms cubic-bezier(0.4, 0, 0.2, 1);width:100%;min-width:0;border:none;border-radius:0;background:none;appearance:none;padding:0}.mdc-text-field__input::-ms-clear{display:none}.mdc-text-field__input::-webkit-calendar-picker-indicator{display:none}.mdc-text-field__input:focus{outline:none}.mdc-text-field__input:invalid{box-shadow:none}@media all{.mdc-text-field__input::placeholder{transition:opacity 67ms 0ms cubic-bezier(0.4, 0, 0.2, 1);opacity:0}}@media all{.mdc-text-field__input:-ms-input-placeholder{transition:opacity 67ms 0ms cubic-bezier(0.4, 0, 0.2, 1);opacity:0}}@media all{.mdc-text-field--no-label .mdc-text-field__input::placeholder,.mdc-text-field--focused .mdc-text-field__input::placeholder{transition-delay:40ms;transition-duration:110ms;opacity:1}}@media all{.mdc-text-field--no-label .mdc-text-field__input:-ms-input-placeholder,.mdc-text-field--focused .mdc-text-field__input:-ms-input-placeholder{transition-delay:40ms;transition-duration:110ms;opacity:1}}.mdc-text-field__affix{-moz-osx-font-smoothing:grayscale;-webkit-font-smoothing:antialiased;font-family:Roboto, sans-serif;font-family:var(--mdc-typography-subtitle1-font-family, var(--mdc-typography-font-family, Roboto, sans-serif));font-size:1rem;font-size:var(--mdc-typography-subtitle1-font-size, 1rem);font-weight:400;font-weight:var(--mdc-typography-subtitle1-font-weight, 400);letter-spacing:0.009375em;letter-spacing:var(--mdc-typography-subtitle1-letter-spacing, 0.009375em);text-decoration:inherit;text-decoration:var(--mdc-typography-subtitle1-text-decoration, inherit);text-transform:inherit;text-transform:var(--mdc-typography-subtitle1-text-transform, inherit);height:28px;transition:opacity 150ms 0ms cubic-bezier(0.4, 0, 0.2, 1);opacity:0;white-space:nowrap}.mdc-text-field--label-floating .mdc-text-field__affix,.mdc-text-field--no-label .mdc-text-field__affix{opacity:1}@supports(-webkit-hyphens: none){.mdc-text-field--outlined .mdc-text-field__affix{align-items:center;align-self:center;display:inline-flex;height:100%}}.mdc-text-field__affix--prefix{padding-left:0;padding-right:2px}[dir=rtl] .mdc-text-field__affix--prefix,.mdc-text-field__affix--prefix[dir=rtl]{padding-left:2px;padding-right:0}.mdc-text-field--end-aligned .mdc-text-field__affix--prefix{padding-left:0;padding-right:12px}[dir=rtl] .mdc-text-field--end-aligned .mdc-text-field__affix--prefix,.mdc-text-field--end-aligned .mdc-text-field__affix--prefix[dir=rtl]{padding-left:12px;padding-right:0}.mdc-text-field__affix--suffix{padding-left:12px;padding-right:0}[dir=rtl] .mdc-text-field__affix--suffix,.mdc-text-field__affix--suffix[dir=rtl]{padding-left:0;padding-right:12px}.mdc-text-field--end-aligned .mdc-text-field__affix--suffix{padding-left:2px;padding-right:0}[dir=rtl] .mdc-text-field--end-aligned .mdc-text-field__affix--suffix,.mdc-text-field--end-aligned .mdc-text-field__affix--suffix[dir=rtl]{padding-left:0;padding-right:2px}.mdc-text-field--filled{height:56px}.mdc-text-field--filled .mdc-text-field__ripple::before,.mdc-text-field--filled .mdc-text-field__ripple::after{background-color:rgba(0, 0, 0, 0.87);background-color:var(--mdc-ripple-color, rgba(0, 0, 0, 0.87))}.mdc-text-field--filled:hover .mdc-text-field__ripple::before,.mdc-text-field--filled.mdc-ripple-surface--hover .mdc-text-field__ripple::before{opacity:0.04;opacity:var(--mdc-ripple-hover-opacity, 0.04)}.mdc-text-field--filled.mdc-ripple-upgraded--background-focused .mdc-text-field__ripple::before,.mdc-text-field--filled:not(.mdc-ripple-upgraded):focus .mdc-text-field__ripple::before{transition-duration:75ms;opacity:0.12;opacity:var(--mdc-ripple-focus-opacity, 0.12)}.mdc-text-field--filled::before{display:inline-block;width:0;height:40px;content:"";vertical-align:0}.mdc-text-field--filled:not(.mdc-text-field--disabled){background-color:whitesmoke}.mdc-text-field--filled:not(.mdc-text-field--disabled) .mdc-line-ripple::before{border-bottom-color:rgba(0, 0, 0, 0.42)}.mdc-text-field--filled:not(.mdc-text-field--disabled):hover .mdc-line-ripple::before{border-bottom-color:rgba(0, 0, 0, 0.87)}.mdc-text-field--filled .mdc-line-ripple::after{border-bottom-color:#6200ee;border-bottom-color:var(--mdc-theme-primary, #6200ee)}.mdc-text-field--filled .mdc-floating-label{left:16px;right:initial}[dir=rtl] .mdc-text-field--filled .mdc-floating-label,.mdc-text-field--filled .mdc-floating-label[dir=rtl]{left:initial;right:16px}.mdc-text-field--filled .mdc-floating-label--float-above{transform:translateY(-106%) scale(0.75)}.mdc-text-field--filled.mdc-text-field--no-label .mdc-text-field__input{height:100%}.mdc-text-field--filled.mdc-text-field--no-label .mdc-floating-label{display:none}.mdc-text-field--filled.mdc-text-field--no-label::before{display:none}@supports(-webkit-hyphens: none){.mdc-text-field--filled.mdc-text-field--no-label .mdc-text-field__affix{align-items:center;align-self:center;display:inline-flex;height:100%}}.mdc-text-field--outlined{height:56px;overflow:visible}.mdc-text-field--outlined .mdc-floating-label--float-above{transform:translateY(-37.25px) scale(1)}.mdc-text-field--outlined .mdc-floating-label--float-above{font-size:.75rem}.mdc-text-field--outlined.mdc-notched-outline--upgraded .mdc-floating-label--float-above,.mdc-text-field--outlined .mdc-notched-outline--upgraded .mdc-floating-label--float-above{transform:translateY(-34.75px) scale(0.75)}.mdc-text-field--outlined.mdc-notched-outline--upgraded .mdc-floating-label--float-above,.mdc-text-field--outlined .mdc-notched-outline--upgraded .mdc-floating-label--float-above{font-size:1rem}.mdc-text-field--outlined .mdc-floating-label--shake{animation:mdc-floating-label-shake-float-above-text-field-outlined 250ms 1}@keyframes mdc-floating-label-shake-float-above-text-field-outlined{0%{transform:translateX(calc(0 - 0%)) translateY(-34.75px) scale(0.75)}33%{animation-timing-function:cubic-bezier(0.5, 0, 0.701732, 0.495819);transform:translateX(calc(4% - 0%)) translateY(-34.75px) scale(0.75)}66%{animation-timing-function:cubic-bezier(0.302435, 0.381352, 0.55, 0.956352);transform:translateX(calc(-4% - 0%)) translateY(-34.75px) scale(0.75)}100%{transform:translateX(calc(0 - 0%)) translateY(-34.75px) scale(0.75)}}.mdc-text-field--outlined .mdc-text-field__input{height:100%}.mdc-text-field--outlined:not(.mdc-text-field--disabled) .mdc-notched-outline__leading,.mdc-text-field--outlined:not(.mdc-text-field--disabled) .mdc-notched-outline__notch,.mdc-text-field--outlined:not(.mdc-text-field--disabled) .mdc-notched-outline__trailing{border-color:rgba(0, 0, 0, 0.38)}.mdc-text-field--outlined:not(.mdc-text-field--disabled):not(.mdc-text-field--focused):hover .mdc-notched-outline .mdc-notched-outline__leading,.mdc-text-field--outlined:not(.mdc-text-field--disabled):not(.mdc-text-field--focused):hover .mdc-notched-outline .mdc-notched-outline__notch,.mdc-text-field--outlined:not(.mdc-text-field--disabled):not(.mdc-text-field--focused):hover .mdc-notched-outline .mdc-notched-outline__trailing{border-color:rgba(0, 0, 0, 0.87)}.mdc-text-field--outlined:not(.mdc-text-field--disabled).mdc-text-field--focused .mdc-notched-outline__leading,.mdc-text-field--outlined:not(.mdc-text-field--disabled).mdc-text-field--focused .mdc-notched-outline__notch,.mdc-text-field--outlined:not(.mdc-text-field--disabled).mdc-text-field--focused .mdc-notched-outline__trailing{border-color:#6200ee;border-color:var(--mdc-theme-primary, #6200ee)}.mdc-text-field--outlined .mdc-notched-outline .mdc-notched-outline__leading{border-top-left-radius:4px;border-top-left-radius:var(--mdc-shape-small, 4px);border-top-right-radius:0;border-bottom-right-radius:0;border-bottom-left-radius:4px;border-bottom-left-radius:var(--mdc-shape-small, 4px)}[dir=rtl] .mdc-text-field--outlined .mdc-notched-outline .mdc-notched-outline__leading,.mdc-text-field--outlined .mdc-notched-outline .mdc-notched-outline__leading[dir=rtl]{border-top-left-radius:0;border-top-right-radius:4px;border-top-right-radius:var(--mdc-shape-small, 4px);border-bottom-right-radius:4px;border-bottom-right-radius:var(--mdc-shape-small, 4px);border-bottom-left-radius:0}@supports(top: max(0%)){.mdc-text-field--outlined .mdc-notched-outline .mdc-notched-outline__leading{width:max(12px, var(--mdc-shape-small, 4px))}}@supports(top: max(0%)){.mdc-text-field--outlined .mdc-notched-outline .mdc-notched-outline__notch{max-width:calc(100% - max(12px, var(--mdc-shape-small, 4px)) * 2)}}.mdc-text-field--outlined .mdc-notched-outline .mdc-notched-outline__trailing{border-top-left-radius:0;border-top-right-radius:4px;border-top-right-radius:var(--mdc-shape-small, 4px);border-bottom-right-radius:4px;border-bottom-right-radius:var(--mdc-shape-small, 4px);border-bottom-left-radius:0}[dir=rtl] .mdc-text-field--outlined .mdc-notched-outline .mdc-notched-outline__trailing,.mdc-text-field--outlined .mdc-notched-outline .mdc-notched-outline__trailing[dir=rtl]{border-top-left-radius:4px;border-top-left-radius:var(--mdc-shape-small, 4px);border-top-right-radius:0;border-bottom-right-radius:0;border-bottom-left-radius:4px;border-bottom-left-radius:var(--mdc-shape-small, 4px)}@supports(top: max(0%)){.mdc-text-field--outlined{padding-left:max(16px, calc(var(--mdc-shape-small, 4px) + 4px))}}@supports(top: max(0%)){.mdc-text-field--outlined{padding-right:max(16px, var(--mdc-shape-small, 4px))}}@supports(top: max(0%)){.mdc-text-field--outlined+.mdc-text-field-helper-line{padding-left:max(16px, calc(var(--mdc-shape-small, 4px) + 4px))}}@supports(top: max(0%)){.mdc-text-field--outlined+.mdc-text-field-helper-line{padding-right:max(16px, var(--mdc-shape-small, 4px))}}.mdc-text-field--outlined.mdc-text-field--with-leading-icon{padding-left:0}@supports(top: max(0%)){.mdc-text-field--outlined.mdc-text-field--with-leading-icon{padding-right:max(16px, var(--mdc-shape-small, 4px))}}[dir=rtl] .mdc-text-field--outlined.mdc-text-field--with-leading-icon,.mdc-text-field--outlined.mdc-text-field--with-leading-icon[dir=rtl]{padding-right:0}@supports(top: max(0%)){[dir=rtl] .mdc-text-field--outlined.mdc-text-field--with-leading-icon,.mdc-text-field--outlined.mdc-text-field--with-leading-icon[dir=rtl]{padding-left:max(16px, var(--mdc-shape-small, 4px))}}.mdc-text-field--outlined.mdc-text-field--with-trailing-icon{padding-right:0}@supports(top: max(0%)){.mdc-text-field--outlined.mdc-text-field--with-trailing-icon{padding-left:max(16px, calc(var(--mdc-shape-small, 4px) + 4px))}}[dir=rtl] .mdc-text-field--outlined.mdc-text-field--with-trailing-icon,.mdc-text-field--outlined.mdc-text-field--with-trailing-icon[dir=rtl]{padding-left:0}@supports(top: max(0%)){[dir=rtl] .mdc-text-field--outlined.mdc-text-field--with-trailing-icon,.mdc-text-field--outlined.mdc-text-field--with-trailing-icon[dir=rtl]{padding-right:max(16px, calc(var(--mdc-shape-small, 4px) + 4px))}}.mdc-text-field--outlined.mdc-text-field--with-leading-icon.mdc-text-field--with-trailing-icon{padding-left:0;padding-right:0}.mdc-text-field--outlined .mdc-notched-outline--notched .mdc-notched-outline__notch{padding-top:1px}.mdc-text-field--outlined .mdc-text-field__ripple::before,.mdc-text-field--outlined .mdc-text-field__ripple::after{background-color:transparent;background-color:var(--mdc-ripple-color, transparent)}.mdc-text-field--outlined .mdc-floating-label{left:4px;right:initial}[dir=rtl] .mdc-text-field--outlined .mdc-floating-label,.mdc-text-field--outlined .mdc-floating-label[dir=rtl]{left:initial;right:4px}.mdc-text-field--outlined .mdc-text-field__input{display:flex;border:none !important;background-color:transparent}.mdc-text-field--outlined .mdc-notched-outline{z-index:1}.mdc-text-field--textarea{flex-direction:column;align-items:center;width:auto;height:auto;padding:0;transition:none}.mdc-text-field--textarea .mdc-floating-label{top:19px}.mdc-text-field--textarea .mdc-floating-label:not(.mdc-floating-label--float-above){transform:none}.mdc-text-field--textarea .mdc-text-field__input{flex-grow:1;height:auto;min-height:1.5rem;overflow-x:hidden;overflow-y:auto;box-sizing:border-box;resize:none;padding:0 16px;line-height:1.5rem}.mdc-text-field--textarea.mdc-text-field--filled::before{display:none}.mdc-text-field--textarea.mdc-text-field--filled .mdc-floating-label--float-above{transform:translateY(-10.25px) scale(0.75)}.mdc-text-field--textarea.mdc-text-field--filled .mdc-floating-label--shake{animation:mdc-floating-label-shake-float-above-textarea-filled 250ms 1}@keyframes mdc-floating-label-shake-float-above-textarea-filled{0%{transform:translateX(calc(0 - 0%)) translateY(-10.25px) scale(0.75)}33%{animation-timing-function:cubic-bezier(0.5, 0, 0.701732, 0.495819);transform:translateX(calc(4% - 0%)) translateY(-10.25px) scale(0.75)}66%{animation-timing-function:cubic-bezier(0.302435, 0.381352, 0.55, 0.956352);transform:translateX(calc(-4% - 0%)) translateY(-10.25px) scale(0.75)}100%{transform:translateX(calc(0 - 0%)) translateY(-10.25px) scale(0.75)}}.mdc-text-field--textarea.mdc-text-field--filled .mdc-text-field__input{margin-top:23px;margin-bottom:9px}.mdc-text-field--textarea.mdc-text-field--filled.mdc-text-field--no-label .mdc-text-field__input{margin-top:16px;margin-bottom:16px}.mdc-text-field--textarea.mdc-text-field--outlined .mdc-notched-outline--notched .mdc-notched-outline__notch{padding-top:0}.mdc-text-field--textarea.mdc-text-field--outlined .mdc-floating-label--float-above{transform:translateY(-27.25px) scale(1)}.mdc-text-field--textarea.mdc-text-field--outlined .mdc-floating-label--float-above{font-size:.75rem}.mdc-text-field--textarea.mdc-text-field--outlined.mdc-notched-outline--upgraded .mdc-floating-label--float-above,.mdc-text-field--textarea.mdc-text-field--outlined .mdc-notched-outline--upgraded .mdc-floating-label--float-above{transform:translateY(-24.75px) scale(0.75)}.mdc-text-field--textarea.mdc-text-field--outlined.mdc-notched-outline--upgraded .mdc-floating-label--float-above,.mdc-text-field--textarea.mdc-text-field--outlined .mdc-notched-outline--upgraded .mdc-floating-label--float-above{font-size:1rem}.mdc-text-field--textarea.mdc-text-field--outlined .mdc-floating-label--shake{animation:mdc-floating-label-shake-float-above-textarea-outlined 250ms 1}@keyframes mdc-floating-label-shake-float-above-textarea-outlined{0%{transform:translateX(calc(0 - 0%)) translateY(-24.75px) scale(0.75)}33%{animation-timing-function:cubic-bezier(0.5, 0, 0.701732, 0.495819);transform:translateX(calc(4% - 0%)) translateY(-24.75px) scale(0.75)}66%{animation-timing-function:cubic-bezier(0.302435, 0.381352, 0.55, 0.956352);transform:translateX(calc(-4% - 0%)) translateY(-24.75px) scale(0.75)}100%{transform:translateX(calc(0 - 0%)) translateY(-24.75px) scale(0.75)}}.mdc-text-field--textarea.mdc-text-field--outlined .mdc-text-field__input{margin-top:16px;margin-bottom:16px}.mdc-text-field--textarea.mdc-text-field--outlined .mdc-floating-label{top:18px}.mdc-text-field--textarea.mdc-text-field--with-internal-counter .mdc-text-field__input{margin-bottom:2px}.mdc-text-field--textarea.mdc-text-field--with-internal-counter .mdc-text-field-character-counter{align-self:flex-end;padding:0 16px}.mdc-text-field--textarea.mdc-text-field--with-internal-counter .mdc-text-field-character-counter::after{display:inline-block;width:0;height:16px;content:"";vertical-align:-16px}.mdc-text-field--textarea.mdc-text-field--with-internal-counter .mdc-text-field-character-counter::before{display:none}.mdc-text-field__resizer{align-self:stretch;display:inline-flex;flex-direction:column;flex-grow:1;max-height:100%;max-width:100%;min-height:56px;min-width:fit-content;min-width:-moz-available;min-width:-webkit-fill-available;overflow:hidden;resize:both}.mdc-text-field--filled .mdc-text-field__resizer{transform:translateY(-1px)}.mdc-text-field--filled .mdc-text-field__resizer .mdc-text-field__input,.mdc-text-field--filled .mdc-text-field__resizer .mdc-text-field-character-counter{transform:translateY(1px)}.mdc-text-field--outlined .mdc-text-field__resizer{transform:translateX(-1px) translateY(-1px)}[dir=rtl] .mdc-text-field--outlined .mdc-text-field__resizer,.mdc-text-field--outlined .mdc-text-field__resizer[dir=rtl]{transform:translateX(1px) translateY(-1px)}.mdc-text-field--outlined .mdc-text-field__resizer .mdc-text-field__input,.mdc-text-field--outlined .mdc-text-field__resizer .mdc-text-field-character-counter{transform:translateX(1px) translateY(1px)}[dir=rtl] .mdc-text-field--outlined .mdc-text-field__resizer .mdc-text-field__input,[dir=rtl] .mdc-text-field--outlined .mdc-text-field__resizer .mdc-text-field-character-counter,.mdc-text-field--outlined .mdc-text-field__resizer .mdc-text-field__input[dir=rtl],.mdc-text-field--outlined .mdc-text-field__resizer .mdc-text-field-character-counter[dir=rtl]{transform:translateX(-1px) translateY(1px)}.mdc-text-field--with-leading-icon{padding-left:0;padding-right:16px}[dir=rtl] .mdc-text-field--with-leading-icon,.mdc-text-field--with-leading-icon[dir=rtl]{padding-left:16px;padding-right:0}.mdc-text-field--with-leading-icon.mdc-text-field--filled .mdc-floating-label{max-width:calc(100% - 48px);left:48px;right:initial}[dir=rtl] .mdc-text-field--with-leading-icon.mdc-text-field--filled .mdc-floating-label,.mdc-text-field--with-leading-icon.mdc-text-field--filled .mdc-floating-label[dir=rtl]{left:initial;right:48px}.mdc-text-field--with-leading-icon.mdc-text-field--filled .mdc-floating-label--float-above{max-width:calc(100% / 0.75 - 64px / 0.75)}.mdc-text-field--with-leading-icon.mdc-text-field--outlined .mdc-floating-label{left:36px;right:initial}[dir=rtl] .mdc-text-field--with-leading-icon.mdc-text-field--outlined .mdc-floating-label,.mdc-text-field--with-leading-icon.mdc-text-field--outlined .mdc-floating-label[dir=rtl]{left:initial;right:36px}.mdc-text-field--with-leading-icon.mdc-text-field--outlined :not(.mdc-notched-outline--notched) .mdc-notched-outline__notch{max-width:calc(100% - 60px)}.mdc-text-field--with-leading-icon.mdc-text-field--outlined .mdc-floating-label--float-above{transform:translateY(-37.25px) translateX(-32px) scale(1)}[dir=rtl] .mdc-text-field--with-leading-icon.mdc-text-field--outlined .mdc-floating-label--float-above,.mdc-text-field--with-leading-icon.mdc-text-field--outlined .mdc-floating-label--float-above[dir=rtl]{transform:translateY(-37.25px) translateX(32px) scale(1)}.mdc-text-field--with-leading-icon.mdc-text-field--outlined .mdc-floating-label--float-above{font-size:.75rem}.mdc-text-field--with-leading-icon.mdc-text-field--outlined.mdc-notched-outline--upgraded .mdc-floating-label--float-above,.mdc-text-field--with-leading-icon.mdc-text-field--outlined .mdc-notched-outline--upgraded .mdc-floating-label--float-above{transform:translateY(-34.75px) translateX(-32px) scale(0.75)}[dir=rtl] .mdc-text-field--with-leading-icon.mdc-text-field--outlined.mdc-notched-outline--upgraded .mdc-floating-label--float-above,[dir=rtl] .mdc-text-field--with-leading-icon.mdc-text-field--outlined .mdc-notched-outline--upgraded .mdc-floating-label--float-above,.mdc-text-field--with-leading-icon.mdc-text-field--outlined.mdc-notched-outline--upgraded .mdc-floating-label--float-above[dir=rtl],.mdc-text-field--with-leading-icon.mdc-text-field--outlined .mdc-notched-outline--upgraded .mdc-floating-label--float-above[dir=rtl]{transform:translateY(-34.75px) translateX(32px) scale(0.75)}.mdc-text-field--with-leading-icon.mdc-text-field--outlined.mdc-notched-outline--upgraded .mdc-floating-label--float-above,.mdc-text-field--with-leading-icon.mdc-text-field--outlined .mdc-notched-outline--upgraded .mdc-floating-label--float-above{font-size:1rem}.mdc-text-field--with-leading-icon.mdc-text-field--outlined .mdc-floating-label--shake{animation:mdc-floating-label-shake-float-above-text-field-outlined-leading-icon 250ms 1}@keyframes mdc-floating-label-shake-float-above-text-field-outlined-leading-icon{0%{transform:translateX(calc(0 - 32px)) translateY(-34.75px) scale(0.75)}33%{animation-timing-function:cubic-bezier(0.5, 0, 0.701732, 0.495819);transform:translateX(calc(4% - 32px)) translateY(-34.75px) scale(0.75)}66%{animation-timing-function:cubic-bezier(0.302435, 0.381352, 0.55, 0.956352);transform:translateX(calc(-4% - 32px)) translateY(-34.75px) scale(0.75)}100%{transform:translateX(calc(0 - 32px)) translateY(-34.75px) scale(0.75)}}[dir=rtl] .mdc-text-field--with-leading-icon.mdc-text-field--outlined .mdc-floating-label--shake,.mdc-text-field--with-leading-icon.mdc-text-field--outlined[dir=rtl] .mdc-floating-label--shake{animation:mdc-floating-label-shake-float-above-text-field-outlined-leading-icon 250ms 1}@keyframes mdc-floating-label-shake-float-above-text-field-outlined-leading-icon-rtl{0%{transform:translateX(calc(0 - -32px)) translateY(-34.75px) scale(0.75)}33%{animation-timing-function:cubic-bezier(0.5, 0, 0.701732, 0.495819);transform:translateX(calc(4% - -32px)) translateY(-34.75px) scale(0.75)}66%{animation-timing-function:cubic-bezier(0.302435, 0.381352, 0.55, 0.956352);transform:translateX(calc(-4% - -32px)) translateY(-34.75px) scale(0.75)}100%{transform:translateX(calc(0 - -32px)) translateY(-34.75px) scale(0.75)}}.mdc-text-field--with-trailing-icon{padding-left:16px;padding-right:0}[dir=rtl] .mdc-text-field--with-trailing-icon,.mdc-text-field--with-trailing-icon[dir=rtl]{padding-left:0;padding-right:16px}.mdc-text-field--with-trailing-icon.mdc-text-field--filled .mdc-floating-label{max-width:calc(100% - 64px)}.mdc-text-field--with-trailing-icon.mdc-text-field--filled .mdc-floating-label--float-above{max-width:calc(100% / 0.75 - 64px / 0.75)}.mdc-text-field--with-trailing-icon.mdc-text-field--outlined :not(.mdc-notched-outline--notched) .mdc-notched-outline__notch{max-width:calc(100% - 60px)}.mdc-text-field--with-leading-icon.mdc-text-field--with-trailing-icon{padding-left:0;padding-right:0}.mdc-text-field--with-leading-icon.mdc-text-field--with-trailing-icon.mdc-text-field--filled .mdc-floating-label{max-width:calc(100% - 96px)}.mdc-text-field--with-leading-icon.mdc-text-field--with-trailing-icon.mdc-text-field--filled .mdc-floating-label--float-above{max-width:calc(100% / 0.75 - 96px / 0.75)}.mdc-text-field-helper-line{display:flex;justify-content:space-between;box-sizing:border-box}.mdc-text-field+.mdc-text-field-helper-line{padding-right:16px;padding-left:16px}.mdc-form-field>.mdc-text-field+label{align-self:flex-start}.mdc-text-field--focused:not(.mdc-text-field--disabled) .mdc-floating-label{color:rgba(98, 0, 238, 0.87)}.mdc-text-field--focused .mdc-notched-outline__leading,.mdc-text-field--focused .mdc-notched-outline__notch,.mdc-text-field--focused .mdc-notched-outline__trailing{border-width:2px}.mdc-text-field--focused+.mdc-text-field-helper-line .mdc-text-field-helper-text:not(.mdc-text-field-helper-text--validation-msg){opacity:1}.mdc-text-field--focused.mdc-text-field--outlined .mdc-notched-outline--notched .mdc-notched-outline__notch{padding-top:2px}.mdc-text-field--focused.mdc-text-field--outlined.mdc-text-field--textarea .mdc-notched-outline--notched .mdc-notched-outline__notch{padding-top:0}.mdc-text-field--invalid:not(.mdc-text-field--disabled):hover .mdc-line-ripple::before{border-bottom-color:#b00020;border-bottom-color:var(--mdc-theme-error, #b00020)}.mdc-text-field--invalid:not(.mdc-text-field--disabled) .mdc-line-ripple::after{border-bottom-color:#b00020;border-bottom-color:var(--mdc-theme-error, #b00020)}.mdc-text-field--invalid:not(.mdc-text-field--disabled) .mdc-floating-label{color:#b00020;color:var(--mdc-theme-error, #b00020)}.mdc-text-field--invalid:not(.mdc-text-field--disabled).mdc-text-field--invalid+.mdc-text-field-helper-line .mdc-text-field-helper-text--validation-msg{color:#b00020;color:var(--mdc-theme-error, #b00020)}.mdc-text-field--invalid .mdc-text-field__input{caret-color:#b00020;caret-color:var(--mdc-theme-error, #b00020)}.mdc-text-field--invalid:not(.mdc-text-field--disabled) .mdc-text-field__icon--trailing{color:#b00020;color:var(--mdc-theme-error, #b00020)}.mdc-text-field--invalid:not(.mdc-text-field--disabled) .mdc-line-ripple::before{border-bottom-color:#b00020;border-bottom-color:var(--mdc-theme-error, #b00020)}.mdc-text-field--invalid:not(.mdc-text-field--disabled) .mdc-notched-outline__leading,.mdc-text-field--invalid:not(.mdc-text-field--disabled) .mdc-notched-outline__notch,.mdc-text-field--invalid:not(.mdc-text-field--disabled) .mdc-notched-outline__trailing{border-color:#b00020;border-color:var(--mdc-theme-error, #b00020)}.mdc-text-field--invalid:not(.mdc-text-field--disabled):not(.mdc-text-field--focused):hover .mdc-notched-outline .mdc-notched-outline__leading,.mdc-text-field--invalid:not(.mdc-text-field--disabled):not(.mdc-text-field--focused):hover .mdc-notched-outline .mdc-notched-outline__notch,.mdc-text-field--invalid:not(.mdc-text-field--disabled):not(.mdc-text-field--focused):hover .mdc-notched-outline .mdc-notched-outline__trailing{border-color:#b00020;border-color:var(--mdc-theme-error, #b00020)}.mdc-text-field--invalid:not(.mdc-text-field--disabled).mdc-text-field--focused .mdc-notched-outline__leading,.mdc-text-field--invalid:not(.mdc-text-field--disabled).mdc-text-field--focused .mdc-notched-outline__notch,.mdc-text-field--invalid:not(.mdc-text-field--disabled).mdc-text-field--focused .mdc-notched-outline__trailing{border-color:#b00020;border-color:var(--mdc-theme-error, #b00020)}.mdc-text-field--invalid+.mdc-text-field-helper-line .mdc-text-field-helper-text--validation-msg{opacity:1}.mdc-text-field--disabled{pointer-events:none}.mdc-text-field--disabled .mdc-text-field__input{color:rgba(0, 0, 0, 0.38)}@media all{.mdc-text-field--disabled .mdc-text-field__input::placeholder{color:rgba(0, 0, 0, 0.38)}}@media all{.mdc-text-field--disabled .mdc-text-field__input:-ms-input-placeholder{color:rgba(0, 0, 0, 0.38)}}.mdc-text-field--disabled .mdc-floating-label{color:rgba(0, 0, 0, 0.38)}.mdc-text-field--disabled+.mdc-text-field-helper-line .mdc-text-field-helper-text{color:rgba(0, 0, 0, 0.38)}.mdc-text-field--disabled .mdc-text-field-character-counter,.mdc-text-field--disabled+.mdc-text-field-helper-line .mdc-text-field-character-counter{color:rgba(0, 0, 0, 0.38)}.mdc-text-field--disabled .mdc-text-field__icon--leading{color:rgba(0, 0, 0, 0.3)}.mdc-text-field--disabled .mdc-text-field__icon--trailing{color:rgba(0, 0, 0, 0.3)}.mdc-text-field--disabled .mdc-text-field__affix--prefix{color:rgba(0, 0, 0, 0.38)}.mdc-text-field--disabled .mdc-text-field__affix--suffix{color:rgba(0, 0, 0, 0.38)}.mdc-text-field--disabled .mdc-line-ripple::before{border-bottom-color:rgba(0, 0, 0, 0.06)}.mdc-text-field--disabled .mdc-notched-outline__leading,.mdc-text-field--disabled .mdc-notched-outline__notch,.mdc-text-field--disabled .mdc-notched-outline__trailing{border-color:rgba(0, 0, 0, 0.06)}@media screen and (forced-colors: active),(-ms-high-contrast: active){.mdc-text-field--disabled .mdc-text-field__input::placeholder{color:GrayText}}@media screen and (forced-colors: active),(-ms-high-contrast: active){.mdc-text-field--disabled .mdc-text-field__input:-ms-input-placeholder{color:GrayText}}@media screen and (forced-colors: active),(-ms-high-contrast: active){.mdc-text-field--disabled .mdc-floating-label{color:GrayText}}@media screen and (forced-colors: active),(-ms-high-contrast: active){.mdc-text-field--disabled+.mdc-text-field-helper-line .mdc-text-field-helper-text{color:GrayText}}@media screen and (forced-colors: active),(-ms-high-contrast: active){.mdc-text-field--disabled .mdc-text-field-character-counter,.mdc-text-field--disabled+.mdc-text-field-helper-line .mdc-text-field-character-counter{color:GrayText}}@media screen and (forced-colors: active),(-ms-high-contrast: active){.mdc-text-field--disabled .mdc-text-field__icon--leading{color:GrayText}}@media screen and (forced-colors: active),(-ms-high-contrast: active){.mdc-text-field--disabled .mdc-text-field__icon--trailing{color:GrayText}}@media screen and (forced-colors: active),(-ms-high-contrast: active){.mdc-text-field--disabled .mdc-text-field__affix--prefix{color:GrayText}}@media screen and (forced-colors: active),(-ms-high-contrast: active){.mdc-text-field--disabled .mdc-text-field__affix--suffix{color:GrayText}}@media screen and (forced-colors: active),(-ms-high-contrast: active){.mdc-text-field--disabled .mdc-line-ripple::before{border-bottom-color:GrayText}}@media screen and (forced-colors: active),(-ms-high-contrast: active){.mdc-text-field--disabled .mdc-notched-outline__leading,.mdc-text-field--disabled .mdc-notched-outline__notch,.mdc-text-field--disabled .mdc-notched-outline__trailing{border-color:GrayText}}@media screen and (forced-colors: active){.mdc-text-field--disabled .mdc-text-field__input{background-color:Window}.mdc-text-field--disabled .mdc-floating-label{z-index:1}}.mdc-text-field--disabled .mdc-floating-label{cursor:default}.mdc-text-field--disabled.mdc-text-field--filled{background-color:#fafafa}.mdc-text-field--disabled.mdc-text-field--filled .mdc-text-field__ripple{display:none}.mdc-text-field--disabled .mdc-text-field__input{pointer-events:auto}.mdc-text-field--end-aligned .mdc-text-field__input{text-align:right}[dir=rtl] .mdc-text-field--end-aligned .mdc-text-field__input,.mdc-text-field--end-aligned .mdc-text-field__input[dir=rtl]{text-align:left}[dir=rtl] .mdc-text-field--ltr-text .mdc-text-field__input,[dir=rtl] .mdc-text-field--ltr-text .mdc-text-field__affix,.mdc-text-field--ltr-text[dir=rtl] .mdc-text-field__input,.mdc-text-field--ltr-text[dir=rtl] .mdc-text-field__affix{direction:ltr}[dir=rtl] .mdc-text-field--ltr-text .mdc-text-field__affix--prefix,.mdc-text-field--ltr-text[dir=rtl] .mdc-text-field__affix--prefix{padding-left:0;padding-right:2px}[dir=rtl] .mdc-text-field--ltr-text .mdc-text-field__affix--suffix,.mdc-text-field--ltr-text[dir=rtl] .mdc-text-field__affix--suffix{padding-left:12px;padding-right:0}[dir=rtl] .mdc-text-field--ltr-text .mdc-text-field__icon--leading,.mdc-text-field--ltr-text[dir=rtl] .mdc-text-field__icon--leading{order:1}[dir=rtl] .mdc-text-field--ltr-text .mdc-text-field__affix--suffix,.mdc-text-field--ltr-text[dir=rtl] .mdc-text-field__affix--suffix{order:2}[dir=rtl] .mdc-text-field--ltr-text .mdc-text-field__input,.mdc-text-field--ltr-text[dir=rtl] .mdc-text-field__input{order:3}[dir=rtl] .mdc-text-field--ltr-text .mdc-text-field__affix--prefix,.mdc-text-field--ltr-text[dir=rtl] .mdc-text-field__affix--prefix{order:4}[dir=rtl] .mdc-text-field--ltr-text .mdc-text-field__icon--trailing,.mdc-text-field--ltr-text[dir=rtl] .mdc-text-field__icon--trailing{order:5}[dir=rtl] .mdc-text-field--ltr-text.mdc-text-field--end-aligned .mdc-text-field__input,.mdc-text-field--ltr-text.mdc-text-field--end-aligned[dir=rtl] .mdc-text-field__input{text-align:right}[dir=rtl] .mdc-text-field--ltr-text.mdc-text-field--end-aligned .mdc-text-field__affix--prefix,.mdc-text-field--ltr-text.mdc-text-field--end-aligned[dir=rtl] .mdc-text-field__affix--prefix{padding-right:12px}[dir=rtl] .mdc-text-field--ltr-text.mdc-text-field--end-aligned .mdc-text-field__affix--suffix,.mdc-text-field--ltr-text.mdc-text-field--end-aligned[dir=rtl] .mdc-text-field__affix--suffix{padding-left:2px}.mdc-text-field-helper-text{-moz-osx-font-smoothing:grayscale;-webkit-font-smoothing:antialiased;font-family:Roboto, sans-serif;font-family:var(--mdc-typography-caption-font-family, var(--mdc-typography-font-family, Roboto, sans-serif));font-size:0.75rem;font-size:var(--mdc-typography-caption-font-size, 0.75rem);line-height:1.25rem;line-height:var(--mdc-typography-caption-line-height, 1.25rem);font-weight:400;font-weight:var(--mdc-typography-caption-font-weight, 400);letter-spacing:0.0333333333em;letter-spacing:var(--mdc-typography-caption-letter-spacing, 0.0333333333em);text-decoration:inherit;text-decoration:var(--mdc-typography-caption-text-decoration, inherit);text-transform:inherit;text-transform:var(--mdc-typography-caption-text-transform, inherit);display:block;margin-top:0;line-height:normal;margin:0;opacity:0;will-change:opacity;transition:opacity 150ms 0ms cubic-bezier(0.4, 0, 0.2, 1)}.mdc-text-field-helper-text::before{display:inline-block;width:0;height:16px;content:"";vertical-align:0}.mdc-text-field-helper-text--persistent{transition:none;opacity:1;will-change:initial}.mdc-text-field-character-counter{-moz-osx-font-smoothing:grayscale;-webkit-font-smoothing:antialiased;font-family:Roboto, sans-serif;font-family:var(--mdc-typography-caption-font-family, var(--mdc-typography-font-family, Roboto, sans-serif));font-size:0.75rem;font-size:var(--mdc-typography-caption-font-size, 0.75rem);line-height:1.25rem;line-height:var(--mdc-typography-caption-line-height, 1.25rem);font-weight:400;font-weight:var(--mdc-typography-caption-font-weight, 400);letter-spacing:0.0333333333em;letter-spacing:var(--mdc-typography-caption-letter-spacing, 0.0333333333em);text-decoration:inherit;text-decoration:var(--mdc-typography-caption-text-decoration, inherit);text-transform:inherit;text-transform:var(--mdc-typography-caption-text-transform, inherit);display:block;margin-top:0;line-height:normal;margin-left:auto;margin-right:0;padding-left:16px;padding-right:0;white-space:nowrap}.mdc-text-field-character-counter::before{display:inline-block;width:0;height:16px;content:"";vertical-align:0}[dir=rtl] .mdc-text-field-character-counter,.mdc-text-field-character-counter[dir=rtl]{margin-left:0;margin-right:auto}[dir=rtl] .mdc-text-field-character-counter,.mdc-text-field-character-counter[dir=rtl]{padding-left:0;padding-right:16px}.mdc-text-field__icon{align-self:center;cursor:pointer}.mdc-text-field__icon:not([tabindex]),.mdc-text-field__icon[tabindex="-1"]{cursor:default;pointer-events:none}.mdc-text-field__icon svg{display:block}.mdc-text-field__icon--leading{margin-left:16px;margin-right:8px}[dir=rtl] .mdc-text-field__icon--leading,.mdc-text-field__icon--leading[dir=rtl]{margin-left:8px;margin-right:16px}.mdc-text-field__icon--trailing{padding:12px;margin-left:0px;margin-right:0px}[dir=rtl] .mdc-text-field__icon--trailing,.mdc-text-field__icon--trailing[dir=rtl]{margin-left:0px;margin-right:0px}.material-icons{font-family:var(--mdc-icon-font, "Material Icons");font-weight:normal;font-style:normal;font-size:var(--mdc-icon-size, 24px);line-height:1;letter-spacing:normal;text-transform:none;display:inline-block;white-space:nowrap;word-wrap:normal;direction:ltr;-webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility;-moz-osx-font-smoothing:grayscale;font-feature-settings:"liga"}:host{display:inline-flex;flex-direction:column;outline:none}.mdc-text-field{width:100%}.mdc-text-field:not(.mdc-text-field--disabled) .mdc-line-ripple::before{border-bottom-color:rgba(0, 0, 0, 0.42);border-bottom-color:var(--mdc-text-field-idle-line-color, rgba(0, 0, 0, 0.42))}.mdc-text-field:not(.mdc-text-field--disabled):hover .mdc-line-ripple::before{border-bottom-color:rgba(0, 0, 0, 0.87);border-bottom-color:var(--mdc-text-field-hover-line-color, rgba(0, 0, 0, 0.87))}.mdc-text-field.mdc-text-field--disabled .mdc-line-ripple::before{border-bottom-color:rgba(0, 0, 0, 0.06);border-bottom-color:var(--mdc-text-field-disabled-line-color, rgba(0, 0, 0, 0.06))}.mdc-text-field.mdc-text-field--invalid:not(.mdc-text-field--disabled) .mdc-line-ripple::before{border-bottom-color:#b00020;border-bottom-color:var(--mdc-theme-error, #b00020)}.mdc-text-field__input{direction:inherit}mwc-notched-outline{--mdc-notched-outline-border-color: var( --mdc-text-field-outlined-idle-border-color, rgba(0, 0, 0, 0.38) )}:host(:not([disabled]):hover) :not(.mdc-text-field--invalid):not(.mdc-text-field--focused) mwc-notched-outline{--mdc-notched-outline-border-color: var( --mdc-text-field-outlined-hover-border-color, rgba(0, 0, 0, 0.87) )}:host(:not([disabled])) .mdc-text-field:not(.mdc-text-field--outlined){background-color:var(--mdc-text-field-fill-color, whitesmoke)}:host(:not([disabled])) .mdc-text-field.mdc-text-field--invalid mwc-notched-outline{--mdc-notched-outline-border-color: var( --mdc-text-field-error-color, var(--mdc-theme-error, #b00020) )}:host(:not([disabled])) .mdc-text-field.mdc-text-field--invalid+.mdc-text-field-helper-line .mdc-text-field-character-counter,:host(:not([disabled])) .mdc-text-field.mdc-text-field--invalid .mdc-text-field__icon{color:var(--mdc-text-field-error-color, var(--mdc-theme-error, #b00020))}:host(:not([disabled])) .mdc-text-field:not(.mdc-text-field--invalid):not(.mdc-text-field--focused) .mdc-floating-label,:host(:not([disabled])) .mdc-text-field:not(.mdc-text-field--invalid):not(.mdc-text-field--focused) .mdc-floating-label::after{color:var(--mdc-text-field-label-ink-color, rgba(0, 0, 0, 0.6))}:host(:not([disabled])) .mdc-text-field.mdc-text-field--focused mwc-notched-outline{--mdc-notched-outline-stroke-width: 2px}:host(:not([disabled])) .mdc-text-field.mdc-text-field--focused:not(.mdc-text-field--invalid) mwc-notched-outline{--mdc-notched-outline-border-color: var( --mdc-text-field-focused-label-color, var(--mdc-theme-primary, rgba(98, 0, 238, 0.87)) )}:host(:not([disabled])) .mdc-text-field.mdc-text-field--focused:not(.mdc-text-field--invalid) .mdc-floating-label{color:#6200ee;color:var(--mdc-theme-primary, #6200ee)}:host(:not([disabled])) .mdc-text-field .mdc-text-field__input{color:var(--mdc-text-field-ink-color, rgba(0, 0, 0, 0.87))}:host(:not([disabled])) .mdc-text-field .mdc-text-field__input::placeholder{color:var(--mdc-text-field-label-ink-color, rgba(0, 0, 0, 0.6))}:host(:not([disabled])) .mdc-text-field-helper-line .mdc-text-field-helper-text:not(.mdc-text-field-helper-text--validation-msg),:host(:not([disabled])) .mdc-text-field-helper-line:not(.mdc-text-field--invalid) .mdc-text-field-character-counter{color:var(--mdc-text-field-label-ink-color, rgba(0, 0, 0, 0.6))}:host([disabled]) .mdc-text-field:not(.mdc-text-field--outlined){background-color:var(--mdc-text-field-disabled-fill-color, #fafafa)}:host([disabled]) .mdc-text-field.mdc-text-field--outlined mwc-notched-outline{--mdc-notched-outline-border-color: var( --mdc-text-field-outlined-disabled-border-color, rgba(0, 0, 0, 0.06) )}:host([disabled]) .mdc-text-field:not(.mdc-text-field--invalid):not(.mdc-text-field--focused) .mdc-floating-label,:host([disabled]) .mdc-text-field:not(.mdc-text-field--invalid):not(.mdc-text-field--focused) .mdc-floating-label::after{color:var(--mdc-text-field-disabled-ink-color, rgba(0, 0, 0, 0.38))}:host([disabled]) .mdc-text-field .mdc-text-field__input,:host([disabled]) .mdc-text-field .mdc-text-field__input::placeholder{color:var(--mdc-text-field-disabled-ink-color, rgba(0, 0, 0, 0.38))}:host([disabled]) .mdc-text-field-helper-line .mdc-text-field-helper-text,:host([disabled]) .mdc-text-field-helper-line .mdc-text-field-character-counter{color:var(--mdc-text-field-disabled-ink-color, rgba(0, 0, 0, 0.38))}`,zv={"mwc-textfield":class extends Hv{static get styles(){return Uv}},"mwc-notched-outline":class extends Lm{static get styles(){return Fm}}};let Fv=class extends(
/**
     * @license
     * Copyright 2021 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */
function(t){return class extends t{createRenderRoot(){const t=this.constructor,{registry:e,elementDefinitions:i,shadowRootOptions:s}=t;i&&!e&&(t.registry=new CustomElementRegistry,Object.entries(i).forEach(([e,i])=>t.registry.define(e,i)));const n=this.renderOptions.creationScope=this.attachShadow({...s,customElements:t.registry});return p(n,this.constructor.elementStyles),n}}}(ht)){constructor(){super(...arguments),this._initialized=!1}setConfig(t){this._config=t,this.loadCardHelpers()}shouldUpdate(){return this._initialized||this._initialize(),!0}get _name(){var t;return(null===(t=this._config)||void 0===t?void 0:t.name)||""}get _hub(){var t;return(null===(t=this._config)||void 0===t?void 0:t.hub)||""}get _selected_schedule(){var t;return(null===(t=this._config)||void 0===t?void 0:t.selected_schedule)||""}get _theme_colors(){var t;return(null===(t=this._config)||void 0===t?void 0:t.theme_colors)||!1}get _show_badges(){var t;return(null===(t=this._config)||void 0===t?void 0:t.show_badges)||!1}get _show_schedule_id(){var t;return(null===(t=this._config)||void 0===t?void 0:t.show_schedule_id)||!1}get _display_only(){var t;return(null===(t=this._config)||void 0===t?void 0:t.display_only)||!1}get _admin_only(){var t;return(null===(t=this._config)||void 0===t?void 0:t.admin_only)||!1}get _view_type(){var t,e;return(null===(t=this._config)||void 0===t?void 0:t.view_type)?null===(e=this._config)||void 0===e?void 0:e.view_type:"default"}get _hide_card_borders(){var t;return(null===(t=this._config)||void 0===t?void 0:t.hide_card_borders)||!1}async loadData(){var t;this.hass&&(this._hubs=await(t=this.hass,t.callWS({type:"wiser/hubs"})),this._schedules=await qt(this.hass,this._hub?this._hub:this._hubs[0]))}render(){return this.hass&&this._helpers&&this._config&&this._hubs&&this._schedules?X`
      <mwc-textfield
        label="Title (optional)"
        .value=${this._name}
        .configValue=${"name"}
        @input=${this._valueChanged}
      ></mwc-textfield>
      ${this.hubSelector()}
      <mwc-select
        naturalMenuWidth
        fixedMenuPosition
        label="Schedule (Optional)"
        .configValue=${"selected_schedule"}
        .value=${this._selected_schedule}
        @selected=${this._valueChanged}
        @closed=${t=>t.stopPropagation()}
      >
        <mwc-list-item></mwc-list-item>
        ${this._schedules.map(t=>X`<mwc-list-item .value=${t.Type+"|"+t.Id}>${t.Name}</mwc-list-item>`)}
      </mwc-select>
      <mwc-select
        naturalMenuWidth
        fixedMenuPosition
        label="View"
        .configValue=${"view_type"}
        .value=${this._view_type}
        @selected=${this._valueChanged}
        @closed=${t=>t.stopPropagation()}
      >
        ${["default","list"].map(t=>{return X`<mwc-list-item .value=${t}>${e=t,e.charAt(0).toUpperCase()+e.slice(1)}</mwc-list-item>`;var e})}
      </mwc-select>
      <mwc-formfield .label=${"Only Allow Display of Schedules"}>
        <mwc-switch
          .checked=${!1!==this._display_only}
          .configValue=${"display_only"}
          @change=${this._valueChanged}
        ></mwc-switch>
      </mwc-formfield>
      <mwc-formfield .label=${"Only Allow Admin to Manage Schedules"}>
        <mwc-switch
          ?disabled=${!0===this._display_only}
          .checked=${!1!==this._admin_only}
          .configValue=${"admin_only"}
          @change=${this._valueChanged}
        ></mwc-switch>
      </mwc-formfield>
      <br />
      <mwc-formfield .label=${"Use Theme Colors"}>
        <mwc-switch
          .checked=${!1!==this._theme_colors}
          .configValue=${"theme_colors"}
          @change=${this._valueChanged}
        ></mwc-switch>
      </mwc-formfield>
      <mwc-formfield .label=${"Hide Card Borders (for stack-in cards)"}>
        <mwc-switch
          .checked=${!1!==this._hide_card_borders}
          .configValue=${"hide_card_borders"}
          @change=${this._valueChanged}
        ></mwc-switch>
      </mwc-formfield>
      <br />
      <p>Default View Options</p>
      <mwc-formfield .label=${"Show Assignment Count Badges"}>
        <mwc-switch
          .checked=${!1!==this._show_badges&&"default"==this._view_type}
          .disabled=${"default"!=this._view_type}
          .configValue=${"show_badges"}
          @change=${this._valueChanged}
        ></mwc-switch>
      </mwc-formfield>
      <mwc-formfield .label=${"Show Schedule IDs"}>
        <mwc-switch
          .checked=${!1!==this._show_schedule_id&&"default"==this._view_type}
          .disabled=${"default"!=this._view_type}
          .configValue=${"show_schedule_id"}
          @change=${this._valueChanged}
        ></mwc-switch>
      </mwc-formfield>
      <br />
      <div class="version">Version: ${$t}</div>
    `:X``}hubSelector(){var t;const e=this._hubs?this._hubs:[];return e.length>1?X`
        <mwc-select
          naturalMenuWidth
          fixedMenuPosition
          label="Wiser Hub (Optional)"
          .configValue=${"hub"}
          .value=${this._hub?this._hub:e[0]}
          @selected=${this._valueChanged}
          @closed=${t=>t.stopPropagation()}
        >
          ${null===(t=this._hubs)||void 0===t?void 0:t.map(t=>X`<mwc-list-item .value=${t}>${t}</mwc-list-item>`)}
        </mwc-select>
      `:X``}_initialize(){void 0!==this.hass&&void 0!==this._config&&void 0!==this._helpers&&(this._initialized=!0)}async loadCardHelpers(){this._helpers=await window.loadCardHelpers(),await this.loadData()}_valueChanged(t){if(!this._config||!this.hass)return;const e=t.target;if(this[`_${e.configValue}`]!==e.value){if(e.configValue)if(""===e.value){const t=Object.assign({},this._config);delete t[e.configValue],this._config=t}else this._config=Object.assign(Object.assign({},this._config),{[e.configValue]:void 0!==e.checked?e.checked:e.value});"hub"===e.configValue&&(this._config.selected_schedule=""),yt(this,"config-changed",{config:this._config})}}};return Fv.elementDefinitions=Object.assign(Object.assign(Object.assign(Object.assign({},zv),Bm),ag),$n),Fv.styles=h`
    mwc-select,
    mwc-textfield {
      margin-bottom: 16px;
      display: block;
    }
    mwc-formfield {
      padding-bottom: 20px;
      display: flex;
    }
    mwc-switch {
      --mdc-theme-secondary: var(--switch-checked-color);
    }
  `,n([gt({attribute:!1})],Fv.prototype,"hass",void 0),n([vt()],Fv.prototype,"_config",void 0),n([vt()],Fv.prototype,"_helpers",void 0),n([vt()],Fv.prototype,"_hubs",void 0),n([vt()],Fv.prototype,"_schedules",void 0),Fv=n([ut("wiser-schedule-card-editor")],Fv),console.info(`%c  WISER-SCHEDULE-CARD \n%c  ${Vt("common.version")} ${$t}    `,"color: orange; font-weight: bold; background: black","color: white; font-weight: bold; background: dimgray"),window.customCards=window.customCards||[],window.customCards.push({type:"wiser-schedule-card",name:"Wiser Schedule Card",description:"A card to manage Wiser schedules",preview:!1}),t.WiserScheduleCard=class extends ht{constructor(){super(),this._view=Et.Overview,this.translationsLoaded=!0,this.component_loaded=!1,this._schedule_id=0,this._schedule_type="heating",this.initialise()}static async getConfigElement(){return document.createElement("wiser-schedule-card-editor")}static getStubConfig(){return{}}setConfig(t){if(!t)throw new Error(Vt("common.invalid_configuration"));t.test_gui&&function(){var t=document.querySelector("home-assistant");if(t=(t=(t=(t=(t=(t=(t=(t=t&&t.shadowRoot)&&t.querySelector("home-assistant-main"))&&t.shadowRoot)&&t.querySelector("app-drawer-layout partial-panel-resolver"))&&t.shadowRoot||t)&&t.querySelector("ha-panel-lovelace"))&&t.shadowRoot)&&t.querySelector("hui-root")){var e=t.lovelace;return e.current_view=t.___curView,e}return null}().setEditMode(!0),this.config=Object.assign({name:"Wiser Schedule"},t)}set hass(t){this._hass=t}async initialise(){return await this.isComponentLoaded()&&(this.component_loaded=!0),this.processConfigSchedule(),!0}async isComponentLoaded(){for(;!this._hass||!this._hass.config.components.includes("wiser");)await new Promise(t=>setTimeout(t,100));return!0}processConfigSchedule(){this.config.selected_schedule?(this._schedule_type=this.config.selected_schedule.split("|")[0],this._schedule_id=parseInt(this.config.selected_schedule.split("|")[1]),this._view=Et.ScheduleEdit):(this._schedule_type="",this._schedule_id=0,this._view=Et.Overview)}getCardSize(){return 9}shouldUpdate(t){return!(!this.config||!this.component_loaded)&&(t.has("config")&&this.processConfigSchedule(),!!t.has("component_loaded")||(!!t.has("_view")||(!!t.has("_schedule_list")||xt(this,t,!1))))}async _handleEvent(t){if("wiser_update_received"===t.event_type){const t=new CustomEvent("wiser-update",{});this.dispatchEvent(t)}}render(){if(!this._hass||!this.config||!this.translationsLoaded)return X``;const t=this.config.hide_card_borders?"border-width: 0px":"";return this._view==Et.Overview?X`
        <ha-card style=${t} .header=${this.config.name}>
          <div class="card-content">
            <wiser-schedule-list-card
              id="schedule_list"
              .hass=${this._hass}
              .config=${this.config}
              @scheduleClick=${this._scheduleClick}
              @addScheduleClick=${this._addScheduleClick}
            ></wiser-schedule-list-card>
          </div>
        </ha-card>
      `:this._view==Et.ScheduleEdit&&this._schedule_id?X`
        <ha-card style=${t} .header=${this.config.name}>
          <div class="card-content">
            <wiser-schedule-edit-card
              .hass=${this._hass}
              .config=${this.config}
              .schedule_id=${this._schedule_id}
              .schedule_type=${this._schedule_type}
              @backClick=${this._backClick}
              @renameClick=${this._renameClick}
              @editClick=${this._editClick}
              @copyClick=${this._copyClick}
              @scheduleDeleted=${this._scheduleDeleted}
            ></wiser-schedule-edit-card>
          </div>
        </ha-card>
      `:this._view==Et.ScheduleAdd?X`
        <ha-card style=${t} .header=${this.config.name}>
          <div class="card-content">
            <wiser-schedule-add-card
              .hass=${this._hass}
              .config=${this.config}
              @backClick=${this._backClick}
              @scheduleAdded=${this._scheduleAdded}
            ></wiser-schedule-add-card>
          </div>
        </ha-card>
      `:this._view==Et.ScheduleCopy?X`
        <ha-card style=${t} .header=${this.config.name}>
          <div class="card-content">
            <wiser-schedule-copy-card
              .hass=${this._hass}
              .config=${this.config}
              .schedule_id=${this._schedule_id}
              .schedule_type=${this._schedule_type}
              @backClick=${this._backClick}
              @scheduleCopied=${this._scheduleCopied}
            ></wiser-schedule-copy-card>
          </div>
        </ha-card>
      `:this._view==Et.ScheduleRename?X`
        <ha-card style=${t} .header=${this.config.name}>
          <div class="card-content">
            <wiser-schedule-rename-card
              .hass=${this._hass}
              .config=${this.config}
              .schedule_id=${this._schedule_id}
              .schedule_type=${this._schedule_type}
              @backClick=${this._backClick}
              @scheduleRenamed=${this._scheduleRenamed}
            ></wiser-schedule-rename-card>
          </div>
        </ha-card>
      `:X``}_scheduleClick(t){this._schedule_type=t.detail.schedule_type,this._schedule_id=t.detail.schedule_id,this._view=Et.ScheduleEdit}_addScheduleClick(){this._view=Et.ScheduleAdd}_renameClick(){this._view=Et.ScheduleRename}_editClick(){this._view=Et.ScheduleEdit}_copyClick(){this._view=Et.ScheduleCopy}_backClick(t){t.detail?this._view=t.detail:this._view=Et.Overview}_scheduleDeleted(){this._view=Et.Overview}_scheduleAdded(){this._view=Et.Overview}_scheduleCopied(){this._view=Et.ScheduleEdit}_scheduleRenamed(){this._view=Et.ScheduleEdit}},n([gt({attribute:!1})],t.WiserScheduleCard.prototype,"_hass",void 0),n([vt()],t.WiserScheduleCard.prototype,"config",void 0),n([vt()],t.WiserScheduleCard.prototype,"_view",void 0),n([vt()],t.WiserScheduleCard.prototype,"translationsLoaded",void 0),n([vt()],t.WiserScheduleCard.prototype,"component_loaded",void 0),n([vt()],t.WiserScheduleCard.prototype,"_schedule_id",void 0),n([vt()],t.WiserScheduleCard.prototype,"_schedule_type",void 0),t.WiserScheduleCard=n([ut("wiser-schedule-card")],t.WiserScheduleCard),t}({});
