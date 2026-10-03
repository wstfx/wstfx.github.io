// Exercise reading before motion is ready, scene selection, and motion preferences.
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
async function run({fonts='pending',reduced=false,stored=false,legacy=true,artScenes=[1,2,3,4]}={}) {
  let resolveFonts, rejectFonts;
  const fontPromise = new Promise((resolve,reject)=>{resolveFonts=resolve;rejectFonts=reject;});
  const body=element(), stage=element(), control=element(), fox=element(), world=element(), canvas=element();
  control.hidden=true;control.disabled=true;
  const stageLabel=element(),stageCount=element(),thought=element(),motionText=element();
  stage.querySelector=s=>({'.stage-label':stageLabel,'.stage-count':stageCount,'.stage-thought':thought}[s]);
  control.querySelector=()=>motionText;
  const nodes={'.story-stage':stage,'.travelling-fox':legacy?fox:null,'.story-canvas':canvas,'.world-drawing':legacy?world:null,'#route-ink':legacy?element():null,'.motion-toggle':control,'.story-pages':element()};
  const scenes=Array.from({length:5},element), characters=Array.from({length:5},element), links=Array.from({length:4},element);
  const chapterArt=artScenes.map(index=>({...element(),dataset:{artScene:String(index)}}));
  const events={},timers=new Map(),frames=[];
  const media=matches=>({matches,events:{},addEventListener(k,fn){this.events[k]=fn;}});
  const reducedMedia=media(reduced),compactMedia=media(false);
  let intersectionCallback;
  const ctx={console,document:{body,hidden:false,querySelector:s=>nodes[s],querySelectorAll:s=>({'.story-step':steps,'.story-waypoints a':links,'.world-scene':legacy?scenes:[],'.mascot-pose':legacy?characters:[],'.chapter-art':chapterArt}[s]||[]),addEventListener(k,fn){events[k]=fn;}},
    matchMedia:q=>q.includes('reduced')?reducedMedia:compactMedia,
    scrollY:0,innerHeight:900,localStorage:{getItem:()=>String(stored),setItem(){}},
    addEventListener(k,fn){events[k]=fn;},requestAnimationFrame:fn=>frames.push(fn),
    IntersectionObserver:class { constructor(callback){intersectionCallback=callback;} observe(){} },
    setTimeout(fn){timers.set(1,fn);return 1;},clearTimeout:id=>timers.delete(id)};
  const steps=Array.from({length:5},(_,i)=>({...element(),getBoundingClientRect:()=>({top:i*1000-ctx.scrollY})}));
  if(fonts!=='absent')ctx.document.fonts={ready:fontPromise};
  const flush=()=>{while(frames.length)frames.shift()();};
  ctx.window=ctx;
  vm.runInNewContext(source,ctx);flush();
  const visit=index=>{ctx.scrollY=index*1000+100;events.scroll();flush();};
  const inView=value=>intersectionCallback([{isIntersecting:value}]);
  return {ctx,body,stage,control,canvas,fox,world,scenes,chapterArt,links,timers,events,flush,visit,inView,reducedMedia,compactMedia,resolveFonts,rejectFonts};
}
function currentArtwork(run) { return run.chapterArt.filter(art=>art.classList.contains('is-current')).map(art=>Number(art.dataset.artScene)); }
(async()=>{
  const slow=await run();
  assert.equal(slow.control.hidden,true,'Control must not advertise an unready interaction');
  assert.equal(slow.control.disabled,true);
  assert.equal(slow.body.classList.contains('story-ready'),false);
  slow.ctx.scrollY=2100;slow.events.scroll();slow.flush();
  assert.equal(slow.stage.dataset.scene,'2','Native reading may move to another chapter before readiness');
  assert.deepEqual(currentArtwork(slow),[2],'The matching illustration must be readable before motion starts');
  assert.equal(slow.stage.classList.contains('has-chapter-art'),true);
  assert.match(slow.canvas.getAttribute('aria-label'),/selected orange sample/);
  slow.resolveFonts();await Promise.resolve();slow.flush();
  assert.equal(slow.body.classList.contains('story-ready'),true);
  assert.equal(slow.control.hidden,false);
  assert.equal(slow.control.disabled,false);
  assert.equal(slow.stage.dataset.scene,'2','Startup must keep the current reading position');
  assert.deepEqual(currentArtwork(slow),[2]);
  slow.control.events.click();slow.flush();
  assert.equal(slow.body.classList.contains('motion-paused'),true);
  assert.equal(slow.control.getAttribute('aria-label'),'Resume animations');
  slow.visit(4);
  assert.deepEqual(currentArtwork(slow),[4],'Pausing motion must not freeze chapter navigation');
  assert.equal(slow.links[3].getAttribute('aria-current'),'location');
  assert.equal(slow.links[1].getAttribute('aria-current'),undefined);
  slow.control.events.click();slow.flush();
  assert.equal(slow.body.classList.contains('motion-paused'),false);
  slow.visit(0);
  assert.deepEqual(currentArtwork(slow),[],'Returning to the opening must hide all chapter art');
  assert.equal(slow.stage.classList.contains('has-chapter-art'),false);

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

  const reordered=await run({fonts:'absent',legacy:false,artScenes:[4,2,1,3]});
  for(const index of [1,3,2,4]) {
    reordered.visit(index);
    assert.deepEqual(currentArtwork(reordered),[index],'Scene identity must follow its data attribute, not DOM order');
    assert.equal(reordered.stage.classList.contains('has-chapter-art'),true);
  }
  reordered.compactMedia.matches=true;reordered.compactMedia.events.change();reordered.flush();
  assert.equal(reordered.canvas.getAttribute('aria-label'),'An orange fox accompanies the story.');
  assert.deepEqual(currentArtwork(reordered),[4],'Responsive changes preserve the reading position');
  reordered.compactMedia.matches=false;reordered.compactMedia.events.change();reordered.flush();
  assert.match(reordered.canvas.getAttribute('aria-label'),/adult learners/);
  reordered.reducedMedia.matches=true;reordered.reducedMedia.events.change();reordered.flush();
  assert.equal(reordered.control.disabled,true);
  assert.equal(reordered.body.classList.contains('motion-paused'),true);
  reordered.visit(1);assert.deepEqual(currentArtwork(reordered),[1]);
  reordered.reducedMedia.matches=false;reordered.reducedMedia.events.change();reordered.flush();
  assert.equal(reordered.control.disabled,false);
  assert.equal(reordered.body.classList.contains('motion-paused'),false);
  reordered.inView(false);
  assert.equal(reordered.body.classList.contains('scene-asleep'),true);
  reordered.ctx.document.hidden=true;reordered.events.visibilitychange();
  reordered.inView(true);
  assert.equal(reordered.body.classList.contains('scene-asleep'),true,'A hidden tab stays asleep even when its stage intersects');
  reordered.ctx.document.hidden=false;reordered.events.visibilitychange();
  assert.equal(reordered.body.classList.contains('scene-asleep'),false);

  const incomplete=await run({fonts:'absent',artScenes:[1,2]});
  incomplete.visit(3);
  assert.equal(incomplete.stage.classList.contains('has-chapter-art'),false,'Missing art must retain the legacy fallback');
  assert.deepEqual(currentArtwork(incomplete),[]);
  assert.equal(incomplete.scenes[3].classList.contains('is-current'),true);
  console.log('PASS: delayed/failed/absent fonts, bounded startup, early reading, chapter identity, legacy fallback/removal, responsive descriptions, pause/resume, reduced motion, saved preference, offscreen/hidden states.');
})().catch(error=>{console.error(error);process.exitCode=1;});
