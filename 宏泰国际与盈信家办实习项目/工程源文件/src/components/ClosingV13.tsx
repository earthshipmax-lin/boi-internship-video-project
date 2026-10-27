import React from 'react';
import {AbsoluteFill,Img,staticFile} from 'remotion';
import {OfficialBrandV10} from './OfficialBrandV10';
import {TextV13} from './FilmChromeV13';
import {captionCuesV12,type Locale} from '../config/locale-v12';
import {themeV13 as C,easeV13 as ease} from '../config/theme-v13';
/** No implicit global Remotion frame: suffix can be moved without changing
 * the official growth/centre-out wordmark timing. */
export const ClosingV13:React.FC<{sceneFrame:number;locale:Locale}>=({sceneFrame,locale})=>{
 const t=Math.min(Math.max(0,sceneFrame)/30,7.4),p=ease((t-.16)/.8),slogan=captionCuesV12[22].text[locale];
 return <AbsoluteFill style={{background:C.paper,color:C.ink}}>
  <div data-v13-asset-language-exception="official-logo" style={{position:'absolute',inset:0,transform:'translateY(-110px)'}}><OfficialBrandV10 seconds={t*2.4} prefix="closing-v13"/></div>
  {locale!=='en'?<div data-v13-text-asset="closing.slogan" data-v13-text-value={slogan} style={{position:'absolute',left:365,top:616,width:1190,height:155,opacity:p,transform:`translateY(${(1-p)*13}px)`}}><Img src={staticFile(locale==='yue'?'brand/closing-r01/slogan-brush.svg':'brand/closing-v13/slogan-cn-brush.svg')} style={{width:'100%',height:'100%',objectFit:'contain'}}/></div>:<TextV13 id="closing.slogan" locale={locale} size={76} minSize={48} style={{left:290,top:632,width:1340,height:150,fontFamily:'Geist',fontWeight:800,textAlign:'center',letterSpacing:-1,opacity:p,transform:`translateY(${(1-p)*13}px)`}}>{slogan}</TextV13>}
  <div style={{position:'absolute',left:718,top:804,display:'flex',alignItems:'center',gap:32,opacity:ease((t-3.8)/.8)}}><span style={{fontSize:45,fontWeight:300,color:C.copper}}>×</span><Img data-v13-asset-language-exception="official-evergreen" src={staticFile('brand/v11/evergreen.svg')} style={{width:380,height:107,objectFit:'contain'}}/></div>
 </AbsoluteFill>;
};
