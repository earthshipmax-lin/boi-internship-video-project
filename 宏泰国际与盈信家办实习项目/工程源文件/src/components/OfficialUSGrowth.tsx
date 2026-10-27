import React from 'react';
import official from '../assets/official-logo-v10.json';
import placement from '../config/official-logo-v10.json';
import logoGrowth from '../config/us-logo-growth.json';
import {progress,theme} from '../theme';
type SvgNode={tag:string;attrs:Record<string,string>;children:SvgNode[]};
const draw=(value:unknown,prefix:string,key?:React.Key):React.ReactNode=>{
 const node=value as SvgNode;
 const attrs={...node.attrs};
 if(attrs.fill==='url(#linear-gradient1)')attrs.fill=`url(#${prefix}-trunk-gradient)`;
 return React.createElement(node.tag,{...attrs,key},node.children.length?node.children.map((child,i)=>draw(child,prefix,i)):undefined);
};
const {scale,translateX,translateY}=placement;
const sourceTransform=`translate(${translateX} ${translateY}) scale(${scale})`;
// Original source paths and colours are retained. Only their visibility and
// local scale animate; leaf position never relies on CSS transform-origin.
export const OfficialUSGrowth:React.FC<{seconds:number;prefix?:string}>=({seconds,prefix='us'})=>{
 const T=logoGrowth.us,pb=progress(seconds,T.baseStart,T.baseDur),pt=progress(seconds,T.trunkStart,T.trunkDur),pw=progress(seconds,T.wordStart,T.wordDur);
 const mid=(19.54+96.14)/2;
 return <svg width={1920} height={1080} style={{position:'absolute',inset:0}}>
  <defs>
   <linearGradient id={`${prefix}-gradient-template`} x1={1038.77} y1={-313.09} x2={1038.77} y2={-222.15} gradientTransform="translate(-1333.76 24.27) scale(.5)" gradientUnits="userSpaceOnUse">
    <stop offset={.51} stopColor="#007bc7"/><stop offset={.78} stopColor="#0057a9"/><stop offset={.82} stopColor="#0051a4"/>
   </linearGradient>
   <linearGradient id={`${prefix}-trunk-gradient`} x1={2782.26} y1={29.17} x2={2782.26} y2={120.1} href={`#${prefix}-gradient-template`}/>
   <clipPath id={`${prefix}-trunk-clip`}><rect x={0} y={84.37-(84.37-38.85)*pt} width={110} height={(84.37-38.85)*pt+.000001}/></clipPath>
   {[['cn',132.03,299.19,22,35],['en',115.43,321.4,64,13]].map(([id,left,right,y,h])=>{
    const width=(Number(right)-Number(left)+1)*pw;
    return <clipPath id={`${prefix}-${id}`} key={id}><rect x={(Number(left)+Number(right)-width)/2} width={width} y={Number(y)} height={Number(h)}/></clipPath>;
   })}
  </defs>
  <g transform={sourceTransform}>
   <g id="trunk" clipPath={`url(#${prefix}-trunk-clip)`}>{draw(official.trunk,prefix)}</g>
   <g id="canopy">{official.ringCounts.map((_,ring)=><g id={`ring-${ring+1}`} key={ring}>
    {official.leaves.filter(leaf=>leaf.ring===ring).map(leaf=>{
     const ringLeaves=official.leaves.filter(item=>item.ring===ring);
     const earliest=Math.min(...ringLeaves.map(item=>item.delay));
     const latest=Math.max(...ringLeaves.map(item=>item.delay));
     // Preserve the source angular sequence within each ring, packed into 40 ms.
     // Ring cadence and each leaf's 340 ms growth remain independently legible.
     const stagger=(leaf.delay-earliest)/(latest-earliest||1)*T.leafStagger;
     const delay=T.leafStart+ring*T.ringGap+stagger;
     const p=progress(seconds,delay,T.leafDur),size=.2+.8*p;
     return <g key={leaf.sourceIndex} transform={`translate(${leaf.x} ${leaf.y}) rotate(0)`}>
      <g transform={`scale(${size})`} opacity={p}><g transform={`translate(${-leaf.x} ${-leaf.y})`}>{draw(leaf.node,prefix)}</g></g>
     </g>;
    })}
   </g>)}</g>
   <g id="base" transform={`translate(${mid} 0) scale(${pb} 1) translate(${-mid} 0)`}>{draw(official.base,prefix)}</g>
   <g opacity={pw}>
    <g clipPath={`url(#${prefix}-cn)`}>{official.chinese.map((glyph,i)=>draw(glyph.node,prefix,i))}</g>
    <g clipPath={`url(#${prefix}-en)`}>{official.english.map((glyph,i)=>draw(glyph,prefix,i))}</g>
   </g>
  </g>
 </svg>;
};
