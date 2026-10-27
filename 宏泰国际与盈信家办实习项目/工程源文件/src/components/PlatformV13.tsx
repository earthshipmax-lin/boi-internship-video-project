import React from 'react';
import {Img,staticFile} from 'remotion';
import official from '../assets/official-logo-v10.json';
import {platformStage9 as p,platformGeometryStage9 as geometry,platformArcStage9 as arc} from '../config/platform-stage9';
import {getPlatformScreenCopyV13} from '../config/screen-copy-v13';
import {getScreenTextV12,type Locale} from '../config/locale-v12';
import {themeV13 as C,revealV13 as reveal} from '../config/theme-v13';
import {TextV13} from './FilmChromeV13';
type SvgNode={tag:string;attrs:Record<string,string>;children:SvgNode[]};
const treeNode=(raw:unknown,key:React.Key):React.ReactNode=>{const n=raw as SvgNode;return React.createElement(n.tag,{...n.attrs,fill:C.paper,key},n.children.length?n.children.map((v,i)=>treeNode(v,i)):undefined);};
const rect=(r:{x:number;y:number;width:number;height:number}):React.CSSProperties=>({left:r.x,top:r.y,width:r.width,height:r.height});
/** Pure picture: same geometry and timing as Stage9; all external copy localized. */
export const PlatformV13:React.FC<{sceneTime:number;locale:Locale}>=({sceneTime,locale})=>{
 const a=p.animation,copy=getPlatformScreenCopyV13(locale),titleP=reveal(sceneTime,0,.85);
 const sectors={insurance:copy.sectors[0],family:copy.sectors[1],wealth:copy.sectors[2]};
 const evidence={insurance:copy.insuranceEvidenceLines,wealth:copy.wealthEvidenceLines,family:[copy.familyEvidence]};
 return <>
  <TextV13 id="platform.title" locale={locale} size={116} minSize={58} style={{left:128,top:242,width:1570,height:130,fontWeight:800,lineHeight:1.12,letterSpacing:'-.055em',color:C.paper,opacity:titleP,transform:`translateY(${(1-titleP)*35}px)`}}>{getScreenTextV12(locale,'platformTitle')}</TextV13>
  <svg width={1920} height={1080} style={{position:'absolute',inset:0,overflow:'visible'}}>
   {geometry.sectors.map((s,i)=>{const progress=reveal(sceneTime,a.arcStart+i*a.arcStagger,a.arcDuration),emphasis=(s.start+s.end)/2-10;return <g key={s.id}>
    <path d={arc(p.innerRadius,s.start,s.end)} fill="none" stroke={C.blue} strokeWidth={2} opacity={.78} strokeDasharray={s.arcLength} strokeDashoffset={s.arcLength*(1-progress)}/><path d={arc(p.innerRadius,emphasis,emphasis+20)} fill="none" stroke={C.paper} strokeWidth={2.6} opacity={.85*progress}/>
   </g>;})}
   {geometry.nodes.map(n=>{const progress=reveal(sceneTime,n.startTime,a.nodeDuration),dx=n.point.x-n.branchStart.x,dy=n.point.y-n.branchStart.y;return <g key={n.id}>
    <path d={`M${n.branchStart.x} ${n.branchStart.y} L${n.branchStart.x+dx*progress} ${n.branchStart.y+dy*progress}`} stroke={C.blue} strokeWidth={2} opacity={progress>0?.85:0} fill="none"/><circle cx={n.point.x} cy={n.point.y} r={8} fill={C.paper} opacity={reveal(sceneTime,n.startTime+.1,.2)}/>
   </g>;})}
   <path d={`M${geometry.evergreenConnector.start.x} ${geometry.evergreenConnector.start.y} L${geometry.evergreenConnector.end.x} ${geometry.evergreenConnector.end.y}`} stroke={C.blue} strokeWidth={1.5} opacity={.8*reveal(sceneTime,a.evergreenStart,a.evergreenDuration)} fill="none"/>
  </svg>
  <svg data-v13-asset-language-exception="official-tree" viewBox={geometry.treeSourceViewBox} style={{position:'absolute',...rect(p.tree),opacity:reveal(sceneTime,a.treeStart,a.treeDuration)}} preserveAspectRatio="xMidYMid meet">{treeNode(official.trunk,'trunk')}{official.leaves.map(l=>treeNode(l.node,l.sourceIndex))}{treeNode(official.base,'base')}</svg>
  {p.sectors.map((s,i)=>{const opacity=reveal(sceneTime,a.arcStart+i*a.arcStagger+.12,.3);return <React.Fragment key={s.id}>
   <TextV13 id={`platform.sector.${s.id}`} locale={locale} size={25} minSize={11} style={{...rect(s.titleRect),textAlign:'center',fontWeight:700,letterSpacing:locale==='en'?0:.5,lineHeight:'32px',color:C.paper,opacity}}>{sectors[s.id]}</TextV13>
   <TextV13 id={`platform.evidence.${s.id}`} locale={locale} size={s.evidenceFontSize} minSize={11} lines={s.id==='family'?1:2} style={{...rect(s.evidenceRect),textAlign:'center',lineHeight:s.id==='insurance'?'20px':'18px',color:C.paper,opacity}}>{evidence[s.id].join('\n')}</TextV13>
  </React.Fragment>;})}
  {geometry.nodes.map((n,i)=><TextV13 key={n.id} id={`platform.node.${n.id}`} locale={locale} size={30} minSize={16} style={{...rect(n.label),textAlign:'center',lineHeight:'38px',letterSpacing:locale==='en'?0:2,color:C.paper,opacity:reveal(sceneTime,n.startTime+.08,.22)}}>{copy.nodes[i]}</TextV13>)}
  <div style={{position:'absolute',...rect(p.evergreen),background:C.paper,borderRadius:'50%',opacity:reveal(sceneTime,a.evergreenStart,a.evergreenDuration)}}/>
  <Img data-v13-asset-language-exception="official-evergreen" src={staticFile(p.evergreen.source)} style={{position:'absolute',...rect(p.evergreen.logo),objectFit:'contain',opacity:reveal(sceneTime,a.evergreenStart,a.evergreenDuration)}}/>
 </>;
};
