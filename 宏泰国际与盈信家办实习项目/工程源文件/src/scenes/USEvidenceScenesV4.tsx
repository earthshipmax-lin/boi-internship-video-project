import React from 'react';
import {AbsoluteFill, Img, staticFile, useCurrentFrame} from 'remotion';
import {theme, clamp01} from '../theme';
import type {CaptionScene} from '../components/BilingualCaptions';
import photos from '../config/us-v4-photos.json';

const {paper, ink, muted, line, terracotta} = theme.color;
const ease = (f: number, from = 0, duration = 15) => theme.ease(clamp01((f - from) / duration));
const normalize = (word: string) => word.toLowerCase().replace(/[^a-z0-9]/g, '');
const cueFrame = (scene: CaptionScene, cue: string) => {
  const word = scene.words.find(item => normalize(item.word) === normalize(cue));
  return word ? scene.voiceStartFrame - scene.startFrame + Math.ceil(word.start * 30) : Infinity;
};
const Text: React.FC<{children: React.ReactNode; style?: React.CSSProperties}> = ({children, style}) =>
  <div data-audit="text" style={{fontFamily: theme.font.latin, ...style}}>{children}</div>;
const Serif: React.FC<{children: React.ReactNode; style?: React.CSSProperties}> = ({children, style}) =>
  <Text style={{fontFamily: theme.font.latinSerif, fontWeight: 400, ...style}}>{children}</Text>;
const Label: React.FC<{children: React.ReactNode; style?: React.CSSProperties}> = ({children, style}) =>
  <Text style={{fontSize: 14, lineHeight: '22px', color: muted, letterSpacing: '.12em', ...style}}>{children}</Text>;

// Assets are native-size source photographs with the single Prompt17 grade baked in.
// Only a cover crop and a translation animate; there is no animated image scaling.
const Figure: React.FC<{id: string; start: number; exit: number; horizontal?: boolean; duration?: number}> = ({id, start, exit, horizontal = false, duration = 15}) => {
  const f = useCurrentFrame();
  const photo = photos.find(item => item.id === id)!;
  const p = ease(f, start, duration);
  return <div data-photo-id={id} data-source-scale={photo.scale} data-source-page={photo.sourcePage}
    style={{position: 'absolute', left: photo.x, top: photo.y, width: photo.width, height: photo.height + 32,
      opacity: p * exit, transform: `translate(${horizontal ? 24 * (1 - p) : 0}px, ${horizontal ? 0 : 12 * (1 - p)}px)`}}>
    <Img src={staticFile(photo.file)} style={{display: 'block', width: photo.width, height: photo.height,
      objectFit: 'cover', objectPosition: `${photo.position[0] * 100}% ${photo.position[1] * 100}%`}}/>
    <div style={{position: 'absolute', inset: '0 0 32px', boxSizing: 'border-box', border: `1px solid ${line}`}}/>
    <Text style={{fontSize: 14, lineHeight: '20px', letterSpacing: '.08em', color: muted, marginTop: 12, whiteSpace: 'nowrap'}}>{photo.figure}</Text>
  </div>;
};

export const USEvidenceShotV4: React.FC<{scene: CaptionScene}> = ({scene}) => {
  const f = useCurrentFrame();
  const exit = Math.min(1, (scene.endFrame - scene.startFrame - 1 - f) / 9);
  const fade = ease(f) * exit;
  if (scene.id === 'S1') return <AbsoluteFill style={{background: paper, color: ink}}>
    <div data-content-box="brand-column" style={{position: 'absolute', left: 200, top: 312, width: 760, height: 450, opacity: fade}}>
      <Serif style={{fontSize: 86, lineHeight: 1.08, letterSpacing: '-.025em'}}>Blue Oak<br/>International.</Serif>
      <Text style={{fontSize: 24, lineHeight: '36px', color: muted, letterSpacing: '.12em', marginTop: 40}}>Hong Kong · United States</Text>
      <div style={{height: 1, width: 680 * ease(f, 4, 18), background: line, marginTop: 32}}/>
      <Text style={{fontSize: 20, lineHeight: '32px', marginTop: 28, opacity: ease(f, cueFrame(scene, 'nineteen'), 18)}}>Group heritage since 1997.</Text>
    </div>
    <Figure id="fig01" start={9} duration={18} exit={exit} horizontal/>
  </AbsoluteFill>;

  if (scene.id === 'S3') {
    const rows = [
      {value: '10B+', label: <>Premium income<br/>for insurers</>, detail: 'Group total · HKD', cue: 'ten', size: 164},
      {value: '1.5B+', label: <>Commission income<br/>for the group</>, detail: 'Group total · HKD', cue: 'one', size: 152},
      {value: '3', label: <>Offices</>, detail: 'Hong Kong · Shenzhen · New York', cue: 'three', size: 144},
    ];
    const photoStart = cueFrame(scene, 'ten') + 12;
    return <AbsoluteFill style={{background: paper, color: ink}}>
      <Label style={{position: 'absolute', left: 200, top: 112, opacity: fade}}>GROUP SCALE · COMPANY-REPORTED</Label>
      <Label style={{position: 'absolute', left: 1180, top: 112, opacity: fade}}>OFFICE ARCHIVE</Label>
      {rows.map((row, i) => {
        const p = ease(f, cueFrame(scene, row.cue), 20);
        return <div key={row.cue} data-content-box={`stat-${row.cue}`} data-stat-cue={row.cue}
          style={{position: 'absolute', left: 200, top: 184 + i * 268, width: 880, height: 190,
            opacity: p * exit, transform: `translateY(${12 * (1 - p)}px)`}}>
          <div style={{display: 'flex', alignItems: 'baseline', gap: 18}}>
            {i < 2 && <Text style={{fontSize: 24, lineHeight: '30px', color: muted, alignSelf: 'flex-start', marginTop: 41}}>HK$</Text>}
            <Serif style={{fontSize: row.size, lineHeight: 1, letterSpacing: '-.045em', fontVariantNumeric: 'lining-nums tabular-nums'}}>{row.value}</Serif>
          </div>
          <div style={{position: 'absolute', left: 532, top: i === 2 ? 30 : 20, width: 348}}>
            <Text style={{fontSize: 26, lineHeight: '34px', letterSpacing: '-.015em'}}>{row.label}</Text>
            <Text style={{fontSize: 16, lineHeight: '24px', color: muted, marginTop: 12, whiteSpace: 'nowrap'}}>{row.detail}</Text>
          </div>
          <div style={{position: 'absolute', left: 0, right: 0, bottom: 0, height: 1, background: line}}/>
        </div>;
      })}
      <Figure id="fig02" start={photoStart} exit={exit}/>
      <Figure id="fig03" start={photoStart + 8} exit={exit}/>
      <Figure id="fig04" start={photoStart + 16} exit={exit}/>
    </AbsoluteFill>;
  }

  if (scene.id === 'S4') {
    const stateEntry = ease(f, cueFrame(scene, 'nine'), 18) * exit;
    return <AbsoluteFill style={{background: paper, color: ink}}>
      <Label style={{position: 'absolute', left: 240, top: 130, opacity: fade}}>CARRIER SELECTION CRITERIA</Label>
      <Serif style={{position: 'absolute', left: 240, top: 172, fontSize: 54, lineHeight: '70px', letterSpacing: '-.015em', opacity: fade}}>Our US carrier selection standard.</Serif>
      <Text style={{position: 'absolute', left: 240, top: 258, fontSize: 20, lineHeight: '30px', color: muted, opacity: fade}}>AM Best financial strength · A-rated or better</Text>
      {[{rating: 'A++', name: 'Superior'}, {rating: 'A+', name: 'Superior'}, {rating: 'A', name: 'Excellent'}].map((r, i) =>
        <div key={r.rating} data-content-box={`rating-${r.rating}`} style={{position: 'absolute', left: 240 + i * 400, top: 328, width: 360, height: 200,
          boxSizing: 'border-box', border: `1px solid ${i === 2 ? terracotta : line}`, textAlign: 'center', opacity: ease(f, cueFrame(scene, 'a') + i * 12, 18) * exit}}>
          <Serif style={{fontSize: 104, lineHeight: '124px', letterSpacing: '-.045em', marginTop: 10}}>{r.rating}</Serif>
          <Text style={{fontSize: 22, lineHeight: '32px', color: muted, marginTop: 6}}>{r.name}</Text>
        </div>)}
      <div data-content-box="nine-state-register" data-stat-cue="nine" style={{position: 'absolute', left: 240, top: 602, width: 1400, height: 164, opacity: stateEntry}}>
        <Serif style={{position: 'absolute', left: 0, top: -16, fontSize: 176, lineHeight: 1, letterSpacing: '-.045em'}}>9</Serif>
        <div style={{position: 'absolute', left: 200, top: 2}}>
          <Text style={{fontSize: 28, lineHeight: '42px'}}>Products across 9 states.</Text>
          <Text style={{fontSize: 14, lineHeight: '24px', color: muted, marginTop: 20, letterSpacing: '.025em'}}>California · New York · Massachusetts · Arizona · Connecticut</Text>
          <Text style={{fontSize: 14, lineHeight: '24px', color: muted, marginTop: 4, letterSpacing: '.025em'}}>Texas · North Carolina · Delaware · New Jersey</Text>
        </div>
      </div>
      <Text style={{position: 'absolute', left: 440, top: 802, fontSize: 26, lineHeight: '38px', opacity: ease(f, cueFrame(scene, 'century'), 18) * exit}}>Carriers with a hundred-year history.</Text>
    </AbsoluteFill>;
  }

  // Unequal four-part arrangement: a real reception, two right-hand records,
  // and a short platform entry below the photo. No certificates are invented.
  return <AbsoluteFill style={{background: paper, color: ink}}>
    <Label style={{position: 'absolute', left: 200, top: 128, opacity: fade}}>THE INFRASTRUCTURE</Label>
    <Serif style={{position: 'absolute', left: 200, top: 170, fontSize: 54, lineHeight: '70px', letterSpacing: '-.015em', opacity: fade}}>A foundation for the work.</Serif>
    <Figure id="fig05" start={cueFrame(scene, 'flushing')} exit={exit}/>
    <div data-content-box="ny-address" style={{position: 'absolute', left: 200, top: 642, width: 660, height: 70, opacity: ease(f, cueFrame(scene, 'flushing'), 15) * exit}}>
      <Text style={{fontSize: 22, lineHeight: '34px'}}>Unit 9E &amp; 9F, 3808 Union St.</Text>
      <Text style={{fontSize: 20, lineHeight: '30px', color: muted}}>Flushing, NY 11354</Text>
    </div>
    <div data-content-box="hk-registration" style={{position: 'absolute', left: 1016, top: 300, width: 700, height: 170, opacity: ease(f, cueFrame(scene, 'a'), 15) * exit}}>
      <div style={{height: 1, background: line}}/>
      <Label style={{marginTop: 24}}>HONG KONG REGISTRATION</Label>
      <Text style={{fontSize: 32, lineHeight: '44px', marginTop: 24}}>IA license · FB1681</Text>
      <Text style={{fontSize: 24, lineHeight: '36px', color: muted, marginTop: 6}}>PIBA member · M0573</Text>
    </div>
    <div data-content-box="insurance-agreements" style={{position: 'absolute', left: 1016, top: 560, width: 700, height: 236, opacity: ease(f, cueFrame(scene, 'insurance'), 15) * exit}}>
      <div style={{height: 1, background: line}}/>
      <Label style={{marginTop: 24}}>INSURANCE-SERVICE AGREEMENTS</Label>
      <Text style={{fontSize: 32, lineHeight: '44px', marginTop: 24}}>China Minsheng</Text>
      <Text style={{fontSize: 26, lineHeight: '38px', marginTop: 6}}>Shanghai Commercial</Text>
      <Text style={{fontSize: 16, lineHeight: '26px', color: muted, marginTop: 12}}>Company-reported agreements</Text>
    </div>
    <div data-content-box="digital-platform" style={{position: 'absolute', left: 200, top: 778, width: 660, height: 114, opacity: ease(f, cueFrame(scene, 'singapore'), 15) * exit}}>
      <Label>DIGITAL PLATFORM</Label>
      <Text style={{fontSize: 28, lineHeight: '40px', marginTop: 10}}>US · Hong Kong</Text>
      <Text style={{fontSize: 22, lineHeight: '32px', color: muted, marginTop: 2}}>Singapore in preparation</Text>
    </div>
  </AbsoluteFill>;
};
