import React from 'react';
import {LogoTileV12} from './LogoGridV12';
import {TextV13} from './FilmChromeV13';
import {logoGridV12 as g,logoOpticalV12 as logos} from '../config/logo-optical-v12';
import type {Locale} from '../config/locale-v12';
import {getScreenCopyExtraV13} from '../config/screen-copy-extras-v13';
import {themeV13 as C,easeV13,clampV13} from '../config/theme-v13';
const initialLights=[432,435,437,440,442,445,448,450,453,455,458,460,463,466,468,471,473,476,478,481];
/** Language-neutral JPEG artwork and existing optical mask are reused intact. */
export const LogoGridV13:React.FC<{sourceFrame:number;locale:Locale}>=({sourceFrame:f,locale})=>{
 const shift=easeV13((f-g.commissionStartFrame)/g.shiftFrames),newRow=f>=g.commissionStartFrame;
 return <div style={{position:'absolute',left:g.premiumLeft-90*shift,top:g.top,width:g.width,height:g.height,opacity:clampV13((f-g.premiumStartFrame)/9)}}>
  {logos.map((a,i)=>{if(i>=20&&!newRow)return null;const lit=i<20?.14+.86*easeV13((f-initialLights[i])/g.fadeFrames):easeV13((f-g.rowAppendStartFrame-a.col*g.rowStaggerFrames)/g.fadeFrames);return <div key={a.id} data-v13-asset-language-exception="source-logo" style={{position:'absolute',left:a.col*(g.cellWidth+g.gap),top:a.row*(g.cellHeight+g.gap)}}><LogoTileV12 logo={a} opacity={g.settledOpacity*lit}/></div>;})}
  {newRow&&<div style={{position:'absolute',left:0,top:368,width:g.width,height:18,opacity:easeV13((f-g.rowAppendStartFrame)/g.fadeFrames),color:C.copper}}><svg width={704} height={18} style={{position:'absolute',inset:0}}><path d="M0 0H422 M486 0H704" transform="translate(0 .5)" stroke="currentColor" strokeWidth={1}/></svg><TextV13 id="logos.banks" locale={locale} size={18} minSize={15} style={{left:432,top:-9,width:54,lineHeight:'18px',letterSpacing:locale==='en'?0:2}}>{getScreenCopyExtraV13(locale,'banks')}</TextV13></div>}
 </div>;
};
