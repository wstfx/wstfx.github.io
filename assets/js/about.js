(() => {
  'use strict';
  const carousel = document.querySelector('.portrait-carousel');
  if (carousel) {
    const slides = [...carousel.querySelectorAll('.portrait-slide')];
    const controls = carousel.querySelector('.portrait-controls');
    const toggle = carousel.querySelector('.portrait-play');
    const announcement = carousel.querySelector('.portrait-announcement');
    const fill = carousel.querySelector('.portrait-progress-fill');
    const reduced = matchMedia('(prefers-reduced-motion: reduce)');
    const duration = 7000;
    let remaining = duration, startedAt = null, progress;
    let index = 0, timer, hovered = false, focused = false;
    let visible = false, paused = reduced.matches;
    function createProgress() {
      progress?.cancel();
      progress = !reduced.matches && fill?.animate ? fill.animate(
        [{transform: 'scaleX(0)'}, {transform: 'scaleX(1)'}],
        {duration, easing: 'linear', fill: 'forwards'}
      ) : null;
      progress?.pause();
    }
    function scheduleSlide() {
      clearTimeout(timer);
      if (startedAt !== null) remaining = Math.max(0, remaining - (performance.now() - startedAt));
      startedAt = null;
      progress?.pause();
      if (progress) progress.currentTime = duration - remaining;
      if (!paused && !hovered && !focused && visible && !document.hidden) {
        startedAt = performance.now();
        progress?.play();
        timer = setTimeout(() => show(index + 1), remaining);
      }
    }
    function updateToggle() {
      toggle.textContent = paused ? 'Play' : 'Pause';
      toggle.setAttribute('aria-label', paused ? 'Play photo slideshow' : 'Pause photo slideshow');
    }
    function show(next, manual = false) {
      clearTimeout(timer);
      remaining = duration;
      startedAt = null;
      index = (next + slides.length) % slides.length;
      slides.forEach((slide, i) => {
        slide.classList.toggle('is-current', i === index);
        slide.setAttribute('aria-hidden', String(i !== index));
      });
      carousel.querySelector('.portrait-counter').textContent = `${index + 1} / ${slides.length}`;
      // Automatic changes stay quiet; manual navigation announces the caption.
      announcement.setAttribute('aria-live', manual ? 'polite' : 'off');
      const sentence = slides[index].querySelector('.portrait-sentence');
      announcement.replaceChildren(`Photo ${index + 1} of ${slides.length}. `, sentence.cloneNode(true), slides[index].querySelector('.portrait-place').textContent);
      if (manual) { paused = true; updateToggle(); }
      scheduleSlide();
    }
    carousel.querySelector('.portrait-prev').addEventListener('click', () => show(index - 1, true));
    carousel.querySelector('.portrait-next').addEventListener('click', () => show(index + 1, true));
    toggle.addEventListener('click', () => { paused = !paused; updateToggle(); scheduleSlide(); });
    carousel.addEventListener('keydown', event => {
      if (!['ArrowLeft', 'ArrowRight'].includes(event.key)) return;
      event.preventDefault(); show(index + (event.key === 'ArrowRight' ? 1 : -1), true);
    });
    let touch;
    carousel.addEventListener('touchstart', event => {
      touch = event.touches.length === 1 ? event.touches[0] : null;
    }, {passive: true});
    carousel.addEventListener('touchend', event => {
      if (!touch || !event.changedTouches.length) return;
      const dx = event.changedTouches[0].clientX - touch.clientX;
      const dy = event.changedTouches[0].clientY - touch.clientY;
      if (Math.abs(dx) > 45 && Math.abs(dx) > Math.abs(dy)) show(index + (dx < 0 ? 1 : -1), true);
      touch = null;
    }, {passive: true});
    carousel.addEventListener('mouseenter', () => { hovered = true; scheduleSlide(); });
    carousel.addEventListener('mouseleave', () => { hovered = false; scheduleSlide(); });
    carousel.addEventListener('focusin', () => { focused = true; scheduleSlide(); });
    carousel.addEventListener('focusout', event => {
      focused = carousel.contains(event.relatedTarget); scheduleSlide();
    });
    document.addEventListener('visibilitychange', scheduleSlide);
    reduced.addEventListener('change', () => {
      if (reduced.matches) paused = true;
      createProgress();
      updateToggle(); scheduleSlide();
    });
    if ('IntersectionObserver' in window) {
      const observer = new IntersectionObserver(entries => {
        visible = entries[0].isIntersecting; scheduleSlide();
      }, {threshold: 0.15});
      observer.observe(carousel);
    } else { visible = true; }
    controls.hidden = false;
    createProgress();
    updateToggle(); scheduleSlide();
  }
  const nav = document.querySelector('.year-nav');
  const years = [...document.querySelectorAll('.timeline-year')];
  if (!nav || !years.length) return;
  const links = [...nav.querySelectorAll('a')];
  const mobile = matchMedia('(max-width: 700px)');
  let current, scheduled = false;
  function update() {
    scheduled = false;
    const threshold = parseFloat(getComputedStyle(years[0]).scrollMarginTop) + 1;
    let index = 0;
    years.forEach((year, i) => { if (year.getBoundingClientRect().top <= threshold) index = i; });
    if (current === index) return;
    current = index;
    links.forEach((link, i) => {
      if (i === index) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    });
    // Keep the current year reachable in the horizontal mobile navigation.
    if (mobile.matches) {
      const target = links[index].getBoundingClientRect();
      const bounds = nav.getBoundingClientRect();
      if (target.left < bounds.left || target.right > bounds.right) {
        nav.scrollLeft += target.left - bounds.left - 12;
      }
    }
  }
  function schedule() {
    if (!scheduled) { scheduled = true; requestAnimationFrame(update); }
  }
  addEventListener('scroll', schedule, {passive: true});
  addEventListener('resize', () => { current = undefined; schedule(); });
  addEventListener('hashchange', schedule);
  update();
})();
