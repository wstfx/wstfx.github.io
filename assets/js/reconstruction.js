(() => {
  const figure = document.querySelector('.sensor-illustration');
  const button = figure?.querySelector('.sensor-motion');
  if (!figure || !button) return;
  let paused = false;
  let visible = true;
  const update = () => figure.classList.toggle('is-paused', paused || !visible || document.hidden);
  button.addEventListener('click', () => {
    paused = !paused;
    button.setAttribute('aria-pressed', String(paused));
    button.textContent = paused ? 'Play animation' : 'Pause animation';
    update();
  });
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(entries => { visible = entries[0].isIntersecting; update(); }).observe(figure);
  }
  document.addEventListener('visibilitychange', update);
})();
