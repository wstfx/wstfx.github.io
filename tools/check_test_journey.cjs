// Deterministic sequencing and scheduler checks for the illustrative map walk.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const crypto=require('node:crypto');
const {NODES,DURATIONS,pointAtDistance,createJourney,createClock,allowed,mount}=require('../assets/js/test-journey.js');

assert.ok(Math.abs(pointAtDistance([[0,0],[0,0],[10,0],[10,0]],.25)[0]-2.5)<.002,'Marker progress follows line length rather than an uneven cubic parameter');

const journey=createJourney(()=>.6);
assert.equal(journey.snapshot().phase,'rest');
assert.equal(journey.snapshot().current,'e');
assert.equal(journey.snapshot().opacity,0);
journey.advance(DURATIONS.rest);
let state=journey.snapshot();
assert.equal(state.phase,'travel');
assert.equal(state.next,'b','The first connection follows the original illustration');
assert.deepEqual(state.marker,NODES.e);
assert.deepEqual(state.highlighted,['e'],'Destination must remain dark before arrival');
journey.advance(DURATIONS.travel/2);
state=journey.snapshot();
assert.equal(state.progress,.5);
assert.notDeepEqual(state.marker,NODES.e);
assert.notDeepEqual(state.marker,NODES.b);
assert.deepEqual(state.highlighted,['e']);
journey.advance(DURATIONS.travel/2);
state=journey.snapshot();
assert.equal(state.phase,'hold');
assert.deepEqual(state.marker,NODES.b,'Marker and route must end at the actual sample center');
assert.deepEqual(state.highlighted,['e','b'],'Destination changes color only when reached');
assert.equal(state.markerOpacity,0,'Moving marker merges into the destination');
journey.advance(DURATIONS.hold+DURATIONS.fade/2);
assert.equal(journey.snapshot().opacity,.36,'The completed connection fades before the next hop');
journey.advance(DURATIONS.fade/2);
assert.equal(journey.snapshot().current,'b');
assert.equal(journey.snapshot().opacity,0);
assert.deepEqual(journey.snapshot().highlighted,['b']);
assert.equal(journey.snapshot().path,'');

// Several route choices are exercised with a fixed pseudo-random sequence.
let seed=41;
const random=()=>{seed=(seed*16807)%2147483647;return seed/2147483647;};
const varied=createJourney(random), destinations=new Set();
for(let hop=0;hop<30;hop++) {
  varied.advance(DURATIONS.rest);
  const departure=varied.snapshot();
  assert.equal(departure.phase,'travel');
  assert.notEqual(departure.current,departure.next);
  assert.notEqual(departure.previous,departure.next,'No immediate backtracking');
  destinations.add(departure.next);
  varied.advance(DURATIONS.travel);
  assert.deepEqual(varied.snapshot().marker,NODES[departure.next]);
  varied.advance(DURATIONS.hold+DURATIONS.fade);
  assert.equal(varied.snapshot().current,departure.next);
}
assert.equal(destinations.size,5,'The route should explore more than one fixed pair');
const beforeInvalid=varied.snapshot();
varied.advance(NaN);varied.advance(-5);
assert.deepEqual(varied.snapshot(),beforeInvalid);

// A paused scheduler schedules no frames and never charges the paused interval.
const frames=new Map();let nextFrame=0;
const request=callback=>{frames.set(++nextFrame,callback);return nextFrame;};
const cancel=id=>frames.delete(id);
const tick=timestamp=>{assert.equal(frames.size,1);const [id,callback]=frames.entries().next().value;frames.delete(id);callback(timestamp);};
const clockJourney=createJourney(()=>0), paints=[];
const clock=createClock(clockJourney,request,cancel,state=>paints.push(state));
clock.setRunning(true);tick(1000);tick(1060);
assert.equal(clockJourney.snapshot().elapsed,60);
clock.setRunning(false);
assert.equal(frames.size,0,'Pausing cancels the scheduled animation frame');
clock.setRunning(true);tick(90000);
assert.equal(clockJourney.snapshot().elapsed,60,'Resuming never jumps over paused time');
tick(90040);
assert.equal(clockJourney.snapshot().elapsed,100);
tick(99000);
assert.equal(clockJourney.snapshot().elapsed,180,'Unexpected suspended frame gaps are bounded');
clock.setRunning(false);

const open={ready:true,paused:false,asleep:false,active:true,reduced:false,hidden:false,compact:false};
assert.equal(allowed(open),true);
for(const key of ['ready','paused','asleep','active','reduced','hidden','compact']) {
  assert.equal(allowed({...open,[key]:!open[key]}),false,`${key} must gate animation`);
}

// Mount proves that guard changes actually reach the scheduler and that the
// original static route survives until the first allowed frame is painted.
const element=(attrs={})=>({attrs:{...attrs},setAttribute(k,v){this.attrs[k]=v;},getAttribute(k){return this.attrs[k];}});
const fallback=element(),live=element({visibility:'hidden'}),route=element(),marker=element();
const shape=element({'data-native-fill':'#FB8232','data-idle-fill':'#374535','data-active-fill':'#F47B20'});
const group={getAttribute:()=> 'e',querySelectorAll:()=>[shape]};
const svg={querySelector:s=>({'[data-journey-fallback]':fallback,'[data-journey-live]':live,'[data-journey-route]':route,'[data-journey-marker]':marker}[s]),querySelectorAll:()=>[group]};
const classes=new Set(),stage={dataset:{scene:'2'}},events={},media={};
let mutation;
const document={hidden:false,body:{classList:{contains:value=>classes.has(value)}},querySelector:s=>s==='.story-stage'?stage:svg,addEventListener:(k,fn)=>events[k]=fn};
const window={requestAnimationFrame:request,cancelAnimationFrame:cancel,
  matchMedia:q=>media[q]={matches:false,addEventListener(k,fn){this.change=fn;}},
  MutationObserver:class {constructor(callback){mutation=callback;}observe(){}},
  addEventListener:(k,fn)=>events[k]=fn};
const mounted=mount(document,window);
assert.equal(frames.size,0);
assert.equal(fallback.attrs.visibility,undefined,'Unready startup preserves the source example');
classes.add('story-ready');mutation();tick(0);
assert.equal(fallback.attrs.visibility,'hidden');
assert.equal(live.attrs.visibility,'visible');
classes.add('motion-paused');mutation();
assert.equal(frames.size,0);
classes.delete('motion-paused');mutation();tick(5000);
assert.equal(mounted.journey.snapshot().elapsed,0);
media['(prefers-reduced-motion: reduce)'].matches=true;
media['(prefers-reduced-motion: reduce)'].change();
assert.equal(frames.size,0);
media['(prefers-reduced-motion: reduce)'].matches=false;
media['(prefers-reduced-motion: reduce)'].change();tick(6000);
stage.dataset.scene='3';mutation();assert.equal(frames.size,0);
stage.dataset.scene='2';mutation();tick(7000);
document.hidden=true;events.visibilitychange();assert.equal(frames.size,0);
document.hidden=false;events.visibilitychange();tick(8000);
media['(max-width:900px)'].matches=true;
media['(max-width:900px)'].change();assert.equal(frames.size,0);

const root=path.resolve(__dirname,'..');
const source=fs.readFileSync(path.join(root,'assets/art/scene-test-overhead.svg'));
assert.equal(crypto.createHash('sha256').update(source).digest('hex'),'d6879050b49e47b1061c93a6a37248f5e1788def4c2f74be4bd91b632caec126','Editable source must remain unchanged');
const derivative=fs.readFileSync(path.join(root,'assets/art/scene-test-journey.svg'),'utf8');
assert.equal(derivative.includes('test-sample-route'),false,'Old CSS route animation must not run under the new route');
assert.equal(derivative.includes('test-sample-point'),false,'Old point pulsing must not compete with arrival colors');
assert.equal((derivative.match(/data-journey-node=/g)||[]).length,9);
assert.match(derivative,/data-journey-fallback/);
assert.match(derivative,/data-journey-live="" visibility="hidden"/);
console.log('PASS: endpoint arrival/color, varied non-backtracking routes, fade/rest phases, deterministic clock, pause without jumps, all activity guards, mount integration, original-source preservation.');
