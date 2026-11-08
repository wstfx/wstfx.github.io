// Exercise the shipped gate through its startup and real form submit handler.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { webcrypto, createHash } = require('node:crypto');
const root = path.join(__dirname, '..');
const source = fs.readFileSync(path.join(root, 'assets/js/privacy-gate.js'), 'utf8');
const storageKey = 'zebang-portfolio-access-v1';
const lifetime = 30 * 86400000;
const testToken = 'test_'.padEnd(43, 'a');
const testDigest = createHash('sha256').update(testToken).digest('hex');
// A test-only digest avoids publishing the owner's live invitation in fixtures.
const testSource = source.replace(/var invitationHash = '[a-f0-9]{64}';/,
  `var invitationHash = '${testDigest}';`);
assert.notEqual(testSource, source, 'The test invitation must be isolated from production.');

async function open({ hash = '', stored = 0, storageBlocked = false,
  cryptoMode = 'normal', loading = false, script = testSource } = {}) {
  const store = new Map(stored ? [[storageKey, String(stored)]] : []);
  const classes = new Set(['privacy-locked']);
  const name = { value: '', focus() {}, select() { selected = 'name'; } };
  const school = { value: '', select() { selected = 'school'; } };
  const error = { textContent: '' };
  const button = { disabled: false };
  let gate, submit, ready, selected, replaced;
  const form = {
    querySelector: () => button,
    addEventListener(event, fn) { assert.equal(event, 'submit'); submit = fn; }
  };
  const location = { hash, pathname: '/work/fire-sim.html', search: '?from=review' };
  const document = {
    readyState: loading ? 'loading' : 'complete',
    documentElement: { classList: { remove: key => classes.delete(key) } },
    body: { classList: { add() {}, remove() {} }, appendChild: el => { gate = el; } },
    createElement: () => ({ setAttribute() {}, remove() { gate = null; } }),
    getElementById: id => ({ 'privacy-gate': gate, 'privacy-gate-form': form,
      'privacy-name': name, 'privacy-school': school, 'privacy-gate-error': error }[id]),
    addEventListener(event, fn) { assert.equal(event, 'DOMContentLoaded'); ready = fn; }
  };
  const historyState = { keep: true };
  const ctx = { document, location, TextEncoder, Date,
    history: { state: historyState, replaceState(state, title, url) {
      assert.equal(state, historyState); replaced = url; location.hash = '';
    } },
    localStorage: {
      getItem(key) { if (storageBlocked) throw Error('Storage blocked'); return store.get(key); },
      setItem(key, value) { if (storageBlocked) throw Error('Storage blocked'); store.set(key, value); }
    }
  };
  if (cryptoMode === 'normal') ctx.crypto = webcrypto;
  if (cryptoMode === 'missing-subtle') ctx.crypto = {};
  if (cryptoMode === 'rejecting') ctx.crypto = {
    subtle: { digest: async () => { throw Error('Crypto unavailable'); } }
  };
  vm.runInNewContext(script, ctx);
  if (loading) await ready();
  // Startup may be waiting for Web Crypto; drain real asynchronous digest work.
  for (let i = 0; i < 100 && classes.has('privacy-locked') && !gate; i++) {
    await new Promise(resolve => setTimeout(resolve, 5));
  }
  return {
    get unlocked() { return !classes.has('privacy-locked'); },
    get gate() { return gate; }, get replaced() { return replaced; },
    get selected() { return selected; }, store, error, button, location,
    async answer(first, second) {
      assert.ok(submit, 'Questions must be available before submitting.');
      name.value = first; school.value = second;
      await submit({ preventDefault() {} });
      assert.equal(button.disabled, false, 'Submit is usable after a failed attempt.');
    }
  };
}

function remembered(run) {
  assert.ok(Math.abs(Number(run.store.get(storageKey)) - Date.now() - lifetime) < 2000,
    'Successful access should last 30 days.');
}

(async () => {
  const accepted = [
    ['Zebang', 'Westlake'], ['Zebang Wu', 'Westlake University'], ['Wu Zebang', 'Westlake Uni'],
    ['Zeb', 'WLU'], ['吴泽邦', '西湖大学'], ['泽邦', '西湖'], ['吳澤邦', '西湖大學'],
    ['澤邦', 'Xi Hu Da Xue'], ['ZEBANG', 'WESTLAKE'], ['  Ze-bang! ', 'West lake'],
    ['Ｚｅｂａｎｇ', 'Ｗｅｓｔｌａｋｅ'], ['Zébang', 'Westláke'],
    ['Ze\u200bbang', 'West\u200blake'],
    ['Zebnag', 'Westlkae'], // Adjacent transposition.
    ['Zebeng', 'Westlale'], // Substitution.
    ['Zebng', 'Westlke'],   // Deletion.
    ['Zebaang', 'Westlaake'], // Insertion.
    ['Zebang W', 'Westlake Universit']
  ];
  for (const cryptoMode of ['normal', 'absent', 'missing-subtle', 'rejecting']) {
    for (const pair of accepted) {
      const run = await open({ cryptoMode });
      assert.ok(run.gate && !run.unlocked);
      await run.answer(...pair);
      assert.ok(run.unlocked && !run.gate, `Should accept ${pair.join(' / ')} (${cryptoMode}).`);
      remembered(run);
    }
  }
  for (const pair of [
    ['', 'Westlake'], ['Zebang', ''], ['  ', '  '], ['!!!', 'Westlake'],
    ['Alice', 'Westlake'], ['Zebang', 'Harvard'], ['Ze', 'Westlake'], ['Zed', 'Westlake'],
    ['吴', '西湖大学'], ['Zebang', 'WL'], ['Zebang', 'xwestlakey'],
    ['helloZebang', 'Westlake'], ['Zebang', 'notWestlake'], ['Zebang', 'W1U'],
    ['Zebang', '西胡大学'], ['Zebang', 'x'.repeat(10000)], ['<script>', 'Westlake']
  ]) {
    const run = await open({ cryptoMode: 'absent' });
    await run.answer(...pair);
    assert.ok(!run.unlocked && run.gate, `Should reject ${pair.join(' / ')}.`);
    assert.equal(run.store.size, 0);
    assert.ok(run.error.textContent);
  }
  const retry = await open();
  await retry.answer('Alice', 'Westlake'); assert.equal(retry.selected, 'name');
  await retry.answer('Zebang', 'Harvard'); assert.equal(retry.selected, 'school');
  await retry.answer('Zebang', 'Westlake'); assert.ok(retry.unlocked);
  const blocked = await open({ storageBlocked: true, cryptoMode: 'absent' });
  await blocked.answer('Zebang', 'Westlake'); assert.ok(blocked.unlocked);
  assert.equal(blocked.store.size, 0);
  assert.ok((await open({ stored: Date.now() + 60000 })).unlocked);
  assert.ok((await open({ stored: Date.now() - 60000 })).gate);

  for (const loading of [true, false]) {
    const invitation = await open({ hash: '#invite=' + testToken, loading });
    assert.ok(invitation.unlocked && !invitation.gate); remembered(invitation);
    assert.equal(invitation.replaced, '/work/fire-sim.html?from=review');
  }
  for (const hash of ['#invite=bad', '#invite=' + 'x'.repeat(43),
    '#invite=' + testToken + '&extra=1', '#invite=%ZZ']) {
    const run = await open({ hash });
    assert.ok(!run.unlocked && run.gate); assert.equal(run.store.size, 0);
    assert.equal(run.replaced, '/work/fire-sim.html?from=review');
  }
  const noCryptoInvite = await open({ hash: '#invite=' + testToken, cryptoMode: 'absent' });
  assert.ok(noCryptoInvite.gate); await noCryptoInvite.answer('Zebang', 'Westlake');
  assert.ok(noCryptoInvite.unlocked);
  const noStorageInvite = await open({ hash: '#invite=' + testToken, storageBlocked: true });
  assert.ok(noStorageInvite.unlocked);
  const existingInvite = await open({ hash: '#invite=' + testToken, stored: Date.now() + 60000 });
  assert.ok(existingInvite.unlocked); assert.ok(existingInvite.replaced);
  const anchor = await open({ hash: '#research' });
  assert.equal(anchor.location.hash, '#research'); assert.equal(anchor.replaced, undefined);

  // If available locally, check the real token/digest pair without logging either.
  const invitationFile = path.join(root, '../website-planning/portfolio-invitation-link.txt');
  if (fs.existsSync(invitationFile)) {
    const url = new URL(fs.readFileSync(invitationFile, 'utf8').trim());
    const liveInvitation = await open({ hash: url.hash, script: source });
    assert.ok(liveInvitation.unlocked, 'Stored owner invitation must remain compatible.');
  }
  console.log('PASS: informal aliases, normalization, bounded typos, unrelated/blank answers, retry focus, unavailable crypto/storage, 30-day access, invitation validation/cleanup and section anchors.');
})().catch(error => { console.error(error); process.exitCode = 1; });
