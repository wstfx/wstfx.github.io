/* A small illustrative sampling walk. No project measurements are represented. */
(function (global, factory) {
  'use strict';
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else api.mount(global.document, global);
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  const NODES = {a:[278,489], b:[433,684], c:[255,766], d:[716,720], e:[557,544]};
  // These curves were checked inside the existing map. Reverse traversal uses
  // the same geometry, so changing the destination cannot wander off the page.
  const EDGES = [
    {a:'e',b:'b',controls:[[527,598],[438,602]]},
    {a:'e',b:'a',controls:[[486,479],[373,459]]},
    {a:'e',b:'d',controls:[[555,654],[622,697]]},
    {a:'a',b:'b',controls:[[350,520],[452,565]]},
    {a:'a',b:'c',controls:[[185,595],[202,694]]},
    {a:'b',b:'c',controls:[[380,710],[317,797]]},
    {a:'b',b:'d',controls:[[507,647],[640,682]]},
    {a:'c',b:'d',controls:[[350,864],[594,788]]}
  ];
  const DURATIONS = {rest:650, travel:2400, hold:900, fade:850};
  const clamp = (x, lo=0, hi=1) => Math.min(hi, Math.max(lo, x));
  const ease = t => t*t*(3-2*t);
  function orient(edge, from) {
    const to = edge.a === from ? edge.b : edge.a;
    const controls = edge.a === from ? edge.controls : [...edge.controls].reverse();
    const points = [NODES[from], ...controls, NODES[to]];
    return {from, to, points, distances:measureCurve(points), d:`M${points[0].join(' ')} C${points.slice(1).map(p=>p.join(' ')).join(' ')}`};
  }
  function pointAt(points, t) {
    const u = 1-t;
    return [0,1].map(axis => u*u*u*points[0][axis] + 3*u*u*t*points[1][axis] + 3*u*t*t*points[2][axis] + t*t*t*points[3][axis]);
  }
  function measureCurve(points) {
    const distances=[0];
    let previous=points[0];
    for (let i=1;i<=96;i++) {
      const point=pointAt(points,i/96);
      distances.push(distances[i-1]+Math.hypot(point[0]-previous[0],point[1]-previous[1]));
      previous=point;
    }
    return distances;
  }
  function pointAtDistance(points, progress, distances=measureCurve(points)) {
    // SVG dash offsets use arc length, not the cubic parameter. Match that
    // distance so the marker stays attached to the growing line on every curve.
    const target=clamp(progress)*distances[distances.length-1];
    let index=1;
    while(index<distances.length-1 && distances[index]<target) index++;
    const span=distances[index]-distances[index-1];
    const fraction=span ? (target-distances[index-1])/span : 0;
    return pointAt(points,(index-1+fraction)/(distances.length-1));
  }
  function createJourney(random=Math.random) {
    let current='e', previous=null, edge=null, phase='rest', elapsed=0, hops=0;
    function next() {
      let choices = EDGES.filter(e=>(e.a===current || e.b===current) && e.a!==previous && e.b!==previous);
      if (!choices.length) choices=EDGES.filter(e=>e.a===current || e.b===current);
      // Start with the familiar connection from the static artwork, then vary
      // destinations while excluding an immediate reversal of the last link.
      edge = orient(hops === 0 ? EDGES[0] : choices[Math.floor(clamp(random(),0,.999999)*choices.length)], current);
      phase='travel';
    }
    function advance(delta) {
      if (!Number.isFinite(delta) || delta < 0) return snapshot();
      elapsed += delta;
      while (elapsed >= DURATIONS[phase]) {
        elapsed -= DURATIONS[phase];
        if (phase==='rest') next();
        else if (phase==='travel') phase='hold';
        else if (phase==='hold') phase='fade';
        else { previous=current; current=edge.to; edge=null; phase='rest'; hops++; }
      }
      return snapshot();
    }
    function snapshot() {
      const progress = phase==='travel' ? ease(elapsed/DURATIONS.travel) : (edge ? 1 : 0);
      const arrived = phase==='hold' || phase==='fade';
      // Pass the emphasis forward with the marker, rather than retaining both
      // endpoints until the completed route disappears. Levels are driven by
      // the same clock as the path, so pause/resume freezes colour as well.
      const emphasis = Object.fromEntries(Object.keys(NODES).map(node=>[node,0]));
      if (phase==='travel') {
        emphasis[current]=1-ease(clamp(progress/.65));
        emphasis[edge.to]=ease(clamp((progress-.65)/.35));
      } else emphasis[arrived ? edge.to : current]=1;
      return {
        current, previous, next:edge?.to || null, phase, elapsed, hops,
        path:edge?.d || '', progress,
        opacity:edge ? .72*(phase==='fade' ? 1-ease(elapsed/DURATIONS.fade) : 1) : 0,
        marker:edge ? pointAtDistance(edge.points, progress, edge.distances) : NODES[current],
        markerOpacity:phase==='travel' ? clamp(elapsed/140) : 0,
        emphasis,
        highlighted:Object.keys(emphasis).filter(node=>emphasis[node]>0)
      };
    }
    return {advance, snapshot};
  }
  function allowed({ready,paused,asleep,active,reduced,hidden,compact}) {
    return ready && !paused && !asleep && active && !reduced && !hidden && !compact;
  }
  function createClock(journey, request, cancel, paint) {
    let running=false, frame=null, last=null;
    function tick(now) {
      frame=null;
      if (!running) return;
      const delta=last===null ? 0 : clamp(now-last,0,80);
      last=now;
      paint(journey.advance(delta));
      frame=request(tick);
    }
    return {
      setRunning(value) {
        if (running===value) return;
        running=value; last=null;
        if (running) frame=request(tick);
        else if (frame!==null) { cancel(frame); frame=null; }
      }
    };
  }
  function mount(document, window) {
    if (!document) return null;
    const svg=document.querySelector('.story-stage [data-test-journey]');
    const stage=document.querySelector('.story-stage');
    if (!svg || !stage) return null;
    const fallback=svg.querySelector('[data-journey-fallback]');
    const live=svg.querySelector('[data-journey-live]');
    const route=svg.querySelector('[data-journey-route]');
    const marker=svg.querySelector('[data-journey-marker]');
    const fragments=[...svg.querySelectorAll('[data-journey-node]')].map(group=>({
      node:group.getAttribute('data-journey-node'), shapes:[...group.querySelectorAll('[data-native-fill]')]
    }));
    if (!fallback || !live || !route || !marker || fragments.length===0) return null;
    const reduced=window.matchMedia('(prefers-reduced-motion: reduce)');
    const compact=window.matchMedia('(max-width:900px)');
    let enhanced=false, lastPath='';
    const journey=createJourney();
    const paint=state=>{
      if (!enhanced) {
        enhanced=true;
        fallback.setAttribute('visibility','hidden');
        live.setAttribute('visibility','visible');
      }
      if (state.path!==lastPath) { route.setAttribute('d',state.path || 'M557 544'); lastPath=state.path; }
      route.setAttribute('stroke-dashoffset',String(1-state.progress));
      route.setAttribute('opacity',String(state.opacity));
      marker.setAttribute('cx',state.marker[0].toFixed(2));
      marker.setAttribute('cy',state.marker[1].toFixed(2));
      marker.setAttribute('opacity',String(state.markerOpacity));
      fragments.forEach(fragment=>{
        const level=state.emphasis[fragment.node];
        if (level===fragment.lastLevel) return;
        fragment.shapes.forEach(shape=>{
          const idle=shape.getAttribute('data-idle-fill');
          const active=shape.getAttribute('data-active-fill');
          const channels=[1,3,5].map(i=>Math.round(parseInt(idle.slice(i,i+2),16)*(1-level)+parseInt(active.slice(i,i+2),16)*level));
          shape.setAttribute('fill',level===0 ? idle : level===1 ? active : `rgb(${channels.join(',')})`);
        });
        fragment.lastLevel=level;
      });
    };
    const clock=createClock(journey,window.requestAnimationFrame.bind(window),window.cancelAnimationFrame.bind(window),paint);
    const update=()=>clock.setRunning(allowed({
      ready:document.body.classList.contains('story-ready'),
      paused:document.body.classList.contains('motion-paused'),
      asleep:document.body.classList.contains('scene-asleep'),
      active:stage.dataset.scene==='2', reduced:reduced.matches,
      hidden:document.hidden, compact:compact.matches
    }));
    // story.js already decides the active chapter and off-screen state. Observe
    // those decisions rather than installing another scroll/geometry loop.
    const observer=new window.MutationObserver(update);
    observer.observe(document.body,{attributes:true,attributeFilter:['class']});
    observer.observe(stage,{attributes:true,attributeFilter:['data-scene']});
    document.addEventListener('visibilitychange',update);
    reduced.addEventListener('change',update);
    compact.addEventListener('change',update);
    window.addEventListener('pageshow',update);
    update();
    return {update,journey};
  }
  return {NODES,EDGES,DURATIONS,pointAt,pointAtDistance,createJourney,createClock,allowed,mount};
});
