(() => {
  const figure = document.querySelector('.vr-illustration');
  if (!figure) return;
  const description = figure.querySelector('[data-vr-description]');
  const overview = description.textContent;
  const descriptions = {
    platform: 'Platform frame: the moving train contracts, and its clock ticks more slowly.',
    train: 'Train frame: the moving platform contracts, and its clock ticks more slowly.'
  };
  const refreshDescription = () => {
    description.textContent = figure.classList.contains('is-at-rest')
      ? 'At rest relative to each other: full lengths and equal clock rates.'
      : (descriptions[figure.dataset.frame] || overview);
  };
  figure.querySelectorAll('[data-vr-frame]').forEach(button => {
    button.addEventListener('click', () => {
      const frame = figure.dataset.frame === button.dataset.vrFrame ? null : button.dataset.vrFrame;
      if (frame) figure.dataset.frame = frame;
      else delete figure.dataset.frame;
      figure.querySelectorAll('[data-vr-frame]').forEach(item => item.setAttribute('aria-pressed', String(item.dataset.vrFrame === frame)));
      refreshDescription();
    });
  });
  const speed = figure.querySelector('#vr-speed');
  const updateSpeed = () => {
    const beta = Number(speed.value) / 100;
    const factor = Math.sqrt(1 - beta * beta);
    figure.style.setProperty('--vr-length', String(factor));
    figure.style.setProperty('--vr-clock-period', `${6 / factor}s`);
    figure.style.setProperty('--vr-travel', `${38 * beta / .8}px`);
    figure.style.setProperty('--vr-platform-travel', `${22 * beta / .8}px`);
    figure.classList.toggle('is-at-rest', beta === 0);
    refreshDescription();
    figure.querySelector('#vr-speed-value').textContent = `v = ${beta.toFixed(2)}c`;
    speed.setAttribute('aria-valuetext', `${Math.round(beta * 100)} percent of the speed of light`);
    figure.querySelector('[data-vr-factor]').textContent = `${Math.round(factor * 100)}%`;
    figure.querySelectorAll('[data-vr-rate]').forEach(label => { label.textContent = `${factor.toFixed(2)}×`; });
    figure.querySelectorAll('[data-vr-length]').forEach(label => { label.textContent = `${factor.toFixed(2)} L₀`; });
  };
  speed.addEventListener('input', updateSpeed);
  updateSpeed();
  let paused = false;
  let visible = true;
  const motion = figure.querySelector('.vr-motion');
  const update = () => figure.classList.toggle('is-paused', paused || !visible || document.hidden);
  motion.hidden = false;
  motion.addEventListener('click', () => {
    paused = !paused;
    motion.textContent = paused ? 'Play animation' : 'Pause animation';
    motion.setAttribute('aria-pressed', String(paused));
    update();
  });
  if ('IntersectionObserver' in window) new IntersectionObserver(entries => { visible = entries[0].isIntersecting; update(); }).observe(figure);
  document.addEventListener('visibilitychange', update);
  update();
})();
