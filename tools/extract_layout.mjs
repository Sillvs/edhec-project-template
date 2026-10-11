#!/usr/bin/env node
// Read the rendered geometry of every slide out of Chrome and write it to JSON.
//
//   node extract_layout.mjs praesentation.html layout.json
//
// The deck is a fixed 1280x720 canvas, so the browser's own layout engine gives
// us exact coordinates for every box, every text block and every icon. That is
// what makes a native (editable) PowerPoint possible: we rebuild those boxes as
// real shapes instead of flattening the slide to a picture.
//
// Uses the DevTools protocol over Node 22's built-in WebSocket, no packages.

import { execFileSync, spawn } from "node:child_process";
import { writeFileSync, mkdirSync } from "node:fs";
import { resolve } from "node:path";

// Resolved at run time, never hardcoded: a Playwright upgrade renames the
// directory and a pinned path fails with a bare "No such file or directory".
const CHROME = process.env.CHROME || execFileSync(
  new URL("find-chrome.sh", import.meta.url).pathname, { encoding: "utf8" }).trim();

const [, , htmlArg, outArg] = process.argv;
if (!htmlArg || !outArg) {
  console.error("usage: node extract_layout.mjs <deck.html> <out.json>");
  process.exit(1);
}
const url = "file://" + resolve(htmlArg);

// ---------------------------------------------------------------- page script
// Runs inside the page. Returns a JSON string describing every slide.
const EXTRACTOR = `(() => {
  const r2 = v => Math.round(v * 100) / 100;

  const colour = c => {
    const m = String(c).match(/rgba?\\(([\\d.]+),\\s*([\\d.]+),\\s*([\\d.]+)(?:,\\s*([\\d.]+))?\\)/);
    if (!m) return null;
    const a = m[4] === undefined ? 1 : parseFloat(m[4]);
    if (a === 0) return null;
    const hx = n => Math.round(+n).toString(16).padStart(2, "0");
    return { c: (hx(m[1]) + hx(m[2]) + hx(m[3])).toUpperCase(), a };
  };

  const gradient = bg => {
    if (!bg || bg.indexOf("gradient") < 0) return null;
    const radial = bg.indexOf("radial-gradient") >= 0;
    const stops = bg.match(/rgba?\\([^)]*\\)/g);
    const ang = bg.match(/linear-gradient\\(\\s*([\\d.]+)deg/);
    if (!stops || stops.length < 2) return null;
    return {
      angle: ang ? parseFloat(ang[1]) : (radial ? 135 : 90),
      radial,
      from: colour(stops[0]),
      to: colour(stops[stops.length - 1]),
    };
  };

  // Text transparency plus letter spacing makes renderers drop trailing
  // characters, so the alpha is blended into a flat colour here and the
  // PowerPoint file never carries a translucent run.
  const opaqueBg = el => {
    let n = el && el.nodeType === 1 ? el : null;
    while (n) {
      const c = colour(getComputedStyle(n).backgroundColor);
      if (c && c.a >= 0.99) return c;
      n = n.parentElement;
    }
    return { c: "FFFFFF", a: 1 };
  };
  const flatten = (fg, el, extraAlpha) => {
    const a = (fg ? fg.a : 1) * (extraAlpha === undefined ? 1 : extraAlpha);
    if (!fg || a >= 0.99) return fg;
    const bg = opaqueBg(el);
    const hx = (v, i) => parseInt(v.slice(i, i + 2), 16);
    const out = [0, 2, 4].map(i =>
      Math.round(hx(fg.c, i) * a + hx(bg.c, i) * (1 - a))
        .toString(16).padStart(2, "0")).join("").toUpperCase();
    return { c: out, a: 1 };
  };

  const fontOf = (cs, el) => ({
    size: parseFloat(cs.fontSize),
    weight: parseInt(cs.fontWeight, 10) || 400,
    italic: cs.fontStyle === "italic",
    colour: flatten(colour(cs.color), el, parseFloat(cs.opacity)),
    upper: cs.textTransform === "uppercase",
    spacing: cs.letterSpacing === "normal" ? 0 : parseFloat(cs.letterSpacing),
    lh: cs.lineHeight === "normal" ? 0 : parseFloat(cs.lineHeight),
    align: cs.textAlign,
  });

  // runs inside one text block: direct text nodes plus inline descendants
  const runsOf = el => {
    const out = [];
    for (const n of el.childNodes) {
      if (n.nodeType === 3) {
        const t = n.textContent.replace(/\\s+/g, " ");
        if (t.trim()) out.push({ s: t, f: fontOf(getComputedStyle(el), el) });
      } else if (n.nodeType === 1) {
        const tag = n.tagName.toLowerCase();
        if (tag === "br") { out.push({ br: true }); continue; }
        if (tag === "svg") continue;
        const cs = getComputedStyle(n);
        if (cs.display !== "inline") continue;   // inline-block is its own box
        out.push(...runsOf(n));
      }
    }
    return out;
  };

  // the ink box of the text itself, which already accounts for padding, flex
  // centring and any inline swatch sitting in front of the first word
  const textBox = (el, base) => {
    // union over the direct text nodes and pure-inline children only: a block
    // child (a label above the text, say) must not drag the box upwards
    let L = Infinity, T = Infinity, R = -Infinity, B = -Infinity;
    const all = [];
    const eat = b => {
      if (!b || (b.width <= 0 && b.height <= 0)) return;
      all.push(b);
      L = Math.min(L, b.left); T = Math.min(T, b.top);
      R = Math.max(R, b.right); B = Math.max(B, b.bottom);
    };
    for (const n of el.childNodes) {
      if (n.nodeType === 3) {
        if (!n.textContent.trim()) continue;
        const rng = document.createRange();
        rng.selectNode(n);
        for (const b of rng.getClientRects()) eat(b);
      } else if (n.nodeType === 1 && getComputedStyle(n).display === "inline") {
        for (const b of n.getClientRects()) eat(b);
      }
    }
    if (!isFinite(L) || R <= L) return null;
    // where the FIRST line starts: an inline-block in front of the text (the
    // "Option A" chip) pushes it right and PowerPoint needs that as an indent
    let first = Infinity;
    for (const b of all) if (Math.round(b.top) === Math.round(T)) first = Math.min(first, b.left);
    return [r2(L - base.left), r2(T - base.top), r2(R - L), r2(B - T),
            r2((isFinite(first) ? first : L) - base.left)];
  };

  const lineCount = el => {
    try {
      const rng = document.createRange();
      rng.selectNodeContents(el);
      const tops = new Set();
      for (const r of rng.getClientRects()) {
        if (r.width > 0 || r.height > 0) tops.add(Math.round(r.top));
      }
      return Math.max(1, tops.size);
    } catch (e) { return 1; }
  };

  const hasOwnText = el => {
    for (const n of el.childNodes) {
      if (n.nodeType === 3 && n.textContent.trim()) return true;
    }
    return false;
  };

  const slides = [...document.querySelectorAll("#deck > .slide")];
  const out = [];
  let iconIx = 0, eid = 0;
  const merged = new WeakSet();   // table cells covered by a single row band

  for (const slide of slides) {
    const base = slide.getBoundingClientRect();
    const items = [];

    const walk = (el, z) => {
      const cs = getComputedStyle(el);
      if (cs.display === "none" || cs.visibility === "hidden") return;
      if (el.classList && el.classList.contains("no-print")) return;

      const b = el.getBoundingClientRect();
      const rect = [r2(b.left - base.left), r2(b.top - base.top), r2(b.width), r2(b.height)];
      const tag = el.tagName.toLowerCase();
      // CSS stacking: a positioned element with z-index paints above its
      // siblings regardless of document order. PowerPoint only knows the order
      // shapes are added in, so the level travels with the item and is sorted on.
      const myId = ++eid;
      const zi = cs.position !== "static" && cs.zIndex !== "auto"
        ? (parseInt(cs.zIndex, 10) || 0) : 0;
      z = Math.max(z, zi);
      const zHere = z;

      if (tag === "svg") {
        if (b.width > 0 && b.height > 0) {
          el.setAttribute("data-icon-ix", String(iconIx));
          items.push({ t: "svg", z: zHere, eid: myId, rect, ix: iconIx++, cls: el.getAttribute("class") || "",
            abs: [r2(b.left + scrollX), r2(b.top + scrollY), r2(b.width), r2(b.height)] });
        }
        return; // icons are rasterised separately
      }

      if (tag === "tr") {
        const cells = [...el.children].filter(c => /^(td|th)$/i.test(c.tagName));
        if (cells.length > 1) {
          const key = c => {
            const q = getComputedStyle(c);
            const f = colour(q.backgroundColor);
            const bwv = parseFloat(q.borderBottomWidth) || 0;
            const bcv = colour(q.borderBottomColor);
            return [f ? f.c : "", bwv, bcv ? bcv.c : ""].join("|");
          };
          const keys = cells.map(key);
          if (keys.every(k => k === keys[0]) && keys[0] !== "||") {
            const q0 = getComputedStyle(cells[0]);
            const f0 = colour(q0.backgroundColor);
            const bw0 = parseFloat(q0.borderBottomWidth) || 0;
            const bc0 = colour(q0.borderBottomColor);
            if (f0 || (bw0 > 0 && bc0)) {
              items.push({
                t: "rect", z: zHere, rect, fill: f0, grad: null,
                bw: [0, 0, bw0, 0], bc: [null, null, bc0, null],
                rad: parseFloat(q0.borderTopLeftRadius) || 0, op: 1,
              });
              cells.forEach(c => merged.add(c));
            }
          }
        }
      }

      if (b.width > 0 && b.height > 0 && !merged.has(el)) {
        const fill = colour(cs.backgroundColor);
        const grad = gradient(cs.backgroundImage);
        const bw = ["Top", "Right", "Bottom", "Left"].map(s =>
          parseFloat(cs["border" + s + "Width"]) || 0);
        const bc = ["Top", "Right", "Bottom", "Left"].map(s =>
          colour(cs["border" + s + "Color"]));
        const bs = ["Top", "Right", "Bottom", "Left"].map(s =>
          cs["border" + s + "Style"]);
        const anyBorder = bw.some(w => w > 0);
        if (fill || grad || anyBorder) {
          items.push({
            t: "rect", z: zHere, eid: myId, rect, fill, grad,
            bw, bc, bs,
            rad: parseFloat(cs.borderTopLeftRadius) || 0,
            op: parseFloat(cs.opacity),
          });
        }
      }

      // a CSS background image (the EDHEC logo) is captured like an icon,
      // otherwise it would be dropped: it is neither a fill nor a border
      if (b.width > 0 && b.height > 0 && cs.backgroundImage.indexOf("url(") >= 0) {
        el.setAttribute("data-icon-ix", String(iconIx));
        items.push({ t: "svg", z: zHere, eid: myId, rect, ix: iconIx++, cls: el.getAttribute("class") || "",
          abs: [r2(b.left + scrollX), r2(b.top + scrollY), r2(b.width), r2(b.height)] });
      }

      // bullet or chevron drawn with ::before
      const pb = getComputedStyle(el, "::before");
      if (pb && pb.content && pb.content !== "none" && pb.content !== "normal") {
        const txt = pb.content.replace(/^["']|["']$/g, "");
        if (txt && txt !== "none") {
          items.push({
            t: "text", rect: [rect[0], rect[1], 24, parseFloat(pb.fontSize) * 1.4],
            runs: [{ s: txt, f: fontOf(pb, el) }], align: "left", pseudo: true, z: zHere,
          });
        }
      }

      {
        const runs = runsOf(el);
        if (runs.length) {
          const pad = [
            parseFloat(cs.paddingLeft) || 0, parseFloat(cs.paddingTop) || 0,
            parseFloat(cs.paddingRight) || 0, parseFloat(cs.paddingBottom) || 0,
          ];
          const flex = cs.display.indexOf("flex") >= 0;
          items.push({
            t: "text", z: zHere, eid: myId, rect, runs, align: cs.textAlign, pad,
            lh: cs.lineHeight === "normal" ? 0 : parseFloat(cs.lineHeight),
            op: parseFloat(cs.opacity),
            // flexbox centres text without touching text-align, so read it too
            jc: flex ? cs.justifyContent : "",
            ai: flex ? cs.alignItems : "",
            lines: lineCount(el),
            flex: cs.display.indexOf("flex") >= 0,
            nowrap: cs.whiteSpace === "nowrap" || cs.whiteSpace === "pre",
            // only a box whose text is its entire content may swallow that text;
            // if a block child sits above it, the text has its own position
            solo: ![...el.children].some(c => getComputedStyle(c).display !== "inline"),
            trect: textBox(el, base),
          });
        }
      }

      for (const ch of el.children) {
        // a pure inline child contributed its text to the block above already
        if (getComputedStyle(ch).display === "inline") continue;
        walk(ch, z);
      }
    };

    const scs = getComputedStyle(slide);
    const sbg = colour(scs.backgroundColor);
    if (sbg && sbg.c !== "FFFFFF") {
      items.push({ t: "rect", rect: [0, 0, r2(base.width), r2(base.height)],
                   fill: sbg, grad: null, bw: [0, 0, 0, 0], bc: [null, null, null, null],
                   rad: 0, op: 1 });
    }
    for (const ch of slide.children) walk(ch, 0);
    items.forEach((it, i) => { it._i = i; });
    items.sort((a, c) => (a.z || 0) - (c.z || 0) || a._i - c._i);
    items.forEach(it => { delete it._i; });
    out.push({ title: slide.getAttribute("data-title") || "", items });
  }
  return JSON.stringify({ w: 1280, h: 720, slides: out });
})()`;

// ------------------------------------------------------------------ CDP glue
const chrome = spawn(CHROME, [
  "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
  "--remote-debugging-port=0", "--window-size=1280,720",
  "--force-device-scale-factor=1", "about:blank",
], { stdio: ["ignore", "pipe", "pipe"] });

const wsUrl = await new Promise((ok, fail) => {
  let buf = "";
  const t = setTimeout(() => fail(new Error("chrome did not report a debug port")), 30000);
  chrome.stderr.on("data", d => {
    buf += d;
    const m = buf.match(/ws:\/\/[^\s]+/);
    if (m) { clearTimeout(t); ok(m[0]); }
  });
});

const ws = new WebSocket(wsUrl);
await new Promise(ok => ws.addEventListener("open", ok, { once: true }));

let seq = 0;
const waiting = new Map();
ws.addEventListener("message", ev => {
  const msg = JSON.parse(ev.data);
  if (msg.id && waiting.has(msg.id)) {
    const { ok, fail } = waiting.get(msg.id);
    waiting.delete(msg.id);
    msg.error ? fail(new Error(JSON.stringify(msg.error))) : ok(msg.result);
  }
});
const send = (method, params = {}, sessionId) =>
  new Promise((ok, fail) => {
    const id = ++seq;
    waiting.set(id, { ok, fail });
    ws.send(JSON.stringify({ id, method, params, sessionId }));
  });

const { targetId } = await send("Target.createTarget", { url: "about:blank" });
const { sessionId } = await send("Target.attachToTarget", { targetId, flatten: true });
await send("Page.enable", {}, sessionId);
await send("Runtime.enable", {}, sessionId);
// the print stylesheet is the authoritative one: on screen every slide but the
// active one is hidden, which would leave us with nothing to measure
await send("Emulation.setEmulatedMedia", { media: "print" }, sessionId);
await send("Page.navigate", { url }, sessionId);
await new Promise(r => setTimeout(r, 3000));

const { result, exceptionDetails } = await send(
  "Runtime.evaluate",
  { expression: EXTRACTOR, returnByValue: true, awaitPromise: false },
  sessionId,
);
if (exceptionDetails) {
  console.error(JSON.stringify(exceptionDetails, null, 1).slice(0, 2000));
  process.exit(1);
}

const parsed = JSON.parse(result.value);

// Icons stay pictures: they are line art, not text, and nobody edits them in
// PowerPoint. Each is captured ISOLATED on a transparent background. Grabbing
// them straight off the page would bake whatever sits behind them into the
// picture, and the honeycomb strip spans the footer, so its capture would carry
// a pixel copy of the footer text that then collides with the real text box.
await send("Emulation.setDefaultBackgroundColorOverride",
  { color: { r: 0, g: 0, b: 0, a: 0 } }, sessionId);
await send("Runtime.evaluate", { expression: `(() => {
  const st = document.createElement("style");
  st.textContent = "html.isolate, html.isolate body { background: transparent !important; }" +
                   "html.isolate body * { visibility: hidden !important; }" +
                   "html.isolate [data-show], html.isolate [data-show] * { visibility: visible !important; }";
  document.head.appendChild(st);
  // the <defs> sprite holds the honeycomb pattern and mask; hiding it would
  // leave every element that paints with url(#...) empty
  const defs = document.querySelector("body > svg[aria-hidden]");
  if (defs) defs.setAttribute("data-show", "1");
  document.documentElement.classList.add("isolate");
})()` }, sessionId);
const iconDir = outArg.replace(/\.json$/, "") + "-icons";
mkdirSync(iconDir, { recursive: true });
let n = 0;
for (const slide of parsed.slides) {
  for (const it of slide.items) {
    if (it.t !== "svg") continue;
    const [x, y, w, h] = it.abs;
    await send("Runtime.evaluate", { expression:
      `document.querySelector('[data-icon-ix="${it.ix}"]').setAttribute("data-show","1")` }, sessionId);
    const shot = await send("Page.captureScreenshot", {
      format: "png", captureBeyondViewport: true, fromSurface: true,
      clip: { x, y, width: w, height: h, scale: 4 },
    }, sessionId);
    await send("Runtime.evaluate", { expression:
      `document.querySelector('[data-icon-ix="${it.ix}"]').removeAttribute("data-show")` }, sessionId);
    const file = `icon${String(++n).padStart(4, "0")}.png`;
    writeFileSync(`${iconDir}/${file}`, Buffer.from(shot.data, "base64"));
    it.img = file;
    delete it.abs;
    delete it.ix;
  }
}
console.log(`  ${n} icons -> ${iconDir}/`);

writeFileSync(outArg, JSON.stringify(parsed));
console.log(
  `${outArg}: ${parsed.slides.length} slides, ` +
  `${parsed.slides.reduce((n, s) => n + s.items.length, 0)} elements`,
);

ws.close();
chrome.kill();
process.exit(0);
