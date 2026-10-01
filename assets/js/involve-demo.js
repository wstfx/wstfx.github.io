(() => {
  const root = document.querySelector('.involve-demo');
  if (!root) return;
  const $ = selector => root.querySelector(selector);
  // Placeholder lesson content; replace with the original course materials later.
  const questions = {
    prompt: {prompt: 'You want an AI coding agent to build a simple to-do page. Which request gives it the clearest starting point?', options: ['Make me a great app', 'Build a to-do page where I can add tasks, mark them done, and delete them. Explain how to open and test it.', 'Use as many advanced technologies as possible'], correct: 1, explanation: 'Describe the desired behavior and how you will check it. Concrete requirements give you and the agent a shared target.'},
    verify: {prompt: 'The agent says your to-do page is finished. What should you do next?', options: ['Assume it works because the agent says so', 'Ask for more features immediately', 'Open it and try adding, completing, and deleting a task; report any mismatch'], correct: 2, explanation: 'Try the expected actions yourself. Describe what you did, what you expected, and what happened so the agent can help you improve it.'}
  };
  let released = false;
  let answer = null;
  const current = () => questions[$('#demo-question').value];
  function mode(name) {
    root.querySelectorAll('[data-mode]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.mode === name)));
    root.querySelectorAll('[data-panel]').forEach(p => p.hidden = p.dataset.panel !== name);
  }
  function populate() {
    const q = current();
    ['#design-prompt', '#teach-prompt', '#student-prompt'].forEach(s => $(s).textContent = q.prompt);
    $('#answer-options').replaceChildren();
    q.options.forEach((text, i) => {
      const label = document.createElement('label');
      const input = document.createElement('input');
      input.type = 'radio'; input.name = 'answer'; input.value = String(i); input.required = true;
      label.append(input, document.createTextNode(text)); $('#answer-options').append(label);
    });
    $('#response-bars').replaceChildren();
    q.options.forEach((text, i) => {
      const row = document.createElement('div'); row.className = 'result-row';
      const count = answer === i ? 1 : 0;
      const label = document.createElement('span'); label.textContent = `${text} — ${count} response${count === 1 ? '' : 's'}`;
      const meter = document.createElement('meter'); meter.min = 0; meter.max = 1; meter.value = count; meter.setAttribute('aria-label', text);
      row.append(label, meter); $('#response-bars').append(row);
    });
  }
  function reset() {
    released = false; answer = null; $('#demo-question').disabled = false; $('#demo-question').value = 'prompt';
    $('#distribute').disabled = false; $('#distribution-state').textContent = 'Draft · not visible to students';
    $('#student-wait').hidden = false; $('#student-answer').hidden = true; $('#student-submitted').hidden = true;
    $('#response-count').textContent = '0 of 1 demo student responded';
    $('#assessment-note').textContent = 'Distribute the question and submit a student answer to see the result.';
    $('#demo-announcement').textContent = 'Start with the teacher’s Design view.';
    mode('design'); populate();
  }
  root.querySelectorAll('[data-mode]').forEach(b => b.addEventListener('click', () => mode(b.dataset.mode)));
  $('#to-teach').addEventListener('click', () => {mode('teach'); $('#distribute').focus();});
  $('#to-assess').addEventListener('click', () => {mode('assess'); $('[data-mode="assess"]').focus();});
  $('#demo-question').addEventListener('change', populate);
  $('#demo-reset').addEventListener('click', reset);
  $('#distribute').addEventListener('click', () => {
    if (released) return;
    released = true; $('#demo-question').disabled = true; $('#distribute').disabled = true;
    $('#distribution-state').textContent = 'Distributed · visible to the student';
    $('#student-wait').hidden = true; $('#student-answer').hidden = false;
    $('#demo-announcement').textContent = 'Question distributed. Choose an answer in the student panel.';
    $('#answer-options input').focus();
  });
  $('#student-answer').addEventListener('submit', event => {
    event.preventDefault();
    if (!released || answer !== null) return;
    const selected = $('#student-answer input:checked'); if (!selected) return;
    answer = Number(selected.value); const q = current();
    $('#student-answer').hidden = true; $('#student-submitted').hidden = false;
    $('#submitted-answer').textContent = `You chose: ${q.options[answer]}`;
    $('#response-count').textContent = '1 of 1 demo student responded';
    $('#assessment-note').textContent = `${answer === q.correct ? 'Correct response.' : 'This response suggests a concept to revisit.'} ${q.explanation}`;
    populate(); $('#demo-announcement').textContent = 'Answer submitted. Open Assess to inspect the response.'; $('#to-assess').focus();
  });
  reset();
})();
