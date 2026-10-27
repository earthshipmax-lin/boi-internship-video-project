import React from 'react';
import {AbsoluteFill,Sequence,useCurrentFrame,staticFile,Audio} from 'remotion';
import {theme,clamp01} from '../theme';
import {USTeamV1} from './USTeamV1';
import official from '../assets/official-logo-v10.json';
import timeline from '../config/us-full-timeline.json';
import '../fonts';
const ink=theme.color.ink,muted=theme.color.muted,paper=theme.color.paper;
const node=(n:any,key:number):React.ReactNode=>React.createElement(n.tag,{...n.attrs,key,fill:n.attrs.fill==='none'?'none':'currentColor'},n.children?.map((c:any,i:number)=>node(c,i)));
const Serif:React.FC<{children:React.ReactNode;style?:React.CSSProperties}>=({children,style={}})=><div style={{fontFamily:theme.font.latinSerif,...style}}>{children}</div>;
const Label:React.FC<{children:React.ReactNode}>=({children})=><div style={{fontFamily:theme.font.latin,fontSize:16,letterSpacing:'.14em',color:muted,marginBottom:32}}>{children}</div>;
const Shot:React.FC<{id:string;frames:number}>=({id,frames})=>{
 const f=useCurrentFrame(),t=f/30,fade=theme.ease(clamp01(f/15))*Math.min(1,(frames-1-f)/9),entry=theme.ease(clamp01(f/22));
 const center:React.CSSProperties={position:'absolute',inset:0,display:'flex',alignItems:'center',justifyContent:'center',flexDirection:'column',padding:'0 144px',textAlign:'center'};
 if(id==='S2')return <div className="team-scene" style={{position:'absolute',inset:0}}><style>{'.team-scene > div > div:last-child{display:none!important}'}</style><USTeamV1/></div>;
 if(id==='S0')return <div style={{...center,opacity:fade}}><Serif style={{fontSize:64,lineHeight:1.2,maxWidth:1300}}>Most people never get a real shot<br/>at this business.</Serif></div>;
 if(id==='S1')return <div style={{position:'absolute',left:240,right:240,bottom:224,opacity:fade}}><Label>A US PRACTICE</Label><Serif style={{fontSize:104,lineHeight:1.03}}>Blue Oak<br/>International.</Serif><div style={{height:1,background:theme.color.line,margin:'48px 0 32px',width:960*entry}}/><div style={{fontFamily:theme.font.latin,fontSize:24,color:muted}}>People. Experience. A shared practice.</div></div>;
 if(id==='S3')return <div style={{...center,opacity:fade}}><Label>THE FIRST YEAR</Label><Serif style={{fontSize:64}}>Build the fundamentals.</Serif><svg width="1504" height="220" style={{marginTop:90}}><line x1="128" x2="1376" y1="80" y2="80" stroke={theme.color.line} strokeWidth="1"/><line x1="128" x2={128+1248*theme.ease(clamp01((t-1)/5))} y1="80" y2="80" stroke={theme.color.terracotta} strokeWidth="2"/>{['Licensing','Products & Process','Client Work'].map((s,i)=><g key={s} opacity={.25+.75*theme.ease(clamp01((t-[.6,2.2,4.4][i])/.5))}><circle cx={128+i*624} cy="80" r="7" fill={ink}/><text x={128+i*624} y="148" textAnchor="middle" fontFamily={theme.font.latin} fontSize="24" fill={ink}>{s}</text><text x={128+i*624} y="193" textAnchor="middle" fontFamily={theme.font.latin} fontSize="14" fill={muted}>0{i+1}</text></g>)}</svg></div>;
 if(id==='S4')return <div style={{...center,opacity:fade}}><Label>ALONGSIDE EXPERIENCED PARTNERS</Label><Serif style={{fontSize:64}}>A practice you build together.</Serif><svg width="1280" height="250" style={{marginTop:70}}><line x1="64" x2="1216" y1="64" y2="64" stroke={ink} strokeWidth="2"/><line x1="64" x2="1216" y1="152" y2="152" stroke={theme.color.line} strokeWidth="2" strokeDasharray="8 12"/><line x1="64" x2={64+1152*theme.ease(clamp01((t-1)/5))} y1="152" y2="152" stroke={ink} strokeWidth="2"/><circle cx={64+1152*theme.ease(clamp01(t/7))} cy="64" r="5" fill={ink}/><circle cx={64+1152*theme.ease(clamp01(Math.max(0,t-.4)/7))} cy="152" r="5" fill={ink}/></svg></div>;
 if(id==='S5')return <div style={{...center,opacity:fade}}><Serif style={{fontSize:52}}>The first year is the hardest one.</Serif></div>;
 const logoOpacity=theme.ease(clamp01((t-4.5)/1));
 return <div style={center}><svg width="1920" height="1080" style={{position:'absolute',inset:0}}>{[184,248,312].map((r,i)=><circle key={r} cx="960" cy="500" r={r} fill="none" stroke={theme.color.terracotta} strokeWidth="1" opacity={.2*theme.ease(clamp01((t-i*.4)/1.5))}/>)}</svg><div style={{position:'absolute',top:150,opacity:1-logoOpacity}}><Serif style={{fontSize:62,lineHeight:1.2}}>This is the conversation to have.</Serif></div><div style={{opacity:logoOpacity,display:'flex',flexDirection:'column',alignItems:'center',position:'relative'}}><svg width="210" height="210" viewBox="0 0 110 100" style={{color:ink}}>{node(official.trunk,0)}{node(official.base,1)}{official.leaves.map((l:any,i:number)=>node(l.node,i+2))}</svg><Serif style={{fontSize:64,marginTop:32}}>Blue Oak International.</Serif></div><div style={{position:'absolute',bottom:40,fontFamily:theme.font.latin,fontSize:12,color:muted,opacity:.5}}>Internal review — not for distribution</div></div>;
};
export const USFilm60V1:React.FC<{qa?:boolean}>=({qa=false})=>{
 const f=useCurrentFrame();if(qa)console.log('US_FULL_AUDIT:'+JSON.stringify({frame:f,scene:timeline.scenes.find(s=>f>=s.startFrame&&f<s.endFrame)?.id,playbackRate:1}));
 return <AbsoluteFill style={{background:paper,color:ink}}>{timeline.scenes.map(s=><Sequence key={s.id} from={s.startFrame} durationInFrames={s.endFrame-s.startFrame}><Shot id={s.id} frames={s.endFrame-s.startFrame}/></Sequence>)}<Audio src={staticFile('music/us-v1/full-review-mix.wav')} playbackRate={1}/></AbsoluteFill>;
};
