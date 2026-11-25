/* Шаблон сайту адвоката · поведінка сторінки */
(() => {
  'use strict';

  /* ---------- «З чим звертаються»: ситуація → пам'ятка ----------
     Телефон: акордеон (пам'ятка відкривається під ситуацією, можна закрити).
     Десктоп: список ліворуч, пам'ятка праворуч, одна завжди відкрита. */
  const sits = document.querySelector('.sits');
  if (sits) {
    const desktop = window.matchMedia('(min-width: 1024px)');
    const buttons = [...sits.querySelectorAll('.sit__btn')];
    const memoOf = (btn) => document.getElementById(btn.getAttribute('aria-controls'));

    const setOpen = (btn, open) => {
      btn.setAttribute('aria-expanded', String(open));
      memoOf(btn).classList.toggle('is-open', open);
    };

    /* десктоп: пам'ятка стає навпроти обраної ситуації, але не вилазить за межі списку */
    const placeMemo = (btn) => {
      const memo = memoOf(btn);
      if (!desktop.matches) { memo.style.top = ''; return; }
      const max = Math.max(0, sits.clientHeight - memo.offsetHeight);
      memo.style.top = Math.min(Math.max(0, btn.offsetTop - 24), max) + 'px';
    };
    const placeOpen = () => buttons.forEach((b) => b.getAttribute('aria-expanded') === 'true' && placeMemo(b));

    const fitHeight = () => {
      if (!desktop.matches) { sits.style.minHeight = ''; return; }
      const tallest = Math.max(...buttons.map((b) => memoOf(b).offsetHeight));
      sits.style.minHeight = tallest + 'px';
      placeOpen();
    };

    const ensureOneOpen = () => {
      if (desktop.matches && !buttons.some((b) => b.getAttribute('aria-expanded') === 'true')) {
        setOpen(buttons[0], true);
      }
      fitHeight();
    };

    buttons.forEach((btn) => {
      btn.addEventListener('click', () => {
        const isOpen = btn.getAttribute('aria-expanded') === 'true';
        if (desktop.matches) {
          if (isOpen) return;
          buttons.forEach((b) => setOpen(b, b === btn));
          placeMemo(btn);
        } else {
          buttons.forEach((b) => setOpen(b, b === btn ? !isOpen : false));
          if (!isOpen) {
            const top = btn.getBoundingClientRect().top;
            if (top < 70) btn.scrollIntoView({ block: 'start', behavior: 'smooth' });
          }
        }
      });
    });

    desktop.addEventListener('change', () => {
      if (!desktop.matches) buttons.forEach((b) => { setOpen(b, false); memoOf(b).style.top = ''; });
      ensureOneOpen();
    });
    window.addEventListener('resize', fitHeight, { passive: true });
    if (document.fonts) document.fonts.ready.then(fitHeight);
    ensureOneOpen();

    /* «Обговорити мою ситуацію» — запам'ятати ситуацію для форми контактів */
    sits.addEventListener('click', (ev) => {
      const link = ev.target.closest('[data-situation]');
      if (link) {
        try { sessionStorage.setItem('situation', link.dataset.situation); } catch (_) { /* приватний режим */ }
      }
    });
  }
})();
