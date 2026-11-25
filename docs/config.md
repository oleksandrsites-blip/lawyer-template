# Як зібрати сайт під ліда (20–30 хв)

1. Скопіюй `leads/demo.json` у `leads/<прізвище-латиницею>.json` і заповни поля (таблиця нижче).
2. Фото: `public/img/leads/<slug>-720.webp` і `-1200.webp` (портрет 2:3, ч/б), у config `"photo": "/img/leads/<slug>"`.
3. `python3 build.py <slug>` → `public/<slug>/index.html`.
4. Перевір на 375 і 1440, особливо довгі імена й назви практик.

`python3 build.py demo` збирає демо в `public/index.html`.

## Поля `leads/<slug>.json`

| Поле | Приклад | Примітка |
|---|---|---|
| `slug` | `ivanenko` | шлях на сайті `/ivanenko/` |
| `style` | `editorial` | `editorial` · пізніше `tysha`, `buro` |
| `concept_note` | `Концепт сайту для Ірини Іваненко` | тонка плашка зверху; `""` — прибрати |
| `noindex` | `true` | прототипи завжди `true` |
| `first_name`, `last_name` | `Олена`, `Коваль` | прізвище йде курсивом |
| `title` | `Адвокатка` / `Адвокат` | як людина називає себе сама |
| `city`, `city_in` | `Рівне`, `у Рівному` | `city_in` — для title і SEO |
| `practices` | `["military", "family"]` | id файлів з `practices/`, 2–4 штуки |
| `hero_line` | одне речення | **без** оцінок і гарантій (ст. 13) |
| `phone`, `telegram`, `viber` | | `telegram` — лише username |
| `address` | `вул. Соборна, 12, офіс 3` | |
| `since`, `certificate`, `council` | `2016`, `№ 123 від 2016 р.` | факти замість оцінок |
| `consult_price` | `від 600 грн` | |
| `photo`, `photo_alt` | `/img/leads/ivanenko` | без розширення |
| `placeholders` | `["phone", "since"]` | ці поля будуть підкреслені пунктиром як умовні |

## Бібліотека практик `practices/<id>.json`

`adj` (військові) · `label` (військові справи) · `group` (заголовок групи) · `situations[]`: `title`, `short`, `now[]` (що зробити зараз), `bring[]` (що взяти на консультацію).
Тексти вичитані за ст. 13: жодних обіцянок результату, лише загальні кроки. Нова практика = новий файл у тому самому форматі.

Розмітка — `template/index.html` (`{{ключ}}`), стилі — `public/css/style.css` (токени на початку файлу).
