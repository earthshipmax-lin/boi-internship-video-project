import {bundle} from '@remotion/bundler';
import {openBrowser,selectComposition,renderStill,renderMedia} from '@remotion/renderer';
import {existsSync,mkdirSync,readFileSync,writeFileSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
process.chdir(path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'));
const logoRevision=process.argv.includes('--logo-r01');
const q=logoRevision?'qa/v12/stage2-logo-r01':'qa/v12/stage2';mkdirSync(`${q}/frames`,{recursive:true});
const onsets=JSON.parse(readFileSync('src/config/beats-v11.json','utf8')).onsets_s;
const targets=[0,6.08,14.35,17.5,20.3,23.5,28.6,35.95,43.2,47.6,52.85,58.55];
const starts=targets.map((t,i)=>{const n=onsets.reduce((best,x)=>Math.abs(x-t)<Math.abs(best-t)?x:best,999);return i?Math.round((Math.abs(n-t)<.18?n:t)*30):0;});
const names=['vision','origin','premium','commission','clients','trust','global','platform','office','values','roots','close'];
const paper=(id,t)=>['office','roots','close'].includes(id)||(id==='values'&&t>=52);
const seams=names.map((id,i)=>({id,startFrame:starts[i],endFrame:starts[i+1]??2040,enter:i&&paper(names[i-1],starts[i]/30-1/30)===paper(id,starts[i]/30)?'crossfade':'cut',background:paper(id,starts[i]/30)?'paper':'navy'}));
writeFileSync(`${q}/scene-seams.json`,JSON.stringify(seams,null,2)+'\n');
const browserExecutable='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const serveUrl=await bundle({entryPoint:path.resolve('src/index.ts'),publicDir:path.resolve('public')});
const browser=await openBrowser('chrome',{browserExecutable});
try{
 const composition=await selectComposition({serveUrl,id:'BOI-HK-Epic-v12-Stage2',browserExecutable,puppeteerInstance:browser});
 if(!process.argv.includes('--render-only')){
  const general=(logoRevision?[14.4,14.7,15.3,15.9,16.3,16.6666667,17,17.4666667,17.5,17.8,18.3,20,24,34.5,43.2,52,66,67.9666667]:[3.2,4.4,5.5,15.7,16.8,18.3,19.8,24.0,24.6,25.4,26.5,27.4,28.0,34.5,40.5,48.5,51.9,52,52.5,54,56.5,63.8,66,67.9666667]).map(t=>Math.round(t*30));
  const seam=starts[8];const frames=[...new Set([...general,...[-3,-2,-1,0,1,2,3].map(n=>seam+n)])].sort((a,b)=>a-b);
  for(const frame of frames)await renderStill({serveUrl,composition,frame,output:`${q}/frames/f${frame}.png`,browserExecutable,puppeteerInstance:browser,imageFormat:'png'});
  console.log('QA frames ready; office seam frame',seam);
 }
 if(!process.argv.includes('--stills-only')){
  const output=logoRevision?'out/BOI-HK_史詩形象片_v12_Logo加速修訂.mp4':'out/BOI-HK_史詩形象片_v12.mp4',video=`${q}/video-only.mp4`;
  if(existsSync(output)||existsSync(video))throw new Error('Output exists; refusing overwrite');
  let last=-1;await renderMedia({serveUrl,composition,outputLocation:video,codec:'h264',crf:18,pixelFormat:'yuv420p',imageFormat:'jpeg',jpegQuality:94,concurrency:4,browserExecutable,puppeteerInstance:browser,muted:true,onProgress:({progress})=>{const p=Math.floor(progress*10);if(p!==last){last=p;console.log('Rendering',p*10+'%');}}});
  execFileSync('ffmpeg',['-v','error','-i',video,'-i','out/BOI-HK_史詩形象片_v12_第一階段試片.mp4','-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart',output]);
  console.log('FINAL',output,'audio copied from accepted Stage1');
 }
}finally{await browser.close({silent:true});}
