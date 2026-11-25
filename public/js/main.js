/* Шаблон сайту адвоката · поведінка сторінки */
(() => {
  'use strict';

  /* ---------- «Що у вас сталося?» ----------
     Телефон: пам'ятка відкривається під ситуацією (акордеон).
     Десктоп: пам'ятки переносяться в праву панель і стають на місце портрета.
     Без JS усі пам'ятки просто видно під ситуаціями. */
  const list = document.querySelector('.qs');
  const panel = document.querySelector('.panel');
  if (list && panel) {
    const desktop = window.matchMedia('(min-width: 1024px)');
    const buttons = [...list.querySelectorAll('.q__btn')];
    const memoOf = (btn) => document.getElementById(btn.getAttribute('aria-controls'));

    const place = () => {
      buttons.forEach((btn) => {
        const memo = memoOf(btn);
        if (desktop.matches) panel.appendChild(memo);
        else btn.after(memo);
      });
    };

    const select = (target) => {
      buttons.forEach((btn) => {
        const open = btn === target;
        btn.setAttribute('aria-expanded', String(open));
        memoOf(btn).classList.toggle('is-open', open);
      });
      panel.classList.toggle('has-memo', Boolean(target));
    };

    buttons.forEach((btn) => {
      btn.addEventListener('click', () => {
        const wasOpen = btn.getAttribute('aria-expanded') === 'true';
        select(wasOpen ? null : btn);
        if (!wasOpen && !desktop.matches && btn.getBoundingClientRect().top < 72) {
          btn.scrollIntoView({ block: 'start', behavior: 'smooth' });
        }
      });
    });

    desktop.addEventListener('change', place);
    place();

    /* «Записатись з цією ситуацією» — передати ситуацію у форму контактів */
    document.addEventListener('click', (ev) => {
      const link = ev.target.closest('[data-situation]');
      if (!link) return;
      try { sessionStorage.setItem('situation', link.dataset.situation); } catch (_) { /* приватний режим */ }
    });
  }
})();
