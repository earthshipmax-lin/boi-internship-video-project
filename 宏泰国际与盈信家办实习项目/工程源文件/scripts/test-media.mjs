import {existsSync,copyFileSync,mkdirSync,unlinkSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
const fixtures=[['qa/fixtures/VO-01.wav','public/vo/hk/VO-01.wav'],['qa/fixtures/S1.mp4','public/footage/S1.mp4'],['qa/fixtures/bgm.wav','public/music/bgm.wav']];
for(const [,dest] of fixtures)if(existsSync(dest))throw new Error(`Existing media preserved; refusing test: ${dest}`);
mkdirSync('qa/fixtures',{recursive:true});
execFileSync('ffmpeg',['-v','error','-y','-f','lavfi','-i','sine=frequency=440:duration=1.2','-ar','48000','qa/fixtures/VO-01.wav']);
execFileSync('ffmpeg',['-v','error','-y','-f','lavfi','-i','color=c=0xe9e5df:s=1920x1080:r=30:d=1','-c:v','libx264','-pix_fmt','yuv420p','qa/fixtures/S1.mp4']);
execFileSync('ffmpeg',['-v','error','-y','-f','lavfi','-i','sine=frequency=160:duration=2','-ar','48000','qa/fixtures/bgm.wav']);
try {
 for(const [src,dest] of fixtures)copyFileSync(src,dest);
 execFileSync('npx',['remotion','render','BOI-HK-60s','qa/test-media-2s.mp4','--frames=360-419','--log=error'],{stdio:'inherit'});
 console.log(execFileSync('ffprobe',['-v','error','-show_entries','stream=codec_name,duration','-of','json','qa/test-media-2s.mp4'],{encoding:'utf8'}));
} finally {for(const [,dest]of fixtures)if(existsSync(dest))unlinkSync(dest);}
