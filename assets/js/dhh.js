(() => {
  'use strict';
  // Work uses reversible CSS reveal. Only the case study has ambient floating motion.
  const figure = document.querySelector('.dhh-illustration');
  const stage = figure?.querySelector('.dhh-stage');
  const button = figure?.querySelector('.dhh-motion');
  if (!stage || !button) return;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  let paused = false;
  let visible = !('IntersectionObserver' in window);
  const update = () => {
    button.hidden = reduced.matches;
    figure.classList.toggle('is-paused', paused || !visible || document.hidden || reduced.matches);
  };
  button.addEventListener('click', () => {
    paused = !paused;
    button.textContent = paused ? 'Play animation' : 'Pause animation';
    button.setAttribute('aria-pressed', String(paused));
    update();
  });
  reduced.addEventListener('change', update);
  document.addEventListener('visibilitychange', update);
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(entries => { visible = entries[0].isIntersecting; update(); }).observe(stage);
  }
  update();
})();
