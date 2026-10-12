(() => {
  'use strict';
  const figure = document.querySelector('.iv-illustration');
  const art = figure?.querySelector('.involve-art');
  const motion = figure?.querySelector('.iv-motion');
  if (art && motion) {
    const reduced = matchMedia('(prefers-reduced-motion: reduce)');
    let paused = false;
    let visible = !('IntersectionObserver' in window);
    const update = () => {
      motion.hidden = reduced.matches;
      figure.classList.toggle('is-paused', paused || !visible || document.hidden || reduced.matches);
    };
    motion.addEventListener('click', () => {
      paused = !paused;
      motion.textContent = paused ? 'Play animation' : 'Pause animation';
      motion.setAttribute('aria-pressed', String(paused));
      update();
    });
    reduced.addEventListener('change', update);
    document.addEventListener('visibilitychange', update);
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(entries => { visible = entries[0].isIntersecting; update(); }).observe(art);
    }
    update();
  }
  const gallery = document.querySelector('.iv-gallery');
  if (!gallery) return;
  const tabs = [...gallery.querySelectorAll('[role=tab]')];
  const panels = [...gallery.querySelectorAll('[role=tabpanel]')];
  const select = (index, focus = false) => {
    tabs.forEach((tab, i) => {
      tab.setAttribute('aria-selected', String(i === index));
      tab.tabIndex = i === index ? 0 : -1;
      panels[i].hidden = i !== index;
    });
    if (focus) tabs[index].focus();
  };
  tabs.forEach((tab, i) => {
    tab.addEventListener('click', () => select(i));
    tab.addEventListener('keydown', event => {
      let next;
      if (event.key === 'ArrowRight') next = (i + 1) % tabs.length;
      if (event.key === 'ArrowLeft') next = (i - 1 + tabs.length) % tabs.length;
      if (event.key === 'Home') next = 0;
      if (event.key === 'End') next = tabs.length - 1;
      if (next === undefined) return;
      event.preventDefault();
      select(next, true);
    });
  });
  gallery.querySelector('.iv-tabs').hidden = false;
  select(0);
})();
