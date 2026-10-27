import React from 'react';
import {Img,staticFile} from 'remotion';
import type {Locale} from '../config/locale-v12';
import {getScreenTextV14,getScreenCopyV14 as getScreenCopyV13} from '../config/copy-v14';
import {getPlatformScreenCopyV13} from '../config/screen-copy-v13';
import {TextV13,BrandV13,MetaV13} from './FilmChromeV13';
import {peopleCurveV13 as ease} from '../config/people-v13';
import logos from '../config/logos-mono-v13.json';
import awards from '../config/awards-stage8.json';
import official from '../assets/official-logo-v10.json';
const paper='#F4EEE2';
export const BrandTracksV13:React.FC<{sourceFrame:number;clock:number;locale:Locale}>=({sourceFrame:f,clock,locale})=>{
 const commission=f>=525,t=(f-(commission?525:431))/30,out=commission?1:1-ease((f-517.5)/7.5),p=ease(t/.4)*out,count=ease((t-.1)/.6),n=Math.round((commission?15:100)*count),value=locale==='en'?`${commission?(1.5*count).toFixed(1):Math.round(10*count)}B+`:`${n}億+`;
 return <><BrandV13/><MetaV13 locale={locale} text={getScreenCopyV13(locale,commission?'meta.commission':'meta.premium')}/><TextV13 id="data.label" locale={locale} size={28} minSize={28} style={{left:130,top:300,width:1400,opacity:p,transform:`translateY(${12*(1-p)}px)`}}>{getScreenCopyV13(locale,commission?'commission.label':'premium.label')}</TextV13><TextV13 id="data.value" locale={locale} size={280} minSize={280} style={{left:130,top:340,width:1500,fontWeight:800,lineHeight:1.1,fontVariantNumeric:'tabular-nums',letterSpacing:'-.05em',opacity:p,transform:`translateY(${commission?24*(1-p):-24*(1-out)}px)`}}>{locale==='zh-CN'?value.replace('億','亿'):value}</TextV13><TextV13 id="data.currency" locale={locale} size={36} minSize={36} style={{left:140,top:660,width:900}}>{getScreenCopyV13(locale,'data.currency')}</TextV13>
 {[logos.slice(0,13),logos.slice(13)].map((row,ri)=>{const width=row.reduce((s,r)=>s+r.width+72,0),shift=(clock*24)%width,opacity=.78*ease((clock-.3)/.5);return <div key={ri} data-redesign-track={ri} style={{position:'absolute',left:0,top:ri?852:732,width:1920,height:56,overflow:'hidden',opacity,maskImage:'linear-gradient(90deg,transparent,black 160px,black calc(100% - 160px),transparent)'}}>{[-1,0,1,2].flatMap(k=>{let x=k*width+(ri?shift-850:-shift);return row.map(r=>{const left=x;x+=r.width+72;return <Img key={`${k}-${r.id}`} src={staticFile(r.file)} style={{position:'absolute',left,top:(56-r.height)/2,width:r.width,height:r.height}}/>;});})}</div>;})}</>;
};
export const AwardsRedesignV13:React.FC<{sceneTime:number;locale:Locale}>=({sceneTime:t,locale})=>{
 const zoom=1+.025*Math.min(1,t/5.3),ids=['native-a016','native-a008','native-a006','native-a010'],items=ids.map(id=>awards.items.find(a=>a.id===id)!);let x=520;
 return <div style={{position:'absolute',inset:0,transform:`scale(${zoom})`,transformOrigin:'960px 600px'}}>
 {['native-a004','native-a005'].map((id,i)=>{const a=awards.items.find(a=>a.id===id)!,h=600,w=h*a.output_pixels[0]/a.output_pixels[1],p=ease(t/.5),left=i?1790-w:130;return <React.Fragment key={id}><Img data-redesign-award={id} src={staticFile(a.file)} style={{position:'absolute',left:left+(i?32:-32)*(1-p),top:300,width:w,height:h,opacity:p}}/><div data-v13-text={`award.couplet.${i}`} style={{position:'absolute',left,top:912,width:w,textAlign:'center',fontSize:16,letterSpacing:2,opacity:.72*p}}>{i?'友邦 AIA':'永明金融 SUN LIFE'}</div></React.Fragment>;})}
 <svg width={1920} height={1080}><path d="M480 862H1440" stroke="#6FB4D2" strokeWidth={1} opacity={.35}/></svg>
 {items.map((a,i)=>{const h=490,w=h*a.output_pixels[0]/a.output_pixels[1],left=x;x+=w+27;const p=ease((t-.2-i*.1)/.5),top=860-h+24*(1-p);const labels=['Blue Whale Award','BOC LIFE · 2022','BOC LIFE · 2023','BOC LIFE · 2024'];return <React.Fragment key={a.id}><Img data-redesign-award={a.id} src={staticFile(a.file)} style={{position:'absolute',left,top,width:w,height:h,opacity:p,filter:t>=.9&&t<=2.5?`brightness(${1+.04*Math.max(0,1-Math.abs((t-.9)/1.6-i/3)*5)})`:undefined}}/><div style={{position:'absolute',left,top:862,width:w,height:120,overflow:'hidden',opacity:.12*p,maskImage:'linear-gradient(black,transparent 83%)'}}><Img src={staticFile(a.file)} style={{position:'absolute',left:0,top:0,width:w,height:h,transform:'scaleY(-1)'}}/></div><div data-v13-text={`award.trophy.${i}`} style={{position:'absolute',left:left-10,top:876,width:w+20,textAlign:'center',fontSize:16,opacity:.65*p}}>{labels[i]}</div></React.Fragment>;})}
 </div>;
};
const draw=(node:any,key:React.Key,mono:boolean,prefix:string):React.ReactNode=>{
 const attrs={...node.attrs};if(attrs.fill==='url(#linear-gradient1)')attrs.fill=`url(#${prefix}-trunk)`;
 if(mono)attrs.fill=paper;
 return React.createElement(node.tag,{...attrs,key},node.children?.length?node.children.map((c:any,i:number)=>draw(c,i,mono,prefix)):undefined);
};
export const GrowingTreeV14:React.FC<{x:number;y:number;width:number;height:number;seconds:number;mono?:boolean;prefix:string}>=({x,y,width,height,seconds:t,mono=false,prefix})=>{
 const base=ease(t/.35),trunk=ease((t-.22)/.65);
 return <svg data-v13-text-asset="official-tree" data-v14-growth={t.toFixed(3)} viewBox="8.8875 8.0655 95.75112751258398 76.3045" style={{position:'absolute',left:x,top:y,width,height}}>
 <defs><linearGradient id={prefix+'-template'} x1={1038.77} y1={-313.09} x2={1038.77} y2={-222.15} gradientTransform="translate(-1333.76 24.27) scale(.5)" gradientUnits="userSpaceOnUse"><stop offset={.51} stopColor="#007bc7"/><stop offset={.78} stopColor="#0057a9"/><stop offset={.82} stopColor="#0051a4"/></linearGradient><linearGradient id={prefix+'-trunk'} x1={2782.26} y1={29.17} x2={2782.26} y2={120.1} href={'#'+prefix+'-template'}/><clipPath id={prefix+'-clip'}><rect x={0} y={84.4-46*trunk} width={110} height={46*trunk+.0001}/></clipPath></defs>
 <g data-v14-tree-base transform={`translate(57.4 0) scale(${base} 1) translate(-57.4 0)`} opacity={base}>{draw(official.base,'base',mono,prefix)}</g>
 <g data-v14-tree-trunk clipPath={`url(#${prefix}-clip)`} opacity={trunk}>{draw(official.trunk,'trunk',mono,prefix)}</g>
 {official.leaves.map((l:any,i:number)=>{const p=ease((t-.62-l.ring*.16-(i%4)*.018)/.5),s=.18+.82*p;return <g key={i} data-v14-tree-leaf={i} opacity={p} transform={`translate(${l.x} ${l.y}) scale(${s}) translate(${-l.x} ${-l.y})`}>{draw(l.node,i,mono,prefix)}</g>;})}
 </svg>;
};
export const PlatformRefinedV14:React.FC<{sceneTime:number;locale:Locale}>=({sceneTime:t,locale})=>{
 const c=getPlatformScreenCopyV13(locale),centers=[710,1150,1590],sectors=[c.sectors[0],c.sectors[1],c.sectors[2]],titles=locale==='en'?['Insurance','Family office','Wealth management']:sectors;
 const evidence=locale==='en'?['Hong Kong · Macau · United States\nBermuda · Singapore (planned)','Evergreen Family Office','Trusts · Estates · Tax planning']:locale==='zh-CN'?['香港 · 澳门 · 美国\n百慕达 · 新加坡（筹备中）','盈信家办 EVERGREEN','信托 · 遗产 · 税务规划']:['香港 · 澳門 · 美國\n百慕達 · 新加坡（籌備中）','盈信家辦 EVERGREEN','信託 · 遺產 · 稅務規劃'];
 const nodes=locale==='en'?['Insurance','Trusts','Tax planning','Education','Residency']:c.nodes;
 const p=ease((t-.25)/.8),lp=ease((t-.45)/.65);
 return <>
 <TextV13 id="platform.title" locale={locale} size={88} minSize={80} style={{left:130,top:190,width:1660,fontWeight:800,lineHeight:1.12,opacity:ease(t/.4)}}>{getScreenTextV14(locale,'platformTitle')}</TextV13>
 <svg width={1920} height={1080} style={{position:'absolute',inset:0}}>
  <circle cx={1150} cy={465} r={105} fill="none" stroke="#B7E7F8" strokeWidth={1.2} opacity={.32*ease((t-.2)/.5)}/>
  {centers.map((x,i)=>{const v=ease((t-.6-i*.1)/.6);return <path key={x} d={`M1150 570 Q1150 625 ${x} 650`} pathLength={1} fill="none" stroke={paper} strokeOpacity={.42} strokeWidth={1.2} strokeDasharray={1} strokeDashoffset={1-v}/>;})}
  <path d="M445 540 C630 540 770 465 1045 465" pathLength={1} fill="none" stroke="#B7E7F8" strokeWidth={1.5} opacity={.75} strokeDasharray={1} strokeDashoffset={1-ease((t-.5)/.7)}/>
  <path d="M600 842H1780" stroke="#B7E7F8" opacity={.25*ease((t-1)/.5)}/>
 </svg>
 <div data-v14-evergreen="disc" style={{position:'absolute',left:175,top:405,width:270,height:270,borderRadius:'50%',background:paper,opacity:p,transform:`translateY(${18*(1-p)}px) scale(${.88+.12*p})`,clipPath:`circle(${Math.max(.1,p*72)}% at 50% 50%)`}}/>
 <Img data-v14-evergreen="logo" src={staticFile('brand/v11/evergreen.svg')} style={{position:'absolute',left:205,top:503,width:210,height:65,objectFit:'contain',opacity:lp,transform:`translateY(${12*(1-lp)}px) scale(${.96+.04*lp})`}}/>
 <TextV13 id="platform.evergreen.name" locale={locale} size={32} minSize={32} style={{left:130,top:720,width:360,textAlign:'center',lineHeight:'44px',fontWeight:600,opacity:ease((t-.65)/.5)}}>{locale==='en'?'Evergreen':locale==='zh-CN'?'盈信家办':'盈信家辦'}</TextV13>
 <TextV13 id="platform.evergreen.role" locale={locale} size={22} minSize={22} style={{left:130,top:792,width:360,textAlign:'center',lineHeight:'30px',opacity:.75*ease((t-.8)/.5)}}>{locale==='en'?'Family Office':locale==='zh-CN'?'家族办公室':'家族辦公室'}</TextV13>
 <GrowingTreeV14 x={1080} y={395} width={140} height={140} seconds={t+.2} mono prefix="platform-v14"/>
 {centers.map((x,i)=><React.Fragment key={i}><TextV13 id={`platform.sector.${i}`} locale={locale} size={locale==='en'?32:36} minSize={locale==='en'?30:36} style={{left:x-190,top:678,width:380,textAlign:'center',lineHeight:'46px',fontWeight:600,opacity:ease((t-.8-i*.08)/.5)}}>{titles[i]}</TextV13><TextV13 id={`platform.evidence.${i}`} locale={locale} size={22} minSize={22} lines={2} style={{left:x-190,top:752,width:380,textAlign:'center',lineHeight:'30px',opacity:.76*ease((t-1-i*.08)/.5)}}>{evidence[i]}</TextV13></React.Fragment>)}
 {nodes.map((n,i)=><TextV13 key={i} id={`platform.service.${i}`} locale={locale} size={locale==='en'?30:34} minSize={locale==='en'?28:34} style={{left:600+i*236,top:880,width:210,textAlign:'center',lineHeight:'46px',opacity:ease((t-1.25-i*.06)/.4),transform:`translateY(${10*(1-ease((t-1.25-i*.06)/.4))}px)`}}>{n}</TextV13>)}
 </>;
};
export const RootsRefinedV14:React.FC<{sourceFrame:number;locale:Locale;elapsed?:number;secondOverride?:boolean;secondElapsed?:number}>=({sourceFrame:f,locale,elapsed,secondOverride,secondElapsed})=>{
 const t=elapsed??(f-1652)/30,second=secondOverride??f>=1740,p=ease((second?(secondElapsed??(f-1740)/30):t)/.4);
 const text=locale==='en'?(second?'Steady steps.\nA lasting future.':'Strong roots.\nRoom to grow.'):locale==='zh-CN'?(second?'步伐够稳，\n走得更远。':'根扎得深，\n长得更高。'):(second?'步伐夠穩，\n走得更遠。':'根扎得深，\n長得更高。');
 return <><TextV13 id="roots.title" locale={locale} size={locale==='en'?90:128} minSize={locale==='en'?82:128} lines={2} style={{left:180,top:430,width:760,fontWeight:700,lineHeight:1.18,color:'#0B2E45',whiteSpace:'pre-line',opacity:Math.max(.01,p),transform:'translateY(-50%)'}}>{text}</TextV13><div style={{position:'absolute',left:180,top:640,width:80,height:3,background:'#B9653F',opacity:ease(t/.5)}}/><GrowingTreeV14 x={1060} y={150} width={700} height={560} seconds={t} prefix="roots-v14"/></>;
};
