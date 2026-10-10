(() => {
  'use strict';
  // Work cards use reversible CSS transitions. The case study has its own paced scene.
  const figure = document.querySelector('.dhh-illustration');
  const stage = figure?.querySelector('.dhh-stage');
  const art = stage?.querySelector('.dhh-life-art');
  const button = figure?.querySelector('.dhh-motion');
  if (!art || !button || typeof art.animate !== 'function') return;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const duration = 2200;
  const frames = (rest, active, start, end) => [
    { transform: rest, offset: 0 },
    { transform: rest, offset: start, easing: 'cubic-bezier(.4,0,.2,1)' },
    { transform: active, offset: end },
    { transform: active, offset: 1 }
  ];
  const poses = [
    ['.dhh-world', 'translate(0px,0px) scale(1)', 'translate(-10px,-4px) scale(1.035)', .04, .5],
    ['.dhh-family', 'scale(1)', 'scale(1.025)', .12, .55],
    ['.dhh-happiness', 'translate(0px,0px) rotate(0deg)', 'translate(-10px,-12px) rotate(-3deg)', .2, .65],
    ['.dhh-ai', 'translate(0px,0px) rotate(0deg)', 'translate(-13px,-7px) rotate(3deg)', .3, .78],
    ['.dhh-ai-core', 'scale(1)', 'scale(1.12)', .48, .9]
  ];
  const animations = poses.map(([selector, rest, active, start, end]) => {
    const animation = art.querySelector(selector).animate(frames(rest, active, start, end), {
      duration, fill: 'both', easing: 'linear'
    });
    animation.pause();
    animation.currentTime = 0;
    return animation;
  });
  const master = animations[0];
  let visible = !('IntersectionObserver' in window);
  let paused = false;
  let pointer = false;
  let focused = false;
  let moving = false;
  let goal = false;
  let nextOpen = true;
  let timer;
  const engaged = () => pointer || focused;
  const allowed = () => visible && !document.hidden && !paused && !reduced.matches;
  const clearTimer = () => { clearTimeout(timer); timer = undefined; };
  const schedule = (open, delay) => {
    nextOpen = open;
    clearTimer();
    if (allowed() && !engaged()) timer = setTimeout(() => move(open), delay);
  };
  const move = open => {
    clearTimer();
    if (!allowed()) return;
    goal = open;
    const atEndpoint = open ? master.currentTime >= duration : master.currentTime <= 0;
    if (atEndpoint) {
      moving = false;
      animations.forEach(animation => animation.pause());
      schedule(!open, open ? 2800 : 1600);
      return;
    }
    moving = true;
    // Reverse the existing timeline in place, including an unfinished incoming gesture.
    animations.forEach(animation => {
      animation.playbackRate = open ? 1 : -1;
      animation.play();
    });
  };
  master.onfinish = () => {
    moving = false;
    schedule(!goal, goal ? 2800 : 1600);
  };
  const update = () => {
    clearTimer();
    button.hidden = reduced.matches;
    if (reduced.matches) {
      animations.forEach(animation => { animation.cancel(); animation.pause(); animation.currentTime = 0; });
      moving = false;
      nextOpen = true;
      return;
    }
    if (!allowed()) { animations.forEach(animation => animation.pause()); return; }
    if (engaged()) move(true);
    else if (moving) animations.forEach(animation => animation.play());
    else schedule(nextOpen, 1200);
  };
  stage.addEventListener('pointerenter', event => {
    if (event.pointerType === 'touch') return;
    pointer = true;
    move(true);
  });
  stage.addEventListener('pointerleave', event => {
    if (event.pointerType === 'touch') return;
    pointer = false;
    if (!focused) move(false);
  });
  stage.addEventListener('focusin', () => { focused = true; move(true); });
  stage.addEventListener('focusout', event => {
    if (stage.contains(event.relatedTarget)) return;
    focused = false;
    if (!pointer) move(false);
  });
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
