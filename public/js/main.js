/* Шаблон сайту адвоката · поведінка сторінки */
(() => {
  'use strict';

  /* ---------- Закріплене меню: скляний фон, щойно сторінка почала скролитись ---------- */
  const topbar = document.querySelector('.topbar');
  if (topbar) {
    const onScroll = () => topbar.classList.toggle('is-scrolled', window.scrollY > 8);
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

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

  /* ---------- Форма заявки → /api/lead → Telegram ---------- */
  const form = document.querySelector('.form');
  if (form) {
    const chip = form.querySelector('.form__situation');
    const status = form.querySelector('.form__status');
    const submit = form.querySelector('.form__submit');
    const tgLink = document.querySelector('a[href^="https://t.me/"]');
    const read = () => { try { return sessionStorage.getItem('situation') || ''; } catch (_) { return ''; } };

    const showSituation = () => {
      const s = read();
      chip.hidden = !s;
      chip.querySelector('b').textContent = s;
    };
    chip.querySelector('button').addEventListener('click', () => {
      try { sessionStorage.removeItem('situation'); } catch (_) { /* немає сховища */ }
      showSituation();
    });
    document.addEventListener('click', (ev) => { if (ev.target.closest('[data-situation]')) setTimeout(showSituation, 0); });
    showSituation();

    const setError = (input, msg) => {
      input.setAttribute('aria-invalid', msg ? 'true' : 'false');
      input.closest('.field').querySelector('.field__error').textContent = msg;
    };
    const check = () => {
      const name = form.elements.name;
      const phone = form.elements.phone;
      const nameOk = /\p{L}{2}/u.test(name.value.trim());
      const phoneOk = phone.value.replace(/\D/g, '').length >= 10;
      setError(name, nameOk ? '' : 'Вкажіть, як до вас звертатися');
      setError(phone, phoneOk ? '' : 'Вкажіть номер повністю, щоб можна було передзвонити');
      if (!nameOk) name.focus(); else if (!phoneOk) phone.focus();
      return nameOk && phoneOk;
    };
    form.addEventListener('input', (ev) => { if (ev.target.getAttribute('aria-invalid') === 'true') setError(ev.target, ''); });

    form.addEventListener('submit', async (ev) => {
      ev.preventDefault();
      status.className = 'form__status';
      status.textContent = '';
      if (!check()) return;
      submit.disabled = true;
      submit.textContent = 'Надсилаю…';
      try {
        const res = await fetch(form.action, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name: form.elements.name.value,
            phone: form.elements.phone.value,
            company: form.elements.company.value,
            situation: read(),
            site: form.dataset.site,
            lawyer: form.dataset.lawyer,
          }),
        });
        if (!res.ok) throw new Error(String(res.status));
        form.reset();
        try { sessionStorage.removeItem('situation'); } catch (_) { /* немає сховища */ }
        showSituation();
        status.textContent = 'Дякую! Заявку отримано — зв\'яжуся з вами найближчим часом.';
      } catch (_) {
        status.classList.add('is-error');
        status.innerHTML = 'Не вдалося надіслати. Напишіть, будь ласка, напряму в <a target="_blank" rel="noopener"></a> або зателефонуйте.';
        const a = status.querySelector('a');
        a.textContent = 'Telegram';
        a.href = tgLink ? tgLink.href : '#contact';
      } finally {
        submit.disabled = false;
        submit.textContent = 'Надіслати заявку';
      }
    });
  }

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
