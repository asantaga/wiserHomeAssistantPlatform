/*! *****************************************************************************
Copyright (c) Microsoft Corporation.

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
PERFORMANCE OF THIS SOFTWARE.
***************************************************************************** */
var t=function(e,i){return t=Object.setPrototypeOf||{__proto__:[]}instanceof Array&&function(t,e){t.__proto__=e}||function(t,e){for(var i in e)Object.prototype.hasOwnProperty.call(e,i)&&(t[i]=e[i])},t(e,i)};function e(e,i){if("function"!=typeof i&&null!==i)throw new TypeError("Class extends value "+String(i)+" is not a constructor or null");function s(){this.constructor=e}t(e,i),e.prototype=null===i?Object.create(i):(s.prototype=i.prototype,new s)}var i=function(){return i=Object.assign||function(t){for(var e,i=1,s=arguments.length;i<s;i++)for(var o in e=arguments[i])Object.prototype.hasOwnProperty.call(e,o)&&(t[o]=e[o]);return t},i.apply(this,arguments)};function s(t,e,i,s){var o,n=arguments.length,r=n<3?e:null===s?s=Object.getOwnPropertyDescriptor(e,i):s;if("object"==typeof Reflect&&"function"==typeof Reflect.decorate)r=Reflect.decorate(t,e,i,s);else for(var a=t.length-1;a>=0;a--)(o=t[a])&&(r=(n<3?o(r):n>3?o(e,i,r):o(e,i))||r);return n>3&&r&&Object.defineProperty(e,i,r),r}function o(t){var e="function"==typeof Symbol&&Symbol.iterator,i=e&&t[e],s=0;if(i)return i.call(t);if(t&&"number"==typeof t.length)return{next:function(){return t&&s>=t.length&&(t=void 0),{value:t&&t[s++],done:!t}}};throw new TypeError(e?"Object is not iterable.":"Symbol.iterator is not defined.")}
/**
 * @license
 * Copyright 2019 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */const n=window.ShadowRoot&&(void 0===window.ShadyCSS||window.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,r=Symbol(),a=new Map;class l{constructor(t,e){if(this._$cssResult$=!0,e!==r)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t}get styleSheet(){let t=a.get(this.cssText);return n&&void 0===t&&(a.set(this.cssText,t=new CSSStyleSheet),t.replaceSync(this.cssText)),t}toString(){return this.cssText}}const d=(t,...e)=>{const i=1===t.length?t[0]:e.reduce(((e,i,s)=>e+(t=>{if(!0===t._$cssResult$)return t.cssText;if("number"==typeof t)return t;throw Error("Value passed to 'css' function must be a 'css' function result: "+t+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+t[s+1]),t[0]);return new l(i,r)},c=(t,e)=>{n?t.adoptedStyleSheets=e.map((t=>t instanceof CSSStyleSheet?t:t.styleSheet)):e.forEach((e=>{const i=document.createElement("style"),s=window.litNonce;void 0!==s&&i.setAttribute("nonce",s),i.textContent=e.cssText,t.appendChild(i)}))},h=n?t=>t:t=>t instanceof CSSStyleSheet?(t=>{let e="";for(const i of t.cssRules)e+=i.cssText;return(t=>new l("string"==typeof t?t:t+"",r))(e)})(t):t
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */;var u;const p=window.trustedTypes,v=p?p.emptyScript:"",m=window.reactiveElementPolyfillSupport,g={toAttribute(t,e){switch(e){case Boolean:t=t?v:null;break;case Object:case Array:t=null==t?t:JSON.stringify(t)}return t},fromAttribute(t,e){let i=t;switch(e){case Boolean:i=null!==t;break;case Number:i=null===t?null:Number(t);break;case Object:case Array:try{i=JSON.parse(t)}catch(t){i=null}}return i}},f=(t,e)=>e!==t&&(e==e||t==t),_={attribute:!0,type:String,converter:g,reflect:!1,hasChanged:f};class b extends HTMLElement{constructor(){super(),this._$Et=new Map,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Ei=null,this.o()}static addInitializer(t){var e;null!==(e=this.l)&&void 0!==e||(this.l=[]),this.l.push(t)}static get observedAttributes(){this.finalize();const t=[];return this.elementProperties.forEach(((e,i)=>{const s=this._$Eh(i,e);void 0!==s&&(this._$Eu.set(s,i),t.push(s))})),t}static createProperty(t,e=_){if(e.state&&(e.attribute=!1),this.finalize(),this.elementProperties.set(t,e),!e.noAccessor&&!this.prototype.hasOwnProperty(t)){const i="symbol"==typeof t?Symbol():"__"+t,s=this.getPropertyDescriptor(t,i,e);void 0!==s&&Object.defineProperty(this.prototype,t,s)}}static getPropertyDescriptor(t,e,i){return{get(){return this[e]},set(s){const o=this[t];this[e]=s,this.requestUpdate(t,o,i)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)||_}static finalize(){if(this.hasOwnProperty("finalized"))return!1;this.finalized=!0;const t=Object.getPrototypeOf(this);if(t.finalize(),this.elementProperties=new Map(t.elementProperties),this._$Eu=new Map,this.hasOwnProperty("properties")){const t=this.properties,e=[...Object.getOwnPropertyNames(t),...Object.getOwnPropertySymbols(t)];for(const i of e)this.createProperty(i,t[i])}return this.elementStyles=this.finalizeStyles(this.styles),!0}static finalizeStyles(t){const e=[];if(Array.isArray(t)){const i=new Set(t.flat(1/0).reverse());for(const t of i)e.unshift(h(t))}else void 0!==t&&e.push(h(t));return e}static _$Eh(t,e){const i=e.attribute;return!1===i?void 0:"string"==typeof i?i:"string"==typeof t?t.toLowerCase():void 0}o(){var t;this._$Ep=new Promise((t=>this.enableUpdating=t)),this._$AL=new Map,this._$Em(),this.requestUpdate(),null===(t=this.constructor.l)||void 0===t||t.forEach((t=>t(this)))}addController(t){var e,i;(null!==(e=this._$Eg)&&void 0!==e?e:this._$Eg=[]).push(t),void 0!==this.renderRoot&&this.isConnected&&(null===(i=t.hostConnected)||void 0===i||i.call(t))}removeController(t){var e;null===(e=this._$Eg)||void 0===e||e.splice(this._$Eg.indexOf(t)>>>0,1)}_$Em(){this.constructor.elementProperties.forEach(((t,e)=>{this.hasOwnProperty(e)&&(this._$Et.set(e,this[e]),delete this[e])}))}createRenderRoot(){var t;const e=null!==(t=this.shadowRoot)&&void 0!==t?t:this.attachShadow(this.constructor.shadowRootOptions);return c(e,this.constructor.elementStyles),e}connectedCallback(){var t;void 0===this.renderRoot&&(this.renderRoot=this.createRenderRoot()),this.enableUpdating(!0),null===(t=this._$Eg)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostConnected)||void 0===e?void 0:e.call(t)}))}enableUpdating(t){}disconnectedCallback(){var t;null===(t=this._$Eg)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostDisconnected)||void 0===e?void 0:e.call(t)}))}attributeChangedCallback(t,e,i){this._$AK(t,i)}_$ES(t,e,i=_){var s,o;const n=this.constructor._$Eh(t,i);if(void 0!==n&&!0===i.reflect){const r=(null!==(o=null===(s=i.converter)||void 0===s?void 0:s.toAttribute)&&void 0!==o?o:g.toAttribute)(e,i.type);this._$Ei=t,null==r?this.removeAttribute(n):this.setAttribute(n,r),this._$Ei=null}}_$AK(t,e){var i,s,o;const n=this.constructor,r=n._$Eu.get(t);if(void 0!==r&&this._$Ei!==r){const t=n.getPropertyOptions(r),a=t.converter,l=null!==(o=null!==(s=null===(i=a)||void 0===i?void 0:i.fromAttribute)&&void 0!==s?s:"function"==typeof a?a:null)&&void 0!==o?o:g.fromAttribute;this._$Ei=r,this[r]=l(e,t.type),this._$Ei=null}}requestUpdate(t,e,i){let s=!0;void 0!==t&&(((i=i||this.constructor.getPropertyOptions(t)).hasChanged||f)(this[t],e)?(this._$AL.has(t)||this._$AL.set(t,e),!0===i.reflect&&this._$Ei!==t&&(void 0===this._$EC&&(this._$EC=new Map),this._$EC.set(t,i))):s=!1),!this.isUpdatePending&&s&&(this._$Ep=this._$E_())}async _$E_(){this.isUpdatePending=!0;try{await this._$Ep}catch(t){Promise.reject(t)}const t=this.scheduleUpdate();return null!=t&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){var t;if(!this.isUpdatePending)return;this.hasUpdated,this._$Et&&(this._$Et.forEach(((t,e)=>this[e]=t)),this._$Et=void 0);let e=!1;const i=this._$AL;try{e=this.shouldUpdate(i),e?(this.willUpdate(i),null===(t=this._$Eg)||void 0===t||t.forEach((t=>{var e;return null===(e=t.hostUpdate)||void 0===e?void 0:e.call(t)})),this.update(i)):this._$EU()}catch(t){throw e=!1,this._$EU(),t}e&&this._$AE(i)}willUpdate(t){}_$AE(t){var e;null===(e=this._$Eg)||void 0===e||e.forEach((t=>{var e;return null===(e=t.hostUpdated)||void 0===e?void 0:e.call(t)})),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EU(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$Ep}shouldUpdate(t){return!0}update(t){void 0!==this._$EC&&(this._$EC.forEach(((t,e)=>this._$ES(e,this[e],t))),this._$EC=void 0),this._$EU()}updated(t){}firstUpdated(t){}}
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
var y;b.finalized=!0,b.elementProperties=new Map,b.elementStyles=[],b.shadowRootOptions={mode:"open"},null==m||m({ReactiveElement:b}),(null!==(u=globalThis.reactiveElementVersions)&&void 0!==u?u:globalThis.reactiveElementVersions=[]).push("1.3.2");const w=globalThis.trustedTypes,x=w?w.createPolicy("lit-html",{createHTML:t=>t}):void 0,$=`lit$${(Math.random()+"").slice(9)}$`,S="?"+$,C=`<${S}>`,k=document,E=(t="")=>k.createComment(t),A=t=>null===t||"object"!=typeof t&&"function"!=typeof t,M=Array.isArray,L=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,D=/-->/g,T=/>/g,O=/>|[ 	\n\r](?:([^\s"'>=/]+)([ 	\n\r]*=[ 	\n\r]*(?:[^ 	\n\r"'`<>=]|("|')|))|$)/g,z=/'/g,N=/"/g,P=/^(?:script|style|textarea|title)$/i,H=(t=>(e,...i)=>({_$litType$:t,strings:e,values:i}))(1),U=Symbol.for("lit-noChange"),I=Symbol.for("lit-nothing"),V=new WeakMap,j=k.createTreeWalker(k,129,null,!1),B=(t,e)=>{const i=t.length-1,s=[];let o,n=2===e?"<svg>":"",r=L;for(let e=0;e<i;e++){const i=t[e];let a,l,d=-1,c=0;for(;c<i.length&&(r.lastIndex=c,l=r.exec(i),null!==l);)c=r.lastIndex,r===L?"!--"===l[1]?r=D:void 0!==l[1]?r=T:void 0!==l[2]?(P.test(l[2])&&(o=RegExp("</"+l[2],"g")),r=O):void 0!==l[3]&&(r=O):r===O?">"===l[0]?(r=null!=o?o:L,d=-1):void 0===l[1]?d=-2:(d=r.lastIndex-l[2].length,a=l[1],r=void 0===l[3]?O:'"'===l[3]?N:z):r===N||r===z?r=O:r===D||r===T?r=L:(r=O,o=void 0);const h=r===O&&t[e+1].startsWith("/>")?" ":"";n+=r===L?i+C:d>=0?(s.push(a),i.slice(0,d)+"$lit$"+i.slice(d)+$+h):i+$+(-2===d?(s.push(void 0),e):h)}const a=n+(t[i]||"<?>")+(2===e?"</svg>":"");if(!Array.isArray(t)||!t.hasOwnProperty("raw"))throw Error("invalid template strings array");return[void 0!==x?x.createHTML(a):a,s]};class R{constructor({strings:t,_$litType$:e},i){let s;this.parts=[];let o=0,n=0;const r=t.length-1,a=this.parts,[l,d]=B(t,e);if(this.el=R.createElement(l,i),j.currentNode=this.el.content,2===e){const t=this.el.content,e=t.firstChild;e.remove(),t.append(...e.childNodes)}for(;null!==(s=j.nextNode())&&a.length<r;){if(1===s.nodeType){if(s.hasAttributes()){const t=[];for(const e of s.getAttributeNames())if(e.endsWith("$lit$")||e.startsWith($)){const i=d[n++];if(t.push(e),void 0!==i){const t=s.getAttribute(i.toLowerCase()+"$lit$").split($),e=/([.?@])?(.*)/.exec(i);a.push({type:1,index:o,name:e[2],strings:t,ctor:"."===e[1]?Z:"?"===e[1]?K:"@"===e[1]?X:q})}else a.push({type:6,index:o})}for(const e of t)s.removeAttribute(e)}if(P.test(s.tagName)){const t=s.textContent.split($),e=t.length-1;if(e>0){s.textContent=w?w.emptyScript:"";for(let i=0;i<e;i++)s.append(t[i],E()),j.nextNode(),a.push({type:2,index:++o});s.append(t[e],E())}}}else if(8===s.nodeType)if(s.data===S)a.push({type:2,index:o});else{let t=-1;for(;-1!==(t=s.data.indexOf($,t+1));)a.push({type:7,index:o}),t+=$.length-1}o++}}static createElement(t,e){const i=k.createElement("template");return i.innerHTML=t,i}}function Y(t,e,i=t,s){var o,n,r,a;if(e===U)return e;let l=void 0!==s?null===(o=i._$Cl)||void 0===o?void 0:o[s]:i._$Cu;const d=A(e)?void 0:e._$litDirective$;return(null==l?void 0:l.constructor)!==d&&(null===(n=null==l?void 0:l._$AO)||void 0===n||n.call(l,!1),void 0===d?l=void 0:(l=new d(t),l._$AT(t,i,s)),void 0!==s?(null!==(r=(a=i)._$Cl)&&void 0!==r?r:a._$Cl=[])[s]=l:i._$Cu=l),void 0!==l&&(e=Y(t,l._$AS(t,e.values),l,s)),e}class W{constructor(t,e){this.v=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}p(t){var e;const{el:{content:i},parts:s}=this._$AD,o=(null!==(e=null==t?void 0:t.creationScope)&&void 0!==e?e:k).importNode(i,!0);j.currentNode=o;let n=j.nextNode(),r=0,a=0,l=s[0];for(;void 0!==l;){if(r===l.index){let e;2===l.type?e=new F(n,n.nextSibling,this,t):1===l.type?e=new l.ctor(n,l.name,l.strings,this,t):6===l.type&&(e=new G(n,this,t)),this.v.push(e),l=s[++a]}r!==(null==l?void 0:l.index)&&(n=j.nextNode(),r++)}return o}m(t){let e=0;for(const i of this.v)void 0!==i&&(void 0!==i.strings?(i._$AI(t,i,e),e+=i.strings.length-2):i._$AI(t[e])),e++}}class F{constructor(t,e,i,s){var o;this.type=2,this._$AH=I,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=i,this.options=s,this._$Cg=null===(o=null==s?void 0:s.isConnected)||void 0===o||o}get _$AU(){var t,e;return null!==(e=null===(t=this._$AM)||void 0===t?void 0:t._$AU)&&void 0!==e?e:this._$Cg}get parentNode(){let t=this._$AA.parentNode;const e=this._$AM;return void 0!==e&&11===t.nodeType&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=Y(this,t,e),A(t)?t===I||null==t||""===t?(this._$AH!==I&&this._$AR(),this._$AH=I):t!==this._$AH&&t!==U&&this.$(t):void 0!==t._$litType$?this.T(t):void 0!==t.nodeType?this.k(t):(t=>{var e;return M(t)||"function"==typeof(null===(e=t)||void 0===e?void 0:e[Symbol.iterator])})(t)?this.S(t):this.$(t)}M(t,e=this._$AB){return this._$AA.parentNode.insertBefore(t,e)}k(t){this._$AH!==t&&(this._$AR(),this._$AH=this.M(t))}$(t){this._$AH!==I&&A(this._$AH)?this._$AA.nextSibling.data=t:this.k(k.createTextNode(t)),this._$AH=t}T(t){var e;const{values:i,_$litType$:s}=t,o="number"==typeof s?this._$AC(t):(void 0===s.el&&(s.el=R.createElement(s.h,this.options)),s);if((null===(e=this._$AH)||void 0===e?void 0:e._$AD)===o)this._$AH.m(i);else{const t=new W(o,this),e=t.p(this.options);t.m(i),this.k(e),this._$AH=t}}_$AC(t){let e=V.get(t.strings);return void 0===e&&V.set(t.strings,e=new R(t)),e}S(t){M(this._$AH)||(this._$AH=[],this._$AR());const e=this._$AH;let i,s=0;for(const o of t)s===e.length?e.push(i=new F(this.M(E()),this.M(E()),this,this.options)):i=e[s],i._$AI(o),s++;s<e.length&&(this._$AR(i&&i._$AB.nextSibling,s),e.length=s)}_$AR(t=this._$AA.nextSibling,e){var i;for(null===(i=this._$AP)||void 0===i||i.call(this,!1,!0,e);t&&t!==this._$AB;){const e=t.nextSibling;t.remove(),t=e}}setConnected(t){var e;void 0===this._$AM&&(this._$Cg=t,null===(e=this._$AP)||void 0===e||e.call(this,t))}}class q{constructor(t,e,i,s,o){this.type=1,this._$AH=I,this._$AN=void 0,this.element=t,this.name=e,this._$AM=s,this.options=o,i.length>2||""!==i[0]||""!==i[1]?(this._$AH=Array(i.length-1).fill(new String),this.strings=i):this._$AH=I}get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}_$AI(t,e=this,i,s){const o=this.strings;let n=!1;if(void 0===o)t=Y(this,t,e,0),n=!A(t)||t!==this._$AH&&t!==U,n&&(this._$AH=t);else{const s=t;let r,a;for(t=o[0],r=0;r<o.length-1;r++)a=Y(this,s[i+r],e,r),a===U&&(a=this._$AH[r]),n||(n=!A(a)||a!==this._$AH[r]),a===I?t=I:t!==I&&(t+=(null!=a?a:"")+o[r+1]),this._$AH[r]=a}n&&!s&&this.C(t)}C(t){t===I?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,null!=t?t:"")}}class Z extends q{constructor(){super(...arguments),this.type=3}C(t){this.element[this.name]=t===I?void 0:t}}const J=w?w.emptyScript:"";class K extends q{constructor(){super(...arguments),this.type=4}C(t){t&&t!==I?this.element.setAttribute(this.name,J):this.element.removeAttribute(this.name)}}class X extends q{constructor(t,e,i,s,o){super(t,e,i,s,o),this.type=5}_$AI(t,e=this){var i;if((t=null!==(i=Y(this,t,e,0))&&void 0!==i?i:I)===U)return;const s=this._$AH,o=t===I&&s!==I||t.capture!==s.capture||t.once!==s.once||t.passive!==s.passive,n=t!==I&&(s===I||o);o&&this.element.removeEventListener(this.name,this,s),n&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){var e,i;"function"==typeof this._$AH?this._$AH.call(null!==(i=null===(e=this.options)||void 0===e?void 0:e.host)&&void 0!==i?i:this.element,t):this._$AH.handleEvent(t)}}class G{constructor(t,e,i){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=i}get _$AU(){return this._$AM._$AU}_$AI(t){Y(this,t)}}const Q=window.litHtmlPolyfillSupport;
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
var tt,et;null==Q||Q(R,F),(null!==(y=globalThis.litHtmlVersions)&&void 0!==y?y:globalThis.litHtmlVersions=[]).push("2.2.3");class it extends b{constructor(){super(...arguments),this.renderOptions={host:this},this._$Dt=void 0}createRenderRoot(){var t,e;const i=super.createRenderRoot();return null!==(t=(e=this.renderOptions).renderBefore)&&void 0!==t||(e.renderBefore=i.firstChild),i}update(t){const e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Dt=((t,e,i)=>{var s,o;const n=null!==(s=null==i?void 0:i.renderBefore)&&void 0!==s?s:e;let r=n._$litPart$;if(void 0===r){const t=null!==(o=null==i?void 0:i.renderBefore)&&void 0!==o?o:null;n._$litPart$=r=new F(e.insertBefore(E(),t),t,void 0,null!=i?i:{})}return r._$AI(t),r})(e,this.renderRoot,this.renderOptions)}connectedCallback(){var t;super.connectedCallback(),null===(t=this._$Dt)||void 0===t||t.setConnected(!0)}disconnectedCallback(){var t;super.disconnectedCallback(),null===(t=this._$Dt)||void 0===t||t.setConnected(!1)}render(){return U}}it.finalized=!0,it._$litElement$=!0,null===(tt=globalThis.litElementHydrateSupport)||void 0===tt||tt.call(globalThis,{LitElement:it});const st=globalThis.litElementPolyfillSupport;null==st||st({LitElement:it}),(null!==(et=globalThis.litElementVersions)&&void 0!==et?et:globalThis.litElementVersions=[]).push("3.2.0");
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const ot=t=>e=>"function"==typeof e?((t,e)=>(window.customElements.define(t,e),e))(t,e):((t,e)=>{const{kind:i,elements:s}=e;return{kind:i,elements:s,finisher(e){window.customElements.define(t,e)}}})(t,e)
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */,nt=(t,e)=>"method"===e.kind&&e.descriptor&&!("value"in e.descriptor)?{...e,finisher(i){i.createProperty(e.key,t)}}:{kind:"field",key:Symbol(),placement:"own",descriptor:{},originalKey:e.key,initializer(){"function"==typeof e.initializer&&(this[e.key]=e.initializer.call(this))},finisher(i){i.createProperty(e.key,t)}};function rt(t){return(e,i)=>void 0!==i?((t,e,i)=>{e.constructor.createProperty(i,t)})(t,e,i):nt(t,e)
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */}function at(t){return rt({...t,state:!0})}
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */const lt=({finisher:t,descriptor:e})=>(i,s)=>{var o;if(void 0===s){const s=null!==(o=i.originalKey)&&void 0!==o?o:i.key,n=null!=e?{kind:"method",placement:"prototype",key:s,descriptor:e(i.key)}:{...i,key:s};return null!=t&&(n.finisher=function(e){t(e,s)}),n}{const o=i.constructor;void 0!==e&&Object.defineProperty(i,s,e(s)),null==t||t(o,s)}}
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */;function dt(t){return lt({finisher:(e,i)=>{Object.assign(e.prototype[i],t)}})}
/**
 * @license
 * Copyright 2021 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */var ct;const ht=null!=(null===(ct=window.HTMLSlotElement)||void 0===ct?void 0:ct.prototype.assignedElements)?(t,e)=>t.assignedElements(e):(t,e)=>t.assignedNodes(e).filter((t=>t.nodeType===Node.ELEMENT_NODE));function ut(t){const{slot:e,selector:i}=null!=t?t:{};return lt({descriptor:s=>({get(){var s;const o="slot"+(e?`[name=${e}]`:":not([name])"),n=null===(s=this.renderRoot)||void 0===s?void 0:s.querySelector(o),r=null!=n?ht(n,t):[];return i?r.filter((t=>t.matches(i))):r},enumerable:!0,configurable:!0})})}var pt=/d{1,4}|M{1,4}|YY(?:YY)?|S{1,3}|Do|ZZ|Z|([HhMsDm])\1?|[aA]|"[^"]*"|'[^']*'/g,vt="[^\\s]+",mt=/\[([^]*?)\]/gm;function gt(t,e){for(var i=[],s=0,o=t.length;s<o;s++)i.push(t[s].substr(0,e));return i}var ft=function(t){return function(e,i){var s=i[t].map((function(t){return t.toLowerCase()})),o=s.indexOf(e.toLowerCase());return o>-1?o:null}};function _t(t){for(var e=[],i=1;i<arguments.length;i++)e[i-1]=arguments[i];for(var s=0,o=e;s<o.length;s++){var n=o[s];for(var r in n)t[r]=n[r]}return t}var bt=["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"],yt=["January","February","March","April","May","June","July","August","September","October","November","December"],wt=gt(yt,3),xt={dayNamesShort:gt(bt,3),dayNames:bt,monthNamesShort:wt,monthNames:yt,amPm:["am","pm"],DoFn:function(t){return t+["th","st","nd","rd"][t%10>3?0:(t-t%10!=10?1:0)*t%10]}},$t=_t({},xt),St=function(t,e){for(void 0===e&&(e=2),t=String(t);t.length<e;)t="0"+t;return t},Ct={D:function(t){return String(t.getDate())},DD:function(t){return St(t.getDate())},Do:function(t,e){return e.DoFn(t.getDate())},d:function(t){return String(t.getDay())},dd:function(t){return St(t.getDay())},ddd:function(t,e){return e.dayNamesShort[t.getDay()]},dddd:function(t,e){return e.dayNames[t.getDay()]},M:function(t){return String(t.getMonth()+1)},MM:function(t){return St(t.getMonth()+1)},MMM:function(t,e){return e.monthNamesShort[t.getMonth()]},MMMM:function(t,e){return e.monthNames[t.getMonth()]},YY:function(t){return St(String(t.getFullYear()),4).substr(2)},YYYY:function(t){return St(t.getFullYear(),4)},h:function(t){return String(t.getHours()%12||12)},hh:function(t){return St(t.getHours()%12||12)},H:function(t){return String(t.getHours())},HH:function(t){return St(t.getHours())},m:function(t){return String(t.getMinutes())},mm:function(t){return St(t.getMinutes())},s:function(t){return String(t.getSeconds())},ss:function(t){return St(t.getSeconds())},S:function(t){return String(Math.round(t.getMilliseconds()/100))},SS:function(t){return St(Math.round(t.getMilliseconds()/10),2)},SSS:function(t){return St(t.getMilliseconds(),3)},a:function(t,e){return t.getHours()<12?e.amPm[0]:e.amPm[1]},A:function(t,e){return t.getHours()<12?e.amPm[0].toUpperCase():e.amPm[1].toUpperCase()},ZZ:function(t){var e=t.getTimezoneOffset();return(e>0?"-":"+")+St(100*Math.floor(Math.abs(e)/60)+Math.abs(e)%60,4)},Z:function(t){var e=t.getTimezoneOffset();return(e>0?"-":"+")+St(Math.floor(Math.abs(e)/60),2)+":"+St(Math.abs(e)%60,2)}},kt=function(t){return+t-1},Et=[null,"[1-9]\\d?"],At=[null,vt],Mt=["isPm",vt,function(t,e){var i=t.toLowerCase();return i===e.amPm[0]?0:i===e.amPm[1]?1:null}],Lt=["timezoneOffset","[^\\s]*?[\\+\\-]\\d\\d:?\\d\\d|[^\\s]*?Z?",function(t){var e=(t+"").match(/([+-]|\d\d)/gi);if(e){var i=60*+e[1]+parseInt(e[2],10);return"+"===e[0]?i:-i}return 0}],Dt=(ft("monthNamesShort"),ft("monthNames"),{default:"ddd MMM DD YYYY HH:mm:ss",shortDate:"M/D/YY",mediumDate:"MMM D, YYYY",longDate:"MMMM D, YYYY",fullDate:"dddd, MMMM D, YYYY",isoDate:"YYYY-MM-DD",isoDateTime:"YYYY-MM-DDTHH:mm:ssZ",shortTime:"HH:mm",mediumTime:"HH:mm:ss",longTime:"HH:mm:ss.SSS"}),Tt=function(t,e,i){if(void 0===e&&(e=Dt.default),void 0===i&&(i={}),"number"==typeof t&&(t=new Date(t)),"[object Date]"!==Object.prototype.toString.call(t)||isNaN(t.getTime()))throw new Error("Invalid Date pass to format");var s=[];e=(e=Dt[e]||e).replace(mt,(function(t,e){return s.push(e),"@@@"}));var o=_t(_t({},$t),i);return(e=e.replace(pt,(function(e){return Ct[e](t,o)}))).replace(/@@@/g,(function(){return s.shift()}))};var Ot,zt;!function(){try{(new Date).toLocaleDateString("i")}catch(t){return"RangeError"===t.name}}(),function(){try{(new Date).toLocaleString("i")}catch(t){return"RangeError"===t.name}}(),function(){try{(new Date).toLocaleTimeString("i")}catch(t){return"RangeError"===t.name}}(),function(t){t.language="language",t.system="system",t.comma_decimal="comma_decimal",t.decimal_comma="decimal_comma",t.space_comma="space_comma",t.none="none"}(Ot||(Ot={})),function(t){t.language="language",t.system="system",t.am_pm="12",t.twenty_four="24"}(zt||(zt={}));var Nt=function(t,e,i,s){s=s||{},i=null==i?{}:i;var o=new Event(e,{bubbles:void 0===s.bubbles||s.bubbles,cancelable:Boolean(s.cancelable),composed:void 0===s.composed||s.composed});return o.detail=i,t.dispatchEvent(o),o};function Pt(t,e,i){if(e.has("config")||i)return!0;if(t.config.entity){var s=e.get("hass");return!s||s.states[t.config.entity]!==t.hass.states[t.config.entity]}return!1}var Ht,Ut,It;!function(t){t.Heating="mdi:radiator",t.OnOff="mdi:power-socket-uk",t.Shutters="mdi:blinds",t.Lighting="mdi:lightbulb-outline"}(Ht||(Ht={})),function(t){t.Overview="OVERVIEW",t.ScheduleEdit="SCHEDULE_EDIT",t.ScheduleCopy="SCHEDULE_COPY",t.ScheduleAdd="SCHEDULE_ADD"}(Ut||(Ut={})),function(t){t.Heating="19",t.OnOff="Off",t.Lighting="0",t.Shutters="100"}(It||(It={}));const Vt=["Heating","OnOff","Lighting","Shutters"],jt=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],Bt=["Mon","Tue","Wed","Thu","Fri","Sat","Sun"];var Rt={version:"Version",invalid_configuration:"Invalid configuration",show_warning:"Show Warning",show_error:"Show Error"},Yt={common:Rt},Wt={version:"Versjon",invalid_configuration:"Ikke gyldig konfiguration",show_warning:"Vis advarsel"},Ft={common:Wt};const qt={en:Object.freeze({__proto__:null,common:Rt,default:Yt}),nb:Object.freeze({__proto__:null,common:Wt,default:Ft})};function Zt(t,e="",i=""){const s=(localStorage.getItem("selectedLanguage")||"en").replace(/['"]+/g,"").replace("-","_");let o;try{o=t.split(".").reduce(((t,e)=>t[e]),qt[s])}catch(e){o=t.split(".").reduce(((t,e)=>t[e]),qt.en)}return void 0===o&&(o=t.split(".").reduce(((t,e)=>t[e]),qt.en)),""!==e&&""!==i&&(o=o.replace(e,i)),o}const Jt=d`
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
    div.text-field, div.secondary {
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
      grid-template-areas: "checkbox slider value";
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
  `,Kt=t=>t.callWS({type:"wiser/hubs"}),Xt=(t,e)=>t.callWS({type:"wiser/schedules/types",hub:e}),Gt=(t,e,i="")=>t.callWS({type:"wiser/schedules",hub:e,schedule_type:i}),Qt=(t,e,i,s)=>t.callWS({type:"wiser/schedule/id",hub:e,schedule_type:i,schedule_id:s}),te=new RegExp("[^#a-f\\d]","gi"),ee=new RegExp("^#?[a-f\\d]{3}[a-f\\d]?$|^#?[a-f\\d]{6}([a-f\\d]{2})?$","i");const ie=Math.trunc;function se(t){if(function(t){return 6===(t=String(t).replace("#","")).length&&!isNaN(Number("0x"+t))}(t)){const e=function(t,e={}){if("string"!=typeof t||te.test(t)||!ee.test(t))throw new TypeError("Expected a valid hex string");let i=1;8===(t=t.replace(/^#/,"")).length&&(i=Number.parseInt(t.slice(6,8),16)/255,t=t.slice(0,6)),4===t.length&&(i=Number.parseInt(t.slice(3,4).repeat(2),16)/255,t=t.slice(0,3)),3===t.length&&(t=t[0]+t[0]+t[1]+t[1]+t[2]+t[2]);const s=Number.parseInt(t,16),o=s>>16,n=s>>8&255,r=255&s,a="number"==typeof e.alpha?e.alpha:i;if("array"===e.format)return[o,n,r,a];if("css"===e.format)return`rgb(${o} ${n} ${r}${1===a?"":` / ${Number((100*a).toFixed(2))}%`})`;return{red:o,green:n,blue:r,alpha:a}}(t);return String(e.red+","+e.green+","+e.blue+","+e.alpha)}return"100,100,100"}function oe(t,e){return getComputedStyle(t).getPropertyValue(e).trim()}function ne(t,e,i){if("onoff"===e.toLowerCase())return se(oe(t,"On"==i?"--state-on-color":"--state-off-color"));if(["lighting","shutters"].includes(e.toLowerCase()))return(0==(s=parseInt(i))?"50,50,50":ie(50+2*s)+","+ie(50+1.5*s)+",0")+",1";{if(-20==i)return"138, 138, 138";const t=5,e=(i-t)/(25-t);return 255+","+Math.floor(255*(1-e))+","+0+",1"}var s}function re(t,e){return!e.display_only&&!!(e.admin_only&&t.user.is_admin||!e.admin_only)}function ae(t,e){return 0==t.slots.length||t.slots.length-1==e?"24:00":t.slots[e+1].Time}function le(t,e,i){return-1==e?function(t,e){const i=[...jt.slice(jt.indexOf(t.day)+1),...jt.slice(0,jt.indexOf(t.day))].reverse();for(t of i){const i=e.ScheduleData.filter((e=>e.day==t))[0];if(i.slots.length>0)return i.slots[i.slots.length-1].Setpoint}return""}(t,i):t.slots[e].Setpoint}function de(t){const[e,i]=t.split(":");return 3600*+e+60*+i}const ce=t=>t.locale||{language:t.language,number_format:Ot.system};let he=class extends it{async showDialog(t){this._params=t,await this.updateComplete}async closeDialog(){this._params&&this._params.cancel(),this._params=void 0}render(){return this._params?H`
      <ha-dialog open .heading=${!0} @closed=${this.closeDialog} @close-dialog=${this.closeDialog}>
        <div slot="heading">
          <ha-header-bar>
            <ha-icon-button slot="navigationIcon" dialogAction="cancel" .path=${"M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"}> </ha-icon-button>
            <span slot="title">
              ${"Confirm Delete"}
            </span>
          </ha-header-bar>
        </div>
        <div class="wrapper">
          ${"Are you sure you wish to delete the schedule "+this._params.name+"?"}
        </div>
        <mwc-button class="warning" slot="primaryAction" style="float: left" @click=${this.confirmClick} dialogAction="close">
          ${"Delete"}
        </mwc-button>
        <mwc-button slot="secondaryAction" @click=${this.cancelClick} dialogAction="close">
          ${"Cancel"}
        </mwc-button>
      </ha-dialog>
    `:H``}confirmClick(){this._params.confirm()}cancelClick(){this._params.cancel()}static get styles(){return d`
      div.wrapper {
        color: var(--primary-text-color);
      }
      mwc-button.warning
        {
          --mdc-theme-primary: var(--error-color);
        }
    `}};s([rt({attribute:!1})],he.prototype,"hass",void 0),s([at()],he.prototype,"_params",void 0),he=s([ot("dialog-delete-confirm")],he);var ue=Object.freeze({__proto__:null,get DialogDeleteConfirm(){return he}});const pe=t=>{class e extends t{connectedCallback(){super.connectedCallback(),this.__checkSubscribed()}disconnectedCallback(){if(super.disconnectedCallback(),this.__unsubs){for(;this.__unsubs.length;){const t=this.__unsubs.pop();t instanceof Promise?t.then((t=>t())):t()}this.__unsubs=void 0}}updated(t){super.updated(t),t.has("hass")&&this.__checkSubscribed()}hassSubscribe(){return[]}__checkSubscribed(){void 0===this.__unsubs&&this.isConnected&&void 0!==this.hass&&(this.__unsubs=this.hassSubscribe())}}return s([rt({attribute:!1})],e.prototype,"hass",void 0),e};let ve=class extends(pe(it)){constructor(){super(...arguments),this.component_loaded=!1,this.connectionError=!1}async initialise(){return await this.isComponentLoaded()&&(this.component_loaded=!0,await this.loadData()),!0}async isComponentLoaded(){for(;!this.hass||!this.hass.config.components.includes("wiser");)await new Promise((t=>setTimeout(t,100)));return!0}hassSubscribe(){return this.initialise(),[this.hass.connection.subscribeMessage((t=>this.handleUpdate(t)),{type:"wiser_updated"})]}async handleUpdate(t){"wiser_updated"==t.event&&await this.loadData()}async loadData(){this.supported_schedule_types=await Xt(this.hass,this.config.hub),this.schedule_list=await Gt(this.hass,this.config.hub)}shouldUpdate(t){return!!t.has("schedule_list")||!!Pt(this,t,!1)&&(this.loadData(),!0)}render(){return this.hass&&this.config?this.schedule_list&&this.schedule_list.length>0?H`
                <ha-card>
                    <div class="card-header">
                        <div class="name">
                            ${this.config.name}
                        </div>
                    </div>
                    <div class="card-content">
                        <div class="info-text">
                            Select a schedule to view
                        </div>
                        ${this.supported_schedule_types.map((t=>this.renderScheduleItemsByType(t)))}
                    </div>
                    ${this.renderAddScheduleButton()}
                </ha-card>
            `:H`
                <ha-card>
                    <div class="card-header">
                        <div class="name">
                            ${this.config.name}
                        </div>
                    </div>
                    <div class="card-content">
                        ${this._showWarning("No schedules found")}
                        </div>
                    </div>
                </ha-card>
            `:H``}_showWarning(t){return H` <hui-warning>${t}</hui-warning> `}renderScheduleItemsByType(t){const e=this.schedule_list.filter((e=>e.Type===t));return e.length>0?H`
                <div class="sub-heading"></div>
                <div class = "wrapper">
                    ${e.map((t=>this.renderScheduleItem(t)))}
                </div>
            `:H``}renderScheduleItem(t){var e;const i=Ht[t.Type];return H`
            <div class="schedule-item"
                id = ${"schedule"+t.Id}
                @click=${()=>this._scheduleClick(t.Type,t.Id)}
            >
                <ha-icon .icon="${function(t){if(t)return"string"!=typeof t&&(t=String(t)),t.match(/^[a-z]+:[a-z0-9-]+$/i)?t:`hass:${t}`}(i)}"></ha-icon>
                <span class="button-label">${t.Name}</span>
                ${(null===(e=this.config)||void 0===e?void 0:e.show_badges)?H`<span class="badge">${t.Assignments}</span>`:null}
            </div>
        `}renderAddScheduleButton(){if(re(this.hass,this.config))return H`
                <div class="card-actions">
                    <mwc-button @click=${this._addScheduleClick}
                    >Add Schedule
                    </mwc-button>
                </div>
            `}async _addScheduleClick(){const t=new CustomEvent("addScheduleClick");this.dispatchEvent(t)}_scheduleClick(t,e){const i=new CustomEvent("scheduleClick",{detail:{schedule_type:t,schedule_id:e}});this.dispatchEvent(i)}};ve.styles=d`
    ${Jt}
    div.info-text {
        margin-bottom: 10px;
    }
    span.button-label {
        padding-left:5px;
        text-transform: uppercase;
        font-weight: 500;
    }
    div.wrapper {
        white-space: nowrap;
        transition: width 0.2s cubic-bezier(0.17, 0.67, 0.83, 0.67),
        margin 0.2s cubic-bezier(0.17, 0.67, 0.83, 0.67);
        overflow: auto;
        display: flex;
        flex-wrap: wrap;
        flex-direction: row;
        justify-content: flex-start;
        }
    div.sub-heading {
        display:block;
        border-bottom: 1px solid var(--divider-color, #e8e8e8);
        margin: 5px 0;
    }

    div.schedule-item ha-icon {
        float: left;
        cursor: pointer;

    }
    .schedule-item {
        line-height: 32px;
        cursor: pointer;
        /*overflow: hidden;*/
        white-space: nowrap;
        text-overflow: ellipsis;
        margin: 5px 10px 5px 0px;
        display: flex;
        padding: 2px 10px 2px 5px;
        color: var(--mdc-theme-primary, #6200ee);
        background: var(--primary-color);
        --mdc-theme-primary: var(--text-primary-color);
        border-radius: 4px;
        font-size: var(--material-button-font-size);
        position: relative;
    }
    .badge {
        font-size: small;
        position: absolute;
        top: -5px;
        right: -8px;
        background-color: var(--label-badge-red);
        width: 20px;
        height: 20px;
        border-radius: 50%;
        line-height: 20px;
        text-align: center;
    }
    `,s([rt()],ve.prototype,"config",void 0),s([rt()],ve.prototype,"schedule_list",void 0),s([rt()],ve.prototype,"component_loaded",void 0),ve=s([ot("schedule-list-card")],ve);class me{}function ge(t,e){if(t.match(/^([0-9:]+)$/)){const e=t.split(":").map(Number);return 3600*e[0]+60*e[1]+(e[2]||0)}const i=be(t);if(i){const t=e.states["sun.sun"],s=ge(t.attributes.next_rising,e),o=ge(t.attributes.next_setting,e);let n="sunrise"==i.event?s:o;return n="+"==i.sign?n+ge(i.offset,e):n-ge(i.offset,e),n}const s=new Date(t);return 3600*s.getHours()+60*s.getMinutes()+s.getSeconds()}function fe(t){const e=Math.floor(t/3600);t-=3600*e;const i=Math.floor(t/60);t-=60*i;const s=Math.round(t);return String(e%24).padStart(2,"0")+":"+String(i).padStart(2,"0")+":"+String(s).padStart(2,"0")}function _e(t,e,i={wrapAround:!0}){let s=t>=0?Math.floor(t/3600):Math.ceil(t/3600),o=Math.floor((t-3600*s)/60);o%e!=0&&(o=Math.round(o/e)*e),o>=60?(s++,o-=60):o<0&&(s--,o+=60),i.wrapAround&&(s>=24?s-=24:s<0&&(s+=24));const n=3600*s+60*o;if(i.maxHours){if(n>3600*i.maxHours)return 3600*i.maxHours;if(n<3600*-i.maxHours)return 3600*-i.maxHours}return n}function be(t){const e=t.match(/^([a-z]+)([\+|-]{1})([0-9:]+)$/);return!!e&&{event:e[1],sign:e[2],offset:e[3]}}var ye;!function(t){t.language="language",t.system="system",t.am_pm="12",t.twenty_four="24"}(ye||(ye={}));const we=t=>{if(t.time_format===ye.language||t.time_format===ye.system){const e=t.time_format===ye.language?t.language:void 0,i=(new Date).toLocaleString(e);return i.includes("AM")||i.includes("PM")}return t.time_format===ye.am_pm};function xe(t,e,i){return i===ye.am_pm||!i&&e.time_format===ye.am_pm?Tt(t,"h:mm A"):i===ye.twenty_four||!i&&e.time_format===ye.twenty_four?Tt(t,"shortTime"):(()=>{try{(new Date).toLocaleTimeString("i")}catch(t){return"RangeError"===t.name}return!1})()?t.toLocaleTimeString(e.language,{hour:"numeric",minute:"2-digit",hour12:we(e)}):we(e)?xe(t,e,ye.am_pm):xe(t,e,ye.twenty_four)}function $e(t){const e=new Date,i=(t||"").match(/^([0-9]{4})-([0-9]{2})-([0-9]{2})/);null!==i&&e.setFullYear(Number(i[1]),Number(i[2])-1,Number(i[3]));const s=(t||"").match(/([0-9]{2}):([0-9]{2})(:([0-9]{2}))?$/);return null!==s&&e.setHours(Number(s[1]),Number(s[2]),s.length>4?Number(s[4]):e.getSeconds()),e}var Se,Ce;!function(t){t.Sunrise="sunrise",t.Sunset="sunset"}(Se||(Se={})),function(t){t.WiserUpdated="wiser_updated"}(Ce||(Ce={}));let ke=class extends it{constructor(){super(...arguments),this.min=0,this.max=255,this.step=1,this.scaleFactor=1,this.unit="",this.optional=!1,this.disabled=!1,this._displayedValue=0}set value(t){t=isNaN(t)?this.min:this._roundedValue(t/this.scaleFactor),this._displayedValue=t}render(){return H`
      <div class="checkbox-container">
        <div class="checkbox">
          ${this.getCheckbox()}
        </div>
        <div class="slider">
          ${this.getSlider()}
        </div>
        <div class="value${this.disabled?" disabled":""}">
          ${this._displayedValue}${this.unit}
        </div>
      </div>
    `}getSlider(){return this.disabled?H`
        <ha-slider
          pin
          min=${this.min}
          max=${this.max}
          step=${this.step}
          value=${this._displayedValue}
          disabled
        ></ha-slider>
      `:H`
        <ha-slider
          pin
          min=${this.min}
          max=${this.max}
          step=${this.step}
          value=${this._displayedValue}
          @change=${this._updateValue}
        ></ha-slider>
      `}getCheckbox(){return this.optional?H`
      <ha-checkbox @change=${this.toggleChecked} ?checked=${!this.disabled}></ha-checkbox>
    `:H``}toggleChecked(t){const e=t.target.checked;this.disabled=!e;const i=this.disabled?null:this._scaledValue(this._displayedValue);Nt(this,"value-changed",{value:i})}_updateValue(t){let e=Number(t.target.value);this._displayedValue=e,e=this._scaledValue(this._displayedValue),Nt(this,"value-changed",{value:e})}_roundedValue(t){return t=Math.round(t/this.step)*this.step,(t=parseFloat(t.toPrecision(12)))>this.max?t=this.max:t<this.min&&(t=this.min),t}_scaledValue(t){return t=this._roundedValue(t),t*=this.scaleFactor,t=parseFloat(t.toFixed(2))}};ke.styles=d`
    ${Jt} :host {
      width: 100%;
    }
    ha-slider {
      width: 100%;
    }
  `,s([rt({type:Number})],ke.prototype,"min",void 0),s([rt({type:Number})],ke.prototype,"max",void 0),s([rt({type:Number})],ke.prototype,"step",void 0),s([rt({type:Number})],ke.prototype,"value",null),s([rt({type:Number})],ke.prototype,"scaleFactor",void 0),s([rt({type:String})],ke.prototype,"unit",void 0),s([rt({type:Boolean})],ke.prototype,"optional",void 0),s([rt({type:Boolean})],ke.prototype,"disabled",void 0),s([rt({type:Number})],ke.prototype,"_displayedValue",void 0),ke=s([ot("variable-slider")],ke);let Ee=class extends it{render(){return H`
            <div id="time-bar" class="time-wrapper">
                ${this.renderTimes()}
            </div>
        `}renderTimes(){const t=parseFloat(getComputedStyle(this).getPropertyValue("width"))||460,e=[1,2,3,4,6,8,12],i=we(ce(this.hass))?55:40;let s=Math.ceil(24/(t/i));for(;!e.includes(s);)s++;const o=[0,...Array.from(Array(24/s-1).keys()).map((t=>(t+1)*s)),24];return o.map((t=>{const e=0==t||24==t,i=e?s/48*100:s/24*100;return H`
            <div
                style="width: ${Math.floor(100*i)/100}%"
                class="${e?"":"time"}"
            >
                ${e?"":xe($e(fe(3600*t)),ce(this.hass))}
            </div>
            `}))}static get styles(){return d`
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
            transition: width 0.2s cubic-bezier(0.17, 0.67, 0.83, 0.67),
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

        `}};s([rt({attribute:!1})],Ee.prototype,"hass",void 0),Ee=s([ot("time-bar")],Ee);let Ae=class extends it{constructor(){super(),this.editMode=!1,this.schedule_type=Vt[0],this._activeSlot=-1,this._activeDay="",this._show_short_days=!1,this.activeMarker=0,this.isDragging=!1,this.currentTime=0,this.timer=0,this.timeout=0,this.zoomFactor=1,this.switchRef=new me,this.rangeMin=0,this.rangeMax=86400,this.stepSize=5,this.initialise()}async initialise(){return this.schedule&&(this.schedule_type=this.schedule.Type),!0}shouldUpdate(){return this.editMode||(this._activeSlot=-1,this._activeDay=""),!0}render(){var t;const e=parseFloat(getComputedStyle(this).getPropertyValue("width"));return this._show_short_days=e<500,this.hass&&this.config?H`
            <div class = "slots-wrapper">
                ${null===(t=this.schedule)||void 0===t?void 0:t.ScheduleData.map((t=>this.renderDay(t)))}
                <div class="wrapper" style="display:flex; height:28px;">
                    <div class="day  ${this._show_short_days?"short":""}">&nbsp;</div>
                        <time-bar style="width:100%"
                            .hass=${this.hass}
                            ></time-bar>
                    </div>
                </div>
            </div>
            ${this.editMode?this.renderAddDeleteButtons():null}
            ${this.renderSetPointControl()}
        `:H``}renderDay(t){return H`
            <div class="wrapper">
                ${this.computeDayLabel(t.day)}
                <div class="outer" id="${t.day}">
                    <div class="wrapper selectable">
                        ${t.slots.length>0?t.slots.map(((e,i)=>this.renderSlot(e,i,t))):this.renderEmptySlot({Time:"24:00",Setpoint:"0"},-1,t)}
                    </div>
                </div>
            </div>
        `}renderEmptySlot(t,e,i){const s="00:00",o=t.Time,n=le(i,e,this.schedule),r=parseFloat(getComputedStyle(this).getPropertyValue("width")),a=this.config.theme_colors?"rgba(var(--rgb-primary-color), 0.7)":"rgba("+ne(this,this.schedule_type,n)+")",l=(de(o)-de(s))/86400*100,d="Start - 00:00\nEnd - "+o+"\nSetting - "+this.computeSetpointLabel(n),c=l/100*r<35?"setpoint rotate":"setpoint";return H`
        <div
            class="slot previous"
            style="width:${Math.floor(100*l)/100}%; background:${a};"
            title='${d}'
            slot="${-1}"
            >
            <div class="slotoverlay previous">
                <span class="${c}">${this.computeSetpointLabel(le(i,-1,this.schedule))}</span>
            </div>
        </div>
    `}renderSlot(t,e,i){const s=t.Time,o=ae(i,e),n=t.Setpoint,r=(de(o)-de(s))/86400*100,a=this.config.theme_colors?"rgba(var(--rgb-primary-color), 0.7)":"rgba("+ne(this,this.schedule_type,n)+")",l=r/100*parseFloat(getComputedStyle(this).getPropertyValue("width"))<35?"setpoint rotate":"setpoint",d="Start - "+s+"\nEnd - "+o+"\nSetting - "+this.computeSetpointLabel(n);return H`
            ${0==e&&"00:00"!=s&&"0:00"!=s?this.renderEmptySlot(t,-1,i):""}
            <div
                id=${i.day+"|"+e}
                class="slot ${this.editMode?"selectable":null} ${this._activeSlot==e&&this._activeDay==i.day?"selected":null}"
                style="width:${Math.floor(100*r)/100}%; background:${a};"
                title='${d}'
                @click=${this._slotClick}
                slot="${e}"
                >

                <div class="slotoverlay ${this.editMode?"selectable":null}">
                    <span class="${l}">${this.computeSetpointLabel(n)}</span>
                </div>
                ${this._activeSlot==e&&this._activeDay==i.day?H`
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
                ${this._activeSlot==e&&this._activeDay==i.day?this.renderTooltip(e):""}
            </div>
        `}renderAddDeleteButtons(){const t=this._activeDay?this.schedule.ScheduleData.filter((t=>t.day==this._activeDay))[0].slots.length:0;return H`
                <div class="wrapper" style="white-space: normal;">
                    <div class="day  ${this._show_short_days?"short":""}">&nbsp;</div>
                    <mwc-button
                        id=${"add-before"}
                        @click=${this._addSlot}
                        ?disabled=${-1===this._activeSlot||t>=24}
                    >
                        <ha-icon icon="hass:plus-circle-outline" class="padded-right"></ha-icon>
                        ${"Add Before"}
                    </mwc-button>
                    <mwc-button
                        id=${"add-after"}
                        @click=${this._addSlot}
                        ?disabled=${-1===this._activeSlot||t>=24}
                    >
                        <ha-icon icon="hass:plus-circle-outline" class="padded-right"></ha-icon>
                        ${"Add After"}
                    </mwc-button>
                    <mwc-button
                        @click=${this._removeSlot}
                        ?disabled=${-1===this._activeSlot||t<=1}
                    >
                        <ha-icon icon="hass:minus-circle-outline" class="padded-right"></ha-icon>
                        ${this.hass.localize("ui.common.delete")}
                    </mwc-button>
                </div>
            `}renderSetPointControl(){if(this.editMode){const t=this._activeDay?this.schedule.ScheduleData.filter((t=>t.day==this._activeDay))[0].slots:{};return"Heating"==this.schedule_type?H`
                    <div class="wrapper" style="white-space: normal;">
                        <div class="day  ${this._show_short_days?"short":""}">&nbsp;</div>
                        <div class="section-header">Temperature</div>
                        <ha-icon-button class="set-off-button" .path=${"M3.28,2L2,3.27L4.77,6.04L5.64,7.39L4.22,9.6L5.95,10.5L7.23,8.5L10.73,12H4A2,2 0 0,0 2,14V22H4V20H18.73L20,21.27V22H22V20.73L22,20.72V20.72L3.28,2M7,17A1,1 0 0,1 6,18A1,1 0 0,1 5,17V15A1,1 0 0,1 6,14A1,1 0 0,1 7,15V17M11,17A1,1 0 0,1 10,18A1,1 0 0,1 9,17V15A1,1 0 0,1 10,14A1,1 0 0,1 11,15V17M15,17A1,1 0 0,1 14,18A1,1 0 0,1 13,17V15C13,14.79 13.08,14.61 13.18,14.45L15,16.27V17M16.25,9.5L17.67,7.3L16.25,5.1L18.25,2L20,2.89L18.56,5.1L20,7.3V7.31L18,10.4L16.25,9.5M22,14V18.18L19,15.18V15A1,1 0 0,0 18,14C17.95,14 17.9,14 17.85,14.03L15.82,12H20C21.11,12 22,12.9 22,14M11.64,7.3L10.22,5.1L12.22,2L13.95,2.89L12.53,5.1L13.95,7.3L13.94,7.31L12.84,9L11.44,7.62L11.64,7.3M7.5,3.69L6.1,2.28L6.22,2.09L7.95,3L7.5,3.69Z"} @click=${()=>this._updateSetPoint("-20")}> </ha-icon-button>
                        <variable-slider
                            min="5"
                            max="30"
                            step="0.5"
                            value=${-1!==this._activeSlot?parseFloat(t[this._activeSlot].Setpoint):0}
                            unit="°C"
                            .optional=${!1}
                            .disabled=${-1===this._activeSlot}
                            @value-changed=${t=>{this._updateSetPoint(Number(t.detail.value))}}
                        >
                        </variable-slider>
                    </div>
                `:"OnOff"==this.schedule_type?H`
                    <div class="wrapper" style="white-space: normal; height: 36px;">
                        <div class="day  ${this._show_short_days?"short":""}">&nbsp;</div>
                        <div class="section-header">State</div>
                        <mwc-button id="state-off"
                            class="state-button active"
                            .disabled=${-1==this._activeSlot||"Off"==t[this._activeSlot].Setpoint}
                            @click=${()=>this._updateSetPoint("Off")}
                            >
                            Off
                        </mwc-button>
                        <mwc-button id="state-on"
                            class="state-button active"
                            .disabled=${-1==this._activeSlot||"On"==t[this._activeSlot].Setpoint}
                            @click=${()=>this._updateSetPoint("On")}
                            >
                            On
                        </mwc-button>
                    </div>
                `:["Lighting","Shutters"].includes(this.schedule_type)?H`
                    <div class="wrapper" style="white-space: normal;">
                        <div class="day  ${this._show_short_days?"short":""}">&nbsp;</div>
                        <div class="section-header">Level</div>
                        <variable-slider
                            min="0"
                            max="100"
                            step="1"
                            value=${-1!==this._activeSlot?parseInt(t[this._activeSlot].Setpoint):0}
                            unit="%"
                            .optional=${!1}
                            .disabled=${-1===this._activeSlot}
                            @value-changed=${t=>{this._updateSetPoint(Number(t.detail.value))}}
                        >
                        </variable-slider>
                    </div>
                `:H``}return H``}renderTooltip(t){const e=this.schedule.ScheduleData.filter((t=>t.day==this._activeDay))[0].slots,i=be(e[t].Time);return H`
          <div class="tooltip-container center">
            <div
              class="tooltip ${this._activeSlot===t?"active":""}"
              @click=${this._selectMarker}
            >
              ${i?H`
                    <ha-icon
                      icon="hass:${"sunrise"==i.event?"weather-sunny":"weather-night"}"
                    ></ha-icon>
                    ${i.sign}
                    ${xe($e(i.offset),ce(this.hass),ye.twenty_four)}
                  `:e[t].Time}
            </div>
          </div>
        `}_slotClick(t){const e=t.target.parentElement.parentElement;if(e.id){const t=e.id.split("|")[0],i=e.id.split("|")[1];i!=this._activeSlot||t!=this._activeDay?(this._activeSlot=parseInt(i),this._activeDay=t):(this._activeSlot=-1,this._activeDay="");const s=new CustomEvent("slotClicked",{detail:{day:this._activeDay,slot:this._activeSlot}});this.dispatchEvent(s)}}_updateSetPoint(t){this.schedule.ScheduleData[jt.indexOf(this._activeDay)].slots=Object.assign(this.schedule.ScheduleData[jt.indexOf(this._activeDay)].slots,{[this._activeSlot]:Object.assign(Object.assign({},this.schedule.ScheduleData[jt.indexOf(this._activeDay)].slots[this._activeSlot]),{Setpoint:t})});const e=new CustomEvent("scheduleChanged",{detail:{schedule:this.schedule}});this.dispatchEvent(e),this.requestUpdate()}_addSlot(t){const e="add-before"===t.target.id;if(-1==this._activeSlot)return;const i=jt.indexOf(this._activeDay),s=ge(this.schedule.ScheduleData[i].slots[this._activeSlot].Time,this.hass);let o=ge(ae(this.schedule.ScheduleData[i],this._activeSlot),this.hass);o<s&&(o+=86400);const n=_e(s+(o-s)/2,this.stepSize);e?this.schedule.ScheduleData[i].slots=[...this.schedule.ScheduleData[i].slots.slice(0,this._activeSlot),{Time:xe($e(fe(s)),ce(this.hass)).padStart(5,"0"),Setpoint:It[this.schedule_type]},Object.assign(Object.assign({},this.schedule.ScheduleData[i].slots[this._activeSlot]),{Time:xe($e(fe(n)),ce(this.hass))}),...this.schedule.ScheduleData[i].slots.slice(this._activeSlot+1)]:(this.schedule.ScheduleData[i].slots=[...this.schedule.ScheduleData[i].slots.slice(0,this._activeSlot+1),{Time:xe($e(fe(n)),ce(this.hass)).padStart(5,"0"),Setpoint:It[this.schedule_type]},...this.schedule.ScheduleData[i].slots.slice(this._activeSlot+1)],this._activeSlot++);const r=new CustomEvent("scheduleChanged",{detail:{schedule:this.schedule}});this.dispatchEvent(r),this.requestUpdate()}_removeSlot(){if(-1==this._activeSlot)return;const t=jt.indexOf(this._activeDay),e=this._activeSlot;this.schedule.ScheduleData[t].slots=0==e?[...this.schedule.ScheduleData[t].slots.slice(e+1)]:[...this.schedule.ScheduleData[t].slots.slice(0,e),...this.schedule.ScheduleData[t].slots.slice(e+1)],this._activeSlot==this.schedule.ScheduleData[t].slots.length&&this._activeSlot--;const i=new CustomEvent("scheduleChanged",{detail:{schedule:this.schedule}});this.dispatchEvent(i),this.requestUpdate()}_handleTouchStart(t){const e=jt.indexOf(this._activeDay);let i=this.schedule.ScheduleData.filter((t=>t.day==this._activeDay))[0].slots;const s=t.target;let o=s;for(;!o.classList.contains("outer");)o=o.parentElement;const n=parseFloat(getComputedStyle(o).getPropertyValue("width")),r=86400/(this.rangeMax-this.rangeMin)*n,a=-(-this.rangeMin/(this.rangeMax-this.rangeMin)*n)/r*86400;let l=s;for(;!l.classList.contains("slot");)l=l.parentElement;const d=l,c=Number(d.getAttribute("slot")),h=c>0?ge(i[c-1].Time,this.hass)+60*this.stepSize:0,u=c<i.length-1?(ge(ae(this.schedule.ScheduleData[e],c),this.hass)||86400)-60*this.stepSize:86400;this.isDragging=!0;const p=d.parentElement.parentElement.getBoundingClientRect();let v=t=>{let s;s="undefined"!=typeof TouchEvent&&t instanceof TouchEvent?t.changedTouches[0].pageX:t.pageX;let o=s-p.left;o>n-10&&(o=n-10),o<-18&&(o=-18);let l=Math.round(o/r*86400+a);l<h&&(l=h),l>u&&(l=u),this.currentTime=l;const d=be(ae(this.schedule.ScheduleData[e],c));let v;d?v=((t,e,i,s={})=>{if(be(t))return t;const o=ge(t,i),n=i.states["sun.sun"],r=ge(n.attributes.next_rising,i),a=ge(n.attributes.next_setting,i);e||(e=Math.abs(o-r)<Math.abs(o-a)?Se.Sunrise:Se.Sunset);let l=o-(e==Se.Sunrise?ge(n.attributes.next_rising,i):ge(n.attributes.next_setting,i));return s.stepSize&&(l=_e(l,s.stepSize,{maxHours:2})),`${e}${l>0?"+":"-"}${fe(Math.abs(l))}`})(fe(l),d.event,this.hass,{stepSize:this.stepSize}):(l=Math.round(l)>=86400?86400:_e(l,this.stepSize),v=xe($e(fe(l)),ce(this.hass)).padStart(5,"0")),v!=ae(this.schedule.ScheduleData[e],c)&&(i=Object.assign(i,{[c]:Object.assign(Object.assign({},i[c]),{Time:v})}),this.requestUpdate())};const m=()=>{window.removeEventListener("mousemove",v),window.removeEventListener("touchmove",v),window.removeEventListener("mouseup",m),window.removeEventListener("touchend",m),window.removeEventListener("blur",m),v=()=>{},setTimeout((()=>{this.isDragging=!1}),100),s.blur();const t=new CustomEvent("scheduleChanged",{detail:{schedule:this.schedule}});this.dispatchEvent(t)};window.addEventListener("mouseup",m),window.addEventListener("touchend",m),window.addEventListener("blur",m),window.addEventListener("mousemove",v),window.addEventListener("touchmove",v)}_selectMarker(t,e=!0){t.stopImmediatePropagation();let i=t.target;for(;!i.classList.contains("slot");)i=i.parentElement;const s=Number(i.getAttribute("slot"));e&&this.activeMarker===s?this.activeMarker=null:this.activeMarker=e?s:null;const o=new CustomEvent("update",{detail:{entry:this._activeSlot,marker:this.activeMarker}});this.dispatchEvent(o),this._updateTooltips()}_updateTooltips(){var t;const e=parseFloat(getComputedStyle(this).getPropertyValue("width")),i=null===(t=this.shadowRoot)||void 0===t?void 0:t.querySelectorAll(".tooltip"),s=t=>{const e=t.offsetWidth,i=t.parentElement.offsetLeft+t.offsetLeft-15;return t.parentElement.classList.contains("left")?[i+e/2,i+3*e/2]:t.parentElement.classList.contains("right")?[i-e/2,i+e/2]:[i,i+e]};null==i||i.forEach(((t,o)=>{const n=t.parentElement,r=n.classList.contains("visible"),a=Number(n.parentElement.getAttribute("slot"));if(a!=this._activeSlot&&a-1!=this._activeSlot)r&&n.classList.remove("visible");else{const l=t.parentElement.offsetLeft;if(l<0||l>e+15)r&&n.classList.remove("visible");else{r||n.classList.add("visible");const l=n.offsetWidth,d=n.classList.contains("center");let c=s(t)[0],h=e-s(t)[1];if(o>0&&a-1==this._activeSlot)c-=s(i[o-1])[1];else if(o+1<i.length&&a==this._activeSlot){const t=s(i[o+1])[0];h-=t<0?0:e-t}c<h?c<0?d&&h>l/2&&(n.classList.add("right"),n.classList.remove("center"),n.classList.remove("left")):(n.classList.add("center"),n.classList.remove("right"),n.classList.remove("left")):h<0?d&&c>l/2&&(n.classList.add("left"),n.classList.remove("center"),n.classList.remove("right")):(n.classList.add("center"),n.classList.remove("left"),n.classList.remove("right"))}}}))}computeDayLabel(t){return H`
            <div class="day  ${this._show_short_days?"short":""}">
                ${this._show_short_days?Bt[jt.indexOf(t)]:t}
            </div>
        `}computeSetpointLabel(t){var e;return"heating"==(null===(e=this.schedule_type)||void 0===e?void 0:e.toLowerCase())?-20==t?"Off":t+"°C":["lighting","shutters","level"].includes(this.schedule_type.toLowerCase())?t+"%":t}static get styles(){return d`
            :host {
            display: block;
            max-width: 100%;
            }
            div.outer {
            width: 100%;
            }
            div.wrapper,
            div.time-wrapper {
            white-space: nowrap;
            transition: width 0.2s cubic-bezier(0.17, 0.67, 0.83, 0.67),
                margin 0.2s cubic-bezier(0.17, 0.67, 0.83, 0.67);
            /* overflow: auto;*/
            display: flex;
            }
            div.assignment-wrapper {
            border-top: 1px solid var(--divider-color, #e8e8e8);
            padding: 5px 0px;
            min-height: 40px;
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
            background: rgba(52,143,255,1)
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
            div.slot.selected {
            border: 3px solid rgba(var(--rgb-primary-color), 0.7);
            box-sizing: border-box;
            -moz-box-sizing: border-box;
            -webkit-box-sizing: border-box;
            }
            .previous {
            display: block;
            background: repeating-linear-gradient(135deg, rgba(0,0,0,0), rgba(0,0,0,0) 5px, rgba(255,255,255,0.2) 5px, rgba(255,255,255,0.2) 10px);
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
            --mdc-icon-size: 20px;
        }

        mwc-button.state-button {
            width: 20%;
			padding: 0px 18px;
			margin: 0 2px;
			max-width: 100px;
        }
        mwc-button#state-on {
            background-color: var(--state-on-color);
        }
        mwc-button#state-off {
            background-color: var(--state-off-color);
        }

          mwc-button.warning
          {
            --mdc-theme-primary: var(--error-color);
          }
          mwc-button.warning .mdc-button .mdc-button__label {
            color: var(--primary-text-color)
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
            margin-right: 11px;
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
            padding-bottom: 10px;
            font-weight: 500;
          }
        `}};s([rt({attribute:!1})],Ae.prototype,"hass",void 0),s([rt()],Ae.prototype,"config",void 0),s([rt()],Ae.prototype,"schedule",void 0),s([rt()],Ae.prototype,"editMode",void 0),s([at()],Ae.prototype,"_activeSlot",void 0),s([at()],Ae.prototype,"_activeDay",void 0),s([at()],Ae.prototype,"_show_short_days",void 0),s([at()],Ae.prototype,"rangeMin",void 0),s([at()],Ae.prototype,"rangeMax",void 0),s([at()],Ae.prototype,"stepSize",void 0),s([dt({passive:!0})],Ae.prototype,"_handleTouchStart",null),Ae=s([ot("schedule-slot-editor")],Ae);let Me=class extends(pe(it)){constructor(){var t;super(),this.schedule_id=0,this.use_heat_colors=!0,this.rooms=[],this.entities=[],this._activeSlot=null,this._activeDay=null,this.editMode=!1,this._current_user=null===(t=this.hass)||void 0===t?void 0:t.user,this.stepSize=5,this._assigning_in_progress=0,this._save_in_progress=!1}async initialise(){return await this._isComponentLoaded()&&(this.component_loaded=!0),!0}hassSubscribe(){return this.initialise(),[this.hass.connection.subscribeMessage((t=>this.handleUpdate(t)),{type:"wiser_updated"})]}async handleUpdate(t){"wiser_updated"==t.event&&await this.loadData()}async _isComponentLoaded(){for(;!this.hass&&!this.config&&!this.hass.config.components.includes("wiser");)await new Promise((t=>setTimeout(t,100)));return await this.loadData(),!0}async loadData(){this.schedule_type&&this.schedule_id&&(this.schedule=await Qt(this.hass,this.config.hub,this.schedule_type,this.schedule_id),this.entities=await this.get_entity_list(this.hass,this.config.hub))}async get_entity_list(t,e){return"heating"==this.schedule.Type.toLowerCase()?await((t,e)=>t.callWS({type:"wiser/rooms",hub:e}))(t,e):await((t,e,i)=>t.callWS({type:"wiser/devices",device_type:i,hub:e}))(t,e,this.schedule.SubType)}shouldUpdate(t){return t.has("schedule_id")||t.has("editMode")?(this.loadData(),!0):!!t.has("force")||!!(t.has("schedule")||t.has("entities")||t.has("editMode")||t.has("_assigning_in_progress")||t.has("_save_in_progress"))}render(){return this.hass&&this.config&&this.component_loaded?this.schedule&&this.entities?H`
            <ha-card>
            <div class="card-header">
                <div class="name">
                ${this.config.name}
                </div>
            </div>
            <div class="card-content">
                <div class="schedule-info">
                    <span class="sub-heading">Schedule Type:</span> ${this.schedule.Type}
                </div>
                <div class="schedule-info">
                    <span class="sub-heading">Schedule Id:</span> ${this.schedule.Id}
                </div>
                <div class="schedule-info">
                    <span class="sub-heading">Schedule Name:</span> ${this.schedule.Name}
                </div>
				<div class=${this.editMode?"mode":""}>
					${this.editMode?"Edit Mode":null}
				</div>
                <div class="wrapper">
                    <div class="schedules">
                        <div class = "slots-wrapper">
                            <schedule-slot-editor
                                .hass=${this.hass}
                                .config=${this.config}
                                .schedule=${this.editMode?this._tempSchedule:this.schedule}
								.schedule_type=${this.schedule_type}
                                .editMode=${this.editMode}
								@scheduleChanged=${this.scheduleChanged}
                            ></schedule-slot-editor>
                        </div>
                    </div>
                </div>
				${this.entities.length?this.renderScheduleAssignment(this.entities,this.schedule.Assignments):"(No available devices)"}
				${this.renderScheduleActionButtonSection()}
            </div>
            ${this.renderCardActions()}
            </ha-card>
        `:H`
        <ha-card>
            <div class="card-header">
                <div class="name">
                ${this.config.name}
                </div>
            </div>
            <div class="card-content">
            </div>
        </ha-card>`:H``}renderScheduleAssignment(t,e){if(this.schedule&&!this.editMode)return re(this.hass,this.config)?H`
					<div class="assignment-wrapper">
						<div class="sub-heading">Schedule Assignment</div>
						${t.map((t=>this.renderEntityButton(t,e.map((function(t){return t.name})).includes(t.Name))))}
					</div>
				`:H`
					<div class="assignment-wrapper">
						<div class="sub-heading">Schedule Assignment</div>
						${e.length>0?t.filter((t=>e.map((function(t){return t.name})).includes(t.Name))).map((t=>this.renderEntityLabel(t))):H`<span class="assignment-label">(Not Assigned)</span>`}
					</div>
				`}renderEntityButton(t,e){return H`
			<mwc-button id=${t.Id}
			class=${e?"active":""}
			@click=${this.entityAssignmentClick}
			>
			${this._assigning_in_progress==t.Id?H`<span class="waiting"><ha-circular-progress active size="small"></ha-circular-progress></span>`:null}
            ${t.Name}
			</mwc-button>
		`}renderScheduleActionButtonSection(){if(this.schedule&&!this.editMode&&re(this.hass,this.config))return H`
					<div class="actions-wrapper">
						<div class="sub-heading">Schedule Actions</div>
						<div class="wrapper schedule-action-wrapper">
							${this.renderEditScheduleButton()}
							${this.renderCopyScheduleButton()}
							${this.renderDeleteScheduleButton()}
						</div>
					</div>
				`}renderEntityLabel(t){return H`
        <span class="assignment-label">
            ${t.Name}
        </span>
        `}renderCardActions(){if(!this.config.selected_schedule)return H`
                <div class="card-actions">
					<div class="action-buttons">
						${this.editMode?null:this.renderBackButton()}
						${this.editMode?this.renderCancelButton():null}
						${this.editMode?this.renderSaveScheduleButton():null}
					</div>
                </div>
            `}renderBackButton(){return H`
			<mwc-button @click=${this.backClick}
			>Back
			</mwc-button>
		`}renderCancelButton(){return H`
			<mwc-button @click=${this.cancelClick}
			>Cancel
			</mwc-button>
		`}renderDeleteScheduleButton(){return H`
        <mwc-button
            class="large warning"
            label=${this.hass.localize("ui.common.delete")}
            .disabled=${1e3==this.schedule_id}
            @click=${this.deleteClick}
        >
        </mwc-button>
        `}renderCopyScheduleButton(){return H`
        <mwc-button
            class="large active"
            label=${"Copy"}
            .disabled=${1e3==this.schedule_id}
            @click=${this.copyClick}
        >
        </mwc-button>
        `}renderEditScheduleButton(){return H`
		<mwc-button
			class="large active"
			label=${"Edit"}
			@click=${this.editClick}
		>
		</mwc-button>
		`}renderSaveScheduleButton(){if(re(this.hass,this.config))return H`
                <mwc-button class="right"
					@click=${this.saveClick}
                >
                ${this._save_in_progress?H`<ha-circular-progress active size="small"></ha-circular-progress>`:"Save"}
            </mwc-button>
            `}async entityAssignmentClick(t){const e=t.target;this._assigning_in_progress=parseInt(e.id),re(this.hass,this.config)&&await((t,e,i,s,o,n=!1)=>t.callWS({type:"wiser/schedule/assign",hub:e,schedule_type:i,schedule_id:s,entity_id:o,remove:n}))(this.hass,this.config.hub,this.schedule_type,this.schedule_id,e.id,e.classList.contains("active")),this._assigning_in_progress=0}backClick(){const t=new CustomEvent("backClick");this.dispatchEvent(t)}editClick(){this._tempSchedule=this.schedule,this.editMode=!this.editMode}copyClick(){const t=new CustomEvent("copyClick");this.dispatchEvent(t)}async deleteClick(t){const e=t.target;if(await new Promise((t=>{Nt(e,"show-dialog",{dialogTag:"dialog-delete-confirm",dialogImport:()=>Promise.resolve().then((function(){return ue})),dialogParams:{cancel:()=>{t(!1)},confirm:()=>{t(!0)},name:this.schedule.Name}})}))){this.schedule_id=0,await(i=this.hass,s=this.config.hub,o=this.schedule.Type,n=this.schedule.Id,i.callWS({type:"wiser/schedule/delete",hub:s,schedule_type:o,schedule_id:n}));const t=new CustomEvent("scheduleDeleted");this.dispatchEvent(t)}var i,s,o,n}async cancelClick(){this.editMode=!1}async saveClick(){var t,e,i,s,o;this._save_in_progress=!0,await(t=this.hass,e=this.config.hub,i=this.schedule_type,s=this.schedule_id,o=this._tempSchedule,t.callWS({type:"wiser/schedule/save",hub:e,schedule_type:i,schedule_id:s,schedule:o})),this._save_in_progress=!1,this.editMode=!1}async scheduleChanged(t){this._tempSchedule=t.detail.schedule}static get styles(){return d`
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
          transition: width 0.2s cubic-bezier(0.17, 0.67, 0.83, 0.67),
            margin 0.2s cubic-bezier(0.17, 0.67, 0.83, 0.67);
          overflow: hidden;
        }
        div.assignment-wrapper, div.actions-wrapper {
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
          background: rgba(52,143,255,1)
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
          background: repeating-linear-gradient(135deg, rgba(0,0,0,0), rgba(0,0,0,0) 5px, rgba(255,255,255,0.2) 5px, rgba(255,255,255,0.2) 10px);
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
        .slots-wrapper {
              padding-bottom: 20px;
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
        mwc-button.warning
        {
          --mdc-theme-primary: #fff;
		  background-color: var(--error-color);
		  border-radius: var(--mdc-shape-small, 4px)
        }
		mwc-button.large {
			width: 20%;
			padding: 0px 18px;
			margin: 0 2px;
			max-width: 200px;
		}
		mwc-button.right {
            float: right;
          }
        mwc-button.warning .mdc-button .mdc-button__label {
          color: var(--primary-text-color)
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
          margin-right: 11px;
        }
        mwc-button.active {
          background: var(--primary-color);
          --mdc-theme-primary: var(--text-primary-color);
          border-radius: 4px;
        }
        mwc-button {
            margin: 2px 0;
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
      `}};s([rt()],Me.prototype,"config",void 0),s([rt()],Me.prototype,"schedule_id",void 0),s([rt()],Me.prototype,"schedule_type",void 0),s([rt()],Me.prototype,"use_heat_colors",void 0),s([rt({reflect:!0,type:Object})],Me.prototype,"schedule",void 0),s([rt()],Me.prototype,"rooms",void 0),s([rt()],Me.prototype,"entities",void 0),s([rt()],Me.prototype,"component_loaded",void 0),s([at()],Me.prototype,"_activeSlot",void 0),s([at()],Me.prototype,"_activeDay",void 0),s([at()],Me.prototype,"editMode",void 0),s([at()],Me.prototype,"_current_user",void 0),s([at()],Me.prototype,"_assigning_in_progress",void 0),s([at()],Me.prototype,"_save_in_progress",void 0),Me=s([ot("schedule-edit-card")],Me);let Le=class extends it{constructor(){super(),this.component_loaded=!1,this.connectionError=!1,this._schedule_types=[],this._schedule_info={Name:"",Type:"Heating"},this.initialise()}async initialise(){return await this.isComponentLoaded()&&(this.component_loaded=!0,await this.loadData()),!0}async isComponentLoaded(){for(;!this.hass||!this.hass.config.components.includes("wiser");)await new Promise((t=>setTimeout(t,100)));return!0}async loadData(){this._schedule_types=await Xt(this.hass,this.config.hub)}render(){return this.hass&&this.config?H`
            <ha-card>
                <div class="card-header">
                    <div class="name">
                        ${this.config.name}
                    </div>
                </div>
                <div class="card-content">
                    <div>
                        Add Schedule
                    </div>
                    <div class="wrapper">
                    ${"Select the schedule type and enter a name for the schedule to create"}
                    </div>
                    <div class="wrapper">
                      ${this._schedule_types.map(((t,e)=>this.renderScheduleTypeButtons(t,e)))}
                    </div>
                    <ha-textfield class="schedule-name"
                      auto-validate
                      required
                      label="Schedule Name"
                      error-message="Name is required"
                      .configValue=${"Name"}
                      @input=${this._valueChanged}
                    >
                    </ha-textfield>
                </div>
                <div class="card-actions">
                    <mwc-button
                        style="float: right"
                        .disabled=${!this._schedule_info||!this._schedule_info.Name}
                        @click=${this.confirmClick}
                        dialogAction="close"
                    >
                        ${"Ok"}
                    </mwc-button>
                    <mwc-button
                        @click=${this.cancelClick}
                    >
                        ${"Cancel"}
                    </mwc-button>
                </div>
            </ha-card>
        `:H``}renderScheduleTypeButtons(t,e){return H`
            <mwc-button
                id=${e}
                class=${this._schedule_info&&this._schedule_info.Type==t?"active":"inactive"}
                @click=${this._valueChanged}
                .configValue=${"Type"}
                .value=${t}
            >
                ${t}
            </mwc-button>
        `}async confirmClick(){await this.createSchedule()}async createSchedule(){var t,e,i,s;await(t=this.hass,e=this.config.hub,i=this._schedule_info.Type,s=this._schedule_info.Name,t.callWS({type:"wiser/schedule/create",hub:e,schedule_type:i,name:s}));const o=new CustomEvent("scheduleAdded");this.dispatchEvent(o)}cancelClick(){const t=new CustomEvent("backClick");this.dispatchEvent(t)}_valueChanged(t){const e=t.target;e.configValue&&(this._schedule_info=Object.assign(Object.assign({},this._schedule_info),{[e.configValue]:void 0!==e.checked?e.checked:e.value}))}static get styles(){return d`
            div.wrapper {
                white-space: nowrap;
                transition: width 0.2s cubic-bezier(0.17, 0.67, 0.83, 0.67),
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
        `}};s([rt({attribute:!1})],Le.prototype,"hass",void 0),s([rt()],Le.prototype,"config",void 0),s([rt()],Le.prototype,"component_loaded",void 0),s([at()],Le.prototype,"_schedule_types",void 0),s([at()],Le.prototype,"_schedule_info",void 0),Le=s([ot("schedule-add-card")],Le);let De=class extends it{constructor(){super(),this.schedule_id=0,this.component_loaded=!1,this._copy_in_progress=0,this.connectionError=!1,this._schedule_list=[],this.initialise()}async initialise(){return await this.isComponentLoaded()&&(this.component_loaded=!0,await this.loadData()),!0}async isComponentLoaded(){for(;!this.hass||!this.hass.config.components.includes("wiser");)await new Promise((t=>setTimeout(t,100)));return!0}async loadData(){this.schedule=await Qt(this.hass,this.config.hub,this.schedule_type,this.schedule_id),this._schedule_list=await Gt(this.hass,this.config.hub,this.schedule_type)}render(){return this.hass&&this.config&&this.schedule?H`
            <ha-card>
                <div class="card-header">
                    <div class="name">
                        ${this.config.name}
                    </div>
                </div>
                <div class="card-content">
                    <div>
                        Copy Schedule
                    </div>
                    <div class="schedule-info">
                        <span class="sub-heading">Schedule Type:</span> ${this.schedule.Type}
                    </div>
                    <div class="schedule-info">
                        <span class="sub-heading">Schedule Id:</span> ${this.schedule.Id}
                    </div>
                    <div class="schedule-info">
                        <span class="sub-heading">Schedule Name:</span> ${this.schedule.Name}
                    </div>
                    <div class="wrapper" style="margin: 20px 0 0 0;">
                    ${"Select the schedule below to copy to"}
                    </div>
                    <div class="assignment-wrapper">
                      ${this._schedule_list.filter((t=>{var e;return t.Id!=(null===(e=this.schedule)||void 0===e?void 0:e.Id)})).map((t=>this.renderScheduleButtons(t)))}
                    </div>
                </div>
                <div class="card-actions">
                    <mwc-button
                        @click=${this.cancelClick}
                    >
                        ${"Cancel"}
                    </mwc-button>
                </div>
            </ha-card>
        `:H``}renderScheduleButtons(t){return H`
            <mwc-button
                id=${t.Id}
                @click=${this._copySchedule}
                .value=${t.Name}
            >
                ${this._copy_in_progress==t.Id?H`<span class="waiting"><ha-circular-progress active size="small"></ha-circular-progress></span>`:null}
                ${t.Name}
            </mwc-button>
        `}cancelClick(){const t=new CustomEvent("backClick",{detail:Ut.ScheduleEdit});this.dispatchEvent(t)}async _copySchedule(t){const e=t.target;if(e.id){this._copy_in_progress=parseInt(e.id),await(i=this.hass,s=this.config.hub,o=this.schedule_type,n=this.schedule_id,r=parseInt(e.id),i.callWS({type:"wiser/schedule/copy",hub:s,schedule_type:o,schedule_id:n,to_schedule_id:r})),this._copy_in_progress=0;const t=new CustomEvent("scheduleCopied");this.dispatchEvent(t)}var i,s,o,n,r}static get styles(){return d`
            div.wrapper {
                white-space: nowrap;
                transition: width 0.2s cubic-bezier(0.17, 0.67, 0.83, 0.67),
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
        `}};s([rt({attribute:!1})],De.prototype,"hass",void 0),s([rt()],De.prototype,"config",void 0),s([rt()],De.prototype,"schedule_id",void 0),s([rt()],De.prototype,"schedule_type",void 0),s([rt({reflect:!0,type:Object})],De.prototype,"schedule",void 0),s([at()],De.prototype,"component_loaded",void 0),s([at()],De.prototype,"_copy_in_progress",void 0),s([at()],De.prototype,"_schedule_list",void 0),De=s([ot("schedule-copy-card")],De),console.info(`%c  WISER-SCHEDULE-CARD \n%c  ${Zt("common.version")} 1.0.0    `,"color: orange; font-weight: bold; background: black","color: white; font-weight: bold; background: dimgray"),window.customCards=window.customCards||[],window.customCards.push({type:"wiser-schedule-card",name:"Wiser Schedule Card",description:"A card to manage Wiser schedules"});let Te=class extends it{constructor(){super(),this._view=Ut.Overview,this.translationsLoaded=!0,this.component_loaded=!1,this._schedule_id=0,this._schedule_type="heating",this.initialise()}static async getConfigElement(){return await import("./editor-18c7bf67.js"),document.createElement("wiser-schedule-card-editor")}static getStubConfig(){return{}}setConfig(t){if(!t)throw new Error(Zt("common.invalid_configuration"));t.test_gui&&function(){var t=document.querySelector("home-assistant");if(t=(t=(t=(t=(t=(t=(t=(t=t&&t.shadowRoot)&&t.querySelector("home-assistant-main"))&&t.shadowRoot)&&t.querySelector("app-drawer-layout partial-panel-resolver"))&&t.shadowRoot||t)&&t.querySelector("ha-panel-lovelace"))&&t.shadowRoot)&&t.querySelector("hui-root")){var e=t.lovelace;return e.current_view=t.___curView,e}return null}().setEditMode(!0),this.config=Object.assign({name:"Wiser Schedule"},t)}set hass(t){this._hass=t}async initialise(){return await this.isComponentLoaded()&&(this.component_loaded=!0),this.processConfigSchedule(),!0}async isComponentLoaded(){for(;!this._hass||!this._hass.config.components.includes("wiser");)await new Promise((t=>setTimeout(t,100)));return!0}processConfigSchedule(){this.config.selected_schedule?(this._schedule_type=this.config.selected_schedule.split("|")[0],this._schedule_id=parseInt(this.config.selected_schedule.split("|")[1]),this._view=Ut.ScheduleEdit):(this._schedule_type="",this._schedule_id=0,this._view=Ut.Overview)}getCardSize(){return 9}shouldUpdate(t){return!(!this.config||!this.component_loaded)&&(t.has("config")&&this.processConfigSchedule(),!!t.has("component_loaded")||(!!t.has("_view")||(!!t.has("_schedule_list")||Pt(this,t,!1))))}async _handleEvent(t){if("wiser_update_received"===t.event_type){const t=new CustomEvent("wiser-update",{});this.dispatchEvent(t)}}render(){return this._hass&&this.config&&this.translationsLoaded?this._view==Ut.Overview?H`
        <schedule-list-card id="schedule_list"
          .hass=${this._hass}
          .config=${this.config}
          @scheduleClick=${this._scheduleClick}
          @addScheduleClick=${this._addScheduleClick}
        >
        </schedule-list-card>
      `:this._view==Ut.ScheduleEdit&&this._schedule_id?H`
        <schedule-edit-card
          .hass=${this._hass}
          .config=${this.config}
          .schedule_id=${this._schedule_id}
          .schedule_type=${this._schedule_type}
          @backClick=${this._backClick}
          @editClick=${this._editClick}
          @copyClick=${this._copyClick}
          @scheduleDeleted=${this._scheduleDeleted}
        >
        </schedule-display-card>
      `:this._view==Ut.ScheduleAdd?H`
        <schedule-add-card
          .hass=${this._hass}
          .config=${this.config}
          @backClick=${this._backClick}
          @scheduleAdded=${this._scheduleAdded}
        ></schedule-add-card>
      `:this._view==Ut.ScheduleCopy?H`
        <schedule-copy-card
          .hass=${this._hass}
          .config=${this.config}
          .schedule_id=${this._schedule_id}
          .schedule_type=${this._schedule_type}
          @backClick=${this._backClick}
          @scheduleCopied=${this._scheduleCopied}
        ></schedule-add-card>
      `:H``:H``}_scheduleClick(t){this._schedule_type=t.detail.schedule_type,this._schedule_id=t.detail.schedule_id,this._view=Ut.ScheduleEdit}async _addScheduleClick(){this._view=Ut.ScheduleAdd}async _scheduleDeleted(){this._view=Ut.Overview}async _scheduleAdded(){this._view=Ut.Overview}async _scheduleSaved(){this._view=Ut.Overview}async _scheduleCopied(){this._view=Ut.ScheduleEdit}_backClick(t){console.log(t.detail),t.detail?this._view=t.detail:this._view=Ut.Overview}_editClick(){this._view=Ut.ScheduleEdit}_copyClick(){this._view=Ut.ScheduleCopy}static get styles(){return d`
      ${Jt}
      mwc-button ha-icon {
        margin-right: 11px;
      }
      mwc-button.active {
      background: var(--primary-color);
      --mdc-theme-primary: var(--text-primary-color);
      border-radius: 4px;
      }
    `}};s([rt()],Te.prototype,"_hass",void 0),s([rt()],Te.prototype,"_view",void 0),s([at()],Te.prototype,"config",void 0),s([rt()],Te.prototype,"translationsLoaded",void 0),s([rt()],Te.prototype,"component_loaded",void 0),s([rt()],Te.prototype,"_schedule_id",void 0),s([rt()],Te.prototype,"_schedule_type",void 0),Te=s([ot("wiser-schedule-card")],Te);export{H as $,Nt as A,Te as W,e as _,i as a,s as b,U as c,dt as d,rt as e,o as f,Kt as g,Gt as h,c as i,ut as l,ot as n,lt as o,d as r,it as s,at as t,I as w};
