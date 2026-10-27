import React, {useLayoutEffect, useRef} from 'react';
import {AbsoluteFill, Audio, Sequence, staticFile, useCurrentFrame, delayRender, continueRender} from 'remotion';
import {theme, clamp01} from '../theme';
import {USTeamFocusV5} from './USTeamFocusV5';
import {USIntroTreeV5} from '../components/USIntroTreeV5';
import {OfficialUSGrowth} from '../components/OfficialUSGrowth';
import {BilingualCaptions, CaptionScene} from '../components/BilingualCaptions';
import timeline from '../config/us-full-v3-timeline.json';
import {USEvidenceShotV4} from './USEvidenceScenesV4';
import '../fonts';

type AlignedWord = {word: string; start: number; end: number};
type Scene = CaptionScene;
const scenes = timeline.scenes as Scene[];
const {ink, muted, paper, line, terracotta} = theme.color;
const sans = theme.font.latin;
const serif = theme.font.latinSerif;
const ease = (frame: number, from = 0, duration = 18) => theme.ease(clamp01((frame - from) / duration));

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
  if (scene.id === 'S2') return <USTeamFocusV5/>;
  if (scene.id === 'S6') return (
    <div style={{...center, opacity: fade}}>
      <Serif style={{fontSize: 52}}>The first year is the hardest one.</Serif>
    </div>
  );

  if (scene.id === 'S1') return <><USEvidenceShotV4 scene={scene}/><USIntroTreeV5 seconds={f/30}/></>;
  if (['S3', 'S4', 'S5'].includes(scene.id)) return <USEvidenceShotV4 scene={scene}/>;

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

export const USFilm60V5: React.FC<{qa?: boolean; captions?: boolean; primary?: 'en' | 'zh'}> = ({qa = false, captions = true, primary = 'en'}) => {
  const frame = useCurrentFrame();
  const root = useRef<HTMLDivElement>(null);
  useLayoutEffect(() => {
    if (!qa || !root.current) return;
    const handle = delayRender('US V5 layout audit');
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
    const visibleOpacity=(element: Element)=>{
      let opacity=1;
      for(let parent:Element|null=element;parent&&parent!==root.current;parent=parent.parentElement){
        const style=getComputedStyle(parent);opacity*=Number(style.opacity);
        if(style.display==='none'||style.visibility==='hidden')return 0;
      }
      return opacity;
    };
    const blocks=Array.from(root.current!.querySelectorAll<HTMLElement>('[data-photo-id],[data-content-box]')).map(element=>{
      const rect=element.getBoundingClientRect();
      return {id:element.dataset.photoId||element.dataset.contentBox, photo:Boolean(element.dataset.photoId), x:(rect.x-rootBox.x)/sx,y:(rect.y-rootBox.y)/sy,width:rect.width/sx,height:rect.height/sy,opacity:visibleOpacity(element),scale:Number(element.dataset.sourceScale||0),page:Number(element.dataset.sourcePage||0)};
    }).filter(item=>item.opacity>.001);
    const focusCards=Array.from(root.current!.querySelectorAll<HTMLElement>('[data-focus-card]')).map(e=>({slug:e.dataset.focusCard,selected:e.dataset.selected==='true',opacity:Number(e.dataset.focusOpacity),scale:Number(e.dataset.imageScale),x:(e.getBoundingClientRect().x-rootBox.x)/sx,y:(e.getBoundingClientRect().y-rootBox.y)/sy}));
    const chars=Array.from(root.current!.querySelectorAll<HTMLElement>('[data-character-index]')).map(e=>Number(getComputedStyle(e).opacity));
    console.log('US_V5_AUDIT:' + JSON.stringify({frame, scene: activeScene?.id, playbackRate: 1, text, blocks, focusCards, chars, activePerson:root.current!.querySelector<HTMLElement>('[data-achievement-person]')?.dataset.achievementPerson, rootRect:{x:rootBox.x,y:rootBox.y,width:rootBox.width,height:rootBox.height}}));
    done=true;continueRender(handle);
    };
    raf=requestAnimationFrame(()=>{raf=requestAnimationFrame(measure);});
    return()=>{cancelAnimationFrame(raf);if(!done)continueRender(handle);};
  }, [frame, qa]);
  return (
    <AbsoluteFill ref={root} style={{background: paper, color: ink}}>
      {scenes.map((scene) => <Sequence key={scene.id} from={scene.startFrame} durationInFrames={scene.endFrame - scene.startFrame}><Shot scene={scene}/></Sequence>)}
      {captions && <BilingualCaptions scene={scenes.find(scene => frame >= scene.startFrame && frame < scene.endFrame)!} cues={scenes.find(scene => frame >= scene.startFrame && frame < scene.endFrame)!.subtitleCues} primary={primary}/>}
      <Audio src={staticFile('music/us-v2/full-review-mix-v5.wav')} playbackRate={1}/>
    </AbsoluteFill>
  );
};
