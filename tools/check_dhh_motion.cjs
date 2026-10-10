/* Verify ambient motion suspension and user pause ownership without timers. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const target = () => ({
  handlers: {}, attrs: {},
  addEventListener(type, fn) { this.handlers[type] = fn; },
  setAttribute(name, value) { this.attrs[name] = value; },
  emit(type) { this.handlers[type]?.(); }
});
const stage = {};
const button = target();
const document = target();
const reduced = { ...target(), matches: false };
let suspended;
let observer;
const figure = {
  querySelector: selector => selector === '.dhh-stage' ? stage : button,
  classList: { toggle(name, value) { assert.equal(name, 'is-paused'); suspended = value; } }
};
document.querySelector = () => figure;
vm.runInNewContext(fs.readFileSync(path.join(__dirname, '../assets/js/dhh.js'), 'utf8'), {
  document, matchMedia: () => reduced,
  window: { IntersectionObserver: true },
  IntersectionObserver: class { constructor(fn) { observer = fn; } observe(element) { assert.equal(element, stage); } }
});
assert.equal(suspended, true, 'wait for visibility before playing');
observer([{ isIntersecting: true }]);
assert.equal(suspended, false);
button.emit('click');
assert.equal(suspended, true);
assert.equal(button.attrs['aria-pressed'], 'true');
observer([{ isIntersecting: false }]);
observer([{ isIntersecting: true }]);
assert.equal(suspended, true, 'visibility cannot override user pause');
button.emit('click');
assert.equal(suspended, false);
assert.equal(button.attrs['aria-pressed'], 'false');
document.hidden = true;
document.emit('visibilitychange');
assert.equal(suspended, true);
document.hidden = false;
document.emit('visibilitychange');
assert.equal(suspended, false);
reduced.matches = true;
reduced.emit('change');
assert.equal(suspended, true);
assert.equal(button.hidden, true);
reduced.matches = false;
reduced.emit('change');
assert.equal(suspended, false);
assert.equal(button.hidden, false);
console.log('PASS: DHH ambient motion respects user pause, visibility and reduced motion.');
