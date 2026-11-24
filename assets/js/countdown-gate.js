(function () {
	'use strict';

	var passwordDigest = '627518de54e525e43f2b4ea8634fce363ff76f2e7c171579d8e43ace1d6cc1dc';
	var storageKey = 'zebang-countdown-access-v1';
	var accessLifetime = 30 * 24 * 60 * 60 * 1000;
	var localHost = ['localhost', '127.0.0.1', '[::1]'].indexOf(location.hostname) !== -1;
	var localFile = location.protocol === 'file:';

	function unlock() {
		document.documentElement.classList.remove('countdown-password-locked');
		var gate = document.getElementById('countdown-password-gate');
		if (gate) gate.remove();
	}

	function hasRememberedAccess() {
		try {
			return Number(localStorage.getItem(storageKey)) > Date.now();
		} catch (_) {
			return false;
		}
	}

	function rememberAccess() {
		try {
			localStorage.setItem(storageKey, String(Date.now() + accessLifetime));
		} catch (_) {}
	}

	async function digest(value) {
		var bytes = new TextEncoder().encode(value);
		var result = await crypto.subtle.digest('SHA-256', bytes);
		return Array.from(new Uint8Array(result), function (byte) {
			return byte.toString(16).padStart(2, '0');
		}).join('');
	}

	function renderGate() {
		var gate = document.createElement('section');
		gate.id = 'countdown-password-gate';
		gate.setAttribute('role', 'dialog');
		gate.setAttribute('aria-modal', 'true');
		gate.setAttribute('aria-labelledby', 'countdown-password-title');
		gate.innerHTML =
			'<div class="countdown-password-card">' +
				'<p class="countdown-password-kicker">Private writing</p>' +
				'<h1 id="countdown-password-title">Before the Countdown Ends</h1>' +
				'<p id="countdown-password-hint">Enter the password to read this essay.</p>' +
				'<form id="countdown-password-form" novalidate>' +
					'<label for="countdown-password-input">Password</label>' +
					'<input id="countdown-password-input" name="password" type="password" autocomplete="current-password" aria-describedby="countdown-password-error" required>' +
					'<button type="submit">Continue</button>' +
					'<p class="countdown-password-error" id="countdown-password-error" role="alert" aria-live="polite"></p>' +
				'</form>' +
				'<p class="countdown-password-note">This device will remember access for 30 days.</p>' +
			'</div>';
		document.body.appendChild(gate);

		var form = document.getElementById('countdown-password-form');
		var input = document.getElementById('countdown-password-input');
		var error = document.getElementById('countdown-password-error');
		var submit = form.querySelector('button[type="submit"]');
		input.focus();

		form.addEventListener('submit', async function (event) {
			event.preventDefault();
			error.textContent = '';
			if (!input.value) {
				error.textContent = 'Enter the password to continue.';
				input.focus();
				return;
			}

			submit.disabled = true;
			try {
				if (await digest(input.value) === passwordDigest) {
					rememberAccess();
					unlock();
					return;
				}
				error.textContent = 'That password did not match. Please try again.';
				input.select();
			} catch (_) {
				error.textContent = 'Password verification is unavailable. Please try a current browser.';
			} finally {
				submit.disabled = false;
			}
		});
	}

	if (localHost || localFile || hasRememberedAccess()) {
		unlock();
		return;
	}

	document.body.classList.add('countdown-password-active');
	renderGate();
}());
