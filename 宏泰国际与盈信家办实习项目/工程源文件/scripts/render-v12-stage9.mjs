import {bundle} from '@remotion/bundler';
import {openBrowser,selectComposition,renderStill,renderMedia} from '@remotion/renderer';
import {existsSync,mkdirSync,writeFileSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
process.chdir(path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'));
const q='qa/v12/stage9';mkdirSync(`${q}/frames`,{recursive:true});
const watermark=!process.argv.includes('--watermark=false'),inputProps={watermark,qa:true};
const serveUrl=await bundle({entryPoint:path.resolve('src/index.ts'),publicDir:path.resolve('public')});
const browserExecutable='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const browser=await openBrowser('chrome',{browserExecutable});
const audit=new Map(),routes=new Map(),platform=new Map();
const onBrowserLog=log=>{
 for(const [prefix,target,key] of [['STAGE9_AUDIT:',audit,'frame'],['STAGE9_ROUTES:',routes,'frame'],['STAGE9_PLATFORM:',platform,'sceneTime']]){
  const p=log.text.indexOf(prefix);if(p>=0){const a=JSON.parse(log.text.slice(p+prefix.length));target.set(key==='sceneTime'?Math.round(1141+a.sceneTime*30):a[key],a);}
 }
};
const save=(kind)=>{for(const [name,map] of [['frame-audit',audit],['routes',routes],['platform',platform]])writeFileSync(`${q}/${kind}-${name}.json`,JSON.stringify(Object.fromEntries([...map].sort((a,b)=>a[0]-b[0])),null,2)+'\n');};
try{
 const composition=await selectComposition({serveUrl,id:'BOI-HK-Epic-v12-Stage9',inputProps,browserExecutable,puppeteerInstance:browser});
 if(!process.argv.includes('--render-only')){
  const frames=[96,500,704,705,716,728,729,741,742,743,744,780,843,863,864,865,888,923,948,990,1004,1005,1006,1007,1025,1041,1042,1043,1070,1071,1072,1073,1096,1097,1098,1099,1110,1140,1141,1150,1168,1177,1200,1213,1225,1250,1280,1322,1323,1336,1358,1359,1383,1450,1517,1602,1652,2043,2102];
  for(let i=0;i<frames.length;i+=4)await Promise.all(frames.slice(i,i+4).map(frame=>renderStill({serveUrl,composition,inputProps,frame,output:`${q}/frames/f${frame}.png`,imageFormat:'png',browserExecutable,puppeteerInstance:browser,onBrowserLog})));
  save('stills');console.log('Stage9 native frames',frames.length);
 }
 if(!process.argv.includes('--stills-only')){
  const output=watermark?'out/BOI-HK_史詩形象片_v12_第九版試片.mp4':'out/BOI-HK_史詩形象片_v12_第九版_乾淨母版.mp4',video=`${q}/${watermark?'video-only':'video-only-clean'}.mp4`;
  if(existsSync(output)||existsSync(video))throw new Error('Refusing overwrite '+output);
  audit.clear();routes.clear();platform.clear();let last=-1;
  await renderMedia({serveUrl,composition,inputProps,outputLocation:video,codec:'h264',crf:18,pixelFormat:'yuv420p',imageFormat:'jpeg',jpegQuality:94,concurrency:4,muted:true,browserExecutable,puppeteerInstance:browser,onBrowserLog,onProgress:({progress})=>{const p=Math.floor(progress*10);if(p!==last){last=p;console.log('Stage9 render',p*10+'%');}}});
  save('review');execFileSync('ffmpeg',['-v','error','-i',video,'-i','qa/v12/stage3/audio-master.m4a','-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart',output]);console.log('FINAL',output,'watermark='+watermark,'original AAC copied');
 }
}finally{await browser.close({silent:true});}
