import React,{useEffect,useLayoutEffect,useRef,useState} from 'react';
import {continueRender,delayRender} from 'remotion';
import world from '../assets/world-v12.json';
import {citiesStage7 as cities,cubicRouteStage7 as cubic,motionEaseStage7 as motion,regionalPointStage7 as regional,routeTimingStage7 as timing,XY} from '../config/routes-stage7';
const clamp=(x:number)=>Math.max(0,Math.min(1,x));
const ease=(x:number)=>1-Math.pow(1-clamp(x),3);
const xy=(a:readonly number[]):XY=>[a[0],a[1]];
const hk=xy(cities['香港'].xy);
const hr=regional(cities['香港'].lon,cities['香港'].lat),sr=regional(cities['深圳'].lon,cities['深圳'].lat);
const routes=[...timing.routes.map(r=>({...r,key:r.name,curve:cubic(hk,xy(cities[r.name].xy)),inset:false})),
  {...timing.routes[0],key:'港深放大',curve:cubic(hr,sr),inset:true}];
type Measure={time:number;key:string;length:number;head:XY;headDistance:number;endNormal:XY;startTangent:XY;maxSampleStep:number;samples:XY[]};
type Label={x:number;y:number;anchor:'start'|'end'|'middle';hanging:boolean;box:number[]};
const unit=(x:number,y:number):XY=>{const n=Math.hypot(x,y)||1;return [x/n,y/n];};
function labelPosition(point:XY,direction:XY,name:string,font:number,occupied:number[][],bounds:number[],routePoints:XY[]):Label {
  let best:Label|undefined,bestCost=Infinity;
  for(const turn of [0,1,-1,2,-2,3,-3,4,-4,5,-5,6,-6,8,-8,10,-10,12]){
    const a=Math.atan2(direction[1],direction[0])+turn*Math.PI/12,nx=Math.cos(a),ny=Math.sin(a);
    const x=point[0]+20*nx,y=point[1]+20*ny,w=name.length*font,h=font*1.22;
    const anchor=nx<-.15?'end':nx>.15?'start':'middle',hanging=ny>.15;
    const box=[x-(anchor==='end'?w:anchor==='middle'?w/2:0),hanging?y:y-h,w,h+(name==='新加坡'?30:0)];
    const outside=Math.max(0,bounds[0]-box[0])+Math.max(0,bounds[1]-box[1])+Math.max(0,box[0]+box[2]-bounds[2])+Math.max(0,box[1]+box[3]-bounds[3]);
    const overlap=occupied.reduce((n,b)=>n+Math.max(0,Math.min(box[0]+box[2],b[0]+b[2])-Math.max(box[0],b[0]))*Math.max(0,Math.min(box[1]+box[3],b[1]+b[3])-Math.max(box[1],b[1])),0);
    const crossings=routePoints.filter(p=>p[0]>box[0]-4&&p[0]<box[0]+box[2]+4&&p[1]>box[1]-4&&p[1]<box[1]+box[3]+4).length;
    const cost=outside*10000+overlap*100+crossings*1000+Math.abs(turn);
    if(cost<bestCost){bestCost=cost;best={x,y,anchor,hanging,box};}
  }
  return best!;
}
export const GeographicNetworkStage7:React.FC<{time:number;sceneTime:number;qa?:boolean}>=({time,sceneTime,qa=false})=>{
  const refs=useRef<Record<string,SVGPathElement|null>>({});
  const [handle]=useState(()=>delayRender('Measure Stage7 single cubic SVG routes'));
  const [measured,setMeasured]=useState<Measure[]|null>(null);
  useLayoutEffect(()=>{
    const next=routes.map(r=>{
      const path=refs.current[r.key]!;const length=path.getTotalLength();
      const p=motion((time-r.start)/r.duration),headDistance=length*p;
      const head=path.getPointAtLength(headDistance),end=path.getPointAtLength(length),before=path.getPointAtLength(Math.max(0,length-1));
      const middle=path.getPointAtLength(length/2),start=path.getPointAtLength(0),after=path.getPointAtLength(Math.min(1,length));
      const tangent=unit(end.x-before.x,end.y-before.y);let normal:XY=[-tangent[1],tangent[0]];
      if(normal[0]*(end.x-middle.x)+normal[1]*(end.y-middle.y)<0)normal=[-normal[0],-normal[1]];
      let maxSampleStep=0,prev=path.getPointAtLength(0);const samples:XY[]=[[prev.x,prev.y]];
      for(let s=Math.min(4.9,length);;s=Math.min(length,s+4.9)){
        const point=path.getPointAtLength(s);samples.push([point.x,point.y]);maxSampleStep=Math.max(maxSampleStep,Math.hypot(point.x-prev.x,point.y-prev.y));prev=point;if(s>=length)break;
      }
      return {time,key:r.key,length,head:[head.x,head.y] as XY,headDistance,endNormal:normal,startTangent:unit(after.x-start.x,after.y-start.y),maxSampleStep,samples};
    });
    setMeasured(next);
  },[time]);
  useEffect(()=>{if(measured)continueRender(handle);},[handle,measured]);
  useEffect(()=>{
    if(qa&&measured&&measured[0].time===time)console.log('STAGE7_ROUTES:'+JSON.stringify({time,labels,routes:measured.map(({samples,...m},i)=>({...m,sampleCount:samples.length,d:routes[i].curve.d,start:routes[i].start,duration:routes[i].duration,main:routes[i].main,inset:routes[i].inset}))}));
  },[measured,time,qa]);
  const measurements=Object.fromEntries((measured||[]).map(m=>[m.key,m]));
  const occupied:number[][]=[];const labels:Record<string,Label>={};
  if(measured){
    const mainPoints=measured.slice(0,3).flatMap(m=>m.samples),regionalPoints=measured[3].samples;
    const outward=unit(-measured.slice(0,3).reduce((s,m)=>s+m.startTangent[0],0),-measured.slice(0,3).reduce((s,m)=>s+m.startTangent[1],0));
    labels['香港']=labelPosition(hk,outward,'香港',33,occupied,[150,310,1780,900],mainPoints);occupied.push(labels['香港'].box);
    for(const r of routes.filter(r=>!r.inset)){const m=measurements[r.key];labels[r.name]=labelPosition(r.curve.end,m.endNormal,r.name,33,occupied,[150,310,1780,900],mainPoints);occupied.push(labels[r.name].box);}
    const regionalOccupied:number[][]=[];
    labels['放大香港']=labelPosition(hr,unit(-measurements['港深放大'].startTangent[0],-measurements['港深放大'].startTangent[1]),'香港',25,regionalOccupied,[160,782,570,906],regionalPoints);regionalOccupied.push(labels['放大香港'].box);
    labels['放大深圳']=labelPosition(sr,measurements['港深放大'].endNormal,'深圳',25,regionalOccupied,[160,782,570,906],regionalPoints);
  }
  const drawRoute=(r:typeof routes[number])=>{
    const m=measurements[r.key],active=time>=r.start,p=motion((time-r.start)/r.duration),arrive=r.start+r.duration;
    const length=m?.length||0,head=m?.headDistance||0,tail=Math.min(60,head),width=r.main?2.4:1.6;
    const arrival=clamp((time-arrive)/timing.arrivalSeconds);
    return <g key={r.key} opacity={active?(r.main?1:.8):0}>
      {[[18,'#8DD8F4',.08],[8,'#B7E7F8',.18],[width,'#E8F8FF',r.main?.96:.72]].map(([w,c,o],i)=><path key={i} d={r.curve.d} fill="none" stroke={c as string} strokeWidth={w as number} opacity={o as number} strokeLinecap="round" strokeDasharray={`${length} ${length+1}`} strokeDashoffset={length-head}/>)}
      {p<1&&Array.from({length:12},(_,i)=>{
        const step=tail/12,start=Math.max(0,head-tail+i*step);
        return <path key={i} d={r.curve.d} fill="none" stroke="#F4EEE2" strokeWidth={width+.6} strokeLinecap="round" strokeDasharray={`${step} ${length+1}`} strokeDashoffset={-start} opacity={(i+.5)/12}/>;
      })}
      {m&&p<1&&<g><circle cx={m.head[0]} cy={m.head[1]} r={10} fill="#F4EEE2" opacity={.25}/><circle cx={m.head[0]} cy={m.head[1]} r={4.5} fill="#F4EEE2"/></g>}
      {time>=arrive&&arrival<1&&<circle cx={r.curve.end[0]} cy={r.curve.end[1]} r={8+18*arrival} fill="none" stroke="#F4EEE2" strokeWidth={2} opacity={.6*(1-arrival)}/>}
    </g>;
  };
  const drawCity=(name:string,point:XY,start:number,where:Label|undefined,font=33)=>{
    const arrival=clamp((time-start)/.4),text=ease((time-start-timing.labelDelay)/.25);
    return <g key={name} opacity={time>=start?1:0}>
      <circle cx={point[0]} cy={point[1]} r={5} fill="#F4EEE2"/>
      <circle cx={point[0]} cy={point[1]} r={.6+13.4*motion(arrival)} fill="none" stroke="#D7F1FC" strokeWidth={1} opacity={.5}/>
      {where&&<g opacity={text}><text x={where.x} y={where.y} textAnchor={where.anchor} dominantBaseline={where.hanging?'hanging':'auto'} fill="#F4EEE2" fontFamily="Noto Sans TC" fontSize={font} fontWeight={700}>{name==='放大香港'?'香港':name==='放大深圳'?'深圳':name}</text>
        {name==='新加坡'&&<text x={where.x} y={where.y+30} textAnchor={where.anchor} dominantBaseline={where.hanging?'hanging':'auto'} fill="#BBCDD5" fontFamily="Noto Sans TC" fontSize={21}>籌備中</text>}
      </g>}
    </g>;
  };
  const band=cubic(hk,[560,736]);
  return <svg width={1920} height={1080} style={{position:'absolute',inset:0,opacity:ease(sceneTime)}}>
    <defs><linearGradient id="regional-band-stage7" gradientUnits="userSpaceOnUse" x1={hk[0]} y1={hk[1]} x2={560} y2={736}><stop offset="0" stopColor="#8DD8F4" stopOpacity={.10}/><stop offset="1" stopColor="#8DD8F4" stopOpacity={.02}/></linearGradient></defs>
    <g visibility="hidden">{routes.map(r=><path key={r.key} ref={p=>{refs.current[r.key]=p;}} d={r.curve.d}/>)}</g>
    <g>{world.land_paths.map((d,i)=><path key={i} d={d} fill="#24556B" fillOpacity={.66} stroke="#4D8CA4" strokeWidth={.75} strokeOpacity={.5}/>)}</g>
    <g opacity={.12} stroke="#9CC8D7" strokeWidth={.8}>{[-30,0,30,60].map(lat=><path key={lat} d={`M140 ${320+(80-lat)*4.4}H1780`}/>)}{[0,60,120,180,240,300].map(lon=><path key={lon} d={`M${140+(lon+40)/360*1640} 320V892`}/>)}</g>
    {routes.filter(r=>!r.inset).map(drawRoute)}
    {drawCity('香港',hk,timing.hongKong,labels['香港'])}
    {timing.routes.map(r=>drawCity(r.name,xy(cities[r.name].xy),r.start+r.duration,labels[r.name]))}
    <g opacity={ease((time-timing.hongKong)/.4)}>
      <path d={band.d} fill="none" stroke="url(#regional-band-stage7)" strokeWidth={8} strokeLinecap="round"/>
      <rect x={150} y={736} width={430} height={180} rx={6} fill="#0B2E45" fillOpacity={.9} stroke="#416F84" strokeWidth={1}/>
      <text x={175} y={765} fill="#B8D1DC" fontSize={18} fontFamily="Noto Sans TC" letterSpacing={2}>香港—深圳 · 局部放大</text>
      {drawRoute(routes[3])}
      {drawCity('放大香港',hr,timing.hongKong,labels['放大香港'],25)}
      {drawCity('放大深圳',sr,timing.routes[0].start+timing.routes[0].duration,labels['放大深圳'],25)}
    </g>
  </svg>;
};
