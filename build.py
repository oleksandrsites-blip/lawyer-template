#!/usr/bin/env python3
"""Збирає сторінку адвоката з config.

    python3 build.py demo        -> public/index.html
    python3 build.py ivanenko    -> public/ivanenko/index.html

Дані ліда: leads/<slug>.json · практики: practices/<id>.json · розмітка: template/index.html
Фото ліда: python3 tools/photo.py <slug> <шлях-до-фото>  (вирізає фон, робить ч/б)
Лише стандартна бібліотека Python, нічого ставити не треба.
"""
import html
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).parent
BASE_URL = "https://advokat-site.pages.dev"  # проєкт Cloudflare Pages (з репозиторію lawyer-template)
VERSION = str(int(time.time()))  # скидає кеш CSS/JS після кожної збірки

# Іконки ситуацій (stroke, 24×24). Ключ — поле "icon" у practices/*.json
ICONS = {
    "doc": '<rect x="4" y="3" width="16" height="18" rx="2"/><path d="M8 8h8M8 12h8M8 16h5"/>',
    "clock": '<circle cx="12" cy="12" r="8"/><path d="M12 8v4l3 2"/>',
    "money": '<rect x="3" y="6" width="18" height="12" rx="2"/><circle cx="12" cy="12" r="2.5"/>',
    "family": '<circle cx="8" cy="8" r="3"/><circle cx="16" cy="8" r="3"/><path d="M3 20c0-3 2.5-5 5-5s5 2 5 5M11 20c0-3 2.5-5 5-5s5 2 5 5"/>',
    "alimony": '<path d="M12 3v18M7 7h7a3 3 0 0 1 0 6H9a3 3 0 0 0 0 6h8"/>',
    "house": '<path d="M3 11 12 4l9 7v9H3z"/><path d="M12 20v-6"/>',
}


def e(value):
    return html.escape(str(value), quote=True)


def icon(name):
    return f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true">{ICONS.get(name, ICONS["doc"])}</svg>'


def join_uk(items):
    """['a', 'b', 'c'] -> 'a, b та c'"""
    items = list(items)
    if len(items) <= 1:
        return "".join(items)
    return ", ".join(items[:-1]) + " та " + items[-1]


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def field(cfg, key):
    """Значення для показу; поля з `placeholders` позначаються візуально."""
    value = e(cfg.get(key, ""))
    if key in cfg.get("placeholders", []):
        return f'<span class="ph" title="Умовні дані — замінити">{value}</span>'
    return value


FONTS = {
    "onest": "https://fonts.googleapis.com/css2?family=Onest:wght@400;500;600&display=swap",
    "lora": "https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,500;0,600;1,500&family=Onest:wght@400;500;600&display=swap",
    "mix": "https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,500;0,600;1,500&family=Onest:wght@400;500;600&display=swap",
}


def hero_visual(cfg, initials):
    """Вирізаний портрет або — якщо фото нема — велика монограма."""
    if cfg.get("photo"):
        p = e(cfg["photo"])
        return f'''          <div class="hero__person">
            <img src="{p}-1100.webp" srcset="{p}-700.webp 700w, {p}-1100.webp 1100w" sizes="(min-width: 1024px) 470px, 92vw" width="1100" height="1728" alt="{e(cfg.get("photo_alt", ""))}" fetchpriority="high">
          </div>'''
    return f'          <div class="hero__mono" aria-hidden="true"><span>{e(initials)}</span></div>'


def about_visual(cfg, initials):
    p = cfg.get("photo_about") or cfg.get("photo")
    if p:
        p = e(p)
        return f'<img src="{p}-1100.webp" srcset="{p}-700.webp 700w, {p}-1100.webp 1100w" sizes="(min-width: 1024px) 40vw, 92vw" width="1100" height="1728" alt="{e(cfg.get("photo_alt", ""))}" loading="lazy">'
    return f'<span class="about__mono" aria-hidden="true">{e(initials)}</span>'


def favicon(initials):
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="16" fill="#121214"/>'
           f'<text x="32" y="42" font-family="Arial,sans-serif" font-size="26" font-weight="700" fill="#fff" text-anchor="middle">{initials}</text></svg>')
    return "data:image/svg+xml," + quote(svg)


def make_og(slug, cfg, name, practice_line):
    """Картинка 1200×630 для прев'ю посилання в Telegram/Viber. Потрібен Pillow; без нього — фото."""
    rel = "/img/og.jpg" if slug == "demo" else f"/img/leads/{slug}/og.jpg"
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return (cfg.get("photo") or "") + "-1100.webp"
    W, H = 1200, 630
    img = Image.new("RGB", (W, H), (242, 242, 243))
    grad = Image.linear_gradient("L").rotate(90).resize((W, H))
    img = Image.composite(Image.new("RGB", (W, H), (215, 217, 223)), img, grad)
    d = ImageDraw.Draw(img)

    def font(size, bold=False):
        for path in ("/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
                     "/Library/Fonts/Arial Unicode.ttf"):
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
        return ImageFont.load_default()

    photo = cfg.get("photo")
    src = ROOT / "public" / (photo.lstrip("/") + "-700.webp") if photo else None
    if src and src.exists():
        p = Image.open(src).convert("RGBA")
        h = 600
        p = p.resize((round(p.width * h / p.height), h), Image.LANCZOS)
        img.paste(p, (W - p.width - 70, H - h), p)
    else:
        d.text((W - 300, H / 2), cfg["first_name"][0] + cfg["last_name"][0], font=font(260, True), fill=(205, 207, 213), anchor="mm")

    chip = f'{cfg["title"]} · {cfg["city"]}'
    d.rounded_rectangle((70, 70, 70 + 44 + d.textlength(chip, font=font(22)), 70 + 44), 22, fill=(255, 255, 255))
    d.text((92, 92), chip, font=font(22), fill=(69, 70, 76), anchor="lm")
    d.text((70, 170), name, font=font(68, True), fill=(18, 18, 20))
    y = 270
    words, line = practice_line.capitalize().split(), ""
    for w in words:  # перенос рядка в межах 640px
        test = (line + " " + w).strip()
        if d.textlength(test, font=font(44)) > 640:
            d.text((70, y), line, font=font(44), fill=(154, 155, 161)); y += 56; line = w
        else:
            line = test
    d.text((70, y), line, font=font(44), fill=(154, 155, 161))
    d.text((70, H - 90), f'Консультація {cfg.get("price", "")}', font=font(26), fill=(69, 70, 76))

    out = ROOT / "public" / rel.lstrip("/")
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, "JPEG", quality=86, optimize=True)
    return rel


def situations(practices):
    return [(p, s) for p in practices for s in p["situations"]]


def render_ticker(items):
    one = "".join(
        f'<a href="#s-{e(s["id"])}" data-memo="memo-{e(s["id"])}">{icon(s["icon"])}{e(s["q"])}</a>'
        for _, s in items
    )
    # другий прохід — для безшовної прокрутки, від скрінрідерів і Tab схований
    dup = one.replace("<a ", '<a tabindex="-1" ')
    return f'<div class="ticker__row"><span class="ticker__set">{one}</span><span class="ticker__set" aria-hidden="true">{dup}</span></div>'


def render_cards(items):
    out = []
    for p, s in items:
        out.append(f'''<li class="sit" id="s-{e(s["id"])}">
  <button class="sit__btn" type="button" data-memo="memo-{e(s["id"])}" aria-haspopup="dialog">
    <span class="sit__top"><span class="sit__icon">{icon(s["icon"])}</span><span class="sit__tag">{e(p["tag"])}</span></span>
    <span class="sit__title">{e(s["q"])}</span>
    <span class="sit__short">{e(s["short"])}</span>
    <span class="sit__more">Перші кроки <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M3 8h10M9 4l4 4-4 4"/></svg></span>
  </button>
</li>''')
    return "\n".join(out)


def render_memos(cfg, items):
    if cfg.get("photo"):
        avatar = f'<span class="memo__avatar"><img src="{e(cfg["photo"])}-700.webp" width="700" height="1099" alt="" loading="lazy"></span>'
    else:
        avatar = f'<span class="memo__avatar memo__avatar--mono">{e(cfg["first_name"][0] + cfg["last_name"][0])}</span>'
    out = []
    for p, s in items:
        now = "".join(f"<li>{e(x)}</li>" for x in s["now"])
        bring = "".join(f"<li>{e(x)}</li>" for x in s["bring"])
        out.append(f'''<dialog class="memo" id="memo-{e(s["id"])}" aria-labelledby="memo-{e(s["id"])}-t">
  <form method="dialog"><button class="memo__close" aria-label="Закрити">×</button></form>
  <p class="memo__kicker">Пам'ятка · {e(p["label"])}</p>
  <h3 class="memo__title" id="memo-{e(s["id"])}-t">{e(s["title"])}</h3>
  <div class="memo__cols">
    <div>
      <h4 class="memo__h">Що зробити зараз</h4>
      <ol class="memo__steps">{now}</ol>
    </div>
    <div>
      <h4 class="memo__h">Що взяти на консультацію</h4>
      <ul class="memo__bring">{bring}</ul>
    </div>
  </div>
  <div class="memo__foot">
    {avatar}
    <p class="memo__note">Це загальні кроки. Що робити саме у вашому випадку, скажу на консультації.</p>
    <a class="btn btn--dark memo__cta" href="#contact" data-situation="{e(s["title"])}">Записатись з цією ситуацією</a>
  </div>
</dialog>''')
    return "\n".join(out)


def render_prices(cfg):
    ph = "prices" in cfg.get("placeholders", [])
    out = []
    for p in cfg.get("prices", []):
        price = e(p["price"])
        if ph:
            price = f'<span class="ph" title="Умовні дані — замінити">{price}</span>'
        main = p.get("main")
        cta = '<a class="btn btn--light" href="#contact">Записатись <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M4 12 12 4M5.5 4H12v6.5"/></svg></a>' if main else ""
        out.append(f'''<li class="price{' price--main' if main else ''}">
  <p class="price__name">{e(p["name"])}</p>
  <p class="price__value">{price}</p>
  <p class="price__note">{e(p["note"])}</p>
  {cta}
</li>''')
    return "\n".join(out)


def render_about(cfg):
    paras = "".join(f"<p>{e(x)}</p>" for x in cfg.get("about", []))
    if cfg.get("about_example"):
        paras += '<p class="about__example">Приклад тексту — замінимо вашою історією.</p>'
    return paras


def render_faq(cfg):
    """Типові питання. Можна перевизначити списком "faq": [{"q": ..., "a": ...}] у config."""
    price = cfg.get("price", "")
    duration = cfg.get("duration", "")
    online = cfg.get("online")
    default = [
        {"q": "Скільки коштує консультація?",
         "a": f"{price}, {duration}. Якщо після консультації ви вирішите продовжити, ціну подальшої роботи фіксуємо в договорі ще до її початку."},
        {"q": "Чи можна проконсультуватися онлайн?",
         "a": "Так, у Telegram, Viber чи за відеозв'язком. Документи надсилаєте заздалегідь фото або сканами."} if online else None,
        {"q": "Що взяти на консультацію?",
         "a": "Усе, що стосується ситуації: повістки, рішення, договори, листування. Якщо не впевнені, що знадобиться, беріть усе — розберемося разом."},
        {"q": "Ви можете сказати, чим закінчиться справа?",
         "a": "Гарантувати результат не може жоден адвокат, і правила адвокатської етики цього не дозволяють. Я чесно скажу, які є варіанти, ризики і що від них залежить."},
        {"q": "Чи дізнається хтось про моє звернення?",
         "a": "Ні. Усе, що ви розповідаєте, — адвокатська таємниця. Це вимога закону."},
        {"q": f"Ви працюєте лише {cfg['city_in']}?",
         "a": f"Офіс — {cfg['city_in']}." + (" Онлайн-консультації можливі з будь-якого міста." if online else "")},
    ]
    items = [x for x in (cfg.get("faq") or default) if x]
    return "\n".join(
        f'<details class="qa"><summary>{e(x["q"])}<span class="qa__icon" aria-hidden="true"></span></summary><p>{e(x["a"])}</p></details>'
        for x in items
    )


def build(slug):
    cfg = load_json(ROOT / "leads" / f"{slug}.json")
    practices = [load_json(ROOT / "practices" / f"{pid}.json") for pid in cfg["practices"]]
    skip = set(cfg.get("skip_situations", []))
    items = [(p, s) for p, s in situations(practices) if s["id"] not in skip]

    name = f'{cfg["first_name"]} {cfg["last_name"]}'
    initials = cfg["first_name"][0] + cfg["last_name"][0]
    if all(p.get("adj") for p in practices):  # «військові та сімейні справи»
        practice_line = join_uk(p["adj"] for p in practices) + " справи"
    else:
        practice_line = join_uk(p["label"] for p in practices)
    tel = "+" + re.sub(r"\D", "", cfg.get("phone", ""))
    url = BASE_URL + ("/" if slug == "demo" else f"/{slug}/")
    description = f'{name} — {cfg["title"].lower()} {cfg["city_in"]}. {practice_line.capitalize()}. Консультація {cfg.get("price", "")}.'

    schema = {
        "@context": "https://schema.org",
        "@type": "Attorney",
        "name": name,
        "url": url,
        "telephone": tel,
        "address": {
            "@type": "PostalAddress",
            "streetAddress": cfg.get("address", ""),
            "addressLocality": cfg["city"],
            "addressCountry": "UA",
        },
        "areaServed": cfg["city"],
        "knowsAbout": [p["label"] for p in practices],
    }

    photo = cfg.get("photo")
    if photo:
        schema["image"] = BASE_URL + photo + "-1100.webp"
    og_image = BASE_URL + make_og(slug, cfg, name, practice_line)

    ctx = {
        "style": e(cfg.get("style", "light")),
        "font": e(cfg.get("font", "mix")),
        "robots": "noindex, nofollow" if cfg.get("noindex", True) else "index, follow",
        "page_title": e(f'{name} — {cfg["title"].lower()} {cfg["city_in"]} · {practice_line}'),
        "description": e(description),
        "url": e(url),
        "og_image": e(og_image),
        "schema": json.dumps(schema, ensure_ascii=False),
        "concept_note": e(cfg.get("concept_note", "")),
        "concept_hidden": "" if cfg.get("concept_note") else " hidden",
        "switcher_hidden": "" if cfg.get("font_switcher") else " hidden",
        "initials": e(initials),
        "first_name": e(cfg["first_name"]),
        "name": e(name),
        "title": e(cfg["title"]),
        "title_lower": e(cfg["title"].lower()),
        "city": e(cfg["city"]),
        "city_in": e(cfg["city_in"]),
        "online_chip": "· офлайн і онлайн" if cfg.get("online") else "",
        "online_text": " або онлайн" if cfg.get("online") else "",
        "practice_line": e(cfg.get("headline") or practice_line.capitalize()),
        "headline_soft": e(cfg.get("headline_soft", "від консультації до суду")),
        "hero_line": e(cfg["hero_line"]),
        "phone": field(cfg, "phone"),
        "tel": e(tel),
        "telegram_url": e(f'https://t.me/{cfg["telegram"]}'),
        "address": field(cfg, "address"),
        "office_short": e(cfg.get("office_short", "")),
        "since": field(cfg, "since"),
        "certificate": field(cfg, "certificate"),
        "council": field(cfg, "council"),
        "price": field(cfg, "price"),
        "duration": field(cfg, "duration"),
        "hero_visual": hero_visual(cfg, initials),
        "about_visual": about_visual(cfg, initials),
        "about_mod": "" if photo else " about__photo--mono",
        "preload": (f'  <link rel="preload" as="image" href="{e(photo)}-1100.webp" imagesrcset="{e(photo)}-700.webp 700w, {e(photo)}-1100.webp 1100w" imagesizes="(min-width: 1024px) 470px, 92vw">\n' if photo else ""),
        "favicon": favicon(initials),
        "fonts_url": FONTS.get(cfg.get("font", "onest"), FONTS["onest"]),
        "ticker": render_ticker(items),
        "cards": render_cards(items),
        "memos": render_memos(cfg, items),
        "about": render_about(cfg),
        "education": field(cfg, "education"),
        "prices": render_prices(cfg),
        "faq": render_faq(cfg),
        "hours": field(cfg, "hours"),
        "maps_url": e(cfg.get("maps_url") or "https://www.google.com/maps/search/?api=1&query=" + quote(cfg.get("address", "") + ", " + cfg["city"])),
        "slug": e(slug),
        "viber_url": e("viber://chat?number=" + re.sub(r"\D", "", cfg.get("viber", ""))) if cfg.get("viber") else "",
        "viber_hidden": "" if cfg.get("viber") else " hidden",
        "year": time.strftime("%Y"),
        "version": VERSION,
    }

    tpl = (ROOT / "template" / "index.html").read_text(encoding="utf-8")
    missing = set()

    def sub(m):
        key = m.group(1)
        if key not in ctx:
            missing.add(key)
            return m.group(0)
        return str(ctx[key])

    page = re.sub(r"\{\{\s*(\w+)\s*\}\}", sub, tpl)
    if missing:
        sys.exit(f"У шаблоні є невідомі ключі: {', '.join(sorted(missing))}")

    out = ROOT / "public" / ("index.html" if slug == "demo" else f"{slug}/index.html")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    print(f"✓ {out.relative_to(ROOT)}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Використання: python3 build.py <slug>   (дані в leads/<slug>.json)")
    build(sys.argv[1])
