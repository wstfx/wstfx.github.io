(() => {
  const figure = document.querySelector('.navix-illustration');
  const button = figure?.querySelector('.navix-motion');
  if (!button) return;
  let paused = false;
  let visible = true;
  const update = () => figure.classList.toggle('is-paused', paused || !visible || document.hidden);
  button.hidden = false;
  button.addEventListener('click', () => {
    paused = !paused;
    button.textContent = paused ? 'Play animation' : 'Pause animation';
    button.setAttribute('aria-pressed', String(paused));
    update();
  });
  if ('IntersectionObserver' in window) new IntersectionObserver(entries => { visible = entries[0].isIntersecting; update(); }).observe(figure);
  document.addEventListener('visibilitychange', update);
})();
