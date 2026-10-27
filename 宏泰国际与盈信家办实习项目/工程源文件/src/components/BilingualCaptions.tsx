import React from 'react';
import {useCurrentFrame} from 'remotion';
import {theme} from '../theme';

export type SubtitleCue = {en: string; zh: string; startWord: number; endWord: number};
export type CaptionScene = {
  id: string; startFrame: number; endFrame: number; voiceStartFrame: number;
  words: {word: string; start: number; end: number}[]; subtitleCues: SubtitleCue[];
};
// Global frame numbers derived from the existing unmodified word alignment.
export const subtitleFrames = (scene: CaptionScene, cue: SubtitleCue) => ({
  from: scene.voiceStartFrame + Math.ceil(scene.words[cue.startWord].start * 30),
  to: Math.min(scene.endFrame, scene.voiceStartFrame + Math.ceil(scene.words[cue.endWord].end * 30)),
});

export const BilingualCaptions: React.FC<{
  scene: CaptionScene; cues: SubtitleCue[]; primary: 'en' | 'zh';
}> = ({scene, cues, primary}) => {
  const frame = useCurrentFrame();
  const cue = cues.find(item => {
    const {from, to} = subtitleFrames(scene, item);
    return frame >= from && frame < to;
  });
  if (!cue) return null;
  const languages: ('en' | 'zh')[] = [primary, primary === 'en' ? 'zh' : 'en'];
  return <div data-caption="bilingual" style={{
    position: 'absolute', bottom: 64, left: '50%', transform: 'translateX(-50%)',
    width: 1200, maxWidth: 1200, textAlign: 'center', color: theme.color.ink,
    display: 'flex', flexDirection: 'column', gap: 6, zIndex: 50,
  }}>
    {languages.map((language, i) => <div
      key={language} data-audit="caption" lang={language === 'zh' ? 'zh-Hant' : 'en'}
      style={{fontFamily: language === 'zh' ? 'Noto Sans TC' : 'Geist',
        fontSize: i === 0 ? 28 : 22, lineHeight: i === 0 ? 1.4 : 1.5,
        fontWeight: 400, opacity: i === 0 ? 1 : .82, overflowWrap: 'normal',
      }}>{cue[language]}</div>)}
  </div>;
};
