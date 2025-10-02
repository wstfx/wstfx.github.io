// copy-id.js: Handles click-to-copy for .copy-id elements and shows a toast
(function(){
  function showToast(text){
    var toast = document.getElementById('copy-toast');
    if(!toast) return;
    toast.textContent = text;
    toast.classList.add('show');
    clearTimeout(toast._hideTimeout);
    toast._hideTimeout = setTimeout(function(){ toast.classList.remove('show'); }, 2200);
  }

  function copyText(text){
    if(navigator.clipboard && navigator.clipboard.writeText){
      return navigator.clipboard.writeText(text);
    }
    var ta = document.createElement('textarea');
    ta.value = text; ta.style.position='fixed'; ta.style.left='-9999px';
    document.body.appendChild(ta); ta.select();
    try{ document.execCommand('copy'); document.body.removeChild(ta); return Promise.resolve(); }
    catch(e){ document.body.removeChild(ta); return Promise.reject(e); }
  }

  document.addEventListener('click', function(e){
    var el = e.target.closest && e.target.closest('.copy-id');
    if(!el) return;
    e.preventDefault();
    var data = el.getAttribute('data-copy') || '';
    if(!data) return;
    copyText(data).then(function(){
      showToast('Copied: ' + data);
    }).catch(function(){
      showToast('Copy failed — please select and copy manually.');
    });
  });
})();

