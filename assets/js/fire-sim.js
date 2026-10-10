(() => {
  const figure = document.querySelector('.fire-illustration');
  if (!figure) return;
  const motion = figure.querySelector('.fire-motion');
  const thermal = figure.querySelector('.fire-thermal');
  figure.querySelector('.fire-art-controls').hidden = false;
  let paused = false;
  let visible = true;
  const update = () => figure.classList.toggle('is-paused', paused || !visible || document.hidden);
  motion.addEventListener('click', () => {
    paused = !paused;
    motion.setAttribute('aria-pressed', String(paused));
    motion.textContent = paused ? 'Play animation' : 'Pause animation';
    update();
  });
  thermal.addEventListener('click', () => {
    const active = figure.classList.toggle('is-thermal');
    thermal.setAttribute('aria-pressed', String(active));
    thermal.textContent = active ? 'Show the house' : 'Look inside';
  });
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(entries => { visible = entries[0].isIntersecting; update(); }).observe(figure);
  }
  document.addEventListener('visibilitychange', update);
})();
