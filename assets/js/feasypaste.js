(() => {
  'use strict';
  const proof = document.querySelector('.fp-proof');
  if (proof) {
    const tabs = [...proof.querySelectorAll('[role=tab]')];
    const panels = [...proof.querySelectorAll('[role=tabpanel]')];
    const select = (index, focus = false) => {
      tabs.forEach((tab, i) => {
        tab.setAttribute('aria-selected', String(i === index));
        tab.tabIndex = i === index ? 0 : -1;
        panels[i].hidden = i !== index;
      });
      if (focus) tabs[index].focus();
    };
    tabs.forEach((tab, i) => {
      tab.addEventListener('click', () => select(i));
      tab.addEventListener('keydown', event => {
        let next;
        if (event.key === 'ArrowRight') next = (i + 1) % tabs.length;
        if (event.key === 'ArrowLeft') next = (i - 1 + tabs.length) % tabs.length;
        if (event.key === 'Home') next = 0;
        if (event.key === 'End') next = tabs.length - 1;
        if (next === undefined) return;
        event.preventDefault();
        select(next, true);
      });
    });
    proof.querySelector('.fp-tabs').hidden = false;
    select(1);
  }
  const video = document.querySelector('.fp-video');
  const play = video?.querySelector('.fp-video-load');
  if (play) {
    play.hidden = false;
    play.addEventListener('click', () => {
      const player = video.querySelector('.fp-video-player');
      const iframe = document.createElement('iframe');
      iframe.src = 'https://player.bilibili.com/player.html?bvid=BV1eVLi6PEMj&p=1&autoplay=0';
      iframe.title = 'FeasyPaste promotional video on Bilibili (Chinese)';
      iframe.allowFullscreen = true;
      iframe.allow = 'fullscreen; picture-in-picture';
      iframe.referrerPolicy = 'no-referrer';
      player.append(iframe);
      player.hidden = false;
      play.hidden = true;
      video.classList.add('is-loaded');
    }, { once: true });
  }
})();
