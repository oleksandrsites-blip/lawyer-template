#!/usr/bin/env python3
"""Збирає сторінку адвоката з config.

    python3 build.py demo        -> public/index.html
    python3 build.py ivanenko    -> public/ivanenko/index.html

Дані ліда: leads/<slug>.json · практики: practices/<id>.json · розмітка: template/index.html
Лише стандартна бібліотека Python, нічого ставити не треба.
"""
import html
import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent
BASE_URL = "https://advokat-site.pages.dev"  # TODO: замінити на справжній домен проєкту
TEMPLATE_VERSION = str(int(time.time()))  # скидає кеш CSS/JS після кожної збірки


def e(value):
    return html.escape(str(value), quote=True)


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


def render_situations(practices):
    out = []
    for p in practices:
        out.append(f'<p class="sits__group">{e(p["group"])}</p>')
        for s in p["situations"]:
            sid = f'sit-{s["id"]}'
            now = "".join(f"<li>{e(x)}</li>" for x in s["now"])
            bring = "".join(f"<li>{e(x)}</li>" for x in s["bring"])
            out.append(f'''<div class="sit">
  <button class="sit__btn" type="button" aria-expanded="false" aria-controls="{sid}">
    <span class="sit__title">{e(s["title"])}</span>
    <span class="sit__short">{e(s["short"])}</span>
    <span class="sit__icon" aria-hidden="true"></span>
  </button>
  <div class="memo" id="{sid}" role="region" aria-label="{e(s["title"])}">
    <p class="memo__kicker">Пам'ятка · {e(p["label"])}</p>
    <h3 class="memo__title">{e(s["title"])}</h3>
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
    <p class="memo__note">Це загальні кроки. Що робити саме у вашій ситуації, скажу на консультації.
      <a class="memo__link" href="#contact" data-situation="{e(s["title"])}">Обговорити мою ситуацію <span aria-hidden="true">→</span></a></p>
  </div>
</div>''')
    return "\n".join(out)


def build(slug):
    cfg = load_json(ROOT / "leads" / f"{slug}.json")
    practices = [load_json(ROOT / "practices" / f"{pid}.json") for pid in cfg["practices"]]

    name = f'{cfg["first_name"]} {cfg["last_name"]}'
    if all(p.get("adj") for p in practices):  # «військові та сімейні справи»
        practice_line = join_uk(p["adj"] for p in practices) + " справи"
    else:
        practice_line = join_uk(p["label"] for p in practices)
    phone_raw = cfg.get("phone", "")
    tel = "+" + re.sub(r"\D", "", phone_raw)
    url = BASE_URL + ("/" if slug == "demo" else f"/{slug}/")
    description = f'{name} — {cfg["title"].lower()} {cfg["city_in"]}. {practice_line.capitalize()}. Консультація {cfg.get("consult_price", "")}.'

    schema = {
        "@context": "https://schema.org",
        "@type": "Attorney",
        "name": name,
        "url": url,
        "telephone": tel,
        "image": BASE_URL + cfg["photo"] + "-1200.webp",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": cfg.get("address", ""),
            "addressLocality": cfg["city"],
            "addressCountry": "UA",
        },
        "areaServed": cfg["city"],
        "knowsAbout": [p["label"] for p in practices],
    }

    ctx = {
        "style": e(cfg.get("style", "editorial")),
        "robots": "noindex, nofollow" if cfg.get("noindex", True) else "index, follow",
        "page_title": e(f'{name} — {cfg["title"].lower()} {cfg["city_in"]} · {practice_line}'),
        "description": e(description),
        "url": e(url),
        "og_image": e(BASE_URL + cfg["photo"] + "-1200.webp"),
        "schema": json.dumps(schema, ensure_ascii=False),
        "concept_note": e(cfg.get("concept_note", "")),
        "concept_hidden": "" if cfg.get("concept_note") else " hidden",
        "first_name": e(cfg["first_name"]),
        "last_name": e(cfg["last_name"]),
        "name": e(name),
        "title": e(cfg["title"]),
        "title_lower": e(cfg["title"].lower()),
        "city": e(cfg["city"]),
        "city_in": e(cfg["city_in"]),
        "practice_line": e(practice_line.capitalize()),
        "hero_line": e(cfg["hero_line"]),
        "phone": field(cfg, "phone"),
        "tel": e(tel),
        "telegram_url": e(f'https://t.me/{cfg["telegram"]}'),
        "address": field(cfg, "address"),
        "since": field(cfg, "since"),
        "certificate": field(cfg, "certificate"),
        "council": field(cfg, "council"),
        "consult_price": field(cfg, "consult_price"),
        "photo": e(cfg["photo"]),
        "photo_alt": e(cfg["photo_alt"]),
        "situations": render_situations(practices),
        "version": TEMPLATE_VERSION,
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
