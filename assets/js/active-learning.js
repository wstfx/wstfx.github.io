(() => {
  const figure = document.querySelector('.al-illustration');
  if (!figure) return;
  const description = figure.querySelector('[data-al-description]');
  const defaultDescription = description.textContent;
  const descriptions = {
    choose: 'Choose a sample that could help the current model learn.',
    learn: 'Use the selected sample to update the target model.',
    check: 'Evaluate the change in error, then inform the next selection.'
  };
  figure.querySelectorAll('[data-al-step]').forEach(button => {
    button.addEventListener('click', () => {
      const step = figure.dataset.step === button.dataset.alStep ? null : button.dataset.alStep;
      if (step) figure.dataset.step = step;
      else delete figure.dataset.step;
      figure.querySelectorAll('[data-al-step]').forEach(item => item.setAttribute('aria-pressed', String(item.dataset.alStep === step)));
      description.textContent = step ? descriptions[step] : defaultDescription;
    });
  });
  let paused = false;
  let visible = true;
  const motion = figure.querySelector('.al-motion');
  const update = () => figure.classList.toggle('is-paused', paused || !visible || document.hidden);
  motion.hidden = false;
  motion.addEventListener('click', () => {
    paused = !paused;
    motion.setAttribute('aria-pressed', String(paused));
    motion.textContent = paused ? 'Play animation' : 'Pause animation';
    update();
  });
  if ('IntersectionObserver' in window) new IntersectionObserver(entries => { visible = entries[0].isIntersecting; update(); }).observe(figure);
  document.addEventListener('visibilitychange', update);
  update();
})();
