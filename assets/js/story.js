(() => {
  'use strict';
  const stage = document.querySelector('.story-stage');
  if (!stage) return;
  const steps = [...document.querySelectorAll('.story-step')];
  const links = [...document.querySelectorAll('.story-waypoints a')];
  const fox = document.querySelector('.travelling-fox');
  const canvas = document.querySelector('.story-canvas');
  const world = document.querySelector('.world-drawing');
  const scenes = [...document.querySelectorAll('.world-scene')];
  const characters = [...document.querySelectorAll('.mascot-pose')];
  const route = document.querySelector('#route-ink');
  const control = document.querySelector('.motion-toggle');
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const compact = matchMedia('(max-width:900px)');
  const preferenceKey = 'zebang-story-motion-paused';
  const labels = ['A QUESTION TAKES SHAPE', '01 / START BY LISTENING', '02 / LOOK FOR THE EVIDENCE', '03 / FOLLOW IT INTO PRACTICE', '04 / THE NEXT QUESTION'];
  const thoughts = ['Every path starts with curiosity.', 'Whose experience needs a closer look?', 'What would make the answer convincing?', 'What happens outside the experiment?', 'What could this help someone understand?'];
  const descriptions = [
    'A curious fox with a field notebook, on a quiet woodland path.',
    'An attentive fox listening beside birds and folded conversation ribbons.',
    'A fox inspecting observations over a layered geometric landscape.',
    'A fox carrying a piece toward a bridge of connected building blocks.',
    'A fox sharing a small new possibility beside a sunlit exploratory structure.'
  ];
  // Mascot and illustration use ONE SVG coordinate system, including at short heights.
  const poses = [[300, 295, 1.10], [430, 380, .80], [165, 390, .80], [150, 340, .79], [155, 385, .80]];
  let userPaused = false;
  try { userPaused = localStorage.getItem(preferenceKey) === 'true'; } catch { /* Storage is optional. */ }
  const paused = () => reduced.matches || userPaused;
  let active = -1, scheduled = false, positions = [], visible = true;
  function measure() { positions = steps.map(step => step.getBoundingClientRect().top + scrollY); }
  function ambientState() {
    document.body.classList.toggle('scene-asleep', document.hidden || !visible);
  }
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
      canvas.setAttribute('aria-label', descriptions[index]);
      scenes.forEach((scene, i) => scene.classList.toggle('is-current', i === index));
      characters.forEach((character, i) => character.classList.toggle('is-current', i === index));
      links.forEach((link, i) => { if (i + 1 === index) link.setAttribute('aria-current', 'location'); else link.removeAttribute('aria-current'); });
    }
    world.setAttribute('viewBox', compact.matches ? '45 25 250 250' : '0 0 600 560');
    if (compact.matches) {
      fox.setAttribute('transform', 'translate(150 155) scale(1.08)');
    } else {
      const distance = Math.min(380, innerHeight * .48);
      const raw = index ? Math.max(0, Math.min(1, (cursor - positions[index]) / distance)) : 1;
      const t = paused() ? 1 : raw * raw * (3 - 2 * raw);
      const from = poses[Math.max(0, index - 1)], to = poses[index];
      const mix = n => from[n] + (to[n] - from[n]) * t;
      fox.setAttribute('transform', `translate(${mix(0)} ${mix(1)}) scale(${mix(2)})`);
    }
    const span = positions[4] - positions[0];
    const progress = span > 0 ? Math.min(1, Math.max(0, (cursor - positions[0]) / span)) : 0;
    if (route) route.style.strokeDashoffset = String(1 - progress);
  }
  function requestRender() { if (!scheduled) { scheduled = true; requestAnimationFrame(render); } }
  function motionState() {
    document.body.classList.toggle('motion-paused', paused());
    control.setAttribute('aria-pressed', String(paused()));
    control.disabled = reduced.matches;
    control.title = reduced.matches ? 'Animations are off to match your system preference.' : (userPaused ? 'Resume animations' : 'Pause animations');
    control.querySelector('.motion-state').textContent = paused() ? 'off' : 'on';
    requestRender();
  }
  control.addEventListener('click', () => {
    userPaused = !userPaused;
    try { localStorage.setItem(preferenceKey, String(userPaused)); } catch { /* Reading still works without storage. */ }
    motionState();
  });
  reduced.addEventListener('change', motionState);
  compact.addEventListener('change', () => { measure(); requestRender(); });
  addEventListener('scroll', requestRender, { passive:true });
  addEventListener('resize', () => { measure(); requestRender(); });
  addEventListener('pageshow', () => { measure(); requestRender(); ambientState(); });
  document.addEventListener('visibilitychange', ambientState);
  if ('IntersectionObserver' in window) new IntersectionObserver(entries => {
    visible = entries[0].isIntersecting;
    ambientState();
  }, { threshold:0 }).observe(stage);
  if ('ResizeObserver' in window) new ResizeObserver(() => { measure(); requestRender(); }).observe(document.querySelector('.story-pages'));
  document.fonts?.ready.then(() => { measure(); requestRender(); });
  measure(); motionState(); ambientState(); render();
})();
