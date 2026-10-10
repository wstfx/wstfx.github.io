(() => {
  'use strict';
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  document.querySelectorAll('.dhh-conversation-art').forEach(art => {
    const target = art.closest('.project-card') || art.closest('.dhh-illustration');
    if (!target || typeof art.animate !== 'function') return;
    const parts = [
      [art.querySelector('.dhh-hand-high'), [
        { transform: 'rotate(0deg)' },
        { transform: 'rotate(-5deg)', offset: .3 },
        { transform: 'rotate(2deg)', offset: .65 },
        { transform: 'rotate(0deg)' }
      ]],
      [art.querySelector('.dhh-hand-low'), [
        { transform: 'rotate(0deg)' },
        { transform: 'rotate(3deg)', offset: .4 },
        { transform: 'rotate(0deg)' }
      ]],
      [art.querySelector('.dhh-listener-head'), [
        { transform: 'rotate(0deg)' },
        { transform: 'rotate(-3deg)', offset: .6 },
        { transform: 'rotate(0deg)' }
      ]],
      [art.querySelector('.dhh-conversation-marks'), [
        { opacity: .5 }, { opacity: 1, offset: .4 }, { opacity: .5 }
      ]]
    ];
    let animations = [];
    const stop = () => { animations.forEach(animation => animation.cancel()); animations = []; };
    const play = () => {
      if (reduced.matches || document.hidden) return;
      stop();
      animations = parts.map(([element, keyframes]) => element.animate(keyframes, {
        duration: 2100, easing: 'ease-in-out', iterations: 1
      }));
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
