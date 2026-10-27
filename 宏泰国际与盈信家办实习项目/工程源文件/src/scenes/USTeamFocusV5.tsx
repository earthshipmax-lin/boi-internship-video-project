import React from 'react';
import {AbsoluteFill, Img, staticFile, useCurrentFrame} from 'remotion';
import {theme,clamp01} from '../theme';
import people from '../config/us-team-v1.json';
import achievements from '../config/us-team-achievements-v5.json';
import '../fonts';
const ranges=[[12,48],[48,84],[84,120],[120,156],[156,192],[192,222]];
const E=(f:number,duration:number)=>theme.ease(clamp01(f/duration));
const former:Record<string,string[]>={
 'david-wang':['Formerly at WFG'],'lily-ku':['Formerly at New York Life','and MassMutual'],
 'noah-cheung':['Engineering background'],'catherine-luo':['Formerly at Deutsche Bank','and RBS'],
 'vivian-mau':['Formerly at WFG and PFA'],'crystal-wan':['Formerly at PFA'],
};
export const USTeamFocusV5:React.FC<{showAchievements?:boolean}>=({showAchievements=true})=>{
 const f=useCurrentFrame(),exit=1-clamp01((f-230)/9);
 const active=ranges.findIndex(([from,to])=>f>=from&&f<to);
 const restoring=f>=222,restore=E(f-222,12);
 return <AbsoluteFill style={{background:theme.color.paper,color:theme.color.ink}} data-focus-active={active}>
  <div data-audit="text" style={{position:'absolute',top:96,left:144,right:144,textAlign:'center',fontFamily:theme.font.latinSerif,fontSize:43,fontWeight:400,lineHeight:'56px',opacity:E(f,11)*exit}}>Meet the people behind our US team.</div>
  {people.map((person,i)=>{
   const x=584+(i%3)*264,y=208+Math.floor(i/3)*376+(i%3===1?16:0),enter=E(f-i,7),name=E(f-i-2,5)*.85;
   const selected=active===i,hasFocus=active>=0;
   const opacity=hasFocus?(selected?1:.35):restoring?(.35+.65*restore):1;
   const focus=selected?E(f-ranges[i][0],12):0;
   const outgoing=!selected&&f>=ranges[i][1]&&f<ranges[i][1]+12?(1-E(f-ranges[i][1],12)):0;
   const scale=1+.04*Math.max(focus,outgoing);
   const saturation=hasFocus?(selected?1:0):restoring?restore:1;
   return <div key={person.slug} data-focus-card={person.slug} data-selected={selected} data-focus-opacity={opacity} data-image-scale={scale}
     style={{position:'absolute',left:x,top:y,opacity,transform:`translateY(${12*(1-enter)}px)`}}>
    {i===0&&<div data-audit="text" style={{position:'absolute',top:-24,width:224,fontFamily:theme.font.latin,fontSize:13,lineHeight:'16px',letterSpacing:'.08em',opacity:name*exit,color:theme.color.muted}}>US GENERAL MANAGER</div>}
    <Img src={staticFile(`portraits/us-v5/${person.slug}.png`)} style={{display:'block',width:224,height:280,opacity:enter*exit,filter:`saturate(${saturation})`,transform:`scale(${scale})`,transformOrigin:'112px 140px'}}/>
    <div style={{position:'absolute',top:286,left:0,width:224*focus,height:1,background:theme.color.terracotta,opacity:selected?exit:0}}/>
    <div style={{opacity:name*exit}}>
     <div data-audit="text" style={{fontFamily:theme.font.latinSerif,fontSize:24,lineHeight:'32px',marginTop:8,whiteSpace:'nowrap'}}>{person.name}</div>
     <div data-audit="text" style={{fontFamily:theme.font.latin,fontSize:14,lineHeight:'18px',letterSpacing:'.06em',color:theme.color.muted,marginTop:4}}>{former[person.slug].map((line,j)=><div key={j}>{line}</div>)}</div>
    </div>
   </div>;
  })}
  {active>=0&&showAchievements&&<div data-achievement-person={people[active].slug} data-content-box="selected-experience" style={{position:'absolute',left:1432,top:208+Math.floor(active/3)*376+(active%3===1?16:0)+174,width:344,height:46,fontFamily:theme.font.latin,fontSize:13,lineHeight:'20px',letterSpacing:'.02em',color:theme.color.muted,opacity:exit}}>
   {achievements[active].lines.map((line,row)=>{
    const offset=achievements[active].lines.slice(0,row).reduce((n,s)=>n+s.length,0);
    return <div key={row} data-audit="achievement" style={{height:20,marginTop:row?6:0,whiteSpace:'pre'}}>{Array.from(line).map((char,i)=>{
     const opacity=theme.ease(clamp01(((f-ranges[active][0])/30-(offset+i)*.012)/.12));
     return <span key={i} data-character-index={offset+i} style={{opacity}}>{char}</span>;
    })}</div>;
   })}
  </div>}
 </AbsoluteFill>;
};
