(() => {
  'use strict';
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  document.querySelectorAll('.dhh-wellbeing-art').forEach(art => {
    const target = art.closest('.project-card') || art.closest('.dhh-illustration');
    if (!target || typeof art.animate !== 'function') return;
    const unfold = (x, y) => [
      { transform: `translate(${x}px, ${y}px) scale(.86)`, opacity: .25 },
      { transform: 'translate(0px, -5px) scale(1.025)', opacity: 1, offset: .7 },
      { transform: 'translate(0px, 0px) scale(1)', opacity: 1 }
    ];
    const parts = [
      ['.dhh-touch', [
        { transform: 'rotate(0deg)' },
        { transform: 'rotate(.7deg)', offset: .3 },
        { transform: 'rotate(0deg)' }
      ], 0, 1000],
      ['.dhh-device', [
        { stroke: '#c45222' },
        { stroke: '#e2a34f', offset: .35 },
        { stroke: '#c45222' }
      ], 80, 1100],
      ['.dhh-family', unfold(-20, 24), 180, 1100],
      ['.dhh-happiness', unfold(-12, 30), 300, 1100],
      ['.dhh-ai', unfold(-30, 18), 420, 1100]
    ];
    let animations = [];
    const stop = () => { animations.forEach(animation => animation.cancel()); animations = []; };
    const play = () => {
      if (reduced.matches || document.hidden) return;
      stop();
      animations = parts.flatMap(([selector, keyframes, delay, duration]) => {
        const element = art.querySelector(selector);
        return element ? [element.animate(keyframes, {
          duration, delay, easing: 'cubic-bezier(.22,.61,.36,1)', iterations: 1, fill: 'backwards'
        })] : [];
      });
    };
    target.addEventListener('pointerenter', event => { if (event.pointerType !== 'touch') play(); });
    target.addEventListener('focusin', event => { if (!target.contains(event.relatedTarget)) play(); });
    reduced.addEventListener('change', () => { if (reduced.matches) stop(); });
    document.addEventListener('visibilitychange', () => { if (document.hidden) stop(); });
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(entries => { if (!entries[0].isIntersecting) stop(); }).observe(art);
    }
  });
})();
