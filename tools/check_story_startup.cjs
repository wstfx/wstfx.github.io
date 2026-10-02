// Exercise startup with delayed/failed fonts and a chapter visited before motion starts.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync(require('node:path').join(__dirname, '../assets/js/story.js'), 'utf8');
function element() {
  const values = new Set(), attrs = new Map();
  return { dataset:{}, style:{}, hidden:false, disabled:false, textContent:'',
    classList:{add:v=>values.add(v),contains:v=>values.has(v),toggle(v,on){if(on)values.add(v);else values.delete(v);}},
    setAttribute:(k,v)=>attrs.set(k,v),removeAttribute:k=>attrs.delete(k),getAttribute:k=>attrs.get(k),
    events:{}, addEventListener(k,fn){this.events[k]=fn;}, getBoundingClientRect:()=>({top:0,bottom:150}) };
}
async function run({fonts='pending',reduced=false,stored=false}={}) {
  let resolveFonts, rejectFonts;
  const fontPromise = new Promise((resolve,reject)=>{resolveFonts=resolve;rejectFonts=reject;});
  const body=element(), stage=element(), control=element(), fox=element(), world=element(), canvas=element();
  control.hidden=true;control.disabled=true;
  const stageLabel=element(),stageCount=element(),thought=element(),motionText=element();
  stage.querySelector=s=>({'.stage-label':stageLabel,'.stage-count':stageCount,'.stage-thought':thought}[s]);
  control.querySelector=()=>motionText;
  const nodes={'.story-stage':stage,'.travelling-fox':fox,'.story-canvas':canvas,'.world-drawing':world,'#route-ink':element(),'.motion-toggle':control,'.story-pages':element()};
  const scenes=Array.from({length:5},element), characters=Array.from({length:5},element), links=Array.from({length:4},element);
  const events={},timers=new Map(),frames=[];
  const ctx={console,document:{body,hidden:false,querySelector:s=>nodes[s],querySelectorAll:s=>({'.story-step':steps,'.story-waypoints a':links,'.world-scene':scenes,'.mascot-pose':characters}[s]),addEventListener(k,fn){events[k]=fn;}},
    matchMedia:q=>({matches:q.includes('reduced')?reduced:false,addEventListener(){}}),
    scrollY:0,innerHeight:900,localStorage:{getItem:()=>String(stored),setItem(){}},
    addEventListener(k,fn){events[k]=fn;},requestAnimationFrame:fn=>frames.push(fn),
    setTimeout(fn){timers.set(1,fn);return 1;},clearTimeout:id=>timers.delete(id)};
  const steps=Array.from({length:5},(_,i)=>({...element(),getBoundingClientRect:()=>({top:i*1000-ctx.scrollY})}));
  if(fonts!=='absent')ctx.document.fonts={ready:fontPromise};
  const flush=()=>{while(frames.length)frames.shift()();};
  ctx.window=ctx;
  vm.runInNewContext(source,ctx);flush();
  return {ctx,body,stage,control,fox,scenes,links,timers,events,flush,resolveFonts,rejectFonts};
}
(async()=>{
  const slow=await run();
  assert.equal(slow.control.hidden,true,'Control must not advertise an unready interaction');
  assert.equal(slow.control.disabled,true);
  assert.equal(slow.body.classList.contains('story-ready'),false);
  slow.ctx.scrollY=2100;slow.events.scroll();slow.flush();
  assert.equal(slow.stage.dataset.scene,'2','Native reading may move to another chapter before readiness');
  slow.resolveFonts();await Promise.resolve();slow.flush();
  assert.equal(slow.body.classList.contains('story-ready'),true);
  assert.equal(slow.control.hidden,false);
  assert.equal(slow.control.disabled,false);
  assert.equal(slow.stage.dataset.scene,'2','Startup must keep the current reading position');
  slow.control.events.click();slow.flush();
  assert.equal(slow.body.classList.contains('motion-paused'),true);
  assert.equal(slow.control.getAttribute('aria-label'),'Resume animations');

  const stalled=await run();stalled.timers.get(1)();stalled.flush();
  assert.equal(stalled.body.classList.contains('story-ready'),true,'Slow fonts must not block enhancement indefinitely');
  stalled.resolveFonts();await Promise.resolve();stalled.flush();
  assert.equal(stalled.control.hidden,false);

  const failed=await run();failed.rejectFonts(new Error('font load failed'));await Promise.resolve();failed.flush();
  assert.equal(failed.body.classList.contains('story-ready'),true);
  const reduced=await run({fonts:'absent',reduced:true});
  assert.equal(reduced.control.disabled,true);
  assert.equal(reduced.body.classList.contains('motion-paused'),true);
  const stored=await run({fonts:'absent',stored:true});
  assert.equal(stored.body.classList.contains('motion-paused'),true);
  assert.equal(stored.control.getAttribute('aria-pressed'),'true');
  console.log('PASS: delayed/failed/absent fonts, bounded startup, early chapter navigation, pause, reduced motion, saved preference.');
})().catch(error=>{console.error(error);process.exitCode=1;});
