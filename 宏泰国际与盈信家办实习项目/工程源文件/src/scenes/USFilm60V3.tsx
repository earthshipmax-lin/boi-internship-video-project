import React, {useLayoutEffect, useRef} from 'react';
import {AbsoluteFill, Audio, Sequence, staticFile, useCurrentFrame, delayRender, continueRender} from 'remotion';
import {theme, clamp01} from '../theme';
import {USTeamV1} from './USTeamV1';
import {OfficialUSGrowth} from '../components/OfficialUSGrowth';
import {BilingualCaptions, CaptionScene} from '../components/BilingualCaptions';
import timeline from '../config/us-full-v3-timeline.json';
import facts from '../config/us-full-v2-facts.json';
import '../fonts';

type AlignedWord = {word: string; start: number; end: number};
type Scene = CaptionScene;
const scenes = timeline.scenes as Scene[];
const {ink, muted, paper, line, terracotta} = theme.color;
const sans = theme.font.latin;
const serif = theme.font.latinSerif;
const ease = (frame: number, from = 0, duration = 18) => theme.ease(clamp01((frame - from) / duration));
const normalize = (word: string) => word.toLowerCase().replace(/[^a-z0-9]/g, '');
const fact = facts as Record<string, unknown>;

// Alignment timestamps are relative to the original, unmodified voice recording.
// Ceil prevents a statistic from appearing even one frame before its spoken cue.
const cueFrame = (scene: Scene, cue: string) => {
  const word = scene.words.find((item) => normalize(item.word) === normalize(cue));
  return word ? scene.voiceStartFrame - scene.startFrame + Math.ceil(word.start * 30) : Infinity;
};


const Text: React.FC<{children: React.ReactNode; style?: React.CSSProperties}> = ({children, style}) => (
  <div data-audit="text" style={{fontFamily: sans, ...style}}>{children}</div>
);
const Serif: React.FC<{children: React.ReactNode; style?: React.CSSProperties}> = ({children, style}) => (
  <Text style={{fontFamily: serif, fontWeight: 400, ...style}}>{children}</Text>
);
const Eyebrow: React.FC<{children: React.ReactNode; style?: React.CSSProperties}> = ({children, style}) => (
  <Text style={{fontSize: 16, lineHeight: '24px', letterSpacing: '.14em', color: muted, ...style}}>{children}</Text>
);

const Shot: React.FC<{scene: Scene}> = ({scene}) => {
  const f = useCurrentFrame();
  const frames = scene.endFrame - scene.startFrame;
  const fade = ease(f, 0, 15) * Math.min(1, (frames - 1 - f) / 9);
  const center: React.CSSProperties = {
    position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center',
    flexDirection: 'column', padding: '0 144px', textAlign: 'center',
  };

  // These approved scenes retain their original dimensions, images and typography.
  if (scene.id === 'S0') return (
    <div style={{...center, opacity: fade}}>
      <Serif style={{fontSize: 64, lineHeight: 1.2, maxWidth: 1300}}>
        Most people never get a real shot<br/>at this business.
      </Serif>
    </div>
  );
  if (scene.id === 'S2') return (
    <div className="us-v2-approved-team" style={{position: 'absolute', inset: 0}}>
      <style>{'.us-v2-approved-team > div > div:last-child{display:none!important}'}</style>
      <USTeamV1/>
    </div>
  );
  if (scene.id === 'S6') return (
    <div style={{...center, opacity: fade}}>
      <Serif style={{fontSize: 52}}>The first year is the hardest one.</Serif>
    </div>
  );

  if (scene.id === 'S1') return (
    <div style={{position: 'absolute', left: 240, right: 240, top: 352, opacity: fade}}>
      <Serif style={{fontSize: 96, lineHeight: 1.08, letterSpacing: '-.025em', whiteSpace: 'nowrap'}}>
        Blue Oak International.
      </Serif>
      <Text style={{fontSize: 24, lineHeight: '36px', color: muted, letterSpacing: '.14em', marginTop: 48}}>
        Hong Kong · United States
      </Text>
      <div style={{height: 1, width: 960 * ease(f, 4, 18), background: line, marginTop: 36}}/>
      <Text style={{fontSize: 20, lineHeight: '32px', marginTop: 32, opacity: ease(f, cueFrame(scene, 'nineteen'), 18)}}>Group heritage since 1997.</Text>
    </div>
  );

  if (scene.id === 'S3') {
    const rows = [
      {value: String(fact.premium || 'HK$10B+'), label: 'Premium income for insurers', detail: 'Company-reported group total', cue: String(fact.premiumCue || 'ten')},
      {value: String(fact.commission || 'HK$1.5B+'), label: 'Commission income for the group', detail: 'Company-reported group total', cue: String(fact.commissionCue || 'one')},
      {value: '3', label: 'Offices', detail: 'Hong Kong · Shenzhen · New York', cue: String(fact.officesCue || 'three')},
    ];
    return (
      <div style={{position: 'absolute', left: 240, right: 240, top: 132}}>
        <Eyebrow style={{opacity: fade}}>GROUP SCALE · COMPANY-REPORTED</Eyebrow>
        {rows.map((row, i) => {
          const reveal = ease(f, cueFrame(scene, row.cue), 20);
          const isMoney = row.value.startsWith('HK$');
          return (
            <div key={row.label} data-stat-cue={row.cue} style={{position: 'absolute', top: 78 + i * 228, width: 1440, height: 212, opacity: reveal * Math.min(1, (frames - 1 - f) / 9), transform: `translateY(${16 * (1 - reveal)}px)`}}>
              <div style={{display: 'flex', alignItems: 'baseline', gap: 20, position: 'absolute', left: 0, top: 0}}>
                {isMoney && <Text style={{fontSize: 28, lineHeight: 1, color: muted, alignSelf: 'flex-start', marginTop: 38}}>HK$</Text>}
                <Serif style={{fontSize: 150, lineHeight: 1, letterSpacing: '-.045em', fontVariantNumeric: 'lining-nums tabular-nums'}}>{isMoney ? row.value.slice(3) : row.value}</Serif>
              </div>
              <div style={{position: 'absolute', left: 696, right: 0, top: 48}}>
                <Text style={{fontSize: 30, lineHeight: '40px', letterSpacing: '-.015em'}}>{row.label}</Text>
                <Text style={{fontSize: 20, lineHeight: '30px', color: muted, marginTop: 14}}>{row.detail}</Text>
              </div>
              <div style={{position: 'absolute', left: 0, right: 0, bottom: 6, height: 1, background: line}}/>
            </div>
          );
        })}
      </div>
    );
  }

  if (scene.id === 'S4') return (
    <div style={{position: 'absolute', left: 256, right: 256, top: 136, opacity: fade}}>
      <Eyebrow>CARRIER SELECTION CRITERIA</Eyebrow>
      <Serif style={{fontSize: 52, lineHeight: '68px', letterSpacing: '-.015em', marginTop: 24}}>
        Our US carrier selection standard.
      </Serif>
      <Text style={{fontSize: 20, color: muted, lineHeight: '30px', marginTop: 24}}>AM Best financial strength · A-rated or better</Text>
      <div style={{display: 'flex', gap: 32, marginTop: 38}}>
        {[{rating: 'A++', name: 'Superior'}, {rating: 'A+', name: 'Superior'}, {rating: 'A', name: 'Excellent'}].map((rating, i) => (
          <div key={rating.rating} style={{width: 448, height: 256, boxSizing: 'border-box', border: `1px solid ${i === 2 ? terracotta : line}`, opacity: ease(f, cueFrame(scene, 'a') + i * 12, 18), textAlign: 'center'}}>
            <Serif style={{fontSize: 124, lineHeight: '150px', letterSpacing: '-.045em', marginTop: 16}}>{rating.rating}</Serif>
            <Text style={{fontSize: 24, lineHeight: '36px', color: muted, marginTop: 8}}>{rating.name}</Text>
          </div>
        ))}
      </div>
      <div style={{marginTop: 52}}>
        <Text style={{fontSize: 30, lineHeight: '42px', opacity: ease(f, cueFrame(scene, 'nine'), 18)}}>Products across 9 US states.</Text>
        <Text style={{fontSize: 26, lineHeight: '38px', marginTop: 10, opacity: ease(f, cueFrame(scene, 'century'), 18)}}>Carriers with a hundred-year history.</Text>
        <Text style={{fontSize: 16, lineHeight: '24px', color: muted, marginTop: 16, opacity: ease(f, cueFrame(scene, 'a'), 18)}}>Company-reported selection standard</Text>
      </div>
    </div>
  );

  if (scene.id === 'S5') {
    const cells = [
      {label: 'NEW YORK OFFICE', title: 'Flushing, New York', lines: ['Unit 9E & 9F, 3808 Union St.', 'Flushing, NY 11354']},
      {label: 'HONG KONG REGISTRATION', title: 'IA license · FB1681', lines: ['PIBA member · M0573']},
      {label: 'INSURANCE-SERVICE AGREEMENTS', title: 'China Minsheng', lines: ['Shanghai Commercial'], note: 'Company-reported agreements'},
      {label: 'DIGITAL PLATFORM', title: 'US · Hong Kong', lines: ['Singapore in preparation']},
    ];
    return (
      <div style={{position: 'absolute', left: 296, top: 132}}>
        <Eyebrow style={{opacity: fade}}>THE INFRASTRUCTURE</Eyebrow>
        <Serif style={{fontSize: 52, lineHeight: '68px', marginTop: 20, opacity: fade}}>A foundation for the work.</Serif>
        {cells.map((cell, i) => {
          const entry = ease(f, 8 + i * 24, 20);
          return (
            <div key={cell.label} style={{position: 'absolute', left: (i % 2) * 688, top: 160 + Math.floor(i / 2) * 328, width: 640, height: 280, opacity: entry * Math.min(1, (frames - 1 - f) / 9), transform: `translateY(${10 * (1 - entry)}px)`}}>
              <div style={{height: 1, width: 640, background: line}}/>
              <Eyebrow style={{fontSize: 12, lineHeight: '20px', marginTop: 26}}>{cell.label}</Eyebrow>
              <Text style={{fontSize: 28, lineHeight: '40px', letterSpacing: '-.01em', marginTop: 26}}>{cell.title}</Text>
              {cell.lines.map((text, j) => <Text key={text} style={{fontSize: j === 0 ? 26 : 22, lineHeight: '38px', color: j === 0 ? ink : muted, marginTop: j === 0 ? 6 : 0}}>{text}</Text>)}
              {cell.note && <Text style={{fontSize: 16, lineHeight: '26px', color: muted, marginTop: 12}}>{cell.note}</Text>}
            </div>
          );
        })}
      </div>
    );
  }

  // US-only growth timing; the official source paths, fills and gradients are intact.
  return (
    <div style={center}>
      <svg width="1920" height="1080" style={{position: 'absolute', inset: 0}}>
        {[184, 248, 312].map((radius, i) => <circle key={radius} cx="960" cy="500" r={radius} fill="none" stroke={terracotta} strokeWidth="1" opacity={.12 * ease(f, i * 12, 45)}/>)}
      </svg>
      <div style={{position: 'absolute', top: 150, opacity: 1 - ease(f, 18, 24)}}>
        <Serif style={{fontSize: 62, lineHeight: 1.2}}>This is the conversation to have.</Serif>
      </div>
      <OfficialUSGrowth seconds={f / 30} prefix="us"/>
      <Text style={{position: 'absolute', bottom: 40, fontSize: 12, color: muted, opacity: .5}}>Internal review — not for distribution</Text>
    </div>
  );
};

export const USFilm60V3: React.FC<{qa?: boolean; captions?: boolean; primary?: 'en' | 'zh'}> = ({qa = false, captions = true, primary = 'en'}) => {
  const frame = useCurrentFrame();
  const root = useRef<HTMLDivElement>(null);
  useLayoutEffect(() => {
    if (!qa || !root.current) return;
    const handle = delayRender('US V3 layout audit');
    let raf=0, done=false;
    const measure=()=>{
    const rootBox=root.current!.getBoundingClientRect();
    const sx=rootBox.width/1920, sy=rootBox.height/1080;
    const activeScene = scenes.find((scene) => frame >= scene.startFrame && frame < scene.endFrame);
    const candidates = Array.from(root.current!.querySelectorAll<HTMLElement>('div, span, text'));
    const text = candidates.filter((element) => {
      if (!element.textContent?.trim()) return false;
      if (element.dataset.audit) return true;
      return element.children.length === 0 && !element.parentElement?.closest('[data-audit]');
    }).map((element) => {
      let opacity = 1;
      for (let parent: Element | null = element; parent && parent !== root.current; parent = parent.parentElement) {
        const computed = getComputedStyle(parent);
        opacity *= Number(computed.opacity);
        if (computed.display === 'none' || computed.visibility === 'hidden') opacity = 0;
      }
      const rect = element.getBoundingClientRect();
      return {text: element.textContent?.trim(), x: (rect.x-rootBox.x)/sx, y: (rect.y-rootBox.y)/sy, width: rect.width/sx, height: rect.height/sy, fontSize: getComputedStyle(element).fontSize, caption: Boolean(element.closest('[data-caption]')), opacity};
    }).filter((item) => item.opacity > .001 && item.width > 0 && item.height > 0);
    console.log('US_V3_AUDIT:' + JSON.stringify({frame, scene: activeScene?.id, playbackRate: 1, text, rootRect:{x:rootBox.x,y:rootBox.y,width:rootBox.width,height:rootBox.height}}));
    done=true;continueRender(handle);
    };
    raf=requestAnimationFrame(()=>{raf=requestAnimationFrame(measure);});
    return()=>{cancelAnimationFrame(raf);if(!done)continueRender(handle);};
  }, [frame, qa]);
  return (
    <AbsoluteFill ref={root} style={{background: paper, color: ink}}>
      {scenes.map((scene) => <Sequence key={scene.id} from={scene.startFrame} durationInFrames={scene.endFrame - scene.startFrame}><Shot scene={scene}/></Sequence>)}
      {captions && <BilingualCaptions scene={scenes.find(scene => frame >= scene.startFrame && frame < scene.endFrame)!} cues={scenes.find(scene => frame >= scene.startFrame && frame < scene.endFrame)!.subtitleCues} primary={primary}/>}
      <Audio src={staticFile('music/us-v2/full-review-mix.wav')} playbackRate={1}/>
    </AbsoluteFill>
  );
};
