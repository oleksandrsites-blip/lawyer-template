# Як зібрати сайт під ліда (20–30 хв)

1. **Фото:** `python3 tools/photo.py <slug> ~/Desktop/фото.jpg` — вирізає фон (macOS Vision), робить ч/б, кладе в `public/img/leads/<slug>/`. Найкраще — портрет до пояса на однотонному фоні.
2. **Дані:** скопіюй `leads/demo.json` у `leads/<slug>.json` і заповни поля (таблиця нижче).
3. **Збірка:** `python3 build.py <slug>` → `public/<slug>/index.html`.
4. Перевір на 375 і 1440: довгі імена, назви практик, де стоїть голова на фото.

`python3 build.py demo` збирає демо в `public/index.html`.

## Поля `leads/<slug>.json`

| Поле | Приклад | Примітка |
|---|---|---|
| `slug` | `ivanenko` | шлях на сайті `/ivanenko/` |
| `style` | `light` | палітра («Світло») |
| `font` | `mix` | `mix` · `lora` · `onest` — шрифт заголовків |
| `font_switcher` | `false` | перемикач шрифтів — лише для демо |
| `concept_note` | `Концепт сайту для Ірини Іваненко` | тонка плашка зверху; `""` — без неї |
| `noindex` | `true` | прототипи завжди `true` |
| `first_name`, `last_name` | `Олена`, `Коваль` | з них і монограма в лого |
| `title` | `Адвокатка` / `Адвокат` | як людина називає себе сама |
| `city`, `city_in` | `Рівне`, `у Рівному` | |
| `practices` | `["military", "family"]` | файли з `practices/`, 2–4 штуки |
| `headline_soft` | `від консультації до суду` | сірий рядок заголовка |
| `hero_line` | одне речення | **без** оцінок і гарантій (ст. 13) |
| `online` | `true` | «офлайн і онлайн» у чипі й картці |
| `phone`, `telegram`, `viber` | | `telegram` — лише username |
| `address`, `office_short` | `вул. Соборна, 12`, `на Соборній` | `office_short` — для скляної картки |
| `since`, `certificate`, `council` | `2016`, `№ 123 від 2016 р.` | факти замість оцінок |
| `price`, `duration` | `600 грн`, `45 хв` | цифри в першому екрані |
| `photo`, `photo_alt` | `/img/leads/ivanenko/cut` | без `-700.webp` |
| `placeholders` | `["phone", "since"]` | ці поля підкреслені пунктиром як умовні |

## Практики `practices/<id>.json`

`adj` (військові) · `label` · `group` · `tag` · `situations[]`: `id`, `icon` (doc, clock, money, family, alimony, house), `q` (як каже клієнт), `title`, `short`, `now[]`, `bring[]`.
Тексти вичитані за ст. 13: жодних обіцянок результату, лише загальні кроки. Нова практика — новий файл у тому самому форматі.
