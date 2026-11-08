(function () {
	'use strict';

	var storageKey = 'zebang-portfolio-access-v1';
	var accessLifetime = 30 * 24 * 60 * 60 * 1000;
	// Only the invitation digest is published. The shareable URL stays with the owner.
	var invitationHash = 'b4281cdf74271f700710d8d76a7768becfbd83b1b95abc933bc08fcac25124dc';
	// These public names are a friendly introduction, not authentication secrets.
	// Match them locally even in browsers without Web Crypto (e.g. some webviews).
	var nameAliases = ['zeb', 'zebang', 'zebangwu', 'wuzebang', '吴泽邦', '吳澤邦', '泽邦', '澤邦'];
	var schoolAliases = ['westlake', 'westlakeuniversity', 'westlakeuni', 'wlu', 'xihu', 'xihudaxue', '西湖', '西湖大学', '西湖大學'];
	// Retain every previously accepted exact answer for compatibility.
	var acceptedNameHashes = new Set([
		'43ba2ff981d420e915076f2f11915edf906bd035bc930906483c2859110bae18',
		'8a1de20d6c37c303b2303768d62013a6495c04fe546be635b3f1ad377e97cd9f',
		'34bdf5e034c551d8d05f2bae7f55fe88b65c63840dbc97641a9115d86c5b771d',
		'26572b3bdf1727c327d51bdd5f400c2ce83589d97e36ab4875ac1a348cbc39ec',
		'8b9fb90c491878f9512ebd3fc69a849ef8afe2ac6234e78b993b6ad42e50b88d'
	]);
	var acceptedSchoolHashes = new Set([
		'42a4558f45a9662cba2c16aa6913401c8593395cd1eb179272fc154c464eb6ca',
		'856204d2bc090c3bf91a4961d1ea9ace7bf2f6d84c7ac6ee9a65995987dd8af8',
		'fa34f08396c19f51841b91708776b52925258c5d9b491e2967f3a73918c1466e',
		'a2b9d187526590d9b463c43e6731a2871db97019449608c3f72d500632159cca',
		'af85e1b5ccaaf1f95618e33d082a8ed5dcd0613679f64064a2f11722b00981b5'
	]);

	function hasAccess() {
		try {
			return Number(localStorage.getItem(storageKey)) > Date.now();
		} catch (_) {
			return false;
		}
	}

	function unlock() {
		document.documentElement.classList.remove('privacy-locked');
		document.body.classList.remove('privacy-gate-active');
		var gate = document.getElementById('privacy-gate');
		if (gate) gate.remove();
	}

	function normalizeAnswer(value) {
		return value
			.normalize('NFKC')
			.toLocaleLowerCase('en-US')
			.replace(/[^\p{L}\p{N}]+/gu, '');
	}

	async function hashText(value) {
		var bytes = new TextEncoder().encode(value);
		var digest = await crypto.subtle.digest('SHA-256', bytes);
		return Array.from(new Uint8Array(digest), function (byte) {
			return byte.toString(16).padStart(2, '0');
		}).join('');
	}

	function hashAnswer(value) {
		return hashText(normalizeAnswer(value));
	}

	function isOneEditAway(value, expected) {
		if (Math.abs(value.length - expected.length) > 1) return false;
		var i = 0;
		while (i < Math.min(value.length, expected.length) && value[i] === expected[i]) i++;
		if (value.length === expected.length) {
			return value.slice(i + 1) === expected.slice(i + 1) ||
				(value[i] === expected[i + 1] && value[i + 1] === expected[i] && value.slice(i + 2) === expected.slice(i + 2));
		}
		if (value.length > expected.length) return value.slice(i + 1) === expected.slice(i);
		return value.slice(i) === expected.slice(i + 1);
	}

	async function matchesAnswer(value, aliases, legacyHashes) {
		var normalized = normalizeAnswer(value).normalize('NFKD').replace(/\p{M}/gu, '');
		if (aliases.indexOf(normalized) !== -1) return true;
		// One insertion, deletion, substitution or adjacent swap in longer Latin names.
		// Keep short nicknames, abbreviations and Chinese names exact after normalization.
		if (/^[a-z]{5,40}$/.test(normalized) && aliases.some(function (alias) {
			return /^[a-z]{5,40}$/.test(alias) && isOneEditAway(normalized, alias);
		})) return true;
		try {
			return legacyHashes.has(await hashAnswer(value));
		} catch (_) {
			return false;
		}
	}

	function rememberAccess() {
		try {
			localStorage.setItem(storageKey, String(Date.now() + accessLifetime));
		} catch (_) {}
	}

	function renderGate() {
		if (hasAccess()) {
			unlock();
			return;
		}

		document.body.classList.add('privacy-gate-active');
		var gate = document.createElement('section');
		gate.id = 'privacy-gate';
		gate.setAttribute('role', 'dialog');
		gate.setAttribute('aria-modal', 'true');
		gate.setAttribute('aria-labelledby', 'privacy-gate-title');
		gate.innerHTML =
			'<div class="privacy-gate-card">' +
				'<p class="privacy-gate-kicker">Private portfolio</p>' +
				'<h1 id="privacy-gate-title">A small introduction.</h1>' +
				'<p class="privacy-gate-intro" id="privacy-gate-hint">This portfolio is intentionally shared with people who know me. Please answer two short questions to continue. A first name or nickname and a university short name are fine.</p>' +
				'<form id="privacy-gate-form" novalidate>' +
					'<label class="privacy-gate-field"><span>What name do you know me by? / 你如何称呼我？</span><input id="privacy-name" name="name" type="text" autocomplete="off" autocapitalize="words" spellcheck="false" aria-describedby="privacy-gate-hint" required /></label>' +
					'<label class="privacy-gate-field"><span>My undergraduate university? / 我的本科院校是？</span><input id="privacy-school" name="school" type="text" autocomplete="off" autocapitalize="words" spellcheck="false" aria-describedby="privacy-gate-hint" required /></label>' +
					'<button class="privacy-gate-submit" type="submit">Continue / 进入</button>' +
					'<p class="privacy-gate-error" id="privacy-gate-error" role="alert" aria-live="polite"></p>' +
				'</form>' +
				'<p class="privacy-gate-note">Your answers stay in this browser and are never submitted. Access is remembered on this device for 30 days.</p>' +
			'</div>';
		document.body.appendChild(gate);

		var form = document.getElementById('privacy-gate-form');
		var error = document.getElementById('privacy-gate-error');
		var submit = form.querySelector('button[type="submit"]');
		var nameInput = document.getElementById('privacy-name');
		var schoolInput = document.getElementById('privacy-school');
		nameInput.focus();

		form.addEventListener('submit', async function (event) {
			event.preventDefault();
			error.textContent = '';
			if (!nameInput.value.trim() || !schoolInput.value.trim()) {
				error.textContent = 'Please answer both questions. / 请填写两个答案。';
				return;
			}

			submit.disabled = true;
			try {
				var matches = await Promise.all([
					matchesAnswer(nameInput.value, nameAliases, acceptedNameHashes),
					matchesAnswer(schoolInput.value, schoolAliases, acceptedSchoolHashes)
				]);
				if (matches[0] && matches[1]) {
					rememberAccess();
					unlock();
					return;
				}
				error.textContent = 'Please try a familiar name and the university’s name or abbreviation. / 请尝试常用称呼和学校名称或简称。';
				(matches[0] ? schoolInput : nameInput).select();
			} catch (_) {
				error.textContent = 'Verification is unavailable in this browser. Please try a current browser.';
			} finally {
				submit.disabled = false;
			}
		});
	}

	async function initialize() {
		var fragment = location.hash;
		var invitation = /^#invite=([A-Za-z0-9_-]{43})$/.exec(fragment);
		// Fragments are not sent to the server; remove the code before further navigation.
		if (fragment.indexOf('#invite=') === 0) {
			try {
				history.replaceState(history.state, '', location.pathname + location.search);
			} catch (_) {}
		}
		if (hasAccess()) {
			unlock();
			return;
		}
		if (invitation) {
			try {
				if (await hashText(invitation[1]) === invitationHash) {
					rememberAccess();
					unlock();
					return;
				}
			} catch (_) {}
		}
		renderGate();
	}

	if (document.readyState === 'loading') {
		document.addEventListener('DOMContentLoaded', initialize, { once: true });
	} else {
		initialize();
	}
})();
