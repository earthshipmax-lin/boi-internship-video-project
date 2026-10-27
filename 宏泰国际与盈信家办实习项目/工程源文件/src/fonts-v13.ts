import {loadFont} from '@remotion/fonts';
import {staticFile} from 'remotion';
/** Await actual FontFace loading before DOM fitting. document.fonts.ready can
 * resolve before asynchronously fetched FontFaces have been added to the set. */
export const fontsReadyV13=Promise.all([
 ['Noto Serif TC','NotoSerifTC.ttf','200 900'],
 ['Noto Sans TC','NotoSansTC.ttf','100 900'],
 ['Source Serif 4','SourceSerif4.ttf','200 900'],
 ['Geist','Geist.ttf','100 900'],
].map(([family,file,weight])=>loadFont({family,url:staticFile(`fonts/${file}`),weight})));
