import {handleAccount, userFrom, useQuota, UserState, ghTokenOf, useBudget, NEURONS, useCounter} from "./account.js";
import {runPro, PRO_LIMITS} from "./pro.js";
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
};
// lucid-origin وphoenix شلناهن: الصورة الوحدة منهن كانت تاكل ربع رصيد اليوم كلّه
const b64ToBytes = s => Uint8Array.from(atob(s), c => c.charCodeAt(0));
const clamp16 = (v, lo, hi) => Math.max(lo, Math.min(hi, Math.round((+v || 1024) / 16) * 16));

// klein (أغلى) بس للتعديل عالصور أو إذا انطلب بالاسم؛ غير هيك schnell (الأرخص)
function pickModel(form) {
  const refs = form.getAll("image").filter(f => f && typeof f !== "string");
  if (refs.length) return "flux-2-klein-4b";
  return String(form.get("model")) === "flux-2-klein-4b" ? "flux-2-klein-4b" : "flux-1-schnell";
}
async function runImage(env, form) {
  const prompt = clean(form.get("prompt"), 2000).trim();
  if (prompt.length < 2) throw Object.assign(new Error("no_prompt"), {status: 400});
  const model = CF_MODELS[pickModel(form)];
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

// ---- 🧠 الذكاء النصّي: من حساب المستخدم نفسه على GitHub Models (GPT ببلاش).
// الشات والأفكار ما بيصرفوا شي من رصيدنا. بدون حساب: بس ترجمة البرومبت على موديل صغير.
const GH_MODELS = ["openai/gpt-4.1-mini", "openai/gpt-4o-mini", "openai/gpt-4.1-nano"];
async function llm(env, user, messages, {max_tokens = 900, temperature = 0.7, vision = false, tiny = false} = {}) {
  const gh = await ghTokenOf(env, user).catch(() => null);
  if (gh) {
    for (const model of vision ? ["openai/gpt-4o-mini", "openai/gpt-4.1-mini"] : GH_MODELS) {
      try {
        const r = await fetch("https://models.github.ai/inference/chat/completions", {method: "POST",
          headers: {"Authorization": "Bearer " + gh, "Content-Type": "application/json", "Accept": "application/json", "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "graphicwo-gateway"},
          body: JSON.stringify({model, messages, max_tokens, temperature})});
        if (r.status === 401 || r.status === 403) break;          // التوكن انتهى أو ما إله صلاحية
        if (!r.ok) continue;                                       // حد الموديل خلص، جرّب اللي بعده
        const t = (await r.json())?.choices?.[0]?.message?.content;
        if (t) return {text: String(t).trim(), via: "github:" + model.split("/")[1]};
      } catch {}
    }
  }
  // بدون حساب: بس المهام الصغيرة (ترجمة البرومبت) على موديل صغير كتير رخيص (تقريباً 5 neuron)
  if (tiny && env.AI) {
    const b = await useBudget(env, 6);
    if (b.ok) {
      const r = await env.AI.run("@cf/meta/llama-3.1-8b-instruct-fast", {messages, max_tokens: Math.min(max_tokens, 300), temperature: 0.2});
      const t = r?.response ?? r?.choices?.[0]?.message?.content;
      if (t) return {text: String(t).trim(), via: "cf-tiny"};
    }
  }
  throw Object.assign(new Error(gh ? "gh_limit" : "login_required"), {status: gh ? 429 : 401});
}

// ---- فكرة إبداعية حسب الصورة المرفقة (موديلات صغيرة ومجانية)
async function imageIdea(env, form, user) {
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
  const r = await llm(env, user, messages, {max_tokens: 100, temperature: 1.0, vision: true});
  return r.text.replace(/^["'«]+|["'»]+$/g, "");
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

async function chat(env, body, user) {
  const msgs = Array.isArray(body.messages) ? body.messages.slice(-16) : [];
  const messages = [{role: "system", content: CHAT_SYSTEM}];
  for (const m of msgs) {
    if (!m || !["user", "assistant"].includes(m.role)) continue;
    messages.push({role: m.role, content: clean(m.content, 4000)});
  }
  if (messages.length < 2) throw Object.assign(new Error("no_message"), {status: 400});
  const r = await llm(env, user, messages);
  return {reply: r.text.replace(/<think>[\s\S]*?<\/think>/g, "").trim(), via: r.via};
}

const nextReset = () => { const d = new Date(); d.setUTCHours(24, 0, 0, 0); return d.getTime(); };
// حالة رصيد السيرفر لليوم (للواجهة)
async function serverStatus(env) { const b = await useBudget(env, 0, true); return {used: b.used || 0, max: b.max || 0, reset: nextReset()}; }

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
      if (env.LIMITER) {
        const {success} = await env.LIMITER.limit({key: "chat:" + (req.headers.get("CF-Connecting-IP") || "anon")});
        if (!success) return json({error: "rate_limited"}, 429, cors);
      }
      let body; try { body = await req.json(); } catch { return json({error: "bad_request"}, 400, cors); }
      try { return json(await chat(env, body, await userFrom(req, env)), 200, cors); }
      catch (e) { const m = String(e && e.message || e); return json({error: /login_required|gh_limit/.test(m) ? m : "failed", detail: m.slice(0, 160)}, e.status || 502, cors); }
    }
    // ترجمة البرومبت للإنجليزي / فكرة عشوائية
    if (req.method === "POST" && url.pathname === "/text") {
      if (!allowed.includes(origin)) return json({error: "forbidden"}, 403, cors);
      if (env.LIMITER) { const {success} = await env.LIMITER.limit({key: "text:" + (req.headers.get("CF-Connecting-IP") || "anon")}); if (!success) return json({error: "rate_limited"}, 429, cors); }
      let body; try { body = await req.json(); } catch { return json({error: "bad_request"}, 400, cors); }
      const user = await userFrom(req, env), task = body.task === "idea" ? "idea" : "translate";
      const text = clean(body.text, 2000);
      const sys = task === "translate"
        ? "Translate the user's image-generation prompt (Arabic, possibly Levantine dialect) into a clear, detailed English prompt. Keep every detail and do not add things that were not mentioned. Any text the user wants written in the image (in quotes or after words like اكتب/مكتوب/كتابة) must stay EXACTLY as written inside double quotes, untranslated. Output ONLY the English prompt."
        : "You write ONE original, vivid image-generation prompt (max 35 words) with surprising creative details, lighting and art style. Reply with the prompt only, no quotes.";
      try { const r = await llm(env, user, [{role: "system", content: sys}, {role: "user", content: text}], {max_tokens: 300, temperature: task === "idea" ? 1.0 : 0.2, tiny: task === "translate"});
        return json({text: r.text.replace(/^["'«]+|["'»]+$/g, ""), via: r.via}, 200, cors); }
      catch (e) { return json({error: String(e.message || e)}, e.status || 502, cors); }
    }
    if (req.method === "POST" && url.pathname === "/idea") {
      if (!allowed.includes(origin)) return json({error: "forbidden"}, 403, cors);
      if (env.IMG_LIMITER) {
        const {success} = await env.IMG_LIMITER.limit({key: "idea:" + (req.headers.get("CF-Connecting-IP") || "anon")});
        if (!success) return json({error: "rate_limited"}, 429, cors);
      }
      try { const idea = await imageIdea(env, await req.formData(), await userFrom(req, env)); if (!idea) throw new Error("empty"); return json({idea}, 200, cors); }
      catch (e) { return json({error: "failed", detail: String(e && e.message || e).slice(0, 160)}, e.status || 502, cors); }
    }
    // 🔥 GPT Image 2.5 عبر Pollo (مدفوع) — بس للمسجّلين، وبسقف يومي لكل مستخدم وللكل
    if (url.pathname === "/pro" && (req.method === "POST" || req.method === "GET")) {
      if (!allowed.includes(origin)) return json({error: "forbidden"}, 403, cors);
      const user = await userFrom(req, env);
      if (req.method === "GET") {
        const u = user ? await useCounter(env, "pro:u:" + user.uid, PRO_LIMITS.perUser, true) : {used: 0};
        const g = await useCounter(env, "global:pro", PRO_LIMITS.perDay, true);
        return json({enabled: !!env.POLLO_KEY, login: !!user, used: u.used || 0, max: PRO_LIMITS.perUser, left: Math.max(0, PRO_LIMITS.perDay - (g.used || 0)), reset: nextReset()}, 200, cors);
      }
      if (!env.POLLO_KEY) return json({error: "not_configured"}, 503, cors);
      if (!user) return json({error: "login_required"}, 401, cors);
      let form; try { form = await req.formData(); } catch { return json({error: "bad_request"}, 400, cors); }
      const u = await useCounter(env, "pro:u:" + user.uid, PRO_LIMITS.perUser, true);
      if ((u.used || 0) >= PRO_LIMITS.perUser) return json({error: "pro_user_limit", used: u.used, max: PRO_LIMITS.perUser, reset: nextReset()}, 429, cors);
      const g = await useCounter(env, "global:pro", PRO_LIMITS.perDay);
      if (!g.ok) return json({error: "pro_day_limit", reset: nextReset()}, 429, cors);
      try {
        const out = await runPro(env, form);
        await useCounter(env, "pro:u:" + user.uid, PRO_LIMITS.perUser);
        return new Response(out.bytes, {headers: {"Content-Type": out.type, "Cache-Control": "no-store", ...cors}});
      } catch (e) { return json({error: String(e.message || e).slice(0, 80)}, e.status || 502, cors); }
    }
    if (req.method === "GET" && url.pathname === "/status") return json(await serverStatus(env), 200, cors);
    if (req.method === "POST" && url.pathname === "/img") {
      if (!allowed.includes(origin)) return json({error: "forbidden"}, 403, cors);
      if (!env.AI) return json({error: "not_configured"}, 503, cors);
      if (env.IMG_LIMITER) {
        const {success} = await env.IMG_LIMITER.limit({key: req.headers.get("CF-Connecting-IP") || "anon"});
        if (!success) return json({error: "rate_limited"}, 429, cors);
      }
      let form;
      try { form = await req.formData(); } catch { return json({error: "bad_request"}, 400, cors); }
      const user = await userFrom(req, env);
      const q = await useQuota(env, req, user, true);
      if (q.used >= (q.max || 1e9)) return json({error: "daily_limit", used: q.used, max: q.max, login: !user}, 429, cors);
      const b = await useBudget(env, NEURONS[pickModel(form)] || 160);
      if (!b.ok) return json({error: "server_daily", reset: nextReset()}, 429, cors);
      await useQuota(env, req, user);
      try {
        const bytes = await runImage(env, form);
        const type = sniff(bytes) === "png" ? "image/png" : sniff(bytes) === "webp" ? "image/webp" : "image/jpeg";
        return new Response(bytes, {headers: {"Content-Type": type, "Cache-Control": "no-store", ...cors}});
      } catch (e) {
        const m = String(e && e.message || e);
        const quota = /neuron|quota|4006|daily/i.test(m);
        if (quota) { await useBudget(env, 1e6).catch(() => {}); }
        return json({error: quota ? "server_daily" : "failed", reset: nextReset(), detail: m.slice(0, 160)}, e.status || (quota ? 429 : 502), cors);
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
