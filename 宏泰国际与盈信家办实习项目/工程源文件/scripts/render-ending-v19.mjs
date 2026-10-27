import {bundle} from '@remotion/bundler';
import {openBrowser,selectComposition,renderMedia,renderStill} from '@remotion/renderer';
import {readFileSync,writeFileSync,mkdirSync,existsSync} from 'node:fs';
import path from 'node:path';
const q='qa/v19/film',exe='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',id='BOI-HK-Epic-v19-CN';mkdirSync(q+'/frames',{recursive:true});
const timeline=JSON.parse(readFileSync('src/config/timeline-v19-cn.json','utf8')),url=await bundle({entryPoint:path.resolve('src/index-v19.tsx'),publicDir:path.resolve('public')}),browser=await openBrowser('chrome',{browserExecutable:exe});
try{
 const base={locale:'zh-CN',timeline,qa:false,muted:false},opts={serveUrl:url,id,browserExecutable:exe,puppeteerInstance:browser};
 const full=await selectComposition({...opts,inputProps:base});if(full.props.muted)throw Error('Resolved full props must be audible');
 const qaProps={...base,qa:true,muted:true},qaComp=await selectComposition({...opts,inputProps:qaProps}),rows=[];
 for(const frame of [2600,2660,2703,2715,2745,2785,2810,2835,2850,2870,2905,2940])await renderStill({serveUrl:url,composition:qaComp,inputProps:qaProps,frame,output:q+'/frames/cn-f'+frame+'.png',browserExecutable:exe,puppeteerInstance:browser,onBrowserLog:l=>{let s=l.text.indexOf('FILM_V13_AUDIT:');if(s>=0)rows.push(JSON.parse(l.text.slice(s+15)));}});
 writeFileSync(q+'/layout-audit.json',JSON.stringify(rows,null,2));
 for(const [kind,output,range] of [['PREVIEW','out/BOI-HK_v19_普通話片尾_雄渾重錄15秒預覽.mp4',[2512,timeline.durationInFrames-1]],['SUFFIX','qa/v19/film/ending-picture-suffix.mp4',[2510,timeline.durationInFrames-1]]]){
  if(existsSync(output))throw Error('Refuse overwrite '+output);let last=-1;
  await renderMedia({serveUrl:url,composition:full,inputProps:base,...(range?{frameRange:range}:{}),outputLocation:output,codec:'h264',crf:18,audioCodec:'aac',audioBitrate:'320k',pixelFormat:'yuv420p',imageFormat:'jpeg',jpegQuality:94,concurrency:6,browserExecutable:exe,puppeteerInstance:browser,onProgress:({progress})=>{let n=Math.floor(progress*10)*10;if(n!==last){last=n;console.log(kind,n+'%');}}});console.log('READY',output);
 }
}finally{await browser.close({silent:true});}
