(() => {
  const figure = document.querySelector('.ig-illustration');
  if (!figure) return;
  let paused = false;
  let visible = true;
  const motion = figure.querySelector('.ig-motion');
  const updateMotion = () => figure.classList.toggle('is-paused', paused || !visible || document.hidden);
  motion.hidden = false;
  motion.addEventListener('click', () => {
    paused = !paused;
    motion.setAttribute('aria-pressed', String(paused));
    motion.textContent = paused ? 'Play animation' : 'Pause animation';
    updateMotion();
  });
  if ('IntersectionObserver' in window) new IntersectionObserver(entries => { visible = entries[0].isIntersecting; updateMotion(); }).observe(figure);
  document.addEventListener('visibilitychange', updateMotion);
  updateMotion();

  const tabs = [...document.querySelectorAll('[data-ig-tab]')];
  const activate = tab => {
    tabs.forEach(item => {
      const active = item === tab;
      item.setAttribute('aria-selected', String(active));
      item.tabIndex = active ? 0 : -1;
      document.getElementById(item.getAttribute('aria-controls')).hidden = !active;
    });
  };
  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => activate(tab));
    tab.addEventListener('keydown', event => {
      let next;
      if (event.key === 'ArrowRight') next = (index + 1) % tabs.length;
      if (event.key === 'ArrowLeft') next = (index + tabs.length - 1) % tabs.length;
      if (event.key === 'Home') next = 0;
      if (event.key === 'End') next = tabs.length - 1;
      if (next === undefined) return;
      event.preventDefault();
      tabs[next].focus();
      activate(tabs[next]);
    });
  });
  if (tabs.length) activate(tabs[0]);
})();
