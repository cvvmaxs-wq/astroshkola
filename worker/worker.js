// Cloudflare Worker: створює рахунок monobank (Plata by mono) для лендінгу.
// Секрет MONO_TOKEN задається через `wrangler secret put MONO_TOKEN`, у код не потрапляє.
// POST /invoice  { parent, email, telegram, child, date, time, place }  ->  { pageUrl, invoiceId }

const AMOUNT = 79000;                 // 790.00 грн у копійках
const PRODUCT = "Персональна натальна карта дитини (PDF)";
const SITE = "https://cvvmaxs-wq.github.io/astroshkola";
const ALLOWED_ORIGINS = ["https://cvvmaxs-wq.github.io", "http://127.0.0.1:8765", "http://localhost:8765"];

function cors(origin) {
  const ok = ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0];
  return {
    "Access-Control-Allow-Origin": ok,
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Vary": "Origin",
  };
}
const json = (data, status, origin) =>
  new Response(JSON.stringify(data), { status, headers: { "Content-Type": "application/json; charset=utf-8", ...cors(origin) } });

const clean = (v, max) => String(v || "").replace(/\s+/g, " ").trim().slice(0, max);

export default {
  async fetch(request, env) {
    const origin = request.headers.get("Origin") || "";
    const url = new URL(request.url);

    if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: cors(origin) });
    if (request.method === "GET" && url.pathname === "/") return json({ ok: true, service: "astroshkola-pay" }, 200, origin);
    if (request.method !== "POST" || url.pathname !== "/invoice") return json({ error: "not found" }, 404, origin);
    if (!env.MONO_TOKEN) return json({ error: "MONO_TOKEN not configured" }, 500, origin);

    let body;
    try { body = await request.json(); } catch { return json({ error: "bad json" }, 400, origin); }

    const parent = clean(body.parent, 80), email = clean(body.email, 120), child = clean(body.child, 60);
    const date = clean(body.date, 10), time = clean(body.time, 5), place = clean(body.place, 80), tg = clean(body.telegram, 40);
    if (!email || !child || !date) return json({ error: "missing fields" }, 400, origin);

    // Що побачить замовниця у виписці mono — щоб зіставити оплату із заявкою з пошти
    const reference = "astro-" + Date.now().toString(36);
    const comment = clean(`Карта дитини: ${child}, ${date} ${time}, ${place} · ${parent} ${email}${tg ? " " + tg : ""}`, 250);

    const payload = {
      amount: AMOUNT,
      ccy: 980,
      paymentType: "debit",
      validity: 3600 * 24 * 3,        // рахунок дійсний 3 дні
      redirectUrl: `${SITE}/thank-you.html`,
      merchantPaymInfo: {
        reference,
        destination: PRODUCT,
        comment,
        customerEmails: [email],
        basketOrder: [{ name: PRODUCT, qty: 1, sum: AMOUNT, total: AMOUNT, unit: "шт.", code: "astro-card-pdf" }],
      },
    };

    const r = await fetch("https://api.monobank.ua/api/merchant/invoice/create", {
      method: "POST",
      headers: { "X-Token": env.MONO_TOKEN, "Content-Type": "application/json", "X-Cms": "astroshkola", "X-Cms-Version": "1.0" },
      body: JSON.stringify(payload),
    });
    const data = await r.json().catch(() => ({}));
    if (!r.ok || !data.pageUrl) return json({ error: "mono", detail: data.errText || data.errCode || r.status }, 502, origin);
    return json({ pageUrl: data.pageUrl, invoiceId: data.invoiceId }, 200, origin);
  },
};
