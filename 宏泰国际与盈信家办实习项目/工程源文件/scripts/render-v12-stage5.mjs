import {bundle} from '@remotion/bundler';
import {openBrowser,selectComposition,renderStill,renderMedia} from '@remotion/renderer';
import {existsSync,mkdirSync,readFileSync,writeFileSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
process.chdir(path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'));
const q='qa/v12/stage5';mkdirSync(`${q}/frames`,{recursive:true});
const manifest={duration:70.1,fps:30,frames:2103,irisCount:1,irisStart:1323,spreadFrames:33,holdFrames:3,officeContent:1359,officeExitStart:1476,valuesStart:1485,firstLine:1491,secondLine:1560,valuesExitStart:1644,rootsStart:1652,closeStart:1822,sourceMovie:'out/BOI-HK_史詩形象片_v12_第四版試片.mp4',audioMaster:'qa/v12/stage3/audio-master.m4a',colorRule:'One blue-to-paper iris; paper remains continuously through the ending.',banks:{panel:[920,824,754,112],heading:[920,778],inkHeight:54,inkCenterY:880,centersX:[1108.5,1485.5],sourceCrop:'CSS whitespace clip only; original source RGB files remain unchanged.'}};
writeFileSync(`${q}/timing.json`,JSON.stringify(manifest,null,2)+'\n');
const browserExecutable='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const serveUrl=await bundle({entryPoint:path.resolve('src/index.ts'),publicDir:path.resolve('public')});
const browser=await openBrowser('chrome',{browserExecutable});
try{
 const composition=await selectComposition({serveUrl,id:'BOI-HK-Epic-v12-Stage5',browserExecutable,puppeteerInstance:browser});
 if(!process.argv.includes('--render-only')){
  const general=[96,459,500,525,534,549,570,597,609,810,900,1098,1380,1467,1476,1484,1485,1491,1509,1530,1559,1560,1578,1602,1644,1651,1652,1682,1755,1822,1840,2043,2102];
  const phase=[-3,0,3,6,9,12,15,18,21,24,27,30,32,33,34,35,36,39,45].map(n=>1323+n);
  const frames=[...new Set([...general,...phase])].sort((a,b)=>a-b);
  for(let i=0;i<frames.length;i+=4)await Promise.all(frames.slice(i,i+4).map(frame=>renderStill({serveUrl,composition,frame,output:`${q}/frames/f${frame}.png`,browserExecutable,puppeteerInstance:browser,imageFormat:'png'})));
  console.log('Stage5 native QA frames:',frames.length);
 }
 if(!process.argv.includes('--stills-only')){
  const output='out/BOI-HK_史詩形象片_v12_第五版試片.mp4',video=`${q}/video-only.mp4`;
  if(existsSync(output)||existsSync(video))throw new Error('Refusing overwrite '+output);
  let last=-1;await renderMedia({serveUrl,composition,outputLocation:video,codec:'h264',crf:18,pixelFormat:'yuv420p',imageFormat:'jpeg',jpegQuality:94,concurrency:4,browserExecutable,puppeteerInstance:browser,muted:true,onProgress:({progress})=>{const p=Math.floor(progress*10);if(p!==last){last=p;console.log('Stage5 rendering',p*10+'%');}}});
  execFileSync('ffmpeg',['-v','error','-i',video,'-i',manifest.audioMaster,'-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart',output]);
  console.log('FINAL',output,'AAC copied directly from Stage4 shared master');
 }
}finally{await browser.close({silent:true});}
