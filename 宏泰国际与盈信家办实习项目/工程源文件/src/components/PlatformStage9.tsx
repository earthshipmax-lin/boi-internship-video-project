import React,{useLayoutEffect,useRef} from 'react';
import {Img,staticFile} from 'remotion';
import official from '../assets/official-logo-v10.json';
import {epicV12Stage5} from '../config/hk-v12-stage5';
import {platformStage9 as p,platformGeometryStage9 as geometry,platformArcStage9 as arc} from '../config/platform-stage9';
const C=epicV12Stage5.colors;
const clamp=(n:number)=>Math.max(0,Math.min(1,n));
const ease=(n:number)=>1-Math.pow(1-clamp(n),4);
const reveal=(time:number,start:number,duration:number)=>ease((time-start)/duration);
type SvgNode={tag:string;attrs:Record<string,string>;children:SvgNode[]};
// Untouched native official-tree outlines in the one-colour negative variant.
// Chinese/English wordmark paths are deliberately not included.
const treeNode=(raw:unknown,key:React.Key):React.ReactNode=>{
 const node=raw as SvgNode;
 return React.createElement(node.tag,{...node.attrs,fill:C.paper,key},node.children.length?node.children.map((n,i)=>treeNode(n,i)):undefined);
};
const rectStyle=(r:{x:number;y:number;width:number;height:number}):React.CSSProperties=>({position:'absolute',left:r.x,top:r.y,width:r.width,height:r.height});
const text:React.CSSProperties={fontFamily:'Noto Sans TC',fontWeight:500,color:C.paper,textAlign:'center',whiteSpace:'nowrap'};
/** Parent owns background, corner brand/meta, captions and audio. */
export const PlatformStage9:React.FC<{sceneTime:number;qa?:boolean}>=({sceneTime,qa=false})=>{
 const root=useRef<HTMLDivElement>(null),a=p.animation;
 const titleProgress=reveal(sceneTime,0,.85);
 useLayoutEffect(()=>{
  if(!qa||!root.current)return;
  const boxes=Array.from(root.current.querySelectorAll('[data-stage9-platform]')).map(element=>{
   const e=element as HTMLElement|SVGGraphicsElement,rect=e.getBoundingClientRect();
   const r=root.current!.getBoundingClientRect(),scale=r.width/1920;
   return {role:e.getAttribute('data-stage9-platform'),id:e.getAttribute('data-id'),x:(rect.x-r.x)/scale,y:(rect.y-r.y)/scale,width:rect.width/scale,height:rect.height/scale,opacity:getComputedStyle(e).opacity};
  });
  console.log('STAGE9_PLATFORM:'+JSON.stringify({sceneTime,geometry,boxes}));
 },[sceneTime,qa]);
 return <div ref={root} style={{position:'absolute',inset:0}}>
  <div data-stage9-platform="title" style={{position:'absolute',left:128,top:242,fontFamily:'Noto Sans TC',fontWeight:800,letterSpacing:'-.055em',lineHeight:1.12,fontSize:116,color:C.paper,whiteSpace:'nowrap',opacity:titleProgress,transform:`translateY(${(1-titleProgress)*35}px)`}}>{p.title.text}</div>
  <svg width={1920} height={1080} style={{position:'absolute',inset:0,overflow:'visible'}}>
   {geometry.sectors.map((s,i)=>{
    const progress=reveal(sceneTime,a.arcStart+i*a.arcStagger,a.arcDuration),emphasisStart=(s.start+s.end)/2-10;
    return <g key={s.id} data-stage9-platform="sector" data-id={s.id}>
     <path data-stage9-platform="arc" data-id={s.id} d={arc(p.innerRadius,s.start,s.end)} fill="none" stroke={C.blue} strokeWidth={2} opacity={.78} strokeDasharray={s.arcLength} strokeDashoffset={s.arcLength*(1-progress)}/>
     <path data-stage9-platform="arc-emphasis" data-id={s.id} d={arc(p.innerRadius,emphasisStart,emphasisStart+20)} fill="none" stroke={C.paper} strokeWidth={2.6} opacity={.85*progress}/>
    </g>;
   })}
   {geometry.nodes.map(n=>{
    const progress=reveal(sceneTime,n.startTime,a.nodeDuration),dx=n.point.x-n.branchStart.x,dy=n.point.y-n.branchStart.y;
    return <g key={n.id} data-stage9-platform="branch-node" data-id={n.id} data-sector={n.sector}>
     <path data-stage9-platform="branch" data-id={n.id} d={`M${n.branchStart.x} ${n.branchStart.y} L${n.branchStart.x+dx*progress} ${n.branchStart.y+dy*progress}`} stroke={C.blue} strokeWidth={2} opacity={progress>0?.85:0} fill="none"/>
     <circle data-stage9-platform="node" data-id={n.id} cx={n.point.x} cy={n.point.y} r={8} fill={C.paper} opacity={reveal(sceneTime,n.startTime+.1,.2)}/>
    </g>;
   })}
   <path data-stage9-platform="evergreen-connector" d={`M${geometry.evergreenConnector.start.x} ${geometry.evergreenConnector.start.y} L${geometry.evergreenConnector.end.x} ${geometry.evergreenConnector.end.y}`} stroke={C.blue} strokeWidth={1.5} opacity={.8*reveal(sceneTime,a.evergreenStart,a.evergreenDuration)} fill="none"/>
  </svg>
  <svg data-stage9-platform="official-tree" viewBox={geometry.treeSourceViewBox} style={{...rectStyle(p.tree),opacity:reveal(sceneTime,a.treeStart,a.treeDuration)}} preserveAspectRatio="xMidYMid meet">
   {treeNode(official.trunk,'trunk')}{official.leaves.map(leaf=>treeNode(leaf.node,leaf.sourceIndex))}{treeNode(official.base,'base')}
  </svg>
  {p.sectors.map((s,i)=>{
   const opacity=reveal(sceneTime,a.arcStart+i*a.arcStagger+.12,.3);
   return <React.Fragment key={s.id}>
    <div data-stage9-platform="sector-title" data-id={s.id} style={{...rectStyle(s.titleRect),...text,fontWeight:700,fontSize:25,letterSpacing:'.5px',lineHeight:'32px',opacity}}>{s.title}</div>
    <div data-stage9-platform="sector-evidence" data-id={s.id} style={{...rectStyle(s.evidenceRect),...text,fontSize:s.evidenceFontSize,letterSpacing:0,lineHeight:s.id==='insurance'?'20px':'18px',opacity:.65*opacity}}>{s.evidence.map(line=><div key={line}>{line}</div>)}</div>
   </React.Fragment>;
  })}
  {geometry.nodes.map(n=><div key={n.id} data-stage9-platform="node-label" data-id={n.id} data-sector={n.sector} style={{...rectStyle(n.label),...text,fontSize:30,lineHeight:'38px',letterSpacing:2,opacity:reveal(sceneTime,n.startTime+.08,.22)}}>{n.text}</div>)}
  <div data-stage9-platform="evergreen-badge" style={{...rectStyle(p.evergreen),background:C.paper,borderRadius:'50%',opacity:reveal(sceneTime,a.evergreenStart,a.evergreenDuration)}}/>
  <Img data-stage9-platform="evergreen-logo" src={staticFile(p.evergreen.source)} style={{...rectStyle(p.evergreen.logo),objectFit:'contain',opacity:reveal(sceneTime,a.evergreenStart,a.evergreenDuration)}}/>
 </div>;
};
