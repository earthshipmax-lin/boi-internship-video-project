import React from 'react';
import {Img,staticFile} from 'remotion';
import {getScreenTextV12,type Locale} from '../config/locale-v12';
import {themeV13 as C} from '../config/theme-v13';
import '../fonts';

export const fontV13=(locale:Locale)=>locale==='en'?'Geist':'Noto Sans TC';
export type TextPropsV13={id:string;locale:Locale;children:React.ReactNode;style?:React.CSSProperties;size:number;minSize?:number;lines?:number};
/** Actual-font fitting is performed once by the parent picture's font-ready
 * layout pass. No text is truncated and a failed fit remains auditable. */
export const TextV13:React.FC<TextPropsV13>=({id,locale,children,style,size,minSize=size*.55,lines=1})=><div data-v13-text={id} data-v13-fit data-v13-base-size={size} data-v13-min-size={minSize} data-v13-lines={lines} style={{position:'absolute',fontFamily:fontV13(locale),fontSize:size,fontWeight:500,lineHeight:'normal',whiteSpace:lines===1?'nowrap':'pre-line',overflowWrap:'normal',...style}}>{children}</div>;

export const BrandV13:React.FC<{paper?:boolean}>=({paper=false})=><div data-v13-asset-language-exception="official-logo" style={{position:'absolute',top:66,left:112,width:330,height:92,opacity:paper?.9:.86}}><Img src={staticFile('brand/v10/宏泰.svg')} style={{width:'100%',height:'100%',objectFit:'contain',filter:paper?'none':'brightness(0) invert(1) drop-shadow(0 0 9px rgba(77,177,224,.26))'}}/></div>;

export const MetaV13:React.FC<{locale:Locale;text:string;paper?:boolean}>=({locale,text,paper=false})=><TextV13 id="meta" locale={locale} size={20} minSize={16} style={{top:94,right:112,width:1100,textAlign:'right',fontWeight:500,letterSpacing:locale==='en'?1:3,opacity:1,color:paper?C.ink:C.paper}}>{text}</TextV13>;

export const FooterV13:React.FC<{locale:Locale;caption:string|null;paper:boolean;watermark:boolean;legal?:readonly string[];legalProgress?:number}>=({locale,caption,paper,watermark,legal,legalProgress=1})=><>
 <TextV13 id="caption" locale={locale} size={36} minSize={28} style={{left:105,top:967,width:1710,height:55,textAlign:'center',fontWeight:500,letterSpacing:1,color:paper?C.ink:C.paper,textShadow:paper?'none':'0 2px 12px rgba(0,0,0,.7)',opacity:caption?1:0}}>{caption??''}</TextV13>
 {legal?<div style={{position:'absolute',left:114,top:1028,width:1600,height:36,opacity:.28*legalProgress,color:C.ink}}>{legal.map((line,i)=><TextV13 key={i} id={`legal-${i}`} locale={locale} size={14} minSize={11} style={{left:0,top:i*18,width:1600,fontWeight:400,lineHeight:'18px',letterSpacing:locale==='en'?.25:1}}>{line}{i===0&&watermark?`　｜　${getScreenTextV12(locale,'watermark')}`:''}</TextV13>)}</div>:watermark&&<TextV13 id="watermark" locale={locale} size={16} minSize={12} style={{left:114,bottom:26,width:1600,fontWeight:400,letterSpacing:2,color:paper?C.ink:C.paper,opacity:.45}}>{getScreenTextV12(locale,'watermark')}</TextV13>}
</>;
