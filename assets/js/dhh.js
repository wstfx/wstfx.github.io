(() => {
  'use strict';
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  document.querySelectorAll('.dhh-sign-art').forEach(art => {
    const hand = art.querySelector('.dhh-sign-hand');
    const arm = art.querySelector('.dhh-sign-arm');
    const trace = art.querySelector('.dhh-sign-trace');
    const figure = art.closest('.dhh-illustration');
    const card = art.closest('.project-card');
    const motion = figure?.querySelector('.dhh-motion');
    let elapsed = 0, last = null, frame = 0, playing = Boolean(figure);
    let paused = false, visible = false;
    // One circle at the chest, followed by a quiet hold. Keep the hand upright.
    const pose = t => {
      const progress = Math.min(1, Math.max(0, (t - 500) / 3000));
      const angle = progress * Math.PI * 2 - Math.PI / 2;
      const x = 236 + Math.cos(angle) * 31;
      const y = 266 + Math.sin(angle) * 31;
      hand.setAttribute('transform', `translate(${x.toFixed(2)} ${y.toFixed(2)})`);
      const wx = x - 16, wy = y + 50;
      arm.setAttribute('d', `M153 353Q175 344 ${wx} ${wy}L${wx + 31} ${wy + 6}Q188 381 155 376Q136 371 153 353Z`);
      trace.style.strokeDashoffset = String(1 - progress);
      trace.style.opacity = progress === 0 ? '0' : '.65';
    };
    const active = () => playing && visible && !paused && !document.hidden && !reduced.matches;
    const tick = now => {
      frame = 0;
      if (!active()) { last = null; return; }
      if (last !== null) elapsed += Math.min(now - last, 80);
      last = now;
      pose(elapsed);
      if (elapsed >= 5500) {
        if (figure) elapsed %= 5500;
        else { playing = false; last = null; return; }
      }
      frame = requestAnimationFrame(tick);
    };
    const update = () => {
      if (motion) {
        motion.hidden = reduced.matches;
        motion.setAttribute('aria-pressed', String(paused));
        motion.textContent = paused ? 'Play animation' : 'Pause animation';
      }
      if (!active()) {
        cancelAnimationFrame(frame); frame = 0; last = null;
        if (reduced.matches) { elapsed = 0; playing = Boolean(figure); pose(3500); }
      } else if (!frame) frame = requestAnimationFrame(tick);
    };
    pose(reduced.matches ? 3500 : 0);
    motion?.addEventListener('click', () => { paused = !paused; update(); });
    const play = () => {
      if (reduced.matches) return;
      elapsed = 0; last = null; playing = true; pose(0); update();
    };
    // Finish the complete sign even if the pointer leaves before the circle ends.
    card?.addEventListener('pointerenter', event => { if (event.pointerType !== 'touch') play(); });
    card?.addEventListener('focusin', event => { if (!card.contains(event.relatedTarget)) play(); });
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(entries => {
        visible = entries[0].isIntersecting;
        update();
      }).observe(art);
    } else { visible = true; update(); }
    reduced.addEventListener('change', update);
    document.addEventListener('visibilitychange', update);
  });
})();
