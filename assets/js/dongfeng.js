(() => {
  const figure = document.querySelector('.dongfeng-illustration');
  const button = figure?.querySelector('.dongfeng-motion');
  if (figure && button) {
    let paused = false;
    let visible = true;
    const update = () => figure.classList.toggle('is-paused', paused || !visible || document.hidden);
    button.hidden = false;
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
  }

  const films = [...document.querySelectorAll('.simulation-film video')];
  films.forEach(film => film.addEventListener('play', () => {
    films.forEach(other => { if (other !== film) other.pause(); });
  }));
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) films.forEach(film => film.pause());
  });
})();
