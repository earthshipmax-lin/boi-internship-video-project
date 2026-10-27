import React from 'react';
import {Img,staticFile} from 'remotion';
import assets from '../config/offices-assets-v12.json';
import {officesV12 as t} from '../config/offices-v12';
import {getScreenCopyV13,type TextScreenCopyIdV13} from '../config/screen-copy-v13';
import {locationLabelsV12,type Locale} from '../config/locale-v12';
import {themeV13 as C,easeV13 as ease} from '../config/theme-v13';
import {TextV13} from './FilmChromeV13';
type City=typeof assets.cities[number];
const cityIds=['hk','sz','ny'] as const;
const addresses:readonly TextScreenCopyIdV13[]=['offices.hk-address','offices.sz-address','offices.ny-address'];
const Photos:React.FC<{city:City;sourceFrame:number;start:number;outgoing?:boolean;lastExit?:boolean}>=({city,sourceFrame:f,start,outgoing=false,lastExit=false})=><>{city.images.map((a,i)=>{
 const r=t.tiles[i],p=ease((f-start-t.photoEntryDelay-i*t.tileStaggerFrames)/t.photoWipeFrames),exit=outgoing?ease((f-start-t.photoExitDelay-i*t.tileStaggerFrames)/t.photoWipeFrames):lastExit?ease((f-t.finalExitStart)/(t.finalExitFrames-1)):0;
 const inset=outgoing||lastExit?`inset(0 0 ${exit*100}% 0)`:`inset(${(1-p)*100}% 0 0 0)`;
 return <div key={a.id} data-v13-office-photo={a.id} data-v13-asset-language-exception="source-office-photo" style={{position:'absolute',left:r.x,top:r.y,width:r.width,height:r.height,overflow:'hidden',clipPath:inset}}><Img src={staticFile(a.file)} style={{width:'100%',height:'100%',objectFit:'cover',objectPosition:a.object_position,filter:assets.photo_filter,transform:`scale(${outgoing||lastExit?1:1.04-.04*p})`,transformOrigin:'center'}}/></div>;
})}</>;

export const OfficesV13:React.FC<{sourceFrame:number;locale:Locale}>=({sourceFrame:f,locale})=>{
 if(f>=t.trustStart){const p=ease((f-t.trustStart)/18),out=1-ease((f-1644)/8);return <TextV13 id="values.title" locale={locale} size={143} minSize={65} style={{left:130,top:360,width:1660,fontWeight:800,lineHeight:1.12,letterSpacing:'-.055em',color:C.ink,opacity:p*out,transform:`translateY(${18*(1-p)}px)`}}>{getScreenCopyV13(locale,'values.title')}</TextV13>;}
 const index=Math.min(2,t.cityStarts.filter(s=>f>=s).length-1),city=assets.cities[index],start=t.cityStarts[index],change=ease((f-start)/t.cityChangeFrames),lastExit=f>=t.finalExitStart,exit=lastExit?ease((f-t.finalExitStart)/(t.finalExitFrames-1)):0,initial=ease((f-t.start)/12);
 return <>
  <TextV13 id="offices.headline" locale={locale} size={t.titleSize} minSize={40} style={{left:130,top:t.titleTop,width:1660,height:t.headlineHeight,fontWeight:800,lineHeight:1.12,letterSpacing:'-.055em',color:C.ink,opacity:initial*(1-exit)}}>{getScreenCopyV13(locale,index===2?'offices.vision-title':'offices.headline')}</TextV13>
  <div style={{position:'absolute',left:t.textRegion.x,top:t.textRegion.y,width:t.textRegion.width,height:t.textRegion.height,overflow:'hidden',color:C.ink,opacity:initial*(1-exit)}}>
   <TextV13 id="offices.index" locale={locale} size={20} style={{left:0,top:130,width:430,fontWeight:400,lineHeight:'24px',color:'#7A8A93',letterSpacing:3}}>{String(index+1).padStart(2,'0')} / 03</TextV13>
   <div style={{position:'absolute',left:0,top:160,width:430,height:160,overflow:'hidden'}}>
    {index>0&&change<1&&<TextV13 id="offices.city-outgoing" locale={locale} size={128} minSize={46} style={{left:0,top:10,width:430,height:145,fontWeight:700,lineHeight:1.1,letterSpacing:'-.035em',opacity:1-change,transform:`translateY(${-40*change}px)`}}>{locationLabelsV12[cityIds[index-1]][locale]}</TextV13>}
    <TextV13 id="offices.city-current" locale={locale} size={128} minSize={46} style={{left:0,top:10,width:430,height:145,fontWeight:700,lineHeight:1.1,letterSpacing:'-.035em',opacity:change,transform:`translateY(${40*(1-change)}px)`}}>{locationLabelsV12[cityIds[index]][locale]}</TextV13>
   </div>
   <TextV13 id="offices.english" locale={locale} size={26} minSize={22} style={{left:0,top:338,width:430,height:36,fontWeight:400,letterSpacing:8,lineHeight:'36px'}}>{city.english}</TextV13>
   <TextV13 id="offices.address" locale={locale} size={24} minSize={15} style={{left:0,top:382,width:430,height:34,fontWeight:400,color:'#41596B',lineHeight:'34px'}}>{getScreenCopyV13(locale,addresses[index])}</TextV13>
   <div style={{position:'absolute',left:0,top:460,width:430,height:66}}>{cityIds.map((id,i)=><div key={id} style={{position:'absolute',left:i*145,top:0,width:120,color:i===index?C.blue:C.ink,opacity:i===index?1:.35}}><TextV13 id={`offices.progress.${id}`} locale={locale} size={20} minSize={14} style={{left:0,top:0,width:120,fontWeight:400,letterSpacing:locale==='en'?0:2}}>{locationLabelsV12[id][locale]}</TextV13><div style={{position:'absolute',left:0,top:43,width:120,height:2,background:'#A9B6BD'}}><div style={{width:120*(i<index?1:i===index?change:0),height:2,background:C.blue}}/></div></div>)}</div>
  </div>
  {index>0&&f<start+23&&<Photos city={assets.cities[index-1]} sourceFrame={f} start={start} outgoing/>}<Photos city={city} sourceFrame={f} start={start} lastExit={lastExit}/>
 </>;
};
