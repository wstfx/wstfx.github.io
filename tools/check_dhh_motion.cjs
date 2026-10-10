/* Exercise interruption/reversal and suspension without depending on wall-clock timing. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const target = () => ({
  handlers: {}, attrs: {},
  addEventListener(type, fn) { this.handlers[type] = fn; },
  setAttribute(name, value) { this.attrs[name] = value; },
  emit(type, extra = {}) { this.handlers[type]?.({ pointerType: 'mouse', ...extra }); },
  contains() { return false; }
});
const stage = target();
const button = target();
const document = target();
const reduced = { ...target(), matches: false };
const animations = [];
const art = { animate() {}, querySelector() { return {
  animate() {
    const animation = {
      currentTime: 0, playbackRate: 1, playState: 'running',
      pause() { this.playState = 'paused'; },
      play() { this.playState = 'running'; },
      cancel() { this.currentTime = null; this.playState = 'idle'; }
    };
    animations.push(animation);
    return animation;
  }
}; } };
stage.querySelector = () => art;
const figure = { querySelector: selector => selector === '.dhh-stage' ? stage : button };
document.querySelector = () => figure;
const timers = new Map();
let observer;
let counter = 0;
const source = fs.readFileSync(path.join(__dirname, '../assets/js/dhh.js'), 'utf8');
vm.runInNewContext(source, {
  document, matchMedia: () => reduced,
  window: { IntersectionObserver: true },
  IntersectionObserver: class { constructor(fn) { observer = fn; } observe() {} },
  setTimeout: fn => { const id = ++counter; timers.set(id, fn); return id; },
  clearTimeout: id => timers.delete(id)
});
const tick = () => { const [id, fn] = timers.entries().next().value; timers.delete(id); fn(); };
const time = value => animations.forEach(animation => { animation.currentTime = value; });
const state = value => animations.forEach(animation => assert.equal(animation.playState, value));
const rate = value => animations.forEach(animation => assert.equal(animation.playbackRate, value));
assert.equal(animations.length, 5);
state('paused');
assert.equal(timers.size, 0, 'offscreen scene does not start');
observer([{ isIntersecting: true }]);
tick();
state('running');
rate(1);
time(700);
stage.emit('pointerenter');
stage.emit('pointerleave');
rate(-1);
animations.forEach(animation => assert.equal(animation.currentTime, 700, 'leave preserves the unfinished pose'));
stage.emit('pointerenter');
rate(1);
animations.forEach(animation => assert.equal(animation.currentTime, 700, 're-entry preserves the return pose'));
time(2200);
animations[0].onfinish();
assert.equal(timers.size, 0, 'hover holds the completed pose');
stage.emit('pointerleave');
rate(-1);
time(1800);
button.emit('click');
state('paused');
assert.equal(button.attrs['aria-pressed'], 'true');
button.emit('click');
state('running');
rate(-1);
observer([{ isIntersecting: false }]);
state('paused');
assert.equal(timers.size, 0);
observer([{ isIntersecting: true }]);
state('running');
rate(-1);
stage.emit('focusin');
rate(1);
stage.emit('pointerleave');
rate(1);
stage.emit('focusout');
rate(-1);
document.hidden = true;
document.emit('visibilitychange');
state('paused');
document.hidden = false;
document.emit('visibilitychange');
state('running');
reduced.matches = true;
reduced.emit('change');
state('paused');
assert.equal(button.hidden, true);
assert.equal(timers.size, 0);
animations.forEach(animation => assert.equal(animation.currentTime, 0));
reduced.matches = false;
reduced.emit('change');
assert.equal(button.hidden, false);
tick();
state('running');
rate(1);
time(2200);
animations[0].onfinish();
tick();
rate(-1);
time(0);
animations[0].onfinish();
tick();
rate(1);
console.log('PASS: DHH scene reverses interrupted gestures, holds on hover/focus, resumes in place, and suspends for pause, visibility and reduced motion.');
