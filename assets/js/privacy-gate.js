(function () {
	'use strict';

	var storageKey = 'zebang-portfolio-access-v1';
	var accessLifetime = 30 * 24 * 60 * 60 * 1000;
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

	async function hashAnswer(value) {
		var bytes = new TextEncoder().encode(normalizeAnswer(value));
		var digest = await crypto.subtle.digest('SHA-256', bytes);
		return Array.from(new Uint8Array(digest), function (byte) {
			return byte.toString(16).padStart(2, '0');
		}).join('');
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
				'<p class="privacy-gate-intro">This portfolio is intentionally shared with people who know me. Please answer two short questions to continue.</p>' +
				'<form id="privacy-gate-form" novalidate>' +
					'<label class="privacy-gate-field"><span>What name do you know me by? / 你如何称呼我？</span><input id="privacy-name" name="name" type="text" autocomplete="off" autocapitalize="words" spellcheck="false" required /></label>' +
					'<label class="privacy-gate-field"><span>My undergraduate university? / 我的本科院校是？</span><input id="privacy-school" name="school" type="text" autocomplete="off" autocapitalize="words" spellcheck="false" required /></label>' +
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
				var hashes = await Promise.all([hashAnswer(nameInput.value), hashAnswer(schoolInput.value)]);
				if (acceptedNameHashes.has(hashes[0]) && acceptedSchoolHashes.has(hashes[1])) {
					try {
						localStorage.setItem(storageKey, String(Date.now() + accessLifetime));
					} catch (_) {}
					unlock();
					return;
				}
				error.textContent = 'Those details did not match. Please check the spelling and try again. / 信息未匹配，请检查后重试。';
				schoolInput.select();
			} catch (_) {
				error.textContent = 'Verification is unavailable in this browser. Please try a current browser.';
			} finally {
				submit.disabled = false;
			}
		});
	}

	if (hasAccess()) {
		document.documentElement.classList.remove('privacy-locked');
	} else if (document.readyState === 'loading') {
		document.addEventListener('DOMContentLoaded', renderGate, { once: true });
	} else {
		renderGate();
	}
})();
