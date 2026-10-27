import {loadFont} from '@remotion/fonts';
import {staticFile} from 'remotion';
// loadFont blocks Remotion rendering until each local font is ready.
for (const [family,file,weight] of [
  ['Noto Serif TC','NotoSerifTC.ttf','200 900'],
  ['Noto Sans TC','NotoSansTC.ttf','100 900'],
  ['Source Serif 4','SourceSerif4.ttf','200 900'],
  ['Geist','Geist.ttf','100 900'],
]) void loadFont({family,url:staticFile(`fonts/${file}`),weight});
