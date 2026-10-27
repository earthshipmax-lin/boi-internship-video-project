import world from '../assets/world-v12.json';
import {arrivalStage9,driftStage9,motionEaseStage9} from './routes-stage9';
import type {XY} from './routes-stage7';

export type MapLocaleStage10='yue'|'en'|'zh-CN';
export type MapCityStage10=keyof typeof world.cities;
export const routeTimingStage10={sceneStart:864,sceneEnd:1141,hongKong:33.38,
  routes:[
    {name:'紐約',start:34.52,duration:1.05,main:true,amplitude:9},
    {name:'新加坡',start:35.60,duration:.85,main:false,amplitude:5},
  ],
  shenzhen:{start:34.16,duration:.45},
  peakScale:1.06,
} as const;
export const modulationStage10={baseSamples:120,cycles:2.5,maxVertexStep:4.8,arcAuditStep:4.8} as const;
export const magnifierStage10={center:[300,820] as XY,radius:190,magnification:48,
  // Source rounded coordinates: 12x gives only13.299px.48x gives53.197px.
  requestedMagnification:12,minimumCityDistance:40,
  regionalCenter:[(world.cities['香港'].xy[0]+world.cities['深圳'].xy[0])/2,
    (world.cities['香港'].xy[1]+world.cities['深圳'].xy[1])/2] as XY,
} as const;
export const mapTextStage10={
  yue:{'香港':'香港','深圳':'深圳','紐約':'紐約','新加坡':'新加坡',preparing:'籌備中',lens:'香港 — 深圳 · 48×'},
  'zh-CN':{'香港':'香港','深圳':'深圳','紐約':'纽约','新加坡':'新加坡',preparing:'筹备中',lens:'香港 — 深圳 · 48×'},
  en:{'香港':'Hong Kong','深圳':'Shenzhen','紐約':'New York','新加坡':'Singapore',preparing:'In preparation',lens:'Hong Kong — Shenzhen · 48×'},
} as const;
export const clampStage10=(v:number)=>Math.max(0,Math.min(1,v));
export const cityPointStage10=(name:MapCityStage10):XY=>[world.cities[name].xy[0],world.cities[name].xy[1]];
export const insetPointStage10=(name:'香港'|'深圳'):XY=>{
  const p=cityPointStage10(name),m=magnifierStage10;
  return [m.center[0]+(p[0]-m.regionalCenter[0])*m.magnification,m.center[1]+(p[1]-m.regionalCenter[1])*m.magnification];
};
export const projectStage10=(lon:number,lat:number):XY=>[140+(lon+40)/360*1640,320+(80-lat)*4.4];
const rad=(d:number)=>d*Math.PI/180;
const vector=(lon:number,lat:number):readonly[number,number,number]=>[Math.cos(rad(lat))*Math.cos(rad(lon)),Math.cos(rad(lat))*Math.sin(rad(lon)),Math.sin(rad(lat))];
const norm=(x:number,y:number):XY=>{const d=Math.hypot(x,y)||1;return [x/d,y/d];};
const distance=(a:XY,b:XY)=>Math.hypot(a[0]-b[0],a[1]-b[1]);
export const arrivalStage10=arrivalStage9;
export const driftStage10=driftStage9;
export const motionEaseStage10=motionEaseStage9;

export function greatCircleGeometryStage10(name:'紐約'|'新加坡',amplitude:number){
  const a=world.cities['香港'],b=world.cities[name],va=vector(a.lon,a.lat),vb=vector(b.lon,b.lat);
  const dot=Math.max(-1,Math.min(1,va.reduce((s,v,i)=>s+v*vb[i],0))),angle=Math.acos(dot),sine=Math.sin(angle);
  const basePoints:XY[]=[],lonlat:XY[]=[];let previousLon=a.lon;
  for(let i=0;i<120;i++){
    const t=i/119,wa=Math.sin((1-t)*angle)/sine,wb=Math.sin(t*angle)/sine;
    const v=va.map((value,j)=>value*wa+vb[j]*wb);
    let lon=Math.atan2(v[1],v[0])*180/Math.PI;
    while(lon-previousLon>180)lon-=360;while(lon-previousLon< -180)lon+=360;
    previousLon=lon;
    const lat=Math.atan2(v[2],Math.hypot(v[0],v[1]))*180/Math.PI;
    lonlat.push([lon,lat]);basePoints.push(projectStage10(lon,lat));
  }
  // Share the actual existing city/land coordinate rounding at both endpoints.
  basePoints[0]=cityPointStage10('香港');basePoints[119]=cityPointStage10(name);
  const modulated=basePoints.map((p,i):XY=>{
    const before=basePoints[Math.max(0,i-1)],after=basePoints[Math.min(119,i+1)],t=i/119;
    const tangent=norm(after[0]-before[0],after[1]-before[1]);
    const off=amplitude*Math.sin(Math.PI*t)*Math.sin(2*Math.PI*2.5*t);
    return [p[0]-tangent[1]*off,p[1]+tangent[0]*off];
  });modulated[0]=basePoints[0];modulated[119]=basePoints[119];
  const points:XY[]=[modulated[0]];
  for(let i=1;i<modulated.length;i++){
    const a=modulated[i-1],b=modulated[i],n=Math.max(1,Math.ceil(distance(a,b)/modulationStage10.maxVertexStep));
    for(let j=1;j<=n;j++)points.push([a[0]+(b[0]-a[0])*j/n,a[1]+(b[1]-a[1])*j/n]);
  }
  return {name,angleRadians:angle,shortArc:angle<=Math.PI,basePoints,lonlat,points,
    baseSampleCount:120,amplitude,
    maxVertexStep:Math.max(...points.slice(1).map((p,i)=>distance(p,points[i]))),
    maxLongitudeJump:Math.max(...lonlat.slice(1).map((p,i)=>Math.abs(p[0]-lonlat[i][0]))),
    minLongitude:Math.min(...lonlat.map(p=>p[0])),maxLongitude:Math.max(...lonlat.map(p=>p[0])),
    maxLatitude:Math.max(...lonlat.map(p=>p[1])),
    d:points.map((p,i)=>`${i?'L':'M'}${p[0]} ${p[1]}`).join(' ')};
}
