import React from 'react';
import {AbsoluteFill,Img,staticFile,useCurrentFrame} from 'remotion';
import {theme,clamp01} from '../theme';
import people from '../config/us-team-v1.json';
import '../fonts';
export const US_TEAM_FRAMES=240;
export const USTeamV1:React.FC<{qa?:boolean}>=({qa=false})=>{
 const f=useCurrentFrame();
 const exit=1-clamp01((f-(US_TEAM_FRAMES-10))/9);
 const title=theme.ease(clamp01(f/11))*exit;
 if(qa)console.log('US_AUDIT:'+JSON.stringify({frame:f,count:people.length,playbackRate:1,people:people.map((p,i)=>({name:p.name,x:584+(i%3)*264,y:208+Math.floor(i/3)*376+(i%3===1?16:0),w:224,h:280,scale:p.scale,enterFrame:i*3,nameFrame:i*3+6,stableFrame:i*3+11,exitFrame:230}))}));
 return <AbsoluteFill style={{background:theme.color.paper,color:theme.color.ink}}>
  <div style={{position:'absolute',top:96,left:144,right:144,textAlign:'center',fontFamily:theme.font.latinSerif,fontSize:43,fontWeight:400,lineHeight:'56px',opacity:title}}>Meet the people behind our US team.</div>
  {people.map((p,i)=>{
   const enter=theme.ease(clamp01((f-i*3)/(30*.35)));
   const name=theme.ease(clamp01((f-i*3-6)/(30*.35)))*.85;
   const x=584+(i%3)*264,y=208+Math.floor(i/3)*376+(i%3===1?16:0);
   const lines:Record<string,string[]>={
    'david-wang':['Formerly at WFG'],
    'lily-ku':['Formerly at New York Life','and MassMutual'],
    'noah-cheung':['Engineering background'],
    'catherine-luo':['Formerly at Deutsche Bank','and RBS'],
    'vivian-mau':['Formerly at WFG and PFA'],
    'crystal-wan':['Formerly at PFA'],
   };
   return <div key={p.slug} style={{position:'absolute',left:x,top:y,transform:`translateY(${12*(1-enter)}px)`}}>
    {i===0&&<div style={{position:'absolute',top:-24,width:224,fontFamily:theme.font.latin,fontSize:12,lineHeight:'16px',letterSpacing:'.06em',opacity:name*exit,color:theme.color.muted}}>US GENERAL MANAGER</div>}
    <Img src={staticFile(`portraits/us-v1/${p.slug}.png`)} style={{display:'block',width:224,height:280,opacity:enter*exit}}/>
    <div style={{opacity:name*exit}}>
     <div style={{fontFamily:theme.font.latinSerif,fontSize:24,lineHeight:'32px',marginTop:8,whiteSpace:'nowrap'}}>{p.name}</div>
     <div style={{fontFamily:theme.font.latin,fontSize:14,lineHeight:'18px',letterSpacing:'.06em',color:theme.color.muted,marginTop:4}}>{lines[p.slug].map((line,j)=><div key={j}>{line}</div>)}</div>
    </div>
   </div>;
  })}
  <div style={{position:'absolute',left:144,bottom:40,fontFamily:theme.font.latin,fontSize:12,letterSpacing:'.06em',color:theme.color.muted,opacity:.55}}>INTERNAL VISUAL STUDY / NOT FOR DISTRIBUTION</div>
 </AbsoluteFill>;
};
