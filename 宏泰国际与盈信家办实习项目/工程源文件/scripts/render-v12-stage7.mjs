import {bundle} from '@remotion/bundler';
import {openBrowser,selectComposition,renderStill,renderMedia} from '@remotion/renderer';
import {existsSync,mkdirSync,readFileSync,writeFileSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
process.chdir(path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'));
const q='qa/v12/stage7';mkdirSync(`${q}/frames`,{recursive:true});
const manifest={duration:70.1,fps:30,frames:2103,composition:'BOI-HK-Epic-v12-Stage7',sourceMovie:'out/BOI-HK_史詩形象片_v12_第六版試片.mp4',audioMaster:'qa/v12/stage3/audio-master.m4a',scopeFrames:[705,1150],awards:{backTopDelta:-30,backLeftDelta:40,backRightDelta:-40,backGap:20,blueWhaleTopDelta:12,sourceImagesUnchanged:true},routes:{origin:'香港',names:['深圳','紐約','新加坡'],starts:[34.16,34.52,35.60],durations:[.45,.95,.80],labelDelay:.12,staggerRule:'At least0.18s and never before narration cue',singleCubic:true,gaussianBlur:false,pointSamplingStep:4.9}};
writeFileSync(`${q}/timing.json`,JSON.stringify(manifest,null,2)+'\n');
const browserExecutable='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const serveUrl=await bundle({entryPoint:path.resolve('src/index.ts'),publicDir:path.resolve('public')});
const browser=await openBrowser('chrome',{browserExecutable});
try{
 const composition=await selectComposition({serveUrl,id:'BOI-HK-Epic-v12-Stage7',browserExecutable,puppeteerInstance:browser});
 if(!process.argv.includes('--render-only')){
  const frames=[96,500,570,704,705,710,720,750,810,900,922,923,926,931,932,990,1002,1024,1025,1028,1029,1030,1031,1032,1033,1036,1039,1046,1047,1048,1049,1050,1051,1064,1065,1068,1076,1077,1078,1079,1080,1081,1092,1096,1104,1110,1140,1141,1145,1149,1150,1326,1602,2043,2102];
  const qaComposition=await selectComposition({serveUrl,id:'BOI-HK-Epic-v12-Stage7',browserExecutable,puppeteerInstance:browser,inputProps:{qa:true}});
  const metrics=new Map();
  const onBrowserLog=log=>{const i=log.text.indexOf('STAGE7_ROUTES:');if(i>=0){const v=JSON.parse(log.text.slice(i+'STAGE7_ROUTES:'.length));metrics.set(Math.round(v.time*30),v);}};
  for(let i=0;i<frames.length;i+=4)await Promise.all(frames.slice(i,i+4).map(frame=>renderStill({serveUrl,composition:qaComposition,inputProps:{qa:true},frame,output:`${q}/frames/f${frame}.png`,browserExecutable,puppeteerInstance:browser,imageFormat:'png',onBrowserLog})));
  writeFileSync(`${q}/route-browser-metrics.json`,JSON.stringify(Object.fromEntries([...metrics].sort((a,b)=>a[0]-b[0])),null,2)+'\n');
  console.log('Stage7 native QA frames:',frames.length);
 }
 if(!process.argv.includes('--stills-only')){
  const output='out/BOI-HK_史詩形象片_v12_第七版試片.mp4',video=`${q}/video-only.mp4`;
  if(existsSync(output)||existsSync(video))throw new Error('Refusing overwrite '+output);
  let last=-1;await renderMedia({serveUrl,composition,outputLocation:video,codec:'h264',crf:18,pixelFormat:'yuv420p',imageFormat:'jpeg',jpegQuality:94,concurrency:4,browserExecutable,puppeteerInstance:browser,muted:true,onProgress:({progress})=>{const p=Math.floor(progress*10);if(p!==last){last=p;console.log('Stage7 rendering',p*10+'%');}}});
  execFileSync('ffmpeg',['-v','error','-i',video,'-i',manifest.audioMaster,'-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart',output]);
  console.log('FINAL',output,'AAC copied directly from Stage6 shared master');
 }
}finally{await browser.close({silent:true});}
