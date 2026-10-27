const ts=require('typescript');const fs=require('fs');const path=require('path');
const load=(file)=>{const js=ts.transpileModule(fs.readFileSync(file,'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,esModuleInterop:true}}).outputText;const mod={exports:{}};new Function('require','module','exports',js)((name)=>require(path.resolve(path.dirname(file),name)),mod,mod.exports);return mod.exports.hk;};
const hk=load(path.resolve(__dirname,'../src/config/hk.ts'));
const visible=hk.scenes.flatMap(s=>[...s.title,...(s.subtitleChunks??[]),...(s.placeholder?[s.placeholder]:[]),...(s.review?[s.review]:[])]).concat(hk.labels.noVoice,hk.labels.footagePrefix,hk.labels.quarter,hk.labels.wordmark);
let next=0;const scenes=[];
for(const s of hk.scenes){const from=Math.round(s.start*30),end=Math.round(s.end*30);if(from!==next)throw Error('Scene gap/overlap '+s.id);next=end;
 const rec=s.vo?hk.voiceTimings[s.vo]:null;if(rec&&rec.duration+s.start+hk.subtitle.leadIn>s.end-.3)throw Error('Insufficient scene time '+s.id);
 scenes.push({id:s.id,from,end,voiceDuration:rec?.duration??0,voiceStartFrame:rec?Math.round((s.start+hk.subtitle.leadIn)*hk.fps):null,playbackRate:1});}
if(next!==Math.round(hk.duration*30))throw Error('Composition duration differs');
const latin=visible.filter(t=>/[A-Za-z]/.test(t));if(latin.length)throw Error('Visible Latin text: '+latin);
const {spawnSync}=require('child_process');
const tc=spawnSync(path.resolve(__dirname,'../.tts-venv/bin/python'),['-c',"import json,sys;from opencc import OpenCC;c=OpenCC('s2t');a=json.load(sys.stdin);bad=[s for s in a if c.convert(s)!=s];print(json.dumps(bad,ensure_ascii=False));sys.exit(bool(bad))"],{input:JSON.stringify(visible),encoding:'utf8'});
if(tc.status!==0)throw Error('Traditional text audit failed: '+tc.stdout+tc.stderr);
if(hk.chineseOnly)throw Error('English brand name must remain visible');
const wordmark=require('../src/assets/wordmark.json');if(wordmark['english-glyphs'].length!==20)throw Error('Incomplete English wordmark');
const result={englishBrandName:'BLUE OAK INTERNATIONAL',brandEnglishException:true,traditionalTextAudit:'OpenCC s2t: unchanged',durationFrames:next,durationSeconds:next/30,allVisibleText:visible,latinText:latin,chineseOnly:hk.chineseOnly,scenes};
fs.writeFileSync(path.resolve(__dirname,'../qa/v3/content-audit.json'),JSON.stringify(result,null,2));console.log('Timeline, Traditional text and Chinese copy and English brand audit OK',next,'frames');
