(() => {
  'use strict';
  document.querySelectorAll('[data-copy-prompt]').forEach(button => {
    const field = document.getElementById(button.dataset.copyPrompt);
    const status = button.nextElementSibling;
    if (!field) return;
    button.hidden = false;
    button.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(field.value);
        status.textContent = 'Prompt copied. Attach your chosen fox reference before generating.';
      } catch {
        field.focus(); field.select();
        status.textContent = 'Prompt selected. Use Copy in your browser to copy it.';
      }
    });
  });
})();
