import {bundle} from '@remotion/bundler';
import {openBrowser,selectComposition,renderStill,renderMedia} from '@remotion/renderer';
import {existsSync,mkdirSync,readFileSync,writeFileSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
process.chdir(path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'));
const q='qa/v12/stage6';mkdirSync(`${q}/frames`,{recursive:true});
const manifest={duration:70.1,fps:30,frames:2103,composition:'BOI-HK-Epic-v12-Stage6',sourceMovie:'out/BOI-HK_史詩形象片_v12_第五版試片.mp4',audioMaster:'qa/v12/stage3/audio-master.m4a',scopeFrames:[431,618],premiumStart:431,commissionStart:525,clientsStart:609,premiumGridLeft:1010,commissionGridLeft:920,gridShift:90,gridTop:300,cell:[128,78],gap:16,grid:[704,454],premiumCells:20,commissionCells:25,insuranceCount:23,bankCount:2,settledOpacity:.82,ringCounts:[8,10],allInitialLitFrame:487,allAddedLitFrame:542,gridShiftSettledFrame:548,ending:'Stage5 exact composition outside the data-scene window'};
writeFileSync(`${q}/timing.json`,JSON.stringify(manifest,null,2)+'\n');
const browserExecutable='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const serveUrl=await bundle({entryPoint:path.resolve('src/index.ts'),publicDir:path.resolve('public')});
const browser=await openBrowser('chrome',{browserExecutable});
try{
 const composition=await selectComposition({serveUrl,id:'BOI-HK-Epic-v12-Stage6',browserExecutable,puppeteerInstance:browser});
 if(!process.argv.includes('--render-only')){
  const frames=[96,430,431,435,450,459,487,500,518,524,525,528,531,534,537,540,542,548,570,600,608,609,612,617,618,810,900,1098,1326,1356,1380,1530,1602,1755,2043,2102];
  for(let i=0;i<frames.length;i+=4)await Promise.all(frames.slice(i,i+4).map(frame=>renderStill({serveUrl,composition,frame,output:`${q}/frames/f${frame}.png`,browserExecutable,puppeteerInstance:browser,imageFormat:'png'})));
  const optical=await selectComposition({serveUrl,id:'BOI-HK-Logo-Optical-Stage6',browserExecutable,puppeteerInstance:browser});
  await renderStill({serveUrl,composition:optical,frame:0,output:`${q}/logo-optical-before-after.png`,browserExecutable,puppeteerInstance:browser,imageFormat:'png'});
  console.log('Stage6 native QA frames:',frames.length);
 }
 if(!process.argv.includes('--stills-only')){
  const output='out/BOI-HK_史詩形象片_v12_第六版試片.mp4',video=`${q}/video-only.mp4`;
  if(existsSync(output)||existsSync(video))throw new Error('Refusing overwrite '+output);
  let last=-1;await renderMedia({serveUrl,composition,outputLocation:video,codec:'h264',crf:18,pixelFormat:'yuv420p',imageFormat:'jpeg',jpegQuality:94,concurrency:4,browserExecutable,puppeteerInstance:browser,muted:true,onProgress:({progress})=>{const p=Math.floor(progress*10);if(p!==last){last=p;console.log('Stage6 rendering',p*10+'%');}}});
  execFileSync('ffmpeg',['-v','error','-i',video,'-i',manifest.audioMaster,'-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart',output]);
  console.log('FINAL',output,'AAC copied directly from Stage5 shared master');
 }
}finally{await browser.close({silent:true});}
