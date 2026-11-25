// Cloudflare Pages Function: POST /api/lead → заявка в Telegram.
// Змінні в Cloudflare Pages (Settings → Variables and secrets → Production):
//   TELEGRAM_BOT_TOKEN — токен бота від @BotFather (Secret)
//   TELEGRAM_CHAT_ID   — chat id за замовчуванням (для прототипів — Олександр), можна кілька через кому
//   LEAD_CHATS         — необов'язково: JSON {"ivanenko": "123456"} — куди слати заявки конкретного сайту

const clean = (v, max) => String(v ?? '').replace(/[<>]/g, '').trim().slice(0, max);

export async function onRequestPost({ request, env }) {
  let data;
  try { data = await request.json(); } catch { return json({ ok: false }, 400); }

  if (data.company) return json({ ok: true }); // honeypot: боти заповнюють приховане поле

  const name = clean(data.name, 60);
  const phone = clean(data.phone, 20);
  const situation = clean(data.situation, 160);
  const site = clean(data.site, 40).replace(/[^a-z0-9-]/gi, '');
  const lawyer = clean(data.lawyer, 80);
  if (!/\p{L}{2}/u.test(name) || phone.replace(/\D/g, '').length < 10) return json({ ok: false }, 422);

  const token = env.TELEGRAM_BOT_TOKEN;
  let chats = {};
  try { chats = JSON.parse(env.LEAD_CHATS || '{}'); } catch { /* порожньо */ }
  const chatIds = String(chats[site] || env.TELEGRAM_CHAT_ID || '').split(',').map((s) => s.trim()).filter(Boolean);
  if (!token || !chatIds.length) return json({ ok: false, error: 'not configured' }, 500);

  const text = [
    `🔔 Нова заявка з сайту${lawyer ? ` — ${lawyer}` : ''}`, '',
    `Ім'я: ${name}`,
    `Телефон: ${phone}`,
    situation && `Ситуація: ${situation}`,
    site && `Сторінка: /${site === 'demo' ? '' : site}`,
  ].filter(Boolean).join('\n');

  const results = await Promise.all(chatIds.map((chat_id) =>
    fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chat_id, text }),
    })
  ));
  const ok = results.some((r) => r.ok);
  return json({ ok }, ok ? 200 : 502);
}

const json = (body, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });
