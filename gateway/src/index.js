import {handleAccount, userFrom, useQuota, UserState} from "./account.js";
export {UserState};
// GraphicWO gateway: receives 👍 images from the studio and stores them in the
// private dataset repo. The GitHub token lives only here (Worker secret), never in the website.
// No IP addresses or personal data are stored.

const MAX_BYTES = 4 * 1024 * 1024;
const MIN_BYTES = 2000;

function json(body, status, cors) {
  return new Response(JSON.stringify(body), {status, headers: {"Content-Type": "application/json", ...cors}});
}

function sniff(b) {
  if (b[0] === 0xFF && b[1] === 0xD8 && b[2] === 0xFF) return "jpg";
  if (b[0] === 0x89 && b[1] === 0x50 && b[2] === 0x4E && b[3] === 0x47) return "png";
  if (b[0] === 0x52 && b[1] === 0x49 && b[2] === 0x46 && b[3] === 0x46 && b[8] === 0x57 && b[9] === 0x45) return "webp";
  return null;
}

function toB64(bytes) {
  let s = "";
  for (let i = 0; i < bytes.length; i += 0x8000) s += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000));
  return btoa(s);
}

const clean = (v, n) => String(v ?? "").replace(/[\u0000-\u001f]/g, " ").slice(0, n);

async function putFile(env, path, b64, message) {
  const r = await fetch(`https://api.github.com/repos/${env.DATASET_REPO}/contents/${path}`, {
    method: "PUT",
    headers: {
      "Authorization": `Bearer ${env.DATASET_TOKEN}`,
      "Accept": "application/vnd.github+json",
      "User-Agent": "graphicwo-gateway",
      "X-GitHub-Api-Version": "2022-11-28",
    },
    body: JSON.stringify({message, content: b64, committer: {name: "GraphicWO Bot", email: "graphicwo@users.noreply.github.com"}}),
  });
  if (!r.ok) throw new Error("github " + r.status);
}

// ---- صور مجانية من Cloudflare Workers AI (10,000 neurons باليوم مجاناً لكل الحساب)
const CF_MODELS = {
  "flux-1-schnell": "@cf/black-forest-labs/flux-1-schnell",
  "flux-2-klein-4b": "@cf/black-forest-labs/flux-2-klein-4b",
  "lucid-origin": "@cf/leonardo/lucid-origin",
  "phoenix": "@cf/leonardo/phoenix-1.0",
};
const b64ToBytes = s => Uint8Array.from(atob(s), c => c.charCodeAt(0));
const clamp16 = (v, lo, hi) => Math.max(lo, Math.min(hi, Math.round((+v || 1024) / 16) * 16));

async function runImage(env, form) {
  const prompt = clean(form.get("prompt"), 2000).trim();
  if (prompt.length < 2) throw Object.assign(new Error("no_prompt"), {status: 400});
  const key = String(form.get("model") || "flux-2-klein-4b");
  const model = CF_MODELS[key] || CF_MODELS["flux-2-klein-4b"];
  const width = clamp16(form.get("width"), 256, 1280), height = clamp16(form.get("height"), 256, 1280);
  const seed = Math.floor(Math.random() * 2 ** 31);
  const refs = form.getAll("image").filter(f => f && typeof f !== "string").slice(0, 4);
  let out;
  if (model.includes("flux-2-klein")) {
    const fd = new FormData();
    fd.append("prompt", prompt); fd.append("width", String(width)); fd.append("height", String(height)); fd.append("seed", String(seed));
    for (let i = 0; i < refs.length; i++) {
      if (refs[i].size > MAX_BYTES) throw Object.assign(new Error("bad_size"), {status: 413});
      fd.append("input_image_" + i, refs[i]);
    }
    const r = new Response(fd);
    out = await env.AI.run(model, {multipart: {body: r.body, contentType: r.headers.get("content-type")}});
  } else if (model.includes("schnell")) {
    out = await env.AI.run(model, {prompt, steps: 4});
  } else {
    out = await env.AI.run(model, {prompt, width, height, seed});
  }
  if (out instanceof ReadableStream) return new Uint8Array(await new Response(out).arrayBuffer());
  if (out && out.image) return b64ToBytes(out.image);
  throw new Error("no_image");
}

// ---- فكرة إبداعية حسب الصورة المرفقة (موديلات صغيرة ومجانية)
async function imageIdea(env, form) {
  const img = form.get("image");
  if (!img || typeof img === "string" || img.size > MAX_BYTES) throw Object.assign(new Error("no_image"), {status: 400});
  const bytes = new Uint8Array(await img.arrayBuffer());
  if (!sniff(bytes)) throw Object.assign(new Error("bad_type"), {status: 415});
  const lang = {ar: "Levantine Arabic", fr: "French"}[String(form.get("lang"))] || "English";
  const seedWords = ["cinematic", "fantasy", "cyberpunk", "anime", "vintage poster", "3D Pixar", "watercolor", "neon night", "luxury product ad", "epic battle", "cozy", "underwater", "space", "Minecraft style", "comic book"];
  const vibe = seedWords[Math.floor(Math.random() * seedWords.length)];
  const mime = sniff(bytes) === "png" ? "image/png" : sniff(bytes) === "webp" ? "image/webp" : "image/jpeg";
  const messages = [
    {role: "system", content: "You write short, creative image-editing instructions for an AI image editor. Reply with ONE instruction only, max 30 words, no quotes, no preamble."},
    {role: "user", content: [
      {type: "text", text: `Look at this reference image. Suggest one surprising, fun way to transform or edit THIS image while keeping its main subject, with a ${vibe} twist. Write the instruction in ${lang}.`},
      {type: "image_url", image_url: {url: `data:${mime};base64,${toB64(bytes)}`}},
    ]},
  ];
  let r, lastErr;
  for (const m of ["@cf/meta/llama-4-scout-17b-16e-instruct", "@cf/google/gemma-3-12b-it", "@cf/mistralai/mistral-small-3.1-24b-instruct"]) {
    try { r = await env.AI.run(m, {messages, max_tokens: 100, temperature: 1.0}); if (r && (r.response || r.choices)) break; } catch (e) { lastErr = e; r = null; }
  }
  if (!r) throw lastErr || new Error("no_model");
  if (!r.response && r.choices) r.response = r.choices[0]?.message?.content;
  return String(r.response || "").trim().replace(/^["'«]+|["'»]+$/g, "");
}

// ---- 💬 شات مجاني (Cloudflare Workers AI)
const CHAT_SYSTEM = `You are "GraphicWO AI", a friendly, smart and helpful assistant inside the free GraphicWO AI Studio app.
- Always answer in the same language as the user. If the user writes Arabic, answer in clear, simple Arabic with a light Syrian/Levantine touch (never Egyptian words), and never mix in other scripts or languages.
- Be accurate and helpful; use short paragraphs and simple lists when useful.
- You CAN create images. When the user asks you to draw/create/generate/design an image, picture, logo, poster, wallpaper etc., reply with ONE short sentence and then, on its own line, exactly:
[[IMAGE: <detailed English image prompt with subject, style, lighting, colors. NEVER put any words, letters, titles or Arabic in this part> || <ALL text the user wants written on the image, exactly in its original language, max 2 short lines separated by " / ", or empty>]]
- When the user asks for a summary image / infographic / "صورة تلخيص" about a topic, reply with ONE short sentence and then, on its own line, exactly:
[[INFO: <short title in the user's language> || <point 1> || <point 2> || <point 3> || <point 4> || <point 5> || <English prompt for a matching decorative background, no text>]]
  Points must be short (max 12 words each), factual, in the user's language.
- Image models CANNOT draw Arabic letters. When the user wants an educational image of letters, the alphabet, numbers, words or a chart (e.g. "الحروف العربية", "الأبجدية", "الأرقام"), reply with ONE short sentence and then, on its own line, exactly:
[[LETTERS: <title in the user's language> || <item> | <item> | ... || <creative, detailed English prompt for the background illustration that matches what the user asked (characters, place, colors, art style), with NO letters or text, leaving the middle area light and simple> || <layout: cards, bubbles or balloons>]]
  Each item is "<letter or number>:<short example word>:<one emoji>", in order. Be creative with the background and layout so every request looks different. For the Arabic alphabet give all 28 letters أ ب ت ث ج ح خ د ذ ر ز س ش ص ض ط ظ ع غ ف ق ك ل م ن ه و ي.
- Never produce sexual content, content about minors, hateful content, or real-person deepfakes.`;

async function chat(env, body) {
  const msgs = Array.isArray(body.messages) ? body.messages.slice(-16) : [];
  const messages = [{role: "system", content: CHAT_SYSTEM}];
  for (const m of msgs) {
    if (!m || !["user", "assistant"].includes(m.role)) continue;
    messages.push({role: m.role, content: clean(m.content, 4000)});
  }
  if (messages.length < 2) throw Object.assign(new Error("no_message"), {status: 400});
  let lastErr;
  const CHAT_MODELS = ["@cf/mistralai/mistral-small-3.1-24b-instruct", "@cf/meta/llama-3.3-70b-instruct-fp8-fast", "@cf/meta/llama-3.1-8b-instruct-fast"];
  const order = CHAT_MODELS.includes(body.model) ? [body.model, ...CHAT_MODELS.filter(m => m !== body.model)] : CHAT_MODELS;
  for (const model of order) {
    try {
      const r = await env.AI.run(model, {messages, max_tokens: 900, temperature: 0.7});
      let text = r?.response ?? r?.choices?.[0]?.message?.content ?? (typeof r === "string" ? r : "");
      text = String(text || "").replace(/<think>[\s\S]*?<\/think>/g, "").trim();
      if (text) return body.debug ? model + " :: " + text : text;
    } catch (e) { lastErr = e; }
  }
  throw lastErr || new Error("no_reply");
}

export default {
  async fetch(req, env) {
    const allowed = String(env.ALLOWED_ORIGINS || "").split(",").map(s => s.trim()).filter(Boolean);
    const origin = req.headers.get("Origin") || "";
    const cors = {
      "Access-Control-Allow-Origin": allowed.includes(origin) ? origin : allowed[0] || "*",
      "Access-Control-Allow-Methods": "GET, POST, DELETE, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Authorization",
      "Vary": "Origin",
    };
    if (req.method === "OPTIONS") return new Response(null, {headers: cors});
    const url = new URL(req.url);
    if (req.method === "GET" && url.pathname === "/") return json({ok: true, service: "graphicwo-gateway"}, 200, cors);
    if (url.pathname.startsWith("/auth/") || url.pathname.startsWith("/me") || url.pathname.startsWith("/gallery")) {
      if (!url.pathname.startsWith("/auth/") && !allowed.includes(origin)) return json({error: "forbidden"}, 403, cors);
      const r = await handleAccount(req, env, url, cors, json, toB64, sniff); if (r) return r;
    }
    if (req.method === "POST" && url.pathname === "/chat") {
      if (!allowed.includes(origin)) return json({error: "forbidden"}, 403, cors);
      if (!env.AI) return json({error: "not_configured"}, 503, cors);
      if (env.LIMITER) {
        const {success} = await env.LIMITER.limit({key: "chat:" + (req.headers.get("CF-Connecting-IP") || "anon")});
        if (!success) return json({error: "rate_limited"}, 429, cors);
      }
      let body; try { body = await req.json(); } catch { return json({error: "bad_request"}, 400, cors); }
      try { return json({reply: await chat(env, body)}, 200, cors); }
      catch (e) { const m = String(e && e.message || e); return json({error: /neuron|quota|limit|4006|daily/i.test(m) ? "daily_limit" : "failed", detail: m.slice(0, 160)}, e.status || 502, cors); }
    }
    if (req.method === "POST" && url.pathname === "/idea") {
      if (!allowed.includes(origin)) return json({error: "forbidden"}, 403, cors);
      if (!env.AI) return json({error: "not_configured"}, 503, cors);
      if (env.IMG_LIMITER) {
        const {success} = await env.IMG_LIMITER.limit({key: "idea:" + (req.headers.get("CF-Connecting-IP") || "anon")});
        if (!success) return json({error: "rate_limited"}, 429, cors);
      }
      try { const idea = await imageIdea(env, await req.formData()); if (!idea) throw new Error("empty"); return json({idea}, 200, cors); }
      catch (e) { return json({error: "failed", detail: String(e && e.message || e).slice(0, 160)}, e.status || 502, cors); }
    }
    if (req.method === "POST" && url.pathname === "/img") {
      if (!allowed.includes(origin)) return json({error: "forbidden"}, 403, cors);
      if (!env.AI) return json({error: "not_configured"}, 503, cors);
      if (env.IMG_LIMITER) {
        const {success} = await env.IMG_LIMITER.limit({key: req.headers.get("CF-Connecting-IP") || "anon"});
        if (!success) return json({error: "rate_limited"}, 429, cors);
      }
      const user = await userFrom(req, env);
      const q = await useQuota(env, req, user);
      if (!q.ok) return json({error: "daily_limit", used: q.used, max: q.max, login: !user}, 429, cors);
      let form;
      try { form = await req.formData(); } catch { return json({error: "bad_request"}, 400, cors); }
      try {
        const bytes = await runImage(env, form);
        const type = sniff(bytes) === "png" ? "image/png" : sniff(bytes) === "webp" ? "image/webp" : "image/jpeg";
        return new Response(bytes, {headers: {"Content-Type": type, "Cache-Control": "no-store", ...cors}});
      } catch (e) {
        const m = String(e && e.message || e);
        const quota = /neuron|quota|limit|capacity|4006|daily/i.test(m);
        return json({error: quota ? "daily_limit" : "failed", detail: m.slice(0, 160)}, e.status || (quota ? 429 : 502), cors);
      }
    }
    if (req.method !== "POST" || url.pathname !== "/like") return json({error: "not_found"}, 404, cors);
    if (!allowed.includes(origin)) return json({error: "forbidden"}, 403, cors);
    if (!env.DATASET_TOKEN) return json({error: "not_configured"}, 503, cors);

    if (env.LIMITER) {
      const ip = req.headers.get("CF-Connecting-IP") || "anon";
      const {success} = await env.LIMITER.limit({key: ip});
      if (!success) return json({error: "rate_limited"}, 429, cors);
    }

    let form;
    try { form = await req.formData(); } catch { return json({error: "bad_request"}, 400, cors); }
    const img = form.get("image");
    if (!img || typeof img === "string") return json({error: "no_image"}, 400, cors);
    if (img.size > MAX_BYTES || img.size < MIN_BYTES) return json({error: "bad_size"}, 413, cors);
    const bytes = new Uint8Array(await img.arrayBuffer());
    const ext = sniff(bytes);
    if (!ext) return json({error: "bad_type"}, 415, cors);

    let meta = {};
    try { meta = JSON.parse(form.get("meta") || "{}"); } catch {}
    const record = {
      prompt: clean(meta.prompt, 600),
      engine: clean(meta.engine, 30),
      model: clean(meta.model, 80),
      style: clean(meta.style, 40),
      ratio: clean(meta.ratio, 10),
      lang: clean(meta.lang, 5),
      source: clean(meta.source, 10) || "like",
      received: new Date().toISOString(),
    };

    const id = new Date().toISOString().replace(/[:.]/g, "-") + "-" + crypto.randomUUID().slice(0, 8);
    const day = id.slice(0, 10);
    try {
      await putFile(env, `pending/${day}/${id}.${ext}`, toB64(bytes), "👍 new image");
      await putFile(env, `pending/${day}/${id}.json`, toB64(new TextEncoder().encode(JSON.stringify(record, null, 1))), "👍 new image info");
    } catch (e) {
      return json({error: "storage_failed"}, 502, cors);
    }
    return json({ok: true}, 200, cors);
  },
};
