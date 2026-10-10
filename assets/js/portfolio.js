(() => {
  'use strict';
  const $ = (s, root = document) => root.querySelector(s);
  const $$ = (s, root = document) => [...root.querySelectorAll(s)];
  const menu = $('.menu-toggle');
  const nav = $('#main-nav');
  const closeMenu = () => { if (!menu) return; menu.setAttribute('aria-expanded', 'false'); menu.textContent = 'Menu +'; nav.classList.remove('is-open'); };
  menu?.addEventListener('click', () => {
    const open = menu.getAttribute('aria-expanded') !== 'true';
    menu.setAttribute('aria-expanded', String(open)); menu.textContent = open ? 'Close −' : 'Menu +'; nav.classList.toggle('is-open', open);
  });
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && menu?.getAttribute('aria-expanded') === 'true') {closeMenu(); menu.focus();} });
  document.addEventListener('click', e => {if (menu && !e.target.closest('.site-header')) closeMenu();});
  $$('#main-nav a').forEach(a => a.addEventListener('click', closeMenu));
  const desktop = matchMedia('(min-width:701px)'); desktop.addEventListener('change', () => closeMenu());

  const grid = $('#work-grid');
  if (grid) {
    const cards = $$('[data-category]', grid), search = $('#project-search');
    const buttons = $$('[data-filter]'); let category = 'All';
    function filter(updateURL = true) {
      const query = search.value.trim().toLowerCase(); let n = 0;
      cards.forEach(card => {const visible = (category === 'All' || card.dataset.category === category) && card.textContent.toLowerCase().includes(query); card.hidden = !visible; if (visible) n++;});
      buttons.forEach(b => b.setAttribute('aria-pressed', String(b.dataset.filter === category)));
      $('#result-count').textContent = `${n} ${n === 1 ? 'experience' : 'experiences'}`;
      $('#no-results').hidden = n !== 0;
      if (updateURL) {
        if (!matchMedia('(prefers-reduced-motion: reduce)').matches) grid.animate([{opacity:.45,transform:'translateY(5px)'},{opacity:1,transform:'translateY(0)'}], {duration:180,easing:'ease-out'});
        const u = new URL(location.href); category === 'All' ? u.searchParams.delete('category') : u.searchParams.set('category', category);
        query ? u.searchParams.set('q', search.value.trim()) : u.searchParams.delete('q');
        history.replaceState(null, '', u);
      }
    }
    function fromURL() {const u = new URL(location.href); const value = u.searchParams.get('category'); category = buttons.some(b => b.dataset.filter === value) ? value : 'All'; search.value = u.searchParams.get('q') || ''; filter(false);}
    buttons.forEach(b => b.addEventListener('click', () => {category = b.dataset.filter; filter();}));
    search.addEventListener('input', () => filter());
    $('#reset-filters').addEventListener('click', () => {category = 'All'; search.value = ''; filter(); search.focus();});
    window.addEventListener('popstate', fromURL); fromURL();
  }

  const toast = $('#toast'); let toastTimer;
  const announce = message => {toast.textContent = message; toast.classList.add('visible'); clearTimeout(toastTimer); toastTimer = setTimeout(() => toast.classList.remove('visible'), 2500);};
  $('.copy-email')?.addEventListener('click', async () => {
    try {await navigator.clipboard.writeText('wuzebang@westlake.edu.cn'); announce('Email address copied.');}
    catch {announce('wuzebang@westlake.edu.cn');}
  });
  $('.cv-print')?.addEventListener('click', () => window.print());

  const dialog = $('#image-viewer');
  let opener, openFrame, closeTimer;
  let closing = false;
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
  const finishClose = () => {
    clearTimeout(closeTimer);
    if (dialog?.open) dialog.close();
  };
  const closeViewer = () => {
    if (!dialog?.open || closing) return;
    closing = true;
    cancelAnimationFrame(openFrame);
    dialog.classList.remove('is-visible');
    if (reducedMotion.matches) finishClose();
    else closeTimer = setTimeout(finishClose, 260);
  };
  $$('[data-lightbox]').forEach(button => {
    // A separate footer communicates the action without covering or moving the image.
    if (!button.querySelector('.image-action')) {
      const hint = document.createElement('span');
      hint.className = 'image-action';
      hint.textContent = 'View full size ↗';
      hint.setAttribute('aria-hidden', 'true');
      button.append(hint);
    }
    button.addEventListener('click', () => {
      if (!dialog || dialog.open) return;
      opener = button;
      closing = false;
      clearTimeout(closeTimer);
      $('#viewer-image').src = button.dataset.lightbox;
      $('#viewer-image').alt = button.dataset.alt || '';
      $('#viewer-caption').textContent = button.dataset.caption || '';
      dialog.showModal();
      // Establish the start style before transitioning the dialog and backdrop together.
      dialog.getBoundingClientRect();
      if (reducedMotion.matches) dialog.classList.add('is-visible');
      else openFrame = requestAnimationFrame(() => dialog.classList.add('is-visible'));
    });
  });
  $('#close-viewer')?.addEventListener('click', closeViewer);
  dialog?.addEventListener('cancel', e => { e.preventDefault(); closeViewer(); });
  dialog?.addEventListener('click', e => {
    if (e.target !== dialog) return;
    const r = dialog.getBoundingClientRect();
    if (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom) closeViewer();
  });
  dialog?.addEventListener('transitionend', e => {
    if (closing && e.target === dialog && e.propertyName === 'opacity') finishClose();
  });
  dialog?.addEventListener('close', () => {
    clearTimeout(closeTimer);
    cancelAnimationFrame(openFrame);
    closing = false;
    dialog.classList.remove('is-visible');
    opener?.focus({preventScroll:true});
  });

  const sections = $$('.case-section');
  if (sections.length && 'IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      const visible = entries.filter(x => x.isIntersecting).sort((a,b) => a.boundingClientRect.top - b.boundingClientRect.top);
      if (!visible.length) return;
      $$('.case-nav a').forEach(a => { if (a.hash === `#${visible[0].target.id}`) a.setAttribute('aria-current', 'location'); else a.removeAttribute('aria-current'); });
    }, {rootMargin:'-110px 0px -55% 0px'}); sections.forEach(s => observer.observe(s));
  }
  let scheduled = false;
  const progress = () => {scheduled = false; const max = document.documentElement.scrollHeight - innerHeight; document.documentElement.style.setProperty('--read-progress', `${max > 0 ? Math.min(100, Math.max(0, scrollY / max * 100)) : 0}%`);};
  addEventListener('scroll', () => {if (!scheduled) {scheduled = true; requestAnimationFrame(progress);}}, {passive:true}); addEventListener('resize', progress); progress();
})();
