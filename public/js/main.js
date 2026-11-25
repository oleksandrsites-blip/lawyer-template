/* Шаблон сайту адвоката · поведінка сторінки */
(() => {
  'use strict';

  /* ---------- Пам'ятки: картка ситуації або пункт бігучого рядка → dialog ---------- */
  const canDialog = typeof HTMLDialogElement === 'function';

  document.addEventListener('click', (ev) => {
    const trigger = ev.target.closest('[data-memo]');
    if (trigger && canDialog) {
      const memo = document.getElementById(trigger.dataset.memo);
      if (memo) {
        ev.preventDefault();
        memo.showModal();
      }
      return;
    }

    /* клік по затемненню поза вікном закриває пам'ятку */
    if (ev.target instanceof HTMLDialogElement && ev.target.open) {
      const r = ev.target.getBoundingClientRect();
      const inside = ev.clientX >= r.left && ev.clientX <= r.right && ev.clientY >= r.top && ev.clientY <= r.bottom;
      if (!inside) ev.target.close();
    }

    /* «Записатись з цією ситуацією» — закрити пам'ятку й передати ситуацію у форму */
    const cta = ev.target.closest('[data-situation]');
    if (cta) {
      try { sessionStorage.setItem('situation', cta.dataset.situation); } catch (_) { /* приватний режим */ }
      const dlg = cta.closest('dialog');
      if (dlg) dlg.close();
    }
  });

  /* ---------- Перемикач шрифтів (лише в демо) ---------- */
  const switcher = document.querySelector('.fontswitch:not([hidden])');
  if (switcher) {
    const root = document.documentElement;
    const buttons = [...switcher.querySelectorAll('button')];
    const mark = () => buttons.forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.font === root.dataset.font)));
    try {
      const saved = localStorage.getItem('font');
      if (saved) root.dataset.font = saved;
    } catch (_) { /* немає сховища */ }
    mark();
    switcher.addEventListener('click', (ev) => {
      const b = ev.target.closest('button');
      if (!b) return;
      root.dataset.font = b.dataset.font;
      try { localStorage.setItem('font', b.dataset.font); } catch (_) { /* немає сховища */ }
      mark();
    });
  }
})();
