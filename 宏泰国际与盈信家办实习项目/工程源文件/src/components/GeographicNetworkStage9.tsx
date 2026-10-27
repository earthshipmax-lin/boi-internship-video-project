import React,{useEffect,useLayoutEffect,useRef,useState} from 'react';
import {continueRender,delayRender} from 'remotion';
import world from '../assets/world-v12.json';
import {arrivalStage9,cityPointStage9,CityNameStage9,clampStage9 as clamp,cubicRouteStage9,
  driftStage9,geographicBackgroundStage9 as bg,labelsStage9,modulationStage9 as modulation,
  motionEaseStage9 as motion,routeTimingStage9 as timing} from '../config/routes-stage9';
import {XY} from '../config/routes-stage7';

const ease=(v:number)=>1-Math.pow(1-clamp(v),3);
const hk=cityPointStage9('香港');
const routes=timing.routes.map(r=>({...r,curve:cubicRouteStage9(hk,cityPointStage9(r.name))}));
type Geometry={name:typeof routes[number]['name'];baseLength:number;basePoints:XY[];points:XY[];
  d:string;maxVertexStep:number;maxNormalOffset:number};
type Metric={name:Geometry['name'];length:number;maxArcSampleStep:number;arcSampleCount:number};
const distance=(a:XY,b:XY)=>Math.hypot(a[0]-b[0],a[1]-b[1]);
const unit=(x:number,y:number):XY=>{const n=Math.hypot(x,y)||1;return [x/n,y/n];};
const point=(p:DOMPoint):XY=>[p.x,p.y];

function modulatedGeometry(route:typeof routes[number],path:SVGPathElement):Geometry {
  const length=path.getTotalLength(),basePoints:XY[]=[],modulated:XY[]=[];
  let maxNormalOffset=0;
  for(let i=0;i<modulation.baseSamples;i++){
    const t=i/(modulation.baseSamples-1),s=length*t,p=path.getPointAtLength(s);
    const a=path.getPointAtLength(Math.max(0,s-.5)),b=path.getPointAtLength(Math.min(length,s+.5));
    const tangent=unit(b.x-a.x,b.y-a.y),normal:XY=[-tangent[1],tangent[0]];
    const offset=route.amplitude*Math.sin(Math.PI*t)*Math.sin(2*Math.PI*modulation.cycles*t);
    maxNormalOffset=Math.max(maxNormalOffset,Math.abs(offset));
    basePoints.push([p.x,p.y]);modulated.push([p.x+normal[0]*offset,p.y+normal[1]*offset]);
  }
  // Keep the exact 120 modulated vertices, subdividing their straight spans.
  // This preserves the requested formula without stretching NY's ~800px line
  // into 119 spans longer than the stated 5px maximum.
  modulated[0]=hk;modulated[modulated.length-1]=route.curve.end;
  const points:XY[]=[modulated[0]];
  for(let i=1;i<modulated.length;i++){
    const a=modulated[i-1],b=modulated[i],count=Math.max(1,Math.ceil(distance(a,b)/modulation.maxVertexStep));
    for(let j=1;j<=count;j++)points.push([a[0]+(b[0]-a[0])*j/count,a[1]+(b[1]-a[1])*j/count]);
  }
  const maxVertexStep=Math.max(...points.slice(1).map((p,i)=>distance(p,points[i])));
  return {name:route.name,baseLength:length,basePoints,points,maxVertexStep,maxNormalOffset,
    d:points.map((p,i)=>`${i?'L':'M'}${p[0]} ${p[1]}`).join(' ')};
}

export const GeographicNetworkStage9:React.FC<{time:number;sceneTime:number;qa?:boolean}>=({time,sceneTime,qa=false})=>{
  const svg=useRef<SVGSVGElement>(null),baseRefs=useRef<Record<string,SVGPathElement|null>>({});
  const modRefs=useRef<Record<string,SVGPathElement|null>>({}),labelRefs=useRef<Record<string,SVGGElement|null>>({});
  const [geometry,setGeometry]=useState<Geometry[]|null>(null),[metrics,setMetrics]=useState<Metric[]|null>(null);
  const [measureHandle]=useState(()=>delayRender('Measure Stage9 modulated geographic routes'));
  const pan=driftStage9(sceneTime),landOpacity=.64+.04*Math.sin(2*Math.PI*sceneTime/bg.opacityPeriod);

  useLayoutEffect(()=>{setGeometry(routes.map(r=>modulatedGeometry(r,baseRefs.current[r.name]!)));},[]);
  useLayoutEffect(()=>{if(!geometry)return;
    const next=geometry.map(g=>{
      const path=modRefs.current[g.name]!,length=path.getTotalLength();
      let previous=path.getPointAtLength(0),maxArcSampleStep=0,arcSampleCount=1;
      for(let s=Math.min(modulation.arcAuditStep,length);;s=Math.min(length,s+modulation.arcAuditStep)){
        const p=path.getPointAtLength(s);maxArcSampleStep=Math.max(maxArcSampleStep,Math.hypot(p.x-previous.x,p.y-previous.y));
        previous=p;arcSampleCount++;if(s>=length)break;
      }
      return {name:g.name,length,maxArcSampleStep,arcSampleCount};
    });setMetrics(next);
  },[geometry]);
  useEffect(()=>{if(metrics)continueRender(measureHandle);},[metrics,measureHandle]);

  useEffect(()=>{
    if(!qa||!geometry||!metrics)return;
    const handle=delayRender('Stage9 route labels after layout'),root=svg.current!;
    let cancelled=false,raf1=0,raf2=0;
    document.fonts.ready.then(()=>{if(cancelled)return;raf1=requestAnimationFrame(()=>{raf2=requestAnimationFrame(()=>{
      if(cancelled)return;
      try{
        const rootRect=root.getBoundingClientRect();
        const labels=(Object.keys(labelsStage9) as CityNameStage9[]).map(name=>{
          const element=labelRefs.current[name]!,r=element.getBoundingClientRect(),local=element.getBBox(),p=cityPointStage9(name);
          const start=name==='香港'?timing.hongKong:timing.routes.find(r=>r.name===name)!.start+timing.routes.find(r=>r.name===name)!.duration;
          const arrival=arrivalStage9(time-start),leader=labelsStage9[name].leader;
          return {name,start,visible:time>=start,scale:arrival.scale,peakScale:timing.peakScale,radius:arrival.radius,
            origin:[p[0]+pan,p[1]],bbox:{x:r.x-rootRect.x,y:r.y-rootRect.y,width:r.width,height:r.height},
            // getBBox excludes the group's own pulse transform, giving a real
            // font box from which the worst-case 106% canvas box is derived.
            peakBBox:{x:p[0]+(local.x-p[0])*timing.peakScale+pan,y:p[1]+(local.y-p[1])*timing.peakScale,
              width:local.width*timing.peakScale,height:local.height*timing.peakScale},
            leaderLength:leader?Math.hypot(leader[0],leader[1]):0};
        });
        const routeMetrics=geometry.map((g,i)=>{
          const r=routes[i],m=metrics[i],path=modRefs.current[g.name]!,p=motion((time-r.start)/r.duration);
          return {key:g.name,name:g.name,inset:false,time,start:r.start,duration:r.duration,main:r.main,
            d:g.d,baseCubicD:r.curve.d,baseLength:g.baseLength,length:m.length,baseSampleCount:modulation.baseSamples,
            sampleCount:g.points.length,maxVertexStep:g.maxVertexStep,maxArcSampleStep:m.maxArcSampleStep,
            maxSampleStep:Math.max(g.maxVertexStep,m.maxArcSampleStep),arcSampleCount:m.arcSampleCount,
            amplitude:r.amplitude,maxNormalOffset:g.maxNormalOffset,head:point(path.getPointAtLength(m.length*p)),
            origin:point(path.getPointAtLength(0)),endpoint:point(path.getPointAtLength(m.length))};
        });
        console.log('STAGE9_ROUTES:'+JSON.stringify({frame:Math.round(time*30),time,sceneTime,
          rootRect:{x:rootRect.x,y:rootRect.y,width:rootRect.width,height:rootRect.height},
          layoutValid:Math.abs(rootRect.width-1920)<.01&&Math.abs(rootRect.height-1080)<.01,
          geographicDriftX:pan,landOpacity,localInsetCount:0,labels,routes:routeMetrics}));
      }finally{continueRender(handle);}
    });});});
    return()=>{cancelled=true;cancelAnimationFrame(raf1);cancelAnimationFrame(raf2);continueRender(handle);};
  },[geometry,metrics,pan,landOpacity,time,sceneTime,qa]);

  const drawRoute=(r:typeof routes[number],i:number)=>{
    const g=geometry?.[i],m=metrics?.[i];if(!g||!m)return null;
    const active=time>=r.start,p=motion((time-r.start)/r.duration),headDistance=m.length*p;
    const head=modRefs.current[r.name]?.getPointAtLength(headDistance),tail=Math.min(60,headDistance);
    return <g key={r.name} data-stage9-route={r.name} opacity={active?1:0}>
      {[[18,.08,'#8DD8F4'],[8,.18,'#B7E7F8'],[2.2,.92,'#E8F8FF']].map(([width,opacity,color],layer)=><path key={layer} d={g.d}
        fill="none" stroke={color as string} strokeWidth={width as number} opacity={opacity as number} strokeLinecap="round" strokeLinejoin="round"
        strokeDasharray={`${m.length} ${m.length+1}`} strokeDashoffset={m.length-headDistance}/>)}
      {p<1&&Array.from({length:12},(_,j)=>{
        const step=tail/12,start=Math.max(0,headDistance-tail+j*step);
        return <path key={j} d={g.d} fill="none" stroke="#F4EEE2" strokeWidth={2.8} strokeLinecap="round" strokeLinejoin="round"
          strokeDasharray={`${step} ${m.length+1}`} strokeDashoffset={-start} opacity={(j+.5)/12}/>;
      })}
      {p<1&&head&&<><circle cx={head.x} cy={head.y} r={10} fill="#F4EEE2" opacity={.25}/><circle cx={head.x} cy={head.y} r={4.5} fill="#F4EEE2"/></>}
    </g>;
  };
  const drawCity=(name:CityNameStage9)=>{
    const p=cityPointStage9(name),label=labelsStage9[name];
    const route=timing.routes.find(r=>r.name===name),start=route?route.start+route.duration:timing.hongKong;
    const elapsed=time-start,arrival=arrivalStage9(elapsed),labelOpacity=ease(elapsed/.12);
    return <g key={name} data-stage9-city={name} opacity={elapsed>=0?1:0}>
      {label.leader&&<path d={`M${p[0]} ${p[1]}l${label.leader[0]} ${label.leader[1]}`} fill="none" stroke="#A3CFE0" strokeWidth={1.2} opacity={.7}/>}
      <circle cx={p[0]} cy={p[1]} r={arrival.radius} fill="#F4EEE2"/>
      {arrival.ringOpacity>0&&<circle cx={p[0]} cy={p[1]} r={arrival.ringRadius} fill="none" stroke="#F4EEE2" strokeWidth={1.6} opacity={arrival.ringOpacity}/>}
      <g ref={e=>{labelRefs.current[name]=e;}} data-stage9-label={name} opacity={labelOpacity}
        transform={`translate(${p[0]} ${p[1]}) scale(${arrival.scale}) translate(${-p[0]} ${-p[1]})`}>
        <text x={p[0]+label.dx} y={p[1]+label.dy} textAnchor={label.anchor} dominantBaseline="hanging" fill="#F4EEE2" fontFamily="Noto Sans TC" fontSize={33} fontWeight={700}>{name}</text>
        {name==='新加坡'&&<text x={p[0]+label.dx} y={p[1]+label.dy+39} textAnchor={label.anchor} dominantBaseline="hanging" fill="#BBCDD5" fontFamily="Noto Sans TC" fontSize={21}>籌備中</text>}
      </g>
    </g>;
  };
  return <svg ref={svg} width={1920} height={1080} viewBox="0 0 1920 1080" style={{position:'absolute',inset:0,opacity:ease(sceneTime/.85)}}>
    <g visibility="hidden">{routes.map(r=><path key={`base-${r.name}`} ref={p=>{baseRefs.current[r.name]=p;}} d={r.curve.d}/>)}
      {geometry?.map(g=><path key={`mod-${g.name}`} ref={p=>{modRefs.current[g.name]=p;}} d={g.d}/>)}
    </g>
    {/* Every geographical layer shares one affine translation. The parent's
        annual rings stay fixed; city markers cannot drift off their land. */}
    <g data-stage9-geography transform={`translate(${pan} 0)`}>
      <g>{world.land_paths.map((d,i)=><path key={i} d={d} fill="#24556B" fillOpacity={landOpacity} stroke="#4D8CA4" strokeWidth={.75} strokeOpacity={.5}/>)}</g>
      <g opacity={.12} stroke="#9CC8D7" strokeWidth={.8}>
        {[-30,0,30,60].map(lat=><path key={lat} d={`M140 ${320+(80-lat)*4.4}H1780`}/>)}
        {[0,60,120,180,240,300].map(lon=><path key={lon} d={`M${140+(lon+40)/360*1640} 320V892`}/>)}
      </g>
      {routes.map(drawRoute)}
      {(Object.keys(labelsStage9) as CityNameStage9[]).map(drawCity)}
    </g>
  </svg>;
};
