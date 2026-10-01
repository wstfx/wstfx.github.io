(() => {
  'use strict';
  const stage = document.querySelector('.story-stage');
  if (!stage) return;
  const steps = [...document.querySelectorAll('.story-step')];
  const links = [...document.querySelectorAll('.story-waypoints a')];
  const fox = document.querySelector('.travelling-fox');
  const canvas = document.querySelector('.story-canvas');
  const route = document.querySelector('#route-ink');
  const control = document.querySelector('.motion-toggle');
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const compact = matchMedia('(max-width:900px)');
  const labels = ['A QUESTION TAKES SHAPE', '01 / START BY LISTENING', '02 / LOOK FOR THE EVIDENCE', '03 / FOLLOW IT INTO PRACTICE', '04 / THE NEXT QUESTION'];
  const thoughts = ['Every path starts with curiosity.', 'Whose experience needs a closer look?', 'What would make the answer convincing?', 'What happens outside the experiment?', 'What could this help someone understand?'];
  // Coordinates are fractions of the same canvas: the logo never changes its geometry.
  const poses = [[0, -.015, 1], [.235, .23, .50], [-.27, .25, .47], [-.245, -.08, .43], [-.235, .17, .49]];
  let paused = reduced.matches;
  let active = -1, scheduled = false, positions = [];
  function measure() { positions = steps.map(step => step.getBoundingClientRect().top + scrollY); }
  function render() {
    scheduled = false;
    const cursor = scrollY + (compact.matches ? stage.getBoundingClientRect().bottom + 35 : innerHeight * .44);
    let index = 0;
    positions.forEach((top, i) => { if (cursor >= top) index = i; });
    if (index !== active) {
      active = index;
      stage.dataset.scene = String(index);
      stage.querySelector('.stage-label').textContent = labels[index];
      stage.querySelector('.stage-count').textContent = `0${index} / 04`;
      stage.querySelector('.stage-thought').textContent = thoughts[index];
      links.forEach((link, i) => { if (i + 1 === index) link.setAttribute('aria-current', 'location'); else link.removeAttribute('aria-current'); });
    }
    if (!compact.matches) {
      // The move finishes inside the opening of each chapter, then settles for reading.
      const distance = Math.min(380, innerHeight * .48);
      const raw = index ? Math.max(0, Math.min(1, (cursor - positions[index]) / distance)) : 1;
      const t = paused ? 1 : raw * raw * (3 - 2 * raw);
      const from = poses[Math.max(0, index - 1)], to = poses[index];
      const mix = n => from[n] + (to[n] - from[n]) * t;
      fox.style.setProperty('--fox-x', `${mix(0) * canvas.clientWidth}px`);
      fox.style.setProperty('--fox-y', `${mix(1) * canvas.clientHeight}px`);
      fox.style.setProperty('--fox-scale', mix(2));
    }
    const span = positions[4] - positions[0];
    const progress = span > 0 ? Math.min(1, Math.max(0, (cursor - positions[0]) / span)) : 0;
    route.style.strokeDashoffset = String(1 - progress);
  }
  function requestRender() { if (!scheduled) { scheduled = true; requestAnimationFrame(render); } }
  function motionState() {
    document.body.classList.toggle('motion-paused', paused);
    control.setAttribute('aria-pressed', String(paused));
    control.setAttribute('aria-label', 'Reduce scene motion');
    control.querySelector('span').textContent = paused ? 'off' : 'on';
    requestRender();
  }
  control.addEventListener('click', () => { paused = !paused; motionState(); });
  reduced.addEventListener('change', () => { paused = reduced.matches; motionState(); });
  addEventListener('scroll', requestRender, { passive:true });
  addEventListener('resize', () => { measure(); requestRender(); });
  addEventListener('pageshow', () => { measure(); requestRender(); });
  if ('ResizeObserver' in window) new ResizeObserver(() => { measure(); requestRender(); }).observe(document.querySelector('.story-pages'));
  document.fonts?.ready.then(() => { measure(); requestRender(); });
  measure(); motionState(); render();
})();
