// 👤 حسابات GraphicWO عبر GitHub (OAuth) — بس الاسم والصورة، ما منطلب أي صلاحية على حساب المستخدم
const enc = new TextEncoder();
const b64u = s => btoa(s).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
const unb64u = s => atob(s.replace(/-/g, "+").replace(/_/g, "/"));
async function hmac(key, data) {
  const k = await crypto.subtle.importKey("raw", enc.encode(key), {name: "HMAC", hash: "SHA-256"}, false, ["sign"]);
  const sig = await crypto.subtle.sign("HMAC", k, enc.encode(data));
  return [...new Uint8Array(sig)].map(b => b.toString(16).padStart(2, "0")).join("");
}
export async function sign(env, obj) { const p = b64u(JSON.stringify(obj)); return p + "." + await hmac(env.GH_OAUTH_SECRET, p); }
export async function verify(env, tok) {
  if (!tok || !env.GH_OAUTH_SECRET) return null;
  const [p, s] = String(tok).split(".");
  if (!p || !s || await hmac(env.GH_OAUTH_SECRET, p) !== s) return null;
  try { const o = JSON.parse(unb64u(p)); return o.exp > Date.now() ? o : null; } catch { return null; }
}
export async function userFrom(req, env) {
  const h = req.headers.get("Authorization") || "";
  return h.startsWith("Bearer ") ? verify(env, h.slice(7)) : null;
}

export const LIMITS = {anon: 25, user: 100};   // صور GraphicWO ⚡ باليوم

// عدّاد يومي + معرض لكل مستخدم (Durable Object ببلاش)
export class UserState {
  constructor(ctx) { this.s = ctx.storage; }
  async fetch(req) {
    const url = new URL(req.url), day = new Date().toISOString().slice(0, 10);
    if (url.pathname === "/use") {
      const max = +url.searchParams.get("max"), peek = url.searchParams.get("peek") === "1";
      let q = (await this.s.get("q")) || {day, n: 0};
      if (q.day !== day) q = {day, n: 0};
      if (peek) return Response.json({used: q.n, max});
      if (q.n >= max) return Response.json({ok: false, used: q.n, max});
      q.n++; await this.s.put("q", q);
      return Response.json({ok: true, used: q.n, max});
    }
    if (url.pathname === "/gal/list") return Response.json((await this.s.get("gal")) || []);
    if (url.pathname === "/gal/add") {
      const it = await req.json(); const g = (await this.s.get("gal")) || [];
      g.unshift(it); if (g.length > 300) g.length = 300; await this.s.put("gal", g); return Response.json({ok: true, count: g.length});
    }
    if (url.pathname === "/gal/del") {
      const {id} = await req.json(); const g = ((await this.s.get("gal")) || []).filter(x => x.id !== id);
      await this.s.put("gal", g); return Response.json({ok: true});
    }
    return new Response("nf", {status: 404});
  }
}
const stub = (env, key) => env.USERS.get(env.USERS.idFromName(key));
export async function useQuota(env, req, user, peek = false) {
  if (!env.USERS) return {ok: true};
  const key = user ? "u:" + user.uid : "ip:" + (req.headers.get("CF-Connecting-IP") || "anon");
  const max = user ? LIMITS.user : LIMITS.anon;
  return (await stub(env, key).fetch(`https://do/use?max=${max}${peek ? "&peek=1" : ""}`)).json();
}

const ghApi = (env, path, init = {}) => fetch("https://api.github.com/repos/" + env.DATASET_REPO + "/contents/" + path, {...init,
  headers: {"Authorization": `Bearer ${env.DATASET_TOKEN}`, "Accept": init.raw ? "application/vnd.github.raw" : "application/vnd.github+json", "User-Agent": "graphicwo-gateway", "X-GitHub-Api-Version": "2022-11-28", ...(init.headers || {})}});

// يرجّع Response أو null إذا المسار مش إلنا
export async function handleAccount(req, env, url, cors, json, toB64, sniff) {
  const p = url.pathname;
  const studio = env.STUDIO_URL || "https://graphicwo-studio.github.io/studio/";
  if (p === "/auth/login") {
    if (!env.GH_CLIENT_ID || !env.GH_OAUTH_SECRET) return json({error: "not_configured"}, 503, cors);
    const state = await sign(env, {r: studio, exp: Date.now() + 10 * 60e3, n: crypto.randomUUID()});
    const q = new URLSearchParams({client_id: env.GH_CLIENT_ID, redirect_uri: url.origin + "/auth/callback", scope: "read:user", state, allow_signup: "true"});
    return Response.redirect("https://github.com/login/oauth/authorize?" + q, 302);
  }
  if (p === "/auth/callback") {
    const st = await verify(env, url.searchParams.get("state"));
    if (!st) return new Response("Login expired, please try again.", {status: 400});
    const tr = await fetch("https://github.com/login/oauth/access_token", {method: "POST", headers: {"Accept": "application/json", "Content-Type": "application/json"},
      body: JSON.stringify({client_id: env.GH_CLIENT_ID, client_secret: env.GH_OAUTH_SECRET, code: url.searchParams.get("code"), redirect_uri: url.origin + "/auth/callback"})});
    const tj = await tr.json();
    if (!tj.access_token) return Response.redirect(studio + "#gwo_login=failed", 302);
    const u = await (await fetch("https://api.github.com/user", {headers: {"Authorization": "Bearer " + tj.access_token, "User-Agent": "graphicwo-gateway"}})).json();
    // ما منحتفظ بتوكن GitHub نهائياً
    const tok = await sign(env, {uid: u.id, login: u.login, avatar: u.avatar_url, exp: Date.now() + 90 * 864e5});
    return Response.redirect(studio + "#gwo_token=" + tok, 302);
  }
  if (!p.startsWith("/me") && !p.startsWith("/gallery")) return null;
  const user = await userFrom(req, env);
  if (!user) return json({error: "login_required"}, 401, cors);
  if (p === "/me") { const q = await useQuota(env, req, user, true); return json({login: user.login, avatar: user.avatar, used: q.used || 0, max: q.max || LIMITS.user, anonMax: LIMITS.anon}, 200, cors); }
  const s = stub(env, "u:" + user.uid);
  if (p === "/gallery" && req.method === "GET") return json(await (await s.fetch("https://do/gal/list")).json(), 200, cors);
  if (p === "/gallery" && req.method === "POST") {
    const form = await req.formData(); const img = form.get("image");
    if (!img || typeof img === "string" || img.size > 4 * 1024 * 1024) return json({error: "bad_image"}, 400, cors);
    const bytes = new Uint8Array(await img.arrayBuffer()); if (!sniff(bytes)) return json({error: "bad_type"}, 415, cors);
    let meta = {}; try { meta = JSON.parse(form.get("meta") || "{}"); } catch {}
    const id = Date.now() + "-" + crypto.randomUUID().slice(0, 6), path = `gallery/${user.uid}/${id}.jpg`;
    const r = await ghApi(env, path, {method: "PUT", body: JSON.stringify({message: "🖼 gallery", content: toB64(bytes), committer: {name: "GraphicWO Bot", email: "graphicwo@users.noreply.github.com"}})});
    if (!r.ok) return json({error: "storage_failed"}, 502, cors);
    const it = {id, prompt: String(meta.prompt || "").slice(0, 300), ratio: String(meta.ratio || "").slice(0, 12), created: Date.now()};
    await s.fetch("https://do/gal/add", {method: "POST", body: JSON.stringify(it)});
    return json({ok: true, item: it}, 200, cors);
  }
  const m = p.match(/^\/gallery\/([\w-]{6,40})$/);
  if (m && req.method === "GET") {
    const r = await ghApi(env, `gallery/${user.uid}/${m[1]}.jpg`, {raw: true});
    if (!r.ok) return json({error: "not_found"}, 404, cors);
    return new Response(r.body, {headers: {"Content-Type": "image/jpeg", "Cache-Control": "private, max-age=86400", ...cors}});
  }
  if (m && req.method === "DELETE") {
    const path = `gallery/${user.uid}/${m[1]}.jpg`, cur = await ghApi(env, path);
    if (cur.ok) { const {sha} = await cur.json(); await ghApi(env, path, {method: "DELETE", body: JSON.stringify({message: "🗑 gallery", sha, committer: {name: "GraphicWO Bot", email: "graphicwo@users.noreply.github.com"}})}); }
    await s.fetch("https://do/gal/del", {method: "POST", body: JSON.stringify({id: m[1]})});
    return json({ok: true}, 200, cors);
  }
  return json({error: "not_found"}, 404, cors);
}
