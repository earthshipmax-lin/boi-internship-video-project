import React from 'react';
import official from '../assets/official-logo-v10.json';
import {progress} from '../theme';
type SvgNode={tag:string;attrs:Record<string,string>;children:SvgNode[]};
// Same fill-preserving draw/gradient structure as OfficialBrandV10; no HK edits.
const draw=(value:unknown,prefix:string,key?:React.Key):React.ReactNode=>{
 const node=value as SvgNode;
 const attrs={...node.attrs};
 if(attrs.fill==='url(#linear-gradient1)')attrs.fill=`url(#${prefix}-trunk-gradient)`;
 return React.createElement(node.tag,{...attrs,key},node.children.length?node.children.map((child,i)=>draw(child,prefix,i)):undefined);
};
const [left,top,right,bottom]=official.treeBounds;
export const USIntroTreeV5:React.FC<{seconds:number}>=({seconds})=>{
 const prefix='us-s1',pb=progress(seconds,0,.5),pt=progress(seconds,.4,.6),mid=(19.54+96.14)/2;
 return <svg data-intro-tree="official" width={88} height={88*(bottom-top)/(right-left)} viewBox={`${left} ${top} ${right-left} ${bottom-top}`} style={{position:'absolute',left:256,top:150}}>
  <defs>
   <linearGradient id={`${prefix}-gradient-template`} x1={1038.77} y1={-313.09} x2={1038.77} y2={-222.15} gradientTransform="translate(-1333.76 24.27) scale(.5)" gradientUnits="userSpaceOnUse">
    <stop offset={.51} stopColor="#007bc7"/><stop offset={.78} stopColor="#0057a9"/><stop offset={.82} stopColor="#0051a4"/>
   </linearGradient>
   <linearGradient id={`${prefix}-trunk-gradient`} x1={2782.26} y1={29.17} x2={2782.26} y2={120.1} href={`#${prefix}-gradient-template`}/>
   <clipPath id={`${prefix}-trunk-clip`}><rect x={0} y={84.37-(84.37-38.85)*pt} width={110} height={(84.37-38.85)*pt+.000001}/></clipPath>
  </defs>
  <g id={`${prefix}-trunk`} clipPath={`url(#${prefix}-trunk-clip)`}>{draw(official.trunk,prefix)}</g>
  <g id={`${prefix}-canopy`}>{official.ringCounts.map((_,ring)=>{
   const leaves=official.leaves.filter(leaf=>leaf.ring===ring),min=Math.min(...leaves.map(l=>l.delay)),max=Math.max(...leaves.map(l=>l.delay));
   return <g id={`${prefix}-ring-${ring+1}`} key={ring}>{leaves.map(leaf=>{
    const stagger=(leaf.delay-min)/(max-min||1)*.02;
    const p=progress(seconds,.8+ring*.12+stagger,.18),scale=.2+.8*p;
    return <g key={leaf.sourceIndex} transform={`translate(${leaf.x} ${leaf.y})`}><g opacity={p} transform={`scale(${scale})`}><g transform={`translate(${-leaf.x} ${-leaf.y})`}>{draw(leaf.node,prefix)}</g></g></g>;
   })}</g>;
  })}</g>
  <g id={`${prefix}-base`} transform={`translate(${mid} 0) scale(${pb} 1) translate(${-mid} 0)`}>{draw(official.base,prefix)}</g>
 </svg>;
};
