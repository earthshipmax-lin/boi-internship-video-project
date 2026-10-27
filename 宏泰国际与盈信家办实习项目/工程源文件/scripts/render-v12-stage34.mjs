import {bundle} from '@remotion/bundler';
import {openBrowser,selectComposition,renderStill,renderMedia} from '@remotion/renderer';
import {existsSync,mkdirSync,readFileSync,writeFileSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
process.chdir(path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'));
const browserExecutable='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const base=JSON.parse(readFileSync('qa/v12/stage2-logo-r01/scene-seams.json','utf8'));
const scenes=base.map(s=>({...s,startFrame:s.startFrame+(s.startFrame>=860?63:0),endFrame:s.endFrame+(s.endFrame>=860?63:0)}));
const phases=[{id:'platform-office',startFrame:1324,contentFrame:1354,paper:true,photo:true},{id:'office-values',startFrame:1463,contentFrame:1493,paper:false,photo:false},{id:'values-vision-trust',startFrame:1534,contentFrame:1564,paper:true,photo:false}];
for(const stage of [3,4])mkdirSync(`qa/v12/stage${stage}/frames`,{recursive:true});
writeFileSync('qa/v12/stage3/scene-seams.json',JSON.stringify(scenes,null,2)+'\n');
mkdirSync('qa/v12/stage4/transitions',{recursive:true});
const manifest={fps:30,spreadFrames:18,holdFrames:12,totalTransitionFrames:30,center:[960,820],radius:1270,feather:60,phases,sceneAnchors:scenes.map(s=>({id:s.id,frame:s.startFrame})),compositionOffset:[{old:'values vision title',xy:[130,360]},{new:'values trust title',xy:[210,420],delta:[80,60]},{old:'license row',xy:[139,715]},{new:'license stack',xy:[1100,750]}],timingAdaptation:'0.60-0.72s is not 12 frames at 30fps; explicit 12-frame acceptance wins, giving 0.60+0.40=1.00s. Iris leads existing content anchors by 30 frames.'};
writeFileSync('qa/v12/stage4/transitions/manifest.json',JSON.stringify(manifest,null,2)+'\n');
const serveUrl=await bundle({entryPoint:path.resolve('src/index.ts'),publicDir:path.resolve('public')});
const browser=await openBrowser('chrome',{browserExecutable});
try{
 for(const stage of process.argv.includes('--stage3')?[3]:process.argv.includes('--stage4')?[4]:[3,4]){
  const q=`qa/v12/stage${stage}`;
  const composition=await selectComposition({serveUrl,id:`BOI-HK-Epic-v12-Stage${stage}`,browserExecutable,puppeteerInstance:browser});
  if(!process.argv.includes('--render-only')){
   const frames=stage===3?[500,705,714,735,810,870,900,912,923,1098,1354,1493,1623,1822,2043,2102]:[0,6,12,500,735,810,900,1098,1623,1652,1822,1840,2043,2102,...phases.flatMap(p=>[-18,-2,0,3,6,9,12,15,17,...Array.from({length:12},(_,i)=>18+i),30,36,45].map(i=>p.startFrame+i))];
   const unique=[...new Set(frames)].sort((a,b)=>a-b);
   for(let i=0;i<unique.length;i+=4)await Promise.all(unique.slice(i,i+4).map(frame=>renderStill({serveUrl,composition,frame,output:`${q}/frames/f${frame}.png`,browserExecutable,puppeteerInstance:browser,imageFormat:'png'})));
   console.log(`Stage${stage} native QA: ${unique.length} frames`);
  }
  if(!process.argv.includes('--stills-only')){
   const output=`out/BOI-HK_史詩形象片_v12_${stage===3?'第三':'第四'}版試片.mp4`,video=`${q}/video-only.mp4`;
   if(existsSync(output)||existsSync(video))throw new Error(`Refusing overwrite ${output}`);
   let last=-1;await renderMedia({serveUrl,composition,outputLocation:video,codec:'h264',crf:18,pixelFormat:'yuv420p',imageFormat:'jpeg',jpegQuality:94,concurrency:4,browserExecutable,puppeteerInstance:browser,muted:true,onProgress:({progress})=>{const p=Math.floor(progress*10);if(p!==last){last=p;console.log(`Stage${stage} rendering ${p*10}%`);}}});
   const master='qa/v12/stage3/audio-master.m4a';
   if(!existsSync(master))execFileSync('ffmpeg',['-v','error','-i','public/music/v12-stage3/review-mix.wav','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',master]);
   execFileSync('ffmpeg',['-v','error','-i',video,'-i',master,'-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart',output]);
   console.log(`Stage${stage} FINAL ${output}`);
  }
 }
}finally{await browser.close({silent:true});}
