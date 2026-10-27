import {bundle} from '@remotion/bundler';
import {openBrowser,selectComposition,renderStill,renderMedia} from '@remotion/renderer';
import {existsSync,mkdirSync,writeFileSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
process.chdir(path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'));
const q='qa/v12/final';mkdirSync(`${q}/frames`,{recursive:true});
// This switch is documented for a future authorized clean-master export.
// The current run uses default watermark=true only.
const clean=process.argv.includes('--clean-master')||process.argv.includes('--watermark=false'),watermark=!clean;
const inputProps={watermark,qa:true};
const serveUrl=await bundle({entryPoint:path.resolve('src/index.ts'),publicDir:path.resolve('public')});
const browserExecutable='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const browser=await openBrowser('chrome',{browserExecutable});
const audit=new Map();
const onBrowserLog=log=>{const p=log.text.indexOf('FINAL_AUDIT:');if(p>=0){const a=JSON.parse(log.text.slice(p+12));audit.set(a.frame,a);}};
try{
 const composition=await selectComposition({serveUrl,id:'BOI-HK-Epic-v12-Final',inputProps,browserExecutable,puppeteerInstance:browser});
 if(!process.argv.includes('--render-only')){
  const frames=[96,250,500,570,650,704,710,750,810,900,926,932,1050,1110,1141,1150,1200,1224,1230,1245,1260,1322,1323,1336,1358,1359,1364,1365,1382,1383,1401,1414,1440,1476,1484,1485,1500,1560,1563,1564,1570,1580,1602,1644,1652,1700,1822,1900,2043,2102];
  for(let i=0;i<frames.length;i+=4)await Promise.all(frames.slice(i,i+4).map(frame=>renderStill({serveUrl,composition,inputProps,frame,output:`${q}/frames/f${frame}.png`,imageFormat:'png',browserExecutable,puppeteerInstance:browser,onBrowserLog})));
  writeFileSync(`${q}/stills-audit.json`,JSON.stringify(Object.fromEntries([...audit].sort((a,b)=>a[0]-b[0])),null,2)+'\n');
  console.log('FINAL native QA frames',frames.length);
 }
 if(!process.argv.includes('--stills-only')){
  const output=clean?'out/BOI-HK_史詩形象片_v12_乾淨母版.mp4':'out/BOI-HK_史詩形象片_v12_定版審片.mp4';
  const video=clean?`${q}/video-only-clean.mp4`:`${q}/video-only.mp4`;
  if(existsSync(output)||existsSync(video))throw new Error('Refusing overwrite: '+output);
  audit.clear();let last=-1;
  await renderMedia({serveUrl,composition,inputProps,outputLocation:video,codec:'h264',crf:18,pixelFormat:'yuv420p',imageFormat:'jpeg',jpegQuality:94,concurrency:4,muted:true,browserExecutable,puppeteerInstance:browser,onBrowserLog,onProgress:({progress})=>{const p=Math.floor(progress*10);if(p!==last){last=p;console.log('FINAL render',p*10+'%');}}});
  writeFileSync(`${q}/${clean?'clean-':'review-'}frame-audit.json`,JSON.stringify(Object.fromEntries([...audit].sort((a,b)=>a[0]-b[0])),null,2)+'\n');
  execFileSync('ffmpeg',['-v','error','-i',video,'-i','qa/v12/stage3/audio-master.m4a','-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart',output]);
  console.log('FINAL',output,'watermark='+watermark,'original AAC copied');
 }
}finally{await browser.close({silent:true});}
