(() => {
  'use strict';
  const figure = document.querySelector('.dhh-illustration');
  if (!figure) return;
  const description = figure.querySelector('[data-dhh-description]');
  const overview = description.textContent;
  const descriptions = {
    happiness: 'Happiness lives in shared routines, meaningful activities, and room for personal choice.',
    support: 'Family, school, community, and public services form the setting for everyday participation.',
    technology: 'Transcription and sound alerts illustrate ways technology could improve access to everyday situations.'
  };
  const buttons = [...figure.querySelectorAll('[data-dhh-lens]')];
  buttons.forEach(button => {
    button.addEventListener('click', () => {
      const lens = figure.dataset.lens === button.dataset.dhhLens ? null : button.dataset.dhhLens;
      if (lens) figure.dataset.lens = lens;
      else delete figure.dataset.lens;
      buttons.forEach(item => item.setAttribute('aria-pressed', String(item.dataset.dhhLens === lens)));
      description.textContent = lens ? descriptions[lens] : overview;
    });
  });
  figure.querySelector('.dhh-lenses').hidden = false;
  const motion = figure.querySelector('.dhh-motion');
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  let paused = false;
  const rect = figure.getBoundingClientRect();
  let visible = rect.bottom > 0 && rect.top < window.innerHeight;
  const update = () => {
    figure.classList.toggle('is-paused', paused || !visible || document.hidden || reduced.matches);
    motion.hidden = reduced.matches;
    motion.setAttribute('aria-pressed', String(paused));
    motion.textContent = paused ? 'Play animation' : 'Pause animation';
  };
  motion.addEventListener('click', () => { paused = !paused; update(); });
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(entries => { visible = entries[0].isIntersecting; update(); }).observe(figure);
  }
  reduced.addEventListener('change', update);
  document.addEventListener('visibilitychange', update);
  update();
})();
