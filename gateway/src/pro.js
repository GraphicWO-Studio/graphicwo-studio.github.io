// 🔥 PRO: GPT Image 2.5 عن طريق Pollo API الرسمي (مدفوع، رخيص) — بس للمسجّلين بـ GitHub، ومع سقف يومي
// المفتاح POLLO_KEY سرّ بالـ Worker، ما بيوصل للمتصفح أبداً.
const API = "https://pollo.ai/api/platform/v1/generation";
// low ≈ $0.006 للصورة، medium ≈ $0.0132 (دقة 1K)
export const PRO_MODELS = {"gpt-image-2.5": "low", "gpt-image-2.5-hd": "medium"};
export const PRO_LIMITS = {perUser: 15, perDay: 300};   // صور باليوم: لكل مستخدم / للكل
const RATIOS = ["1:1", "9:16", "16:9", "3:4", "4:3", "4:5", "5:4", "2:3", "3:2", "21:9", "9:21"];

const sleep = ms => new Promise(r => setTimeout(r, ms));

export async function runPro(env, form) {
  if (!env.POLLO_KEY) throw Object.assign(new Error("not_configured"), {status: 503});
  const head = {"x-api-key": env.POLLO_KEY, "Content-Type": "application/json"};
  const quality = PRO_MODELS[String(form.get("model"))] || "low";
  const ratio = RATIOS.includes(String(form.get("ratio"))) ? String(form.get("ratio")) : "1:1";
  const prompt = String(form.get("prompt") || "").slice(0, 4000).trim();
  if (prompt.length < 2) throw Object.assign(new Error("no_prompt"), {status: 400});
  const r = await fetch(API + "/openai/gpt-image-2-5/image", {method: "POST", headers: head,
    body: JSON.stringify({input: {prompt, aspectRatio: ratio, resolution: "1K", quality, mode: "flare"}})});
  const j = await r.json().catch(() => ({}));
  const task = j.taskId || (j.data && j.data.taskId);
  if (r.status === 402 || /credit|balance|insufficient/i.test(String(j.errorCode || j.message || ""))) throw Object.assign(new Error("pro_no_credit"), {status: 402});
  if (!r.ok || !task) throw Object.assign(new Error("pro_failed:" + (j.errorCode || r.status)), {status: 502});
  let url = null;
  for (let i = 0; i < 40 && !url; i++) {          // لحد ~2 دقيقة (حد الـ Worker 50 طلب)
    await sleep(i < 4 ? 1500 : 3000);
    const s = await (await fetch(API + "/" + task + "/status", {headers: head})).json().catch(() => null);
    const d = s && (s.data || s);
    const g = d && Array.isArray(d.generations) ? (d.generations.find(x => x.mediaType === "image") || d.generations[0]) : null;
    if (!g) continue;
    if (g.status === "failed") throw Object.assign(new Error("pro_failed:" + String(g.failMsg || "gen").slice(0, 60)), {status: 502});
    if (g.status === "succeed" && g.url) url = g.url;
  }
  if (!url) throw Object.assign(new Error("pro_timeout"), {status: 504});
  const img = await fetch(url);
  if (!img.ok) throw Object.assign(new Error("pro_fetch"), {status: 502});
  return {bytes: new Uint8Array(await img.arrayBuffer()), type: img.headers.get("content-type") || "image/png"};
}
