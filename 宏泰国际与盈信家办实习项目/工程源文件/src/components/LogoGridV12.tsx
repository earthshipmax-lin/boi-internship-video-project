import React from 'react';
import {Img, staticFile} from 'remotion';
import {logoGridV12 as g, logoOpticalV12 as logos} from '../config/logo-optical-v12';
import stencil from '../assets/logo-masks-v12.json';

const clamp = (v: number) => Math.max(0, Math.min(1, v));
const ease = (v: number) => 1 - Math.pow(1 - clamp(v), 4);
const initialLights = [432,435,437,440,442,445,448,450,453,455,458,460,463,466,468,471,473,476,478,481];
type Logo = typeof logos[number];
const masks = Object.fromEntries(logos.map(a => [a.id, `url("data:image/svg+xml,${encodeURIComponent(
  `<svg xmlns="http://www.w3.org/2000/svg" width="${a.sourceWidth}" height="${a.sourceHeight}" viewBox="0 0 ${a.sourceWidth} ${a.sourceHeight}"><path fill="white" d="${stencil[a.id]}"/></svg>`
)}")`]));

export const LogoTileV12: React.FC<{logo: Logo; optical?: boolean; opacity?: number}> = ({logo: a, optical = true, opacity = .82}) => {
  const [x0,y0,x1,y1] = a.ink;
  const scale = Math.min(g.safeWidth / (x1-x0), g.safeHeight / (y1-y0)) * a.opticalScale;
  return <div style={{position:'relative',width:g.cellWidth,height:g.cellHeight,background:g.tileColor,overflow:'hidden',opacity}}>
    {optical ? <Img src={staticFile(a.file)} style={{position:'absolute',
      left:g.cellWidth/2-(x0+x1)*scale/2,top:g.cellHeight/2-(y0+y1)*scale/2,
      width:a.sourceWidth*scale,height:a.sourceHeight*scale,
      maskImage:masks[a.id],WebkitMaskImage:masks[a.id],maskSize:'100% 100%',WebkitMaskSize:'100% 100%',
      maskRepeat:'no-repeat',WebkitMaskRepeat:'no-repeat'}}/>
      : <Img src={staticFile(a.file)} style={{position:'absolute',left:16,top:12,width:96,height:54,objectFit:'contain'}}/>}
  </div>;
};

export const LogoGridV12: React.FC<{frame: number}> = ({frame}) => {
  const shift = ease((frame-g.commissionStartFrame)/g.shiftFrames);
  const left = g.premiumLeft - 90*shift;
  const incoming = clamp((frame-g.premiumStartFrame)/9);
  const newRow = frame >= g.commissionStartFrame;
  const rowOpacity = ease((frame-g.rowAppendStartFrame)/g.fadeFrames);
  return <div style={{position:'absolute',left,top:g.top,width:g.width,height:g.height,opacity:incoming}}>
    {logos.map((a,i) => {
      if (i>=20 && !newRow) return null;
      const lit = i<20 ? .14+.86*ease((frame-initialLights[i])/g.fadeFrames)
        : ease((frame-g.rowAppendStartFrame-a.col*g.rowStaggerFrames)/g.fadeFrames);
      return <div key={a.id} style={{position:'absolute',left:a.col*(g.cellWidth+g.gap),top:a.row*(g.cellHeight+g.gap)}}>
        <LogoTileV12 logo={a} opacity={g.settledOpacity*lit}/>
      </div>;
    })}
    {newRow && <div style={{position:'absolute',left:0,top:368,width:g.width,height:18,opacity:rowOpacity,color:'#B9653F'}}>
      <svg width={704} height={18} style={{position:'absolute',inset:0}}><path d="M0 0H422 M486 0H704" transform="translate(0 0.5)" stroke="currentColor" strokeWidth={1}/></svg>
      <div style={{position:'absolute',left:432,top:-9,fontFamily:'Noto Sans TC',fontSize:18,fontWeight:500,lineHeight:'18px',letterSpacing:2}}>銀行</div>
    </div>}
  </div>;
};

export const LogoOpticalComparisonStage6: React.FC = () => <div style={{position:'absolute',inset:0,background:'#061C2B',color:'#F4EEE2',fontFamily:'Noto Sans TC'}}>
  <div style={{position:'absolute',left:110,top:50,fontSize:38,fontWeight:700}}>Logo 光學尺寸：每組左為原圖框適配，右為調整後</div>
  <div style={{position:'absolute',left:110,top:112,fontSize:21,opacity:.7}}>同一128×78米白格／96×54安全區；保留原JPEG字形與色彩，僅遮去外部淺色背景。</div>
  {logos.map((a,i) => <div key={a.id} style={{position:'absolute',left:110+(i%5)*338,top:195+Math.floor(i/5)*166,width:310}}>
    <div style={{fontSize:17,marginBottom:12,height:25}}>{String(i+1).padStart(2,'0')} · {a.name}</div>
    <div style={{display:'flex',gap:16}}><LogoTileV12 logo={a} optical={false}/><LogoTileV12 logo={a}/></div>
    <div style={{fontSize:15,marginTop:8,opacity:.65}}>有效字標 {a.displayInkWidth.toFixed(1)} × {a.displayInkHeight.toFixed(1)}px</div>
  </div>)}
</div>;
