import React,{useEffect,useId,useLayoutEffect,useRef,useState} from 'react';
import {continueRender,delayRender} from 'remotion';
import world from '../assets/world-v12.json';
import regionalLand from '../assets/regional-land-stage10.json';
import {arrivalStage10,cityPointStage10,clampStage10 as clamp,driftStage10,greatCircleGeometryStage10,
  insetPointStage10,magnifierStage10 as lens,mapTextStage10,modulationStage10 as modulation,
  motionEaseStage10 as motion,routeTimingStage10 as defaultTiming} from '../config/routes-stage10';
import type {MapCityStage10,MapLocaleStage10} from '../config/routes-stage10';
const baseRoutes=defaultTiming.routes.map(r=>({...r,geometry:greatCircleGeometryStage10(r.name,r.amplitude)}));
const ease=(v:number)=>1-Math.pow(1-clamp(v),3);
type Metric={name:typeof baseRoutes[number]['name'];length:number;maxArcSampleStep:number;arcSampleCount:number};
type Placement={dx:number;dy:number;anchor:'end'|'start'};
const labelPlacement:Record<MapCityStage10,Placement>={
  '香港':{dx:-20,dy:20,anchor:'end'},'紐約':{dx:-20,dy:20,anchor:'end'},
  '新加坡':{dx:20,dy:20,anchor:'start'},'深圳':{dx:18,dy:-44,anchor:'start'},
};

export type RouteTimingV13={hongKong:number;shenzhen:{start:number;duration:number};routes:{name:'紐約'|'新加坡';start:number;duration:number;main:boolean;amplitude:number}[]};
export const GeographicNetworkV13:React.FC<{time:number;sceneTime:number;locale?:MapLocaleStage10;qa?:boolean;landFill?:string;landStroke?:string;customTiming?:RouteTimingV13}>=
({time,sceneTime,locale='yue',qa=false,landFill='#1E6B93',landStroke='#6FB4D2',customTiming})=>{
  const timing=customTiming??defaultTiming;
  const routes=timing.routes.map(r=>({...r,geometry:baseRoutes.find(b=>b.name===r.name)!.geometry}));
  const svg=useRef<SVGSVGElement>(null),paths=useRef<Record<string,SVGPathElement|null>>({});
  const labels=useRef<Record<string,SVGGElement|null>>({});
  const [metrics,setMetrics]=useState<Metric[]|null>(null),[measureHandle]=useState(()=>delayRender('Stage10 real SVG arc lengths'));
  const [placements,setPlacements]=useState(labelPlacement),[labelsReady,setLabelsReady]=useState(false);
  const [avoidance,setAvoidance]=useState<unknown[]>([]);
  const uid=useId().replace(/[^a-zA-Z0-9]/g,''),clipId=`stage10-lens-${uid}`;
  const pan=driftStage10(sceneTime),landOpacity=.64+.04*Math.sin(2*Math.PI*sceneTime/3),text=mapTextStage10[locale];
  const font=locale==='en'?'Geist':'Noto Sans TC';
  const sz=timing.shenzhen,szStart=sz.start+sz.duration;
  const lensOpacity=ease((time-timing.hongKong)/.3);
  const localHK=insetPointStage10('香港'),localSZ=insetPointStage10('深圳');
  const localD=`M${localHK[0]} ${localHK[1]}L${localSZ[0]} ${localSZ[1]}`;

  useLayoutEffect(()=>{const next=routes.map(r=>{
    const p=paths.current[r.name]!,length=p.getTotalLength();let prev=p.getPointAtLength(0),maxArcSampleStep=0,arcSampleCount=1;
    for(let s=Math.min(modulation.arcAuditStep,length);;s=Math.min(length,s+modulation.arcAuditStep)){
      const a=p.getPointAtLength(s);maxArcSampleStep=Math.max(maxArcSampleStep,Math.hypot(a.x-prev.x,a.y-prev.y));prev=a;arcSampleCount++;
      if(s>=length)break;
    }return {name:r.name,length,maxArcSampleStep,arcSampleCount};
  });setMetrics(next);},[]);
  // Honour the prescribed label quadrant, increasing its horizontal clearance
  // only when a true-font106% frame would cross either measured route. This
  // specifically avoids the HK caption crossing the Singapore trajectory.
  useEffect(()=>{if(!metrics)return;let cancelled=false;
    document.fonts.ready.then(()=>{if(cancelled)return;
      const next={...labelPlacement},checks:unknown[]=[];
      for(const name of ['香港','紐約','新加坡'] as const){
        const el=labels.current[name]!,bb=el.getBBox(),p=cityPointStage10(name),base=labelPlacement[name];
        const candidates=Array.from({length:12},(_,i)=>({...base,dx:base.dx+Math.sign(base.dx)*i*12}));
        const intersects=(candidate:Placement)=>{
          const x=p[0]+(bb.x+candidate.dx-placements[name].dx-p[0])*1.06,y=p[1]+(bb.y-p[1])*1.06;
          const width=bb.width*1.06,height=bb.height*1.06;
          const hits=routes.filter(r=>r.geometry.points.some(q=>q[0]>=x-8&&q[0]<=x+width+8&&q[1]>=y-8&&q[1]<=y+height+8)).map(r=>r.name);
          return {hits,safe:x-40>=40&&x+width<=1880&&y>=40&&y+height<=1040};
        };
        const chosen=candidates.find(c=>{const v=intersects(c);return !v.hits.length&&v.safe;})??base;
        next[name]=chosen;checks.push({name,prescribed:base,chosen,...intersects(chosen)});
      }
      setPlacements(next);setAvoidance(checks);setLabelsReady(true);
    });return()=>{cancelled=true;};
  },[metrics,locale]);
  useEffect(()=>{if(metrics&&labelsReady)continueRender(measureHandle);},[metrics,labelsReady,measureHandle]);

  useEffect(()=>{if(!qa||!metrics||!labelsReady)return;const handle=delayRender('Stage10 font/label audit'),root=svg.current!;let cancelled=false,a=0,b=0;
    document.fonts.ready.then(()=>{if(cancelled)return;a=requestAnimationFrame(()=>{b=requestAnimationFrame(()=>{if(cancelled)return;
      try{
        const rect=root.getBoundingClientRect();
        const labelMetrics=Object.entries(labels.current).filter((e):e is [string,SVGGElement]=>!!e[1]).map(([key,el])=>{
          const r=el.getBoundingClientRect(),bb=el.getBBox(),inset=key.startsWith('inset-'),name=key.replace('inset-','') as MapCityStage10;
          const p=inset?insetPointStage10(name as '香港'|'深圳'):cityPointStage10(name),start=name==='香港'?timing.hongKong:name==='深圳'?szStart:timing.routes.find(r=>r.name===name)!.start+timing.routes.find(r=>r.name===name)!.duration;
          return {key,name,inset,visible:time>=start,scale:arrivalStage10(time-start).scale,origin:[p[0]+(inset?0:pan),p[1]],
            bbox:{x:r.x-rect.x,y:r.y-rect.y,width:r.width,height:r.height},
            peakBBox:{x:p[0]+(bb.x-p[0])*1.06+(inset?0:pan),y:p[1]+(bb.y-p[1])*1.06,width:bb.width*1.06,height:bb.height*1.06}};
        });
        console.log('STAGE10_ROUTES:'+JSON.stringify({frame:Math.round(time*30),time,sceneTime,locale,rootRect:{width:rect.width,height:rect.height},
          layoutValid:Math.abs(rect.width-1920)<.01&&Math.abs(rect.height-1080)<.01,geographicDriftX:pan,landFill,landStroke,landOpacity,
          mainCities:['香港','紐約','新加坡'],mainShenzhenCount:0,labels:labelMetrics,labelRouteAvoidance:avoidance,
          magnifier:{center:lens.center,radius:lens.radius,magnification:lens.magnification,requestedMagnification:lens.requestedMagnification,
            title:text.lens,hongKong:localHK,shenzhen:localSZ,cityDistance:Math.hypot(localHK[0]-localSZ[0],localHK[1]-localSZ[1]),
            landSource:regionalLand.source,landPaths:regionalLand.land_paths.length},
          routes:routes.map((r,i)=>{const m=metrics[i],p=paths.current[r.name]!,h=p.getPointAtLength(m.length*motion((time-r.start)/r.duration)),start=p.getPointAtLength(0),end=p.getPointAtLength(m.length);return {
            ...r.geometry,start:r.start,duration:r.duration,length:m.length,maxArcSampleStep:m.maxArcSampleStep,
            maxSampleStep:Math.max(r.geometry.maxVertexStep,m.maxArcSampleStep),arcSampleCount:m.arcSampleCount,head:[h.x,h.y],origin:[start.x,start.y],endpoint:[end.x,end.y]};})}));
      }finally{continueRender(handle);}
    });});});return()=>{cancelled=true;cancelAnimationFrame(a);cancelAnimationFrame(b);continueRender(handle);};
  },[qa,metrics,labelsReady,avoidance,time,sceneTime,locale,pan,landOpacity,landFill,landStroke,szStart,text.lens,localHK,localSZ]);

  const city=(name:MapCityStage10,inset=false)=>{
    const p=inset?insetPointStage10(name as '香港'|'深圳'):cityPointStage10(name),pos=inset?labelPlacement[name]:placements[name];
    const route=timing.routes.find(r=>r.name===name),start=name==='香港'?timing.hongKong:name==='深圳'?szStart:route!.start+route!.duration;
    const elapsed=time-start,arrival=arrivalStage10(elapsed),key=`${inset?'inset-':''}${name}`;
    const dx=inset&&name==='香港'?-18:pos.dx,dy=inset&&name==='香港'?22:pos.dy;
    return <g key={key} data-stage10-city={key} opacity={elapsed>=0?1:0}>
      <circle cx={p[0]} cy={p[1]} r={arrival.radius} fill="#F4EEE2"/>
      {arrival.ringOpacity>0&&<circle cx={p[0]} cy={p[1]} r={arrival.ringRadius} fill="none" stroke="#F4EEE2" strokeWidth={1.6} opacity={arrival.ringOpacity}/>}
      <g ref={e=>{labels.current[key]=e;}} data-stage10-label={key} opacity={ease(elapsed/.12)} transform={`translate(${p[0]} ${p[1]}) scale(${arrival.scale}) translate(${-p[0]} ${-p[1]})`}>
        <text x={p[0]+dx} y={p[1]+dy} textAnchor={pos.anchor} dominantBaseline="hanging" fill="#F4EEE2" fontFamily={font} fontSize={inset?26:locale==='en'?31:33} fontWeight={700}>{text[name]}</text>
        {name==='新加坡'&&<text x={p[0]+dx} y={p[1]+dy+39} dominantBaseline="hanging" fill="#D8E5EA" fontFamily={font} fontSize={locale==='en'?18:21}>{text.preparing}</text>}
      </g>
    </g>;
  };
  const drawRoute=(r:typeof routes[number],i:number)=>{
    const m=metrics?.[i];if(!m)return null;const p=motion((time-r.start)/r.duration),length=m.length,d=r.geometry.d,distance=length*p,head=paths.current[r.name]?.getPointAtLength(distance),tail=Math.min(60,distance);
    return <g key={r.name} data-stage10-route={r.name} opacity={time>=r.start?1:0}>
      {[[18,.08,'#8DD8F4'],[8,.18,'#B7E7F8'],[r.main?2.4:1.6,r.main?.96:.72,'#E8F8FF']].map(([w,o,c],j)=><path key={j} d={d} fill="none" stroke={c as string} strokeWidth={w as number} opacity={o as number} strokeLinecap="round" strokeLinejoin="round" strokeDasharray={`${length} ${length+1}`} strokeDashoffset={length-distance}/>)}
      {p<1&&Array.from({length:12},(_,j)=>{const step=tail/12,start=Math.max(0,distance-tail+j*step);return <path key={j} d={d} fill="none" stroke="#F4EEE2" strokeWidth={2.8} strokeLinecap="round" strokeDasharray={`${step} ${length+1}`} strokeDashoffset={-start} opacity={(j+.5)/12}/>;})}
      {p<1&&head&&<><circle cx={head.x} cy={head.y} r={10} fill="#F4EEE2" opacity={.25}/><circle cx={head.x} cy={head.y} r={4.5} fill="#F4EEE2"/></>}
    </g>;
  };
  const hk=cityPointStage10('香港'),localProgress=motion((time-sz.start)/sz.duration),localLength=Math.hypot(localHK[0]-localSZ[0],localHK[1]-localSZ[1]);
  return <svg ref={svg} width={1920} height={1080} viewBox="0 0 1920 1080" style={{position:'absolute',inset:0,opacity:ease(sceneTime/.85)}}>
    <defs><clipPath id={clipId}><circle cx={lens.center[0]} cy={lens.center[1]} r={lens.radius}/></clipPath></defs>
    <g visibility="hidden">{routes.map(r=><path key={r.name} ref={p=>{paths.current[r.name]=p;}} d={r.geometry.d}/>)}</g>
    <g data-stage10-geography transform={`translate(${pan} 0)`}>
      <g>{world.land_paths.map((d,i)=><path key={i} d={d} fill={landFill} fillOpacity={landOpacity} stroke={landStroke} strokeWidth={.75} strokeOpacity={.5}/>)}</g>
      <g opacity={.12} stroke="#9CC8D7" strokeWidth={.8}>{[-30,0,30,60].map(lat=><path key={lat} d={`M140 ${320+(80-lat)*4.4}H1780`}/>)}{[0,60,120,180,240,300].map(lon=><path key={lon} d={`M${140+(lon+40)/360*1640} 320V892`}/>)}</g>
      {routes.map(drawRoute)}{(['香港','紐約','新加坡'] as const).map(name=>city(name))}
    </g>
    <g data-stage10-magnifier opacity={lensOpacity}>
      <path d={`M${hk[0]+pan-1} ${hk[1]}L${hk[0]+pan+1} ${hk[1]}L${lens.center[0]+13} ${lens.center[1]-lens.radius}L${lens.center[0]-13} ${lens.center[1]-lens.radius}Z`} fill="#8DD8F4" opacity={.10}/>
      <circle cx={lens.center[0]} cy={lens.center[1]} r={lens.radius} fill="#0F4668"/>
      <g clipPath={`url(#${clipId})`}>
        <g transform={`translate(${lens.center[0]} ${lens.center[1]}) scale(${lens.magnification}) translate(${-lens.regionalCenter[0]} ${-lens.regionalCenter[1]})`}>
          {regionalLand.land_paths.map((d,i)=><path key={i} d={d} fill={landFill} fillOpacity={.68} stroke={landStroke} strokeWidth={.75/lens.magnification} strokeOpacity={.65} fillRule="evenodd"/>)}
        </g>
        <path d={localD} fill="none" stroke="#E8F8FF" strokeWidth={1.6} strokeLinecap="round" strokeDasharray={`${localLength} ${localLength+1}`} strokeDashoffset={localLength*(1-localProgress)} opacity={time>=sz.start?.72:0}/>
      </g>
      <circle cx={lens.center[0]} cy={lens.center[1]} r={lens.radius} fill="none" stroke={landStroke} strokeWidth={1}/>
      <text x={lens.center[0]-lens.radius} y={lens.center[1]-lens.radius-10} dominantBaseline="auto" fill="#F4EEE2" opacity={.8} fontFamily={font} fontSize={14}>{text.lens}</text>
      {city('香港',true)}{city('深圳',true)}
    </g>
  </svg>;
};
