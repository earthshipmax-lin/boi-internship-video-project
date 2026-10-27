import {USFilm60V5} from './scenes/USFilm60V5';
import {USFilm60V4} from './scenes/USFilm60V4';
import {USFilm60V3} from './scenes/USFilm60V3';
import {USFilm60V2} from './scenes/USFilm60V2';
import {USFilm60V1} from './scenes/USFilm60V1';
import {USTeamVoiceB} from './scenes/USTeamVoiceB';
import {USTeamV1} from './scenes/USTeamV1';
import React from 'react';
import {Composition,Folder} from 'remotion';
import {Film} from './Film';
import {LogoScene} from './scenes/Scenes';
import {PrototypeReference} from './Reference';
import {hk} from './config/hk';
import {LogoIntroV7,LogoOutroV7} from './LogoBookendsV7';
import logoV7 from './config/logo-hk-v7.json';
import {LogoIntroV10,LogoOutroV10} from './LogoBookendsV10';
import {OfficialReferenceV10} from './components/OfficialBrandV10';
import {EpicFilmV11} from './scenes/ScenesV11';
import {EpicEndingRevisionR01} from './scenes/EndingRevisionR01';
import {EpicFilmV12} from './scenes/ScenesV12';
import {EpicFilmV12Stage2} from './scenes/ScenesV12Stage2';
import {EpicFilmV12Stage3} from './scenes/ScenesV12Stage3';
import {EpicFilmV12Stage4} from './scenes/ScenesV12Stage4';
import {EpicFilmV12Stage5} from './scenes/ScenesV12Stage5';
import {EpicFilmV12Stage6} from './scenes/ScenesV12Stage6';
import {LogoOpticalComparisonStage6} from './components/LogoGridV12';
import {EpicFilmV12Stage7} from './scenes/ScenesV12Stage7';
import {EpicFilmV12Stage8} from './scenes/ScenesV12Stage8';
import {EpicFilmV12Final} from './scenes/ScenesV12Final';
import {EpicFilmV12Offices} from './scenes/ScenesV12Offices';
import {EpicFilmV12Stage9} from './scenes/ScenesV12Stage9';
export const Root:React.FC=()=> <>
 <Folder name="US"><Composition id="US-Team-v1-60s-V5" component={USFilm60V5} width={1920} height={1080} fps={30} durationInFrames={1800} defaultProps={{qa:false,captions:true,primary:'en' as const}}/><Composition id="US-Team-v1-60s-V4" component={USFilm60V4} width={1920} height={1080} fps={30} durationInFrames={1800} defaultProps={{qa:false,captions:true,primary:'en' as const}}/><Composition id="US-Team-v1-60s-V3" component={USFilm60V3} width={1920} height={1080} fps={30} durationInFrames={1800} defaultProps={{qa:false,captions:true,primary:'en' as const}}/><Composition id="US-Team-v1-60s-V2" component={USFilm60V2} width={1920} height={1080} fps={30} durationInFrames={1800} defaultProps={{qa:false}}/><Composition id="US-Team-v1-60s" component={USFilm60V1} width={1920} height={1080} fps={30} durationInFrames={1800} defaultProps={{qa:false}}/><Composition id="US-Team-v1-VoiceB" component={USTeamVoiceB} width={1920} height={1080} fps={30} durationInFrames={240}/><Composition id="US-Team-v1" component={USTeamV1} width={1920} height={1080} fps={30} durationInFrames={240} defaultProps={{qa:false}}/></Folder>
 <Folder name="V12Stage9"><Composition id="BOI-HK-Epic-v12-Stage9" component={EpicFilmV12Stage9} width={1920} height={1080} fps={30} durationInFrames={2103} defaultProps={{watermark:true,qa:false}}/></Folder>
 <Folder name="V12Offices"><Composition id="BOI-HK-Epic-v12-Offices" component={EpicFilmV12Offices} width={1920} height={1080} fps={30} durationInFrames={2103} defaultProps={{watermark:true,qa:false}}/></Folder>
 <Folder name="V12Final"><Composition id="BOI-HK-Epic-v12-Final" component={EpicFilmV12Final} width={1920} height={1080} fps={30} durationInFrames={2103} defaultProps={{watermark:true,qa:false}}/></Folder>
 <Folder name="V12Stage8"><Composition id="BOI-HK-Epic-v12-Stage8" component={EpicFilmV12Stage8} width={1920} height={1080} fps={30} durationInFrames={2103}/></Folder>
 <Folder name="V12Stage7"><Composition id="BOI-HK-Epic-v12-Stage7" component={EpicFilmV12Stage7} width={1920} height={1080} fps={30} durationInFrames={2103}/></Folder>
 <Folder name="V12Stage6"><Composition id="BOI-HK-Epic-v12-Stage6" component={EpicFilmV12Stage6} width={1920} height={1080} fps={30} durationInFrames={2103}/><Composition id="BOI-HK-Logo-Optical-Stage6" component={LogoOpticalComparisonStage6} width={1920} height={1080} fps={30} durationInFrames={1}/></Folder>
 <Folder name="V12Stage5"><Composition id="BOI-HK-Epic-v12-Stage5" component={EpicFilmV12Stage5} width={1920} height={1080} fps={30} durationInFrames={2103}/></Folder>
 <Folder name="V12Stage4"><Composition id="BOI-HK-Epic-v12-Stage4" component={EpicFilmV12Stage4} width={1920} height={1080} fps={30} durationInFrames={2103}/></Folder>
 <Folder name="V12Stage3"><Composition id="BOI-HK-Epic-v12-Stage3" component={EpicFilmV12Stage3} width={1920} height={1080} fps={30} durationInFrames={2103}/></Folder>
 <Folder name="V12Stage2"><Composition id="BOI-HK-Epic-v12-Stage2" component={EpicFilmV12Stage2} width={1920} height={1080} fps={30} durationInFrames={2040}/></Folder>
 <Folder name="V12"><Composition id="BOI-HK-Epic-v12-Stage1" component={EpicFilmV12} width={1920} height={1080} fps={30} durationInFrames={2040}/></Folder>
 <Folder name="EndingRevision"><Composition id="BOI-HK-Epic-v11-ending-r01" component={EpicEndingRevisionR01} width={1920} height={1080} fps={30} durationInFrames={2040}/></Folder>
 <Folder name="V11"><Composition id="BOI-HK-Epic-v11" component={EpicFilmV11} width={1920} height={1080} fps={30} durationInFrames={2040}/></Folder>
 <Composition id={hk.composition} component={Film} width={hk.width} height={hk.height} fps={hk.fps} durationInFrames={Math.round(hk.duration*hk.fps)} defaultProps={{bgm:true}}/>
 <Composition id="BOI-HK-Logo" component={LogoScene} width={1920} height={1080} fps={30} durationInFrames={360} defaultProps={{transition:true,still:false}}/>
 <Folder name="V7"><Composition id="BOI-HK-Intro-v7" component={LogoIntroV7} width={1920} height={1080} fps={30} durationInFrames={logoV7.introFrames}/><Composition id="BOI-HK-Outro-v7" component={LogoOutroV7} width={1920} height={1080} fps={30} durationInFrames={logoV7.outroFrames}/></Folder>
 <Folder name="V10"><Composition id="BOI-HK-Intro-v10" component={LogoIntroV10} width={1920} height={1080} fps={30} durationInFrames={logoV7.introFrames}/><Composition id="BOI-HK-Outro-v10" component={LogoOutroV10} width={1920} height={1080} fps={30} durationInFrames={logoV7.outroFrames}/><Composition id="BOI-HK-Official-Reference-v10" component={OfficialReferenceV10} width={1920} height={1080} fps={30} durationInFrames={1}/></Folder>
 <Folder name="QA"><Composition id="BOI-HK-Prototype-Reference" component={PrototypeReference} width={1920} height={1080} fps={30} durationInFrames={360}/><Composition id="BOI-HK-Logo-Hold" component={LogoScene} width={1920} height={1080} fps={30} durationInFrames={360} defaultProps={{transition:false,still:false,chineseOnly:false}}/></Folder>
</>;
